"""
Fixed Additional Demo Data Seeder for Investigation Portal
Creates 30 realistic assigned investigation cases with proper ID references
"""
import asyncio
import sys
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import random

load_dotenv('/app/backend/.env')

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'investigation_portal')

# Realistic test data
INSURED_NAMES = [
    "Rajesh Kumar", "Priya Sharma", "Amit Patel", "Sunita Verma", "Vikram Singh",
    "Anjali Reddy", "Suresh Nair", "Deepika Iyer", "Arun Joshi", "Kavita Desai",
    "Ramesh Gupta", "Meena Kapoor", "Sanjay Mehta", "Pooja Malhotra", "Rakesh Bansal",
    "Neha Aggarwal", "Manoj Khanna", "Swati Bhatia", "Kiran Rao", "Vijay Kulkarni",
    "Ritu Sinha", "Ashok Pandey", "Geeta Mishra", "Nitin Chopra", "Smita Jain",
    "Harish Dubey", "Nisha Saxena", "Mohit Arora", "Anita Tiwari", "Praveen Soni"
]

ASSESSOR_NOTES = [
    "Please conduct thorough verification and submit detailed findings within 7 days.",
    "High priority case. Expedite investigation and report within 3 days.",
    "Multiple discrepancies noted in initial review. Verify all details carefully.",
    "Previous claim history exists. Check for any patterns or inconsistencies.",
    "Claimant has requested urgent processing. Maintain quality standards.",
    "Complex case requiring detailed investigation. Take necessary time for accuracy.",
    "Standard verification required. Follow established protocols and guidelines.",
    "Suspected fraud indicators present. Investigate thoroughly and document evidence.",
    "Premium client case. Provide comprehensive report with supporting documentation.",
    "Medical records seem inconsistent. Verify with multiple independent sources."
]

# Category to services mapping (will be looked up from database)
CATEGORY_SERVICE_MAP = {
    "Death Verification": ["Hospital Visit", "Medical Report Collection", "Mobile Photo/Video Capture"],
    "Hospital Verification": ["Hospital Visit", "Medical Record Verification", "Document Verification"],
    "Medical Verification": ["Hospital Visit", "Medical Report Collection", "Mobile Photo/Video Capture"],
    "Address Verification": ["Physical Verification", "Mobile Photo/Video Capture", "Neighbor Interview"],
    "Identity Verification": ["Document Verification", "Mobile Photo/Video Capture", "In-Person Meeting"],
    "Income Verification": ["Document Verification", "Bank Visit", "Employer Verification"],
    "Bank Verification": ["Bank Visit", "Document Verification", "Account Statement Collection"],
    "Legal Verification": ["Court Visit", "Legal Document Collection", "Report Drafting - Final"],
}


