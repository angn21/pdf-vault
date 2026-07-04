@echo off
setlocal EnableExtensions EnableDelayedExpansion
set "ROOT=%~dp0"
set "WORKER=%ROOT%pdf-worker"
set "WEB=%ROOT%web"
set "VENV_DIR=%WORKER%\.venv"
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"

echo Starting PDF Vault...
echo.

call :find_python
if errorlevel 1 (
  echo.
  echo ERROR: PDF Vault needs Python 3.9, 3.10, 3.11, or 3.12.
  echo Python 3.14 is not supported yet by some dependencies.
  echo.
  echo Install Python 3.12 from https://www.python.org/downloads/
  echo   or use Anaconda / py -3.10 if already installed.
  pause
  exit /b 1
)

echo Using Python: !PY_EXE!
!PY_EXE! --version

if exist "%VENV_PY%" (
  "%VENV_PY%" -c "import sys; raise SystemExit(0 if sys.version_info < (3, 14) else 1)" >nul 2>&1
  if errorlevel 1 (
    echo Removing incompatible venv ^(Python 3.14+^)...
    rmdir /s /q "%VENV_DIR%" 2>nul
  )
)

if not exist "%VENV_PY%" (
  echo.
  echo Setting up Python venv in pdf-worker ^(first run only^)...
  "!PY_EXE!" -m venv "%VENV_DIR%"
  if errorlevel 1 (
    echo.
    echo ERROR: Could not create a Python venv.
    pause
    exit /b 1
  )
)

"%VENV_PY%" -c "import uvicorn" >nul 2>&1
if errorlevel 1 (
  echo.
  echo Installing worker dependencies...
  "%VENV_PY%" -m pip install --upgrade pip
  "%VENV_PY%" -m pip install -r "%WORKER%\requirements.txt"
  if errorlevel 1 (
    echo.
    echo ERROR: Failed to install pdf-worker requirements.
    echo Try deleting pdf-worker\.venv and running this script again.
    pause
    exit /b 1
  )
)

echo.
echo Stopping any existing services on ports 8000 and 3000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1

start "PDF Worker" cmd /k "cd /d "%WORKER%" && set "DATA_DIR=%ROOT%data\jobs" && "%VENV_PY%" -m uvicorn main:app --host 127.0.0.1 --port 8000"
timeout /t 2 /nobreak >nul
start "PDF Vault Web" cmd /k "cd /d "%WEB%" && npm run dev"
echo.
echo PDF Worker: http://localhost:8000
echo Web UI:     http://localhost:3000
echo.
echo Close both terminal windows to stop.
goto :eof

:find_python
set "PY_EXE="
where py >nul 2>&1 && (
  for %%v in (3.12 3.11 3.10 3.9) do (
    if not defined PY_EXE (
      for /f "usebackq delims=" %%p in (`py -%%v -c "import sys; print(sys.executable)" 2^>nul`) do (
        set "PY_EXE=%%p"
      )
    )
  )
)
if not defined PY_EXE (
  if exist "%USERPROFILE%\anaconda3\python.exe" set "PY_EXE=%USERPROFILE%\anaconda3\python.exe"
)
if not defined PY_EXE (
  for /f "usebackq delims=" %%p in (`python -c "import sys; print(sys.executable)" 2^>nul`) do (
    set "PY_EXE=%%p"
  )
)
if not defined PY_EXE exit /b 1
"!PY_EXE!" -c "import sys; raise SystemExit(0 if sys.version_info < (3, 14) else 1)" >nul 2>&1
if errorlevel 1 (
  set "PY_EXE="
  exit /b 1
)
exit /b 0
