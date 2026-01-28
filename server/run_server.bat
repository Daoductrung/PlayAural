@echo off
echo Starting PlayAural v0.1 Server...
echo.
uv sync
uv run python main.py
pause
