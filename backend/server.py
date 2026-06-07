from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request, Response, UploadFile, File, Query, Header
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt
import requests
from bson import ObjectId
import io

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ===== AUTH UTILITIES =====
JWT_SECRET = os.environ['JWT_SECRET']
JWT_ALGORITHM = "HS256"

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(user_id: str, email: str, role: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
        "type": "access"
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
        "type": "refresh"
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(request: Request) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        user["id"] = str(user.pop("_id"))
        user.pop("password_hash", None)
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def require_role(request: Request, allowed_roles: List[str]):
    user = await get_current_user(request)
    if user["role"] not in allowed_roles:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return user

# ===== OBJECT STORAGE =====
STORAGE_URL = "https://integrations.emergentagent.com/objstore/api/v1/storage"
EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY")
APP_NAME = "investigation-portal"
storage_key = None

def init_storage():
    global storage_key
    if storage_key:
        return storage_key
    try:
        resp = requests.post(f"{STORAGE_URL}/init", json={"emergent_key": EMERGENT_KEY}, timeout=30)
        resp.raise_for_status()
        storage_key = resp.json()["storage_key"]
        logger.info("Storage initialized successfully")
        return storage_key
    except Exception as e:
        logger.error(f"Storage init failed: {e}")
        raise

def put_object(path: str, data: bytes, content_type: str) -> dict:
    key = init_storage()
    resp = requests.put(
        f"{STORAGE_URL}/objects/{path}",
        headers={"X-Storage-Key": key, "Content-Type": content_type},
        data=data,
        timeout=120
    )
    resp.raise_for_status()
    return resp.json()

def get_object(path: str) -> tuple:
    key = init_storage()
    resp = requests.get(
        f"{STORAGE_URL}/objects/{path}",
        headers={"X-Storage-Key": key},
        timeout=60
    )
    resp.raise_for_status()
    return resp.content, resp.headers.get("Content-Type", "application/octet-stream")

# ===== MODELS =====
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str
    agency_id: Optional[str] = None
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str
    agency_id: Optional[str] = None
    phone: Optional[str] = None
    created_at: str

class AgencyCreate(BaseModel):
    name: str
    contact_person: str
    email: EmailStr
    phone: str
    address: Optional[str] = None

class AgencyResponse(BaseModel):
    id: str
    name: str
    contact_person: str
    email: str
    phone: str
    address: Optional[str] = None
    is_active: bool
    created_at: str

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class SubCategoryCreate(BaseModel):
    category_id: str
    name: str
    description: Optional[str] = None

class ServiceCategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    requires_geo_tag: bool = False

class InvestigationCaseCreate(BaseModel):
    claim_number: str
    policy_number: str
    insured_name: str
    category_id: str
    sub_category_id: str
    assigned_investigator_id: str
    assessor_notes: str
    requested_services: List[Dict[str, str]]
    due_date: str

class ServiceUpdate(BaseModel):
    status: str
    remarks: Optional[str] = None

class EvidenceUpload(BaseModel):
    investigation_id: str
    service_id: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    notes: Optional[str] = None

class FindingsSubmit(BaseModel):
    observations: str
    conclusion: str
    recommendation: str
    outcome: str

class ReworkRequest(BaseModel):
    reason: str
    additional_instructions: str
    expected_deliverables: str

# ===== ADMIN SEEDING =====
async def seed_admin():
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@investigationportal.com")
    admin_password = os.environ.get("ADMIN_PASSWORD", "Admin@123")
    existing = await db.users.find_one({"email": admin_email})
    if existing is None:
        hashed = hash_password(admin_password)
        await db.users.insert_one({
            "email": admin_email,
            "password_hash": hashed,
            "name": "Admin",
            "role": "admin",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        logger.info(f"Admin user created: {admin_email}")
    elif not verify_password(admin_password, existing["password_hash"]):
        await db.users.update_one(
            {"email": admin_email},
            {"$set": {"password_hash": hash_password(admin_password)}}
        )
        logger.info("Admin password updated")
    
    # Write test credentials
    MEMORY_PATH = os.getenv("MEMORY_PATH", "./memory")

    Path(MEMORY_PATH).mkdir(parents=True, exist_ok=True)
    with open(f"{MEMORY_PATH}/test_credentials.md", "w") as f:
        f.write("# Test Credentials\n\n")
        f.write(f"## Admin\n")
        f.write(f"- Email: {admin_email}\n")
        f.write(f"- Password: {admin_password}\n")
        f.write(f"- Role: admin\n\n")
        f.write("## Auth Endpoints\n")
        f.write("- POST /api/auth/register\n")
        f.write("- POST /api/auth/login\n")
        f.write("- GET /api/auth/me\n")
        f.write("- POST /api/auth/logout\n")

# ===== AUTH ROUTES =====
@api_router.post("/auth/register")
async def register(user: UserCreate, response: Response):
    user.email = user.email.lower()
    existing = await db.users.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed = hash_password(user.password)
    user_doc = {
        "email": user.email,
        "password_hash": hashed,
        "name": user.name,
        "role": user.role,
        "agency_id": user.agency_id,
        "phone": user.phone,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    result = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)
    
    access_token = create_access_token(user_id, user.email, user.role)
    refresh_token = create_refresh_token(user_id)
    
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True, samesite="none", max_age=900, path="/")
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite="none", max_age=604800, path="/")
    
    return UserResponse(
        id=user_id,
        email=user.email,
        name=user.name,
        role=user.role,
        agency_id=user.agency_id,
        phone=user.phone,
        created_at=user_doc["created_at"]
    )

@api_router.post("/auth/login")
async def login(credentials: UserLogin, response: Response, request: Request):
    credentials.email = credentials.email.lower()
    user = await db.users.find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user_id = str(user["_id"])
    access_token = create_access_token(user_id, user["email"], user["role"])
    refresh_token = create_refresh_token(user_id)
    
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True, samesite="none", max_age=900, path="/")
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite="none", max_age=604800, path="/")
    
    return UserResponse(
        id=user_id,
        email=user["email"],
        name=user["name"],
        role=user["role"],
        agency_id=user.get("agency_id"),
        phone=user.get("phone"),
        created_at=user["created_at"]
    )

