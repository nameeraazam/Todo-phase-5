@echo off
REM Shutdown Script for Advanced Todo Features
REM Run this from project root to stop all services

echo ============================================
echo  Advanced Todo - Stopping Services
echo ============================================
echo.

docker-compose down

echo.
echo ============================================
echo  All services stopped.
echo ============================================