async def seed_fixed_data():
    print("="*70)
    print("FIXED INVESTIGATION DEMO DATA SEEDING")
    print("="*70)
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Get investigator
    investigator = await db.users.find_one({"email": "investigator@test.com"})
    if not investigator:
        print("❌ investigator@test.com not found!")
        client.close()
        return
    
    investigator_id = str(investigator["_id"])
    
    # Get assessor
    assessor = await db.users.find_one({"role": "assessor"})
    if not assessor:
        print("❌ Assessor not found!")
        client.close()
        return
    
    assessor_id = str(assessor["_id"])
    
    print(f"\n✓ Investigator: {investigator['name']} ({investigator['email']})")
    print(f"✓ Assessor: {assessor['name']}")
    
    # Get all categories, subcategories, and services from database
    categories = await db.categories.find({}).to_list(100)
    subcategories = await db.subcategories.find({}).to_list(100)
    service_categories = await db.service_categories.find({}).to_list(100)
    
    print(f"✓ Available Categories: {len(categories)}")
    print(f"✓ Available Subcategories: {len(subcategories)}")
    print(f"✓ Available Services: {len(service_categories)}")
    
    # Helper functions
    def get_category_by_name(name):
        for cat in categories:
            if cat["name"] == name:
                return cat
        return None
    
    def get_subcategory_for_category(category_id):
        matching = [s for s in subcategories if str(s["category_id"]) == str(category_id)]
        return random.choice(matching) if matching else None
    
    def get_service_by_name(name):
        for svc in service_categories:
            if svc["name"] == name:
                return svc
        return None
    
    # Count existing investigations
    existing_count = await db.investigations.count_documents({})
    print(f"\nExisting investigations: {existing_count}")
    
    # Generate 30 new cases
    investigations = []
    activities = []
    base_inv_number = existing_count + 1
    
    print(f"\nGenerating 30 new investigation cases...\n")
    
    # Use available categories
    available_categories = [
        "Death Verification",
        "Hospital Verification", 
        "Medical Verification",
        "Address Verification",
        "Identity Verification",
        "Income Verification",
        "Bank Verification",
        "Legal Verification"
    ]
    
    for i in range(30):
        # Select category
        category_name = available_categories[i % len(available_categories)]
        category = get_category_by_name(category_name)
        
        if not category:
            print(f"⚠ Category '{category_name}' not found, skipping...")
            continue
        
        category_id = str(category["_id"])
        
        # Get subcategory for this category
        subcategory = get_subcategory_for_category(category_id)
        if not subcategory:
            print(f"⚠ No subcategory found for '{category_name}', skipping...")
            continue
        
        subcategory_id = str(subcategory["_id"])
        
        # Get services for this category
        service_names = CATEGORY_SERVICE_MAP.get(category_name, ["Hospital Visit", "Report Drafting - Final"])
        
        # Build services array
        services = []
        for svc_name in service_names[:3]:  # Limit to 3 services per case
            service_cat = get_service_by_name(svc_name)
            if service_cat:
                services.append({
                    "id": str(uuid4()),
                    "service_category_id": str(service_cat["_id"]),
                    "service_name": service_cat["name"],
                    "remarks": f"Standard {svc_name.lower()} required",
                    "status": "pending",
                    "evidence_count": 0,
                    "completed_at": None
                })
        
        if not services:
            print(f"⚠ No services found for case {i+1}, skipping...")
            continue
        
        # Generate investigation data
        inv_num = base_inv_number + i
        investigation_id = f"INV{str(inv_num).zfill(6)}"
        claim_number = f"CLM{str(2000000 + inv_num).zfill(7)}"
        policy_number = f"N{str(100000 + inv_num).zfill(7)}"
        insured_name = INSURED_NAMES[i % len(INSURED_NAMES)]
        
        # Dates
        assigned_days_ago = random.randint(0, 5)
        assigned_date = datetime.now(timezone.utc) - timedelta(days=assigned_days_ago)
        due_date = assigned_date + timedelta(days=random.randint(7, 21))
        
        # Priority
        priority = random.choice(["low", "medium", "high", "urgent"])
        
        # Create investigation
        investigation = {
            "investigation_id": investigation_id,
            "claim_number": claim_number,
            "policy_number": policy_number,
            "insured_name": insured_name,
            "category_id": category_id,
            "sub_category_id": subcategory_id,
            "assigned_investigator_id": investigator_id,
            "assessor_id": assessor_id,
            "assessor_notes": ASSESSOR_NOTES[i % len(ASSESSOR_NOTES)],
            "status": "assigned",
            "services": services,
            "due_date": due_date.isoformat(),
            "assigned_date": assigned_date.isoformat(),
            "created_at": assigned_date.isoformat(),
            "updated_at": assigned_date.isoformat()
        }
        
        investigations.append(investigation)
        
        # Create activity
        activities.append({
            "investigation_id": investigation_id,
            "user_id": assessor_id,
            "user_name": assessor["name"],
            "action": "investigation_created",
            "description": f"Investigation created and assigned to {investigator['name']}",
            "timestamp": assigned_date.isoformat()
        })
        
        print(f"✓ Generated: {investigation_id} - {category_name} - {insured_name}")
    
    if not investigations:
        print("\n❌ No investigations generated. Check category/service data.")
        client.close()
        return
    
    # Insert investigations
    print(f"\n{'='*70}")
    print(f"Inserting {len(investigations)} investigations...")
    result = await db.investigations.insert_many(investigations)
    print(f"✓ Inserted {len(result.inserted_ids)} investigations")
    
    # Insert activities
    print(f"Creating {len(activities)} activities...")
    await db.activities.insert_many(activities)
    print(f"✓ Created {len(activities)} activities")
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    
    category_counts = {}
    priority_counts = {}
    service_counts = 0
    
    for inv in investigations:
        # Get category name for summary
        cat = next((c for c in categories if str(c["_id"]) == inv["category_id"]), None)
        if cat:
            cat_name = cat["name"]
            category_counts[cat_name] = category_counts.get(cat_name, 0) + 1
        
        priority_counts[inv["status"]] = priority_counts.get(inv["status"], 0) + 1
        service_counts += len(inv["services"])
    
    print("\nBy Category:")
    for cat, count in sorted(category_counts.items()):
        print(f"  {cat}: {count}")
    
    print(f"\nStatus:")
    for status, count in sorted(priority_counts.items()):
        print(f"  {status}: {count}")
    
    print(f"\nTotal Services: {service_counts}")
    print(f"Total Investigations: {len(investigations)}")
    
    print(f"\n{'='*70}")
    print("✓ SEEDING COMPLETE!")
    print(f"{'='*70}")
    print(f"\nTest Account: investigator@test.com")
    print(f"New Assigned Cases: {len(investigations)}")
    print(f"\nAll investigations use proper ID references and should open correctly.")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(seed_fixed_data())
