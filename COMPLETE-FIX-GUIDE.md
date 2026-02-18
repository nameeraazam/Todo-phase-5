# 🚀 Complete Fix Guide - Todo App (MERN + Kafka + Docker)

**For Windows 11 + PowerShell**

---

## 📋 Quick Fix (One Command)

```powershell
# Open PowerShell in project folder
cd "C:\phase 5\todo 5"

# Run the fix script
.\FIX-EVERYTHING.ps1
```

This will fix everything automatically!

---

## 🔧 Manual Step-by-Step Fix

### **Step 1: Fix Docker Desktop**

**Problem:** `dockerDesktopLinuxEngine pipe not found`

**Solution:**

1. **Quit Docker Desktop completely:**
   - Right-click Docker icon in system tray (near clock)
   - Click **"Quit Docker Desktop"**

2. **Wait 10 seconds**

3. **Restart Docker Desktop:**
   - Press `Win` key → type "Docker Desktop" → Open
   - Wait until you see **"Engine running"** in green at bottom

4. **Verify Docker:**
   ```powershell
   docker info
   ```
   
   ✅ Success: Shows Docker info  
   ❌ Failure: Restart your PC

---

### **Step 2: Stop Existing Containers**

```powershell
cd "C:\phase 5\todo 5"

# Stop all containers
docker-compose down
docker-compose -f kafka-docker-compose.yml down
```

---

### **Step 3: Pull Kafka Images**

```powershell
docker pull confluentinc/cp-zookeeper:7.5.0
docker pull confluentinc/cp-kafka:7.5.0
docker pull confluentinc/cp-schema-registry:7.5.0
docker pull provectuslabs/kafka-ui:latest
```

⏱️ Takes 5-10 minutes depending on internet

---

### **Step 4: Start Kafka Services**

```powershell
docker-compose -f kafka-docker-compose.yml up -d
```

Wait 30 seconds for Kafka to start.

---

### **Step 5: Verify Kafka is Running**

```powershell
docker-compose -f kafka-docker-compose.yml ps
```

You should see:
- `todo-zookeeper` - healthy
- `todo-kafka` - healthy
- `todo-schema-registry` - running
- `todo-kafka-ui` - running

---

### **Step 6: Install Backend Dependencies**

```powershell
cd "C:\phase 5\todo 5\backend"
npm install
```

---

### **Step 7: Start Backend Server**

```powershell
# In backend folder
node server.js
```

You should see:
```
Mock API server is running on http://localhost:8000
```

---

### **Step 8: Start Frontend (New Terminal)**

Open **new PowerShell window**:

```powershell
cd "C:\phase 5\todo 5\frontend"
npm run dev
```

Frontend runs on: **http://localhost:3000**

---

## ✅ Verify Everything Works

### **1. Test Backend API**

```powershell
# Health check
curl http://localhost:8000/api/health

# Should return: {"status":"OK",...}
```

### **2. Test Login**

```powershell
curl -X POST http://localhost:8000/api/auth/signin `
  -H "Content-Type: application/json" `
  -d "{\"email\":\"test@example.com\",\"password\":\"test123\"}"
```

Should return user + token.

### **3. Test Create Task**

```powershell
# First get token from login response, then:
curl -X POST http://localhost:8000/api/tasks `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer YOUR_TOKEN_HERE" `
  -d "{\"title\":\"Test Task\",\"description\":\"Testing\"}"
```

Should return created task.

### **4. Test Kafka UI**

Open browser: **http://localhost:8090**

You should see Kafka cluster dashboard.

---

## 🛠️ Common Issues & Solutions

### **Issue 1: Docker "Cannot connect to daemon"**

**Solution:**
```powershell
# Quit Docker Desktop from system tray
# Wait 10 seconds
# Restart Docker Desktop
# Wait for "Engine running"
```

---

### **Issue 2: Port already in use**

**Solution:**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill it (replace PID with actual number)
taskkill /PID <PID> /F
```

---

### **Issue 3: "Failed to create task"**

**Cause:** Backend restarted, lost in-memory users

**Solution:** Create new account:
1. Go to http://localhost:3000
2. Click "Sign up"
3. Create account:
   - Name: Your name
   - Email: you@example.com
   - Password: yourpassword
4. Login with same credentials
5. Create task - will work!

---

### **Issue 4: Kafka containers not starting**

**Solution:**
```powershell
# Remove old containers
docker-compose -f kafka-docker-compose.yml down -v

# Rebuild
docker-compose -f kafka-docker-compose.yml up -d --build

# Check logs
docker-compose -f kafka-docker-compose.yml logs -f
```

---

## 📊 Service Status Commands

```powershell
# Check all containers
docker ps

# Check Kafka specifically
docker-compose -f kafka-docker-compose.yml ps

# View Kafka logs
docker-compose -f kafka-docker-compose.yml logs -f kafka

# View Zookeeper logs
docker-compose -f kafka-docker-compose.yml logs -f zookeeper

# Stop all Kafka services
docker-compose -f kafka-docker-compose.yml down

# Restart all services
docker-compose -f kafka-docker-compose.yml up -d --build
```

---

## 🎯 Quick Start Commands

### **Start Everything:**
```powershell
cd "C:\phase 5\todo 5"

# Start Kafka
docker-compose -f kafka-docker-compose.yml up -d

# Start backend (in backend folder)
cd backend
node server.js

# Start frontend (in new terminal, frontend folder)
cd ..\frontend
npm run dev
```

### **Stop Everything:**
```powershell
cd "C:\phase 5\todo 5"
docker-compose -f kafka-docker-compose.yml down
# Press Ctrl+C in backend and frontend terminals
```

---

## 📁 Project Structure

```
C:\phase 5\todo 5\
├── backend/
│   ├── server.js          # Express backend
│   ├── package.json
│   └── node_modules/
├── frontend/
│   ├── src/
│   ├── package.json
│   └── node_modules/
├── kafka-docker-compose.yml
├── FIX-EVERYTHING.ps1
└── README.md
```

---

## 🔗 Service URLs

| Service | URL | Port |
|---------|-----|------|
| Frontend | http://localhost:3000 | 3000 |
| Backend API | http://localhost:8000 | 8000 |
| API Docs | http://localhost:8000/docs | 8000 |
| Kafka UI | http://localhost:8090 | 8090 |
| Kafka | localhost:9092 | 9092 |
| Zookeeper | localhost:2181 | 2181 |
| Schema Registry | localhost:8081 | 8081 |

---

## 📝 Test Credentials

**Create your own account:**
1. Open http://localhost:3000
2. Click "Sign up"
3. Enter your details
4. Login and start using!

---

## 🚀 GitHub Push

After everything works:

```powershell
cd "C:\phase 5\todo 5"

# Add all changes
git add -A

# Commit
git commit -m "fix: Complete MERN + Kafka setup working"

# Push
git push origin 003-advanced-todo-features
```

---

## ❓ Need Help?

1. **Docker issues:** Restart Docker Desktop or PC
2. **Task creation fails:** Create new account (backend uses in-memory storage)
3. **Port conflicts:** Kill processes using `netstat -ano | findstr :PORT`
4. **Kafka not starting:** Run `docker-compose -f kafka-docker-compose.yml down -v` then restart

---

**Good luck! 🎉**
