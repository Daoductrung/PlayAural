@echo off
title Building PlayAural Client...
echo ==========================================
echo      PlayAural Production Build Script
echo ==========================================

REM 1. Activate Environment (Try client venv first)
if exist "client\.venv\Scripts\activate" (
    echo Activating Client Virtual Environment...
    call client\.venv\Scripts\activate
) else (
    if exist "server\.venv\Scripts\activate" (
        echo Activating Server Virtual Environment...
        call server\.venv\Scripts\activate
    ) else (
        echo No virtual environment found. Using system Python...
    )
)

REM 2. Install Dependencies
echo Installing Dependencies...
pip install pyinstaller requests psutil websockets pyperclip platformdirs accessible_output2 sound_lib wxPython fluent-runtime

REM 3. Clean previous builds
echo Cleaning up...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM 4. Build Updater (Standalone EXE)
echo.
echo Building Updater...
pyinstaller updater.spec
if %errorlevel% neq 0 (
    echo Error building Updater!
    pause
    exit /b %errorlevel%
)

REM 5. Build Main Client (Directory based)
echo.
echo Building PlayAural Client...
pyinstaller PlayAural.spec

if %errorlevel% neq 0 (
    echo Error building Client!
    pause
    exit /b %errorlevel%
)

REM 6. Assemble Final Package
echo.
echo Assembling final package...
move dist\updater.exe dist\PlayAural\updater.exe

echo.
echo ==========================================
echo      BUILD SUCCESSFUL!
echo ==========================================
echo Output location: dist\PlayAural
echo.
pause
