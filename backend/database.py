"""
ไฟล์กำหนดค่าการเชื่อมต่อฐานข้อมูล (Database Configuration)
ใช้ SQLAlchemy สำหรับจัดการฐานข้อมูล PostgreSQL
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- ตั้งค่า URL สำหรับการเชื่อมต่อฐานข้อมูล ---
# รูปแบบ: postgresql://[ชื่อผู้ใช้]:[รหัสผ่าน]@[ที่อยู่โฮสต์]/[ชื่อฐานข้อมูล]
# ในทีนี้ใช้ผู้ใช้ postgres และรหัสผ่าน 1900 เชื่อมต่อไปยังฐานข้อมูล ghp_db ที่เครื่องตัวเอง (localhost)
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1900@localhost/ghp_db"

# สร้างเครื่องยนต์สำหรับเชื่อมต่อ (Engine) 
# เป็นตัวจัดการการติดต่อสื่อสารระดับต่ำกับฐานข้อมูล
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

# สร้าง SessionLocal class
# เมื่อเรียกใช้ จะได้ออบเจกต์สำหรับจัดการ Transaction ของฐานข้อมูล
# บรรทัดนี้ระบุว่ายังไม่ต้องบันทึกข้อมูลอัตโนมัติ (autocommit=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# สร้าง Base Class 
# เป็นคลาสแม่สำหรับคลาส Model อื่นๆ ในโฟลเดอร์ models 
# เพื่อให้ SQLAlchemy ทราบว่าคลาสไหนจะถูกนำไปสร้างเป็นตารางในฐานข้อมูล
Base = declarative_base()

# ฟังก์ชันสำหรับเรียกใช้งาน Database (Dependency Injection)
# จะถูกเรียกใช้ในพาร์ทต่างๆ ของ API เพื่อเปิดและปิดการเชื่อมต่อโดยอัตโนมัติ
def get_db():
    db = SessionLocal() # สร้าง Session ใหม่สำหรับการทำงานหนึ่งรอบ
    try:
        yield db # ส่งคืนค่า session ให้กับผู้เรียกใช้
    finally:
        db.close() # เมื่อทำงานเสร็จสิ้น (ไม่ว่าจะสำเร็จหรือไม่) ให้ปิดการเชื่อมต่อเสมอ
