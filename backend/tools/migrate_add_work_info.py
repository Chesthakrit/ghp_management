"""
Migration script สำหรับ PostgreSQL
เพิ่มคอลัมน์ department, job_title, hire_date, employment_status, termination_date ใน users table
Run: python migrate_add_work_info.py
"""
from sqlalchemy import text
from database import engine

def run_migration():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users'
        """))
        existing_columns = {row[0] for row in result}
        print(f"Existing columns: {existing_columns}")

        new_columns = {
            "department": "VARCHAR",
            "job_title": "VARCHAR",
            "hire_date": "VARCHAR",
            "employment_status": "VARCHAR DEFAULT 'intern'",
            "termination_date": "VARCHAR",
        }

        for col, col_type in new_columns.items():
            if col not in existing_columns:
                conn.execute(text(f"ALTER TABLE users ADD COLUMN {col} {col_type}"))
                print(f"✅ Added column: {col}")
            else:
                print(f"⏭️  Column '{col}' already exists, skipping.")

        conn.commit()
        print("\nMigration complete! No data was lost.")

if __name__ == "__main__":
    run_migration()
