"""
Seed Production Users
Creates test users for different roles (admin, assessor, investigator)
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import bcrypt
from datetime import datetime, timezone

load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'investigation_portal')


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


TEST_USERS = [
    {
        "email": "admin@investigationportal.com",
        "password": "Admin@123",
        "name": "System Administrator",
        "role": "admin",
        "agency_id": "system",
        "phone": "+1-555-0100"
    },
    {
        "email": "jane.assessor@investigationportal.com",
        "password": "Assessor@123",
        "name": "Jane Assessor",
        "role": "assessor",
        "agency_id": "agency-apex",
        "phone": "+1-555-0101"
    },
    {
        "email": "investigator@test.com",
        "password": "Investigator@123",
        "name": "John Anderson",
        "role": "investigator",
        "agency_id": "agency-apex",
        "phone": "+60 12-345-6789"
    },
    {
        "email": "sarah.investigator@investigationportal.com",
        "password": "Investigator@123",
        "name": "Sarah Investigator",
        "role": "investigator",
        "agency_id": "agency-apex",
        "phone": "+1-555-0103"
    }
]


async def seed_users():
    print("="*70)
    print("SEEDING PRODUCTION USERS")
    print("="*70)
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Check connection
    await db.command("ping")
    print("✓ Connected to MongoDB")
    
    print(f"\n👥 Creating test users...")
    
    created_count = 0
    existing_count = 0
    
    for user_data in TEST_USERS:
        email = user_data["email"]
        
        # Check if user exists
        existing = await db.users.find_one({"email": email})
        
        if existing:
            print(f"⚠ User exists: {email}")
            existing_count += 1
        else:
            user_doc = {
                "email": email,
                "password_hash": hash_password(user_data["password"]),
                "name": user_data["name"],
                "role": user_data["role"],
                "agency_id": user_data["agency_id"],
                "phone": user_data["phone"],
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            await db.users.insert_one(user_doc)
            print(f"✓ Created: {email} ({user_data['role']})")
            created_count += 1
    
    # ======================
    # SUMMARY
    # ======================
    total_users = await db.users.count_documents({})
    
    print(f"\n{'='*70}")
    print("USER SEEDING COMPLETE")
    print(f"{'='*70}")
    print(f"\nSummary:")
    print(f"  Created: {created_count}")
    print(f"  Already existed: {existing_count}")
    print(f"  Total users in database: {total_users}")
    
    print(f"\n🔐 Test Credentials:")
    print(f"\n  Admin:")
    print(f"    Email: admin@investigationportal.com")
    print(f"    Password: Admin@123")
    print(f"\n  Assessor:")
    print(f"    Email: jane.assessor@investigationportal.com")
    print(f"    Password: Assessor@123")
    print(f"\n  Investigator:")
    print(f"    Email: investigator@test.com")
    print(f"    Password: Investigator@123")
    print(f"\n⚠️  IMPORTANT: Change these passwords in production!\n")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(seed_users())
