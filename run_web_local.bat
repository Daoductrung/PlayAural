@echo off
cd web_client
echo Starting local web server at http://localhost:8080
echo Press Ctrl+C to stop
start http://localhost:8080
python -m http.server 8080
