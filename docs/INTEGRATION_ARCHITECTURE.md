# Investigation Portal - Integration Architecture
## MetaMorphoSys Claims Platform Integration Specification

**Version:** 1.0  
**Date:** June 3, 2026  
**Status:** Requirements & Specification  
**Owner:** Investigation Portal Team

---

## Executive Summary

This document outlines the complete integration architecture required between the MetaMorphoSys Claims Platform and the Investigation Portal. The integration enables seamless bi-directional communication for investigation lifecycle management.

**Key Integration Points:** 10  
**Required APIs:** 24  
**Authentication:** JWT with Service Account  
**Communication Pattern:** REST APIs + Webhooks (Event-driven)

---

## Table of Contents

1. [Integration Overview](#integration-overview)
2. [Integration Points](#integration-points)
3. [API Specifications](#api-specifications)
4. [Authentication Strategy](#authentication-strategy)
5. [Data Synchronization](#data-synchronization)
6. [Event Flow Diagrams](#event-flow-diagrams)
7. [API Gap Analysis](#api-gap-analysis)
8. [Mock APIs](#mock-apis)
9. [Questions for MetaMorphoSys Team](#questions)

---

## Integration Overview

### Architecture Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│                    MetaMorphoSys Claims Platform                 │
│  ┌───────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │ Claims Inbox  │  │ Collaboration│  │ Investigation View │  │
│  │   Module      │  │    Module    │  │     Module         │  │
│  └───────┬───────┘  └──────┬───────┘  └────────┬───────────┘  │
│          │                  │                    │               │
└──────────┼──────────────────┼────────────────────┼───────────────┘
           │                  │                    │
           │   REST APIs      │    Webhooks        │
           ▼                  ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway / Integration Layer             │
│                   (Authentication, Rate Limiting, Logging)       │
└─────────────────────────────────────────────────────────────────┘
           │                  │                    │
           ▼                  ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Investigation Portal                        │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────┐  │
│  │  Dashboard   │  │ Investigations│  │  Evidence Manager   │  │
│  └──────────────┘  └──────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Communication Modes

1. **Synchronous (REST APIs)**
   - Investigation creation
   - Data retrieval
   - Status updates
   - Findings submission

2. **Asynchronous (Webhooks/Events)**
   - Status change notifications
   - Assignment notifications
   - Rework requests
   - Completion notifications

---

## Integration Points

### Integration Point 1: Investigation Creation ⭐ Critical
**Flow:** Claims Platform → Investigation Portal  
**Trigger:** Assessor creates investigation request via Collaboration module  
**Priority:** P0 (Must Have)

### Integration Point 2: Claim Information Retrieval ⭐ Critical
**Flow:** Investigation Portal → Claims Platform  
**Trigger:** Investigator opens investigation case  
**Priority:** P0 (Must Have)

### Integration Point 3: Investigator Directory
**Flow:** Claims Platform → Investigation Portal  
**Trigger:** Assessor selects investigator for assignment  
**Priority:** P0 (Must Have)

### Integration Point 4: Document Retrieval
**Flow:** Investigation Portal → Claims Platform  
**Trigger:** Investigator requests claim documents  
**Priority:** P1 (Should Have)

### Integration Point 5: Investigation Status Updates ⭐ Critical
**Flow:** Investigation Portal → Claims Platform  
**Trigger:** Investigator changes case status  
**Priority:** P0 (Must Have)

### Integration Point 6: Evidence Upload & Access
**Flow:** Bidirectional  
**Trigger:** Evidence uploaded by investigator  
**Priority:** P0 (Must Have)

### Integration Point 7: Investigation Findings Submission ⭐ Critical
**Flow:** Investigation Portal → Claims Platform  
**Trigger:** Investigator submits findings  
**Priority:** P0 (Must Have)

### Integration Point 8: Rework Request ⭐ Critical
**Flow:** Claims Platform → Investigation Portal  
**Trigger:** Assessor requests additional investigation  
**Priority:** P0 (Must Have)

### Integration Point 9: Investigation Timeline Sync
**Flow:** Bidirectional  
**Trigger:** Any activity on investigation  
**Priority:** P1 (Should Have)

### Integration Point 10: Notification System
**Flow:** Bidirectional  
**Trigger:** Key events in investigation lifecycle  
**Priority:** P1 (Should Have)

---

## API Specifications

### 1. Investigation Management APIs

#### 1.1 Create Investigation (Claims Platform → Investigation Portal)

**Endpoint:** `POST /api/integrations/investigations`

**Request Headers:**
```json
{
  "Authorization": "Bearer {JWT_TOKEN}",
  "X-Client-ID": "metamorphosys-claims-platform",
  "X-Request-ID": "unique-request-id",
  "Content-Type": "application/json"
}
```

**Request Body:**
```json
{
  "external_reference": {
    "claim_number": "CLM0001288",
    "claim_id": "uuid-of-claim",
    "policy_number": "DIOP00000002",
    "policy_id": "uuid-of-policy"
  },
  "insured_details": {
    "insured_name": "John Smith",
    "insured_id": "uuid-or-nric",
    "date_of_birth": "1985-05-15",
    "contact_number": "+65-9123-4567",
    "email": "john.smith@email.com",
    "address": {
      "street": "123 Main Street",
      "unit": "#05-10",
      "postal_code": "123456",
      "city": "Singapore",
      "country": "Singapore"
    }
  },
  "claim_details": {
    "claim_type": "Death Claim",
    "date_of_event": "2026-04-15",
    "date_of_notification": "2026-04-20",
    "claim_amount": 400000.00,
    "currency": "SGD",
    "current_status": "Under Investigation",
    "description": "Death claim for policy holder"
  },
  "investigation_request": {
    "category_id": "cat-001",
    "category_name": "Death Verification",
    "sub_category_id": "subcat-001",
    "sub_category_name": "Hospital Death Certificate",
    "priority": "high",
    "due_date": "2026-06-20",
    "assigned_investigator_id": "inv-001",
    "assigned_investigator_email": "investigator@agency.com",
    "agency_id": "agency-001",
    "assessor_id": "assessor-001",
    "assessor_name": "Jane Assessor",
    "assessor_email": "jane.assessor@metamorphosys.com",
    "assessor_notes": "Please verify hospital death certificate and interview attending physician. Suspicious timing of claim.",
    "special_instructions": "Handle with high priority. Potential fraud indicators."
  },
  "requested_services": [
    {
      "service_category_id": "svc-001",
      "service_name": "Hospital Visit",
      "service_code": "HOSP_VISIT",
      "remarks": "Visit National University Hospital and verify admission records",
      "priority": "high",
      "requires_geo_tag": true
    },
    {
      "service_category_id": "svc-002",
      "service_name": "Mobile Photo/Video Capture",
      "service_code": "PHOTO_VIDEO",
      "remarks": "Capture photos of death certificate and hospital records",
      "priority": "high",
      "requires_geo_tag": false
    },
    {
      "service_category_id": "svc-003",
      "service_name": "Report Drafting - Final",
      "service_code": "REPORT_FINAL",
      "remarks": "Comprehensive investigation report with findings",
      "priority": "medium",
      "requires_geo_tag": false
    }
  ],
  "attachments": [
    {
      "document_id": "doc-001",
      "document_name": "death_certificate.pdf",
      "document_type": "death_certificate",
      "document_url": "https://claims-platform.com/api/documents/doc-001",
      "uploaded_date": "2026-04-20T10:30:00Z",
      "uploaded_by": "Jane Assessor"
    }
  ],
  "metadata": {
    "created_by": "assessor-001",
    "created_at": "2026-06-03T10:00:00Z",
    "source_system": "claims-platform",
    "source_module": "collaboration",
    "workflow_id": "wf-001"
  }
}
```

**Response (Success):**
```json
{
  "success": true,
  "data": {
    "investigation_id": "INV000251",
    "external_reference": {
      "claim_number": "CLM0001288",
      "policy_number": "DIOP00000002"
    },
    "status": "assigned",
    "assigned_date": "2026-06-03T10:00:15Z",
    "due_date": "2026-06-20",
    "portal_url": "https://investigations.metamorphosys.com/investigations/INV000251",
    "assigned_investigator": {
      "id": "inv-001",
      "name": "John Investigator",
      "email": "investigator@agency.com"
    }
  },
  "message": "Investigation case created successfully",
  "request_id": "unique-request-id"
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid investigator ID",
    "details": {
      "field": "investigation_request.assigned_investigator_id",
      "reason": "Investigator not found in system"
    }
  },
  "request_id": "unique-request-id"
}
```

---

#### 1.2 Get Investigation Status (Claims Platform Query)

**Endpoint:** `GET /api/integrations/investigations/{investigation_id}`

**Request Headers:**
```json
{
  "Authorization": "Bearer {JWT_TOKEN}",
  "X-Client-ID": "metamorphosys-claims-platform"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "investigation_id": "INV000251",
    "external_reference": {
      "claim_number": "CLM0001288",
      "policy_number": "DIOP00000002"
    },
    "status": "in_progress",
    "assigned_investigator": {
      "id": "inv-001",
      "name": "John Investigator",
      "email": "investigator@agency.com",
      "phone": "+65-9123-4567"
    },
    "timeline": {
      "assigned_date": "2026-06-03T10:00:15Z",
      "started_date": "2026-06-03T14:30:00Z",
      "last_updated": "2026-06-04T09:15:00Z",
      "due_date": "2026-06-20"
    },
    "services": [
      {
        "service_id": "svc-uuid-001",
        "service_name": "Hospital Visit",
        "status": "completed",
        "completed_date": "2026-06-04T09:00:00Z",
        "evidence_count": 5
      },
      {
        "service_id": "svc-uuid-002",
        "service_name": "Mobile Photo/Video Capture",
        "status": "completed",
        "completed_date": "2026-06-04T09:15:00Z",
        "evidence_count": 8
      },
      {
        "service_id": "svc-uuid-003",
        "service_name": "Report Drafting - Final",
        "status": "in_progress",
        "evidence_count": 0
      }
    ],
    "progress_summary": {
      "total_services": 3,
      "completed_services": 2,
      "pending_services": 1,
      "progress_percentage": 67
    }
  }
}
```

---

#### 1.3 Update Investigation Status (Investigation Portal → Claims Platform)

**Endpoint:** `POST /api/integrations/investigations/{investigation_id}/status`

**Request Body:**
```json
{
  "investigation_id": "INV000251",
  "external_reference": {
    "claim_number": "CLM0001288"
  },
  "old_status": "assigned",
  "new_status": "in_progress",
  "status_changed_by": {
    "user_id": "inv-001",
    "user_name": "John Investigator",
    "user_email": "investigator@agency.com"
  },
  "status_changed_at": "2026-06-03T14:30:00Z",
  "remarks": "Started investigation, visited hospital",
  "metadata": {
    "source_system": "investigation-portal",
    "client_ip": "192.168.1.1"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Status updated successfully in claims platform",
  "claim_number": "CLM0001288",
  "updated_at": "2026-06-03T14:30:05Z"
}
```

---

### 2. Claim Information APIs

#### 2.1 Get Claim Details (Investigation Portal Query)

**Endpoint:** `GET /api/integrations/claims/{claim_number}`

**Request Headers:**
```json
{
  "Authorization": "Bearer {JWT_TOKEN}",
  "X-Client-ID": "investigation-portal"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "claim": {
      "claim_id": "claim-uuid-001",
      "claim_number": "CLM0001288",
      "claim_type": "Death Claim",
      "claim_status": "Under Investigation",
      "date_of_event": "2026-04-15",
      "date_of_notification": "2026-04-20",
      "date_registered": "2026-04-21",
      "claim_amount": {
        "requested": 400000.00,
        "approved": null,
        "currency": "SGD"
      },
      "description": "Death claim for policy holder"
    },
    "policy": {
      "policy_id": "policy-uuid-001",
      "policy_number": "DIOP00000002",
      "policy_type": "Universal Life",
      "policy_status": "Active",
      "sum_assured": 400000.00,
      "currency": "SGD",
      "policy_start_date": "2020-05-20",
      "policy_term": "5Y, 0M, 10D",
      "premium_frequency": "Annual"
    },
    "insured": {
      "insured_id": "insured-uuid-001",
      "insured_name": "John Smith",
      "nric": "S1234567A",
      "date_of_birth": "1985-05-15",
      "age": 41,
      "gender": "Male",
      "contact": {
        "phone": "+65-9123-4567",
        "email": "john.smith@email.com",
        "address": {
          "street": "123 Main Street",
          "unit": "#05-10",
          "postal_code": "123456",
          "city": "Singapore",
          "country": "Singapore"
        }
      }
    },
    "assessor": {
      "assessor_id": "assessor-001",
      "assessor_name": "Jane Assessor",
      "assessor_email": "jane.assessor@metamorphosys.com",
      "phone": "+65-6789-1234"
    },
    "investigation_context": {
      "reason_for_investigation": "Suspicious timing of claim notification",
      "red_flags": [
        "Claim notified 5 days after event",
        "Large sum assured",
        "Recent policy issuance (within 2 years)"
      ],
      "previous_claims": 0
    }
  }
}
```

---

### 3. Investigator Directory APIs

#### 3.1 Search Investigators

**Endpoint:** `GET /api/integrations/investigators/search`

**Query Parameters:**
- `agency_id` (optional)
- `location` (optional)
- `specialization` (optional)
- `status=active`

**Response:**
```json
{
  "success": true,
  "data": {
    "investigators": [
      {
        "investigator_id": "inv-001",
        "name": "John Investigator",
        "email": "john@investigations.com",
        "phone": "+65-9123-4567",
        "agency_id": "agency-001",
        "agency_name": "ABC Investigation Services",
        "specializations": ["Death Verification", "Hospital Verification"],
        "location": "Singapore",
        "rating": 4.8,
        "cases_completed": 145,
        "status": "active",
        "availability": "available"
      }
    ],
    "total": 1
  }
}
```

---

### 4. Document Management APIs

#### 4.1 Get Claim Documents

**Endpoint:** `GET /api/integrations/claims/{claim_number}/documents`

**Response:**
```json
{
  "success": true,
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
        "download_url": "https://claims-platform.com/api/documents/doc-001/download",
        "preview_url": "https://claims-platform.com/api/documents/doc-001/preview"
      }
    ],
    "total": 1
  }
}
```

#### 4.2 Download Document

**Endpoint:** `GET /api/integrations/documents/{document_id}/download`

**Response:** Binary file stream

---

### 5. Evidence Management APIs

#### 5.1 Upload Evidence (Investigation Portal → Claims Platform)

**Endpoint:** `POST /api/integrations/investigations/{investigation_id}/evidence`

**Request:** Multipart form-data

**Form Fields:**
- `file` - File upload
- `service_id` - Service UUID
- `evidence_type` - Type of evidence
- `description` - Evidence description
- `geo_location` - JSON with lat/long (if applicable)

**Response:**
```json
{
  "success": true,
  "data": {
    "evidence_id": "evidence-uuid-001",
    "investigation_id": "INV000251",
    "file_name": "hospital_visit_photo.jpg",
    "file_size": 2048576,
    "file_type": "image/jpeg",
    "uploaded_at": "2026-06-04T09:00:00Z",
    "download_url": "https://storage.metamorphosys.com/evidence/evidence-uuid-001",
    "geo_location": {
      "latitude": 1.2958,
      "longitude": 103.7867,
      "captured_at": "2026-06-04T08:45:00Z"
    }
  }
}
```

---

### 6. Findings Submission APIs

#### 6.1 Submit Investigation Findings

**Endpoint:** `POST /api/integrations/investigations/{investigation_id}/findings`

**Request Body:**
```json
{
  "investigation_id": "INV000251",
  "external_reference": {
    "claim_number": "CLM0001288"
  },
  "findings": {
    "summary": "Investigation completed. Hospital records verified. Death certificate authenticated.",
    "observations": "Visited National University Hospital on 2026-06-04. Interviewed Dr. Smith who attended to patient. Death certificate verified as authentic. Hospital admission records consistent with claim details.",
    "key_findings": "1. Death certificate is genuine. 2. Hospital records match claim. 3. No fraud indicators found. 4. Timeline is consistent.",
    "suspicion_indicators": null,
    "conclusion": "Claim appears legitimate. All documentation verified and authentic. No red flags identified.",
    "outcome": "genuine",
    "recommendation": "approve",
    "confidence_level": "high"
  },
  "evidence_summary": {
    "total_evidence": 13,
    "photos": 8,
    "videos": 1,
    "documents": 4,
    "geo_tagged": 5
  },
  "services_completed": [
    {
      "service_id": "svc-uuid-001",
      "service_name": "Hospital Visit",
      "status": "completed",
      "completion_date": "2026-06-04T09:00:00Z"
    }
  ],
  "submitted_by": {
    "investigator_id": "inv-001",
    "investigator_name": "John Investigator",
    "investigator_email": "investigator@agency.com"
  },
  "submitted_at": "2026-06-05T14:30:00Z",
  "investigation_duration_hours": 48
}
```

**Response:**
```json
{
  "success": true,
  "message": "Investigation findings received successfully",
  "claim_number": "CLM0001288",
  "status_updated_to": "Investigation Complete - Pending Review",
  "next_action": "Assessor review required",
  "findings_id": "findings-uuid-001"
}
```

---

### 7. Rework Request APIs

#### 7.1 Create Rework Request (Claims Platform → Investigation Portal)

**Endpoint:** `POST /api/integrations/investigations/{investigation_id}/rework`

**Request Body:**
```json
{
  "investigation_id": "INV000251",
  "rework_reason": "additional_evidence_required",
  "reason_description": "Please obtain signed statement from attending physician",
  "additional_instructions": "Interview Dr. Smith again and obtain written statement confirming cause of death. Also verify patient's medical history with hospital records department.",
  "expected_deliverables": [
    "Signed physician statement",
    "Medical history records",
    "Updated investigation report"
  ],
  "priority": "high",
  "new_due_date": "2026-06-15",
  "requested_by": {
    "assessor_id": "assessor-001",
    "assessor_name": "Jane Assessor",
    "assessor_email": "jane.assessor@metamorphosys.com"
  },
  "requested_at": "2026-06-06T10:00:00Z"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "rework_id": "rework-uuid-001",
    "investigation_id": "INV000251",
    "status": "rework_requested",
    "notification_sent": true,
    "investigator_notified": "investigator@agency.com"
  }
}
```

---

### 8. Timeline & Activity APIs

#### 8.1 Get Investigation Timeline

**Endpoint:** `GET /api/integrations/investigations/{investigation_id}/timeline`

**Response:**
```json
{
  "success": true,
  "data": {
    "activities": [
      {
        "activity_id": "activity-001",
        "timestamp": "2026-06-03T10:00:15Z",
        "activity_type": "case_assigned",
        "description": "Investigation case assigned to John Investigator",
        "performed_by": {
          "user_id": "assessor-001",
          "user_name": "Jane Assessor",
          "user_role": "assessor"
        }
      },
      {
        "activity_id": "activity-002",
        "timestamp": "2026-06-03T14:30:00Z",
        "activity_type": "status_changed",
        "description": "Status changed from 'assigned' to 'in_progress'",
        "performed_by": {
          "user_id": "inv-001",
          "user_name": "John Investigator",
          "user_role": "investigator"
        }
      }
    ],
    "total": 2
  }
}
```

---

### 9. Notification APIs

#### 9.1 Webhook for Status Changes (Investigation Portal → Claims Platform)

**Endpoint:** `POST {CLAIMS_PLATFORM_WEBHOOK_URL}/webhooks/investigation-status`

**Payload:**
```json
{
  "event_type": "investigation.status_changed",
  "event_id": "event-uuid-001",
  "timestamp": "2026-06-03T14:30:00Z",
  "data": {
    "investigation_id": "INV000251",
    "claim_number": "CLM0001288",
    "old_status": "assigned",
    "new_status": "in_progress",
    "changed_by": {
      "user_id": "inv-001",
      "user_name": "John Investigator"
    }
  }
}
```

#### 9.2 Webhook for Findings Submitted

**Payload:**
```json
{
  "event_type": "investigation.findings_submitted",
  "event_id": "event-uuid-002",
  "timestamp": "2026-06-05T14:30:00Z",
  "data": {
    "investigation_id": "INV000251",
    "claim_number": "CLM0001288",
    "outcome": "genuine",
    "recommendation": "approve",
    "findings_url": "https://investigations.metamorphosys.com/api/integrations/investigations/INV000251/findings"
  }
}
```

---

## Authentication Strategy

### Recommended Approach: JWT with Service Accounts

**Why JWT?**
- Stateless authentication
- Scalable
- Industry standard
- Easy to implement
- Supports expiration and refresh

**Implementation:**

1. **Service Account Creation**
   ```json
   {
     "service_account": {
       "client_id": "metamorphosys-claims-platform",
       "client_secret": "generated-secret",
       "permissions": [
         "investigations.create",
         "investigations.read",
         "investigations.update",
         "claims.read",
         "documents.read"
       ],
       "rate_limit": 1000,
       "rate_limit_window": "1h"
     }
   }
   ```

2. **Token Generation**
   ```http
   POST /api/integrations/auth/token
   Content-Type: application/json
   
   {
     "client_id": "metamorphosys-claims-platform",
     "client_secret": "generated-secret",
     "grant_type": "client_credentials"
   }
   ```

3. **Token Response**
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIs...",
     "token_type": "Bearer",
     "expires_in": 3600,
     "scope": "investigations.* claims.read"
   }
   ```

4. **Usage**
   ```http
   GET /api/integrations/investigations/INV000251
   Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
   X-Client-ID: metamorphosys-claims-platform
   ```

---

## Data Synchronization Strategy

### 1. Real-time Sync (Webhooks)
- Status changes
- Findings submission
- Rework requests
- Critical events

### 2. Polling (Fallback)
- Every 5 minutes for pending updates
- Retry logic with exponential backoff

### 3. Batch Sync (Daily)
- Full data reconciliation at 2 AM
- Audit trail verification
- Data consistency checks

### 4. Event Store
- Store all events in event log
- Replay capability for recovery
- Audit trail for compliance

---

## Event Flow Diagrams

### Flow 1: Investigation Creation

```
Assessor (Claims Platform)
    │
    │ 1. Fill Investigation Form
    │    (Category, Services, Notes)
    │
    ▼
Claims Platform Backend
    │
    │ 2. Validate Data
    │ 3. Create Local Record
    │
    ▼
API Call: POST /api/integrations/investigations
    │
    ▼
Investigation Portal Backend
    │
    │ 4. Validate Request
    │ 5. Create Investigation Case
    │ 6. Assign to Investigator
    │
    ▼
Response: Investigation ID + URL
    │
    ▼
Claims Platform Backend
    │
    │ 7. Store Investigation ID
    │ 8. Update Claim Status
    │
    ▼
Investigator
    │
    │ 9. Receives Notification
    │ 10. Opens Investigation Portal
    │
```

### Flow 2: Findings Submission

```
Investigator
    │
    │ 1. Complete Services
    │ 2. Upload Evidence
    │ 3. Fill Findings Form
    │ 4. Submit Findings
    │
    ▼
Investigation Portal Backend
    │
    │ 5. Validate Findings
    │ 6. Update Case Status
    │ 7. Store Findings
    │
    ▼
API Call: POST /api/integrations/investigations/{id}/findings
    │
    ▼
Claims Platform Backend
    │
    │ 8. Receive Findings
    │ 9. Update Claim Status
    │ 10. Notify Assessor
    │
    ▼
Webhook: investigation.findings_submitted
    │
    ▼
Claims Platform UI
    │
    │ 11. Show Notification
    │ 12. Enable Review
    │
    ▼
Assessor
    │
    │ 13. Review Findings
    │ 14. Approve/Reject/Rework
    │
```

---

## Questions for MetaMorphoSys Team

### Technical Questions

1. **Authentication & Security**
   - Do you have existing service account infrastructure?
   - What authentication mechanism is preferred? (JWT, OAuth2, API Keys)
   - What are your rate limiting requirements?
   - Do you have API gateway for external integrations?

2. **Existing APIs**
   - Do you have existing APIs for claim data retrieval?
   - Is there a document management API?
   - Do you have investigator directory APIs?
   - What is the current API versioning strategy?

3. **Data Standards**
   - What is the standard format for claim numbers?
   - Policy number format and validation?
   - Investigation ID format preferences?
   - Date/time format (ISO 8601 preferred)?

4. **Webhooks & Events**
   - Do you support webhook callbacks?
   - What is your webhook retry policy?
   - Do you need webhook signature verification?

5. **Performance & Scale**
   - Expected API call volume?
   - Response time SLA requirements?
   - Data retention requirements?
   - Backup and disaster recovery expectations?

### Business Questions

6. **Workflow Integration**
   - At what claim status should investigation be triggered?
   - Should investigation findings auto-update claim decision?
   - Who approves investigation recommendations?
   - What happens if investigator misses deadline?

7. **User Management**
   - How are investigators registered in your system?
   - Should investigation portal sync user changes?
   - How to handle investigator agency changes?

8. **Reporting & Analytics**
   - Do you need investigation metrics in claims dashboard?
   - Should investigation data appear in claims reports?
   - Do you need API for historical investigation data?

9. **Compliance & Audit**
   - Data residency requirements?
   - Audit log retention period?
   - PII handling requirements?
   - GDPR/PDPA compliance needs?

10. **Future Requirements**
    - Plans for mobile app integration?
    - Real-time chat requirements?
    - Document e-signature integration?
    - AI/ML integration for fraud detection?

---

**End of Integration Architecture Document**

Next: API Gap Analysis & Mock APIs Documentation
