from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import projects as models
from models import users as user_models
from schemas import projects as schemas
import oauth2

router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)

# --- 1. สร้างโปรเจกต์ใหม่ (Create) ---
@router.post("/", response_model=schemas.ProjectOut)
def create_project(
    request: schemas.ProjectCreate, 
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(oauth2.get_current_user) # ต้อง Login ก่อน
):
    # สร้างงานใหม่ โดยดึง ID คนสร้างมาจาก current_user (ไม่ต้องกรอกเอง)
    new_project = models.Project(
        name=request.name,
        customer=request.customer,
        description=request.description,
        due_date=request.due_date,
        owner_id=current_user.id 
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

# --- 2. ดูโปรเจกต์ทั้งหมดของฉัน (Read All) ---
@router.get("/", response_model=List[schemas.ProjectOut])
def get_my_projects(
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(oauth2.get_current_user)
):
    # ดึงเฉพาะงานที่ owner_id ตรงกับคน Login (งานคนอื่นไม่เห็น)
    projects = db.query(models.Project).filter(models.Project.owner_id == current_user.id).all()
    return projects