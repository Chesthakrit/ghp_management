from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from database import engine, Base
from routers import users, auth, projects, roles, permissions

# --- ส่วนของการนำเข้า Models (เพื่อให้ Database รู้จักตาราง) ---
# เราต้อง import ไฟล์ models เข้ามาเฉยๆ เพื่อให้มันลงทะเบียนกับ Base
from models import users as model_users
from models import projects as model_projects
from fastapi.middleware.cors import CORSMiddleware

# 2. สั่งสร้างตารางทั้งหมด (ใช้ Base ตัวแม่สั่งโดยตรง)
Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- 2. เพิ่มชุดคำสั่งอนุญาต CORS (แปะต่อจาก app = FastAPI() เลย) ---
origins = [
    "http://localhost:5173",         # อนุญาตให้ Vue หน้าบ้านเข้ามาได้
    "http://127.0.0.1:5173",
    "http://192.168.100.13:5173",    # ← มือถือในวง LAN
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(roles.router)
app.include_router(permissions.router)

# Serve uploaded files (photos & id_docs) as static
import os
_uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(_uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=_uploads_dir), name="uploads")

@app.get("/")
async def root():
    return {"message": "GHP System is Running & Projects Table Ready!"}