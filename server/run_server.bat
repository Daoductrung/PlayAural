@echo off
echo Starting PlayAural Server...
echo.
uv sync
uv run python main.py
pause
