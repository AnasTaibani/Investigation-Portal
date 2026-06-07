# Investigation Portal

## Enterprise Investigation Management Platform

A comprehensive, production-grade investigation management system designed for insurance claims investigations. Built with modern technologies for scalability, security, and user experience.

![Dashboard Screenshot](https://via.placeholder.com/1200x600/1D4ED8/FFFFFF?text=Investigation+Portal+Dashboard)

---

## 🚀 Features

### Core Functionality
- ✅ **Investigation Case Management** - Complete lifecycle from assignment to closure
- ✅ **Evidence Management** - Upload files with geo-tagging support
- ✅ **Service Tracking** - Track multiple services per investigation
- ✅ **Findings & Recommendations** - Structured investigation outcomes
- ✅ **Rework Management** - Request and track additional investigation work
- ✅ **Activity Timeline** - Complete audit trail of all actions
- ✅ **Notifications** - In-app notifications for key events

### User Roles
- **Investigator** - Execute investigations, upload evidence, submit findings
- **Assessor** - Review findings, request rework, approve cases
- **Admin** - Full system access, user management, configuration

### Categories & Services
- 10 pre-configured investigation categories
- 34 subcategories for specific investigation types
- 12 service categories with geo-tagging requirements

### UI/UX Excellence
- 🎨 **Light & Dark Themes** with seamless switching
- 🏢 **MetaMorphoSys Branding** with dynamic logo switching
- 📊 **Dashboard Analytics** with charts and KPIs
- 📱 **Fully Responsive** design for mobile, tablet, desktop
- ⚡ **Fast & Smooth** animations and transitions
- 🎯 **Intuitive Navigation** with breadcrumbs and search

---

## 🛠️ Technology Stack

### Backend
- **FastAPI** - High-performance Python API framework
- **MongoDB** - Flexible NoSQL database
- **Motor** - Async MongoDB driver
- **JWT** - Secure authentication
- **Bcrypt** - Password hashing
- **Emergent Object Storage** - File storage service

### Frontend
- **React 18** - Modern UI library
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Recharts** - Data visualization
- **Tailwind CSS** - Utility-first styling
- **Shadcn UI** - High-quality component library
- **Lucide React** - Icon library

---

## 📦 Quick Start

### Prerequisites
```bash
- Python 3.9+
- Node.js 16+ & Yarn
- MongoDB 4.4+
```

### Installation

1. **Clone repository**
```bash
git clone <repo-url>
cd investigation-portal
```

2. **Backend setup**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure .env
cp .env.example .env
# Edit .env with your settings

# Seed data
python3 seed_data.py
python3 seed_demo_data.py

# Run backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

3. **Frontend setup**
```bash
cd frontend
yarn install

# Configure .env
cp .env.example .env
# Set REACT_APP_BACKEND_URL=http://localhost:8001

# Run frontend
yarn start
```

4. **Access application**
- Frontend: http://localhost:3000
- Backend: http://localhost:8001
- API Docs: http://localhost:8001/docs

---

## 🔐 Default Credentials

**Admin Account:**
```
Email: admin@investigationportal.com
Password: Admin@123
```

**Test Investigator:**
```
Email: investigator@test.com
Password: Investigator@123
```

**Test Assessor:**
```
Email: assessor@test.com
Password: Assessor@123
```

⚠️ **Change these in production!**

---

## 📊 Demo Data

The portal comes with **250 realistic investigation cases** across:
- 10 investigation categories
- 20 investigators
- Various statuses (Assigned, In Progress, Submitted, Completed, etc.)
- Date range: Last 90 days
- Realistic findings and evidence patterns

To seed demo data:
```bash
cd backend
python3 seed_demo_data.py
```

---

## 🎨 Branding & Themes

### Light Theme
Professional enterprise appearance with:
- Clean white backgrounds
- Soft gray surfaces
- Blue primary actions
- High readability

### Dark Theme
Modern executive dashboard with:
- Dark charcoal backgrounds
- Muted contrast
- Professional blue accents
- Reduced eye strain

### Dynamic Branding
- MetaMorphoSys Technologies logo
- Automatic logo switching with theme
- Configurable in `/frontend/src/config/branding.js`

---

## 📈 Dashboard Analytics

### KPI Cards
- Total Cases
- Assigned Cases
- In Progress
- Submitted
- Completed
- Closed
- Trend indicators

### Visualizations
- **Pie Chart** - Cases by Status
- **Bar Chart** - Status Overview
- **Activity Feed** - Recent investigations

---

## 🗂️ Project Structure

```
investigation-portal/
├── backend/
│   ├── server.py              # Main FastAPI application
│   ├── seed_data.py           # Initial data seeding
│   ├── seed_demo_data.py      # Demo data generation
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment variables
├── frontend/
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   ├── pages/             # Page components
│   │   ├── contexts/          # React contexts (Auth, Theme)
│   │   ├── config/            # Configuration (branding)
│   │   ├── lib/               # API client
│   │   └── App.js             # Main app component
│   ├── package.json           # Node dependencies
│   └── .env                   # Environment variables
├── DEPLOYMENT.md              # Deployment guide
└── README.md                  # This file
```

---

## 🔒 Security Features

- ✅ JWT authentication with httpOnly cookies
- ✅ Bcrypt password hashing
- ✅ Role-based access control
- ✅ CORS configuration
- ✅ Secure file upload
- ✅ Session management
- ✅ Complete audit logging

---

## 🚀 Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions including:
- Docker deployment
- Manual deployment
- Nginx configuration
- SSL setup
- Environment configuration
- Backup strategies

---

## 📝 API Documentation

Interactive API documentation available at:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

### Key Endpoints

#### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - Register user (admin only)
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - Logout

#### Investigations
- `GET /api/investigations` - List investigations
- `GET /api/investigations/{id}` - Get details
- `POST /api/investigations` - Create investigation
- `PUT /api/investigations/{id}/status` - Update status
- `POST /api/investigations/{id}/evidence` - Upload evidence
- `POST /api/investigations/{id}/findings` - Submit findings
- `POST /api/investigations/{id}/rework` - Request rework

#### Users (Admin only)
- `GET /api/users` - List users
- `GET /api/users/{id}` - Get user
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user

---

## 📄 License

Proprietary - MetaMorphoSys Technologies

---

## 📞 Support

For support, email support@metamorphosys.com or contact your system administrator.

---

**Built with ❤️ by MetaMorphoSys Technologies**
