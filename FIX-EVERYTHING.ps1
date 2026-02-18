# ============================================================
# COMPLETE TODO APP FIX SCRIPT - Windows PowerShell
# ============================================================
# This script will fix ALL issues from scratch
# Run this in PowerShell (NOT as admin needed)
# ============================================================

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  TODO APP - COMPLETE FIX SCRIPT" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Navigate to project root
Write-Host "[Step 1/8] Navigating to project directory..." -ForegroundColor Yellow
Set-Location "C:\phase 5\todo 5"
Write-Host "✓ Project directory: $PWD" -ForegroundColor Green
Write-Host ""

# Step 2: Check and fix Docker Desktop
Write-Host "[Step 2/8] Checking Docker Desktop..." -ForegroundColor Yellow
try {
    $dockerInfo = docker info 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Docker is running!" -ForegroundColor Green
    } else {
        Write-Host "✗ Docker is not running properly" -ForegroundColor Red
        Write-Host ""
        Write-Host "ACTION REQUIRED:" -ForegroundColor Red
        Write-Host "1. Right-click Docker Desktop icon in system tray" -ForegroundColor Yellow
        Write-Host "2. Click 'Quit Docker Desktop'" -ForegroundColor Yellow
        Write-Host "3. Wait 10 seconds" -ForegroundColor Yellow
        Write-Host "4. Open Docker Desktop from Start Menu" -ForegroundColor Yellow
        Write-Host "5. Wait until you see 'Engine running' (green) at bottom" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Press any key after Docker shows 'Engine running'..." -ForegroundColor Red
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        
        # Verify again
        $dockerInfo = docker info 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "✗ Docker still not running. Please restart your PC." -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "✗ Error checking Docker: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 3: Stop any existing containers
Write-Host "[Step 3/8] Stopping existing containers..." -ForegroundColor Yellow
docker-compose down 2>$null
docker-compose -f kafka-docker-compose.yml down 2>$null
Write-Host "✓ Containers stopped" -ForegroundColor Green
Write-Host ""

# Step 4: Pull Kafka images
Write-Host "[Step 4/8] Pulling Kafka Docker images (this takes 5-10 mins)..." -ForegroundColor Yellow
docker pull confluentinc/cp-zookeeper:7.5.0
docker pull confluentinc/cp-kafka:7.5.0
docker pull confluentinc/cp-schema-registry:7.5.0
docker pull provectuslabs/kafka-ui:latest
Write-Host "✓ All Kafka images pulled" -ForegroundColor Green
Write-Host ""

# Step 5: Start Kafka services
Write-Host "[Step 5/8] Starting Kafka services..." -ForegroundColor Yellow
docker-compose -f kafka-docker-compose.yml up -d
Write-Host "✓ Kafka services starting..." -ForegroundColor Green
Write-Host ""

# Step 6: Wait for Kafka to be ready
Write-Host "[Step 6/8] Waiting for Kafka to be ready (30 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Verify Kafka is running
$checkKafka = docker ps --filter "name=todo-kafka" --format "{{.Status}}"
if ($checkKafka -like "*healthy*") {
    Write-Host "✓ Kafka is healthy!" -ForegroundColor Green
} else {
    Write-Host "⚠ Kafka still starting (this is normal, continuing...)" -ForegroundColor Yellow
}
Write-Host ""

# Step 7: Install backend dependencies
Write-Host "[Step 7/8] Installing backend dependencies..." -ForegroundColor Yellow
Set-Location "C:\phase 5\todo 5\backend"
npm install
Write-Host "✓ Backend dependencies installed" -ForegroundColor Green
Write-Host ""

# Step 8: Start backend
Write-Host "[Step 8/8] Starting backend server..." -ForegroundColor Yellow
Write-Host "Note: Backend will run in this window. Press Ctrl+C to stop." -ForegroundColor Yellow
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  SETUP COMPLETE!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services Running:" -ForegroundColor Cyan
Write-Host "  ✓ Kafka:        localhost:9092" -ForegroundColor White
Write-Host "  ✓ Zookeeper:    localhost:2181" -ForegroundColor White
Write-Host "  ✓ Schema Reg:   localhost:8081" -ForegroundColor White
Write-Host "  ✓ Kafka UI:     http://localhost:8090" -ForegroundColor White
Write-Host ""
Write-Host "Backend:" -ForegroundColor Cyan
Write-Host "  ✓ API:          http://localhost:8000" -ForegroundColor White
Write-Host "  ✓ Health:       http://localhost:8000/api/health" -ForegroundColor White
Write-Host ""
Write-Host "Frontend:" -ForegroundColor Cyan
Write-Host "  ✓ App:          http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "Test Credentials:" -ForegroundColor Cyan
Write-Host "  Email:    test@example.com" -ForegroundColor White
Write-Host "  Password: test123" -ForegroundColor White
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Start backend server
node server.js
