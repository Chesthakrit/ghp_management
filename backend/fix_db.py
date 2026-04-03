from sqlalchemy import text
from database import engine

print("Checking table columns...")
with engine.connect() as conn:
    # Adding columns to existing tables if they don't exist
    try:
        conn.execute(text("ALTER TABLE departments ADD COLUMN IF NOT EXISTS permissions VARCHAR;"))
        print("Ensured Department.permissions column exist.")
    except Exception as e:
        print(f"Error for departments: {e}")
        
    try:
        conn.execute(text("ALTER TABLE job_titles ADD COLUMN IF NOT EXISTS permissions VARCHAR;"))
        print("Ensured JobTitle.permissions column exist.")
    except Exception as e:
        print(f"Error for job_titles: {e}")
    conn.commit()
print("Done!")
