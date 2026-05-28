@echo off
echo ========================================
echo   RAG Agent Server Starter
echo ========================================
echo.

cd /d "%~dp0"

echo [0/3] Cleaning up existing processes...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000 " ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5173 " ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 /nobreak >nul

echo [1/3] Starting Backend (port 8000)...
start "RAG-Backend" cmd /k "cd /d %~dp0 && .venv\Scripts\python.exe -m uvicorn project_agent.main:app --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo [2/3] Starting Frontend (port 5173)...
start "RAG-Frontend" cmd /k "cd /d %~dp0\frontend && npx vite --host 0.0.0.0 --port 5173"

echo.
echo [3/3] Done!
echo.
echo ========================================
echo   Servers started!
echo   Backend:  http://127.0.0.1:8000
echo   Frontend: http://127.0.0.1:5173
echo ========================================
echo.
echo To stop: run stop.bat or close the windows
echo.
pause
