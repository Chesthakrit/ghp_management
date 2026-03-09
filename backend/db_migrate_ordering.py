from sqlalchemy import create_engine
import os

DATABASE_URL = "postgresql://postgres:1900@localhost/ghp_db"
engine = create_engine(DATABASE_URL)

def migrate():
    print("Starting migration for job_title sorting...")
    
    with engine.connect() as conn:
        try:
            from sqlalchemy import text
            conn.execute(text("ALTER TABLE job_titles ADD COLUMN display_order INTEGER DEFAULT 100;"))
            conn.commit()
            print("Added 'display_order' column to 'job_titles' table.")
        except Exception as e:
            print(f"Skipping job_titles.display_order: {str(e)[:100]}...")

        conn.close()
    
    print("Migration finished.")

if __name__ == "__main__":
    migrate()
