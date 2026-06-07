#!/bin/bash
# Quick Start Deployment Script
# Run this after deploying to Render and Vercel

set -e

echo "=========================================="
echo "Investigation Portal - Database Setup"
echo "=========================================="

# Check if MONGO_URL is set
if [ -z "$MONGO_URL" ]; then
    echo "❌ Error: MONGO_URL environment variable not set"
    echo "Please set it with:"
    echo "export MONGO_URL='your-mongodb-connection-string'"
    exit 1
fi

# Check if DB_NAME is set
if [ -z "$DB_NAME" ]; then
    echo "⚠️  Warning: DB_NAME not set, using default 'investigation_portal'"
    export DB_NAME="investigation_portal"
fi

echo ""
echo "📊 Database: $DB_NAME"
echo ""

# Navigate to backend directory
cd backend

echo "Step 1: Installing dependencies..."
pip install -q pymongo motor python-dotenv bcrypt

echo "Step 2: Initializing database..."
python init_database.py

echo ""
echo "Step 3: Seeding reference data..."
python seed_reference_data.py

echo ""
echo "Step 4: Creating test users..."
python seed_production_users.py

echo ""
echo "=========================================="
echo "✅ Database setup complete!"
echo "=========================================="
echo ""
echo "🔐 Default Credentials:"
echo ""
echo "  Investigator:"
echo "    Email: investigator@test.com"
echo "    Password: Investigator@123"
echo ""
echo "  Admin:"
echo "    Email: admin@investigationportal.com"
echo "    Password: Admin@123"
echo ""
echo "⚠️  IMPORTANT: Change these passwords immediately!"
echo ""
echo "Optional: Run demo data seeding"
echo "  python seed_80_cases.py"
echo ""
