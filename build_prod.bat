@echo off
setlocal

echo ============================================================
echo  PlayAural Production Build
echo ============================================================
echo.

cd /d "%~dp0"

set "PYTHON_CMD=py -3.12"
where py >nul 2>nul
if errorlevel 1 (
    set "PYTHON_CMD=python"
)

echo [0/4] Verifying build environment...
%PYTHON_CMD% -c "import sys; print(sys.version)"
if errorlevel 1 (
    echo.
    echo ERROR: Python 3.12 was not found. Install Python 3.12 and try again.
    pause
    exit /b 1
)

%PYTHON_CMD% -c "import PyInstaller, wx, accessible_output2, sound_lib, keyring, requests, fluent.runtime, livekit, sounddevice"
if errorlevel 1 (
    echo.
    echo ERROR: One or more build dependencies are missing in the selected Python environment.
    echo Install the required packages, then run this script again.
    pause
    exit /b 1
)
echo       Build environment is ready.
echo.

echo [1/4] Cleaning previous build output...
if exist "build" rmdir /s /q "build"
if exist "dist\PlayAural" rmdir /s /q "dist\PlayAural"
if exist "dist\updater.exe" del /f /q "dist\updater.exe"
echo       Previous output removed.
echo.

echo [2/4] Building updater...
%PYTHON_CMD% -m PyInstaller --clean --noconfirm updater.spec
if errorlevel 1 (
    echo.
    echo ERROR: updater build failed. Aborting.
    pause
    exit /b 1
)
if not exist "dist\updater.exe" (
    echo.
    echo ERROR: updater.exe was not produced.
    pause
    exit /b 1
)
echo       updater.exe built successfully.
echo.

echo [3/4] Building PlayAural...
%PYTHON_CMD% -m PyInstaller --clean --noconfirm PlayAural.spec
if errorlevel 1 (
    echo.
    echo ERROR: PlayAural build failed. Aborting.
    pause
    exit /b 1
)
if not exist "dist\PlayAural\PlayAural.exe" (
    echo.
    echo ERROR: dist\PlayAural\PlayAural.exe was not produced.
    pause
    exit /b 1
)
echo       PlayAural built successfully.
echo.

echo [4/4] Finalizing release folder...
copy /y "dist\updater.exe" "dist\PlayAural\updater.exe" >nul
if errorlevel 1 (
    echo.
    echo ERROR: Failed to copy updater.exe into the release folder.
    pause
    exit /b 1
)
if not exist "dist\PlayAural\sounds" (
    echo.
    echo ERROR: sounds folder is missing from dist\PlayAural.
    pause
    exit /b 1
)
if not exist "dist\PlayAural\locales" (
    echo.
    echo ERROR: locales folder is missing from dist\PlayAural.
    pause
    exit /b 1
)
echo       Release folder verified.
echo.

echo ============================================================
echo  Build complete.
echo  Output: dist\PlayAural\
echo ============================================================
pause
