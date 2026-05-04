"""
Module สำหรับระบบติดตามการเข้างานรายวัน (Attendance Monitoring / Dashboard)
ทำหน้าที่ดึงข้อมูลสถานะพนักงานทุกคนในวันปัจจุบัน
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
import oauth2
from database import get_db
from models import attendance as models
from schemas import attendance as schemas
from models import users as user_models

router = APIRouter(
    prefix="/attendance-monitoring",
    tags=["Attendance Monitoring"]
)

@router.get("/today")
def get_today_attendance(
    db: Session = Depends(get_db),
    current_user = Depends(oauth2.get_current_user)
):
    """
    ดึงข้อมูลการเข้างานของพนักงานทุกคน เฉพาะวันนี้
    สำหรับแสดงผลใน Monitoring Dashboard
    """
    check_monitoring_permission(current_user)
    
    today = date.today()
    
    # 1. ดึงพนักงานทั้งหมด (ไม่เอา Admin และพนักงานที่ลาออก)
    users = db.query(user_models.User).join(user_models.EmployeeProfile).outerjoin(user_models.Role).filter(
        user_models.User.username != 'admin',
        user_models.EmployeeProfile.employment_status != 'terminated'
    ).all()
    
    # 2. ดึง Attendance Logs ของวันนี้
    logs = db.query(models.AttendanceLog).filter(models.AttendanceLog.date == today).all()
    log_map = {log.user_id: log for log in logs}
    
    results = []
    for u in users:
        log = log_map.get(u.id)
        
        results.append({
            "user_id": u.id,
            "username": u.username,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "photo_path": u.photo_path,
            "job_title": u.employee_profile.job_title if u.employee_profile else None,
            "attendance": schemas.AttendanceLogResponse.from_orm(log) if log else None
        })
        
    return results

def check_monitoring_permission(user):
    """ตรวจสอบสิทธิ์การเข้าดู Monitoring Dashboard"""
    is_admin = (user.role and user.role.name.lower() == 'admin') or (user.username.lower() == 'admin')
    perms = user.permissions or []

    if is_admin:
        return True

    if 'page.attendance_dash' not in perms:
         raise HTTPException(status_code=403, detail="ไม่มีสิทธิ์เข้าถึงข้อมูลส่วนนี้")

    return True
