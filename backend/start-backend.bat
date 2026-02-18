@echo off
REM ============================================================
REM Start MERN Backend Server
REM ============================================================

echo.
echo ============================================================
echo   TODO Backend - Starting...
echo ============================================================
echo.

cd /d "%~dp0"

echo Checking if port 8000 is already in use...
netstat -ano | findstr :8000 >nul 2>&1
if %errorlevel% equ 0 (
    echo ERROR: Port 8000 is already in use!
    echo Please stop the existing process or use a different port.
    echo.
    pause
    exit /b 1
)

echo Starting backend server on http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.

node server.js
