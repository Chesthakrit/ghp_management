from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean, JSON, ForeignKey
import os

# Database Connection
DATABASE_URL = "postgresql://postgres:1900@localhost/ghp_db"
engine = create_engine(DATABASE_URL)
metadata = MetaData()

def migrate():
    print("Starting migration...")
    
    # 1. Add 'permissions' to 'users' table if not exists (as JSON column)
    with engine.connect() as conn:
        try:
            from sqlalchemy import text
            conn.execute(text("ALTER TABLE users ADD COLUMN permissions TEXT;"))
            conn.commit()
            print("Added 'permissions' column to 'users' table.")
        except Exception as e:
            print(f"Skipping users.permissions: {str(e)[:100]}...")

        # 2. Add 'job_title_id' to 'employee_profiles'
        try:
            conn.execute(text("ALTER TABLE employee_profiles ADD COLUMN job_title_id INTEGER REFERENCES job_titles(id);"))
            conn.commit()
            print("Added 'job_title_id' to 'employee_profiles' table.")
        except Exception as e:
            print(f"Skipping employee_profiles.job_title_id: {str(e)[:100]}...")

        conn.close()
    
    print("Migration finished.")

if __name__ == "__main__":
    migrate()
