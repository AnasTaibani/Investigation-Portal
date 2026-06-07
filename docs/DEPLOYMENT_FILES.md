# Investigation Portal - Deployment Files Summary

## 📦 Complete Deployment Package

This document lists all deployment-related files and their purposes.

---

## Core Configuration Files

### 1. `vercel.json`
**Purpose**: Vercel deployment configuration for frontend  
**Location**: Project root  
**Description**: Configures build settings, environment variables, rewrites, and security headers for Vercel deployment

### 2. `render.yaml`
**Purpose**: Render deployment configuration for backend  
**Location**: Project root  
**Description**: Defines web service settings, build/start commands, and environment variables for Render

### 3. `.env.example`
**Purpose**: Complete environment variables template  
**Location**: Project root  
**Description**: Master template showing all required environment variables for both frontend and backend

---

## Environment Configuration

### 4. `frontend/.env.example`
**Purpose**: Frontend development environment template  
**Location**: `/frontend/`  
**Contains**: `REACT_APP_BACKEND_URL`

### 5. `frontend/.env.production.example`
**Purpose**: Frontend production environment template  
**Location**: `/frontend/`  
**Contains**: Production backend URL configuration

### 6. `backend/.env.example`
**Purpose**: Backend development environment template  
**Location**: `/backend/`  
**Contains**: MongoDB, JWT, Emergent LLM key, CORS configuration

### 7. `backend/.env.production.example`
**Purpose**: Backend production environment template  
**Location**: `/backend/`  
**Contains**: Production database and service URLs

---

## Database Initialization Scripts

### 8. `backend/init_database.py`
**Purpose**: Initialize database with indexes and default admin  
**When to run**: Once after MongoDB Atlas setup  
**Creates**:
- All required indexes
- Default admin user
- Collection structure verification

**Default Credentials**:
- Email: admin@investigationportal.com
- Password: Admin@123

### 9. `backend/seed_reference_data.py`
**Purpose**: Seed categories, subcategories, and services  
**When to run**: After `init_database.py`  
**Creates**:
- 7 investigation categories
- 20+ subcategories
- 11 service types

### 10. `backend/seed_production_users.py`
**Purpose**: Create test users for all roles  
**When to run**: After `seed_reference_data.py`  
**Creates**:
- Admin user
- Assessor user
- 2 Investigator users

### 11. `backend/seed_80_cases.py`
**Purpose**: Generate 80-90 demo investigation cases  
**When to run**: Optional - for testing/demonstration  
**Creates**:
- 30-35 Assigned cases (no evidence)
- 45-50 Mixed status cases (with evidence)

### 12. `backend/setup_production_db.sh`
**Purpose**: Automated database setup script  
**When to run**: One-command setup after deployment  
**Executes**:
- All initialization scripts in correct order
- Verifies setup completion

**Usage**:
```bash
export MONGO_URL="your-connection-string"
./setup_production_db.sh
```

---

## CI/CD and Automation

### 13. `.github/workflows/deploy.yml`
**Purpose**: GitHub Actions automated deployment workflow  
**Location**: `.github/workflows/`  
**Triggers**: Push to main branch or manual trigger  

**Workflow Steps**:
1. Run backend tests
2. Run frontend tests and build
3. Deploy to Vercel
4. Deploy to Render
5. Post-deployment health checks

**Required Secrets**:
- `VERCEL_TOKEN`
- `VERCEL_ORG_ID`
- `VERCEL_PROJECT_ID`
- `RENDER_DEPLOY_HOOK_URL`
- `BACKEND_URL`
- `FRONTEND_URL`
- `REACT_APP_BACKEND_URL`

---

## Documentation

### 14. `DEPLOYMENT_GUIDE.md`
**Purpose**: Complete step-by-step deployment documentation  
**Length**: Comprehensive 350+ line guide  
**Sections**:
- Prerequisites checklist
- MongoDB Atlas setup (detailed)
- Render backend deployment (detailed)
- Vercel frontend deployment (detailed)
- Database initialization steps
- Post-deployment verification
- Environment variables reference
- Troubleshooting guide
- Security checklist
- Production optimization tips

### 15. `DEPLOYMENT_README.md`
**Purpose**: Quick start deployment package overview  
**Sections**:
- Package contents
- Quick start guide
- Deployment checklist
- Environment variables summary
- Local development setup
- Architecture overview
- Security requirements
- Monitoring setup
- Support resources

---

## Verification and Testing

### 16. `verify_deployment.py`
**Purpose**: Post-deployment verification script  
**Language**: Python  
**Tests**:
- ✅ Backend health endpoint
- ✅ Frontend accessibility
- ✅ Login functionality
- ✅ Reference data seeding
- ✅ CORS configuration

**Usage**:
```bash
python verify_deployment.py <backend_url> <frontend_url>
```

**Output**:
- Colored test results
- Pass/fail summary
- Actionable next steps

---

## Code Changes for Production

### 17. Updated `backend/server.py`
**Changes Made**:

1. **Environment-based CORS** (Line 1109-1127):
   ```python
   frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
   allowed_origins = [frontend_url, "http://localhost:3000"]
   ```

2. **Health Check Endpoint** (Line 1111-1123):
   ```python
   @app.get("/api/health")
   async def health_check():
       # Tests database connection
       # Returns status and timestamp
   ```

3. **Production Environment Detection**:
   - Supports Vercel preview URLs
   - Wildcard CORS for staging environments

---

## Deployment Architecture

