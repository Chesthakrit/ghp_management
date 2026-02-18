from fastapi import FastAPI
from database import engine, Base # <--- 1. เรียก Base มาจากต้นทางเลย ชัวร์สุด
from routers import users, auth
from routers import users, auth, projects

# --- ส่วนของการนำเข้า Models (เพื่อให้ Database รู้จักตาราง) ---
# เราต้อง import ไฟล์ models เข้ามาเฉยๆ เพื่อให้มันลงทะเบียนกับ Base
from models import users as model_users
from models import projects as model_projects
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # <--- 1. เพิ่มบรรทัดนี้ด้านบนสุด
# ... (imports อื่นๆ เหมือนเดิม)

# 2. สั่งสร้างตารางทั้งหมด (ใช้ Base ตัวแม่สั่งโดยตรง)
Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- 2. เพิ่มชุดคำสั่งอนุญาต CORS (แปะต่อจาก app = FastAPI() เลย) ---
origins = [
    "http://localhost:5173",    # อนุญาตให้ Vue หน้าบ้านเข้ามาได้
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- เชื่อมต่อ Router ---
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(projects.router)

@app.get("/")
async def root():
    return {"message": "GHP System is Running & Projects Table Ready!"}