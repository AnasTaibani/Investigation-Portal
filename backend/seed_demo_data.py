import asyncio
import os
import sys
import random
from pathlib import Path
from datetime import datetime, timedelta, timezone
import uuid

sys.path.insert(0, str(Path(__file__).parent))

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Sample data
INVESTIGATOR_NAMES = [
    "John Smith", "Sarah Johnson", "Michael Chen", "Emily Davis", "Robert Garcia",
    "Jennifer Martinez", "David Lee", "Lisa Anderson", "James Wilson", "Maria Rodriguez",
    "William Taylor", "Patricia Brown", "Richard Jones", "Linda Miller", "Thomas Moore",
    "Barbara Jackson", "Christopher White", "Elizabeth Harris", "Daniel Martin", "Susan Thompson"
]

INSURED_NAMES = [
    "Alice Cooper", "Bob Williams", "Carol Green", "David Brown", "Emma Wilson",
    "Frank Martinez", "Grace Lee", "Henry Davis", "Ivy Chen", "Jack Robinson",
    "Kate Thompson", "Leo Garcia", "Maya Patel", "Noah Singh", "Olivia Kim",
    "Peter Wong", "Quinn Taylor", "Rachel Lee", "Sam Johnson", "Tina Anderson"
]

CLAIM_PREFIXES = ["CLM", "CLAIM", "CL"]
POLICY_PREFIXES = ["POL", "POLICY", "P"]

CITIES = ["Singapore", "Kuala Lumpur", "Jakarta", "Manila", "Bangkok", "Ho Chi Minh City", "Hanoi", "Yangon"]

STATUSES = ["assigned", "in_progress", "submitted", "rework_requested", "completed", "closed"]

SERVICE_REMARKS = [
    "Verify hospital admission records",
    "Confirm identity with government ID",
    "Collect witness statements",
    "Photograph property damage",
    "Interview family members",
    "Obtain medical records",
    "Verify employment status",
    "Check financial documents",
    "Inspect accident scene",
    "Record video evidence"
]

FINDINGS_TEMPLATES = {
    "genuine": {
        "summary": "Investigation completed successfully. All documentation verified and authentic.",
        "observations": "Claimant cooperative. Documents provided are legitimate. Witness statements consistent.",
        "findings": "All evidence supports the claim. No discrepancies found in documentation or statements.",
        "conclusion": "Claim appears legitimate based on investigation findings.",
        "outcome": "genuine",
        "recommendation": "approve"
    },
    "suspicious": {
        "summary": "Investigation reveals inconsistencies requiring further review.",
        "observations": "Some discrepancies noted in timeline. Documentation partially verified.",
        "findings": "Minor inconsistencies found but not conclusive of fraud.",
        "conclusion": "Recommend further investigation before final decision.",
        "outcome": "suspicious",
        "recommendation": "further_investigation"
    },
    "fraud": {
        "summary": "Investigation uncovered evidence of potential fraud.",
        "observations": "Multiple red flags identified. Documentation appears forged. Witness statements contradict.",
        "findings": "Strong evidence suggests fraudulent claim. Forged documents detected.",
        "conclusion": "Recommend claim rejection due to fraud indicators.",
        "outcome": "fraud_suspected",
        "recommendation": "reject"
    }
}

