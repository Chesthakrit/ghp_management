from sqlalchemy import create_engine, text
from database import SQLALCHEMY_DATABASE_URL

def migrate():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    commands = [
        # Departments
        "ALTER TABLE departments ADD COLUMN IF NOT EXISTS name_th VARCHAR;",
        "ALTER TABLE departments ADD COLUMN IF NOT EXISTS name_v3 VARCHAR;",
        
        # Job Titles
        "ALTER TABLE job_titles ADD COLUMN IF NOT EXISTS name_th VARCHAR;",
        "ALTER TABLE job_titles ADD COLUMN IF NOT EXISTS name_v3 VARCHAR;",
        
        # Duty Categories
        "ALTER TABLE duty_categories ADD COLUMN IF NOT EXISTS name_th VARCHAR;",
        "ALTER TABLE duty_categories ADD COLUMN IF NOT EXISTS name_v3 VARCHAR;",
        
        # Duties
        "ALTER TABLE duties ADD COLUMN IF NOT EXISTS name_th VARCHAR;",
        "ALTER TABLE duties ADD COLUMN IF NOT EXISTS name_v3 VARCHAR;",
        "ALTER TABLE duties ADD COLUMN IF NOT EXISTS description_th VARCHAR;",
        "ALTER TABLE duties ADD COLUMN IF NOT EXISTS description_v3 VARCHAR;",
        
        # Sub Duties
        "ALTER TABLE sub_duties ADD COLUMN IF NOT EXISTS name_th VARCHAR;",
        "ALTER TABLE sub_duties ADD COLUMN IF NOT EXISTS name_v3 VARCHAR;",
        
        # Job Descriptions
        "ALTER TABLE job_descriptions ADD COLUMN IF NOT EXISTS description_th VARCHAR;",
        "ALTER TABLE job_descriptions ADD COLUMN IF NOT EXISTS description_v3 VARCHAR;",
    ]
    
    with engine.connect() as conn:
        for cmd in commands:
            print(f"Executing: {cmd}")
            try:
                conn.execute(text(cmd))
                conn.commit()
            except Exception as e:
                print(f"Error executing {cmd}: {e}")
    
    print("Migration completed!")

if __name__ == "__main__":
    migrate()
