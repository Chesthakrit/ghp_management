"""
ไฟล์จัดการระบบบันทึกเวลาเข้า-ออกงาน (Attendance Router)
รองรับการ Check-in, Check-out และการดูประวัติการลงเวลา
"""
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from sqlalchemy.orm import Session
from datetime import date, datetime
import os
import shutil
import uuid
import oauth2
from database import get_db
from models import attendance as models
from schemas import attendance as schemas
from utils.attendance_utils import calculate_attendance_status, calculate_ot_hours # เพิ่มการคำนวณ OT

router = APIRouter(
    prefix="/attendance",
    tags=["Attendance System"]
)

@router.get("/ot-rules")
def get_ot_rules(
    db: Session = Depends(get_db),
    current_user = Depends(oauth2.get_current_user) # บังคับ Login เพื่อดูกฎบริษัท
):
    """
    ดึงกฎเวลา OT (เฉพาะพนักงานในระบบ)
    """
    keys = ["ot_normal_start", "ot_normal_end", "ot_special_start", "ot_special_end", "ot_morning_start", "ot_morning_end"]
    configs = db.query(models.AttendanceConfig).filter(models.AttendanceConfig.key.in_(keys)).all()
    return {c.key: c.value for c in configs}

# Setup Upload Directory
UPLOAD_DIR = "uploads/attendance"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload-image")
def upload_attendance_image(
    file: UploadFile = File(...),
    current_user = Depends(oauth2.get_current_user)
):
    """
    อัปโหลดรูปภาพ Check-In / Check-Out
    """
    try:
        file_ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        new_filename = f"attd_{current_user.username}_{uuid.uuid4().hex[:8]}.{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, new_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return {"filename": new_filename, "path": f"uploads/attendance/{new_filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

    # --- ลอจิกการคำนวณสถานะสาย (Server-side Calculation) ---
    all_configs = db.query(models.AttendanceConfig).all()
    cfg_dict = {c.key: c.value for c in all_configs}
    check_in_dt = datetime.now()
    
    # เรียกใช้ฟังก์ชันจาก utils เพิื่อคำนวณสถานะสาย (Clean Code)
    status = calculate_attendance_status(current_user.id, check_in_dt, cfg_dict)

    # สร้าง Record ใหม่ในตาราง attendance_logs
    new_attendance = models.AttendanceLog(
        user_id=current_user.id,
        date=today,
        check_in_time=check_in_dt,
        check_in_type=check_in_data.check_in_type,
        location_lat=check_in_data.location_lat,
        location_lon=check_in_data.location_lon,
        site_name=check_in_data.site_name,
        ip_address=client_ip,
        check_in_image=check_in_data.check_in_image,
        note=check_in_data.note,
        status=status # บันทึกสถานะที่คำนวณได้ลง DB ทันที
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


def check_time_permission(user, action_perm=None):
    """ตรวจสอบสิทธิ์การจัดการเวลา (รองรับสิทธิ์แอดมินและรายบุคคล)"""
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
            
    return db.query(models.AttendanceLog).filter(models.AttendanceLog.user_id == user_id).order_by(models.AttendanceLog.date.desc()).all()


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
    elif any(k.startswith('ot_') for k in keys):
        required_perm = 'action.time.edit_ot'
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


@router.post("/ot-requests", response_model=schemas.OTRequestResponse)
def create_ot_request(
    ot_data: schemas.OTRequestCreate,
    db: Session = Depends(get_db),
    current_user = Depends(oauth2.get_current_user)
):
    """
    บันทึกคำขอทำ OT พร้อมตรวจสอบความถูกต้องจากฝั่ง Server
    """
    # 1. ดึง Config เพื่อใช้คำนวณ
    all_configs = db.query(models.AttendanceConfig).all()
    cfg_dict = {c.key: c.value for c in all_configs}
    
    # 2. ตรวจสอบว่าเป็นวันหยุดหรือไม่ (ใช้ Logic เดียวกับหน้าบ้าน)
    is_weekend = ot_data.request_date.weekday() in [5, 6] # 5=Sat, 6=Sun
    
    # 3. คำนวณชั่วโมงใหม่จากฝั่ง Server เพื่อ Validate (Security)
    srv_std, srv_sp = calculate_ot_hours(
        ot_data.start_time, 
        ot_data.end_time, 
        cfg_dict, 
        is_weekend
    )
    
    new_ot = models.OTRequest(
        user_id=current_user.id,
        request_date=ot_data.request_date,
        start_time=ot_data.start_time,
        end_time=ot_data.end_time,
        standard_hours=srv_std, # ใช้ค่าที่คำนวณจาก Server เพื่อความปลอดภัย
        special_hours=srv_sp,
        total_hours=srv_std + srv_sp,
        reason=ot_data.reason,
        status="pending"
    )
    
    db.add(new_ot)
    db.commit()
    db.refresh(new_ot)
    return new_ot


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


# --- Location Management Endpoints ---

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
