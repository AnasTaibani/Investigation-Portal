import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
import uuid

sys.path.insert(0, str(Path(__file__).parent))

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def seed_investigator_demo_data():
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    print("="*70)
    print("INVESTIGATOR DEMO DATA SEEDING - Complete UAT Dataset")
    print("="*70)
    
    # Get investigator account
    investigator = await db.users.find_one({"email": "investigator@test.com"})
    if not investigator:
        print("❌ Investigator account not found. Run seed_data.py first.")
        return
    
    investigator_id = str(investigator["_id"])
    investigator_name = investigator["name"]
    
    # Update investigator profile
    await db.users.update_one(
        {"_id": investigator["_id"]},
        {"$set": {
            "name": "John Anderson",
            "agency_id": "agency-apex",
            "phone": "+60 12-345-6789"
        }}
    )
    
    # Create agency
    agency_exists = await db.agencies.find_one({"name": "Apex Investigation Services"})
    if not agency_exists:
        await db.agencies.insert_one({
            "name": "Apex Investigation Services",
            "contact_person": "Michael Wong",
            "email": "contact@apexinvestigations.com",
            "phone": "+60 12-999-8888",
            "address": "Level 15, Menara IQ, Kuala Lumpur",
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
    
    # Get assessor
    assessor = await db.users.find_one({"role": "assessor"})
    assessor_id = str(assessor["_id"])
    assessor_name = assessor["name"]
    
    # Get categories and subcategories
    categories = await db.categories.find({}).to_list(100)
    subcategories = await db.subcategories.find({}).to_list(100)
    service_categories = await db.service_categories.find({}).to_list(100)
    
    print(f"\n✓ Investigator: {investigator_name} ({investigator['email']})")
    print(f"✓ Agency: Apex Investigation Services")
    print(f"✓ Assessor: {assessor_name}")
    print(f"✓ Categories: {len(categories)}, Subcategories: {len(subcategories)}, Services: {len(service_categories)}\n")
    
    # Helper functions
    def get_category_by_name(name):
        return next((c for c in categories if c["name"] == name), None)
    
    def get_subcategory_by_name(category_id, name):
        return next((s for s in subcategories if s["category_id"] == category_id and s["name"] == name), None)
    
    def get_service_by_name(name):
        return next((s for s in service_categories if s["name"] == name), None)
    
    base_date = datetime.now(timezone.utc) - timedelta(days=30)
    
    # Define 15 test cases
    test_cases = [
        # ASSIGNED CASES (3)
        {
            "case_num": 1,
            "status": "assigned",
            "category": "Death Verification",
            "subcategory": "Hospital Death Certificate",
            "claim_number": "CLM100001",
            "policy_number": "POL500001",
            "insured_name": "Ahmad bin Hassan",
            "services": ["Hospital Visit", "Mobile Photo/Video Capture", "Report Drafting - Final"],
            "assessor_notes": "Verify cause of death and obtain supporting records from hospital administration. Patient admitted on 2026-05-10, deceased on 2026-05-15. Please verify with National Heart Institute.",
            "due_days": 14,
            "assigned_days_ago": 2,
            "evidence": [],
            "findings": None
        },
        {
            "case_num": 2,
            "status": "assigned",
            "category": "Address Verification",
            "subcategory": "Home Visit",
            "claim_number": "CLM100002",
            "policy_number": "POL500002",
            "insured_name": "Siti Nurhaliza",
            "services": ["Residence Visit", "Mobile Photo/Video Capture"],
            "assessor_notes": "Verify current residence and occupancy details. Address: No. 45, Jalan Ampang, Kuala Lumpur. Confirm insured is residing at declared address.",
            "due_days": 7,
            "assigned_days_ago": 1,
            "evidence": [],
            "findings": None
        },
        {
            "case_num": 3,
            "status": "assigned",
            "category": "Identity Verification",
            "subcategory": "Passport Check",
            "claim_number": "CLM100003",
            "policy_number": "POL500003",
            "insured_name": "Lee Ming Wei",
            "services": ["Document Pickup / Delivery", "Forensics / Digital Auth Check"],
            "assessor_notes": "Verify passport authenticity. Insured claims to have lost original IC. Please verify passport details and check for any red flags.",
            "due_days": 10,
            "assigned_days_ago": 0.5,
            "evidence": [],
            "findings": None
        },
        
        # IN PROGRESS CASES (3)
        {
            "case_num": 4,
            "status": "in_progress",
            "category": "Hospital Verification",
            "subcategory": "Treatment Record & Billing Match",
            "claim_number": "CLM100004",
            "policy_number": "POL500004",
            "insured_name": "Rajesh Kumar",
            "services": ["Hospital Visit", "Hospital Bill Pattern Analysis"],
            "assessor_notes": "Verify treatment records at Prince Court Medical Centre. Claimed amount: RM 85,000. Please verify bills and treatment authenticity.",
            "due_days": 10,
            "assigned_days_ago": 5,
            "started_days_ago": 4,
            "evidence": [
                {"type": "image/jpeg", "name": "hospital_entrance.jpg", "service": "Hospital Visit", "geo": True},
                {"type": "image/jpeg", "name": "billing_counter.jpg", "service": "Hospital Visit", "geo": True},
                {"type": "image/jpeg", "name": "treatment_records.jpg", "service": "Hospital Visit", "geo": False},
                {"type": "application/pdf", "name": "billing_statement.pdf", "service": "Hospital Bill Pattern Analysis", "geo": False}
            ],
            "service_statuses": {"Hospital Visit": "completed"},
            "findings": None
        },
        {
            "case_num": 5,
            "status": "in_progress",
            "category": "Insured Alive Check",
            "subcategory": "Alive Confirmation Video",
            "claim_number": "CLM100005",
            "policy_number": "POL500005",
            "insured_name": "Tan Ah Kow",
            "services": ["Alive Check Visit / Video Call", "Mobile Photo/Video Capture"],
            "assessor_notes": "Conduct alive check via video call. Insured is 78 years old. Please verify identity and record video confirmation.",
            "due_days": 5,
            "assigned_days_ago": 3,
            "started_days_ago": 2,
            "evidence": [
                {"type": "image/jpeg", "name": "insured_selfie.jpg", "service": "Alive Check Visit / Video Call", "geo": True},
                {"type": "video/mp4", "name": "alive_check_video.mp4", "service": "Mobile Photo/Video Capture", "geo": False}
            ],
            "service_statuses": {},
            "findings": None
        },
        {
            "case_num": 6,
            "status": "in_progress",
            "category": "Medical Verification",
            "subcategory": "Hospital Record Verification",
            "claim_number": "CLM100006",
            "policy_number": "POL500006",
            "insured_name": "Wong Mei Ling",
            "services": ["Hospital Visit", "Report Drafting - Interim"],
            "assessor_notes": "Verify medical history at Gleneagles Hospital. Insured claims pre-existing condition. Please verify records from 2020-2026.",
            "due_days": 12,
            "assigned_days_ago": 6,
            "started_days_ago": 5,
            "evidence": [
                {"type": "image/jpeg", "name": "medical_records_page1.jpg", "service": "Hospital Visit", "geo": False},
                {"type": "image/jpeg", "name": "medical_records_page2.jpg", "service": "Hospital Visit", "geo": False}
            ],
            "service_statuses": {},
            "findings": None
        },
        
        # SUBMITTED CASES (2)
        {
            "case_num": 7,
            "status": "submitted",
            "category": "Income Verification",
            "subcategory": "Bank Credits",
            "claim_number": "CLM100007",
            "policy_number": "POL500007",
            "insured_name": "David Tan",
            "services": ["Bank Statement Submission & Validation"],
            "assessor_notes": "Verify income from bank statements. Claimed income: RM 15,000/month. Please verify last 6 months statements.",
            "due_days": 7,
            "assigned_days_ago": 10,
            "started_days_ago": 9,
            "submitted_days_ago": 2,
            "evidence": [
                {"type": "application/pdf", "name": "bank_statement_jan_2026.pdf", "service": "Bank Statement Submission & Validation", "geo": False},
                {"type": "application/pdf", "name": "bank_statement_feb_2026.pdf", "service": "Bank Statement Submission & Validation", "geo": False},
                {"type": "application/pdf", "name": "bank_statement_mar_2026.pdf", "service": "Bank Statement Submission & Validation", "geo": False},
                {"type": "application/pdf", "name": "verification_report.pdf", "service": "Bank Statement Submission & Validation", "geo": False}
            ],
            "service_statuses": {"Bank Statement Submission & Validation": "completed"},
            "findings": {
                "summary": "Income verification completed successfully. Bank statements verified for January to March 2026.",
                "observations": "Reviewed 3 months of bank statements from CIMB Bank. Regular salary credits of RM 15,000 observed on 25th of each month. No irregularities detected.",
                "findings": "1. Salary credits consistent with claimed amount. 2. Employment verified through salary deposits. 3. No suspicious transactions noted. 4. Bank account active and in good standing.",
                "suspicion_indicators": None,
                "conclusion": "Income verification successful. Claimed monthly income of RM 15,000 is accurate based on bank statement analysis.",
                "outcome": "genuine",
                "recommendation": "approve"
            }
        },
        {
            "case_num": 8,
            "status": "submitted",
            "category": "Source / Community Check",
            "subcategory": "Employer / Colleague",
            "claim_number": "CLM100008",
            "policy_number": "POL500008",
            "insured_name": "Sarah Abdullah",
            "services": ["Workplace Visit", "Digital Interview (Zoom/WhatsApp)"],
            "assessor_notes": "Verify employment at Tech Solutions Sdn Bhd. Claimed position: Senior Manager. Please interview HR and direct supervisor.",
            "due_days": 10,
            "assigned_days_ago": 12,
            "started_days_ago": 11,
            "submitted_days_ago": 3,
            "evidence": [
                {"type": "image/jpeg", "name": "office_building.jpg", "service": "Workplace Visit", "geo": True},
                {"type": "image/jpeg", "name": "employee_id_card.jpg", "service": "Workplace Visit", "geo": False},
                {"type": "application/pdf", "name": "interview_notes.pdf", "service": "Digital Interview (Zoom/WhatsApp)", "geo": False}
            ],
            "service_statuses": {"Workplace Visit": "completed", "Digital Interview (Zoom/WhatsApp)": "completed"},
            "findings": {
                "summary": "Employment verification conducted. Unable to fully verify all details due to company policy restrictions.",
                "observations": "Visited Tech Solutions Sdn Bhd office on Level 20, Menara KLCC. Spoke with HR Manager Ms. Lim. Company confirmed employment but declined to share salary details due to confidentiality policy.",
                "findings": "1. Employment confirmed by HR department. 2. Position verified as Senior Manager. 3. Salary details not disclosed by company policy. 4. No negative feedback from supervisor interview.",
                "suspicion_indicators": "Company reluctance to share full employment details raises minor concerns.",
                "conclusion": "Employment confirmed but income details could not be independently verified through employer.",
                "outcome": "unable_to_verify",
                "recommendation": "further_investigation"
            }
        },
        
        # REWORK REQUESTED CASES (2)
        {
            "case_num": 9,
            "status": "rework_requested",
            "category": "Address Verification",
            "subcategory": "Utility Bill Match",
            "claim_number": "CLM100009",
            "policy_number": "POL500009",
            "insured_name": "Kumar Subramaniam",
            "services": ["Residence Visit", "Mobile Photo/Video Capture"],
            "assessor_notes": "Verify residence through utility bill. Address: 123, Jalan SS2/24, Petaling Jaya. Obtain clear copy of utility bill.",
            "due_days": 7,
            "assigned_days_ago": 15,
            "started_days_ago": 14,
            "submitted_days_ago": 8,
            "rework_requested_days_ago": 7,
            "evidence": [
                {"type": "image/jpeg", "name": "house_exterior.jpg", "service": "Residence Visit", "geo": True},
                {"type": "image/jpeg", "name": "utility_bill_blurry.jpg", "service": "Mobile Photo/Video Capture", "geo": False}
            ],
            "service_statuses": {"Residence Visit": "completed", "Mobile Photo/Video Capture": "completed"},
            "findings": {
                "summary": "Address verification completed with documentation.",
                "observations": "Visited residence. Occupant confirmed as Kumar Subramaniam. Utility bill photographed.",
                "findings": "Residence verified. Utility bill obtained.",
                "suspicion_indicators": None,
                "conclusion": "Address verified successfully.",
                "outcome": "genuine",
                "recommendation": "approve"
            },
            "rework": {
                "reason": "Utility bill copy is unclear and unreadable. Date and address details cannot be verified from submitted photo.",
                "instructions": "Please revisit the residence and obtain a clearer, high-resolution photo of the utility bill. Ensure all text is legible including: 1) Account holder name, 2) Full address, 3) Bill date, 4) Account number.",
                "deliverables": "Clear utility bill photo showing all required details"
            }
        },
        {
            "case_num": 10,
            "status": "rework_requested",
            "category": "Fraud & Pattern Detection",
            "subcategory": "Suspicious Claiming Behavior",
            "claim_number": "CLM100010",
            "policy_number": "POL500010",
            "insured_name": "Lim Chee Kong",
            "services": ["Digital Interview (Zoom/WhatsApp)", "Report Drafting - Interim"],
            "assessor_notes": "Multiple claims in short period. Investigate claiming pattern. Interview insured and gather additional background information.",
            "due_days": 14,
            "assigned_days_ago": 18,
            "started_days_ago": 17,
            "submitted_days_ago": 10,
            "rework_requested_days_ago": 9,
            "evidence": [
                {"type": "application/pdf", "name": "interview_transcript.pdf", "service": "Digital Interview (Zoom/WhatsApp)", "geo": False},
                {"type": "application/pdf", "name": "interim_report.pdf", "service": "Report Drafting - Interim", "geo": False}
            ],
            "service_statuses": {"Digital Interview (Zoom/WhatsApp)": "completed"},
            "findings": {
                "summary": "Investigation into claiming pattern completed. Multiple claims identified.",
                "observations": "Insured filed 4 claims in last 12 months. Interview conducted via WhatsApp video call. Insured cooperative.",
                "findings": "Pattern of frequent claims noted. Insured provided explanations for each claim.",
                "suspicion_indicators": "High claim frequency. Similar claim types.",
                "conclusion": "Suspicious pattern identified but not conclusive of fraud.",
                "outcome": "suspicious",
                "recommendation": "further_investigation"
            },
            "rework": {
                "reason": "Need additional evidence supporting fraud indicators. Current investigation insufficient to determine fraud conclusively.",
                "instructions": "Please conduct the following additional investigations: 1) Interview at least 2 witnesses/family members, 2) Verify employment and financial status, 3) Obtain supporting documents for previous claims, 4) Check social media activity for inconsistencies.",
                "deliverables": "Witness statements, employment verification, previous claim documents, comprehensive fraud analysis report"
            }
        },
        
        # COMPLETED CASES (3)
        {
            "case_num": 11,
            "status": "completed",
            "category": "Bank Verification",
            "subcategory": "Account Ownership",
            "claim_number": "CLM100011",
            "policy_number": "POL500011",
            "insured_name": "Chen Wei Ming",
            "services": ["Bank Statement Submission & Validation"],
            "assessor_notes": "Verify bank account ownership. Account number: 1234567890 (Maybank). Confirm insured is sole account holder.",
            "due_days": 5,
            "assigned_days_ago": 25,
            "started_days_ago": 24,
            "submitted_days_ago": 20,
            "completed_days_ago": 18,
            "evidence": [
                {"type": "application/pdf", "name": "bank_account_statement.pdf", "service": "Bank Statement Submission & Validation", "geo": False},
                {"type": "image/jpeg", "name": "bank_account_details.jpg", "service": "Bank Statement Submission & Validation", "geo": False},
                {"type": "application/pdf", "name": "ownership_verification.pdf", "service": "Bank Statement Submission & Validation", "geo": False}
            ],
            "service_statuses": {"Bank Statement Submission & Validation": "completed"},
            "findings": {
                "summary": "Bank account ownership successfully verified. Account belongs to insured person.",
                "observations": "Obtained official bank statement from Maybank showing account holder name as Chen Wei Ming. Account number matches policy declaration. Account opened in 2015, active status.",
                "findings": "1. Account holder name verified as Chen Wei Ming. 2. Account number 1234567890 confirmed. 3. Sole account holder confirmed. 4. No joint account holders. 5. Account in good standing with regular activity.",
                "suspicion_indicators": None,
                "conclusion": "Bank account ownership verified successfully. No discrepancies found.",
                "outcome": "genuine",
                "recommendation": "approve"
            }
        },
        {
            "case_num": 12,
            "status": "completed",
            "category": "Identity Verification",
            "subcategory": "Signature Match",
            "claim_number": "CLM100012",
            "policy_number": "POL500012",
            "insured_name": "Fatimah Zahra",
            "services": ["Document Pickup / Delivery", "Forensics / Digital Auth Check"],
            "assessor_notes": "Verify signature on claim form matches policy application signature. Potential forgery suspected.",
            "due_days": 10,
            "assigned_days_ago": 22,
            "started_days_ago": 21,
            "submitted_days_ago": 18,
            "completed_days_ago": 16,
            "evidence": [
                {"type": "image/jpeg", "name": "claim_form_signature.jpg", "service": "Document Pickup / Delivery", "geo": False},
                {"type": "image/jpeg", "name": "policy_signature.jpg", "service": "Document Pickup / Delivery", "geo": False},
                {"type": "application/pdf", "name": "forensic_analysis_report.pdf", "service": "Forensics / Digital Auth Check", "geo": False}
            ],
            "service_statuses": {"Document Pickup / Delivery": "completed", "Forensics / Digital Auth Check": "completed"},
            "findings": {
                "summary": "Signature verification completed. Signatures match and are authentic.",
                "observations": "Collected claim form and original policy application. Signatures compared using forensic analysis methods. Key characteristics analyzed: stroke patterns, pressure points, letter formations.",
                "findings": "1. Signature on claim form matches policy application signature. 2. No signs of forgery detected. 3. Natural variations within acceptable range. 4. Writing pressure and flow consistent. 5. Forensic analysis confirms authenticity.",
                "suspicion_indicators": None,
                "conclusion": "Signature verification successful. No evidence of forgery. Signatures are authentic and match.",
                "outcome": "genuine",
                "recommendation": "approve"
            }
        },
        {
            "case_num": 13,
            "status": "completed",
            "category": "Hospital Verification",
            "subcategory": "Treatment Record & Billing Match",
            "claim_number": "CLM100013",
            "policy_number": "POL500013",
            "insured_name": "Muthu Krishnan",
            "services": ["Hospital Visit", "Hospital Bill Pattern Analysis", "Report Drafting - Final"],
            "assessor_notes": "Verify treatment at Mount Elizabeth Hospital. Claimed amount: RM 120,000 for cardiac surgery. Verify bills, treatment records, and surgeon details.",
            "due_days": 15,
            "assigned_days_ago": 28,
            "started_days_ago": 27,
            "submitted_days_ago": 22,
            "completed_days_ago": 20,
            "evidence": [
                {"type": "image/jpeg", "name": "hospital_admission.jpg", "service": "Hospital Visit", "geo": True},
                {"type": "image/jpeg", "name": "surgery_ward.jpg", "service": "Hospital Visit", "geo": True},
                {"type": "application/pdf", "name": "treatment_records.pdf", "service": "Hospital Visit", "geo": False},
                {"type": "application/pdf", "name": "hospital_bill_detailed.pdf", "service": "Hospital Bill Pattern Analysis", "geo": False},
                {"type": "application/pdf", "name": "surgeon_credentials.pdf", "service": "Hospital Visit", "geo": False},
                {"type": "application/pdf", "name": "final_investigation_report.pdf", "service": "Report Drafting - Final", "geo": False}
            ],
            "service_statuses": {
                "Hospital Visit": "completed",
                "Hospital Bill Pattern Analysis": "completed",
                "Report Drafting - Final": "completed"
            },
            "findings": {
                "summary": "Comprehensive hospital verification completed. Several irregularities identified in billing.",
                "observations": "Visited Mount Elizabeth Hospital. Verified admission records dated 2026-04-10 to 2026-04-18. Interviewed hospital administrator and reviewed billing. Cardiac surgery confirmed but billing shows inflated charges. Interviewed surgeon Dr. Kumar who confirmed surgery but expressed surprise at total bill amount.",
                "findings": "1. Patient admission and surgery confirmed. 2. Cardiac bypass surgery performed by Dr. Kumar (verified credentials). 3. Billing analysis reveals 35% markup compared to standard rates. 4. Several unnecessary charges included. 5. Medication charges inflated. 6. Hospital unable to justify pricing discrepancy.",
                "suspicion_indicators": "Significantly inflated hospital charges. Unexplained premium pricing. Possible collaboration between hospital billing and patient.",
                "conclusion": "Treatment verified but billing appears manipulated to claim higher amount. Recommend partial approval based on market rate pricing.",
                "outcome": "suspicious",
                "recommendation": "further_investigation"
            }
        },
        
        # CLOSED CASE (1)
        {
            "case_num": 14,
            "status": "closed",
            "category": "Legal / Court Verification",
            "subcategory": "Civil Case Lookup",
            "claim_number": "CLM100014",
            "policy_number": "POL500014",
            "insured_name": "Ramasamy Pillay",
            "services": ["Workplace Visit", "Document Pickup / Delivery"],
            "assessor_notes": "Verify if insured has any pending civil cases. Check court records for any litigation history.",
            "due_days": 14,
            "assigned_days_ago": 30,
            "started_days_ago": 29,
            "submitted_days_ago": 25,
            "completed_days_ago": 23,
            "closed_days_ago": 22,
            "evidence": [
                {"type": "application/pdf", "name": "court_records_search.pdf", "service": "Workplace Visit", "geo": False},
                {"type": "application/pdf", "name": "legal_clearance_certificate.pdf", "service": "Document Pickup / Delivery", "geo": False}
            ],
            "service_statuses": {"Workplace Visit": "completed", "Document Pickup / Delivery": "completed"},
            "findings": {
                "summary": "Legal verification completed. No civil cases found against insured.",
                "observations": "Conducted comprehensive court records search at High Court and Magistrate Court. Searched for name: Ramasamy Pillay, IC: XXXXXXXX-XX-XXXX. No pending or past civil cases found. Obtained legal clearance certificate.",
                "findings": "1. No civil cases registered. 2. No litigation history found. 3. Clean legal record. 4. No bankruptcy proceedings. 5. No court judgments against insured.",
                "suspicion_indicators": None,
                "conclusion": "Legal verification successful. Insured has clean legal record with no civil cases.",
                "outcome": "genuine",
                "recommendation": "approve"
            }
        },
        
        # CANCELLED CASE (1)
        {
            "case_num": 15,
            "status": "cancelled",
            "category": "Death Verification",
            "subcategory": "Police Report",
            "claim_number": "CLM100015",
            "policy_number": "POL500015",
            "insured_name": "Abdullah Rahman",
            "services": ["Hospital Visit", "Document Pickup / Delivery"],
            "assessor_notes": "Verify death through police report. Obtain copy of police report from Dang Wangi station.",
            "due_days": 10,
            "assigned_days_ago": 20,
            "cancelled_days_ago": 18,
            "cancellation_reason": "Investigation no longer required. Family provided complete documentation directly to assessor. Police report and death certificate verified by assessor office.",
            "evidence": [],
            "findings": None
        }
    ]
    
    print("Creating 15 detailed investigation cases...\n")
    
    # Create each case
    case_counter = await db.investigations.count_documents({})
    
    for tc in test_cases:
        case_num = case_counter + tc["case_num"]
        investigation_id = f"INV{str(case_num).zfill(6)}"
        
        # Get category and subcategory
        category = get_category_by_name(tc["category"])
        if not category:
            print(f"⚠️  Category '{tc['category']}' not found, skipping case {tc['case_num']}")
            continue
        
        category_id = str(category["_id"])
        subcategory = get_subcategory_by_name(category_id, tc["subcategory"])
        if not subcategory:
            print(f"⚠️  Subcategory '{tc['subcategory']}' not found, skipping case {tc['case_num']}")
            continue
        
        subcategory_id = str(subcategory["_id"])
        
        # Build services
        services = []
        for svc_name in tc["services"]:
            svc = get_service_by_name(svc_name)
            if svc:
                service_status = tc.get("service_statuses", {}).get(svc_name, "pending")
                services.append({
                    "id": str(uuid.uuid4()),
                    "service_category_id": str(svc["_id"]),
                    "service_name": svc_name,
                    "remarks": tc.get("assessor_notes", ""),
                    "status": service_status,
                    "evidence_count": len([e for e in tc.get("evidence", []) if e.get("service") == svc_name]),
                    "completed_at": (base_date + timedelta(days=tc.get("started_days_ago", 0) + 1)).isoformat() if service_status == "completed" else None
                })
        
        # Dates
        assigned_date = base_date + timedelta(days=30 - tc["assigned_days_ago"])
        due_date = assigned_date + timedelta(days=tc["due_days"])
        
        # Create case document
        case_doc = {
            "investigation_id": investigation_id,
            "claim_number": tc["claim_number"],
            "policy_number": tc["policy_number"],
            "insured_name": tc["insured_name"],
            "category_id": category_id,
            "sub_category_id": subcategory_id,
            "assigned_investigator_id": investigator_id,
            "assessor_id": assessor_id,
            "assessor_notes": tc["assessor_notes"],
            "status": tc["status"],
            "services": services,
            "due_date": due_date.isoformat(),
            "assigned_date": assigned_date.isoformat(),
            "created_at": assigned_date.isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Add findings if case is submitted/completed/closed
        if tc.get("findings"):
            submitted_date = base_date + timedelta(days=30 - tc.get("submitted_days_ago", 0))
            case_doc["findings"] = {
                **tc["findings"],
                "submitted_by": investigator_id,
                "submitted_by_name": investigator_name,
                "submitted_at": submitted_date.isoformat()
            }
        
        # Add rework history if rework requested
        if tc.get("rework"):
            rework_date = base_date + timedelta(days=30 - tc.get("rework_requested_days_ago", 0))
            case_doc["rework_history"] = [{
                "id": str(uuid.uuid4()),
                "reason": tc["rework"]["reason"],
                "additional_instructions": tc["rework"]["instructions"],
                "expected_deliverables": tc["rework"]["deliverables"],
                "requested_by": assessor_id,
                "requested_by_name": assessor_name,
                "requested_at": rework_date.isoformat()
            }]
        
        # Add cancellation reason
        if tc["status"] == "cancelled":
            case_doc["cancellation_reason"] = tc["cancellation_reason"]
            case_doc["cancelled_at"] = (base_date + timedelta(days=30 - tc.get("cancelled_days_ago", 0))).isoformat()
        
        # Insert investigation
        await db.investigations.insert_one(case_doc)
        
        # Create evidence entries
        for ev in tc.get("evidence", []):
            evidence_doc = {
                "id": str(uuid.uuid4()),
                "investigation_id": investigation_id,
                "service_id": next((s["id"] for s in services if s["service_name"] == ev["service"]), None),
                "storage_path": f"investigation-portal/evidence/{investigation_id}/{uuid.uuid4()}.{ev['name'].split('.')[-1]}",
                "original_filename": ev["name"],
                "content_type": ev["type"],
                "size": 1024000,  # 1MB mock size
                "latitude": 3.1390 if ev.get("geo") else None,
                "longitude": 101.6869 if ev.get("geo") else None,
                "notes": f"Evidence for {ev['service']}",
                "uploaded_by": investigator_id,
                "uploaded_by_name": investigator_name,
                "is_deleted": False,
                "created_at": (assigned_date + timedelta(days=tc.get("started_days_ago", 0) + 0.5)).isoformat()
            }
            await db.evidence.insert_one(evidence_doc)
        
        # Create activity timeline
        activities = [
            {
                "investigation_id": investigation_id,
                "user_id": assessor_id,
                "user_name": assessor_name,
                "action": "case_assigned",
                "description": f"Investigation case assigned to {investigator_name}",
                "timestamp": assigned_date.isoformat()
            }
        ]
        
        if tc.get("started_days_ago") is not None:
            started_date = base_date + timedelta(days=30 - tc["started_days_ago"])
            activities.append({
                "investigation_id": investigation_id,
                "user_id": investigator_id,
                "user_name": investigator_name,
                "action": "status_changed",
                "description": "Status changed to in_progress",
                "timestamp": started_date.isoformat()
            })
            
            activities.append({
                "investigation_id": investigation_id,
                "user_id": investigator_id,
                "user_name": investigator_name,
                "action": "case_opened",
                "description": "Investigator opened case and started investigation",
                "timestamp": started_date.isoformat()
            })
        
        if tc.get("evidence"):
            for i, ev in enumerate(tc["evidence"]):
                upload_date = assigned_date + timedelta(days=tc.get("started_days_ago", 0) + 0.5 + (i * 0.1))
                activities.append({
                    "investigation_id": investigation_id,
                    "user_id": investigator_id,
                    "user_name": investigator_name,
                    "action": "evidence_uploaded",
                    "description": f"Evidence file '{ev['name']}' uploaded",
                    "timestamp": upload_date.isoformat()
                })
        
        if tc.get("submitted_days_ago") is not None:
            submitted_date = base_date + timedelta(days=30 - tc["submitted_days_ago"])
            activities.append({
                "investigation_id": investigation_id,
                "user_id": investigator_id,
                "user_name": investigator_name,
                "action": "findings_submitted",
                "description": "Investigation findings submitted",
                "timestamp": submitted_date.isoformat()
            })
        
        if tc.get("rework_requested_days_ago") is not None:
            rework_date = base_date + timedelta(days=30 - tc["rework_requested_days_ago"])
            activities.append({
                "investigation_id": investigation_id,
                "user_id": assessor_id,
                "user_name": assessor_name,
                "action": "rework_requested",
                "description": f"Rework requested: {tc['rework']['reason']}",
                "timestamp": rework_date.isoformat()
            })
        
        if tc.get("completed_days_ago") is not None:
            completed_date = base_date + timedelta(days=30 - tc["completed_days_ago"])
            activities.append({
                "investigation_id": investigation_id,
                "user_id": assessor_id,
                "user_name": assessor_name,
                "action": "case_completed",
                "description": "Investigation case marked as completed by assessor",
                "timestamp": completed_date.isoformat()
            })
        
        if tc.get("closed_days_ago") is not None:
            closed_date = base_date + timedelta(days=30 - tc["closed_days_ago"])
            activities.append({
                "investigation_id": investigation_id,
                "user_id": assessor_id,
                "user_name": assessor_name,
                "action": "case_closed",
                "description": "Investigation case closed",
                "timestamp": closed_date.isoformat()
            })
        
        if tc["status"] == "cancelled":
            cancelled_date = base_date + timedelta(days=30 - tc.get("cancelled_days_ago", 0))
            activities.append({
                "investigation_id": investigation_id,
                "user_id": assessor_id,
                "user_name": assessor_name,
                "action": "case_cancelled",
                "description": f"Investigation cancelled: {tc['cancellation_reason']}",
                "timestamp": cancelled_date.isoformat()
            })
        
        await db.activities.insert_many(activities)
        
        # Create notification
        notif_type = {
            "assigned": "case_assignment",
            "rework_requested": "rework_request",
            "completed": "case_completion",
            "closed": "case_closure"
        }.get(tc["status"], "case_assignment")
        
        await db.notifications.insert_one({
            "user_id": investigator_id,
            "investigation_id": investigation_id,
            "type": notif_type,
            "message": f"Investigation {investigation_id} - {tc['claim_number']}: {tc['status'].replace('_', ' ').title()}",
            "is_read": tc["status"] not in ["assigned", "rework_requested"],
            "created_at": assigned_date.isoformat()
        })
        
        status_emoji = {
            "assigned": "🆕",
            "in_progress": "⏳",
            "submitted": "✅",
            "rework_requested": "🔄",
            "completed": "✔️",
            "closed": "🔒",
            "cancelled": "❌"
        }
        
        print(f"{status_emoji.get(tc['status'], '•')} Case {tc['case_num']:2d}: {investigation_id} - {tc['category']:30s} [{tc['status']:20s}] - {len(tc.get('evidence', []))} evidence")
    
    print(f"\n{'='*70}")
    print("✅ DEMO DATA SEEDING COMPLETE")
    print(f"{'='*70}")
    print(f"\nInvestigator Account: {investigator['email']}")
    print(f"Password: Investigator@123")
    print(f"\nTotal Cases Created: 15")
    print(f"  - Assigned: 3")
    print(f"  - In Progress: 3")
    print(f"  - Submitted: 2")
    print(f"  - Rework Requested: 2")
    print(f"  - Completed: 3")
    print(f"  - Closed: 1")
    print(f"  - Cancelled: 1")
    print(f"\nAll cases include:")
    print(f"  ✓ Complete activity timelines")
    print(f"  ✓ Realistic evidence files")
    print(f"  ✓ Service tracking")
    print(f"  ✓ Findings (where applicable)")
    print(f"  ✓ Rework history (where applicable)")
    print(f"  ✓ Notifications")
    print(f"\nThe investigator can now:")
    print(f"  1. Login to Investigation Portal")
    print(f"  2. View all 15 cases on dashboard")
    print(f"  3. Test complete investigation workflow")
    print(f"  4. Upload evidence for assigned/in-progress cases")
    print(f"  5. Submit findings")
    print(f"  6. Review rework requests")
    print(f"  7. View complete audit trail")
    print(f"\n{'='*70}\n")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_investigator_demo_data())
