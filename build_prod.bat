@echo off
setlocal enabledelayedexpansion
echo ============================================================
echo  PlayAural Production Build
echo ============================================================
echo.

:: Ensure we run from the repo root regardless of where the script is called from.
cd /d "%~dp0"

:: ---------------------------------------------------------------------------
:: Step 1: Build updater.exe (single-file bundle)
:: ---------------------------------------------------------------------------
echo [1/3] Building updater...
pyinstaller --noconfirm updater.spec
if errorlevel 1 (
    echo.
    echo ERROR: updater build failed. Aborting.
    pause
    exit /b 1
)
echo       updater.exe built successfully.
echo.

:: ---------------------------------------------------------------------------
:: Step 2: Build PlayAural (one-dir bundle)
:: ---------------------------------------------------------------------------
echo [2/3] Building PlayAural...
pyinstaller --noconfirm PlayAural.spec
if errorlevel 1 (
    echo.
    echo ERROR: PlayAural build failed. Aborting.
    pause
    exit /b 1
)
echo       PlayAural built successfully.
echo.

:: ---------------------------------------------------------------------------
:: Step 3: Copy updater.exe into the PlayAural dist folder so it ships together
:: ---------------------------------------------------------------------------
echo [3/3] Copying updater.exe into dist\PlayAural\...
if not exist "dist\PlayAural" (
    echo ERROR: dist\PlayAural directory not found. Aborting.
    pause
    exit /b 1
)
copy /y "dist\updater.exe" "dist\PlayAural\updater.exe"
if errorlevel 1 (
    echo ERROR: Failed to copy updater.exe. Aborting.
    pause
    exit /b 1
)
echo       updater.exe copied.
echo.

echo ============================================================
echo  Build complete.
echo  Output: dist\PlayAural\
echo ============================================================
pause
