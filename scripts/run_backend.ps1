#requires -Version 5.1
<#!
.SYNOPSIS
    Start the ManakSetu FastAPI dev server on Windows.

.DESCRIPTION
    Run from PowerShell at the repository root:
      Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
      .\scripts\run_backend.ps1

    Optionally pass a port number (default 8000):
      .\scripts\run_backend.ps1 -Port 8080
#>

param(
    [int]$Port = 8000
)

$ErrorActionPreference = 'Stop'

$RepositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$BackendRoot = Join-Path $RepositoryRoot 'backend'
$VenvPath = Join-Path $BackendRoot '.venv'
$ActivateScript = Join-Path $VenvPath 'Scripts\Activate.ps1'

# ── Verify venv exists ─────────────────────────────────────────
if (-not (Test-Path -LiteralPath $ActivateScript -PathType Leaf)) {
    Write-Host "Virtual environment not found at $VenvPath" -ForegroundColor Red
    Write-Host 'Run .\scripts\setup_backend_windows.ps1 first.' -ForegroundColor Yellow
    exit 1
}

# ── Activate venv ──────────────────────────────────────────────
Write-Host "Activating venv: $VenvPath" -ForegroundColor Cyan
. $ActivateScript

# ── Verify critical imports ────────────────────────────────────
Write-Host 'Verifying imports...' -ForegroundColor Cyan
& python -c "import fastapi, uvicorn, chromadb, sentence_transformers; print('ALL_MODULES_OK')"
if ($LASTEXITCODE -ne 0) {
    Write-Host 'Import verification failed. Run .\scripts\setup_backend_windows.ps1 again.' -ForegroundColor Red
    exit 1
}

# ── Start Uvicorn ──────────────────────────────────────────────
Set-Location -LiteralPath $BackendRoot
Write-Host "Starting ManakSetu backend on http://127.0.0.1:${Port}" -ForegroundColor Green
Write-Host '(Press CTRL+C to stop)' -ForegroundColor DarkGray

& python -m uvicorn app.main:app --reload --port $Port
