# Quick run script for HacknoverNGFW on Windows
Write-Host "========================================" -ForegroundColor Green
Write-Host "HacknoverNGFW - NextGen Firewall" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Check for administrator privileges
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[ERROR] This script requires Administrator privileges!" -ForegroundColor Red
    Write-Host "Please run PowerShell as Administrator" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Attempting to restart as Administrator..." -ForegroundColor Yellow
    Start-Process powershell -Verb RunAs -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; .\run_firewall.ps1"
    exit
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
if (Test-Path "venv\Scripts\Activate.ps1") {
    .\venv\Scripts\Activate.ps1
} else {
    Write-Host "[ERROR] Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: py -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Check if dependencies are installed
Write-Host "Checking dependencies..." -ForegroundColor Cyan
$missing = @()
$required = @("scapy", "Flask", "requests", "psutil", "yaml", "setproctitle")
foreach ($pkg in $required) {
    $result = python -c "import $pkg" 2>&1
    if ($LASTEXITCODE -ne 0) {
        $missing += $pkg
    }
}

if ($missing.Count -gt 0) {
    Write-Host "[WARNING] Missing dependencies: $($missing -join ', ')" -ForegroundColor Yellow
    Write-Host "Installing missing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# Check for Npcap/WinPcap (warns but doesn't fail)
Write-Host ""
Write-Host "Checking for packet capture library..." -ForegroundColor Cyan
$npcapInstalled = Test-Path "C:\Program Files\Npcap"
$winpcapInstalled = Test-Path "C:\Windows\System32\wpcap.dll"
if (-not $npcapInstalled -and -not $winpcapInstalled) {
    Write-Host "[WARNING] Npcap or WinPcap not found!" -ForegroundColor Yellow
    Write-Host "Packet capture (DPI) may not work properly." -ForegroundColor Yellow
    Write-Host "Download Npcap: https://npcap.com/download/" -ForegroundColor Cyan
} else {
    Write-Host "[OK] Packet capture library found" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Starting NextGen Firewall..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Run the firewall
python main.py -v