```
┌─────────────────┐
│   GitHub Repo   │
└────────┬────────┘
         │
         ├──────────────────┬──────────────────┐
         │                  │                  │
         ▼                  ▼                  ▼
┌─────────────────┐  ┌──────────────┐  ┌──────────────┐
│ GitHub Actions  │  │   Vercel     │  │   Render     │
│   (CI/CD)       │  │  (Frontend)  │  │  (Backend)   │
└─────────────────┘  └──────┬───────┘  └──────┬───────┘
                            │                  │
                            │                  │
                            ▼                  ▼
                     ┌──────────────────────────────┐
                     │     MongoDB Atlas            │
                     │  (Database + Backups)        │
                     └──────────────────────────────┘
```

---

## File Locations Reference

```
investigation-portal/
│
├── vercel.json                       # Vercel config
├── render.yaml                       # Render config
├── .env.example                      # Master env template
├── DEPLOYMENT_GUIDE.md              # Complete guide
├── DEPLOYMENT_README.md             # Quick start
├── verify_deployment.py             # Verification script
│
├── .github/
│   └── workflows/
│       └── deploy.yml               # CI/CD workflow
│
├── frontend/
│   ├── .env.example                 # Frontend dev env
│   ├── .env.production.example      # Frontend prod env
│   ├── package.json                 # Dependencies
│   └── src/                         # Source code
│
└── backend/
    ├── .env.example                 # Backend dev env
    ├── .env.production.example      # Backend prod env
    ├── requirements.txt             # Python dependencies
    ├── server.py                    # Main application (updated)
    ├── init_database.py             # DB initialization
    ├── seed_reference_data.py       # Reference data seeding
    ├── seed_production_users.py     # User seeding
    ├── seed_80_cases.py             # Demo data seeding
    └── setup_production_db.sh       # Automated setup
```

---

## Deployment Workflow

### Initial Setup (One-time)

1. **MongoDB Atlas**
   ```
   Create cluster → Configure access → Get connection string
   ```

2. **Render Backend**
   ```
   Create service → Set env vars → Deploy → Get URL
   ```

3. **Vercel Frontend**
   ```
   Import project → Set env vars → Deploy → Get URL
   ```

4. **Database Initialization**
   ```bash
   # Option 1: Render Shell
   python init_database.py
   python seed_reference_data.py
   python seed_production_users.py
   
   # Option 2: Automated
   ./setup_production_db.sh
   ```

5. **Verification**
   ```bash
   python verify_deployment.py <backend_url> <frontend_url>
   ```

### Subsequent Deployments

**Automatic** (with GitHub Actions):
```
git push origin main
→ Tests run → Deploys to Vercel & Render → Health checks
```

**Manual**:
```
# Frontend: Push triggers Vercel auto-deploy
# Backend: Push triggers Render auto-deploy
```

---

## Environment Variables Checklist

### Frontend (Vercel)
- [ ] `REACT_APP_BACKEND_URL`

### Backend (Render)
- [ ] `MONGO_URL`
- [ ] `DB_NAME`
- [ ] `JWT_SECRET`
- [ ] `EMERGENT_LLM_KEY`
- [ ] `FRONTEND_URL`
- [ ] `ENVIRONMENT`
- [ ] `PYTHON_VERSION`

### GitHub Secrets (for CI/CD)
- [ ] `VERCEL_TOKEN`
- [ ] `VERCEL_ORG_ID`
- [ ] `VERCEL_PROJECT_ID`
- [ ] `RENDER_DEPLOY_HOOK_URL`
- [ ] `BACKEND_URL`
- [ ] `FRONTEND_URL`
- [ ] `REACT_APP_BACKEND_URL`

---

## Post-Deployment Checklist

- [ ] All deployment files reviewed
- [ ] MongoDB Atlas configured
- [ ] Backend deployed to Render
- [ ] Frontend deployed to Vercel
- [ ] Database initialized
- [ ] Reference data seeded
- [ ] Test users created
- [ ] Health checks passing
- [ ] Login tested
- [ ] CORS working
- [ ] Default passwords changed
- [ ] Monitoring configured
- [ ] Backup strategy in place

---

## Support Resources

### Documentation
- **Start Here**: `DEPLOYMENT_GUIDE.md`
- **Quick Reference**: `DEPLOYMENT_README.md`
- **This File**: Complete file listing and architecture

### Scripts
- **Verification**: `verify_deployment.py`
- **Automated Setup**: `backend/setup_production_db.sh`

### Services
- **MongoDB Atlas**: https://cloud.mongodb.com/
- **Render**: https://dashboard.render.com/
- **Vercel**: https://vercel.com/dashboard
- **Emergent**: https://www.emergentagent.com/profile

---

## Maintenance Commands

```bash
# Test deployment
python verify_deployment.py $BACKEND_URL $FRONTEND_URL

# Initialize database
cd backend && python init_database.py

# Seed reference data
cd backend && python seed_reference_data.py

# Create users
cd backend && python seed_production_users.py

# Generate demo data
cd backend && python seed_80_cases.py

# Complete setup (automated)
cd backend && ./setup_production_db.sh

# Trigger Render deployment
curl -X POST $RENDER_DEPLOY_HOOK_URL

# Generate JWT secret
openssl rand -hex 32
```

---

## Version Information

- **Package Version**: 1.0.0
- **Created**: 2024
- **Last Updated**: 2024
- **Deployment Targets**: 
  - Frontend: Vercel (Free tier compatible)
  - Backend: Render (Free tier compatible)
  - Database: MongoDB Atlas (M0 free tier compatible)

---

## Quick Links

- 📖 [Complete Deployment Guide](./DEPLOYMENT_GUIDE.md)
- 🚀 [Quick Start Guide](./DEPLOYMENT_README.md)
- ✅ [Verification Script](./verify_deployment.py)
- 🔄 [CI/CD Workflow](./.github/workflows/deploy.yml)

---

**Status**: ✅ Ready for Production Deployment

All files are production-ready and tested. Follow the DEPLOYMENT_GUIDE.md for complete setup instructions.
