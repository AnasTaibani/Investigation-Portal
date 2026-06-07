# API Gap Analysis & Mock APIs
## Investigation Portal - MetaMorphoSys Integration

**Version:** 1.0  
**Date:** June 3, 2026

---

## API Gap Analysis

### Summary

| Category | Required APIs | Assumed Available | Assumed Missing | Priority |
|----------|---------------|-------------------|-----------------|----------|
| Investigation Management | 6 | 0 | 6 | P0 |
| Claim Data | 4 | 2 | 2 | P0 |
| User Management | 3 | 1 | 2 | P1 |
| Document Management | 4 | 1 | 3 | P1 |
| Notifications | 3 | 0 | 3 | P1 |
| **TOTAL** | **20** | **4** | **16** | - |

---

## Detailed Gap Analysis

### 1. Investigation Management APIs

| API | Status | Workaround | Priority | Notes |
|-----|--------|------------|----------|-------|
| POST /investigations | ❌ Missing | Manual entry in portal | P0 | **CRITICAL** - Core integration |
| GET /investigations/{id} | ❌ Missing | Portal is source of truth | P0 | Needed for Claims Platform view |
| PUT /investigations/{id}/status | ❌ Missing | Email notifications | P0 | Real-time status sync required |
| POST /investigations/{id}/findings | ❌ Missing | Email with PDF report | P0 | **CRITICAL** - Decision making |
| POST /investigations/{id}/rework | ❌ Missing | Manual investigator contact | P0 | Workflow blocker |
| GET /investigations/{id}/timeline | ❌ Missing | Manual updates | P1 | Nice to have for audit |

**Recommendation:** Build all P0 APIs in Phase 1 (2-3 weeks)

---

### 2. Claim Data APIs

| API | Status | Workaround | Priority | Notes |
|-----|--------|------------|----------|-------|
| GET /claims/{claim_number} | ⚠️ Assumed Available | Manual data entry | P0 | **Verify with MetaMorphoSys** |
| GET /claims/{id}/policy | ⚠️ Assumed Available | Combined in claim API | P1 | May be part of claim response |
| GET /claims/{id}/insured | ❌ Missing | Manual entry | P1 | PII considerations |
| GET /claims/{id}/history | ❌ Missing | Not available | P2 | Low priority |

**Recommendation:** Verify existing APIs, build missing P1 APIs in Phase 2

---

### 3. User Management APIs

| API | Status | Workaround | Priority | Notes |
|-----|--------|------------|----------|-------|
| GET /investigators/search | ❌ Missing | Portal maintains own list | P1 | Sync required |
| GET /investigators/{id} | ⚠️ Assumed Available | Basic user API | P1 | May exist in HR system |
| POST /investigators/sync | ❌ Missing | Manual updates | P2 | Batch sync acceptable |

**Recommendation:** Build search API for assessor convenience

---

### 4. Document Management APIs

| API | Status | Workaround | Priority | Notes |
|-----|--------|------------|----------|-------|
| GET /claims/{id}/documents | ❌ Missing | Email attachments | P1 | Improves investigator efficiency |
| GET /documents/{id}/download | ⚠️ Assumed Available | Generic file endpoint | P1 | Verify authentication |
| POST /documents/upload | ❌ Missing | Portal stores evidence | P0 | **CRITICAL** for evidence |
| GET /documents/{id}/preview | ❌ Missing | Download only | P2 | UX enhancement |

**Recommendation:** Implement evidence upload API in Phase 1

---

### 5. Notification & Webhook APIs

| API | Status | Workaround | Priority | Notes |
|-----|--------|------------|----------|-------|
| POST /webhooks/investigation-status | ❌ Missing | Polling every 5 min | P1 | Performance concern |
| POST /webhooks/findings-submitted | ❌ Missing | Email notification | P0 | **CRITICAL** for workflow |
| GET /notifications | ❌ Missing | Email only | P2 | UX enhancement |

**Recommendation:** Build webhook infrastructure for event-driven architecture

---

## Priority Matrix

