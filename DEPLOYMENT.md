# 🚀 Vercel Deployment Guide

## ✅ GitHub Pe Push Ho Gaya!

**Repository:** https://github.com/nameeraazam/Todo-phase-5

---

## 📦 Step 1: Deploy Backend to Vercel

### Option A: Vercel Dashboard (Recommended)

1. **Vercel pe jao:** https://vercel.com
2. **Login with GitHub**
3. **"Add New Project"** click karo
4. **Import GitHub Repository:**
   - Repository: `Todo-phase-5`
   - **Root Directory:** `backend` (important!)
   - Framework Preset: `Node.js`
5. **Environment Variables:**
   ```
   NODE_ENV = production
   ```
6. **"Deploy"** click karo

### Option B: Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy backend
cd backend
vercel --prod
```

**Backend URL note kar lo:** `https://your-backend.vercel.app`

---

## 📦 Step 2: Deploy Frontend to Vercel

### Option A: Vercel Dashboard

1. **"Add New Project"** click karo
2. **Import GitHub Repository:**
   - Repository: `Todo-phase-5`
   - **Root Directory:** `frontend` (important!)
   - Framework Preset: `Vite`
3. **Environment Variables:**
   ```
   VITE_API_URL = https://your-backend.vercel.app
   ```
   (Replace with your actual backend URL from Step 1)
4. **"Deploy"** click karo

### Option B: Vercel CLI

```bash
# Deploy frontend
cd frontend
vercel --prod
```

**Frontend URL:** `https://your-frontend.vercel.app`

---

## 🎯 Step 3: Test Deployment

### Frontend Test
1. Open: `https://your-frontend.vercel.app`
2. Login with any email/password
3. Create tasks
4. Everything should work!

### Backend API Test
```bash
# Health check
curl https://your-backend.vercel.app/api/health

# Login
curl -X POST https://your-backend.vercel.app/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"123"}'
```

---

## ⚠️ Important Notes

### Backend Considerations

**In-Memory Storage:**
- Backend uses in-memory storage (arrays)
- **Data lost on server restart** (Vercel serverless functions)
- For production, connect to MongoDB/PostgreSQL

**Solution for Production:**
```javascript
// Add MongoDB connection in backend/server.js
import mongoose from 'mongoose';

mongoose.connect(process.env.MONGODB_URI);
// Then create User and Task models
```

### Frontend Considerations

**API URL:**
- Make sure `VITE_API_URL` is set correctly in Vercel
- Local development: `http://localhost:8000`
- Production: `https://your-backend.vercel.app`

---

## 🔧 Environment Variables

### Backend (Vercel Dashboard → Settings → Environment Variables)

```
NODE_ENV=production
JWT_SECRET=your-super-secret-key-change-this
MONGODB_URI=mongodb://user:pass@host:port/db (optional for production)
```

### Frontend (Vercel Dashboard → Settings → Environment Variables)

```
VITE_API_URL=https://your-backend.vercel.app
```

---

## 🐛 Troubleshooting

### Issue: Frontend can't connect to backend

**Solution:**
1. Check `VITE_API_URL` in Vercel frontend settings
2. Make sure it's the full URL: `https://your-backend.vercel.app`
3. Redeploy frontend after changing env variable

### Issue: Backend 500 error

**Solution:**
1. Check Vercel Functions logs
2. Make sure all dependencies in `package.json`
3. Check `vercel.json` configuration

### Issue: CORS error

**Solution:**
Backend already has CORS enabled. If still issue:
```javascript
// In backend/server.js
app.use(cors({
  origin: ['https://your-frontend.vercelel.app'],
  credentials: true
}));
```

---

## 📊 Vercel Deployment Structure

```
Todo-phase-5/
├── backend/
│   ├── server.js         → Deployed to Vercel Functions
│   ├── package.json      → Dependencies
│   └── vercel.json       → Vercel config
│
└── frontend/
    ├── src/              → Built as static files
    ├── package.json      → Build dependencies
    ├── vercel.json       → Vercel config
    └── dist/             → Production build
```

---

## 🎉 Success Checklist

- [ ] Backend deployed to Vercel
- [ ] Frontend deployed to Vercel
- [ ] `VITE_API_URL` set correctly
- [ ] Can login with any password
- [ ] Can create tasks
- [ ] No CORS errors
- [ ] API health check passes

---

## 🔗 Quick Links

- **Vercel Dashboard:** https://vercel.com/dashboard
- **Vercel Docs:** https://vercel.com/docs
- **Vercel CLI:** https://vercel.com/docs/cli
- **Your Repo:** https://github.com/nameeraazam/Todo-phase-5

---

## 🚀 One-Click Deploy

### Frontend
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/nameeraazam/Todo-phase-5&project-name=todo-frontend&repository-name=todo-frontend&root-directory=frontend)

### Backend
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/nameeraazam/Todo-phase-5&project-name=todo-backend&repository-name=todo-backend&root-directory=backend)

---

**Happy Deploying! 🎉**
