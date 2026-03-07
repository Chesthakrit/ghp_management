import sys
import os
# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import users as models
from models import projects # Ensure Project model is loaded

def seed_hr_data():
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(models.Department).count() > 0:
            print("HR data already seeded.")
            return

        print("Seeding initial HR data...")
        
        dept_data = {
            'office':       ['Admin', 'Accounting', 'Purchasing', 'Manager', 'Supervisor'],
            'draftman':     ['Master Draftman', 'Senior Draftman', 'Junior Draftman'],
            'production':   ['QC', 'CNC-Edge', 'Custom', 'Packing'],
            'installation': ['Supervisor', 'Installer', 'Assistant'],
            'management':   ['CEO'],
        }
        
        dept_labels = {
            'office': 'Office',
            'draftman': 'Draftman',
            'production': 'Production',
            'installation': 'Installation',
            'management': 'Management'
        }

        for value, titles in dept_data.items():
            name = dept_labels[value]
            dept = models.Department(name=name, value=value)
            db.add(dept)
            db.flush() # Get ID
            
            for title in titles:
                jt = models.JobTitle(name=title, department_id=dept.id)
                db.add(jt)
        
        db.commit()
        print("Success!")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_hr_data()
