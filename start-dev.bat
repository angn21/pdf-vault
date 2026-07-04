@echo off
echo Starting PDF Vault...
echo.
echo Stopping any existing worker on port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
start "PDF Worker" cmd /k "cd /d %~dp0pdf-worker && set "DATA_DIR=%~dp0data\jobs" && python -m uvicorn main:app --host 127.0.0.1 --port 8000"
timeout /t 2 /nobreak >nul
start "PDF Vault Web" cmd /k "cd /d %~dp0web && npm run dev"
echo.
echo PDF Worker: http://localhost:8000
echo Web UI:     http://localhost:3000
echo.
echo Close both terminal windows to stop.
