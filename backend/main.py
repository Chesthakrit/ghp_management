"""
ไฟล์หลัก (Main Entry Point) สำหรับรันแอปพลิเคชัน FastAPI
"""

import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# นำเข้าโมดูลฐานข้อมูลและโมดูลอื่นๆ ที่เกี่ยวข้อง
from database import engine, Base
from models import users as model_users
from models import projects as model_projects
from models import payroll as model_payroll
from routers import users, auth, projects, permissions, hr, attendance, payroll

# สร้างอินสแตนซ์ของ FastAPI
app = FastAPI()

# --- 1. การกำหนดค่า CORS (Cross-Origin Resource Sharing) ---
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://192.168.1.104:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. ตั้งค่าการเก็บและเข้าถึงไฟล์ Static ---
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# จัดการโฟลเดอร์วิดีโอ (ตอนนี้ย้ายไปใช้ Protected Route ใน hr.py เพื่อความปลอดภัยสูงสุด)
VIDEO_DIR = os.path.join(UPLOAD_DIR, "videos")
os.makedirs(VIDEO_DIR, exist_ok=True)

# --- 3. การรวมพาร์ท (Routes) ---
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(permissions.router)
app.include_router(hr.router)
app.include_router(attendance.router)
app.include_router(payroll.router)

@app.get("/")
async def root():
    return {"message": "GHP System is Running (PostgreSQL Mode)"}
