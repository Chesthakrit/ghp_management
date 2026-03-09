"""
เครื่องมืออัปเกรดฐานข้อมูลเพื่อรองรับหลายภาษา (Multi-Language Migration Tool)
ไฟล์นี้ใช้สำหรับเพิ่มคอลัมน์ภาษาไทย (_th) และภาษาที่สาม (_v3) ลงในตารางต่างๆ
เช่น ชื่อแผนก, ชื่อตำแหน่ง, คำอธิบายทักษะ เพื่อให้ระบบรองรับการแสดงผลหลายภาษา
"""

from sqlalchemy import create_engine, text
from database import SQLALCHEMY_DATABASE_URL

def migrate():
    """ฟังก์ชันสำหรับรันคำสั่ง SQL เพื่อเพิ่มคอลัมน์ใหม่ในฐานข้อมูล"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    # รายการคำสั่ง SQL สำหรับเพิ่มฟิลด์ภาษาเพิ่มเติม (ตรวจสอบว่ามีคอลัมน์หรือยังก่อนเพิ่ม)
    commands = [
        # ตารางแผนก (Departments)
        "ALTER TABLE departments ADD COLUMN IF NOT EXISTS name_th VARCHAR;",
        "ALTER TABLE departments ADD COLUMN IF NOT EXISTS name_v3 VARCHAR;",
        
        # ตารางตำแหน่งงาน (Job Titles)
        "ALTER TABLE job_titles ADD COLUMN IF NOT EXISTS name_th VARCHAR;",
        "ALTER TABLE job_titles ADD COLUMN IF NOT EXISTS name_v3 VARCHAR;",
        
        # ตารางหมวดหมู่ทักษะ (Duty Categories)
        "ALTER TABLE duty_categories ADD COLUMN IF NOT EXISTS name_th VARCHAR;",
        "ALTER TABLE duty_categories ADD COLUMN IF NOT EXISTS name_v3 VARCHAR;",
        
        # ตารางทักษะหลัก (Duties)
        "ALTER TABLE duties ADD COLUMN IF NOT EXISTS name_th VARCHAR;",
        "ALTER TABLE duties ADD COLUMN IF NOT EXISTS name_v3 VARCHAR;",
        "ALTER TABLE duties ADD COLUMN IF NOT EXISTS description_th VARCHAR;",
        "ALTER TABLE duties ADD COLUMN IF NOT EXISTS description_v3 VARCHAR;",
        
        # ตารางทักษะย่อย (Sub Duties)
        "ALTER TABLE sub_duties ADD COLUMN IF NOT EXISTS name_th VARCHAR;",
        "ALTER TABLE sub_duties ADD COLUMN IF NOT EXISTS name_v3 VARCHAR;",
        
        # ตารางรายละเอียดงาน (Job Descriptions)
        "ALTER TABLE job_descriptions ADD COLUMN IF NOT EXISTS description_th VARCHAR;",
        "ALTER TABLE job_descriptions ADD COLUMN IF NOT EXISTS description_v3 VARCHAR;",
    ]
    
    with engine.connect() as conn:
        for cmd in commands:
            print(f"กำลังรัน: {cmd}")
            try:
                conn.execute(text(cmd))
                conn.commit()
            except Exception as e:
                print(f"เกิดข้อผิดพลาดในการรัน {cmd}: {e}")
    
    print("อัปเกรดฐานข้อมูลรองรับหลายภาษาเรียบร้อย!")

if __name__ == "__main__":
    migrate()

