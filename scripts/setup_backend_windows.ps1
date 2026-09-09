#requires -Version 5.1
<#!
.SYNOPSIS
    Rebuilds the SIH FastAPI backend virtual environment with Python 3.13.

.DESCRIPTION
    Run from PowerShell:
      Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
      .\scripts\setup_backend_windows.ps1

    The script terminates named python, uvicorn, and git processes because they
    can retain Windows file handles. Do not run it while another project needs
    one of those processes. It removes only this repository's backend\.venv and
    .git\index.lock, then installs requirements and verifies imports.
#>

$ErrorActionPreference = 'Stop'

$RepositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$BackendRoot = Join-Path $RepositoryRoot 'backend'
$VenvPath = Join-Path $BackendRoot '.venv'
$GitLockPath = Join-Path $RepositoryRoot '.git\index.lock'

if (-not (Test-Path -LiteralPath $BackendRoot -PathType Container)) {
    throw "Backend directory not found: $BackendRoot"
}

Write-Host 'Checking for Python 3.13...' -ForegroundColor Cyan
& py -3.13 --version
if ($LASTEXITCODE -ne 0) {
    throw 'Python 3.13 was not found. Install Python 3.13 and ensure the py launcher is available.'
}

Write-Host 'Stopping potentially locking Python, Uvicorn, and Git processes...' -ForegroundColor Cyan
foreach ($ProcessName in @('python', 'uvicorn', 'git')) {
    Get-Process -Name $ProcessName -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
}

if (Test-Path -LiteralPath $GitLockPath -PathType Leaf) {
    Write-Host "Removing stale Git lock: $GitLockPath" -ForegroundColor Yellow
    Remove-Item -LiteralPath $GitLockPath -Force
}

if (Test-Path -LiteralPath $VenvPath -PathType Container) {
    Write-Host "Removing existing virtual environment: $VenvPath" -ForegroundColor Yellow
    $RemovedVenv = $false
    for ($Attempt = 1; $Attempt -le 5 -and -not $RemovedVenv; $Attempt++) {
        try {
            Get-Process -Name python, uvicorn, git -ErrorAction SilentlyContinue |
                Stop-Process -Force -ErrorAction SilentlyContinue
            Remove-Item -LiteralPath $VenvPath -Recurse -Force -ErrorAction Stop
            $RemovedVenv = $true
        } catch {
            if ($Attempt -eq 5) {
                throw "Unable to remove $VenvPath after five attempts. Close editors or security tools holding its files, then run this script again. Details: $($_.Exception.Message)"
            }
            Write-Host "Virtual environment is still locked; retrying ($Attempt/5)..." -ForegroundColor Yellow
            Start-Sleep -Seconds 2
        }
    }
}

Set-Location -LiteralPath $BackendRoot

Write-Host 'Creating Python 3.13 virtual environment...' -ForegroundColor Cyan
& py -3.13 -m venv .venv
if ($LASTEXITCODE -ne 0) {
    throw 'Virtual environment creation failed.'
}

$ActivateScript = Join-Path $VenvPath 'Scripts\Activate.ps1'
Write-Host 'Activating the virtual environment...' -ForegroundColor Cyan
. $ActivateScript

Write-Host 'Confirming active interpreter...' -ForegroundColor Cyan
& python --version
$PythonVersion = (& python --version 2>&1).ToString()
if ($PythonVersion -notmatch '^Python 3\.13\.') {
    throw "Expected Python 3.13.x, but active interpreter is: $PythonVersion"
}

Write-Host 'Upgrading pip...' -ForegroundColor Cyan
& python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    throw 'pip upgrade failed.'
}

$RequirementsPath = Join-Path $BackendRoot 'requirements.txt'
if (Test-Path -LiteralPath $RequirementsPath -PathType Leaf) {
    Write-Host 'Installing backend requirements...' -ForegroundColor Cyan
    & python -m pip install -r $RequirementsPath
} else {
    Write-Host 'requirements.txt not found; installing core packages...' -ForegroundColor Yellow
    & python -m pip install fastapi 'uvicorn[standard]' chromadb sentence-transformers pydantic python-dotenv
}
if ($LASTEXITCODE -ne 0) {
    throw 'Dependency installation failed.'
}

Write-Host 'Verifying Python version and required imports...' -ForegroundColor Cyan
& python --version
& python -c "import fastapi, uvicorn, chromadb, sentence_transformers, pydantic; print('ALL_MODULES_OK')"
if ($LASTEXITCODE -ne 0) {
    throw 'Dependency verification failed.'
}

# ── .env setup ───────────────────────────────────────────────
$EnvFile = Join-Path $RepositoryRoot '.env'
$EnvExample = Join-Path $RepositoryRoot '.env.example'
if ((Test-Path -LiteralPath $EnvExample -PathType Leaf) -and -not (Test-Path -LiteralPath $EnvFile -PathType Leaf)) {
    Write-Host 'Creating .env from .env.example...' -ForegroundColor Cyan
    Copy-Item -LiteralPath $EnvExample -Destination $EnvFile
    Write-Host '.env created — edit it with your API keys before running the server.' -ForegroundColor Green
} elseif (Test-Path -LiteralPath $EnvFile -PathType Leaf) {
    Write-Host '.env already exists — skipping copy.' -ForegroundColor Yellow
}

# ── Build / refresh ChromaDB index ───────────────────────────
$ProcessedDir = Join-Path $RepositoryRoot 'data\processed'
if (Test-Path -LiteralPath $ProcessedDir -PathType Container) {
    Write-Host 'Building ChromaDB index from data/processed (first run downloads ~130 MB model)...' -ForegroundColor Cyan
    & python -m app.rag.ingest --input-dir $ProcessedDir
    if ($LASTEXITCODE -ne 0) {
        Write-Host 'ChromaDB ingestion failed — retry with:  .\scripts\ingest_data.ps1 (or python -m app.rag.ingest --reset)' -ForegroundColor Yellow
    } else {
        Write-Host 'ChromaDB index built.' -ForegroundColor Green
    }
} else {
    Write-Host 'data/processed not found — skipping ChromaDB ingestion. Add documents and re-run.' -ForegroundColor Yellow
}

Write-Host "Backend environment is ready: $VenvPath" -ForegroundColor Green
