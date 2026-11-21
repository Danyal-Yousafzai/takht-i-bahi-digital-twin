@echo off
echo Starting Takht-i-Bahi Digital Twin Web Server...
start "" http://localhost:8000
python -m http.server 8000
pause
