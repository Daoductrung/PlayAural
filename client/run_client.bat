@echo off
setlocal
cd /d "%~dp0"
set "EXIT_CODE=0"

echo Starting PlayAural Client...
echo.

where uv >nul 2>nul
if errorlevel 1 (
    echo ERROR: uv was not found on PATH.
    echo Install uv, then run this script again.
    set "EXIT_CODE=1"
    goto finish
)

echo Installing dependencies, including development test tools...
uv sync --extra dev
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install PlayAural Client dependencies.
    set "EXIT_CODE=1"
    goto finish
)

echo.
echo Launching...
uv run python client.py
set "EXIT_CODE=%ERRORLEVEL%"

:finish
echo.
if not "%EXIT_CODE%"=="0" (
    echo Client exited with code %EXIT_CODE%.
)
pause
exit /b %EXIT_CODE%
