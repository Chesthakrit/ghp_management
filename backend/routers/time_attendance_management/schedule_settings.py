"""
ไฟล์จัดการการตั้งค่าระบบบันทึกเวลา (Attendance Settings Router)
จัดการค่าคอนฟิก, วันหยุด และสถานที่เช็คอิน
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import oauth2
from database import get_db
from models import attendance as models
from schemas import attendance as schemas

router = APIRouter(
    prefix="/attendance",
    tags=["Attendance Settings"]
)

@router.get("/ot-rules")
def get_ot_rules(db: Session = Depends(get_db)):
    """
    Helper endpoint สำหรับดึงค่า Config ทั้งหมดมาไว้ในรูปแบบ Dict
    ใช้สำหรับคำนวณหน้าจอในฝั่ง Frontend
    """
    configs = db.query(models.AttendanceConfig).all()
    return {c.key: c.value for c in configs}

@router.get("/settings", response_model=list[schemas.AttendanceConfigResponse])
def get_attendance_configs(db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    check_time_permission(current_user)
    return db.query(models.AttendanceConfig).all()

@router.put("/settings", response_model=list[schemas.AttendanceConfigResponse])
def update_attendance_configs(
    configs: list[schemas.AttendanceConfigUpdate],
    db: Session = Depends(get_db),
    current_user = Depends(oauth2.get_current_user)
):
    # Determine the required granular permission based on the keys being updated
    keys = [c.key for c in configs]
    required_perm = None
    if any(k in ['check_in_time', 'check_out_time', 'late_grace_period_mins'] for k in keys):
        required_perm = 'action.time.edit_hours'
    elif any(k.startswith('quota_') for k in keys):
        required_perm = 'action.time.edit_leave'
    
    check_time_permission(current_user, required_perm)
    
    for cfg in configs:
        db_cfg = db.query(models.AttendanceConfig).filter(models.AttendanceConfig.key == cfg.key).first()
        if db_cfg:
            db_cfg.value = cfg.value
        else:
            db_cfg = models.AttendanceConfig(key=cfg.key, value=cfg.value)
            db.add(db_cfg)
    db.commit()
    return db.query(models.AttendanceConfig).all()

@router.get("/holidays/{year}", response_model=list[schemas.CompanyHolidayResponse])
def get_holidays_by_year(year: int, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    check_time_permission(current_user)
    return db.query(models.CompanyHoliday).filter(models.CompanyHoliday.year == year).order_by(models.CompanyHoliday.date).all()

@router.post("/holidays", response_model=schemas.CompanyHolidayResponse)
def create_holiday(
    holiday: schemas.CompanyHolidayCreate,
    db: Session = Depends(get_db),
    current_user = Depends(oauth2.get_current_user)
):
    check_time_permission(current_user, 'action.time.edit_holiday')
    db_holiday = models.CompanyHoliday(
        year=holiday.year,
        date=holiday.date,
        name=holiday.name,
        is_active=True
    )
    db.add(db_holiday)
    db.commit()
    db.refresh(db_holiday)
    return db_holiday

@router.delete("/holidays/{holiday_id}")
def delete_holiday(
    holiday_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(oauth2.get_current_user)
):
    check_time_permission(current_user, 'action.time.edit_holiday')
    db_holiday = db.query(models.CompanyHoliday).filter(models.CompanyHoliday.id == holiday_id).first()
    if not db_holiday:
        raise HTTPException(status_code=404, detail="Holiday not found")
    db.delete(db_holiday)
    db.commit()
    return {"message": "Deleted successfully"}

@router.put("/holidays/{holiday_id}", response_model=schemas.CompanyHolidayResponse)
def update_holiday(
    holiday_id: int,
    holiday: schemas.CompanyHolidayCreate,
    db: Session = Depends(get_db),
    current_user = Depends(oauth2.get_current_user)
):
    check_time_permission(current_user, 'action.time.edit_holiday')
    db_holiday = db.query(models.CompanyHoliday).filter(models.CompanyHoliday.id == holiday_id).first()
    if not db_holiday:
        raise HTTPException(status_code=404, detail="Holiday not found")
    db_holiday.year = holiday.year
    db_holiday.date = holiday.date
    db_holiday.name = holiday.name
    db.commit()
    db.refresh(db_holiday)
    return db_holiday

@router.get("/locations", response_model=list[schemas.AttendanceLocationResponse])
def get_locations(db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    """ดึงรายการสถานที่เช็คอินทั้งหมด"""
    check_time_permission(current_user)
    return db.query(models.AttendanceLocation).all()

@router.post("/locations", response_model=schemas.AttendanceLocationResponse)
def create_location(
    loc_data: schemas.AttendanceLocationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(oauth2.get_current_user)
):
    """เพิ่มสถานที่เช็คอินใหม่ (Fixed/Onsite)"""
    check_time_permission(current_user, 'action.time.edit_location')
    new_loc = models.AttendanceLocation(**loc_data.dict())
    db.add(new_loc)
    db.commit()
    db.refresh(new_loc)
    return new_loc

@router.delete("/locations/{loc_id}")
def delete_location(
    loc_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(oauth2.get_current_user)
):
    """ลบสถานที่เช็คอิน"""
    check_time_permission(current_user, 'action.time.edit_location')
    db_loc = db.query(models.AttendanceLocation).filter(models.AttendanceLocation.id == loc_id).first()
    if not db_loc:
        raise HTTPException(status_code=404, detail="Location not found")
    db.delete(db_loc)
    db.commit()
    return {"message": "Location deleted"}

def check_time_permission(user, action_perm=None):
    """ตรวจสอบสิทธิ์การจัดการเวลา (รองรับสิทธิ์แอดมินและรายบุคคล)"""
    is_admin = (user.role and user.role.name.lower() == 'admin') or (user.username.lower() == 'admin')
    perms = user.permissions or []

    if is_admin:
        return True

    if 'page.time_leave' not in perms:
         raise HTTPException(status_code=403, detail="ไม่มีสิทธิ์เข้าถึงข้อมูลส่วนนี้")
    
    if action_perm and action_perm not in perms:
        raise HTTPException(status_code=403, detail=f"คุณไม่มีสิทธิ์ทำรายการนี้: {action_perm}")

    return True
