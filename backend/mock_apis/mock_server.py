from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid

app = FastAPI(
    title="MetaMorphoSys Claims Platform - Mock APIs",
    description="Mock API server for testing Investigation Portal integration",
    version="1.0.0"
)

# ===== MOCK DATA =====

MOCK_CLAIMS = {
    "CLM0001288": {
        "claim_id": "claim-uuid-001",
        "claim_number": "CLM0001288",
        "claim_type": "Death Claim",
        "claim_status": "Under Investigation",
        "date_of_event": "2026-04-15",
        "date_of_notification": "2026-04-20",
        "date_registered": "2026-04-21",
        "claim_amount": 400000.00,
        "currency": "SGD",
        "policy_number": "DIOP00000002",
        "policy_type": "Universal Life",
        "sum_assured": 400000.00,
        "insured_name": "John Smith",
        "insured_nric": "S1234567A",
        "insured_dob": "1985-05-15",
        "insured_phone": "+65-9123-4567",
        "insured_email": "john.smith@email.com",
        "assessor_name": "Jane Assessor",
        "assessor_email": "jane.assessor@metamorphosys.com"
    },
    "CLM774904": {
        "claim_id": "claim-uuid-002",
        "claim_number": "CLM774904",
        "claim_type": "Hospital Claim",
        "claim_status": "Under Investigation",
        "date_of_event": "2026-05-10",
        "date_of_notification": "2026-05-15",
        "claim_amount": 50000.00,
        "currency": "SGD",
        "policy_number": "POL8815441",
        "insured_name": "Sam Johnson",
        "assessor_name": "Jane Assessor",
        "assessor_email": "jane.assessor@metamorphosys.com"
    }
}

MOCK_INVESTIGATORS = [
    {
        "investigator_id": "inv-001",
        "name": "John Investigator",
        "email": "john@investigations.com",
        "phone": "+65-9123-4567",
        "agency_id": "agency-001",
        "agency_name": "ABC Investigation Services",
        "specializations": ["Death Verification", "Hospital Verification"],
        "status": "active",
        "rating": 4.8,
        "cases_completed": 145
    },
    {
        "investigator_id": "inv-002",
        "name": "Sarah Chen",
        "email": "sarah@investigations.com",
        "phone": "+65-9234-5678",
        "agency_id": "agency-001",
        "agency_name": "ABC Investigation Services",
        "specializations": ["Address Verification", "Identity Verification"],
        "status": "active",
        "rating": 4.9,
        "cases_completed": 178
    }
]

# Store for received data
RECEIVED_INVESTIGATIONS = []
RECEIVED_STATUS_UPDATES = []
RECEIVED_FINDINGS = []

# ===== AUTHENTICATION =====

def verify_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    return True

# ===== ENDPOINTS =====

@app.get("/")
def root():
    return {
        "service": "MetaMorphoSys Claims Platform Mock API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "claims": "/api/integrations/claims/{claim_number}",
            "investigators": "/api/integrations/investigators/search",
            "auth": "/api/integrations/auth/token",
            "receive_investigation": "/api/integrations/investigations/receive",
            "receive_status": "/api/integrations/investigations/{id}/status/receive",
            "receive_findings": "/api/integrations/investigations/{id}/findings/receive"
        }
    }

# ===== CLAIM APIS =====

@app.get("/api/integrations/claims/{claim_number}")
def get_claim(claim_number: str, authorized: bool = Depends(verify_token)):
    """Get claim details by claim number"""
    if claim_number not in MOCK_CLAIMS:
        raise HTTPException(status_code=404, detail=f"Claim {claim_number} not found")
    
    claim_data = MOCK_CLAIMS[claim_number]
    
    return {
        "success": True,
        "data": {
            "claim": {
                "claim_id": claim_data["claim_id"],
                "claim_number": claim_data["claim_number"],
                "claim_type": claim_data["claim_type"],
                "claim_status": claim_data["claim_status"],
                "date_of_event": claim_data["date_of_event"],
                "date_of_notification": claim_data["date_of_notification"],
                "claim_amount": {
                    "requested": claim_data["claim_amount"],
                    "currency": claim_data["currency"]
                },
                "description": f"{claim_data['claim_type']} for policy holder"
            },
            "policy": {
                "policy_number": claim_data["policy_number"],
                "policy_type": claim_data.get("policy_type", "Life Insurance"),
                "sum_assured": claim_data.get("sum_assured", claim_data["claim_amount"]),
                "currency": claim_data["currency"],
                "policy_status": "Active"
            },
            "insured": {
                "insured_name": claim_data["insured_name"],
                "nric": claim_data.get("insured_nric", "N/A"),
                "date_of_birth": claim_data.get("insured_dob", "1985-01-01"),
                "contact": {
                    "phone": claim_data.get("insured_phone", "+65-9000-0000"),
                    "email": claim_data.get("insured_email", "insured@email.com")
                }
            },
            "assessor": {
                "assessor_name": claim_data["assessor_name"],
                "assessor_email": claim_data["assessor_email"]
            }
        }
    }

