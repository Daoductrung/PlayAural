@echo off
REM Switch to the script's directory ensures we operate on the right files
cd /d "%~dp0"

echo ==========================================
echo      PLAY AURAL CLEANUP UTILITY
echo ==========================================
echo Working Directory: %CD%

echo [1/4] Closing running Python processes...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM pythonw.exe /T >nul 2>&1
echo Done.

echo [2/4] Removing temporary cache files (__pycache__)...
powershell -NoProfile -Command "Get-ChildItem -Path . -Recurse -Directory -Filter '__pycache__' | ForEach-Object { Write-Host 'Deleting: ' $_.FullName; Remove-Item -LiteralPath $_.FullName -Recurse -Force -ErrorAction SilentlyContinue }"

echo [3/4] Removing server data and logs...
echo [3/4] Removing local server development data...
if exist "server\playaural.db" (
    del /f /q "server\playaural.db"
    echo Deleted server\playaural.db
)
if exist "playaural.db" (
    del /f /q "playaural.db"
    echo Deleted playaural.db
)
if exist "server\errors.log" (
    del /f /q "server\errors.log"
    echo Deleted server\errors.log
)
if exist "server\uploads" (
    rmdir /s /q "server\uploads"
    echo Deleted server\uploads directory
)
if exist "server\database" (
    rmdir /s /q "server\database"
    echo Deleted server\database directory
)

echo [4/4] Removing client configuration (.playaural)...
powershell -NoProfile -Command "$path = Join-Path $env:APPDATA 'ddt.one\PlayAural'; if (Test-Path $path) { Write-Host 'Deleting: ' $path; Remove-Item -LiteralPath $path -Recurse -Force } else { Write-Host 'Config not found (clean).' }"

echo ==========================================
echo CLEANUP COMPLETE!
echo You can now restart the application freshly.
echo ==========================================
pause
