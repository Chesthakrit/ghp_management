from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date

from database import get_db
from models import users as models
from schemas import users as schemas
import oauth2

router = APIRouter(prefix="", tags=["User & Personnel"])

@router.get("/{user_id}", response_model=schemas.UserOut)
def read_user(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(oauth2.get_current_user)
):
    """API สำหรับดูรายละเอียดพนักงานหนึ่งคน"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="ไม่พบผู้ใช้งานนี้")
    return user

@router.put("/{user_id}", response_model=schemas.UserOut)
def update_user(
    user_id: int,
    request: schemas.UserUpdate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_edit_user_profile)
):
    """API สำหรับแอดมินแก้ไขข้อมูลพื้นฐานของพนักงาน"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="ไม่พบผู้ใช้งานนี้")

    is_target_admin = (user.role and user.role.name.lower() == 'admin') or (user.username.lower() == 'admin')
    if is_target_admin:
        raise HTTPException(status_code=403, detail="ระบบไม่อนุญาตให้แก้ไขข้อมูล Master Admin ได้ครับ")

    if request.role is not None:
        new_role = db.query(models.Role).filter(models.Role.name == request.role).first()
        if not new_role:
            raise HTTPException(status_code=400, detail=f"ไม่พบสิทธิ์ (Role): {request.role}")
        user.role = new_role

    if request.is_active is not None:
        user.is_active = request.is_active
    if request.first_name is not None:
        user.first_name = request.first_name
    if request.last_name is not None:
        user.last_name = request.last_name
    if request.birth_date is not None:
        user.birth_date = request.birth_date
    if request.phone is not None:
        user.phone = request.phone
    if request.nickname is not None:
        user.nickname = request.nickname
    if request.nationality is not None:
        user.nationality = request.nationality
    if request.id_card_number is not None:
        user.id_card_number = request.id_card_number

    db.commit()
    db.refresh(user)
    return user

@router.put("/{user_id}/profile", response_model=schemas.UserOut)
def update_employee_profile(
    user_id: int,
    request: schemas.EmployeeProfileUpdate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_edit_user_profile)
):
    """API สำหรับแอดมินแก้ไขข้อมูลการจ้างงาน (แผนก, ตำแหน่ง, สถานะ)"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="ไม่พบผู้ใช้งานนี้")

    is_target_admin = (user.role and user.role.name.lower() == 'admin') or (user.username.lower() == 'admin')
    if is_target_admin:
        raise HTTPException(status_code=403, detail="ระบบไม่อนุญาตให้แก้ไขข้อมูล Master Admin ได้ครับ")

    profile = db.query(models.EmployeeProfile).filter(models.EmployeeProfile.user_id == user_id).first()
    if not profile:
        profile = models.EmployeeProfile(user_id=user_id)
        db.add(profile)

    if request.department is not None:
        profile.department = request.department
    if request.job_title is not None:
        profile.job_title = request.job_title
    if request.hire_date is not None:
        profile.hire_date = request.hire_date
    if request.employment_status is not None:
        profile.employment_status = request.employment_status
        if request.employment_status == 'terminated' and profile.termination_date is None:
            profile.termination_date = str(date.today())
        elif request.employment_status != 'terminated':
            profile.termination_date = None
    
    if request.salary_type is not None:
        profile.salary_type = request.salary_type
    if request.base_salary is not None:
        profile.base_salary = request.base_salary
    if request.bank_account is not None:
        profile.bank_account = request.bank_account
    if request.scan_id is not None:
        profile.scan_id = request.scan_id

    db.commit()
    db.refresh(user)
    return user