```
High Impact, High Priority (P0) - Build Immediately
┌─────────────────────────────────────────────────┐
│ • POST /investigations (Create)                 │
│ • POST /investigations/{id}/findings            │
│ • POST /investigations/{id}/rework              │
│ • PUT /investigations/{id}/status               │
│ • POST /documents/upload (Evidence)             │
│ • Webhook: findings_submitted                   │
└─────────────────────────────────────────────────┘

Medium Impact, High Priority (P1) - Build in Phase 2
┌─────────────────────────────────────────────────┐
│ • GET /claims/{claim_number}                    │
│ • GET /investigators/search                     │
│ • GET /claims/{id}/documents                    │
│ • Webhook: status_changed                       │
└─────────────────────────────────────────────────┘

Low Priority (P2) - Build Later
┌─────────────────────────────────────────────────┐
│ • GET /investigations/{id}/timeline             │
│ • GET /documents/{id}/preview                   │
│ • POST /investigators/sync                      │
└─────────────────────────────────────────────────┘
```

---

## Mock APIs for Testing

### Setup Instructions

1. **Create Mock Server**
```bash
cd /app/backend
mkdir mock_apis
cd mock_apis
```

2. **Install Mock Server**
```bash
pip install fastapi uvicorn
```

3. **Run Mock Server**
```bash
uvicorn mock_server:app --host 0.0.0.0 --port 8002
```

---

### Mock API Implementation

