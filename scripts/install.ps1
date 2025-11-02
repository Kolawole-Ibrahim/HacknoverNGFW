Write-Host "========================================" -ForegroundColor Green
Write-Host "HacknoverNGFW Windows PowerShell Installer" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Yellow
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.7+ from https://python.org" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
    Write-Host "Make sure venv is available in your Python installation" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "Installing dependencies..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1
pip install --upgrade pip

if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
} else {
    Write-Host "requirements.txt not found, installing common dependencies..." -ForegroundColor Yellow
    pip install flask requests scapy-python3 psutil
}
@("logs", "config", "data") | ForEach-Object {
    if (-not (Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ | Out-Null
    }
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Installation Completed Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`nTo run the application:" -ForegroundColor White
Write-Host "1. Activate virtual environment: .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host "2. Run: python main.py" -ForegroundColor Cyan
Write-Host "`nNote: Scapy may require WinPcap/Npcap on Windows" -ForegroundColor Yellow
Read-Host "`nPress Enter to continue"