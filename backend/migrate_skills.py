from database import engine, Base
from models import users

print("Creating new tables for duties and the many-to-many relationship...")
Base.metadata.create_all(bind=engine)
print("Finished creating tables.")
