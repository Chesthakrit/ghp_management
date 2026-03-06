import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import users as models
from models import projects # Ensure Project model is loaded

def verify():
    db = SessionLocal()
    try:
        depts = db.query(models.Department).all()
        print(f"Found {len(depts)} departments.")
        for d in depts:
            titles = db.query(models.JobTitle).filter(models.JobTitle.department_id == d.id).all()
            print(f" - {d.name}: {len(titles)} titles")
    finally:
        db.close()

if __name__ == "__main__":
    verify()
