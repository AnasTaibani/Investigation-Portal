# Investigation Portal - Complete Deployment Guide

This comprehensive guide will walk you through deploying the Investigation Portal to production using:
- **Frontend**: Vercel
- **Backend**: Render
- **Database**: MongoDB Atlas

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [MongoDB Atlas Setup](#mongodb-atlas-setup)
3. [Backend Deployment (Render)](#backend-deployment-render)
4. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
5. [Database Initialization](#database-initialization)
6. [Post-Deployment Verification](#post-deployment-verification)
7. [Environment Variables Reference](#environment-variables-reference)
8. [Troubleshooting](#troubleshooting)
9. [GitHub Actions Setup](#github-actions-setup-optional)

---

## Prerequisites

Before starting, ensure you have:

- [ ] GitHub account (with your project repository)
- [ ] MongoDB Atlas account (free tier available)
- [ ] Render account (free tier available)
- [ ] Vercel account (free tier available)
- [ ] Emergent LLM Key (get from https://www.emergentagent.com/profile)
- [ ] Git installed locally
- [ ] Node.js 18+ and Python 3.11+ (for local testing)

---

## MongoDB Atlas Setup

### Step 1: Create MongoDB Cluster

1. Go to https://www.mongodb.com/cloud/atlas/register
2. Sign up or log in to your account
3. Click **"Build a Database"**
4. Select **"Shared"** (Free tier - M0)
5. Choose a cloud provider and region (closest to your users)
6. Cluster Name: `investigation-portal-prod`
7. Click **"Create Cluster"** (takes 3-5 minutes)

### Step 2: Configure Database Access

1. In left sidebar, click **"Database Access"**
2. Click **"Add New Database User"**
3. **Authentication Method**: Password
4. **Username**: `portal_admin` (or your preferred username)
5. **Password**: Click **"Autogenerate Secure Password"** and save it securely
6. **Database User Privileges**: Select **"Read and write to any database"**
7. Click **"Add User"**

### Step 3: Configure Network Access

1. In left sidebar, click **"Network Access"**
2. Click **"Add IP Address"**
3. Click **"Allow Access from Anywhere"** (0.0.0.0/0)
   - ⚠️ **Note**: For production, you can restrict this to Render's IP addresses later
4. Click **"Confirm"**

### Step 4: Get Connection String

1. Go to **"Database"** in the left sidebar
2. Click **"Connect"** on your cluster
3. Select **"Connect your application"**
4. **Driver**: Python, **Version**: 3.12 or later
5. Copy the connection string - it looks like:
   ```
   mongodb+srv://portal_admin:<password>@investigation-portal-prod.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
6. Replace `<password>` with the actual password you saved earlier
7. **Save this connection string** - you'll need it for Render

---

## Backend Deployment (Render)

### Step 1: Prepare Repository

1. Ensure your code is pushed to GitHub:
   ```bash
   git add .
   git commit -m "Prepare for production deployment"
   git push origin main
   ```

### Step 2: Create Render Account

1. Go to https://render.com/
2. Sign up with your GitHub account
3. Authorize Render to access your repositories

### Step 3: Create New Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Select **"Connect"** next to your repository

### Step 4: Configure Web Service

Fill in the following details:

**Basic Settings:**
- **Name**: `investigation-portal-backend`
- **Region**: Select closest to your users
- **Branch**: `main`
- **Root Directory**: `backend`
- **Runtime**: `Python 3`
- **Build Command**: 
  ```
  pip install -r requirements.txt
  ```
- **Start Command**: 
  ```
  uvicorn server:app --host 0.0.0.0 --port $PORT
  ```

**Instance Type:**
- Select **"Free"** (or paid tier for better performance)

### Step 5: Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"** and add the following:

| Key | Value | Notes |
|-----|-------|-------|
| `MONGO_URL` | `mongodb+srv://portal_admin:password@cluster...` | Your MongoDB Atlas connection string |
| `DB_NAME` | `investigation_portal` | Database name |
| `JWT_SECRET` | Click "Generate" or use: `openssl rand -hex 32` | Min 32 characters |
| `EMERGENT_LLM_KEY` | `your-emergent-key` | Get from emergent.ai profile |
| `FRONTEND_URL` | `https://your-app.vercel.app` | Will update after Vercel deployment |
| `ENVIRONMENT` | `production` | Enables production settings |
| `PYTHON_VERSION` | `3.11.0` | Python version |

### Step 6: Deploy

1. Click **"Create Web Service"**
2. Wait for deployment (5-10 minutes for first deployment)
3. Once deployed, you'll see a URL like: `https://investigation-portal-backend.onrender.com`
4. **Save this URL** - you'll need it for Vercel

### Step 7: Test Backend Health

1. Visit: `https://your-backend-url.onrender.com/api/health`
2. You should see:
   ```json
   {
     "status": "healthy",
     "database": "connected",
     "timestamp": "2024-01-01T00:00:00.000Z"
   }
   ```

---

## Frontend Deployment (Vercel)

### Step 1: Create Vercel Account

1. Go to https://vercel.com/signup
2. Sign up with your GitHub account
3. Authorize Vercel to access your repositories

### Step 2: Import Project

1. Click **"Add New..."** → **"Project"**
2. Import your GitHub repository
3. Click **"Import"**

### Step 3: Configure Project

**Framework Preset:** Create React App (auto-detected)

**Root Directory:** `frontend` (click "Edit" to change)

**Build & Development Settings:**
- **Build Command**: `yarn build`
- **Output Directory**: `build`
- **Install Command**: `yarn install`

### Step 4: Add Environment Variables

Click **"Environment Variables"** and add:

| Name | Value | Notes |
|------|-------|-------|
| `REACT_APP_BACKEND_URL` | `https://investigation-portal-backend.onrender.com` | Your Render backend URL (no trailing slash) |

### Step 5: Deploy

1. Click **"Deploy"**
2. Wait for deployment (3-5 minutes)
3. Once deployed, you'll see: `https://your-app.vercel.app`
4. Click **"Visit"** to open your app

### Step 6: Update Backend CORS

1. Go back to Render dashboard
2. Go to your backend service → **"Environment"**
3. Update `FRONTEND_URL` to your Vercel URL:
   ```
   https://your-app.vercel.app
   ```
4. Save changes (this will trigger a redeploy)

---

## Database Initialization

After both deployments are complete, initialize the database:

### Option 1: Using Render Shell (Recommended)

1. Go to your Render backend service
2. Click **"Shell"** tab (top right)
3. Run the initialization scripts:

```bash
# 1. Initialize database (creates indexes and admin user)
python init_database.py

# 2. Seed reference data (categories, services)
python seed_reference_data.py

# 3. Seed test users
python seed_production_users.py

# 4. (Optional) Seed demo investigations
python seed_80_cases.py
```

### Option 2: Using Local Machine with Production Database

```bash
# 1. Set environment variables locally
export MONGO_URL="your-mongodb-atlas-connection-string"
export DB_NAME="investigation_portal"

# 2. Navigate to backend folder
cd backend

# 3. Run scripts
python init_database.py
python seed_reference_data.py
python seed_production_users.py
```

### Verify Database

1. Go to MongoDB Atlas → **"Browse Collections"**
2. You should see:
   - `users`: 4 users (admin, assessor, investigators)
   - `categories`: 7 categories
   - `subcategories`: ~20 subcategories
   - `service_categories`: 11 services

---

## Post-Deployment Verification

### 1. Test Backend API

```bash
# Health check
curl https://your-backend.onrender.com/api/health

# Expected: {"status":"healthy","database":"connected",...}
```

### 2. Test Frontend

1. Open your Vercel URL in browser
2. You should see the login page
3. Check browser console for errors (F12)

### 3. Test Login

**Investigator Credentials:**
- Email: `investigator@test.com`
- Password: `Investigator@123`

**Admin Credentials:**
- Email: `admin@investigationportal.com`
- Password: `Admin@123`

### 4. Test Complete Workflow

1. ✅ **Login** with investigator credentials
2. ✅ **Navigate** to Workbench (should load)
3. ✅ **View** Dashboard (charts should display)
4. ✅ **Open** an investigation (if demo data seeded)
5. ✅ **Test** evidence upload (file selection should work)
6. ✅ **Test** findings submission
7. ✅ **Check** timeline and activities

---

## Environment Variables Reference

### Frontend (.env)

```bash
REACT_APP_BACKEND_URL=https://your-backend.onrender.com
```

### Backend (Render Environment Variables)

```bash
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
DB_NAME=investigation_portal
JWT_SECRET=your-32-character-secret-key
EMERGENT_LLM_KEY=your-emergent-llm-key
FRONTEND_URL=https://your-app.vercel.app
ENVIRONMENT=production
PYTHON_VERSION=3.11.0
```

---

## Troubleshooting

### Backend Issues

#### "Service Unavailable" or 503 Error

**Check:**
1. Render dashboard → Logs
2. Look for MongoDB connection errors
3. Verify `MONGO_URL` is correct in environment variables

**Solution:**
- Check MongoDB Atlas Network Access allows Render IPs
- Verify MongoDB user credentials are correct

#### "CORS Error" in Browser Console

**Error**: `Access to XMLHttpRequest blocked by CORS policy`

**Solution:**
1. Go to Render → Environment Variables
2. Verify `FRONTEND_URL` matches your Vercel URL exactly (no trailing slash)
3. Redeploy backend service

#### Backend Not Starting

**Check Logs in Render:**
```
ImportError: No module named 'fastapi'
```

**Solution:**
- Verify `requirements.txt` is in `/backend` folder
- Build command should be: `pip install -r requirements.txt`

### Frontend Issues

#### Blank Page or "Cannot read property"

**Check:**
1. Browser console (F12)
2. Network tab for failed API calls

**Common Issues:**
- `REACT_APP_BACKEND_URL` not set
- Backend URL has trailing slash (remove it)
- Backend is down

**Solution:**
```bash
# Vercel Dashboard → Project → Settings → Environment Variables
# Update REACT_APP_BACKEND_URL
# Redeploy from Deployments tab
```

#### "Login Failed" or 401 Errors

**Possible Causes:**
1. JWT_SECRET not set in backend
2. MongoDB connection failed
3. Users not seeded

**Solution:**
1. Check backend logs
2. Verify database was initialized
3. Try creating new user via Render shell

### Database Issues

#### "No investigations found"

**Cause:** Database not seeded

**Solution:**
```bash
# Run in Render Shell
python seed_reference_data.py
python seed_80_cases.py
```

#### "Failed to connect to MongoDB"

**Causes:**
1. Wrong connection string
2. Network access not configured
3. Wrong database user credentials

**Solution:**
1. MongoDB Atlas → Database → Connect → Copy new string
2. Update MONGO_URL in Render
3. Check Network Access allows 0.0.0.0/0

---

## GitHub Actions Setup (Optional)

For automatic deployments on every push to main:

### Step 1: Get Tokens

**Vercel:**
1. Vercel → Settings → Tokens → Create Token
2. Save as GitHub Secret: `VERCEL_TOKEN`

**Render:**
1. Render → Account Settings → API Keys → Create Key
2. Save as GitHub Secret: `RENDER_DEPLOY_HOOK_URL`
   - Format: `https://api.render.com/deploy/srv-xxxxx?key=xxxxx`

### Step 2: Add GitHub Secrets

1. GitHub repo → Settings → Secrets and variables → Actions
2. Add these secrets:
   - `VERCEL_TOKEN`
   - `VERCEL_ORG_ID` (from Vercel project settings)
   - `VERCEL_PROJECT_ID` (from Vercel project settings)
   - `RENDER_DEPLOY_HOOK_URL`
   - `BACKEND_URL` (for health checks)
   - `FRONTEND_URL` (for health checks)
   - `REACT_APP_BACKEND_URL`

### Step 3: Enable Workflow

The workflow file is already at `.github/workflows/deploy.yml`

Every push to `main` will now trigger:
1. Backend tests
2. Frontend build
3. Deploy to Vercel
4. Deploy to Render
5. Health checks

---

## Security Checklist

Before going live:

- [ ] Change default passwords (admin, assessor, investigator)
- [ ] Set strong JWT_SECRET (32+ characters, random)
- [ ] Enable MongoDB Atlas IP whitelisting (restrict to Render IPs)
- [ ] Review CORS settings (remove wildcard if possible)
- [ ] Enable HTTPS only (Vercel and Render do this by default)
- [ ] Set up MongoDB Atlas backups
- [ ] Configure Render alerts for downtime
- [ ] Review and limit Emergent LLM Key permissions

---

## Production Optimization (Optional)

### Performance

1. **Vercel:**
   - Enable Edge Network (automatic)
   - Add custom domain for better caching

2. **Render:**
   - Upgrade to paid tier (no cold starts)
   - Enable Auto-Deploy on Git push

3. **MongoDB Atlas:**
   - Upgrade to M10+ for better performance
   - Enable MongoDB Performance Advisor

### Monitoring

1. **Vercel Analytics:**
   - Enable in project settings
   - Track page views and performance

2. **Render Monitoring:**
   - Set up email alerts
   - Monitor memory and CPU usage

3. **MongoDB Atlas:**
   - Enable Performance Advisor
   - Set up alerts for database issues

---

## Support

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review deployment logs (Render/Vercel dashboards)
3. Check MongoDB Atlas metrics
4. Verify all environment variables are set correctly

---

## Deployment Checklist

Use this checklist for each deployment:

### Pre-Deployment
- [ ] All tests passing locally
- [ ] Environment variables documented
- [ ] Database backup created (if updating schema)
- [ ] Code pushed to GitHub

### MongoDB Atlas
- [ ] Cluster created
- [ ] Database user created
- [ ] Network access configured
- [ ] Connection string saved

### Render (Backend)
- [ ] Service created
- [ ] Environment variables set
- [ ] Deployment successful
- [ ] Health check passing
- [ ] Logs reviewed

### Vercel (Frontend)
- [ ] Project imported
- [ ] Environment variables set
- [ ] Build successful
- [ ] Site accessible
- [ ] No console errors

### Database Initialization
- [ ] init_database.py run
- [ ] seed_reference_data.py run
- [ ] seed_production_users.py run
- [ ] Collections verified in MongoDB Atlas

### Post-Deployment Testing
- [ ] Login works
- [ ] Dashboard loads
- [ ] Workbench displays investigations
- [ ] Investigation detail page works
- [ ] Evidence upload functional
- [ ] Findings submission works
- [ ] All API calls successful
- [ ] No CORS errors

### Security
- [ ] Default passwords changed
- [ ] JWT_SECRET is strong and unique
- [ ] MongoDB network access restricted
- [ ] HTTPS enforced everywhere

---

## Quick Reference

### Useful Commands

```bash
# Generate JWT Secret
openssl rand -hex 32

# Test backend health
curl https://your-backend.onrender.com/api/health

# Test backend login
curl -X POST https://your-backend.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"investigator@test.com","password":"Investigator@123"}'

# Trigger Render deployment
curl -X POST $RENDER_DEPLOY_HOOK_URL

# View Render logs
# Go to Render Dashboard → Service → Logs tab
```

### Important URLs

- **MongoDB Atlas**: https://cloud.mongodb.com/
- **Render Dashboard**: https://dashboard.render.com/
- **Vercel Dashboard**: https://vercel.com/dashboard
- **Emergent Profile**: https://www.emergentagent.com/profile

---

**Deployment complete!** 🎉

Your Investigation Portal is now live and accessible worldwide.
