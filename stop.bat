@echo off
echo ========================================
echo   RAG Agent Server Stopper
echo ========================================
echo.

echo Stopping Backend (port 8000)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000 " ^| findstr "LISTENING"') do (
    echo   Killing PID %%a
    taskkill /F /PID %%a >nul 2>&1
)

echo Stopping Frontend (port 5173)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5173 " ^| findstr "LISTENING"') do (
    echo   Killing PID %%a
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo All servers stopped.
echo.
pause
