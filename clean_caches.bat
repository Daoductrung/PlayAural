@echo off
echo ============================================================
echo  PlayAural Cache Cleaner
echo ============================================================
echo.

:: --- __pycache__ directories ---
echo Cleaning __pycache__ directories...
FOR /d /r . %%d IN (__pycache__) DO @IF EXIST "%%d" (
    echo   Removing "%%d"
    rd /s /q "%%d"
)

:: --- Compiled Python files ---
echo Cleaning .pyc files...
FOR /r . %%f IN (*.pyc) DO @IF EXIST "%%f" (
    echo   Removing "%%f"
    del /q "%%f"
)
echo Cleaning .pyo files...
FOR /r . %%f IN (*.pyo) DO @IF EXIST "%%f" (
    echo   Removing "%%f"
    del /q "%%f"
)

:: --- pytest cache ---
echo Cleaning .pytest_cache directories...
FOR /d /r . %%d IN (.pytest_cache) DO @IF EXIST "%%d" (
    echo   Removing "%%d"
    rd /s /q "%%d"
)

:: --- mypy cache ---
echo Cleaning .mypy_cache directories...
FOR /d /r . %%d IN (.mypy_cache) DO @IF EXIST "%%d" (
    echo   Removing "%%d"
    rd /s /q "%%d"
)

:: --- ruff cache ---
echo Cleaning .ruff_cache directories...
FOR /d /r . %%d IN (.ruff_cache) DO @IF EXIST "%%d" (
    echo   Removing "%%d"
    rd /s /q "%%d"
)

:: --- tox ---
echo Cleaning .tox directories...
FOR /d /r . %%d IN (.tox) DO @IF EXIST "%%d" (
    echo   Removing "%%d"
    rd /s /q "%%d"
)

echo.
echo ============================================================
echo  Done.
echo ============================================================
pause
