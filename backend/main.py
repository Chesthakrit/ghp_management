import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from models import users as model_users
from models import projects as model_projects
from routers import users, auth, projects, roles, permissions, hr

app = FastAPI()

# --- 1. CORS Configuration ---
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://192.168.1.104:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. Static Files (Uploads) ---
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# --- 3. Routes ---
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(roles.router)
app.include_router(permissions.router)
app.include_router(hr.router)

@app.get("/")
async def root():
    return {"message": "GHP System is Running (PostgreSQL Mode)"}