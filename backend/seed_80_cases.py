"""
Investigation Portal - 80 Demo Cases Seeder
Creates comprehensive demo data:
- 30-35 cases with status "assigned" (no evidence)
- 45-50 cases with mixed statuses (open, in_progress, submitted, completed)
- Multiple services per investigation (2-4 services)
- Evidence linked to non-assigned cases
"""
import asyncio
import sys
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import random

load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'investigation_portal')

# Realistic test data
INSURED_NAMES = [
    "Rajesh Kumar", "Priya Sharma", "Amit Patel", "Sunita Verma", "Vikram Singh",
    "Anjali Reddy", "Suresh Nair", "Deepika Iyer", "Arun Joshi", "Kavita Desai",
    "Ramesh Gupta", "Meena Kapoor", "Sanjay Mehta", "Pooja Malhotra", "Rakesh Bansal",
    "Neha Aggarwal", "Manoj Khanna", "Swati Bhatia", "Kiran Rao", "Vijay Kulkarni",
    "Ritu Sinha", "Ashok Pandey", "Geeta Mishra", "Nitin Chopra", "Smita Jain",
    "Harish Dubey", "Nisha Saxena", "Mohit Arora", "Anita Tiwari", "Praveen Soni",
    "Sandeep Yadav", "Manisha Gupta", "Ravi Shankar", "Divya Reddy", "Karthik Iyer",
    "Lakshmi Nair", "Abhishek Jain", "Sneha Kulkarni", "Aditya Verma", "Priyanka Singh",
    "Gopal Krishna", "Bhavana Rao", "Vishal Malhotra", "Nandini Desai", "Tarun Khanna",
    "Madhavi Patel", "Arjun Sharma", "Shilpa Bansal", "Gaurav Chopra", "Archana Mishra",
    "Rohan Mehta", "Kavya Tiwari", "Siddharth Pandey", "Pallavi Sinha", "Kunal Aggarwal",
    "Shruti Bhatia", "Nikhil Arora", "Vaishali Kapoor", "Akash Dubey", "Tanvi Saxena",
    "Harsh Kumar", "Preeti Singh", "Varun Joshi", "Aarti Reddy", "Sameer Nair",
    "Poornima Iyer", "Rahul Gupta", "Deepti Kulkarni", "Ajay Verma", "Meera Desai",
    "Saurabh Khanna", "Anjana Patel", "Vivek Sharma", "Nisha Bansal", "Amar Chopra",
    "Shreya Mishra", "Karan Mehta", "Roshni Tiwari", "Pankaj Pandey", "Sonal Sinha"
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
    "Medical records seem inconsistent. Verify with multiple independent sources.",
    "Urgent case. Client is requesting expedited resolution.",
    "Standard due diligence required. Follow all compliance guidelines.",
    "Cross-verify all documents with original sources.",
    "Physical verification mandatory for this investigation.",
    "Document all findings with photographic evidence where applicable."
]

# Category to services mapping
CATEGORY_SERVICE_MAP = {
    "Death Verification": ["Hospital Visit", "Medical Report Collection", "Mobile Photo/Video Capture", "Report Drafting - Final"],
    "Hospital Verification": ["Hospital Visit", "Medical Record Verification", "Document Verification", "Report Drafting - Final"],
    "Medical Verification": ["Hospital Visit", "Medical Report Collection", "Mobile Photo/Video Capture", "Report Drafting - Final"],
    "Address Verification": ["Physical Verification", "Mobile Photo/Video Capture", "Report Drafting - Final"],
    "Identity Verification": ["Document Verification", "Mobile Photo/Video Capture", "In-Person Meeting", "Report Drafting - Final"],
    "Income Verification": ["Document Verification", "Bank Visit", "Employer Verification", "Report Drafting - Final"],
    "Bank Verification": ["Bank Visit", "Document Verification", "Account Statement Collection", "Report Drafting - Final"],
}

EVIDENCE_FILENAMES = [
    "hospital_bill.pdf", "medical_report.pdf", "xray_scan.jpg", "doctor_prescription.pdf",
    "house_photo_front.jpg", "house_photo_back.jpg", "id_card_scan.pdf", "aadhaar_copy.pdf",
    "bank_statement.pdf", "salary_slip.pdf", "employment_letter.pdf", "pan_card.pdf",
    "death_certificate.pdf", "police_report.pdf", "witness_statement.pdf", "property_photo.jpg",
    "vehicle_photo.jpg", "interview_recording.mp3", "site_visit_video.mp4", "neighbor_statement.pdf"
]


