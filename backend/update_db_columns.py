
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# โหลดค่าจาก .env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def update_database():
    engine = create_engine(DATABASE_URL)
    
    # คำสั่งเพิ่มคอลัมน์ใหม่
    commands = [
        "ALTER TABLE attendance_logs ADD COLUMN IF NOT EXISTS actual_check_in TIMESTAMP;",
        "ALTER TABLE attendance_logs ADD COLUMN IF NOT EXISTS actual_check_out TIMESTAMP;"
    ]
    
    with engine.connect() as conn:
        print("--- Starting Database Update ---")
        for cmd in commands:
            try:
                conn.execute(text(cmd))
                conn.commit()
                print(f"Executed: {cmd}")
            except Exception as e:
                print(f"Error executing {cmd}: {e}")
        print("--- Database Update Finished ---")

if __name__ == "__main__":
    update_database()