@app.get("/api/integrations/claims/{claim_number}/documents")
def get_claim_documents(claim_number: str, authorized: bool = Depends(verify_token)):
    """Get documents associated with a claim"""
    if claim_number not in MOCK_CLAIMS:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    return {
        "success": True,
        "data": {
            "documents": [
                {
                    "document_id": f"doc-{uuid.uuid4()}",
                    "document_name": "death_certificate.pdf",
                    "document_type": "death_certificate",
                    "category": "supporting_documents",
                    "size_bytes": 524288,
                    "uploaded_date": "2026-04-20T10:30:00Z",
                    "uploaded_by": "Jane Assessor",
                    "download_url": f"https://claims-platform.com/api/documents/download/doc-001"
                },
                {
                    "document_id": f"doc-{uuid.uuid4()}",
                    "document_name": "medical_report.pdf",
                    "document_type": "medical_report",
                    "category": "supporting_documents",
                    "size_bytes": 1048576,
                    "uploaded_date": "2026-04-21T14:20:00Z",
                    "uploaded_by": "Jane Assessor",
                    "download_url": f"https://claims-platform.com/api/documents/download/doc-002"
                }
            ],
            "total": 2
        }
    }

# ===== INVESTIGATOR APIS =====

@app.get("/api/integrations/investigators/search")
def search_investigators(
    agency_id: Optional[str] = None,
    specialization: Optional[str] = None,
    location: Optional[str] = None,
    authorized: bool = Depends(verify_token)
):
    """Search for available investigators"""
    filtered = MOCK_INVESTIGATORS.copy()
    
    if agency_id:
        filtered = [inv for inv in filtered if inv["agency_id"] == agency_id]
    
    if specialization:
        filtered = [inv for inv in filtered if specialization in inv["specializations"]]
    
    return {
        "success": True,
        "data": {
            "investigators": filtered,
            "total": len(filtered)
        }
    }

@app.get("/api/integrations/investigators/{investigator_id}")
def get_investigator(investigator_id: str, authorized: bool = Depends(verify_token)):
    """Get investigator details"""
    investigator = next((inv for inv in MOCK_INVESTIGATORS if inv["investigator_id"] == investigator_id), None)
    
    if not investigator:
        raise HTTPException(status_code=404, detail="Investigator not found")
    
    return {
        "success": True,
        "data": investigator
    }

# ===== INVESTIGATION RECEIVE APIS =====

@app.post("/api/integrations/investigations/receive")
def receive_investigation(payload: Dict[Any, Any], authorized: bool = Depends(verify_token)):
    """
    Receive investigation creation request from Investigation Portal
    This simulates the Claims Platform receiving the request
    """
    investigation_id = f"INV{str(len(RECEIVED_INVESTIGATIONS) + 1).zfill(6)}"
    
    RECEIVED_INVESTIGATIONS.append({
        "investigation_id": investigation_id,
        "payload": payload,
        "received_at": datetime.now(timezone.utc).isoformat()
    })
    
    print(f"\n✅ Investigation Received:")
    print(f"   ID: {investigation_id}")
    print(f"   Claim: {payload.get('external_reference', {}).get('claim_number')}")
    print(f"   Category: {payload.get('investigation_request', {}).get('category_name')}")
    print(f"   Assigned to: {payload.get('investigation_request', {}).get('assigned_investigator_email')}")
    
    return {
        "success": True,
        "data": {
            "investigation_id": investigation_id,
            "status": "assigned",
            "assigned_date": datetime.now(timezone.utc).isoformat(),
            "portal_url": f"https://investigations.metamorphosys.com/investigations/{investigation_id}"
        },
        "message": "Investigation case created successfully"
    }

