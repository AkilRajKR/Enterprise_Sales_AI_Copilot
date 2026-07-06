#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Enterprise Sales AI Copilot — Clean Startup Script
    Kills stale processes, then starts the backend on port 8000.

.USAGE
    From project root:
        .\start_backend.ps1

    Or from backend folder:
        cd backend; ..\start_backend.ps1
#>

$ErrorActionPreference = "Continue"
$PROJECT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
$BACKEND_DIR  = Join-Path $PROJECT_ROOT "backend"

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Enterprise Sales AI Copilot — Backend Start   ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ── Step 1: Kill stale processes on ports 8000 and 8001 ──────────────────────
Write-Host "→ Clearing stale processes on ports 8000 / 8001..." -ForegroundColor Yellow

foreach ($port in @(8000, 8001)) {
    $conns = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    foreach ($conn in $conns) {
        $ownerPid = $conn.OwningProcess
        if ($ownerPid -and $ownerPid -ne 0) {
            $proc = Get-Process -Id $ownerPid -ErrorAction SilentlyContinue
            if ($proc) {
                Write-Host "  Killing $($proc.Name) (PID $ownerPid) on port $port" -ForegroundColor Red
                Stop-Process -Id $ownerPid -Force -ErrorAction SilentlyContinue
            }
        }
    }
    # Also try taskkill approach
    $netstatLines = netstat -ano 2>$null | Select-String "0\.0\.0\.0:$port.*LISTENING"
    foreach ($line in $netstatLines) {
        $parts = ($line.ToString().Trim() -split '\s+')
        $stalePid = $parts[-1]
        if ($stalePid -match '^\d+$') {
            taskkill /PID $stalePid /F /T 2>$null | Out-Null
        }
    }
}

Start-Sleep -Seconds 2
Write-Host "  Ports cleared." -ForegroundColor Green
Write-Host ""

# ── Step 2: Activate venv and start backend ───────────────────────────────────
$venvPython = Join-Path $BACKEND_DIR "venv\Scripts\python.exe"
$venvUvicorn = Join-Path $BACKEND_DIR "venv\Scripts\uvicorn.exe"

if (-not (Test-Path $venvPython)) {
    Write-Host "ERROR: venv not found at $venvPython" -ForegroundColor Red
    Write-Host "  Run: cd backend && python -m venv venv && venv\Scripts\pip install -r requirements.txt"
    exit 1
}

Write-Host "→ Starting FastAPI backend (port 8002)..." -ForegroundColor Yellow
Write-Host "  Python : $venvPython" -ForegroundColor Gray
Write-Host "  Dir    : $BACKEND_DIR" -ForegroundColor Gray
Write-Host ""
Write-Host "  Open in browser → http://localhost:5173  (frontend)" -ForegroundColor Cyan
Write-Host "  API health      → http://localhost:8002/health" -ForegroundColor Cyan
Write-Host "  API docs        → http://localhost:8002/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Press Ctrl+C to stop." -ForegroundColor Yellow
Write-Host ""

Set-Location $BACKEND_DIR
& $venvUvicorn api.main:app --reload --host 0.0.0.0 --port 8002
