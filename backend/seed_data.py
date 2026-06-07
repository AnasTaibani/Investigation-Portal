import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def seed_categories():
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    # Categories with their subcategories
    categories_data = [
        {
            "name": "Address Verification",
            "description": "Verify residential and business addresses",
            "subcategories": ["Home Visit", "Utility Bill Match"]
        },
        {
            "name": "Bank Verification",
            "description": "Verify banking information",
            "subcategories": ["Account Ownership", "Transaction Pattern"]
        },
        {
            "name": "Death Verification",
            "description": "Verify death claims",
            "subcategories": ["Village Death Report", "Hospital Death Certificate", "Police Report"]
        },
        {
            "name": "Digital Verification",
            "description": "Digital evidence collection",
            "subcategories": ["Geo-Tagged Photo", "QR Code-based Document Authentication", "Video Interview"]
        },
        {
            "name": "Document Validation",
            "description": "Validate authenticity of documents",
            "subcategories": ["Forged Document Detection", "Missing Signature / Stamp"]
        },
        {
            "name": "Employment Verification",
            "description": "Verify employment status",
            "subcategories": ["Migrant Worker - Work Pass / Agency", "Salaried - Employer Letter", "Self-Employed - Business Permit"]
        },
        {
            "name": "Hospital Verification",
            "description": "Verify hospital treatments and records",
            "subcategories": ["MOH/MOH-recognized Facility Check", "Treatment Record & Billing Match"]
        },
        {
            "name": "Identity Verification",
            "description": "Verify identity of claimant",
            "subcategories": ["Biometric Verification", "National ID Check", "Passport Check", "Signature Match"]
        },
        {
            "name": "Income Verification",
            "description": "Verify income sources",
            "subcategories": ["Bank Credits", "Pay Slips", "Tax Return"]
        },
        {
            "name": "Medical Verification",
            "description": "Verify medical history",
            "subcategories": ["Clinic / GP Visit History", "Hospital Record Verification"]
        }
    ]
    
    # Service categories
    service_categories = [
        {"name": "Hospital Visit", "description": "Physical visit to hospital", "requires_geo_tag": True},
        {"name": "Residence Visit", "description": "Physical visit to residence", "requires_geo_tag": True},
        {"name": "Workplace Visit", "description": "Physical visit to workplace", "requires_geo_tag": True},
        {"name": "Mobile Photo/Video Capture", "description": "Capture photo/video evidence", "requires_geo_tag": True},
        {"name": "Alive Check Visit / Video Call", "description": "Verify person is alive", "requires_geo_tag": False},
        {"name": "Document Pickup / Delivery", "description": "Collect or deliver documents", "requires_geo_tag": False},
        {"name": "Digital Interview (Zoom/WhatsApp)", "description": "Conduct digital interview", "requires_geo_tag": False},
        {"name": "Report Drafting - Interim", "description": "Draft interim investigation report", "requires_geo_tag": False},
        {"name": "Report Drafting - Final", "description": "Draft final investigation report", "requires_geo_tag": False},
        {"name": "Bank Statement Submission & Validation", "description": "Collect and validate bank statements", "requires_geo_tag": False},
        {"name": "Translation Service", "description": "Translate documents", "requires_geo_tag": False},
        {"name": "Affidavit Collection", "description": "Collect sworn statements", "requires_geo_tag": False}
    ]
    
    print("Seeding categories...")
    for cat_data in categories_data:
        # Check if category exists
        existing_cat = await db.categories.find_one({"name": cat_data["name"]})
        if not existing_cat:
            result = await db.categories.insert_one({
                "name": cat_data["name"],
                "description": cat_data["description"],
                "created_at": "2026-06-03T00:00:00"
            })
            category_id = str(result.inserted_id)
            print(f"Created category: {cat_data['name']}")
            
            # Add subcategories
            for sub_name in cat_data["subcategories"]:
                await db.subcategories.insert_one({
                    "category_id": category_id,
                    "name": sub_name,
                    "description": "",
                    "created_at": "2026-06-03T00:00:00"
                })
                print(f"  - Created subcategory: {sub_name}")
        else:
            print(f"Category already exists: {cat_data['name']}")
    
    print("\nSeeding service categories...")
    for svc in service_categories:
        existing_svc = await db.service_categories.find_one({"name": svc["name"]})
        if not existing_svc:
            await db.service_categories.insert_one({
                **svc,
                "created_at": "2026-06-03T00:00:00"
            })
            print(f"Created service category: {svc['name']}")
        else:
            print(f"Service category already exists: {svc['name']}")
    
    # Create a test investigator
    investigator_email = "investigator@test.com"
    existing_inv = await db.users.find_one({"email": investigator_email})
    if not existing_inv:
        from server import hash_password
        await db.users.insert_one({
            "email": investigator_email,
            "password_hash": hash_password("Investigator@123"),
            "name": "John Investigator",
            "role": "investigator",
            "phone": "+1234567890",
            "created_at": "2026-06-03T00:00:00"
        })
        print(f"\nCreated test investigator: {investigator_email} / Investigator@123")
        
        # Update test credentials
        with open("/app/memory/test_credentials.md", "a") as f:
            f.write("\n## Test Investigator\n")
            f.write(f"- Email: {investigator_email}\n")
            f.write("- Password: Investigator@123\n")
            f.write("- Role: investigator\n")
    else:
        print(f"\nTest investigator already exists: {investigator_email}")
    
    # Create a test assessor
    assessor_email = "assessor@test.com"
    existing_ass = await db.users.find_one({"email": assessor_email})
    if not existing_ass:
        from server import hash_password
        await db.users.insert_one({
            "email": assessor_email,
            "password_hash": hash_password("Assessor@123"),
            "name": "Jane Assessor",
            "role": "assessor",
            "phone": "+1234567891",
            "created_at": "2026-06-03T00:00:00"
        })
        print(f"Created test assessor: {assessor_email} / Assessor@123")
        
        # Update test credentials
        with open("/app/memory/test_credentials.md", "a") as f:
            f.write("\n## Test Assessor\n")
            f.write(f"- Email: {assessor_email}\n")
            f.write("- Password: Assessor@123\n")
            f.write("- Role: assessor\n")
    else:
        print(f"Test assessor already exists: {assessor_email}")
    
    print("\nSeed completed successfully!")
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_categories())
