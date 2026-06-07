# Investigation Portal - Deployment Documentation

## Overview

Enterprise-grade Investigation Management Portal for insurance claims investigations. Built with FastAPI, React, MongoDB, and Emergent Object Storage.

---

## Prerequisites

- Python 3.9+
- Node.js 16+ and Yarn
- MongoDB 4.4+
- Git

---

## Local Development Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd investigation-portal
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and set:
# - MONGO_URL="mongodb://localhost:27017"
# - DB_NAME="investigation_portal"
# - JWT_SECRET="<generate-random-64-char-hex>"
# - ADMIN_EMAIL="admin@yourdomain.com"
# - ADMIN_PASSWORD="<secure-password>"
# - EMERGENT_LLM_KEY="<your-emergent-key>"
# - CORS_ORIGINS="http://localhost:3000"

# Seed initial data
python3 seed_data.py
python3 seed_demo_data.py

# Run backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
yarn install

# Configure environment
cp .env.example .env
# Edit .env and set:
# - REACT_APP_BACKEND_URL=http://localhost:8001

# Run frontend
yarn start
```

### 4. Access Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8001
- API Docs: http://localhost:8001/docs

---

## Production Deployment

### Option 1: Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Option 2: Manual Deployment

#### Backend Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Set production environment variables
export MONGO_URL="mongodb://<production-host>:27017"
export DB_NAME="investigation_portal"
export JWT_SECRET="<production-secret>"
export ADMIN_EMAIL="admin@yourdomain.com"
export ADMIN_PASSWORD="<secure-password>"
export EMERGENT_LLM_KEY="<your-key>"
export CORS_ORIGINS="https://yourdomain.com"

# Run with gunicorn
gunicorn server:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8001
```

#### Frontend Deployment

```bash
# Build for production
yarn build

# Serve with nginx
# Copy build/ folder to /var/www/investigation-portal
# Configure nginx reverse proxy
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Frontend
    location / {
        root /var/www/investigation-portal/build;
        try_files $uri /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Environment Variables

### Backend (.env)

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| MONGO_URL | MongoDB connection string | Yes | - |
| DB_NAME | Database name | Yes | investigation_portal |
| JWT_SECRET | Secret key for JWT tokens | Yes | - |
| ADMIN_EMAIL | Admin user email | Yes | - |
| ADMIN_PASSWORD | Admin user password | Yes | - |
| EMERGENT_LLM_KEY | Emergent API key for object storage | Yes | - |
| CORS_ORIGINS | Allowed CORS origins (comma-separated) | Yes | - |

### Frontend (.env)

| Variable | Description | Required |
|----------|-------------|----------|
| REACT_APP_BACKEND_URL | Backend API URL | Yes |

---

## Database Setup

### MongoDB Indexes

Automatically created on startup:
- `users.email` (unique)
- `investigations.investigation_id` (unique)
- `investigations.assigned_investigator_id`
- `investigations.status`
- `activities.investigation_id`
- `notifications.user_id`

### Initial Data Seeding

```bash
# Seed categories, subcategories, service categories, and test users
python3 backend/seed_data.py

