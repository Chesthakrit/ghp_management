"""
ไฟล์จัดการระบบบันทึกเวลาเข้า-ออกงาน (Attendance Router)
ข้อมูลการสแกนถูกส่งเข้าระบบโดยเครื่อง ZKTeco ผ่าน /iclock endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
import oauth2
from database import get_db
from models import attendance as models
from schemas import attendance as schemas

router = APIRouter(
    prefix="/attendance",
    tags=["Attendance System"]
)


@router.get("/ot-rules")
def get_ot_rules(db: Session = Depends(get_db)):
    """
    Helper endpoint สำหรับดึงค่า Config ทั้งหมดมาไว้ในรูปแบบ Dict
    ใช้สำหรับคำนวณหน้าจอในฝั่ง Frontend
    """
    configs = db.query(models.AttendanceConfig).all()
    return {c.key: c.value for c in configs}


@router.get("/debug-version")
def debug_version():
    return {"version": "1.0.1", "status": "OT routes should be active"}



@router.get("/me", response_model=list[schemas.AttendanceLogResponse])
def get_my_attendance(
    db: Session = Depends(get_db),
    current_user = Depends(oauth2.get_current_user)
):
    """
    ดึงประวัติการเข้า-ออกงานทั้งหมด ของตัวพนักงานเอง
    นำไปทำ History Calendar พร้อมข้อมูล OT
    """
    logs = db.query(models.AttendanceLog).filter(models.AttendanceLog.user_id == current_user.id).order_by(models.AttendanceLog.date.desc()).all()
    return logs
        
    return logs


def check_time_permission(user, action_perm=None):
    """ตรวจสอบสิทธิ์การจัดการเวลา (รองรับสิทธิ์แอดมิตและรายบุคคล)"""
    is_admin = (user.role and user.role.name.lower() == 'admin') or (user.username.lower() == 'admin')
    perms = user.permissions or []

    # ถ้าเป็น Admin ให้ผ่านทุกกรณี
    if is_admin:
        return True

    # หากไม่ใช่แอดมิน ต้องมีสิทธิ์เข้าหน้า Time & Leave
    if 'page.time_leave' not in perms:
         raise HTTPException(status_code=403, detail="ไม่มีสิทธิ์เข้าถึงข้อมูลส่วนนี้")
    
    # เช็คสิทธิ์การกระทำเฉพาะเจาะจง (ถ้ามีระบุ)
    if action_perm and action_perm not in perms:
        raise HTTPException(status_code=403, detail=f"คุณไม่มีสิทธิ์ทำรายการนี้: {action_perm}")

    return True


@router.get("/user/{user_id}", response_model=list[schemas.AttendanceLogResponse])
def get_user_attendance(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(oauth2.get_current_user)
):
    """
    ดึงประวัติการเข้างาน (Security: เฉพาะเจ้าของข้อมุล หรือ Admin/HR เท่านั้น)
    """
    # 1. ถ้าไม่ใช่เจ้าของข้อมูล ต้องเช็คสิทธิ์ Admin/HR
    if current_user.id != user_id:
        check_time_permission(current_user) # ฟังก์ชันนี้จะคัดกรองสิทธิ์ให้
            
    logs = db.query(models.AttendanceLog).filter(models.AttendanceLog.user_id == user_id).order_by(models.AttendanceLog.date.desc()).all()
    return logs

