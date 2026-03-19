"""
Migration: เพิ่มคอลัมน์ tutorial_url ให้กับตาราง sub_duties
สำหรับเก็บลิงก์วิดีโอสอนของแต่ละสกิลย่อย
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine
from sqlalchemy import text

def migrate():
    with engine.connect() as conn:
        # เช็คว่ามีคอลัมน์อยู่แล้วหรือไม่
        result = conn.execute(text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'sub_duties' AND column_name = 'tutorial_url'
        """))
        if result.fetchone():
            print("✅ Column 'tutorial_url' already exists in 'sub_duties'. Skipping.")
            return
        
        # เพิ่มคอลัมน์
        conn.execute(text("ALTER TABLE sub_duties ADD COLUMN tutorial_url VARCHAR NULL"))
        conn.commit()
        print("✅ Added 'tutorial_url' column to 'sub_duties' table successfully!")

if __name__ == "__main__":
    migrate()
