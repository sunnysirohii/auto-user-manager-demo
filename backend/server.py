from fastapi import FastAPI, APIRouter, HTTPException, Depends, Form, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials  
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import jwt
import hashlib
import asyncio
from passlib.context import CryptContext

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "ai-automation-demo-secret-key-not-for-production"

# Create the main app
app = FastAPI(title="AI-Driven Web Automation Demo")
api_router = APIRouter(prefix="/api")

# Mock SaaS Portal Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    role: str  # admin, user, viewer
    status: str = "active"  # active, inactive, pending
    last_login: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    name: str
    email: str
    role: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class MFARequest(BaseModel):
    otp_code: str
    session_token: str

class AutomationJob(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_type: str  # scrape_users, provision_user, deprovision_user
    status: str = "pending"  # pending, running, completed, failed
    parameters: dict = {}
    results: dict = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    logs: List[str] = []

# Authentication helpers
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Initialize demo data
async def init_demo_data():
    # Check if demo users already exist
    existing_users = await db.demo_users.count_documents({})
    if existing_users == 0:
        demo_users = [
            {"id": str(uuid.uuid4()), "name": "Alice Johnson", "email": "alice@company.com", "role": "admin", "status": "active", "last_login": "2024-01-15 14:30:00", "created_at": datetime.utcnow()},
            {"id": str(uuid.uuid4()), "name": "Bob Smith", "email": "bob@company.com", "role": "user", "status": "active", "last_login": "2024-01-14 09:15:00", "created_at": datetime.utcnow()},
            {"id": str(uuid.uuid4()), "name": "Carol Davis", "email": "carol@company.com", "role": "viewer", "status": "inactive", "last_login": "2024-01-10 16:45:00", "created_at": datetime.utcnow()},
            {"id": str(uuid.uuid4()), "name": "David Wilson", "email": "david@company.com", "role": "user", "status": "active", "last_login": "2024-01-16 11:20:00", "created_at": datetime.utcnow()},
            {"id": str(uuid.uuid4()), "name": "Eve Brown", "email": "eve@company.com", "role": "admin", "status": "pending", "last_login": None, "created_at": datetime.utcnow()},
            {"id": str(uuid.uuid4()), "name": "Frank Miller", "email": "frank@company.com", "role": "user", "status": "active", "last_login": "2024-01-13 08:30:00", "created_at": datetime.utcnow()},
            {"id": str(uuid.uuid4()), "name": "Grace Lee", "email": "grace@company.com", "role": "viewer", "status": "active", "last_login": "2024-01-16 10:00:00", "created_at": datetime.utcnow()},
        ]
        await db.demo_users.insert_many(demo_users)

# Mock SaaS Portal API Routes
@api_router.post("/mock-saas/login")
async def mock_login(request: LoginRequest):
    """Simulated SaaS login with MFA"""
    # Simulate credential validation (demo: admin/password)
    if request.username == "admin" and request.password == "password":
        # Return session token for MFA step
        session_token = create_access_token({"username": request.username, "step": "mfa_required"})
        return {"success": True, "requires_mfa": True, "session_token": session_token}
    else:
        await asyncio.sleep(1)  # Simulate processing delay
        raise HTTPException(status_code=401, detail="Invalid credentials")

@api_router.post("/mock-saas/verify-mfa")
async def verify_mfa(request: MFARequest):
    """Verify MFA code (demo: accepts 123456)"""
    try:
        payload = jwt.decode(request.session_token, SECRET_KEY, algorithms=["HS256"])
        if payload.get("step") != "mfa_required":
            raise HTTPException(status_code=400, detail="Invalid session")
        
        # Demo: accept any 6-digit code
        if len(request.otp_code) == 6 and request.otp_code.isdigit():
            # Create final access token
            access_token = create_access_token({"username": payload["username"], "step": "authenticated"})
            return {"success": True, "access_token": access_token}
        else:
            raise HTTPException(status_code=400, detail="Invalid OTP code")
    except jwt.PyJWTError:
        raise HTTPException(status_code=400, detail="Invalid session token")

@api_router.get("/mock-saas/users")
async def get_mock_users(
    page: int = 1, 
    limit: int = 10, 
    search: str = "",
    role: str = "",
    status: str = "",
    current_user=Depends(verify_token)
):
    """Get paginated users from mock SaaS"""
    query = {}
    
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}}
        ]
    
    if role:
        query["role"] = role
    
    if status:
        query["status"] = status
    
    skip = (page - 1) * limit
    users = await db.demo_users.find(query).skip(skip).limit(limit).to_list(limit)
    total = await db.demo_users.count_documents(query)
    
    return {
        "users": [User(**user) for user in users],
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }

