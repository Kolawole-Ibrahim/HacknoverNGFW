@echo off
REM Simple launcher for Protection Dashboard
title HacknoverNGFW Dashboard

REM Change to script directory
cd /d "%~dp0"

REM Check if venv exists
if exist "venv\Scripts\python.exe" (
    echo Starting Protection Dashboard...
    venv\Scripts\python.exe protection_dashboard.py
) else (
    echo Virtual environment not found!
    echo.
    echo Please run the installer first:
    echo   installer_simple.py
    echo   or
    echo   SIMPLE_INSTALL.bat
    echo.
    pause
    exit /b 1
)

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start dashboard
    echo.
    echo Trying alternative methods...
    echo.
    
    REM Try py command
    py protection_dashboard.py 2>nul
    if errorlevel 1 (
        REM Try python
        python protection_dashboard.py 2>nul
        if errorlevel 1 (
            echo.
            echo Could not start dashboard.
            echo Please check Python installation.
            pause
        )
    )
)

