from sqlalchemy.orm import Session
from database import engine, Base, SessionLocal
from models import users as models
from models import projects as project_models # Import to ensure projects table is dropped
from passlib.context import CryptContext
import json

# Setup Hash
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def reset_database():
    print("WARNING: This will delete all data in the database!")
    
    # 1. Drop all tables
    Base.metadata.drop_all(bind=engine)
    print("Tables dropped.")

    # 2. Create all tables
    Base.metadata.create_all(bind=engine)
    print("Tables created.")

    # 3. Seed Initial Roles
    db = SessionLocal()
    
    # Role: Admin (All Permissions)
    admin_perms = [
        "user.view", "user.manage", 
        "role.manage", 
        "project.view_all", "project.delete"
    ]
    role_admin = models.Role(name="admin", permissions=json.dumps(admin_perms))

    # Role: Manager (Some Permissions)
    manager_perms = ["user.view", "project.view_all"]
    role_manager = models.Role(name="manager", permissions=json.dumps(manager_perms))

    # Role: Employee (Basic Permissions)
    employee_perms = []
    role_employee = models.Role(name="employee", permissions=json.dumps(employee_perms))

    db.add(role_admin)
    db.add(role_manager)
    db.add(role_employee)
    db.commit()
    print("Roles created.")

    # 4. Seed Master Admin User
    hashed_password = pwd_context.hash("admin9999")
    admin_user = models.User(
        username="admin",
        password=hashed_password,
        role=role_admin, # Link object directly
        email="admin@ghp.com",
        first_name="Master",
        last_name="Admin"
    )
    
    db.add(admin_user)
    db.commit()
    print(f"Master Admin created: admin / admin9999 (Role: {role_admin.name})")

    db.close()
    print("Database reset complete.")

if __name__ == "__main__":
    reset_database()
