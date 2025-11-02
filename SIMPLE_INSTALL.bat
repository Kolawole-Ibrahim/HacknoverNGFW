@echo off
title HacknoverNGFW Simple Installer
color 0B
cls
echo.
echo ========================================
echo   HacknoverNGFW - Simple Installer
echo ========================================
echo.
echo This will install HacknoverNGFW for you.
echo.
pause

echo [1/5] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.7+ from python.org
    pause
    exit /b 1
)
python --version
echo OK!
echo.

echo [2/5] Creating virtual environment...
if exist venv rmdir /s /q venv
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create venv
    pause
    exit /b 1
)
echo OK!
echo.

echo [3/5] Upgrading pip...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
echo OK!
echo.

echo [4/5] Installing dependencies (please wait)...
pip install setproctitle scapy Flask requests psutil PyYAML --quiet
echo OK!
echo.

echo [5/5] Creating directories...
if not exist logs mkdir logs
if not exist quarantined mkdir quarantined
echo OK!
echo.

echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo To start the firewall:
echo   Double-click: START_FIREWALL.bat
echo   Or run: python gui_launcher.py
echo.
echo IMPORTANT: Run as Administrator when starting!
echo.
pause

