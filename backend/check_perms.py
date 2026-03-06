
from database import SessionLocal
from models.users import User, Role
import json

db = SessionLocal()
try:
    print("--- ROLES ---")
    roles = db.query(Role).all()
    for r in roles:
        print(f"ID: {r.id}, Name: {r.name}, Permissions: {r.permissions}")

    print("\n--- USERS ---")
    users = db.query(User).all()
    for u in users:
        role_name = u.role.name if u.role else "None"
        print(f"ID: {u.id}, Username: {u.username}, Role: {role_name}, Permissions (calculated): {u.permissions}")

finally:
    db.close()
