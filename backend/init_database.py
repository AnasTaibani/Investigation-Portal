"""
Database Initialization Script for Production
Creates all necessary collections, indexes, and initial data
"""
import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import bcrypt
from datetime import datetime, timezone

# Load environment variables
load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'investigation_portal')

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


async def init_database():
    """Initialize database with collections, indexes, and default data"""
    print("="*70)
    print("INVESTIGATION PORTAL - DATABASE INITIALIZATION")
    print("="*70)
    
    if not MONGO_URL:
        print("❌ ERROR: MONGO_URL environment variable not set!")
        print("Please set MONGO_URL in your .env file or environment variables.")
        sys.exit(1)
    
    print(f"\n📊 Connecting to MongoDB...")
    print(f"   Database: {DB_NAME}")
    
    try:
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        
        # Test connection
        await db.command("ping")
        print("✓ Connected to MongoDB successfully")
        
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        sys.exit(1)
    
    # ======================
    # CREATE INDEXES
    # ======================
    print(f"\n📑 Creating database indexes...")
    
    try:
        # Users collection indexes
        await db.users.create_index("email", unique=True)
        print("✓ Created users.email index")
        
        # Investigations collection indexes
        await db.investigations.create_index("investigation_id", unique=True)
        await db.investigations.create_index("assigned_investigator_id")
        await db.investigations.create_index("status")
        await db.investigations.create_index([("created_at", -1)])
        print("✓ Created investigations indexes")
        
        # Evidence collection indexes
        await db.evidence.create_index("investigation_id")
        await db.evidence.create_index("id", unique=True)
        print("✓ Created evidence indexes")
        
        # Activities collection indexes
        await db.activities.create_index("investigation_id")
        await db.activities.create_index([("timestamp", -1)])
        print("✓ Created activities indexes")
        
        # Notifications collection indexes
        await db.notifications.create_index("user_id")
        await db.notifications.create_index([("created_at", -1)])
        print("✓ Created notifications indexes")
        
        # Categories indexes
        await db.categories.create_index("name", unique=True)
        await db.subcategories.create_index([("category_id", 1), ("name", 1)])
        await db.service_categories.create_index("name", unique=True)
        print("✓ Created category indexes")
        
    except Exception as e:
        print(f"⚠ Warning: Index creation partially failed: {e}")
    
    # ======================
    # CREATE DEFAULT ADMIN
    # ======================
    print(f"\n👤 Creating default admin user...")
    
    admin_exists = await db.users.find_one({"email": "admin@investigationportal.com"})
    
    if not admin_exists:
        admin_user = {
            "email": "admin@investigationportal.com",
            "password_hash": hash_password("Admin@123"),
            "name": "System Administrator",
            "role": "admin",
            "agency_id": "system",
            "phone": "+1-555-0100",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        result = await db.users.insert_one(admin_user)
        print(f"✓ Created admin user: admin@investigationportal.com")
        print(f"  Default password: Admin@123")
        print(f"  ⚠️  IMPORTANT: Change this password after first login!")
    else:
        print("✓ Admin user already exists")
    
    # ======================
    # VERIFY COLLECTIONS
    # ======================
    print(f"\n📦 Verifying collections...")
    
    collections = await db.list_collection_names()
    required_collections = [
        'users', 'investigations', 'evidence', 'activities', 
        'notifications', 'categories', 'subcategories', 'service_categories'
    ]
    
    for coll in required_collections:
        if coll in collections:
            count = await db[coll].count_documents({})
            print(f"✓ {coll}: {count} documents")
        else:
            print(f"⚠ {coll}: collection will be created on first insert")
    
    # ======================
    # SUMMARY
    # ======================
    print(f"\n{'='*70}")
    print("DATABASE INITIALIZATION COMPLETE")
    print(f"{'='*70}")
    print(f"\n✅ Database initialized successfully!")
    print(f"\n📝 Next Steps:")
    print(f"   1. Run seed_reference_data.py to populate categories and services")
    print(f"   2. Run seed_production_users.py to create test users")
    print(f"   3. Optionally run seed_demo_investigations.py for sample data")
    print(f"\n🔐 Default Credentials:")
    print(f"   Email: admin@investigationportal.com")
    print(f"   Password: Admin@123")
    print(f"   ⚠️  Change password immediately after first login!\n")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(init_database())
