"""
เครื่องมืออัปเกรดฐานข้อมูลเพื่อรองรับการกำหนดเงินเดือน (Salary Migration Tool)
ไฟล์นี้ใช้สำหรับเพิ่มคอลัมน์ salary_type, min_salary, max_salary ลงในตาราง job_titles
"""

import sys
import os

# เพิ่มพาธของโฟลเดอร์หลัก (backend) เพื่อให้เรียกใช้ database ได้
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from database import SQLALCHEMY_DATABASE_URL

def migrate():
    """ฟังก์ชันสำหรับรันคำสั่ง SQL เพื่อเพิ่มคอลัมน์ใหม่ในฐานข้อมูล"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    commands = [
        # ตารางตำแหน่งงาน (Job Titles)
        "ALTER TABLE job_titles ADD COLUMN IF NOT EXISTS salary_type VARCHAR DEFAULT 'monthly';",
        "ALTER TABLE job_titles ADD COLUMN IF NOT EXISTS min_salary INTEGER DEFAULT 0;",
        "ALTER TABLE job_titles ADD COLUMN IF NOT EXISTS max_salary INTEGER DEFAULT 0;",
    ]
    
    with engine.connect() as conn:
        for cmd in commands:
            print(f"กำลังรัน: {cmd}")
            try:
                conn.execute(text(cmd))
                conn.commit()
            except Exception as e:
                print(f"เกิดข้อผิดพลาดในการรัน {cmd}: {e}")
    
    print("อัปเกรดฐานข้อมูลรองรับข้อมูลเงินเดือนเรียบร้อย!")

if __name__ == "__main__":
    migrate()
