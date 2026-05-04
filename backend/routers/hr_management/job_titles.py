from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import users as models
from schemas import hr as schemas
import oauth2

router = APIRouter(prefix="/job-titles", tags=["HR - Job Titles"])

@router.get("/", response_model=List[schemas.JobTitle])
def get_job_titles(dept_id: Optional[int] = None, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    """ดึงรายชื่อตำแหน่งงานทั้งหมด (สามารถเลือกกรองตามแผนกได้)"""
    query = db.query(models.JobTitle).order_by(models.JobTitle.display_order.asc())
    if dept_id:
        query = query.filter(models.JobTitle.department_id == dept_id)
    return query.all()

@router.post("/", response_model=schemas.JobTitle)
def create_job_title(
    jt: schemas.JobTitleCreate, 
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    """สร้างตำแหน่งงานใหม่ภายใต้แผนก (เฉพาะ Admin เท่านั้น)"""
    db_jt = models.JobTitle(**jt.dict())
    db.add(db_jt)
    db.commit()
    db.refresh(db_jt)
    return db_jt

@router.put("/reorder", response_model=List[schemas.JobTitle])
def reorder_job_titles(
    payload: schemas.ReorderRequest,
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    """บันทึกลำดับตำแหน่งงานใหม่หลังการ Drag & Drop"""
    for item in payload.items:
        db.query(models.JobTitle).filter(models.JobTitle.id == item.id).update(
            {"display_order": item.display_order}
        )
    db.commit()
    return db.query(models.JobTitle).order_by(models.JobTitle.display_order.asc()).all()

@router.put("/{jt_id}", response_model=schemas.JobTitle)
def update_job_title(
    jt_id: int, 
    jt_update: schemas.JobTitleUpdate, 
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    """แก้ไขข้อมูลตำแหน่งงาน (เฉพาะ Admin)"""
    db_jt = db.query(models.JobTitle).filter(models.JobTitle.id == jt_id).first()
    if not db_jt:
        raise HTTPException(status_code=404, detail="ไม่พบตำแหน่งงาน")
        
    for key, value in jt_update.dict(exclude_unset=True).items():
        setattr(db_jt, key, value)
        
    db.commit()
    db.refresh(db_jt)
    return db_jt

@router.delete("/{jt_id}")
def delete_job_title(
    jt_id: int, 
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    """ลบตำแหน่งงาน (เฉพาะ Admin)"""
    db_jt = db.query(models.JobTitle).filter(models.JobTitle.id == jt_id).first()
    if not db_jt:
        raise HTTPException(status_code=404, detail="ไม่พบตำแหน่งงาน")
    db.delete(db_jt)
    db.commit()
    return {"message": "ลบตำแหน่งงานเรียบร้อย"}

@router.post("/job-descriptions", response_model=schemas.JobDescription)
def create_job_description(
    jd: schemas.JobDescriptionCreate, 
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    """เพิ่มคำอธิบายรายละเอียดงาน (JD) ให้กับตำแหน่งงาน"""
    db_jd = models.JobDescription(**jd.dict())
    db.add(db_jd)
    db.commit()
    db.refresh(db_jd)
    return db_jd

@router.delete("/job-descriptions/{jd_id}")
def delete_job_description(
    jd_id: int, 
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    """ลบรายละเอียดงานที่ไม่ได้ใช้ง่าน"""
    db_jd = db.query(models.JobDescription).filter(models.JobDescription.id == jd_id).first()
    if not db_jd:
        raise HTTPException(status_code=404, detail="ไม่พบข้อมูล")
    db.delete(db_jd)
    db.commit()
    return {"message": "ลบ JD เรียบร้อย"}

@router.put("/{jt_id}/duties", response_model=schemas.JobTitle)
def update_job_title_duties(
    jt_id: int,
    payload: schemas.JobTitleDutiesUpdate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    """กำหนดว่าตำแหน่งงานนี้ จะต้องมีทักษะ/ความรู้เรื่องอะไรบ้าง"""
    db_jt = db.query(models.JobTitle).filter(models.JobTitle.id == jt_id).first()
    if not db_jt:
        raise HTTPException(status_code=404, detail="ไม่พบตำแหน่งงาน")
        
    duties = db.query(models.Duty).filter(models.Duty.id.in_(payload.duty_ids)).all()
    db_jt.duties = duties
    db.commit()
    db.refresh(db_jt)
    return db_jt
