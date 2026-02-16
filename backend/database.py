from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- ตั้งค่าการเชื่อมต่อ ---
# รูปแบบ: postgresql://USER:PASSWORD@HOST/DATABASE_NAME
# ตรง 'รหัสผ่านของช่างกิ๊บ' ให้ใส่รหัสผ่านที่คุณตั้งไว้ตอนลง PostgreSQL นะครับ
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1900@localhost/ghp_db"

# สร้างเครื่องยนต์สำหรับเชื่อมต่อ (Engine)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

# สร้าง Session (ตัวจัดการช่วงเวลาการใช้งาน)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# สร้าง Base Class (แม่พิมพ์สำหรับสร้างตารางต่างๆ ในอนาคต)
Base = declarative_base()

# ฟังก์ชันสำหรับเรียกใช้งาน Database (Dependency)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()