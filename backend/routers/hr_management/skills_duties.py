from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import users as models
from schemas import hr as schemas
import oauth2

router = APIRouter(prefix="/skills", tags=["HR - Skills & Duties"])

# ─────────────────────────────────────────────
#  หมวดหมู่ทักษะ (Skill Categories / Tags)
# ─────────────────────────────────────────────

@router.get("/categories", response_model=List[schemas.DutyCategory])
def get_duty_categories(db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    """ดึงหมวดหมู่ทักษะทั้งหมด"""
    return db.query(models.DutyCategory).order_by(models.DutyCategory.display_order.asc()).all()

@router.post("/categories", response_model=schemas.DutyCategory)
def create_duty_category(
    cat: schemas.DutyCategoryCreate, 
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    """เพิ่มหมวดหมู่ทักษะใหม่"""
    db_cat = models.DutyCategory(**cat.dict())
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat

@router.put("/categories/reorder", response_model=List[schemas.DutyCategory])
def reorder_duty_categories(
    payload: schemas.ReorderRequest,
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    for item in payload.items:
        db.query(models.DutyCategory).filter(models.DutyCategory.id == item.id).update(
            {"display_order": item.display_order}
        )
    db.commit()
    return db.query(models.DutyCategory).order_by(models.DutyCategory.display_order.asc()).all()

@router.put("/categories/{cat_id}", response_model=schemas.DutyCategory)
def update_duty_category(
    cat_id: int,
    cat_update: schemas.DutyCategoryUpdate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    db_cat = db.query(models.DutyCategory).filter(models.DutyCategory.id == cat_id).first()
    if not db_cat:
        raise HTTPException(status_code=404, detail="ไม่พบหมวดหมู่")
    for key, value in cat_update.dict(exclude_unset=True).items():
        setattr(db_cat, key, value)
    db.commit()
    db.refresh(db_cat)
    return db_cat

@router.delete("/categories/{cat_id}")
def delete_duty_category(
    cat_id: int, 
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    db_cat = db.query(models.DutyCategory).filter(models.DutyCategory.id == cat_id).first()
    if not db_cat:
        raise HTTPException(status_code=404, detail="ไม่พบข้อมูล")
    db.delete(db_cat)
    db.commit()
    return {"message": "ลบหมวดหมู่เรียบร้อย"}

# ─────────────────────────────────────────────
#  คลังทักษะหลัก (Duties / Skill Library)
# ─────────────────────────────────────────────

@router.get("/duties", response_model=List[schemas.Duty])
def get_duties(db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    """ดึงรายชื่อทักษะ (Skill) ทั้งหมดที่มีในระบบ"""
    return db.query(models.Duty).order_by(models.Duty.display_order.asc()).all()

@router.post("/duties", response_model=schemas.Duty)
def create_duty(
    duty: schemas.DutyCreate, 
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    db_duty = models.Duty(**duty.dict())
    db.add(db_duty)
    db.commit()
    db.refresh(db_duty)
    return db_duty

@router.put("/duties/reorder", response_model=List[schemas.Duty])
def reorder_duties(
    payload: schemas.ReorderRequest,
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    try:
        for item in payload.items:
            db.query(models.Duty).filter(models.Duty.id == item.id).update(
                {"display_order": item.display_order}
            )
        db.commit()
        return db.query(models.Duty).order_by(models.Duty.display_order.asc()).all()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/duties/{duty_id}", response_model=schemas.Duty)
def get_duty(duty_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    db_duty = db.query(models.Duty).filter(models.Duty.id == duty_id).first()
    if not db_duty:
        raise HTTPException(status_code=404, detail="ไม่พบทักษะ")
    return db_duty

@router.put("/duties/{duty_id}", response_model=schemas.Duty)
def update_duty(
    duty_id: int, 
    duty_update: schemas.DutyUpdate, 
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    db_duty = db.query(models.Duty).filter(models.Duty.id == duty_id).first()
    if not db_duty:
        raise HTTPException(status_code=404, detail="ไม่พบทักษะ")
    for key, value in duty_update.dict(exclude_unset=True).items():
        setattr(db_duty, key, value)
    db.commit()
    db.refresh(db_duty)
    return db_duty

@router.delete("/duties/{duty_id}")
def delete_duty(
    duty_id: int, 
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    db_duty = db.query(models.Duty).filter(models.Duty.id == duty_id).first()
    if not db_duty:
        raise HTTPException(status_code=404, detail="ไม่พบข้อมูล")
    db.delete(db_duty)
    db.commit()
    return {"message": "ลบทักษะเรียบร้อย"}

# ─────────────────────────────────────────────
#  ทักษะปลีกย่อย (Sub-Duties / Checklist Items)
# ─────────────────────────────────────────────

@router.post("/sub-duties", response_model=schemas.SubDuty)
def create_sub_duty(
    sub_duty: schemas.SubDutyCreate, 
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    db_sub = models.SubDuty(**sub_duty.dict())
    db.add(db_sub)
    db.commit()
    db.refresh(db_sub)
    return db_sub

@router.put("/sub-duties/reorder", response_model=List[schemas.SubDuty])
def reorder_sub_duties(
    payload: schemas.ReorderRequest,
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    try:
        for item in payload.items:
            db_obj = db.query(models.SubDuty).filter(models.SubDuty.id == item.id).first()
            if db_obj:
                db_obj.display_order = item.display_order
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    return db.query(models.SubDuty).order_by(models.SubDuty.display_order.asc()).all()

@router.put("/sub-duties/{sub_id}", response_model=schemas.SubDuty)
def update_sub_duty(
    sub_id: int,
    update: schemas.SubDutyUpdate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    db_sub = db.query(models.SubDuty).filter(models.SubDuty.id == sub_id).first()
    if not db_sub:
        raise HTTPException(status_code=404, detail="ไม่พบทักษะย่อย")
    for key, value in update.dict(exclude_unset=True).items():
        setattr(db_sub, key, value)
    db.commit()
    db.refresh(db_sub)
    return db_sub

@router.delete("/sub-duties/{sub_id}")
def delete_sub_duty(
    sub_id: int, 
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    db_sub = db.query(models.SubDuty).filter(models.SubDuty.id == sub_id).first()
    if not db_sub:
        raise HTTPException(status_code=404, detail="ไม่พบข้อมูล")
    db.delete(db_sub)
    db.commit()
    return {"message": "ลบเรียบร้อย"}
