@echo off
setlocal

cd /d "%~dp0web_client"
if errorlevel 1 (
    echo ERROR: Could not open the web_client directory.
    exit /b 1
)

set "PYTHON_EXE="
set "PYTHON_ARGS="
where python >nul 2>nul
if not errorlevel 1 set "PYTHON_EXE=python"

if not defined PYTHON_EXE (
    where py >nul 2>nul
    if not errorlevel 1 (
        set "PYTHON_EXE=py"
        set "PYTHON_ARGS=-3"
    )
)

if not defined PYTHON_EXE (
    echo ERROR: Python was not found on PATH.
    echo Install Python 3.11 or newer, then run this script again.
    exit /b 1
)

echo Starting local web server at http://localhost:8080
echo Press Ctrl+C to stop
start "" "http://localhost:8080"
%PYTHON_EXE% %PYTHON_ARGS% -m http.server 8080
exit /b %ERRORLEVEL%
