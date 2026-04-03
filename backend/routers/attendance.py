"""
ไฟล์จัดการระบบบันทึกเวลาเข้า-ออกงาน (Attendance Router)
รองรับการ Check-in, Check-out และการดูประวัติการลงเวลา
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import date, datetime
import oauth2
from database import get_db
from models import attendance as models
from schemas import attendance as schemas

router = APIRouter(
    prefix="/attendance",
    tags=["Attendance System"]
)

@router.post("/check-in", response_model=schemas.AttendanceLogResponse)
def check_in(
    request: Request,
    check_in_data: schemas.AttendanceCheckIn,
    db: Session = Depends(get_db),
    current_user = Depends(oauth2.get_current_user)
):
    """
    บันทึกเวลาเข้างาน (Check-in)
    รับข้อมูล พิกัด GPS, ประเภทการเข้างาน (On-Site/Factory), รูปถ่าย
    """
    today = date.today()
    
    # ตรวจสอบว่าวันนี้มีการเข้างานไปหรือยัง (เพื่อให้เช็คอินได้แค่วันละ 1 Record)
    existing_log = db.query(models.AttendanceLog).filter(
        models.AttendanceLog.user_id == current_user.id,
        models.AttendanceLog.date == today
    ).first()

    if existing_log:
        raise HTTPException(status_code=400, detail="คุณได้ทำการ Check-in สำหรับวันนี้ไปแล้ว")

    # ดึง IP Address (มีประโยชน์มากถ้าเช็คอินด้วยเน็ตโรงงาน)
    client_ip = request.client.host if request.client else None

    # สร้าง Record ใหม่ในตาราง attendance_logs
    new_attendance = models.AttendanceLog(
        user_id=current_user.id,
        date=today,
        check_in_time=datetime.now(),
        check_in_type=check_in_data.check_in_type,
        location_lat=check_in_data.location_lat,
        location_lon=check_in_data.location_lon,
        site_name=check_in_data.site_name,
        ip_address=client_ip,
        check_in_image=check_in_data.check_in_image,
        note=check_in_data.note,
        status="present" # ค่าเริ่มต้น (ค่อยเขียนลอจิกเช็คสายทีหลัง)
    )

    db.add(new_attendance)
    db.commit()
    db.refresh(new_attendance)
    return new_attendance


@router.put("/check-out", response_model=schemas.AttendanceLogResponse)
def check_out(
    check_out_data: schemas.AttendanceCheckOut,
    db: Session = Depends(get_db),
    current_user = Depends(oauth2.get_current_user)
):
    """
    บันทึกเวลาเลิกงาน (Check-out)
    จะไปอัปเดตช่อง check_out_time ของรายการที่ได้เปิดไว้เมื่อเช้า
    """
    today = date.today()
    
    # ค้นหารายการเช็คอินของวันนี้
    log = db.query(models.AttendanceLog).filter(
        models.AttendanceLog.user_id == current_user.id,
        models.AttendanceLog.date == today
    ).first()

    if not log:
        raise HTTPException(status_code=400, detail="ไม่พบประวัติการ Check-in ของวันนี้ โปรด Check-in ก่อน")
    
    if log.check_out_time:
        raise HTTPException(status_code=400, detail="คุณได้ทำการ Check-out ไปแล้ว")

    log.check_out_time = datetime.now()
    if check_out_data.check_out_image:
        log.check_out_image = check_out_data.check_out_image

    db.commit()
    db.refresh(log)
    return log


@router.get("/me", response_model=list[schemas.AttendanceLogResponse])
def get_my_attendance(
    db: Session = Depends(get_db),
    current_user = Depends(oauth2.get_current_user)
):
    """
    ดึงประวัติการเข้า-ออกงานทั้งหมด ของตัวพนักงานเอง
    นำไปทำ History Calendar
    """
    return db.query(models.AttendanceLog).filter(models.AttendanceLog.user_id == current_user.id).order_by(models.AttendanceLog.date.desc()).all()


@router.get("/user/{user_id}", response_model=list[schemas.AttendanceLogResponse])
def get_user_attendance(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(oauth2.get_current_user)
):
    """
    ดึงประวัติการเข้า-ออกงานของพนักงานระบุบุคคล (สำหรับ Admin/HR)
    """
    if current_user.id != user_id:
        is_admin = (current_user.role and current_user.role.name.lower() == 'admin') or (current_user.username.lower() == 'admin')
        perms = current_user.permissions or []
        if not is_admin and 'user.manage' not in perms and 'page.usermanagement' not in perms:
            raise HTTPException(status_code=403, detail="ไม่มีสิทธิ์ดูข้อมูลลงเวลาของผู้อื่น")
            
    return db.query(models.AttendanceLog).filter(models.AttendanceLog.user_id == user_id).order_by(models.AttendanceLog.date.desc()).all()


@router.get("/today", response_model=schemas.AttendanceLogResponse)
def get_today_status(
    db: Session = Depends(get_db),
    current_user = Depends(oauth2.get_current_user)
):
    """
    เช็คสถานะวันของวันนี้ (มาหรือยัง? กลับหรือยัง?)
    เอาไว้เปลี่ยนปุ่มจากสีเขียว (Check-in) เป็นส้ม (Check-out) หน้าแอป
    """
    today = date.today()
    log = db.query(models.AttendanceLog).filter(
        models.AttendanceLog.user_id == current_user.id,
        models.AttendanceLog.date == today
    ).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="No record today")
    return log

# --- SETTINGS & PUBLIC HOLIDAYS ---
def check_admin_or_hr(user):
    is_admin = (user.role and user.role.name.lower() == 'admin') or (user.username.lower() == 'admin')
    perms = user.permissions or []
    if not is_admin and 'page.hr' not in perms:
        raise HTTPException(status_code=403, detail="Not authorized to manage settings")


@router.get("/settings", response_model=list[schemas.AttendanceConfigResponse])
def get_attendance_configs(db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    check_admin_or_hr(current_user)
    return db.query(models.AttendanceConfig).all()


@router.put("/settings", response_model=list[schemas.AttendanceConfigResponse])
def update_attendance_configs(
    configs: list[schemas.AttendanceConfigUpdate],
    db: Session = Depends(get_db),
    current_user = Depends(oauth2.get_current_user)
):
    check_admin_or_hr(current_user)
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
    return db.query(models.CompanyHoliday).filter(models.CompanyHoliday.year == year).order_by(models.CompanyHoliday.date).all()


@router.post("/holidays", response_model=schemas.CompanyHolidayResponse)
def create_holiday(
    holiday: schemas.CompanyHolidayCreate,
    db: Session = Depends(get_db),
    current_user = Depends(oauth2.get_current_user)
):
    check_admin_or_hr(current_user)
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
    check_admin_or_hr(current_user)
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
    check_admin_or_hr(current_user)
    db_holiday = db.query(models.CompanyHoliday).filter(models.CompanyHoliday.id == holiday_id).first()
    if not db_holiday:
        raise HTTPException(status_code=404, detail="Holiday not found")
    db_holiday.year = holiday.year
    db_holiday.date = holiday.date
    db_holiday.name = holiday.name
    db.commit()
    db.refresh(db_holiday)
    return db_holiday
