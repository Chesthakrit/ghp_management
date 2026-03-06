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

@router.put("/departments/{dept_id}", response_model=schemas.Department)
def update_department(
    dept_id: int, 
    dept_update: schemas.DepartmentUpdate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    if not (current_user.role and current_user.role.name.lower() == 'admin') and not (current_user.username.lower() == 'admin'):
        raise HTTPException(status_code=403, detail="Not authorized")
        
    db_dept = db.query(models.Department).filter(models.Department.id == dept_id).first()
    if not db_dept:
        raise HTTPException(status_code=404, detail="Department not found")
        
    for key, value in dept_update.dict(exclude_unset=True).items():
        setattr(db_dept, key, value)
        
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

@router.put("/job-titles/{jt_id}", response_model=schemas.JobTitle)
def update_job_title(
    jt_id: int, 
    jt_update: schemas.JobTitleUpdate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    if not (current_user.role and current_user.role.name.lower() == 'admin') and not (current_user.username.lower() == 'admin'):
        raise HTTPException(status_code=403, detail="Not authorized")
        
    db_jt = db.query(models.JobTitle).filter(models.JobTitle.id == jt_id).first()
    if not db_jt:
        raise HTTPException(status_code=404, detail="Job title not found")
        
    for key, value in jt_update.dict(exclude_unset=True).items():
        setattr(db_jt, key, value)
        
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

# ─────────────────────────────────────────────
#  Duties (Skill Library)
# ─────────────────────────────────────────────
@router.get("/duties", response_model=List[schemas.Duty])
def get_duties(db: Session = Depends(get_db)):
    return db.query(models.Duty).all()

@router.post("/duties", response_model=schemas.Duty)
def create_duty(
    duty: schemas.DutyCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    if not (current_user.role and current_user.role.name.lower() == 'admin') and not (current_user.username.lower() == 'admin'):
        raise HTTPException(status_code=403, detail="Not authorized")
        
    db_duty = models.Duty(**duty.dict())
    db.add(db_duty)
    db.commit()
    db.refresh(db_duty)
    return db_duty

@router.put("/duties/{duty_id}", response_model=schemas.Duty)
def update_duty(
    duty_id: int, 
    duty_update: schemas.DutyUpdate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    if not (current_user.role and current_user.role.name.lower() == 'admin') and not (current_user.username.lower() == 'admin'):
        raise HTTPException(status_code=403, detail="Not authorized")
        
    db_duty = db.query(models.Duty).filter(models.Duty.id == duty_id).first()
    if not db_duty:
        raise HTTPException(status_code=404, detail="Duty not found")
        
    for key, value in duty_update.dict(exclude_unset=True).items():
        setattr(db_duty, key, value)
        
    db.commit()
    db.refresh(db_duty)
    return db_duty

@router.delete("/duties/{duty_id}")
def delete_duty(
    duty_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    if not (current_user.role and current_user.role.name.lower() == 'admin') and not (current_user.username.lower() == 'admin'):
        raise HTTPException(status_code=403, detail="Not authorized")
        
    db_duty = db.query(models.Duty).filter(models.Duty.id == duty_id).first()
    if not db_duty:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(db_duty)
    db.commit()
    return {"message": "Deleted"}

@router.put("/job-titles/{jt_id}/duties", response_model=schemas.JobTitle)
def update_job_title_duties(
    jt_id: int,
    payload: schemas.JobTitleDutiesUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    if not (current_user.role and current_user.role.name.lower() == 'admin') and not (current_user.username.lower() == 'admin'):
        raise HTTPException(status_code=403, detail="Not authorized")
        
    db_jt = db.query(models.JobTitle).filter(models.JobTitle.id == jt_id).first()
    if not db_jt:
        raise HTTPException(status_code=404, detail="Job title not found")
        
    # Fetch duties
    duties = db.query(models.Duty).filter(models.Duty.id.in_(payload.duty_ids)).all()
    
    # Assign new list of duties (this replaces the old many-to-many relationship)
    db_jt.duties = duties
    db.commit()
    db.refresh(db_jt)
    return db_jt
