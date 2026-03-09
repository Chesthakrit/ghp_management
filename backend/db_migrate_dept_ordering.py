from sqlalchemy import create_engine
import os

DATABASE_URL = "postgresql://postgres:1900@localhost/ghp_db"
engine = create_engine(DATABASE_URL)

def migrate():
    print("Starting migration for dept & job_titles ordering...")
    from sqlalchemy import text

    # ใช้ connection แยกกันสำหรับแต่ละ ALTER เพื่อป้องกัน transaction abort cascade
    for table, col in [("departments", "display_order"), ("job_titles", "display_order")]:
        with engine.connect() as conn:
            try:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} INTEGER DEFAULT 100;"))
                conn.commit()
                print(f"Added '{col}' column to '{table}' table.")
            except Exception as e:
                conn.rollback()
                print(f"Skipping {table}.{col}: {str(e)[:100]}...")
    
    print("Migration finished.")

if __name__ == "__main__":
    migrate()
