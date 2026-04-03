import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine
from sqlalchemy import text

def migrate():
    with engine.connect() as conn:
        # Check if the column exists in 'duty_categories'
        result = conn.execute(text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'duty_categories' AND column_name = 'display_order'
        """))
        if result.fetchone():
            print("✅ Column 'display_order' already exists in 'duty_categories'. Skipping.")
        else:
            # Add the column to 'duty_categories'
            conn.execute(text("ALTER TABLE duty_categories ADD COLUMN display_order INTEGER DEFAULT 100"))
            conn.commit()
            print("✅ Added 'display_order' column to 'duty_categories' table successfully!")

if __name__ == "__main__":
    migrate()
