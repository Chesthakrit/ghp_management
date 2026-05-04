from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import users as models
from schemas import hr as schemas
import oauth2

router = APIRouter(prefix="/departments", tags=["HR - Departments"])

@router.get("/", response_model=List[schemas.Department])
def get_departments(db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    """ดึงรายชื่อแผนกทั้งหมดที่มีในบริษัท (เรียงตาม display_order)"""
    return db.query(models.Department).order_by(models.Department.display_order.asc()).all()

@router.post("/", response_model=schemas.Department)
def create_department(
    dept: schemas.DepartmentCreate, 
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    """เพิ่มแผนกใหม่ (เฉพาะ Admin เท่านั้น)"""
    db_dept = models.Department(**dept.dict())
    db.add(db_dept)
    db.commit()
    db.refresh(db_dept)
    return db_dept

@router.put("/reorder", response_model=List[schemas.Department])
def reorder_departments(
    payload: schemas.ReorderRequest,
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    """บันทึกลำดับแผนกใหม่หลังการ Drag & Drop"""
    for item in payload.items:
        db.query(models.Department).filter(models.Department.id == item.id).update(
            {"display_order": item.display_order}
        )
    db.commit()
    return db.query(models.Department).order_by(models.Department.display_order.asc()).all()

@router.put("/{dept_id}", response_model=schemas.Department)
def update_department(
    dept_id: int,
    dept: schemas.DepartmentUpdate, 
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    """แก้ไขข้อมูลพื้นฐานของแผนก (เช่น เปลี่ยนชื่อพิกัดแผนก หรือสิทธิ์ส่วนกลาง)"""
    db_dept = db.query(models.Department).filter(models.Department.id == dept_id).first()
    if not db_dept:
        raise HTTPException(status_code=404, detail="Department not found")
        
    update_data = dept.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_dept, key, value)
        
    db.commit()
    db.refresh(db_dept)
    return db_dept

@router.delete("/{dept_id}")
def delete_department(
    dept_id: int, 
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    """ลบแผนก (เฉพาะ Admin เท่านั้น)"""
    db_dept = db.query(models.Department).filter(models.Department.id == dept_id).first()
    if not db_dept:
        raise HTTPException(status_code=404, detail="ไม่พบแผนก")
    db.delete(db_dept)
    db.commit()
    return {"message": "ลบแผนกเรียบร้อยแล้า"}