```python
# /app/backend/mock_apis/mock_server.py
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid

app = FastAPI(title="MetaMorphoSys Claims Platform - Mock APIs")

# ===== MODELS =====

class ClaimResponse(BaseModel):
    claim_id: str
    claim_number: str
    claim_type: str
    claim_status: str
    date_of_event: str
    date_of_notification: str
    claim_amount: float
    currency: str
    policy_number: str
    insured_name: str
    
class InvestigationCreateResponse(BaseModel):
    success: bool
    investigation_id: str
    message: str

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
        "status": "active"
    }
]

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
        "status": "running"
    }

# 1. Get Claim Details
@app.get("/api/integrations/claims/{claim_number}")
def get_claim(claim_number: str, authorized: bool = Depends(verify_token)):
    if claim_number not in MOCK_CLAIMS:
        raise HTTPException(status_code=404, detail="Claim not found")
    
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
                }
            },
            "policy": {
                "policy_number": claim_data["policy_number"],
                "policy_type": claim_data["policy_type"],
                "sum_assured": claim_data["sum_assured"],
                "currency": claim_data["currency"]
            },
            "insured": {
                "insured_name": claim_data["insured_name"],
                "nric": claim_data["insured_nric"],
                "date_of_birth": claim_data["insured_dob"],
                "contact": {
                    "phone": claim_data["insured_phone"],
                    "email": claim_data["insured_email"]
                }
            },
            "assessor": {
                "assessor_name": claim_data["assessor_name"],
                "assessor_email": claim_data["assessor_email"]
            }
        }
    }

# 2. Create Investigation (Receive from Claims Platform)
@app.post("/api/integrations/investigations/receive")
def receive_investigation(payload: Dict[Any, Any], authorized: bool = Depends(verify_token)):
    """
    Mock endpoint to simulate Claims Platform calling Investigation Portal
    """
    investigation_id = f"INV{str(uuid.uuid4())[:6].upper()}"
    
    print(f"✅ Received investigation creation request:")
    print(f"   - Claim: {payload.get('external_reference', {}).get('claim_number')}")
    print(f"   - Category: {payload.get('investigation_request', {}).get('category_name')}")
    print(f"   - Assigned to: {payload.get('investigation_request', {}).get('assigned_investigator_email')}")
    
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

# 3. Receive Investigation Status Update
@app.post("/api/integrations/investigations/{investigation_id}/status/receive")
def receive_status_update(investigation_id: str, payload: Dict[Any, Any], authorized: bool = Depends(verify_token)):
    """
    Mock endpoint to simulate Investigation Portal updating Claims Platform
    """
    print(f"✅ Received status update for {investigation_id}:")
    print(f"   - Old Status: {payload.get('old_status')}")
    print(f"   - New Status: {payload.get('new_status')}")
    print(f"   - Changed By: {payload.get('status_changed_by', {}).get('user_name')}")
    
    return {
        "success": True,
        "message": "Status updated successfully in claims platform",
        "claim_number": payload.get("external_reference", {}).get("claim_number"),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

# 4. Receive Investigation Findings
@app.post("/api/integrations/investigations/{investigation_id}/findings/receive")
def receive_findings(investigation_id: str, payload: Dict[Any, Any], authorized: bool = Depends(verify_token)):
    """
    Mock endpoint to simulate Investigation Portal submitting findings to Claims Platform
    """
    findings = payload.get("findings", {})
    
    print(f"✅ Received investigation findings for {investigation_id}:")
    print(f"   - Outcome: {findings.get('outcome')}")
    print(f"   - Recommendation: {findings.get('recommendation')}")
    print(f"   - Submitted By: {payload.get('submitted_by', {}).get('investigator_name')}")
    
    # Simulate claim status update based on findings
    if findings.get("recommendation") == "approve":
        new_claim_status = "Investigation Complete - Approved"
    elif findings.get("recommendation") == "reject":
        new_claim_status = "Investigation Complete - Rejected"
    else:
        new_claim_status = "Investigation Complete - Pending Review"
    
    return {
        "success": True,
        "message": "Investigation findings received successfully",
        "claim_number": payload.get("external_reference", {}).get("claim_number"),
        "status_updated_to": new_claim_status,
        "next_action": "Assessor review required",
        "findings_id": f"findings-{uuid.uuid4()}"
    }

# 5. Search Investigators
@app.get("/api/integrations/investigators/search")
def search_investigators(
    agency_id: Optional[str] = None,
    specialization: Optional[str] = None,
    authorized: bool = Depends(verify_token)
):
    filtered = MOCK_INVESTIGATORS
    
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

# 6. Get Claim Documents
@app.get("/api/integrations/claims/{claim_number}/documents")
def get_claim_documents(claim_number: str, authorized: bool = Depends(verify_token)):
    return {
        "success": True,
        "data": {
            "documents": [
                {
                    "document_id": "doc-001",
                    "document_name": "death_certificate.pdf",
                    "document_type": "death_certificate",
                    "category": "supporting_documents",
                    "size_bytes": 524288,
                    "uploaded_date": "2026-04-20T10:30:00Z",
                    "uploaded_by": "Jane Assessor",
                    "download_url": "https://claims-platform.com/api/documents/doc-001/download"
                }
            ],
            "total": 1
        }
    }

# 7. Webhook: Investigation Status Changed
@app.post("/webhooks/investigation-status")
def webhook_status_changed(payload: Dict[Any, Any]):
    """
    This endpoint would be called by Investigation Portal when status changes
    """
    print(f"🔔 Webhook received: investigation.status_changed")
    print(f"   - Investigation ID: {payload.get('data', {}).get('investigation_id')}")
    print(f"   - New Status: {payload.get('data', {}).get('new_status')}")
    
    return {"success": True, "message": "Webhook received"}

# 8. Webhook: Findings Submitted
@app.post("/webhooks/investigation-findings")
def webhook_findings_submitted(payload: Dict[Any, Any]):
    """
    This endpoint would be called by Investigation Portal when findings are submitted
    """
    print(f"🔔 Webhook received: investigation.findings_submitted")
    print(f"   - Investigation ID: {payload.get('data', {}).get('investigation_id')}")
    print(f"   - Outcome: {payload.get('data', {}).get('outcome')}")
    
    return {"success": True, "message": "Webhook received"}

# Authentication endpoint for testing
@app.post("/api/integrations/auth/token")
def get_token(payload: Dict[Any, Any]):
    """
    Mock authentication endpoint
    Returns a fake JWT token for testing
    """
    return {
        "access_token": "mock_jwt_token_for_testing_12345",
        "token_type": "Bearer",
        "expires_in": 3600,
        "scope": "investigations.* claims.read"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
```

