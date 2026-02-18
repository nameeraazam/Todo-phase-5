@echo off
REM Startup Script for Advanced Todo Features - Local Development
REM Run this from project root to start all services

echo ============================================
echo  Advanced Todo - Local Development Startup
echo ============================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running. Please start Docker Desktop first.
    exit /b 1
)

echo [1/3] Starting Docker Compose services...
docker-compose up -d

if %errorlevel% neq 0 (
    echo ERROR: Failed to start Docker Compose.
    exit /b 1
)

echo.
echo [2/3] Waiting for services to be ready...
timeout /t 10 /nobreak >nul

echo.
echo [3/3] Verifying services...
docker-compose ps

echo.
echo ============================================
echo  Services Started Successfully!
echo ============================================
echo.
echo Available Services:
echo   - Kafka:        localhost:9092
echo   - Zookeeper:    localhost:2181
echo   - PostgreSQL:   localhost:5432
echo   - Redis:        localhost:6379
echo   - Dapr:         localhost:50005
echo.
echo Admin UIs:
echo   - Kafka UI:     http://localhost:8090
echo   - PgAdmin:      http://localhost:8091
echo   - Dapr Dashboard: http://localhost:8080
echo.
echo Next Steps:
echo   1. cd backend
echo   2. dapr run --app-id todo-backend --app-port 8000 --dapr-http-port 3500 --components-path ./dapr/components -- uvicorn src.api.main:app --reload --port 8000
echo.
echo To stop services: docker-compose down
echo ============================================