@api_router.get("/auth/me")
async def get_me(request: Request):
    user = await get_current_user(request)
    user["id"] = user.pop("_id", user.get("id"))
    return user

@api_router.post("/auth/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}

# ===== USER MANAGEMENT =====
@api_router.get("/users")
async def list_users(request: Request, role: Optional[str] = None):
    await require_role(request, ["admin"])
    query = {"role": role} if role else {}
    users = await db.users.find(query, {"password_hash": 0}).to_list(1000)
    for u in users:
        u["id"] = str(u.pop("_id"))
    return users

@api_router.get("/users/{user_id}")
async def get_user(user_id: str, request: Request):
    await require_role(request, ["admin"])
    user = await db.users.find_one({"_id": ObjectId(user_id)}, {"password_hash": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user["id"] = str(user.pop("_id"))
    return user

@api_router.put("/users/{user_id}")
async def update_user(user_id: str, data: dict, request: Request):
    await require_role(request, ["admin"])
    data.pop("password", None)
    data.pop("password_hash", None)
    result = await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User updated"}

@api_router.delete("/users/{user_id}")
async def delete_user(user_id: str, request: Request):
    await require_role(request, ["admin"])
    result = await db.users.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}

# ===== AGENCY MANAGEMENT =====
@api_router.post("/agencies")
async def create_agency(agency: AgencyCreate, request: Request):
    await require_role(request, ["admin"])
    agency_doc = {
        **agency.model_dump(),
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    result = await db.agencies.insert_one(agency_doc)
    return {"id": str(result.inserted_id), **agency_doc}

@api_router.get("/agencies")
async def list_agencies(request: Request):
    user = await get_current_user(request)
    agencies = await db.agencies.find({}).to_list(1000)
    for a in agencies:
        a["id"] = str(a.pop("_id"))
    return agencies

@api_router.get("/agencies/{agency_id}")
async def get_agency(agency_id: str, request: Request):
    user = await get_current_user(request)
    agency = await db.agencies.find_one({"_id": ObjectId(agency_id)})
    if not agency:
        raise HTTPException(status_code=404, detail="Agency not found")
    agency["id"] = str(agency.pop("_id"))
    return agency

@api_router.put("/agencies/{agency_id}")
async def update_agency(agency_id: str, data: dict, request: Request):
    await require_role(request, ["admin"])
    result = await db.agencies.update_one({"_id": ObjectId(agency_id)}, {"$set": data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Agency not found")
    return {"message": "Agency updated"}

@api_router.delete("/agencies/{agency_id}")
async def delete_agency(agency_id: str, request: Request):
    await require_role(request, ["admin"])
    result = await db.agencies.delete_one({"_id": ObjectId(agency_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Agency not found")
    return {"message": "Agency deleted"}

# ===== CATEGORY MANAGEMENT =====
@api_router.post("/categories")
async def create_category(category: CategoryCreate, request: Request):
    await require_role(request, ["admin"])
    category_doc = {**category.model_dump(), "created_at": datetime.now(timezone.utc).isoformat()}
    result = await db.categories.insert_one(category_doc)
    return {"id": str(result.inserted_id), **category_doc}

@api_router.get("/categories")
async def list_categories(request: Request):
    user = await get_current_user(request)
    categories = await db.categories.find({}).to_list(1000)
    for c in categories:
        c["id"] = str(c.pop("_id"))
    return categories

@api_router.delete("/categories/{category_id}")
async def delete_category(category_id: str, request: Request):
    await require_role(request, ["admin"])
    result = await db.categories.delete_one({"_id": ObjectId(category_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted"}

# ===== SUB-CATEGORY MANAGEMENT =====
@api_router.post("/subcategories")
async def create_subcategory(subcategory: SubCategoryCreate, request: Request):
    await require_role(request, ["admin"])
    subcategory_doc = {**subcategory.model_dump(), "created_at": datetime.now(timezone.utc).isoformat()}
    result = await db.subcategories.insert_one(subcategory_doc)
    return {"id": str(result.inserted_id), **subcategory_doc}

@api_router.get("/subcategories")
async def list_subcategories(request: Request, category_id: Optional[str] = None):
    user = await get_current_user(request)
    query = {"category_id": category_id} if category_id else {}
    subcategories = await db.subcategories.find(query).to_list(1000)
    for sc in subcategories:
        sc["id"] = str(sc.pop("_id"))
    return subcategories

@api_router.delete("/subcategories/{subcategory_id}")
async def delete_subcategory(subcategory_id: str, request: Request):
    await require_role(request, ["admin"])
    result = await db.subcategories.delete_one({"_id": ObjectId(subcategory_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Subcategory not found")
    return {"message": "Subcategory deleted"}

# ===== SERVICE CATEGORIES =====
@api_router.post("/service-categories")
async def create_service_category(service: ServiceCategoryCreate, request: Request):
    await require_role(request, ["admin"])
    service_doc = {**service.model_dump(), "created_at": datetime.now(timezone.utc).isoformat()}
    result = await db.service_categories.insert_one(service_doc)
    return {"id": str(result.inserted_id), **service_doc}

@api_router.get("/service-categories")
async def list_service_categories(request: Request):
    user = await get_current_user(request)
    services = await db.service_categories.find({}).to_list(1000)
    for s in services:
        s["id"] = str(s.pop("_id"))
    return services

@api_router.delete("/service-categories/{service_id}")
async def delete_service_category(service_id: str, request: Request):
    await require_role(request, ["admin"])
    result = await db.service_categories.delete_one({"_id": ObjectId(service_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Service category not found")
    return {"message": "Service category deleted"}

# ===== INVESTIGATION CASES =====
@api_router.post("/investigations")
async def create_investigation(case: InvestigationCaseCreate, request: Request):
    user = await require_role(request, ["admin", "assessor"])
    
    # Generate investigation ID
    count = await db.investigations.count_documents({})
    investigation_id = f"INV{str(count + 1).zfill(6)}"
    
    # Create services
    services = []
    for svc in case.requested_services:
        services.append({
            "id": str(uuid.uuid4()),
            "service_category_id": svc.get("service_category_id"),
            "service_name": svc.get("service_name"),
            "remarks": svc.get("remarks", ""),
            "status": "pending",
            "evidence_count": 0,
            "completed_at": None
        })
    
    case_doc = {
        "investigation_id": investigation_id,
        "claim_number": case.claim_number,
        "policy_number": case.policy_number,
        "insured_name": case.insured_name,
        "category_id": case.category_id,
        "sub_category_id": case.sub_category_id,
        "assigned_investigator_id": case.assigned_investigator_id,
        "assessor_id": user["id"],
        "assessor_notes": case.assessor_notes,
        "status": "assigned",
        "services": services,
        "due_date": case.due_date,
        "assigned_date": datetime.now(timezone.utc).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    result = await db.investigations.insert_one(case_doc)
    
    # Create activity log
    await db.activities.insert_one({
        "investigation_id": investigation_id,
        "user_id": user["id"],
        "user_name": user["name"],
        "action": "case_assigned",
        "description": f"Investigation case assigned to investigator",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    # Create notification
    await db.notifications.insert_one({
        "user_id": case.assigned_investigator_id,
        "investigation_id": investigation_id,
        "type": "case_assignment",
        "message": f"New investigation case {investigation_id} assigned to you",
        "is_read": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    case_doc["id"] = str(result.inserted_id)
    case_doc.pop("_id", None)
    return case_doc

@api_router.get("/investigations")
async def list_investigations(
    request: Request,
    status: Optional[str] = None,
    investigator_id: Optional[str] = None,
    category_id: Optional[str] = None,
    search: Optional[str] = None
):
    user = await get_current_user(request)
    
    query = {}
    if user["role"] == "investigator":
        query["assigned_investigator_id"] = user["id"]
    elif investigator_id:
        query["assigned_investigator_id"] = investigator_id
    
    if status:
        query["status"] = status
    if category_id:
        query["category_id"] = category_id
    if search:
        query["$or"] = [
            {"investigation_id": {"$regex": search, "$options": "i"}},
            {"claim_number": {"$regex": search, "$options": "i"}},
            {"policy_number": {"$regex": search, "$options": "i"}},
            {"insured_name": {"$regex": search, "$options": "i"}}
        ]
    
    investigations = await db.investigations.find(query).sort("created_at", -1).to_list(1000)
    for inv in investigations:
        inv["id"] = str(inv.pop("_id"))
    return investigations

@api_router.get("/investigations/{investigation_id}")
async def get_investigation(investigation_id: str, request: Request):
    user = await get_current_user(request)
    investigation = await db.investigations.find_one({"investigation_id": investigation_id})
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")
    
    if user["role"] == "investigator" and investigation["assigned_investigator_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to view this investigation")
    
    investigation["id"] = str(investigation.pop("_id"))
    
    # Get category and subcategory names
    category = await db.categories.find_one({"_id": ObjectId(investigation["category_id"])})
    subcategory = await db.subcategories.find_one({"_id": ObjectId(investigation["sub_category_id"])})
    investigator = await db.users.find_one({"_id": ObjectId(investigation["assigned_investigator_id"])}, {"password_hash": 0})
    
    investigation["category_name"] = category["name"] if category else ""
    investigation["sub_category_name"] = subcategory["name"] if subcategory else ""
    investigation["investigator_name"] = investigator["name"] if investigator else ""
    
    return investigation

@api_router.put("/investigations/{investigation_id}/status")
async def update_investigation_status(investigation_id: str, data: dict, request: Request):
    user = await get_current_user(request)
    investigation = await db.investigations.find_one({"investigation_id": investigation_id})
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")
    
    if user["role"] == "investigator" and investigation["assigned_investigator_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.investigations.update_one(
        {"investigation_id": investigation_id},
        {"$set": {"status": data["status"], "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    # Log activity
    await db.activities.insert_one({
        "investigation_id": investigation_id,
        "user_id": user["id"],
        "user_name": user["name"],
        "action": "status_changed",
        "description": f"Status changed to {data['status']}",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    return {"message": "Status updated"}

# ===== SERVICE MANAGEMENT =====
@api_router.put("/investigations/{investigation_id}/services/{service_id}")
async def update_service(investigation_id: str, service_id: str, data: ServiceUpdate, request: Request):
    user = await get_current_user(request)
    investigation = await db.investigations.find_one({"investigation_id": investigation_id})
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")
    
    if user["role"] == "investigator" and investigation["assigned_investigator_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    services = investigation["services"]
    for svc in services:
        if svc["id"] == service_id:
            svc["status"] = data.status
            if data.remarks:
                svc["remarks"] = data.remarks
            if data.status == "completed":
                svc["completed_at"] = datetime.now(timezone.utc).isoformat()
            break
    
    await db.investigations.update_one(
        {"investigation_id": investigation_id},
        {"$set": {"services": services, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    # Log activity
    await db.activities.insert_one({
        "investigation_id": investigation_id,
        "user_id": user["id"],
        "user_name": user["name"],
        "action": "service_updated",
        "description": f"Service status changed to {data.status}",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    return {"message": "Service updated"}

# ===== EVIDENCE MANAGEMENT =====
@api_router.post("/investigations/{investigation_id}/evidence")
async def upload_evidence(
    investigation_id: str,
    request: Request,
    file: UploadFile = File(...),
    service_ids: str = Query(""),  # Comma-separated service IDs
    latitude: Optional[float] = Query(None),
    longitude: Optional[float] = Query(None),
    notes: Optional[str] = Query(None)
):
    user = await get_current_user(request)
    investigation = await db.investigations.find_one({"investigation_id": investigation_id})
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")
    
    if user["role"] == "investigator" and investigation["assigned_investigator_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Parse service IDs
    linked_services = [sid.strip() for sid in service_ids.split(",") if sid.strip()]
    
    # Upload file to storage
    ext = file.filename.split(".")[-1] if "." in file.filename else "bin"
    path = f"{APP_NAME}/evidence/{investigation_id}/{uuid.uuid4()}.{ext}"
    file_data = await file.read()
    
    result = put_object(path, file_data, file.content_type or "application/octet-stream")
    
    # Store evidence metadata - CENTRALIZED MODEL
    evidence_doc = {
        "id": str(uuid.uuid4()),
        "investigation_id": investigation_id,
        "linked_services": linked_services,  # Array of service IDs
        "storage_path": result["path"],
        "original_filename": file.filename,
        "content_type": file.content_type,
        "size": result["size"],
        "latitude": latitude,
        "longitude": longitude,
        "notes": notes,
        "uploaded_by": user["id"],
        "uploaded_by_name": user["name"],
        "is_deleted": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.evidence.insert_one(evidence_doc)
    
    # Update service evidence count for all linked services
    services = investigation["services"]
    for svc in services:
        if svc["id"] in linked_services:
            svc["evidence_count"] = svc.get("evidence_count", 0) + 1
    
    await db.investigations.update_one(
        {"investigation_id": investigation_id},
        {"$set": {"services": services}}
    )
    
    # Log activity
    service_names = [svc["service_name"] for svc in services if svc["id"] in linked_services]
    await db.activities.insert_one({
        "investigation_id": investigation_id,
        "user_id": user["id"],
        "user_name": user["name"],
        "action": "evidence_uploaded",
        "description": f"Evidence '{file.filename}' uploaded and linked to {len(linked_services)} service(s)",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    evidence_doc.pop("_id", None)
    return evidence_doc

@api_router.get("/investigations/{investigation_id}/evidence")
async def list_evidence(investigation_id: str, request: Request, service_id: Optional[str] = None):
    user = await get_current_user(request)
    query = {"investigation_id": investigation_id, "is_deleted": False}
    
    # Filter by service if provided
    if service_id:
        query["linked_services"] = service_id
    
    evidence_list = await db.evidence.find(query, {"_id": 0}).to_list(1000)
    return evidence_list

@api_router.get("/evidence/{evidence_id}/download")
async def download_evidence(evidence_id: str, request: Request, auth: Optional[str] = Query(None)):
    if auth:
        request.headers.__dict__["_list"].append((b"authorization", f"Bearer {auth}".encode()))
    
    user = await get_current_user(request)
    evidence = await db.evidence.find_one({"id": evidence_id, "is_deleted": False})
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    data, content_type = get_object(evidence["storage_path"])
    return Response(content=data, media_type=evidence.get("content_type", content_type))

# ===== EVIDENCE LINKING =====
class EvidenceLinkUpdate(BaseModel):
    service_ids: List[str]

@api_router.put("/evidence/{evidence_id}/link-services")
async def update_evidence_links(evidence_id: str, data: EvidenceLinkUpdate, request: Request):
    """Update which services an evidence item is linked to"""
    user = await get_current_user(request)
    evidence = await db.evidence.find_one({"id": evidence_id, "is_deleted": False})
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    investigation = await db.investigations.find_one({"investigation_id": evidence["investigation_id"]})
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")
    
    # Authorization check
    if user["role"] == "investigator" and investigation["assigned_investigator_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    old_services = evidence.get("linked_services", [])
    new_services = data.service_ids
    
    # Update evidence document
    await db.evidence.update_one(
        {"id": evidence_id},
        {"$set": {"linked_services": new_services}}
    )
    
    # Update service evidence counts
    services = investigation["services"]
    for svc in services:
        # Decrement count for removed services
        if svc["id"] in old_services and svc["id"] not in new_services:
            svc["evidence_count"] = max(0, svc.get("evidence_count", 0) - 1)
        # Increment count for added services
        elif svc["id"] not in old_services and svc["id"] in new_services:
            svc["evidence_count"] = svc.get("evidence_count", 0) + 1
    
    await db.investigations.update_one(
        {"investigation_id": evidence["investigation_id"]},
        {"$set": {"services": services}}
    )
    
    # Log activity
    await db.activities.insert_one({
        "investigation_id": evidence["investigation_id"],
        "user_id": user["id"],
        "user_name": user["name"],
        "action": "evidence_links_updated",
        "description": f"Evidence '{evidence['original_filename']}' service links updated",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    return {"message": "Evidence links updated successfully"}

@api_router.get("/investigations/{investigation_id}/evidence/library")
async def get_evidence_library(investigation_id: str, request: Request):
    """Get all evidence for an investigation with service details"""
    user = await get_current_user(request)
    investigation = await db.investigations.find_one({"investigation_id": investigation_id})
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")
    
    # Get all evidence
    evidence_list = await db.evidence.find(
        {"investigation_id": investigation_id, "is_deleted": False},
        {"_id": 0}
    ).to_list(1000)
    
    # Enrich with service names
    service_map = {svc["id"]: svc["service_name"] for svc in investigation.get("services", [])}
    
    for evidence in evidence_list:
        linked_service_names = [
            {"id": sid, "name": service_map.get(sid, "Unknown")}
            for sid in evidence.get("linked_services", [])
        ]
        evidence["linked_service_details"] = linked_service_names
    
    return evidence_list

# ===== FINDINGS =====
@api_router.post("/investigations/{investigation_id}/findings")
async def submit_findings(investigation_id: str, findings: FindingsSubmit, request: Request):
    user = await get_current_user(request)
    investigation = await db.investigations.find_one({"investigation_id": investigation_id})
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")
    
    # Authorization check
    if user["role"] == "investigator" and investigation["assigned_investigator_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="You are not authorized to submit findings for this investigation")
    
    # Status validation - ensure valid transition
    current_status = investigation.get("status")
    valid_statuses = ["in_progress", "rework_requested"]
    if current_status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Investigation must be in 'In Progress' or 'Rework Requested' status to submit findings. Current status: {current_status}"
        )
    
    # Service completion validation - at least one service should be completed or have evidence
    services = investigation.get("services", [])
    has_completed_service = any(svc.get("status") == "completed" for svc in services)
    
    if not has_completed_service:
        # Check if any service has evidence
        evidence_count = await db.evidence.count_documents({
            "investigation_id": investigation_id,
            "is_deleted": False
        })
        if evidence_count == 0:
            raise HTTPException(
                status_code=400,
                detail="Please complete at least one service or upload evidence before submitting findings"
            )
    
    # Field validation (already handled by Pydantic, but adding explicit messages)
    if not findings.observations or not findings.observations.strip():
        raise HTTPException(status_code=400, detail="Observations are required")
    
    if not findings.conclusion or not findings.conclusion.strip():
        raise HTTPException(status_code=400, detail="Conclusion is required")
    
    if not findings.recommendation:
        raise HTTPException(status_code=400, detail="Recommendation is required")
    
    if not findings.outcome:
        raise HTTPException(status_code=400, detail="Outcome is required")
    
    # Valid values check
    valid_recommendations = ["approve", "reject", "further_investigation"]
    if findings.recommendation.lower() not in valid_recommendations:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid recommendation. Must be one of: {', '.join(valid_recommendations)}"
        )
    
    valid_outcomes = ["genuine", "suspicious", "unable_to_verify", "fraud_suspected", "insufficient_evidence"]
    if findings.outcome.lower() not in valid_outcomes:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid outcome. Must be one of: {', '.join(valid_outcomes)}"
        )
    
    # Create findings document
    findings_doc = {
        **findings.model_dump(),
        "submitted_by": user["id"],
        "submitted_by_name": user["name"],
        "submitted_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Update investigation
    await db.investigations.update_one(
        {"investigation_id": investigation_id},
        {"$set": {
            "findings": findings_doc,
            "status": "submitted",
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # Log activity
    await db.activities.insert_one({
        "investigation_id": investigation_id,
        "user_id": user["id"],
        "user_name": user["name"],
        "action": "findings_submitted",
        "description": f"Investigation findings submitted - Outcome: {findings.outcome}, Recommendation: {findings.recommendation}",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    # Notify assessor
    if investigation.get("assessor_id"):
        await db.notifications.insert_one({
            "user_id": investigation["assessor_id"],
            "investigation_id": investigation_id,
            "type": "findings_submitted",
            "message": f"Findings submitted for investigation {investigation_id}",
            "is_read": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
    
    return {"message": "Findings submitted successfully", "status": "submitted"}

@api_router.get("/investigations/{investigation_id}/findings")
async def get_findings(investigation_id: str, request: Request):
    user = await get_current_user(request)
    investigation = await db.investigations.find_one({"investigation_id": investigation_id})
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")
    
    return investigation.get("findings", {})

# ===== REWORK =====
@api_router.post("/investigations/{investigation_id}/rework")
async def request_rework(investigation_id: str, rework: ReworkRequest, request: Request):
    user = await require_role(request, ["admin", "assessor"])
    investigation = await db.investigations.find_one({"investigation_id": investigation_id})
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")
    
    rework_doc = {
        "id": str(uuid.uuid4()),
        **rework.model_dump(),
        "requested_by": user["id"],
        "requested_by_name": user["name"],
        "requested_at": datetime.now(timezone.utc).isoformat()
    }
    
    rework_history = investigation.get("rework_history", [])
    rework_history.append(rework_doc)
    
    await db.investigations.update_one(
        {"investigation_id": investigation_id},
        {"$set": {
            "status": "rework_requested",
            "rework_history": rework_history,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # Log activity
    await db.activities.insert_one({
        "investigation_id": investigation_id,
        "user_id": user["id"],
        "user_name": user["name"],
        "action": "rework_requested",
        "description": f"Rework requested: {rework.reason}",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    # Notify investigator
    await db.notifications.insert_one({
        "user_id": investigation["assigned_investigator_id"],
        "investigation_id": investigation_id,
        "type": "rework_request",
        "message": f"Rework requested for investigation {investigation_id}",
        "is_read": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    return {"message": "Rework requested successfully"}

# ===== ACTIVITY TIMELINE =====
@api_router.get("/investigations/{investigation_id}/activities")
async def get_activities(investigation_id: str, request: Request):
    user = await get_current_user(request)
    activities = await db.activities.find({"investigation_id": investigation_id}).sort("timestamp", -1).to_list(1000)
    for a in activities:
        a["id"] = str(a.pop("_id"))
    return activities

# ===== NOTIFICATIONS =====
@api_router.get("/notifications")
async def get_notifications(request: Request):
    user = await get_current_user(request)
    notifications = await db.notifications.find({"user_id": user["id"]}).sort("created_at", -1).limit(50).to_list(50)
    for n in notifications:
        n["id"] = str(n.pop("_id"))
    return notifications

@api_router.put("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str, request: Request):
    user = await get_current_user(request)
    await db.notifications.update_one(
        {"_id": ObjectId(notification_id), "user_id": user["id"]},
        {"$set": {"is_read": True}}
    )
    return {"message": "Notification marked as read"}

# ===== DASHBOARD STATS =====
@api_router.get("/dashboard/stats")
async def get_dashboard_stats(request: Request):
    user = await get_current_user(request)
    
    if user["role"] == "investigator":
        query = {"assigned_investigator_id": user["id"]}
        assigned = await db.investigations.count_documents({**query, "status": "assigned"})
        in_progress = await db.investigations.count_documents({**query, "status": "in_progress"})
        submitted = await db.investigations.count_documents({**query, "status": "submitted"})
        rework = await db.investigations.count_documents({**query, "status": "rework_requested"})
        completed = await db.investigations.count_documents({**query, "status": "completed"})
        closed = await db.investigations.count_documents({**query, "status": "closed"})
        
        return {
            "assigned": assigned,
            "in_progress": in_progress,
            "submitted": submitted,
            "rework_requested": rework,
            "completed": completed,
            "closed": closed
        }
    else:
        total = await db.investigations.count_documents({})
        assigned = await db.investigations.count_documents({"status": "assigned"})
        in_progress = await db.investigations.count_documents({"status": "in_progress"})
        submitted = await db.investigations.count_documents({"status": "submitted"})
        completed = await db.investigations.count_documents({"status": "completed"})
        closed = await db.investigations.count_documents({"status": "closed"})
        
        # Category breakdown
        pipeline = [
            {"$group": {"_id": "$category_id", "count": {"$sum": 1}}}
        ]
        category_stats = await db.investigations.aggregate(pipeline).to_list(100)
        
        return {
            "total": total,
            "assigned": assigned,
            "in_progress": in_progress,
            "submitted": submitted,
            "completed": completed,
            "closed": closed,
            "by_category": category_stats
        }

# ===== STARTUP =====
@app.on_event("startup")
async def startup():
    await seed_admin()
    try:
        init_storage()
    except Exception as e:
        logger.error(f"Storage initialization failed: {e}")
    
    # Create indexes
    await db.users.create_index("email", unique=True)
    await db.investigations.create_index("investigation_id", unique=True)
    await db.investigations.create_index("assigned_investigator_id")
    await db.investigations.create_index("status")
    await db.activities.create_index("investigation_id")
    await db.notifications.create_index("user_id")
    logger.info("Investigation Portal Backend Started")

app.include_router(api_router)

# Health Check Endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    try:
        # Test database connection
        await db.command("ping")
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

# CORS Configuration - Production Ready
frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
allowed_origins = [
    frontend_url,
    "http://localhost:3000",
    "https://field-ops-44.preview.emergentagent.com"
]

# Add Vercel preview URLs if in production
if os.environ.get('ENVIRONMENT') == 'production':
    allowed_origins.append("https://*.vercel.app")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
