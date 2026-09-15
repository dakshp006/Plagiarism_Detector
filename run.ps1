Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "   PLAGIARISM & DUPLICATE TEXT DETECTION SYSTEM - LAUNCHER (PowerShell)" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

if (-not (Test-Path "venv")) {
    Write-Host "[INFO] Creating Python virtual environment 'venv'..." -ForegroundColor Yellow
    python -m venv venv
}

Write-Host "[INFO] Activating virtual environment..." -ForegroundColor Green
& ".\venv\Scripts\Activate.ps1"

Write-Host "[INFO] Installing required dependencies..." -ForegroundColor Green
python -m pip install -r requirements.txt

Write-Host "[INFO] Launching Web Server on http://127.0.0.1:5000 ..." -ForegroundColor Cyan
python run_web.py
