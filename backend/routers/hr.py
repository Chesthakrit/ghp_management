from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import users as models
from schemas import hr as schemas
import oauth2

router = APIRouter(
    prefix="/hr",
    tags=["HR Management"]
)

# ─────────────────────────────────────────────
#  Departments
# ─────────────────────────────────────────────
@router.get("/departments", response_model=List[schemas.Department])
def get_departments(db: Session = Depends(get_db)):
    return db.query(models.Department).all()

@router.post("/departments", response_model=schemas.Department)
def create_department(
    dept: schemas.DepartmentCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    # Only admin can manage master data
    if not (current_user.role and current_user.role.name.lower() == 'admin') and not (current_user.username.lower() == 'admin'):
        raise HTTPException(status_code=403, detail="Not authorized")
        
    db_dept = models.Department(**dept.dict())
    db.add(db_dept)
    db.commit()
    db.refresh(db_dept)
    return db_dept

@router.delete("/departments/{dept_id}")
def delete_department(
    dept_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    if not (current_user.role and current_user.role.name.lower() == 'admin') and not (current_user.username.lower() == 'admin'):
        raise HTTPException(status_code=403, detail="Not authorized")
        
    db_dept = db.query(models.Department).filter(models.Department.id == dept_id).first()
    if not db_dept:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(db_dept)
    db.commit()
    return {"message": "Deleted"}

# ─────────────────────────────────────────────
#  Job Titles
# ─────────────────────────────────────────────
@router.get("/job-titles", response_model=List[schemas.JobTitle])
def get_job_titles(dept_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(models.JobTitle)
    if dept_id:
        query = query.filter(models.JobTitle.department_id == dept_id)
    return query.all()

@router.post("/job-titles", response_model=schemas.JobTitle)
def create_job_title(
    jt: schemas.JobTitleCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    if not (current_user.role and current_user.role.name.lower() == 'admin') and not (current_user.username.lower() == 'admin'):
        raise HTTPException(status_code=403, detail="Not authorized")
        
    db_jt = models.JobTitle(**jt.dict())
    db.add(db_jt)
    db.commit()
    db.refresh(db_jt)
    return db_jt

@router.delete("/job-titles/{jt_id}")
def delete_job_title(
    jt_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    if not (current_user.role and current_user.role.name.lower() == 'admin') and not (current_user.username.lower() == 'admin'):
        raise HTTPException(status_code=403, detail="Not authorized")
        
    db_jt = db.query(models.JobTitle).filter(models.JobTitle.id == jt_id).first()
    if not db_jt:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(db_jt)
    db.commit()
    return {"message": "Deleted"}

# ─────────────────────────────────────────────
#  Job Descriptions
# ─────────────────────────────────────────────
@router.post("/job-descriptions", response_model=schemas.JobDescription)
def create_job_description(
    jd: schemas.JobDescriptionCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    if not (current_user.role and current_user.role.name.lower() == 'admin') and not (current_user.username.lower() == 'admin'):
        raise HTTPException(status_code=403, detail="Not authorized")
        
    db_jd = models.JobDescription(**jd.dict())
    db.add(db_jd)
    db.commit()
    db.refresh(db_jd)
    return db_jd

@router.delete("/job-descriptions/{jd_id}")
def delete_job_description(
    jd_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    if not (current_user.role and current_user.role.name.lower() == 'admin') and not (current_user.username.lower() == 'admin'):
        raise HTTPException(status_code=403, detail="Not authorized")
        
    db_jd = db.query(models.JobDescription).filter(models.JobDescription.id == jd_id).first()
    if not db_jd:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(db_jd)
    db.commit()
    return {"message": "Deleted"}
