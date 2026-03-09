import sys
import os

# Add parent directory to path to import database module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from database import SQLALCHEMY_DATABASE_URL

def migrate():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    commands = [
        "ALTER TABLE employee_profiles ADD COLUMN IF NOT EXISTS salary_type VARCHAR DEFAULT 'monthly';"
    ]
    
    with engine.connect() as conn:
        for cmd in commands:
            print(f"Executing: {cmd}")
            try:
                conn.execute(text(cmd))
                conn.commit()
            except Exception as e:
                print(f"Error executing {cmd}: {e}")
    
    print("Database migration for EmployeeProfile dual salary support complete!")

if __name__ == "__main__":
    migrate()
