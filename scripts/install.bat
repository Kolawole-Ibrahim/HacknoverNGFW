@echo off
echo ========================================
echo HacknoverNGFW Windows Installer For Windows Only
echo ========================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%I in ('python --version 2^>^&1') do set PYTHON_VERSION=%%I
echo Found Python version: %PYTHON_VERSION%

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    echo Make sure venv is available in your Python installation
    pause
    exit /b 1
)

REM Activate virtual environment and install dependencies
echo Installing dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip

REM Install from requirements.txt if it exists
if exist requirements.txt (
    pip install -r requirements.txt
) else (
    echo requirements.txt not found, installing common dependencies...
    pip install flask requests scapy netifaces psutil
)

REM Create necessary directories
if not exist logs mkdir logs
if not exist config mkdir config
if not exist data mkdir data

echo.
echo ========================================
echo Installation Completed Successfully!
echo ========================================
echo.
echo To run the application:
echo 1. Activate virtual environment: venv\Scripts\activate
echo 2. Run: python main.py
echo.
pause