# Seed 250 demo investigation cases (optional)
python3 backend/seed_demo_data.py
```

---

## Default Credentials

After running `seed_data.py`:

**Admin:**
- Email: admin@investigationportal.com
- Password: Admin@123

**Investigator:**
- Email: investigator@test.com
- Password: Investigator@123

**Assessor:**
- Email: assessor@test.com
- Password: Assessor@123

⚠️ **IMPORTANT:** Change these credentials in production!

---

## Features

### Authentication
- JWT-based authentication with httpOnly cookies
- Role-based access control (Admin, Investigator, Assessor)
- Secure password hashing with bcrypt
- Session management with access and refresh tokens

### User Management
- Admin can create users with roles
- User CRUD operations
- No self-registration (admin-only user creation)

### Investigation Management
- Create and assign investigation cases
- Track case lifecycle (Assigned → In Progress → Submitted → Completed → Closed)
- Service execution tracking
- Evidence upload with geo-tagging
- Findings and recommendations
- Rework request management

### Evidence Management
- File upload with object storage (Emergent)
- Supports: PDF, DOCX, XLSX, JPG, PNG, JPEG, MP4, MOV, audio, ZIP
- Maximum file size: 100MB per file
- Geo-tagging for location-based services

### Dashboard & Analytics
- Role-specific dashboards
- KPI cards with trend indicators
- Pie and bar charts for case distribution
- Recent investigations table

### Theme Support
- Light and dark themes
- Theme persistence across sessions
- Dynamic branding with logo switching

---

## API Documentation

### Authentication Endpoints

**POST /api/auth/register**
- Register new user (admin only)
- Body: `{ email, password, name, role, phone }`

**POST /api/auth/login**
- User login
- Body: `{ email, password }`
- Returns: User object, sets httpOnly cookies

**GET /api/auth/me**
- Get current user
- Requires: Authentication

**POST /api/auth/logout**
- Logout user
- Clears authentication cookies

### Investigation Endpoints

**GET /api/investigations**
- List investigations
- Query params: `status`, `investigator_id`, `category_id`, `search`

**GET /api/investigations/{investigation_id}**
- Get investigation details

**POST /api/investigations**
- Create new investigation
- Requires: Admin or Assessor role

**PUT /api/investigations/{investigation_id}/status**
- Update investigation status
- Body: `{ status }`

**POST /api/investigations/{investigation_id}/evidence**
- Upload evidence
- Multipart form with file, service_id, latitude, longitude, notes

**POST /api/investigations/{investigation_id}/findings**
- Submit investigation findings
- Body: `{ summary, observations, findings, conclusion, outcome, recommendation }`

**POST /api/investigations/{investigation_id}/rework**
- Request rework
- Body: `{ reason, additional_instructions, expected_deliverables }`

### User Management Endpoints

**GET /api/users**
- List users
- Query params: `role`
- Requires: Admin role

**GET /api/users/{user_id}**
- Get user details
- Requires: Admin role

**PUT /api/users/{user_id}**
- Update user
- Requires: Admin role

**DELETE /api/users/{user_id}**
- Delete user
- Requires: Admin role

---

## Monitoring & Health Checks

### Backend Health Check
```bash
curl http://localhost:8001/api/
```

### Database Connection
```bash
mongosh mongodb://localhost:27017/investigation_portal
```

### Logs
```bash
# Backend logs
tail -f /var/log/investigation-portal/backend.log

# Frontend logs (nginx)
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

---

## Backup & Recovery

### Database Backup
```bash
mongodump --uri="mongodb://localhost:27017/investigation_portal" --out=/backup/$(date +%Y%m%d)
```

### Database Restore
```bash
mongorestore --uri="mongodb://localhost:27017/investigation_portal" /backup/20260603/
```

---

## Troubleshooting

### Backend won't start
- Check MongoDB connection
- Verify environment variables
- Check port 8001 is available

### Frontend can't connect to backend
- Verify REACT_APP_BACKEND_URL in .env
- Check CORS configuration in backend
- Ensure backend is running

### Authentication issues
- Clear browser cookies
- Check JWT_SECRET is set
- Verify cookie settings (httpOnly, secure, samesite)

### File upload fails
- Check EMERGENT_LLM_KEY is valid
- Verify file size under 100MB
- Check object storage connectivity

---

## Security Considerations

1. **Change default credentials** in production
2. **Use strong JWT_SECRET** (64+ characters)
3. **Enable HTTPS** in production
4. **Set secure cookie flags** (secure=True for HTTPS)
5. **Configure firewall** to restrict MongoDB access
6. **Regular backups** of database
7. **Monitor logs** for suspicious activity
8. **Keep dependencies updated**

---

## Performance Optimization

1. **Database indexes** - automatically created
2. **Pagination** - limit API responses
3. **CDN** for static assets
4. **Caching** - implement Redis for sessions
5. **Load balancing** - use multiple backend instances
6. **MongoDB replica set** for high availability

---

## Support

For issues or questions:
- Email: support@metamorphosys.com
- Documentation: [Internal Wiki]
- Issue Tracker: [GitHub Issues]

---

## License

Proprietary - MetaMorphoSys Technologies
