"""
ไฟล์หลักสำหรับการเริ่มต้นระบบ (Main Entry Point)
ตั้งค่า FastAPI, CORS, Static Files และเชื่อมต่อ Router ต่างๆ
"""
import os

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routers import permissions, access_control
from routers.personnel_management import router as users_router
from hashing import Hash
from sqlalchemy.orm import Session
from database import get_db
from models import users as models
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from datetime import datetime, timedelta
from routers.hr_management import router as hr_router
from routers.time_attendance_management import logs_router, settings_router, zkteco_router
from routers.attendance_monitoring import monitoring_router

app = FastAPI(title="GHP Management API")

@app.on_event("startup")
async def startup_event():
    print("\n" + "="*50)
    print("REGISTERED ROUTES:")
    for route in app.routes:
        methods = getattr(route, 'methods', None)
        print(f"Path: {route.path} | Methods: {methods}")
    print("="*50 + "\n")

# ─── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "http://192.168.1.104:5173",
        "http://192.168.1.104:5174",
        "http://192.168.1.104:5175",
        "http://192.168.1.104:5176",
        "http://192.168.1.104:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Static Files ──────────────────────────────────────────────────────────────
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(os.path.join(UPLOAD_DIR, "videos"), exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.include_router(permissions.router)
app.include_router(hr_router)
app.include_router(logs_router)
app.include_router(settings_router)
app.include_router(zkteco_router)
app.include_router(monitoring_router)
app.include_router(access_control.router)

# ─── Auth & Users (Directly in main.py for debugging) ───
SECRET_KEY = "1900"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/auth/login")
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == request.username).first()
    if not user or not Hash.verify(request.password, user.password):
        raise HTTPException(status_code=404, detail="ชื่อผู้ใช้งานหรือรหัสผ่านไม่ถูกต้อง")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

app.include_router(users_router)


@app.get("/")
async def root():
    return {"message": "GHP Management System is running."}

@app.get("/test-refactor")
def test_refactor():
    return {"status": "ok", "message": "Refactor code is active"}
