# 🚀 Complete Setup Guide - Todo App

## Prerequisites
- Windows 11
- Docker Desktop installed
- VSCode with PowerShell terminal

---

## 📋 Step-by-Step Instructions

### **Step 1: Fix Docker Desktop (CRITICAL)**

If you're getting Docker errors, follow these steps **exactly**:

#### Option A: Quick Restart (Recommended - 90% success rate)

1. **Quit Docker Desktop completely:**
   - Right-click Docker Desktop icon in system tray (bottom-right corner, near clock)
   - Click **"Quit Docker Desktop"**

2. **Wait 10 seconds**

3. **Start Docker Desktop:**
   - Press `Win` key, type "Docker Desktop"
   - Click to open
   - **Wait** until you see **"Engine running"** in green at bottom (takes 30-60 seconds)

4. **Test Docker:**
   ```powershell
   docker info
   ```
   If this shows output without errors, proceed to Step 2!

#### Option B: If Option A Fails - Reset Docker

1. Open Docker Desktop
2. Click **Settings (⚙️ gear icon)** → **Troubleshoot**
3. Click **"Clean / Purge data"** → **"Restart"**
4. Wait for Docker to restart completely

#### Option C: Last Resort - Reinstall

1. Uninstall Docker Desktop from Windows Settings → Apps
2. Download: https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe
3. Reinstall (check "Use WSL 2 instead of Hyper-V")
4. **Restart PC once** (only time needed)

---

### **Step 2: Verify Docker is Working**

Run in PowerShell:
```powershell
docker --version
docker info
```

✅ **Success:** You see Docker version and system info
❌ **Failure:** Go back to Step 1

---

### **Step 3: Pull Confluent Kafka Images**

```powershell
cd "C:\phase 5\todo 5"

# Pull all required images
docker pull confluentinc/cp-zookeeper:7.5.0
docker pull confluentinc/cp-kafka:7.5.0
docker pull confluentinc/cp-schema-registry:7.5.0
```

This takes 5-10 minutes depending on your internet speed.

---

### **Step 4: Install Frontend Dependencies**

```powershell
cd "C:\phase 5\todo 5\frontend"
npm install
```

---

### **Step 5: Start All Services**

#### Option A: Using the Startup Script (Recommended)

```powershell
cd "C:\phase 5\todo 5"
.\start-full.bat
```

#### Option B: Manual Start

```powershell
cd "C:\phase 5\todo 5"
docker-compose up -d
```

---

### **Step 6: Verify Services**

```powershell
# Check all containers are running
docker-compose ps

# View logs if needed
docker-compose logs -f
```

---

### **Step 7: Open in Browser**

1. **Frontend:** http://localhost:3000
2. **Backend API:** http://localhost:8000
3. **API Docs (Swagger):** http://localhost:8000/docs
4. **Kafka UI:** http://localhost:8090
5. **PgAdmin:** http://localhost:8091 (login: admin@admin.com / admin)

---

## 🎯 Quick Test

1. Open http://localhost:3000
2. Click **"Sign up"**
3. Create an account:
   - Name: Your name
   - Email: test@example.com
   - Password: test123
4. Login with your credentials
5. Create tasks, mark complete, delete, etc.

---

## 🛠️ Troubleshooting

### Docker Issues

**Error: "Cannot connect to the Docker daemon"**
- Solution: Docker Desktop is not running. Follow Step 1 again.

**Error: "Access is denied"**
- Solution: Run PowerShell as Administrator once:
  ```powershell
  net start com.docker.service
  ```

**Error: "system cannot find the file specified"**
- Solution: Docker Desktop is in broken state. Quit and restart Docker Desktop.

### Port Already in Use

**Error: "Bind for 0.0.0.0:8000 failed: port is already occupied"**

```powershell
# Find and kill process using port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Services Not Starting

```powershell
# Stop all services
docker-compose down

# Remove volumes (WARNING: deletes data)
docker-compose down -v

# Rebuild and start
docker-compose up -d --build
```

### Frontend Shows Blank Page

1. Check browser console (F12)
2. Verify backend is running: http://localhost:8000/api/health
3. Restart frontend:
   ```powershell
   docker-compose restart frontend
   ```

---

## 📊 Service Architecture

```
┌─────────────┐
│   Browser   │
│ localhost   │
│   :3000     │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌──────────────┐
│  Frontend   │────▶│   Backend    │
│   (React)   │     │  (FastAPI)   │
│             │     │  localhost   │
│             │     │   :8000      │
└─────────────┘     └──────┬───────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  PostgreSQL  │  │    Redis     │  │    Kafka     │
│   :5432      │  │    :6379     │  │    :9092     │
└──────────────┘  └──────────────┘  └──────────────┘
```

---

## 🚀 Common Commands

```powershell
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Restart a service
docker-compose restart backend

# Rebuild after code changes
docker-compose up -d --build

# Remove everything (including data)
docker-compose down -v

# Check service status
docker-compose ps
```

---

## 📝 Features Included

### Frontend (React + Vite + Tailwind)
- ✅ Modern, beautiful UI
- ✅ User authentication (signup/login)
- ✅ Create, read, update, delete tasks
- ✅ Mark tasks as complete
- ✅ Search and filter tasks
- ✅ Responsive design
- ✅ Toast notifications
- ✅ Real-time stats dashboard

### Backend (FastAPI Python)
- ✅ RESTful API
- ✅ JWT authentication
- ✅ Password hashing (bcrypt)
- ✅ CORS enabled
- ✅ Auto-generated API docs
- ✅ In-memory storage (easy to replace with DB)

### Infrastructure (Docker)
- ✅ PostgreSQL database
- ✅ Redis cache
- ✅ Kafka message broker
- ✅ Schema Registry
- ✅ Kafka UI for monitoring
- ✅ PgAdmin for database management

---

## 🎉 Success Checklist

- [ ] Docker Desktop shows "Engine running"
- [ ] `docker info` works without errors
- [ ] All Confluent images pulled
- [ ] `docker-compose up -d` completes successfully
- [ ] Frontend opens at http://localhost:3000
- [ ] Can create account and login
- [ ] Can create and manage tasks
- [ ] API docs accessible at http://localhost:8000/docs

---

## 📞 Need Help?

If you're still stuck:

1. **Check Docker Desktop** - 90% of issues are Docker not running properly
2. **Restart Docker Desktop** - Quit completely and restart
3. **Check logs** - `docker-compose logs -f` shows what's happening
4. **Verify ports** - Make sure no other apps are using ports 3000, 8000, etc.

---

**Good luck! 🚀**
