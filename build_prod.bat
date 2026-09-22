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
set "BUILD_DEPS_CHECK=import PyInstaller, wx, accessible_output2, cosmos, keyring, requests, psutil, websockets, fluent.runtime, numpy, sounddevice; from livekit import rtc; assert callable(cosmos.SoundManager); assert callable(rtc.Room)"
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
call :require_release_file "%CONTENTS_DIR%\accessible_output2\lib\nvdaControllerClient64.dll"
if errorlevel 1 goto :release_verification_failed
call :require_release_file "%CONTENTS_DIR%\_sounddevice_data\portaudio-binaries\libportaudio64bit.dll"
if errorlevel 1 goto :release_verification_failed
call :require_release_file "%CONTENTS_DIR%\livekit\rtc\resources\livekit_ffi.dll"
if errorlevel 1 goto :release_verification_failed
call :require_release_file "%CONTENTS_DIR%\livekit\rtc\resources\LICENSE.md"
if errorlevel 1 goto :release_verification_failed
call :require_release_file "%CONTENTS_DIR%\cosmos\cosmos.pyd"
if errorlevel 1 goto :release_verification_failed
call :require_release_file "%CONTENTS_DIR%\cosmos\phonon.dll"
if errorlevel 1 goto :release_verification_failed
call :require_release_file "%CONTENTS_DIR%\cosmos\LICENSE"
if errorlevel 1 goto :release_verification_failed
call :require_release_file "%CONTENTS_DIR%\cosmos\third_party\steam_audio\LICENSE.md"
if errorlevel 1 goto :release_verification_failed
call :require_release_file "%CONTENTS_DIR%\cosmos\third_party\steam_audio\THIRDPARTY.md"
if errorlevel 1 goto :release_verification_failed
call :require_release_file "%CONTENTS_DIR%\cosmos\third_party\steam_audio\TRADEMARK_RIGHTS.md"
if errorlevel 1 goto :release_verification_failed
call :require_release_file "%CONTENTS_DIR%\cosmos\third_party\steam_audio\UPSTREAM.json"
if errorlevel 1 goto :release_verification_failed
"%PYTHON_EXE%" %PYTHON_ARGS% -c "import hashlib, json, pathlib, zipfile; root = pathlib.Path(r'%CONTENTS_DIR%\cosmos'); notices = root / 'third_party' / 'steam_audio'; wheels = list(pathlib.Path('client/vendor').glob('cosmos-*.whl')); assert len(wheels) == 1; wheel = zipfile.ZipFile(wheels[0]); names = wheel.namelist(); digest = lambda data: hashlib.sha256(data).hexdigest(); packaged = lambda path: path.read_bytes(); assert digest(packaged(root / 'cosmos.pyd')) == digest(wheel.read('cosmos/cosmos.pyd')); assert digest(packaged(root / 'phonon.dll')) == digest(wheel.read('cosmos/phonon.dll')); license_name = next(name for name in names if name.endswith('.dist-info/licenses/LICENSE')); assert packaged(root / 'LICENSE') == wheel.read(license_name); manifest = json.loads(packaged(notices / 'UPSTREAM.json')); assert digest(packaged(root / 'phonon.dll')) == manifest['artifacts']['phonon.dll']; assert all(digest(packaged(notices / name)) == manifest['artifacts'][name] == digest(wheel.read('cosmos/third_party/steam_audio/' + name)) for name in ('LICENSE.md', 'THIRDPARTY.md', 'TRADEMARK_RIGHTS.md'))"
if errorlevel 1 (
    echo.
    echo ERROR: Packaged Cosmos or Steam Audio files failed integrity verification.
    goto :release_verification_failed
)

if exist "%CONTENTS_DIR%\accessible_output2-*.dist-info" (
    echo.
    echo ERROR: Redundant accessible_output2 distribution metadata was packaged.
    goto :release_verification_failed
)
if exist "%CONTENTS_DIR%\livekit-*.dist-info" (
    echo.
    echo ERROR: Redundant LiveKit distribution metadata was packaged.
    goto :release_verification_failed
)
if exist "%CONTENTS_DIR%\cosmos\target" (
    echo.
    echo ERROR: Cosmos source build artifacts were packaged.
    goto :release_verification_failed
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
if /I "%PYTHON_EXE%"=="%CD%\client\.venv\Scripts\python.exe" (
    where uv >nul 2>nul
    if not errorlevel 1 (
        uv sync --project client --extra dev
        if errorlevel 1 exit /b 1
        uv pip install --python "%PYTHON_EXE%" --upgrade "pyinstaller>=6.0"
        if errorlevel 1 exit /b 1
        exit /b 0
    )
)
"%PYTHON_EXE%" %PYTHON_ARGS% -m ensurepip --upgrade >nul 2>nul
"%PYTHON_EXE%" %PYTHON_ARGS% -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    exit /b 1
)
"%PYTHON_EXE%" %PYTHON_ARGS% -m pip install --upgrade pyinstaller -r requirements.txt
exit /b %errorlevel%

:require_release_file
if not exist "%~1" (
    echo.
    echo ERROR: Required release file is missing: %~1
    exit /b 1
)
for %%F in ("%~1") do if %%~zF EQU 0 (
    echo.
    echo ERROR: Required release file is empty: %~1
    exit /b 1
)
exit /b 0

:release_verification_failed
pause
exit /b 1
