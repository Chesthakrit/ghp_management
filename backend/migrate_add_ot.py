from sqlalchemy import create_engine, text
from database import SQLALCHEMY_DATABASE_URL

def add_ot_column():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    with engine.connect() as conn:
        print("Checking if 'ot' column exists in attendance_logs table...")
        # Check if column exists
        result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='attendance_logs' AND column_name='ot'"))
        if not result.fetchone():
            print("Adding 'ot' column to attendance_logs table...")
            conn.execute(text("ALTER TABLE attendance_logs ADD COLUMN ot FLOAT DEFAULT 0.0"))
            conn.commit()
            print("Column 'ot' added successfully.")
        else:
            print("Column 'ot' already exists.")

if __name__ == "__main__":
    add_ot_column()
