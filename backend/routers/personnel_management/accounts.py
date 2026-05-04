from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import os

from database import get_db
from models import users as models
from schemas import users as schemas
import oauth2

router = APIRouter(prefix="", tags=["User & Personnel"])

@router.get("/", response_model=List[schemas.UserOut])
def get_all_users(db: Session = Depends(get_db), admin: models.User = Depends(oauth2.check_can_manage_users)):
    """API สำหรับดึงรายชื่อพนักงานทุกคนในระบบ"""
    users = db.query(models.User).all()
    users.sort(key=lambda u: (0 if (u.role and u.role.name == 'admin') else 1, u.id))
    return users

@router.get("/me", response_model=schemas.UserOut)
def read_users_me(current_user: models.User = Depends(oauth2.get_current_user)):
    """API สำหรับดึงข้อมูลของตัวเอง"""
    return current_user

@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_delete_user)
):
    """API สำหรับแอดมินลบผู้ใช้งานออกจากระบบอย่างถาวร"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="ไม่พบผู้ใช้งานนี้")

    if user.username == 'admin':
        raise HTTPException(status_code=403, detail="ไม่สามารถลบบัญชี Master Admin ได้")

    from sqlalchemy.exc import ProgrammingError
    try:
        db.query(models.UserDutyEvaluation).filter(
            models.UserDutyEvaluation.evaluated_by_id == user_id
        ).update({"evaluated_by_id": None})
        db.query(models.UserPageAccess).filter(models.UserPageAccess.user_id == user_id).delete()
    except ProgrammingError:
        db.rollback()

    profile = db.query(models.EmployeeProfile).filter(models.EmployeeProfile.user_id == user_id).first()
    if profile:
        db.delete(profile)

    def remove_file(relative_path: str):
        if not relative_path:
            return
        full_path = os.path.join(os.path.dirname(__file__), "..", "..", relative_path)
        full_path = os.path.normpath(full_path)
        try:
            if os.path.isfile(full_path):
                os.remove(full_path)
        except OSError:
            pass

    remove_file(user.photo_path)
    remove_file(user.id_doc_path)

    db.delete(user)
    db.commit()
    return
