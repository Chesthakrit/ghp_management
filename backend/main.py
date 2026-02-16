from fastapi import FastAPI
from database import engine, Base # <--- 1. เรียก Base มาจากต้นทางเลย ชัวร์สุด
from routers import users, auth
from routers import users, auth, projects

# --- ส่วนของการนำเข้า Models (เพื่อให้ Database รู้จักตาราง) ---
# เราต้อง import ไฟล์ models เข้ามาเฉยๆ เพื่อให้มันลงทะเบียนกับ Base
from models import users as model_users
from models import projects as model_projects

# 2. สั่งสร้างตารางทั้งหมด (ใช้ Base ตัวแม่สั่งโดยตรง)
Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- เชื่อมต่อ Router ---
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(projects.router)

@app.get("/")
async def root():
    return {"message": "GHP System is Running & Projects Table Ready!"}