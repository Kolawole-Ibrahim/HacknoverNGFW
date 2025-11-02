@echo off
REM Quick launcher for HacknoverNGFW GUI
REM Double-click this file to start the firewall

title HacknoverNGFW Launcher

REM Check if running as admin
net session >nul 2>&1
if errorlevel 1 (
    echo Requesting Administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

REM Change to script directory
cd /d "%~dp0"

REM Check if venv exists
if not exist "venv\Scripts\python.exe" (
    echo Virtual environment not found!
    echo.
    echo Please run the installer first:
    echo   - installer_gui.py (GUI installer)
    echo   - scripts\install.bat (Command line installer)
    echo.
    pause
    exit /b 1
)

REM Launch Protection Dashboard
echo Starting HacknoverNGFW Protection Dashboard...
echo.

REM Check for virtual environment first
if exist "venv\Scripts\python.exe" (
    echo Using virtual environment...
    venv\Scripts\python.exe protection_dashboard.py
    goto end
)

REM Fallback to system Python
echo Virtual environment not found, trying system Python...
py protection_dashboard.py 2>nul
if errorlevel 1 (
    python protection_dashboard.py 2>nul
    if errorlevel 1 (
        echo.
        echo [ERROR] Failed to start dashboard
        echo.
        echo Virtual environment not found!
        echo Please run the installer first:
        echo   installer_simple.py
        echo   or
        echo   SIMPLE_INSTALL.bat
        echo.
        pause
        exit /b 1
    )
)

:end

pause