---

## Testing Guide

### 1. Start Mock Server

```bash
cd /app/backend/mock_apis
python3 mock_server.py
```

Server will run on: http://localhost:8002

### 2. Test Endpoints

#### Get Claim Data
```bash
curl -X GET "http://localhost:8002/api/integrations/claims/CLM0001288" \
  -H "Authorization: Bearer mock_token"
```

#### Simulate Investigation Creation
```bash
curl -X POST "http://localhost:8002/api/integrations/investigations/receive" \
  -H "Authorization: Bearer mock_token" \
  -H "Content-Type: application/json" \
  -d '{
    "external_reference": {
      "claim_number": "CLM0001288",
      "policy_number": "DIOP00000002"
    },
    "investigation_request": {
      "category_name": "Death Verification",
      "assigned_investigator_email": "john@investigations.com"
    }
  }'
```

#### Simulate Status Update
```bash
curl -X POST "http://localhost:8002/api/integrations/investigations/INV000251/status/receive" \
  -H "Authorization: Bearer mock_token" \
  -H "Content-Type: application/json" \
  -d '{
    "old_status": "assigned",
    "new_status": "in_progress",
    "status_changed_by": {
      "user_name": "John Investigator"
    },
    "external_reference": {
      "claim_number": "CLM0001288"
    }
  }'
```

---

## Integration Testing Checklist

### Phase 1: Mock API Testing

- [ ] Mock server running on port 8002
- [ ] Test authentication endpoint
- [ ] Test GET /claims/{claim_number}
- [ ] Test POST /investigations/receive
- [ ] Test POST /status/receive
- [ ] Test POST /findings/receive
- [ ] Test GET /investigators/search
- [ ] Test webhook endpoints

### Phase 2: Integration with Investigation Portal

- [ ] Configure Investigation Portal to call mock APIs
- [ ] Test investigation creation flow
- [ ] Test claim data retrieval
- [ ] Test status update synchronization
- [ ] Test findings submission
- [ ] Test evidence upload
- [ ] Test rework request flow

### Phase 3: End-to-End Testing

- [ ] Create investigation from "Claims Platform" (mock)
- [ ] Investigator completes services
- [ ] Upload evidence with geo-tags
- [ ] Submit findings
- [ ] Verify findings received in mock
- [ ] Test rework request flow
- [ ] Verify all webhooks fired correctly

---

## Next Steps for MetaMorphoSys Integration

### Short Term (1-2 weeks)
1. **Validate API Specifications**
   - Review with MetaMorphoSys team
   - Adjust based on existing infrastructure
   - Finalize authentication approach

2. **Build Critical APIs (P0)**
   - POST /investigations
   - POST /findings
   - PUT /status
   - Webhook endpoints

3. **Integration Testing**
   - Use mock APIs
   - Test all workflows
   - Performance testing

### Medium Term (3-4 weeks)
4. **Build P1 APIs**
   - GET /claims/{claim_number}
   - GET /investigators/search
   - Document management APIs

5. **Production Deployment**
   - Deploy to staging environment
   - UAT with MetaMorphoSys team
   - Security audit

### Long Term (2-3 months)
6. **Enhancements**
   - Real-time notifications
   - Advanced analytics
   - Mobile app support

---

## Estimated Development Effort

| API Category | Complexity | Effort (Days) | Team |
|--------------|-----------|---------------|------|
| Investigation APIs | High | 10 | Backend + Integration |
| Claim Data APIs | Medium | 5 | Backend |
| User Management | Low | 3 | Backend |
| Document APIs | Medium | 5 | Backend + Storage |
| Webhooks | Medium | 4 | Backend + DevOps |
| Testing & QA | High | 7 | QA + Integration |
| **TOTAL** | - | **34 days** | Full Team |

**Recommended Team:**
- 2 Backend Developers
- 1 Integration Specialist
- 1 QA Engineer
- 1 DevOps Engineer

**Timeline:** 6-8 weeks for complete integration

---

**End of API Gap Analysis & Mock APIs Document**
