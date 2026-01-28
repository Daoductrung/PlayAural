@echo off
echo Deleting all __pycache__ folders...
FOR /d /r . %%d IN (__pycache__) DO @IF EXIST "%%d" (
    echo Removing "%%d"
    rd /s /q "%%d"
)
echo Done.
pause
