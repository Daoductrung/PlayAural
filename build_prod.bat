@echo off
setlocal

echo ============================================================
echo  PlayAural Production Build
echo ============================================================
echo.

cd /d "%~dp0"

set "PYTHON_EXE="
set "PYTHON_ARGS="
set "PREFERRED_PYTHON_EXE="
set "PREFERRED_PYTHON_ARGS="
set "BUILD_DEPS_CHECK=import PyInstaller, wx, accessible_output2, sound_lib, keyring, requests, fluent.runtime, livekit, sounddevice"
set "DIST_ROOT=dist\PlayAural"
set "CONTENTS_DIR="

echo [0/4] Verifying build environment...
call :select_python
if errorlevel 1 (
    echo.
    echo ERROR: No usable Python interpreter was found.
    echo Activate your virtual environment or install Python, then run this script again.
    pause
    exit /b 1
)

echo       Using Python: %PYTHON_EXE% %PYTHON_ARGS%
"%PYTHON_EXE%" %PYTHON_ARGS% -c "import sys; print(sys.version)"
if errorlevel 1 (
    echo.
    echo ERROR: The selected Python interpreter could not be started.
    pause
    exit /b 1
)

call :check_build_dependencies
if errorlevel 1 (
    echo       Required build dependencies are missing in the selected Python environment.
    echo       Attempting to install or update build dependencies now...
    call :bootstrap_build_dependencies
    if errorlevel 1 (
        echo.
        echo ERROR: Could not install the required build dependencies.
        echo Try activating your desktop build virtual environment and run:
        echo     python -m pip install --upgrade pyinstaller -r requirements.txt
        pause
        exit /b 1
    )
    call :check_build_dependencies
    if errorlevel 1 (
        echo.
        echo ERROR: Build dependencies are still missing after installation.
        echo Try activating your desktop build virtual environment and run:
        echo     python -m pip install --upgrade pyinstaller -r requirements.txt
        pause
        exit /b 1
    )
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
"%PYTHON_EXE%" %PYTHON_ARGS% -m PyInstaller --clean --noconfirm updater.spec
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
"%PYTHON_EXE%" %PYTHON_ARGS% -m PyInstaller --clean --noconfirm PlayAural.spec
if errorlevel 1 (
    echo.
    echo ERROR: PlayAural build failed. Aborting.
    pause
    exit /b 1
)
if not exist "%DIST_ROOT%\PlayAural.exe" (
    echo.
    echo ERROR: %DIST_ROOT%\PlayAural.exe was not produced.
    pause
    exit /b 1
)
echo       PlayAural built successfully.
echo.

echo [4/4] Finalizing release folder...
copy /y "dist\updater.exe" "%DIST_ROOT%\updater.exe" >nul
if errorlevel 1 (
    echo.
    echo ERROR: Failed to copy updater.exe into the release folder.
    pause
    exit /b 1
)

set "CONTENTS_DIR=%DIST_ROOT%"
if exist "%DIST_ROOT%\_internal" (
    set "CONTENTS_DIR=%DIST_ROOT%\_internal"
)

if not exist "%CONTENTS_DIR%\sounds" (
    echo.
    echo ERROR: sounds folder is missing from %CONTENTS_DIR%.
    pause
    exit /b 1
)
if not exist "%CONTENTS_DIR%\locales" (
    echo.
    echo ERROR: locales folder is missing from %CONTENTS_DIR%.
    pause
    exit /b 1
)
echo       Release folder verified.
echo       Asset content directory: %CONTENTS_DIR%
echo.

echo ============================================================
echo  Build complete.
echo  Output: dist\PlayAural\
echo ============================================================
pause
exit /b 0

:select_python
if defined VIRTUAL_ENV (
    call :try_python_candidate "%VIRTUAL_ENV%\Scripts\python.exe" ""
)
call :try_python_candidate "%CD%\.venv\Scripts\python.exe" ""
call :try_python_candidate "%CD%\venv\Scripts\python.exe" ""
call :try_python_candidate "%CD%\client\.venv\Scripts\python.exe" ""
call :try_python_candidate "%CD%\client\venv\Scripts\python.exe" ""
call :try_python_candidate "python" ""
call :try_python_candidate "py" "-3"
call :try_python_candidate "py" ""

if defined PYTHON_EXE (
    exit /b 0
)

if defined PREFERRED_PYTHON_EXE (
    set "PYTHON_EXE=%PREFERRED_PYTHON_EXE%"
    set "PYTHON_ARGS=%PREFERRED_PYTHON_ARGS%"
    exit /b 0
)

exit /b 1

:try_python_candidate
if defined PYTHON_EXE (
    exit /b 0
)

set "CANDIDATE_EXE=%~1"
set "CANDIDATE_ARGS=%~2"

if "%CANDIDATE_EXE%"=="" (
    exit /b 0
)

if /I "%CANDIDATE_EXE%"=="python" (
    where python >nul 2>nul
    if errorlevel 1 exit /b 0
) else if /I "%CANDIDATE_EXE%"=="py" (
    where py >nul 2>nul
    if errorlevel 1 exit /b 0
) else (
    if not exist "%CANDIDATE_EXE%" exit /b 0
)

"%CANDIDATE_EXE%" %CANDIDATE_ARGS% -c "import sys" >nul 2>nul
if errorlevel 1 (
    exit /b 0
)

if not defined PREFERRED_PYTHON_EXE (
    set "PREFERRED_PYTHON_EXE=%CANDIDATE_EXE%"
    set "PREFERRED_PYTHON_ARGS=%CANDIDATE_ARGS%"
)

"%CANDIDATE_EXE%" %CANDIDATE_ARGS% -c "%BUILD_DEPS_CHECK%" >nul 2>nul
if errorlevel 1 (
    echo       Candidate missing build dependencies: %CANDIDATE_EXE% %CANDIDATE_ARGS%
    exit /b 0
)

set "PYTHON_EXE=%CANDIDATE_EXE%"
set "PYTHON_ARGS=%CANDIDATE_ARGS%"
exit /b 0

:check_build_dependencies
"%PYTHON_EXE%" %PYTHON_ARGS% -c "%BUILD_DEPS_CHECK%" >nul 2>nul
exit /b %errorlevel%

:bootstrap_build_dependencies
"%PYTHON_EXE%" %PYTHON_ARGS% -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    exit /b 1
)
"%PYTHON_EXE%" %PYTHON_ARGS% -m pip install --upgrade pyinstaller -r requirements.txt
exit /b %errorlevel%
