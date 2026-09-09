#requires -Version 5.1
<#!
.SYNOPSIS
    (Re)builds the ChromaDB vector index from data/processed/ for the SIH backend.

.DESCRIPTION
    Run from PowerShell (repository root):
      Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
      .\scripts\ingest_data.ps1 [-Reset]

    -Reset  wipes and rebuilds the collection from scratch.
#>
param(
    [switch]$Reset
)

$ErrorActionPreference = 'Stop'

$RepositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$BackendRoot = Join-Path $RepositoryRoot 'backend'
$ProcessedDir = Join-Path $RepositoryRoot 'data\processed'
$VenvPath = Join-Path $BackendRoot '.venv'

if (-not (Test-Path -LiteralPath $ProcessedDir -PathType Container)) {
    throw "No data\processed directory found at $ProcessedDir"
}
if (-not (Test-Path -LiteralPath (Join-Path $VenvPath 'Scripts\Activate.ps1') -PathType Leaf)) {
    throw "No backend\.venv found. Run .\scripts\setup_backend_windows.ps1 first."
}

Set-Location -LiteralPath $BackendRoot
. (Join-Path $VenvPath 'Scripts\Activate.ps1')

Write-Host 'Ingesting documents into ChromaDB...' -ForegroundColor Cyan
& python -m app.rag.ingest --input-dir $ProcessedDir -Reset:$Reset
if ($LASTEXITCODE -ne 0) {
    throw 'ChromaDB ingestion failed.'
}

Write-Host 'Done. Start the backend with:  python -m uvicorn app.main:app --reload --port 8000' -ForegroundColor Green