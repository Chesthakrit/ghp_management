import sys
import os

# Add parent directory to path to import database module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from database import SQLALCHEMY_DATABASE_URL

def migrate():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    commands = [
        # Add new dual salary columns
        "ALTER TABLE job_titles ADD COLUMN IF NOT EXISTS min_salary_monthly INTEGER DEFAULT 0;",
        "ALTER TABLE job_titles ADD COLUMN IF NOT EXISTS max_salary_monthly INTEGER DEFAULT 0;",
        "ALTER TABLE job_titles ADD COLUMN IF NOT EXISTS min_salary_daily INTEGER DEFAULT 0;",
        "ALTER TABLE job_titles ADD COLUMN IF NOT EXISTS max_salary_daily INTEGER DEFAULT 0;",
        
        # Drop old single columns (optional, but cleaner)
        # We keep them for safety if you want, but for dual support we use the new ones.
        # "ALTER TABLE job_titles DROP COLUMN IF EXISTS salary_type;",
        # "ALTER TABLE job_titles DROP COLUMN IF EXISTS min_salary;",
        # "ALTER TABLE job_titles DROP COLUMN IF EXISTS max_salary;"
    ]
    
    with engine.connect() as conn:
        for cmd in commands:
            print(f"Executing: {cmd}")
            try:
                conn.execute(text(cmd))
                conn.commit()
            except Exception as e:
                print(f"Error executing {cmd}: {e}")
    
    print("Database migration for dual salary support complete!")

if __name__ == "__main__":
    migrate()
