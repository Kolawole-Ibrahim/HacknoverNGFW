@echo off
cls
echo.
echo ========================================
echo   HacknoverNGFW - Easy Installer
echo ========================================
echo.
echo Choose an installer:
echo.
echo [1] Simple GUI Installer (Recommended)
echo [2] Command Line Installer
echo.
choice /C 12 /M "Select option"

if errorlevel 2 goto cli
if errorlevel 1 goto gui_simple

:gui_simple
echo.
echo Starting Simple GUI Installer...
python installer_simple.py
goto end

:cli
echo.
echo Starting Command Line Installer...
call scripts\install.bat
goto end

:end
pause

