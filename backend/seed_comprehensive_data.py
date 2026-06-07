"""
Comprehensive Investigation Portal Demo Data Seeder
Creates 30 realistic investigations with mixed statuses and multiple services
"""
import asyncio
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import random

load_dotenv('/app/backend/.env')

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'investigation_portal')

# Test data
INSURED_NAMES = [
    "Rajesh Kumar Singh", "Priya Sharma Patel", "Amit Kumar Verma", "Sunita Devi Reddy",
    "Vikram Singh Rathore", "Anjali Sharma", "Suresh Nair", "Deepika Iyer",
    "Arun Joshi", "Kavita Desai", "Ramesh Gupta", "Meena Kapoor",
    "Sanjay Mehta", "Pooja Malhotra", "Rakesh Bansal", "Neha Aggarwal",
    "Manoj Khanna", "Swati Bhatia", "Kiran Rao", "Vijay Kulkarni",
    "Ritu Sinha", "Ashok Pandey", "Geeta Mishra", "Nitin Chopra",
    "Smita Jain", "Harish Dubey", "Nisha Saxena", "Mohit Arora",
    "Anita Tiwari", "Praveen Soni"
]

ASSESSOR_NOTES = [
    "Please conduct thorough verification and submit detailed findings within 7 days.",
    "High priority case. Expedite investigation and report within 3 days.",
    "Multiple discrepancies noted in initial review. Verify all details carefully and cross-check documents.",
    "Previous claim history exists. Check for any patterns or inconsistencies with prior submissions.",
    "Claimant has requested urgent processing. Maintain quality standards while expediting.",
    "Complex case requiring detailed investigation. Take necessary time for accuracy and completeness.",
    "Standard verification required. Follow established protocols and guidelines strictly.",
    "Suspected fraud indicators present. Investigate thoroughly and document all evidence properly.",
    "Premium client case. Provide comprehensive report with supporting documentation and photos.",
    "Medical records seem inconsistent. Verify with multiple independent sources and hospital administration."
]

# Comprehensive category to service mapping
INVESTIGATION_TEMPLATES = [
    # Hospital Verification
    {
        "category": "Hospital Verification",
        "services": ["Hospital Visit", "Mobile Photo/Video Capture", "Report Drafting - Final"],
        "count": 3
    },
    {
        "category": "Hospital Verification",
        "services": ["Hospital Visit", "Medical Record Verification", "Document Verification"],
        "count": 2
    },
    
    # Death Verification
    {
        "category": "Death Verification",
        "services": ["Hospital Visit", "Mobile Photo/Video Capture", "Report Drafting - Final"],
        "count": 3
    },
    {
        "category": "Death Verification",
        "services": ["Hospital Visit", "Medical Record Verification", "Document Pickup / Delivery"],
        "count": 2
    },
    
    # Address Verification
    {
        "category": "Address Verification",
        "services": ["Physical Verification", "Mobile Photo/Video Capture", "Neighbor Interview"],
        "count": 3
    },
    {
        "category": "Address Verification",
        "services": ["Physical Verification", "Document Verification", "Mobile Photo/Video Capture"],
        "count": 2
    },
    
    # Identity Verification
    {
        "category": "Identity Verification",
        "services": ["Document Pickup / Delivery", "Mobile Photo/Video Capture", "Document Verification"],
        "count": 3
    },
    {
        "category": "Identity Verification",
        "services": ["In-Person Meeting", "Mobile Photo/Video Capture", "Report Drafting - Final"],
        "count": 2
    },
    
    # Medical Verification
    {
        "category": "Medical Verification",
        "services": ["Hospital Visit", "Medical Record Verification", "Mobile Photo/Video Capture"],
        "count": 3
    },
    
    # Income Verification
    {
        "category": "Income Verification",
        "services": ["Document Verification", "Mobile Photo/Video Capture", "Report Drafting - Final"],
        "count": 2
    },
    
    # Bank Verification
    {
        "category": "Bank Verification",
        "services": ["Bank Visit", "Document Verification", "Mobile Photo/Video Capture"],
        "count": 2
    },
    
    # Employment Verification
    {
        "category": "Employment Verification",
        "services": ["Employer Visit", "Document Verification", "Mobile Photo/Video Capture"],
        "count": 2
    },
    
    # Digital Verification
    {
        "category": "Digital Verification",
        "services": ["Digital Interview", "Document Verification", "Report Drafting - Final"],
        "count": 2
    },
]