async def seed_80_cases():
    print("="*70)
    print("80 DEMO CASES SEEDING - INVESTIGATION PORTAL")
    print("="*70)
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Get investigator and assessor
    investigator = await db.users.find_one({
        "email": "investigator@test.com"
    })

    assessor = await db.users.find_one({
        "email": "jane.assessor@investigationportal.com"
    })

    if not investigator:
        print("❌ Investigator not found: investigator@test.com")
        client.close()
        return

    if not assessor:
        print("❌ Assessor not found: jane.assessor@investigationportal.com")
        client.close()
        return
    
    investigator_id = str(investigator["_id"])
    assessor_id = str(assessor["_id"])
    
    print(f"\n✓ Investigator: {investigator['name']} ({investigator['email']})")
    print(f"✓ Assessor: {assessor['name']}")
    
    # Get database reference data
    categories = await db.categories.find({}).to_list(100)
    subcategories = await db.subcategories.find({}).to_list(100)
    service_categories = await db.service_categories.find({}).to_list(100)
    
    print(f"✓ Categories: {len(categories)}")
    print(f"✓ Subcategories: {len(subcategories)}")
    print(f"✓ Services: {len(service_categories)}")
    
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
    
    # WIPE EXISTING INVESTIGATIONS
    print("\n" + "="*70)
    print("WIPING EXISTING INVESTIGATIONS...")
    delete_result = await db.investigations.delete_many({})
    print(f"✓ Deleted {delete_result.deleted_count} existing investigations")
    
    # Also clear evidence and activities for clean slate
    await db.evidence.delete_many({})
    await db.activities.delete_many({})
    print("✓ Cleared evidence and activities")
    
    # Available categories
    available_categories = list(CATEGORY_SERVICE_MAP.keys())
    
    # Determine split: 30-35 assigned, rest mixed (generate extra to account for skips)
    target_total = 80
    generate_count = 95  # Generate more to account for skips
    assigned_count = 33  # Fixed count for assigned
    
    print(f"\n{'='*70}")
    print(f"GENERATION PLAN:")
    print(f"  • Target: {target_total} total cases")
    print(f"  • Assigned cases (no evidence): ~{assigned_count}")
    print(f"  • Mixed status cases (with evidence): ~{target_total - assigned_count}")
    print(f"{'='*70}\n")
    
    investigations = []
    activities = []
    evidence_items = []
    
    # Available statuses for mixed cases
    mixed_statuses = ["in_progress", "submitted", "completed"]
    
    # Generate cases (with buffer for skips)
    for i in range(generate_count):
        is_assigned = i < assigned_count
        status = "assigned" if is_assigned else random.choice(mixed_statuses)
        
        # Select category
        category_name = random.choice(available_categories)
        category = get_category_by_name(category_name)
        
        if not category:
            print(f"⚠ Category '{category_name}' not found, skipping...")
            continue
        
        category_id = str(category["_id"])
        
        # Get subcategory
        subcategory = get_subcategory_for_category(category_id)
        if not subcategory:
            print(f"⚠ No subcategory found for '{category_name}', skipping...")
            continue
        
        subcategory_id = str(subcategory["_id"])
        
        # Get services for this category (2-4 services per investigation)
        service_names = CATEGORY_SERVICE_MAP.get(category_name, ["Hospital Visit", "Report Drafting - Final"])
        num_services = random.randint(2, min(4, len(service_names)))
        selected_service_names = random.sample(service_names, num_services)
        
        # Build services array
        services = []
        for svc_name in selected_service_names:
            service_cat = get_service_by_name(svc_name)
            if service_cat:
                service_status = "pending" if is_assigned else random.choice(["pending", "completed"])
                services.append({
                    "id": str(uuid4()),
                    "service_category_id": str(service_cat["_id"]),
                    "service_name": service_cat["name"],
                    "remarks": f"Standard {svc_name.lower()} required",
                    "status": service_status,
                    "evidence_count": 0,  # Will be updated when evidence is added
                    "completed_at": None if service_status == "pending" else datetime.now(timezone.utc).isoformat()
                })
        
        if not services:
            print(f"⚠ No services found for case {i+1}, skipping...")
            continue
        
        # Generate investigation data
        inv_num = i + 1
        investigation_id = f"INV{str(inv_num).zfill(6)}"
        claim_number = f"CLM{str(3000000 + inv_num).zfill(7)}"
        policy_number = f"N{str(200000 + inv_num).zfill(7)}"
        insured_name = INSURED_NAMES[i % len(INSURED_NAMES)]
        
        # Dates
        assigned_days_ago = random.randint(1, 30)
        assigned_date = datetime.now(timezone.utc) - timedelta(days=assigned_days_ago)
        due_date = assigned_date + timedelta(days=random.randint(7, 21))
        
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
        
        # Add evidence for non-assigned cases
        if not is_assigned:
            # Random number of evidence items (1-3 per service)
            completed_services = [s for s in services if s["status"] == "completed"]
            if completed_services:
                num_evidence = random.randint(1, min(3, len(completed_services) * 2))
                
                for ev_idx in range(num_evidence):
                    # Randomly link to 1-2 services
                    num_linked = random.randint(1, min(2, len(services)))
                    linked_services = [s["id"] for s in random.sample(services, num_linked)]
                    
                    evidence_filename = random.choice(EVIDENCE_FILENAMES)
                    evidence_id = str(uuid4())
                    
                    # Create mock evidence
                    evidence = {
                        "id": evidence_id,
                        "investigation_id": investigation_id,
                        "linked_services": linked_services,
                        "storage_path": f"mock/storage/{investigation_id}/{evidence_id}/{evidence_filename}",
                        "original_filename": evidence_filename,
                        "content_type": "application/pdf" if evidence_filename.endswith(".pdf") else "image/jpeg",
                        "size": random.randint(50000, 500000),
                        "latitude": 12.9716 + random.uniform(-0.5, 0.5) if random.random() > 0.3 else None,
                        "longitude": 77.5946 + random.uniform(-0.5, 0.5) if random.random() > 0.3 else None,
                        "notes": f"Evidence for {', '.join([s['service_name'] for s in services if s['id'] in linked_services])}",
                        "uploaded_by": investigator_id,
                        "uploaded_by_name": investigator["name"],
                        "is_deleted": False,
                        "created_at": (assigned_date + timedelta(days=random.randint(1, max(2, assigned_days_ago)))).isoformat()
                    }
                    
                    evidence_items.append(evidence)
                    
                    # Update evidence count for linked services
                    for svc in services:
                        if svc["id"] in linked_services:
                            svc["evidence_count"] = svc.get("evidence_count", 0) + 1
        
        # Update investigation with final evidence counts
        investigation["services"] = services
        
        status_emoji = "📋" if is_assigned else "✅"
        print(f"{status_emoji} Case {i+1}/80: {investigation_id} - {status.upper()} - {category_name} ({len(services)} services)")
    
    if not investigations:
        print("\n❌ No investigations generated!")
        client.close()
        return
    
    # Insert data
    print(f"\n{'='*70}")
    print(f"INSERTING DATA INTO DATABASE...")
    
    result = await db.investigations.insert_many(investigations)
    print(f"✓ Inserted {len(result.inserted_ids)} investigations")
    
    if activities:
        await db.activities.insert_many(activities)
        print(f"✓ Created {len(activities)} activities")
    
    if evidence_items:
        await db.evidence.insert_many(evidence_items)
        print(f"✓ Inserted {len(evidence_items)} evidence items")
    
    # Summary statistics
    print(f"\n{'='*70}")
    print("SUMMARY STATISTICS")
    print(f"{'='*70}")
    
    status_counts = {}
    category_counts = {}
    total_services = 0
    total_evidence = len(evidence_items)
    
    for inv in investigations:
        status_counts[inv["status"]] = status_counts.get(inv["status"], 0) + 1
        
        cat = next((c for c in categories if str(c["_id"]) == inv["category_id"]), None)
        if cat:
            category_counts[cat["name"]] = category_counts.get(cat["name"], 0) + 1
        
        total_services += len(inv["services"])
    
    print("\nBy Status:")
    for status, count in sorted(status_counts.items()):
        print(f"  • {status.replace('_', ' ').title()}: {count}")
    
    print("\nBy Category:")
    for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {cat}: {count}")
    
    print(f"\nTotals:")
    print(f"  • Investigations: {len(investigations)}")
    print(f"  • Services: {total_services}")
    print(f"  • Evidence Items: {total_evidence}")
    print(f"  • Activities: {len(activities)}")
    
    print(f"\n{'='*70}")
    print("✓ SEEDING COMPLETE!")
    print(f"{'='*70}")
    print(f"\nTest Account: {investigator['email']}")
    print(f"Password: Investigator@123")
    print(f"\nAssigned cases have NO evidence.")
    print(f"Mixed status cases have evidence linked to multiple services.")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(seed_80_cases())
