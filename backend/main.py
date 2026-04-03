"""
ไฟล์หลักสำหรับการเริ่มต้นระบบ (Main Entry Point)
ทำหน้าที่ตั้งค่า FastAPI, CORS, Static Files และเชื่อมต่อ Router ต่างๆ เข้าด้วยกัน
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routers import attendance, auth, hr, payroll, permissions, projects, users, access_control

# สร้างอินสแตนซ์ของ FastAPI
app = FastAPI()

# --- 1. การกำหนดค่า CORS (เปิดกว้างสำหรับการทดสอบบนมือถือ) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
app.include_router(access_control.router)

@app.get("/")
async def root():
    return {"message": "GHP System is Running (PostgreSQL Mode)"}
