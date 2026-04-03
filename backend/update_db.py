from database import engine, Base
from models import users, projects # Import all modules to ensure they are registered with Base

print("Syncing database schema...")
Base.metadata.create_all(bind=engine)
print("Done! All tables created/updated.")