@api_router.post("/mock-saas/users")
async def create_mock_user(user: UserCreate, current_user=Depends(verify_token)):
    """Create new user in mock SaaS"""
    # Check if email already exists
    existing = await db.demo_users.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    new_user = User(**user.dict())
    await db.demo_users.insert_one(new_user.dict())
    return new_user

@api_router.put("/mock-saas/users/{user_id}")
async def update_mock_user(user_id: str, user: UserUpdate, current_user=Depends(verify_token)):
    """Update user in mock SaaS"""
    existing = await db.demo_users.find_one({"id": user_id})
    if not existing:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = {k: v for k, v in user.dict().items() if v is not None}
    if update_data:
        await db.demo_users.update_one({"id": user_id}, {"$set": update_data})
    
    updated_user = await db.demo_users.find_one({"id": user_id})
    return User(**updated_user)

@api_router.delete("/mock-saas/users/{user_id}")
async def delete_mock_user(user_id: str, current_user=Depends(verify_token)):
    """Delete user from mock SaaS"""
    result = await db.demo_users.delete_one({"id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"success": True, "message": "User deleted"}

# Automation Orchestrator API Routes
@api_router.post("/automation/jobs")
async def create_automation_job(job_type: str, parameters: dict = {}):
    """Create new automation job"""
    job = AutomationJob(job_type=job_type, parameters=parameters)
    await db.automation_jobs.insert_one(job.dict())
    
    # In a real system, this would trigger the automation engine
    # For demo, we'll simulate job execution
    asyncio.create_task(simulate_job_execution(job.id))
    
    return job

async def simulate_job_execution(job_id: str):
    """Simulate automation job execution"""
    await asyncio.sleep(2)  # Simulate processing time
    
    job = await db.automation_jobs.find_one({"id": job_id})
    if not job:
        return
    
    # Simulate different job types
    if job["job_type"] == "scrape_users":
        # Simulate scraping results
        users = await db.demo_users.find().limit(5).to_list(5)
        results = {
            "scraped_users": len(users),
            "users_data": [{"name": u["name"], "email": u["email"], "role": u["role"]} for u in users]
        }
        logs = [
            "Started browser automation",
            "Navigated to login page", 
            "Entered credentials",
            "Solved MFA challenge",
            "Navigated to users page",
            f"Scraped {len(users)} users successfully"
        ]
    elif job["job_type"] == "provision_user":
        results = {"success": True, "user_created": job["parameters"]}
        logs = [
            "Started provisioning workflow",
            "Navigated to add user page",
            "Filled user form",
            "Submitted form",
            "Verified user creation"
        ]
    else:
        results = {"success": True}
        logs = ["Job completed"]
    
    # Update job status
    await db.automation_jobs.update_one(
        {"id": job_id}, 
        {
            "$set": {
                "status": "completed",
                "results": results,
                "logs": logs,
                "completed_at": datetime.utcnow()
            }
        }
    )

@api_router.get("/automation/jobs")
async def get_automation_jobs():
    """Get automation jobs"""
    jobs = await db.automation_jobs.find().sort("created_at", -1).limit(20).to_list(20)
    return [AutomationJob(**job) for job in jobs]

@api_router.get("/automation/jobs/{job_id}")
async def get_automation_job(job_id: str):
    """Get specific automation job"""
    job = await db.automation_jobs.find_one({"id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return AutomationJob(**job)

# Status check routes (existing)
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

@api_router.get("/")
async def root():
    return {"message": "AI-Driven Web Automation Demo API"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelevel)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    await init_demo_data()
    logger.info("Demo data initialized")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()