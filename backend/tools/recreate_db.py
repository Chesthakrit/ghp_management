"""
เครื่องมือล้างและสร้างฐานข้อมูลใหม่ (Recreate Database Tool)
ไฟล์นี้ใช้สำหรับ "ล้างข้อมูลทั้งหมด" ในฐานข้อมูลและสร้างตารางขึ้นมาใหม่
พร้อมกับใส่ข้อมูลตั้งต้น (Seed Data) เช่น บทบาท (Roles) และบัญชีแอดมินคนแรก
"""

from sqlalchemy.orm import Session
from database import engine, Base, SessionLocal
from models import users as models
from models import projects as project_models # Import เพื่อให้ SQLAlchemy รับรู้ตาราง projects ตอน Drop/Create
from passlib.context import CryptContext
import json

# ตั้งค่าสำหรับการเข้ารหัสรหัสผ่าน
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def reset_database():
    """ฟังก์ชันหลักสำหรับล้างและตั้งค่าฐานข้อมูลใหม่"""
    print("คำเตือน: ข้อมูลทั้งหมดในฐานข้อมูลจะถูกลบออกถาวร!")
    
    # 1. ลบตารางที่มีอยู่ทั้งหมด
    Base.metadata.drop_all(bind=engine)
    print("ลบตารางเดิมเรียบร้อย.")

    # 2. สร้างตารางทั้งหมดขึ้นมาใหม่ตาม Models ที่นิยามไว้
    Base.metadata.create_all(bind=engine)
    print("สร้างตารางใหม่เรียบร้อย.")

    # 3. สร้างข้อมูลบทบาท (Initial Roles)
    db = SessionLocal()
    
    # สิทธิ์สำหรับแอดมิน (เข้าถึงได้ทุกส่วน)
    admin_perms = [
        "user.view", "user.manage", 
        "role.manage", 
        "project.view_all", "project.delete"
    ]
    role_admin = models.Role(name="admin", permissions=json.dumps(admin_perms))

    # สิทธิ์สำหรับผู้จัดการ (ดูข้อมูลพนักงานและโครงการทั้งหมดได้)
    manager_perms = ["user.view", "project.view_all"]
    role_manager = models.Role(name="manager", permissions=json.dumps(manager_perms))

    # สิทธิ์สำหรับพนักงานทั่วไป (สิทธิ์พื้นฐาน)
    employee_perms = []
    role_employee = models.Role(name="employee", permissions=json.dumps(employee_perms))

    db.add(role_admin)
    db.add(role_manager)
    db.add(role_employee)
    db.commit()
    print("สร้างบทบาท (Roles) พื้นฐานเรียบร้อย.")

    # 4. สร้างบัญชีผู้ดูแลระบบสูงสุด (Master Admin User)
    hashed_password = pwd_context.hash("admin9999")
    admin_user = models.User(
        username="admin",
        password=hashed_password,
        role=role_admin, 
        email="admin@ghp.com",
        first_name="Master",
        last_name="Admin"
    )
    
    db.add(admin_user)
    db.commit()
    print(f"สร้างบัญชี Master Admin เรียบร้อย: username คือ admin / รหัสผ่านคือ admin9999")

    db.close()
    print("เสร็จสิ้นการตั้งค่าฐานข้อมูลใหม่!")

if __name__ == "__main__":
    reset_database()

