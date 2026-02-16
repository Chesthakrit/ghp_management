from sqlalchemy import Column, Integer, String, Boolean, Enum
from database import Base
import enum
from sqlalchemy.orm import relationship
# สร้างตัวเลือกสำหรับ Role (ตำแหน่ง) เพื่อป้องกันการกรอกผิด
class UserRole(str, enum.Enum):
    admin = "admin"           # ผู้ดูแลระบบสูงสุด
    employee = "employee"     # พนักงานทั่วไป
    customer = "customer"     # ลูกค้า

class User(Base):
    __tablename__ = "users"   # ชื่อตารางใน Database

    # --- กำหนดคอลัมน์ (Columns) ---
    id = Column(Integer, primary_key=True, index=True)  # รหัสประจำตัว (Run อัตโนมัติ 1, 2, 3...)
    username = Column(String, unique=True, index=True)  # ชื่อผู้ใช้ (ห้ามซ้ำ)
    password = Column(String)                           # รหัสผ่าน (เดี๋ยวเราจะเข้ารหัสก่อนเก็บ)
    email = Column(String, unique=True, index=True)     # อีเมล
    role = Column(String, default="employee")           # ตำแหน่ง (ค่าเริ่มต้นเป็นพนักงาน)
    is_active = Column(Boolean, default=True)           # สถานะ (True=ใช้งานได้, False=โดนแบน)
    # เพื่อบอกว่า User 1 คน มีได้หลาย Project
    projects = relationship("Project", back_populates="owner")