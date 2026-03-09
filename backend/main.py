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
from routers import users, auth, projects, permissions, hr

# สร้างอินสแตนซ์ของ FastAPI
app = FastAPI()

# --- 1. การกำหนดค่า CORS (Cross-Origin Resource Sharing) ---
# ระบุ URL ของ Frontend ที่อนุญาตให้เชื่อมต่อกับ Backend นี้ได้
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://192.168.100.13:5173",
]

# เพิ่ม Middleware เพื่อจัดการเรื่องความปลอดภัยในการเรียกใช้ข้ามโดเมน
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # อนุญาต Origin ตามรายการด้านบน
    allow_credentials=True,     # อนุญาตให้ส่ง Cookies หรือ Authentication Headers ได้
    allow_methods=["*"],        # อนุญาตการส่งคำขอทุกรูปแบบ (GET, POST, PUT, DELETE ฯลฯ)
    allow_headers=["*"],        # อนุญาต Headers ทุกประเภท
)

# --- 2. ตั้งค่าการเก็บและเข้าถึงไฟล์ Static (เช่น ไฟล์รูปภาพที่อัปโหลด) ---
# กำหนดโฟลเดอร์สำหรับเก็บไฟล์อัปโหลด
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
# ตรวจสอบว่าถ้ายังไม่มีโฟลเดอร์ uploads ให้สร้างขึ้นมา
os.makedirs(UPLOAD_DIR, exist_ok=True)
# เชื่อมต่อ URL /uploads ให้ชี้ไปที่โฟลเดอร์ uploads ในเครื่อง
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# --- 3. การรวมพาร์ท (Routes) ของแต่ละโมดูลเข้ามาไว้ที่เดียว ---
# ลงทะเบียน API Router จากไฟล์ต่างๆ
app.include_router(users.router)       # เกี่ยวกับผู้ใช้งาน
app.include_router(auth.router)        # เกี่ยวกับการล็อกอินและยืนยันตัวตน
app.include_router(projects.router)    # เกี่ยวกับโครงการ
app.include_router(permissions.router) # เกี่ยวกับสิทธิ์การเข้าถึง
app.include_router(hr.router)          # เกี่ยวกับฝ่ายบุคคลและทักษะพนักงาน

# หน้าแรกของ API สำหรับทดสอบสถานะระบบ
@app.get("/")
async def root():
    return {"message": "GHP System is Running (PostgreSQL Mode)"}
