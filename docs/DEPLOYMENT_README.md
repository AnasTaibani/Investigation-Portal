# Investigation Portal - Deployment Package

## 📦 What's Included

This deployment package contains everything needed to deploy the Investigation Portal to production.

### Configuration Files

- `vercel.json` - Vercel deployment configuration for frontend
- `render.yaml` - Render deployment configuration for backend
- `.env.example` - Complete environment variables template
- `.github/workflows/deploy.yml` - GitHub Actions CI/CD workflow

### Database Scripts

- `backend/init_database.py` - Initialize database, create indexes, default admin
- `backend/seed_reference_data.py` - Seed categories, subcategories, services
- `backend/seed_production_users.py` - Create test users for all roles
- `backend/seed_80_cases.py` - (Optional) Generate 80 demo investigation cases
- `backend/setup_production_db.sh` - Automated setup script

### Documentation

- `DEPLOYMENT_GUIDE.md` - **Complete step-by-step deployment guide** (START HERE!)
- `frontend/.env.production.example` - Frontend production env template
- `backend/.env.production.example` - Backend production env template

---

## 🚀 Quick Start

### 1. Read the Deployment Guide

**👉 Start with [`DEPLOYMENT_GUIDE.md`](./DEPLOYMENT_GUIDE.md)**

It contains:
- Complete setup instructions for MongoDB Atlas, Render, and Vercel
- Step-by-step configuration guide
- Environment variables reference
- Troubleshooting guide
- Post-deployment verification checklist

### 2. Prerequisites

- MongoDB Atlas account (free tier available)
- Render account (free tier available)
- Vercel account (free tier available)
- Emergent LLM Key (get from https://www.emergentagent.com/profile)
- GitHub repository with your code

### 3. Deployment Order

1. **MongoDB Atlas** - Set up database cluster (10 min)
2. **Render** - Deploy backend API (15 min)
3. **Vercel** - Deploy frontend app (10 min)
4. **Initialize Database** - Run setup scripts (5 min)
5. **Verify** - Test complete workflow (10 min)

**Total Time:** ~50 minutes for first deployment

---

## 📋 Deployment Checklist

### MongoDB Atlas Setup
- [ ] Create cluster
- [ ] Configure database user
- [ ] Configure network access
- [ ] Get connection string

### Backend (Render)
- [ ] Create web service
- [ ] Set environment variables (MONGO_URL, JWT_SECRET, etc.)
- [ ] Deploy and verify health check

### Frontend (Vercel)
- [ ] Import project
- [ ] Set REACT_APP_BACKEND_URL
- [ ] Deploy and verify site loads

### Database Initialization
- [ ] Run `init_database.py`
- [ ] Run `seed_reference_data.py`
- [ ] Run `seed_production_users.py`
- [ ] Verify collections in MongoDB Atlas

### Testing
- [ ] Test login
- [ ] Test dashboard
- [ ] Test workbench
- [ ] Test investigation detail
- [ ] Test evidence upload
- [ ] Test findings submission

---

## 🔧 Environment Variables

### Frontend (Vercel)

```bash
REACT_APP_BACKEND_URL=https://your-backend.onrender.com
```

### Backend (Render)

```bash
MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/
DB_NAME=investigation_portal
JWT_SECRET=your-32-character-secret
EMERGENT_LLM_KEY=your-emergent-key
FRONTEND_URL=https://your-app.vercel.app
ENVIRONMENT=production
```

---

## 🧪 Local Development

### Frontend

```bash
cd frontend
cp .env.example .env
# Edit .env with your backend URL
yarn install
yarn start
```

### Backend

```bash
cd backend
cp .env.example .env
# Edit .env with your MongoDB URL
pip install -r requirements.txt
uvicorn server:app --reload
```

---

## 📚 Documentation

### Architecture

**Frontend (React + Tailwind + Shadcn UI)**
- Location: `/frontend`
- Build: Create React App with craco
- Deployment: Vercel

**Backend (FastAPI + MongoDB)**
- Location: `/backend`
- Framework: FastAPI with Motor (async MongoDB driver)
- Deployment: Render

**Database (MongoDB Atlas)**
- Cloud-hosted MongoDB cluster
- Free tier (M0) available
- Automatic backups and monitoring

### Key Features

- JWT Authentication with HTTP-only cookies
- Role-based access control (Admin, Assessor, Investigator)
- Evidence management with multi-service linking
- Investigation workflow automation
- Real-time status tracking
- Timeline and activity logging
- Findings submission and approval workflow

---

## 🔒 Security

### Required After Deployment

1. **Change Default Passwords**
   - Admin: `admin@investigationportal.com`
   - Assessor: `jane.assessor@investigationportal.com`
   - Investigator: `investigator@test.com`

2. **Secure Environment Variables**
   - Use strong JWT_SECRET (32+ characters)
   - Restrict MongoDB network access
   - Enable HTTPS everywhere

3. **MongoDB Security**
   - Limit IP whitelist to Render IPs only
   - Enable MongoDB authentication
   - Regular backups

---

## 📊 Monitoring

### Render (Backend)
- View logs: Dashboard → Service → Logs
- Health check: `https://your-backend.onrender.com/api/health`
- Metrics: Dashboard → Service → Metrics

### Vercel (Frontend)
- Analytics: Dashboard → Project → Analytics
- Deployments: Dashboard → Project → Deployments
- Logs: Dashboard → Project → Deployments → View Function Logs

### MongoDB Atlas
- Metrics: Cluster → Metrics tab
- Performance: Database → Performance Advisor
- Alerts: Project → Alerts

---

## 🐛 Troubleshooting

### Common Issues

1. **CORS Errors**
   - Verify FRONTEND_URL in Render matches Vercel URL exactly
   - No trailing slashes in URLs

2. **Database Connection Failed**
   - Check MONGO_URL format
   - Verify network access in MongoDB Atlas (0.0.0.0/0)
   - Test connection string locally

3. **Login Not Working**
   - Verify JWT_SECRET is set in Render
   - Check backend logs for errors
   - Ensure users were seeded (run `seed_production_users.py`)

4. **Evidence Upload Issues**
   - EMERGENT_LLM_KEY must be set
   - Check backend logs for storage initialization errors

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md#troubleshooting) for detailed troubleshooting.

---

## 📞 Support

### Resources

- **Deployment Guide**: [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
- **MongoDB Atlas Docs**: https://www.mongodb.com/docs/atlas/
- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs

### Quick Commands

```bash
# Generate JWT Secret
openssl rand -hex 32

# Test Backend Health
curl https://your-backend.onrender.com/api/health

# Test Login API
curl -X POST https://your-backend.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"investigator@test.com","password":"Investigator@123"}'

# Initialize Database (Render Shell)
cd backend && python init_database.py

# View Backend Logs (Render Dashboard)
Dashboard → Service → Logs → Live Logs
```

---

## 📝 Version History

- **v1.0.0** - Initial production deployment package
  - Complete deployment configuration for Vercel + Render + MongoDB Atlas
  - Database initialization and seeding scripts
  - Comprehensive deployment guide
  - CI/CD workflow with GitHub Actions

---

## ⚖️ License

MetaMorphoSys Investigation Portal © 2024

---

## 🎉 Ready to Deploy?

Start with the **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** for complete instructions.

**Questions?** Check the troubleshooting section in the deployment guide.

**Need help?** Review the logs in Render/Vercel dashboards and verify all environment variables are set correctly.

---

**Happy Deploying! 🚀**