async def seed_comprehensive_data():
    print("="*80)
    print("COMPREHENSIVE INVESTIGATION PORTAL DEMO DATA SEEDING")
    print("="*80)
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Get investigator and assessor
    investigator = await db.users.find_one({"email": "investigator@test.com"})
    assessor = await db.users.find_one({"role": "assessor"})
    
    if not investigator or not assessor:
        print("❌ Required users not found!")
        client.close()
        return
    
    investigator_id = str(investigator["_id"])
    assessor_id = str(assessor["_id"])
    
    print(f"\n✓ Investigator: {investigator['name']} ({investigator['email']})")
    print(f"✓ Assessor: {assessor['name']}")
    
    # Get database references
    categories = await db.categories.find({}).to_list(100)
    subcategories = await db.subcategories.find({}).to_list(100)
    service_categories = await db.service_categories.find({}).to_list(100)
    
    print(f"✓ Database References: {len(categories)} categories, {len(subcategories)} subcategories, {len(service_categories)} services\n")
    
    # Helper functions
    def get_category_by_name(name):
        return next((c for c in categories if c["name"] == name), None)
    
    def get_subcategory_for_category(category_id):
        matching = [s for s in subcategories if str(s["category_id"]) == str(category_id)]
        return random.choice(matching) if matching else None
    
    def get_service_by_name(name):
        return next((s for s in service_categories if s["name"] == name), None)
    
    # Status distribution: 40% assigned, 30% in_progress, 20% submitted, 10% rework_requested
    statuses = (
        ["assigned"] * 12 + 
        ["in_progress"] * 9 + 
        ["submitted"] * 6 + 
        ["rework_requested"] * 3
    )
    random.shuffle(statuses)
    
    investigations = []
    activities = []
    base_inv_number = 1
    
    print("Generating 30 investigation cases with mixed statuses...\n")
    
    case_index = 0
    for template in INVESTIGATION_TEMPLATES:
        for _ in range(template["count"]):
            if case_index >= 30:
                break
            
            category = get_category_by_name(template["category"])
            if not category:
                continue
            
            category_id = str(category["_id"])
            subcategory = get_subcategory_for_category(category_id)
            if not subcategory:
                continue
            
            subcategory_id = str(subcategory["_id"])
            
            # Build services
            services = []
            for svc_name in template["services"]:
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
                continue
            
            # Generate investigation data
            inv_num = base_inv_number + case_index
            investigation_id = f"INV{str(inv_num).zfill(6)}"
            claim_number = f"CLM{str(2000000 + inv_num).zfill(7)}"
            policy_number = f"N{str(100000 + inv_num).zfill(7)}"
            insured_name = INSURED_NAMES[case_index % len(INSURED_NAMES)]
            status = statuses[case_index % len(statuses)]
            
            # Date logic based on status
            if status == "assigned":
                assigned_days_ago = random.randint(0, 3)
                assigned_date = datetime.now(timezone.utc) - timedelta(days=assigned_days_ago)
                due_date = assigned_date + timedelta(days=random.randint(10, 21))
            elif status == "in_progress":
                assigned_days_ago = random.randint(3, 10)
                assigned_date = datetime.now(timezone.utc) - timedelta(days=assigned_days_ago)
                due_date = assigned_date + timedelta(days=random.randint(10, 21))
            elif status == "submitted":
                assigned_days_ago = random.randint(10, 20)
                assigned_date = datetime.now(timezone.utc) - timedelta(days=assigned_days_ago)
                due_date = assigned_date + timedelta(days=random.randint(10, 21))
            else:  # rework_requested
                assigned_days_ago = random.randint(15, 25)
                assigned_date = datetime.now(timezone.utc) - timedelta(days=assigned_days_ago)
                due_date = assigned_date + timedelta(days=random.randint(10, 21))
            
            investigation = {
                "investigation_id": investigation_id,
                "claim_number": claim_number,
                "policy_number": policy_number,
                "insured_name": insured_name,
                "category_id": category_id,
                "sub_category_id": subcategory_id,
                "assigned_investigator_id": investigator_id,
                "assessor_id": assessor_id,
                "assessor_notes": ASSESSOR_NOTES[case_index % len(ASSESSOR_NOTES)],
                "status": status,
                "services": services,
                "due_date": due_date.isoformat(),
                "assigned_date": assigned_date.isoformat(),
                "created_at": assigned_date.isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
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
            
            status_icon = {
                "assigned": "📋",
                "in_progress": "🔄",
                "submitted": "✅",
                "rework_requested": "🔁"
            }
            
            print(f"{status_icon[status]} {investigation_id} - {template['category'][:30]:<30} - {status:<20} - {len(services)} services")
            
            case_index += 1
    
    if not investigations:
        print("\n❌ No investigations generated!")
        client.close()
        return
    
    # Insert data
    print(f"\n{'='*80}")
    print(f"Inserting {len(investigations)} investigations...")
    result = await db.investigations.insert_many(investigations)
    print(f"✓ Inserted {len(result.inserted_ids)} investigations")
    
    await db.activities.insert_many(activities)
    print(f"✓ Created {len(activities)} activities")
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    
    category_counts = {}
    status_counts = {}
    total_services = 0
    
    for inv in investigations:
        cat = next((c for c in categories if str(c["_id"]) == inv["category_id"]), None)
        if cat:
            category_counts[cat["name"]] = category_counts.get(cat["name"], 0) + 1
        
        status_counts[inv["status"]] = status_counts.get(inv["status"], 0) + 1
        total_services += len(inv["services"])
    
    print("\nBy Category:")
    for cat, count in sorted(category_counts.items()):
        print(f"  {cat:<30} {count}")
    
    print("\nBy Status:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status:<20} {count}")
    
    print(f"\nTotal Services: {total_services}")
    print(f"Average Services/Investigation: {total_services/len(investigations):.1f}")
    
    print(f"\n{'='*80}")
    print("✓ COMPREHENSIVE SEEDING COMPLETE!")
    print(f"{'='*80}")
    print(f"\nTest Account: investigator@test.com")
    print(f"Total Cases: {len(investigations)}")
    print(f"  📋 Assigned: {status_counts.get('assigned', 0)}")
    print(f"  🔄 In Progress: {status_counts.get('in_progress', 0)}")
    print(f"  ✅ Submitted: {status_counts.get('submitted', 0)}")
    print(f"  🔁 Rework Requested: {status_counts.get('rework_requested', 0)}")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(seed_comprehensive_data())
