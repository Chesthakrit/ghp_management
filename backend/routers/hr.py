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
#  Duty Categories (Skill Tags)
# ─────────────────────────────────────────────
@router.get("/duty-categories", response_model=List[schemas.DutyCategory])
def get_duty_categories(db: Session = Depends(get_db)):
    return db.query(models.DutyCategory).all()

@router.post("/duty-categories", response_model=schemas.DutyCategory)
def create_duty_category(
    cat: schemas.DutyCategoryCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    if not (current_user.role and current_user.role.name.lower() == 'admin') and not (current_user.username.lower() == 'admin'):
        raise HTTPException(status_code=403, detail="Not authorized")
        
    db_cat = models.DutyCategory(**cat.dict())
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat

@router.put("/duty-categories/{cat_id}", response_model=schemas.DutyCategory)
def update_duty_category(
    cat_id: int,
    cat_update: schemas.DutyCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    if not (current_user.role and current_user.role.name.lower() == 'admin') and not (current_user.username.lower() == 'admin'):
        raise HTTPException(status_code=403, detail="Not authorized")
        
    db_cat = db.query(models.DutyCategory).filter(models.DutyCategory.id == cat_id).first()
    if not db_cat:
        raise HTTPException(status_code=404, detail="Category not found")
        
    for key, value in cat_update.dict(exclude_unset=True).items():
        setattr(db_cat, key, value)
        
    db.commit()
    db.refresh(db_cat)
    return db_cat

@router.delete("/duty-categories/{cat_id}")
def delete_duty_category(
    cat_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    if not (current_user.role and current_user.role.name.lower() == 'admin') and not (current_user.username.lower() == 'admin'):
        raise HTTPException(status_code=403, detail="Not authorized")
        
    db_cat = db.query(models.DutyCategory).filter(models.DutyCategory.id == cat_id).first()
    if not db_cat:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(db_cat)
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

# ─────────────────────────────────────────────
#  Sub-Duties (Skill Checklist Items)
# ─────────────────────────────────────────────
@router.post("/sub-duties", response_model=schemas.SubDuty)
def create_sub_duty(
    sub_duty: schemas.SubDutyCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    if not (current_user.role and current_user.role.name.lower() == 'admin') and not (current_user.username.lower() == 'admin'):
        raise HTTPException(status_code=403, detail="Not authorized")
        
    db_sub = models.SubDuty(**sub_duty.dict())
    db.add(db_sub)
    db.commit()
    db.refresh(db_sub)
    return db_sub

@router.delete("/sub-duties/{sub_id}")
def delete_sub_duty(
    sub_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    if not (current_user.role and current_user.role.name.lower() == 'admin') and not (current_user.username.lower() == 'admin'):
        raise HTTPException(status_code=403, detail="Not authorized")
        
    db_sub = db.query(models.SubDuty).filter(models.SubDuty.id == sub_id).first()
    if not db_sub:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(db_sub)
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

# ─────────────────────────────────────────────
#  Skill Evaluations
# ─────────────────────────────────────────────
@router.get("/evaluations/{user_id}", response_model=List[schemas.UserDutyEvaluation])
def get_user_evaluations(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    # Only self or admin/manager can view
    is_admin = (current_user.role and current_user.role.name.lower() == 'admin') or (current_user.username.lower() == 'admin')
    if not is_admin and current_user.id != user_id:
        # Check permission for non-admins
        if 'user.manage' not in current_user.permissions:
            raise HTTPException(status_code=403, detail="Not authorized")
        
    return db.query(models.UserDutyEvaluation).filter(models.UserDutyEvaluation.user_id == user_id).all()

@router.post("/evaluations", response_model=schemas.UserDutyEvaluation)
def save_user_evaluation(
    eval_req: schemas.UserDutyEvaluationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    # Only admin/manager can evaluate
    is_admin = (current_user.role and current_user.role.name.lower() == 'admin') or (current_user.username.lower() == 'admin')
    if not is_admin and 'user.manage' not in current_user.permissions:
        raise HTTPException(status_code=403, detail="Not authorized to evaluate skills")

    from datetime import datetime
    
    # Check if exists
    db_eval = db.query(models.UserDutyEvaluation).filter(
        models.UserDutyEvaluation.user_id == eval_req.user_id,
        models.UserDutyEvaluation.duty_id == eval_req.duty_id
    ).first()
    
    if db_eval:
        db_eval.score = eval_req.score
        db_eval.evaluated_by_id = current_user.id
        db_eval.updated_at = datetime.now().isoformat()
    else:
        db_eval = models.UserDutyEvaluation(
            **eval_req.dict(),
            evaluated_by_id=current_user.id,
            updated_at=datetime.now().isoformat()
        )
        db.add(db_eval)

    db.commit()
    db.refresh(db_eval)
    return db_eval

# ─────────────────────────────────────────────
#  Sub-Skill Checklist Evaluations
# ─────────────────────────────────────────────
@router.get("/sub-evaluations/{user_id}", response_model=List[schemas.UserSubDutyEvaluation])
def get_user_sub_evaluations(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.UserSubDutyEvaluation).filter(models.UserSubDutyEvaluation.user_id == user_id).all()

@router.post("/sub-evaluations", response_model=schemas.UserSubDutyEvaluation)
def save_user_sub_evaluation(
    eval_req: schemas.UserSubDutyEvaluationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    # Only admin/manager can check/uncheck
    is_admin = (current_user.role and current_user.role.name.lower() == 'admin') or (current_user.username.lower() == 'admin')
    if not is_admin and 'user.manage' not in current_user.permissions:
        raise HTTPException(status_code=403, detail="Not authorized to manage checklists")

    from datetime import datetime
    
    db_eval = db.query(models.UserSubDutyEvaluation).filter(
        models.UserSubDutyEvaluation.user_id == eval_req.user_id,
        models.UserSubDutyEvaluation.sub_duty_id == eval_req.sub_duty_id
    ).first()
    
    if db_eval:
        db_eval.is_completed = eval_req.is_completed
        db_eval.updated_at = datetime.now().isoformat()
    else:
        db_eval = models.UserSubDutyEvaluation(
            **eval_req.dict(),
            updated_at=datetime.now().isoformat()
        )
        db.add(db_eval)

    db.commit()
    db.refresh(db_eval)
    return db_eval
