@echo off
REM ============================================================
REM VERCEL DEPLOYMENT SCRIPT
REM ============================================================
REM This script will deploy both frontend and backend to Vercel
REM You need to be logged in to Vercel first
REM ============================================================

echo.
echo ============================================================
echo   VERCEL DEPLOYMENT - TODO APP
echo ============================================================
echo.

cd /d "%~dp0"

REM Check if Vercel CLI is installed
where vercel >nul 2>&1
if %errorlevel% neq 0 (
    echo Vercel CLI is not installed.
    echo.
    echo Installing Vercel CLI...
    npm install -g vercel
    if %errorlevel% neq 0 (
        echo Failed to install Vercel CLI. Please install manually.
        echo Run: npm install -g vercel
        pause
        exit /b 1
    )
)

echo Vercel CLI is installed.
echo.

REM Check if logged in
echo Checking Vercel login status...
vercel whoami >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo You are not logged in to Vercel.
    echo Please login first:
    echo   vercel login
    echo.
    echo Opening Vercel login page...
    start https://vercel.com/login
    echo.
    echo After login, press any key to continue...
    pause >nul
)

echo.
echo ============================================================
echo   STEP 1: DEPLOY BACKEND
echo ============================================================
echo.

cd backend

echo Current directory: %CD%
echo.
echo Deploying backend to Vercel...
echo.
echo IMPORTANT: 
echo   - When asked, confirm the deployment
echo   - Note down the backend URL after deployment
echo.

vercel --prod

if %errorlevel% neq 0 (
    echo.
    echo Backend deployment failed!
    echo Please check the error above.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   BACKEND DEPLOYED SUCCESSFULLY!
echo ============================================================
echo.
echo Please note your backend URL (it should be shown above)
echo Example: https://todo-backend-xxx.vercel.app
echo.
set /p BACKEND_URL="Enter your backend URL: "
echo.

cd ..

echo.
echo ============================================================
echo   STEP 2: DEPLOY FRONTEND
echo ============================================================
echo.

cd frontend

echo Current directory: %CD%
echo.
echo Deploying frontend to Vercel...
echo.
echo Backend URL: %BACKEND_URL%
echo.
echo IMPORTANT:
echo   - Set VITE_API_URL environment variable in Vercel dashboard
echo   - Or update vercel.json with your backend URL
echo.

vercel --prod

if %errorlevel% neq 0 (
    echo.
    echo Frontend deployment failed!
    echo Please check the error above.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   FRONTEND DEPLOYED SUCCESSFULLY!
echo ============================================================
echo.
echo Your frontend URL should be shown above.
echo Example: https://todo-frontend-xxx.vercel.app
echo.

cd ..

echo.
echo ============================================================
echo   DEPLOYMENT COMPLETE!
echo ============================================================
echo.
echo Backend:  %BACKEND_URL%
echo Frontend: (see Vercel dashboard)
echo.
echo Next Steps:
echo   1. Go to Vercel Dashboard: https://vercel.com/dashboard
echo   2. Set environment variable for frontend:
echo      VITE_API_URL = %BACKEND_URL%
echo   3. Redeploy frontend if needed
echo   4. Test your app!
echo.
echo Test URLs:
echo   Backend Health: %BACKEND_URL%/api/health
echo   Frontend App:   (your frontend URL)
echo.
start https://vercel.com/dashboard
echo.
pause
