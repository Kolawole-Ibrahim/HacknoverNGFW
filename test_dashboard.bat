@echo off
echo Testing Dashboard...
echo.
echo If it closes immediately, the error will be shown here:
echo.

cd /d "%~dp0"

if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe protection_dashboard.py
) else (
    py protection_dashboard.py
)

if errorlevel 1 (
    echo.
    echo Dashboard failed with error code: %ERRORLEVEL%
    echo.
    echo Check above for error messages.
)

echo.
pause

