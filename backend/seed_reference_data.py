"""
Seed Reference Data - Categories, Subcategories, and Services
This should be run once after database initialization
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'investigation_portal')

# Reference Data
CATEGORIES = [
    {"name": "Death Verification", "description": "Verification of death claims and related documentation"},
    {"name": "Hospital Verification", "description": "Hospital visit and medical record verification"},
    {"name": "Medical Verification", "description": "Medical document and treatment verification"},
    {"name": "Address Verification", "description": "Physical address and residence verification"},
    {"name": "Identity Verification", "description": "Identity document verification"},
    {"name": "Income Verification", "description": "Income and employment verification"},
    {"name": "Bank Verification", "description": "Bank account and financial verification"},
]

SUBCATEGORIES_MAP = {
    "Death Verification": [
        "Natural Death", "Accidental Death", "Death Certificate Verification"
    ],
    "Hospital Verification": [
        "Hospital Bill Verification", "Treatment Record Verification", "Discharge Summary Verification"
    ],
    "Medical Verification": [
        "Medical Report Verification", "Prescription Verification", "Medical History Verification"
    ],
    "Address Verification": [
        "Residence Verification", "Business Address Verification", "Property Verification"
    ],
    "Identity Verification": [
        "Aadhaar Verification", "PAN Card Verification", "Passport Verification"
    ],
    "Income Verification": [
        "Salary Verification", "Business Income Verification", "Agricultural Income Verification"
    ],
    "Bank Verification": [
        "Bank Account Verification", "Transaction Verification", "Bank Statement Verification"
    ]
}

SERVICES = [
    {"name": "Hospital Visit", "description": "Physical visit to hospital for verification", "estimated_hours": 4},
    {"name": "Medical Report Collection", "description": "Collection and verification of medical reports", "estimated_hours": 2},
    {"name": "Medical Record Verification", "description": "Verification of medical records and documents", "estimated_hours": 3},
    {"name": "Document Verification", "description": "General document verification", "estimated_hours": 2},
    {"name": "Mobile Photo/Video Capture", "description": "Photo and video evidence capture using mobile", "estimated_hours": 1},
    {"name": "Physical Verification", "description": "Physical site or location verification", "estimated_hours": 3},
    {"name": "Bank Visit", "description": "Visit to bank for verification", "estimated_hours": 3},
    {"name": "Employer Verification", "description": "Employment and employer verification", "estimated_hours": 4},
    {"name": "Account Statement Collection", "description": "Collection of bank account statements", "estimated_hours": 2},
    {"name": "In-Person Meeting", "description": "Face-to-face meeting with subject", "estimated_hours": 2},
    {"name": "Report Drafting - Final", "description": "Final investigation report preparation", "estimated_hours": 4},
]


async def seed_reference_data():
    print("="*70)
    print("SEEDING REFERENCE DATA")
    print("="*70)
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Check connection
    await db.command("ping")
    print("✓ Connected to MongoDB")
    
    # ======================
    # SEED CATEGORIES
    # ======================
    print(f"\n📋 Seeding Categories...")
    
    existing_categories = await db.categories.count_documents({})
    if existing_categories > 0:
        print(f"⚠ {existing_categories} categories already exist. Skipping categories...")
    else:
        category_docs = []
        for cat in CATEGORIES:
            category_docs.append({
                "_id": ObjectId(),
                "name": cat["name"],
                "description": cat["description"],
                "is_active": True
            })
        
        await db.categories.insert_many(category_docs)
        print(f"✓ Inserted {len(category_docs)} categories")
    
    # ======================
    # SEED SUBCATEGORIES
    # ======================
    print(f"\n📂 Seeding Subcategories...")
    
    existing_subcats = await db.subcategories.count_documents({})
    if existing_subcats > 0:
        print(f"⚠ {existing_subcats} subcategories already exist. Skipping subcategories...")
    else:
        # Get categories with their IDs
        categories = await db.categories.find({}).to_list(100)
        category_map = {cat["name"]: cat["_id"] for cat in categories}
        
        subcat_docs = []
        for cat_name, subcats in SUBCATEGORIES_MAP.items():
            if cat_name in category_map:
                for subcat_name in subcats:
                    subcat_docs.append({
                        "_id": ObjectId(),
                        "name": subcat_name,
                        "category_id": category_map[cat_name],
                        "is_active": True
                    })
        
        await db.subcategories.insert_many(subcat_docs)
        print(f"✓ Inserted {len(subcat_docs)} subcategories")
    
    # ======================
    # SEED SERVICES
    # ======================
    print(f"\n🛠️ Seeding Service Categories...")
    
    existing_services = await db.service_categories.count_documents({})
    if existing_services > 0:
        print(f"⚠ {existing_services} services already exist. Skipping services...")
    else:
        service_docs = []
        for service in SERVICES:
            service_docs.append({
                "_id": ObjectId(),
                "name": service["name"],
                "description": service["description"],
                "estimated_hours": service["estimated_hours"],
                "is_active": True
            })
        
        await db.service_categories.insert_many(service_docs)
        print(f"✓ Inserted {len(service_docs)} services")
    
    # ======================
    # SUMMARY
    # ======================
    categories_count = await db.categories.count_documents({})
    subcategories_count = await db.subcategories.count_documents({})
    services_count = await db.service_categories.count_documents({})
    
    print(f"\n{'='*70}")
    print("REFERENCE DATA SEEDING COMPLETE")
    print(f"{'='*70}")
    print(f"\nCurrent Database State:")
    print(f"  Categories: {categories_count}")
    print(f"  Subcategories: {subcategories_count}")
    print(f"  Services: {services_count}")
    print(f"\n✅ Reference data seeded successfully!\n")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(seed_reference_data())
