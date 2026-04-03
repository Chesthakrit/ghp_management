from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import users as models
from schemas import users as schemas
import oauth2

router = APIRouter(
    prefix="/access-control",
    tags=["Access Control"]
)

@router.get("/users-with-access", response_model=List[dict])
def get_users_with_individual_access(db: Session = Depends(get_db), admin: models.User = Depends(oauth2.check_can_manage_access)):
    """ดึงรายชื่อผู้ใช้ทั้งหมดที่มีการกำหนดสิทธิ์การเข้าถึงหน้าเว็บเป็นรายบุคคล"""
    access_list = db.query(models.UserPageAccess).all()
    # ดึงรายชื่อ User IDs ที่ไม่ซ้ำกัน
    user_ids = set([a.user_id for a in access_list])
    
    users = db.query(models.User).filter(models.User.id.in_(user_ids)).all()
    result = []
    for u in users:
        # ดึงว่าแต่ละคนเข้าถึงหน้าไหนได้บ้าง
        u_access = [a for a in access_list if a.user_id == u.id]
        result.append({
            "id": u.id,
            "username": u.username,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "page_access": [{"page_id": a.page_id, "can_edit": a.can_edit} for a in u_access]
        })
    return result

@router.post("/grant", status_code=201)
def grant_page_access(user_id: int, page_id: str, can_edit: bool = False, db: Session = Depends(get_db), admin: models.User = Depends(oauth2.check_can_manage_access)):
    """มอบสิทธิ์การเข้าถึงหน้าเว็บให้กับ User ID ที่ระบุรายบุคคล"""
    # ตรวจสอบว่ามี User นี้อยู่จริงหรือไม่
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="ไม่พบผู้ใช้งาน")
        
    # ลบสิทธิ์เดิมของหน้านั้นออกก่อน (ถ้ามี)
    db.query(models.UserPageAccess).filter(models.UserPageAccess.user_id == user_id, models.UserPageAccess.page_id == page_id).delete()
    
    # เพิ่มสิทธิ์ใหม่
    new_access = models.UserPageAccess(user_id=user_id, page_id=page_id, can_edit=can_edit)
    db.add(new_access)
    db.commit()
    return {"message": f"มอบสิทธิ์การเข้าถึง {page_id} ให้กับ User ID {user_id} เรียบร้อยแล้ว"}

@router.delete("/revoke")
def revoke_page_access(user_id: int, page_id: str, db: Session = Depends(get_db), admin: models.User = Depends(oauth2.check_can_manage_access)):
    """ดึงสิทธิ์การเข้าถึงหน้าเว็บคืนจาก User ID ที่ระบุ"""
    access = db.query(models.UserPageAccess).filter(models.UserPageAccess.user_id == user_id, models.UserPageAccess.page_id == page_id).first()
    if not access:
        raise HTTPException(status_code=404, detail="ไม่พบข้อมูลสิทธิ์เข้าใช้งานนี้")
        
    db.delete(access)
    db.commit()
    return {"message": "ดึงสิทธิ์คืนเรียบร้อยแล้ว"}

@router.get("/user/{user_id}", response_model=List[dict])
def get_user_page_access(user_id: int, db: Session = Depends(get_db), admin: models.User = Depends(oauth2.check_can_manage_access)):
    """ดึงรายการสิทธิ์การเข้าถึงหน้าเว็บทั้งหมดของผู้ใช้งานรายบุคคล"""
    access_list = db.query(models.UserPageAccess).filter(models.UserPageAccess.user_id == user_id).all()
    return [{"page_id": a.page_id, "can_edit": a.can_edit} for a in access_list]
