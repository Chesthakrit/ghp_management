from sqlalchemy import inspect
from database import engine, SessionLocal
from models import users as models
from hashing import Hash

def check_status():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Tables found: {tables}")

    if "roles" not in tables:
        print("CRITICAL: 'roles' table missing! You must run 'python recreate_db.py'")
        return

    db = SessionLocal()
    
    # Check Roles
    roles = db.query(models.Role).all()
    print(f"Roles found: {[r.name for r in roles]}")
    
    if not roles:
        print("CRITICAL: No roles found! You must run 'python recreate_db.py'")
        return

    # Check Admin User
    admin = db.query(models.User).filter(models.User.username == "admin").first()
    if admin:
        print(f"Admin user found: {admin.username}")
        if admin.role:
            print(f"Admin Role: {admin.role.name}")
            print(f"Admin Permissions: {admin.role.permissions}")
        else:
            print("CRITICAL: Admin has no role assigned!")
            
        # Verify Password
        if Hash.verify("admin9999", admin.password):
            print("Password check: OK (admin9999)")
        else:
            print("Password check: FAILED")
    else:
        print("Admin user NOT found.")

    db.close()

if __name__ == "__main__":
    check_status()
