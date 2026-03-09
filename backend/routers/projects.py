"""
ไฟล์จัดการข้อมูลโครงการหรือโปรเจกต์ (Projects Router)
ทำหน้าที่จัดการการสร้างโปรเจกต์ใหม่ และการดึงข้อมูลโครงการที่ผู้ใช้รับผิดชอบ
"""

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
    current_user: user_models.User = Depends(oauth2.get_current_user) # ต้อง Login ก่อนถึงจะสร้างได้
):
    """API สำหรับบันทึกข้อมูลโครงการใหม่เข้าระบบ"""
    
    # สร้าง Obj โปรเจกต์ใหม่ โดยดึง ID ผู้สร้างมาจาก Token ของคนที่ Login อยู่ (current_user)
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

# --- 2. ดูรายชื่อโปรเจกต์ที่รับผิดชอบ (Read All) ---
@router.get("/", response_model=List[schemas.ProjectOut])
def get_my_projects(
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(oauth2.get_current_user)
):
    """API สำหรับดึงรายการโครงการที่ผู้ใช้เกี่ยวข้อง หรือดูทั้งหมดหากเป็นแอดมิน"""
    
    # ตรวจสอบสิทธิ์: หากเป็นแอดมิน (admin) หรือมีสิทธิ์ 'project.view_all' ให้เห็นทุกโปรเจกต์ในระบบ
    is_admin = (current_user.role and current_user.role.name.lower() == 'admin') or (current_user.username.lower() == 'admin')
    
    if is_admin or "project.view_all" in current_user.permissions:
        # แอดมินดูได้ทั้งหมด
        projects = db.query(models.Project).all()
    else:
        # พนักงานปกติ เห็นเฉพาะโครงการที่ตัวเองเป็นเจ้าของ (Owner) เท่านั้น
        projects = db.query(models.Project).filter(models.Project.owner_id == current_user.id).all()
    
    return projects
