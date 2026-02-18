@echo off
REM ============================================
REM Complete Startup Script for Todo App
REM ============================================

echo.
echo ============================================
echo   Advanced Todo App - Full Stack Startup
echo ============================================
echo.

REM Step 1: Check Docker
echo [Step 1/5] Checking Docker status...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Docker is not running!
    echo.
    echo Please follow these steps:
    echo   1. Open Docker Desktop from Start Menu
    echo   2. Wait until you see "Engine running" at bottom
    echo   3. Run this script again
    echo.
    pause
    exit /b 1
)
echo Docker is running!

REM Step 2: Navigate to project root
echo.
echo [Step 2/5] Navigating to project directory...
cd /d "%~dp0"
echo Project directory: %CD%

REM Step 3: Pull images
echo.
echo [Step 3/5] Pulling Docker images (this may take a few minutes)...
docker-compose pull

REM Step 4: Start services
echo.
echo [Step 4/5] Starting all services...
docker-compose up -d

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to start services!
    pause
    exit /b 1
)

REM Step 5: Wait and verify
echo.
echo [Step 5/5] Waiting for services to be ready...
timeout /t 15 /nobreak >nul

echo.
echo ============================================
echo   Services Started Successfully!
echo ============================================
echo.
echo Backend API:    http://localhost:8000
echo Frontend:       http://localhost:3000
echo PostgreSQL:     localhost:5432
echo Redis:          localhost:6379
echo Kafka:          localhost:9092
echo.
echo Admin UIs:
echo   - Kafka UI:   http://localhost:8090
echo   - PgAdmin:    http://localhost:8091
echo.
echo API Documentation:
echo   - Swagger UI: http://localhost:8000/docs
echo   - ReDoc:      http://localhost:8000/redoc
echo.
echo ============================================
echo.
echo Opening frontend in your browser...
start http://localhost:3000

echo.
echo To stop all services, run: docker-compose down
echo ============================================
echo.
pause
