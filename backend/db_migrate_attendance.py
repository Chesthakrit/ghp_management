from database import engine, Base
from models import users, projects, attendance

def migrate():
    print("Creating attendance tables if they do not exist...")
    # Base.metadata.create_all(bind=engine) will create all tables defined in models
    # Since we imported attendance, its table will be discovered and created
    Base.metadata.create_all(bind=engine)
    print("Migration successful! AttendanceLog table is ready.")

if __name__ == "__main__":
    migrate()
