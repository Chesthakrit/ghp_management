from database import engine, Base
from models import users as models

def migrate():
    print("Creating new tables for SubSkills and Checklist Evaluations...")
    # SubDuty and UserSubDutyEvaluation are new
    models.SubDuty.__table__.create(engine, checkfirst=True)
    models.UserSubDutyEvaluation.__table__.create(engine, checkfirst=True)
    print("Migration completed successfully.")

if __name__ == "__main__":
    migrate()
