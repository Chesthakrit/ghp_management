"""
Migration: สร้างตาราง employee_profiles
เพิ่ม EmployeeProfile ให้กับ users ที่มีอยู่แล้ว

Run: python migrate_employee_profiles.py
"""
from sqlalchemy import text
from database import engine, SessionLocal
from models.users import EmployeeProfile, User

def run_migration():
    # 1. สร้างตาราง employee_profiles (ถ้ายังไม่มี)
    from database import Base
    from models import users  # import เพื่อให้ Base รู้จัก model ทั้งหมด
    from models import projects

    Base.metadata.create_all(bind=engine, checkfirst=True)
    print("✅ Tables created (if not existed)")

    # 2. สร้าง EmployeeProfile สำหรับ user ที่ยังไม่มี profile
    db = SessionLocal()
    try:
        users_list = db.query(User).all()
        created = 0
        for user in users_list:
            existing = db.query(EmployeeProfile).filter(
                EmployeeProfile.user_id == user.id
            ).first()
            if not existing:
                profile = EmployeeProfile(user_id=user.id)
                db.add(profile)
                created += 1
        db.commit()
        print(f"✅ Created {created} empty EmployeeProfile(s) for existing users")
    finally:
        db.close()

    print("\nMigration complete!")

if __name__ == "__main__":
    run_migration()