async def seed_demo_data():
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    print("=== Starting Demo Data Seeding ===\n")
    
    # Get existing data
    categories = await db.categories.find({}).to_list(100)
    subcategories = await db.subcategories.find({}).to_list(100)
    service_categories = await db.service_categories.find({}).to_list(100)
    
    if not categories:
        print("⚠️  No categories found. Run seed_data.py first.")
        return
    
    print(f"✓ Found {len(categories)} categories, {len(subcategories)} subcategories, {len(service_categories)} services\n")
    
    # Create 20 investigators
    print("Creating investigators...")
    investigators = []
    for i, name in enumerate(INVESTIGATOR_NAMES[:20]):
        email = f"investigator{i+1}@test.com"
        existing = await db.users.find_one({"email": email})
        if not existing:
            from server import hash_password
            user_doc = {
                "email": email,
                "password_hash": hash_password(f"Inv{i+1}@123"),
                "name": name,
                "role": "investigator",
                "phone": f"+65-{random.randint(8000, 9999)}-{random.randint(1000, 9999)}",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            result = await db.users.insert_one(user_doc)
            investigators.append({"id": str(result.inserted_id), "name": name})
        else:
            investigators.append({"id": str(existing["_id"]), "name": existing["name"]})
    
    print(f"✓ Created/found {len(investigators)} investigators\n")
    
    # Get assessor
    assessor = await db.users.find_one({"role": "assessor"})
    if not assessor:
        print("⚠️  No assessor found")
        return
    
    # Create 250 investigation cases
    print("Creating investigation cases...")
    
    base_date = datetime.now(timezone.utc) - timedelta(days=90)
    cases_created = 0
    
    for i in range(250):
        # Random timing
        days_offset = random.randint(0, 90)
        assigned_date = base_date + timedelta(days=days_offset)
        due_date = assigned_date + timedelta(days=random.randint(5, 14))
        
        # Random category and subcategory
        category = random.choice(categories)
        category_subs = [s for s in subcategories if s["category_id"] == str(category["_id"])]
        if not category_subs:
            continue
        subcategory = random.choice(category_subs)
        
        # Random investigator
        investigator = random.choice(investigators)
        
        # Random status with realistic distribution
        status_weights = {
            "assigned": 0.15,
            "in_progress": 0.25,
            "submitted": 0.20,
            "rework_requested": 0.10,
            "completed": 0.20,
            "closed": 0.10
        }
        status = random.choices(list(status_weights.keys()), weights=list(status_weights.values()))[0]
        
        # Generate unique IDs
        case_num = i + 1
        investigation_id = f"INV{str(case_num).zfill(6)}"
        claim_number = f"{random.choice(CLAIM_PREFIXES)}{random.randint(100000, 999999)}"
        policy_number = f"{random.choice(POLICY_PREFIXES)}{random.randint(1000000, 9999999)}"
        insured_name = random.choice(INSURED_NAMES)
        
        # Generate services
        num_services = random.randint(2, 4)
        selected_services = random.sample(service_categories, min(num_services, len(service_categories)))
        services = []
        for svc in selected_services:
            service_status = "completed" if status in ["submitted", "completed", "closed"] else random.choice(["pending", "completed"])
            services.append({
                "id": str(uuid.uuid4()),
                "service_category_id": str(svc["_id"]),
                "service_name": svc["name"],
                "remarks": random.choice(SERVICE_REMARKS),
                "status": service_status,
                "evidence_count": random.randint(0, 5) if service_status == "completed" else 0,
                "completed_at": (assigned_date + timedelta(days=random.randint(1, 5))).isoformat() if service_status == "completed" else None
            })
        
        case_doc = {
            "investigation_id": investigation_id,
            "claim_number": claim_number,
            "policy_number": policy_number,
            "insured_name": insured_name,
            "category_id": str(category["_id"]),
            "sub_category_id": str(subcategory["_id"]),
            "assigned_investigator_id": investigator["id"],
            "assessor_id": str(assessor["_id"]),
            "assessor_notes": f"Please investigate {category['name']} case for {insured_name}. Verify all documentation and provide detailed report.",
            "status": status,
            "services": services,
            "due_date": due_date.isoformat(),
            "assigned_date": assigned_date.isoformat(),
            "created_at": assigned_date.isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Add findings for submitted/completed/closed cases
        if status in ["submitted", "completed", "closed"]:
            finding_type = random.choice(["genuine", "genuine", "genuine", "suspicious", "fraud"])  # 60% genuine
            template = FINDINGS_TEMPLATES[finding_type]
            case_doc["findings"] = {
                **template,
                "submitted_by": investigator["id"],
                "submitted_by_name": investigator["name"],
                "submitted_at": (assigned_date + timedelta(days=random.randint(3, 7))).isoformat()
            }
        
        # Add rework history for rework_requested cases
        if status == "rework_requested":
            case_doc["rework_history"] = [{
                "id": str(uuid.uuid4()),
                "reason": "Additional documentation required",
                "additional_instructions": "Please provide hospital admission records and interview witness again.",
                "expected_deliverables": "Updated witness statement, hospital records scan",
                "requested_by": str(assessor["_id"]),
                "requested_by_name": assessor["name"],
                "requested_at": (assigned_date + timedelta(days=random.randint(4, 6))).isoformat()
            }]
        
        await db.investigations.insert_one(case_doc)
        
        # Create activity log
        activities = [
            {
                "investigation_id": investigation_id,
                "user_id": str(assessor["_id"]),
                "user_name": assessor["name"],
                "action": "case_assigned",
                "description": f"Investigation case assigned to {investigator['name']}",
                "timestamp": assigned_date.isoformat()
            }
        ]
        
        if status != "assigned":
            activities.append({
                "investigation_id": investigation_id,
                "user_id": investigator["id"],
                "user_name": investigator["name"],
                "action": "status_changed",
                "description": "Status changed to in_progress",
                "timestamp": (assigned_date + timedelta(hours=random.randint(2, 24))).isoformat()
            })
        
        if status in ["submitted", "completed", "closed"]:
            activities.append({
                "investigation_id": investigation_id,
                "user_id": investigator["id"],
                "user_name": investigator["name"],
                "action": "findings_submitted",
                "description": "Investigation findings submitted",
                "timestamp": (assigned_date + timedelta(days=random.randint(3, 7))).isoformat()
            })
        
        await db.activities.insert_many(activities)
        
        # Create notification
        await db.notifications.insert_one({
            "user_id": investigator["id"],
            "investigation_id": investigation_id,
            "type": "case_assignment",
            "message": f"New investigation case {investigation_id} assigned to you",
            "is_read": status != "assigned",  # Mark as read if case has progressed
            "created_at": assigned_date.isoformat()
        })
        
        cases_created += 1
        if cases_created % 50 == 0:
            print(f"  Created {cases_created} cases...")
    
    print(f"✓ Created {cases_created} investigation cases\n")
    
    print("=== Demo Data Seeding Complete ===")
    print(f"\nSummary:")
    print(f"  - {len(investigators)} investigators")
    print(f"  - {cases_created} investigation cases")
    print(f"  - Statuses: Assigned, In Progress, Submitted, Rework Requested, Completed, Closed")
    print(f"  - Date range: Last 90 days")
    print(f"\nYou can now login and explore the portal with realistic data!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_demo_data())
