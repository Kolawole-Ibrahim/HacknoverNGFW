@echo off
title HacknoverNGFW Installer
color 0A
echo ========================================
echo    HacknoverNGFW Windows Installer
echo    User-Friendly Installation Wizard
echo ========================================
echo.

REM Check for administrator privileges
net session >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Administrator privileges not detected!
    echo Some features may require admin rights.
    echo.
    pause
)

REM Check if Python is installed
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.7+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%I in ('python --version 2^>^&1') do set PYTHON_VERSION=%%I
echo [OK] Found Python version: %PYTHON_VERSION%
echo.

REM Check if GUI installer exists and offer to use it
if exist "installer_gui.py" (
    echo Would you like to use the GUI installer instead?
    echo (Recommended for non-technical users)
    choice /C YN /M "Use GUI Installer"
    if errorlevel 2 goto command_line
    if errorlevel 1 (
        echo.
        echo Launching GUI installer...
        python installer_gui.py
        exit /b 0
    )
)

:command_line
echo [2/5] Creating virtual environment...
if exist venv (
    echo Removing existing virtual environment...
    rmdir /s /q venv
)
python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    echo Make sure venv is available in your Python installation
    pause
    exit /b 1
)
echo [OK] Virtual environment created
echo.

echo [3/5] Upgrading pip...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
echo [OK] pip upgraded
echo.

echo [4/5] Installing dependencies (this may take a few minutes)...
echo Please wait...

REM Install dependencies individually to handle failures gracefully
echo Installing setproctitle...
pip install setproctitle --quiet
echo Installing scapy...
pip install scapy --quiet
echo Installing Flask...
pip install Flask --quiet
echo Installing requests...
pip install requests --quiet
echo Installing psutil...
pip install psutil --quiet
echo Installing PyYAML...
pip install PyYAML --quiet

REM Try netifaces but don't fail if it doesn't work
echo Attempting to install netifaces (optional)...
pip install netifaces --quiet 2>nul
if errorlevel 1 (
    echo [WARNING] netifaces installation failed - this is optional
) else (
    echo [OK] netifaces installed
)

echo [OK] Dependencies installed
echo.

echo [5/5] Creating necessary directories...
if not exist logs mkdir logs
if not exist quarantined mkdir quarantined
echo [OK] Directories created
echo.

echo ========================================
echo    Installation Completed Successfully!
echo ========================================
echo.
echo NEXT STEPS:
echo.
echo Option 1 - GUI Launcher (Recommended):
echo    Double-click: gui_launcher.py
echo    Or run: python gui_launcher.py
echo.
echo Option 2 - Command Line:
echo    1. Activate: venv\Scripts\activate
echo    2. Run: python main.py
echo.
echo IMPORTANT: Run as Administrator for full functionality!
echo.
echo Creating desktop shortcut...
if exist "gui_launcher.py" (
    echo @echo off > "%USERPROFILE%\Desktop\HacknoverNGFW.bat"
    echo cd /d "%~dp0" >> "%USERPROFILE%\Desktop\HacknoverNGFW.bat"
    echo python gui_launcher.py >> "%USERPROFILE%\Desktop\HacknoverNGFW.bat"
    echo [OK] Desktop shortcut created
) else (
    echo [SKIP] gui_launcher.py not found
)
echo.
echo ========================================
pause