@app.post("/api/integrations/investigations/{investigation_id}/status/receive")
def receive_status_update(investigation_id: str, payload: Dict[Any, Any], authorized: bool = Depends(verify_token)):
    """Receive status update from Investigation Portal"""
    RECEIVED_STATUS_UPDATES.append({
        "investigation_id": investigation_id,
        "payload": payload,
        "received_at": datetime.now(timezone.utc).isoformat()
    })
    
    print(f"\n✅ Status Update Received:")
    print(f"   Investigation: {investigation_id}")
    print(f"   Old Status: {payload.get('old_status')}")
    print(f"   New Status: {payload.get('new_status')}")
    print(f"   Changed By: {payload.get('status_changed_by', {}).get('user_name')}")
    
    return {
        "success": True,
        "message": "Status updated successfully in claims platform",
        "claim_number": payload.get("external_reference", {}).get("claim_number"),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

@app.post("/api/integrations/investigations/{investigation_id}/findings/receive")
def receive_findings(investigation_id: str, payload: Dict[Any, Any], authorized: bool = Depends(verify_token)):
    """Receive investigation findings from Investigation Portal"""
    findings = payload.get("findings", {})
    
    RECEIVED_FINDINGS.append({
        "investigation_id": investigation_id,
        "payload": payload,
        "received_at": datetime.now(timezone.utc).isoformat()
    })
    
    print(f"\n✅ Findings Received:")
    print(f"   Investigation: {investigation_id}")
    print(f"   Outcome: {findings.get('outcome')}")
    print(f"   Recommendation: {findings.get('recommendation')}")
    print(f"   Submitted By: {payload.get('submitted_by', {}).get('investigator_name')}")
    
    # Determine new claim status based on recommendation
    recommendation = findings.get("recommendation", "further_investigation")
    status_map = {
        "approve": "Investigation Complete - Approved",
        "reject": "Investigation Complete - Rejected",
        "further_investigation": "Investigation Complete - Pending Review"
    }
    new_claim_status = status_map.get(recommendation, "Investigation Complete - Pending Review")
    
    return {
        "success": True,
        "message": "Investigation findings received successfully",
        "claim_number": payload.get("external_reference", {}).get("claim_number"),
        "status_updated_to": new_claim_status,
        "next_action": "Assessor review required",
        "findings_id": f"findings-{uuid.uuid4()}"
    }

# ===== WEBHOOK ENDPOINTS =====

@app.post("/webhooks/investigation-status")
def webhook_status_changed(payload: Dict[Any, Any]):
    """Webhook for status changes"""
    print(f"\n🔔 Webhook: investigation.status_changed")
    print(f"   Investigation: {payload.get('data', {}).get('investigation_id')}")
    print(f"   New Status: {payload.get('data', {}).get('new_status')}")
    
    return {"success": True, "message": "Webhook received"}

@app.post("/webhooks/investigation-findings")
def webhook_findings_submitted(payload: Dict[Any, Any]):
    """Webhook for findings submission"""
    print(f"\n🔔 Webhook: investigation.findings_submitted")
    print(f"   Investigation: {payload.get('data', {}).get('investigation_id')}")
    print(f"   Outcome: {payload.get('data', {}).get('outcome')}")
    
    return {"success": True, "message": "Webhook received"}

# ===== AUTHENTICATION =====

@app.post("/api/integrations/auth/token")
def get_token(payload: Dict[Any, Any]):
    """Mock authentication endpoint"""
    return {
        "access_token": "mock_jwt_token_for_testing_12345",
        "token_type": "Bearer",
        "expires_in": 3600,
        "scope": "investigations.* claims.read documents.read"
    }

# ===== DEBUG ENDPOINTS =====

@app.get("/debug/received-investigations")
def debug_investigations():
    """View all received investigations"""
    return {
        "total": len(RECEIVED_INVESTIGATIONS),
        "investigations": RECEIVED_INVESTIGATIONS
    }

@app.get("/debug/received-status-updates")
def debug_status_updates():
    """View all received status updates"""
    return {
        "total": len(RECEIVED_STATUS_UPDATES),
        "updates": RECEIVED_STATUS_UPDATES
    }

@app.get("/debug/received-findings")
def debug_findings():
    """View all received findings"""
    return {
        "total": len(RECEIVED_FINDINGS),
        "findings": RECEIVED_FINDINGS
    }

@app.post("/debug/reset")
def debug_reset():
    """Reset all received data"""
    global RECEIVED_INVESTIGATIONS, RECEIVED_STATUS_UPDATES, RECEIVED_FINDINGS
    RECEIVED_INVESTIGATIONS = []
    RECEIVED_STATUS_UPDATES = []
    RECEIVED_FINDINGS = []
    return {"message": "All data reset"}

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("MetaMorphoSys Claims Platform - Mock API Server")
    print("="*60)
    print("\nStarting server on http://localhost:8002")
    print("\nAvailable endpoints:")
    print("  GET  /                                          - API info")
    print("  GET  /api/integrations/claims/{claim_number}   - Get claim")
    print("  GET  /api/integrations/investigators/search    - Search investigators")
    print("  POST /api/integrations/investigations/receive  - Receive investigation")
    print("  POST /api/integrations/auth/token             - Get auth token")
    print("\nDebug endpoints:")
    print("  GET  /debug/received-investigations            - View received data")
    print("  POST /debug/reset                              - Reset data")
    print("\n" + "="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8002)
