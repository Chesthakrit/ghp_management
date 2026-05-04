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

# ─── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    # 1. เช็คว่ามี Admin ในระบบหรือยัง (ถ้าไม่มีให้สร้างตัวตั้งต้นให้)
    admin_user = db.query(models.User).filter(models.User.username == "admin").first()
    if not admin_user and request.username == "admin" and request.password == "admin9999":
        # สร้าง Role admin ก่อน
        admin_role = db.query(models.Role).filter(models.Role.name == "admin").first()
        if not admin_role:
            admin_role = models.Role(name="admin", permissions='["*"]')
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
            
        new_admin = models.User(
            username="admin",
            password=Hash.bcrypt("admin9999"),
            role_id=admin_role.id,
            first_name="Master",
            last_name="Admin",
            is_active=True
        )
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
        admin_user = new_admin

    # 2. ตรวจสอบการ Login ปกติ
    user = db.query(models.User).filter(models.User.username == request.username).first()
    if not user or not Hash.verify(request.password, user.password):
        # เปลี่ยนเป็น 401 เพื่อให้แยกจาก 404 (Route Not Found)
        raise HTTPException(status_code=401, detail="ชื่อผู้ใช้งานหรือรหัสผ่านไม่ถูกต้อง")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

app.include_router(users_router)


@app.get("/")
async def root():
    return {"message": "GHP Management System is running."}
