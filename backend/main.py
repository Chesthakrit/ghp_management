"""
ไฟล์หลักสำหรับการเริ่มต้นระบบ (Main Entry Point)
ตั้งค่า FastAPI, CORS, Static Files และเชื่อมต่อ Router ต่างๆ
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routers import auth, hr, payroll, permissions, projects, users, access_control
from routers.time_attendance_management import logs_router, settings_router, zkteco_router
from routers.attendance_monitoring import monitoring_router

app = FastAPI(title="GHP Management API")

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

# ─── Routers ───────────────────────────────────────────────────────────────────
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(permissions.router)
app.include_router(hr.router)
app.include_router(logs_router)
app.include_router(settings_router)
app.include_router(zkteco_router)
app.include_router(monitoring_router)
app.include_router(payroll.router)
app.include_router(access_control.router)


@app.get("/")
async def root():
    return {"message": "GHP Management System is running."}
