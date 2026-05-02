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
def get_ot_rules(
    db: Session = Depends(get_db),
    current_user = Depends(oauth2.get_current_user)
):
    """ดึงกฎเวลา OT สำหรับคำนวณใน Frontend"""
    keys = ["ot_normal_start", "ot_normal_end", "ot_special_start", "ot_special_end",
            "ot_morning_start", "ot_morning_end", "check_in_time",
            "ot_request_start_time", "ot_request_end_time"]
    configs = db.query(models.AttendanceConfig).filter(models.AttendanceConfig.key.in_(keys)).all()
    return {c.key: c.value for c in configs}


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
    # 1. ดึง Config เพื่อใช้คำนวณและตรวจสอบเงื่อนไข
    all_configs = db.query(models.AttendanceConfig).all()
    cfg_dict = {c.key: c.value for c in all_configs}
    
    # 2. ตรวจสอบ "ช่วงเวลาที่อนุญาตให้ส่งคำขอ OT" (Time Span OT Request)
    # กฎ: ต้องมีการขอล่วงหน้าในช่วงเวลาที่กำหนด
    req_start_str = cfg_dict.get("ot_request_start_time", "00:00")
    req_end_str = cfg_dict.get("ot_request_end_time", "23:59")
    
    now_time = datetime.now().time()
    try:
        req_start = datetime.strptime(req_start_str, "%H:%M").time()
        req_end = datetime.strptime(req_end_str, "%H:%M").time()
        
        # ตรวจสอบว่าเวลาปัจจุบันอยู่ในช่วงที่อนุญาตหรือไม่
        is_in_window = False
        if req_start <= req_end:
            is_in_window = req_start <= now_time <= req_end
        else:
            # กรณีช่วงเวลาข้ามคืน (เช่น 22:00 ถึง 08:00)
            is_in_window = now_time >= req_start or now_time <= req_end
            
        if not is_in_window:
            raise HTTPException(
                status_code=400, 
                detail=f"ไม่อยู่ในช่วงเวลาที่อนุญาตให้ส่งคำขอ OT (อนุญาตระหว่าง {req_start_str} - {req_end_str})"
            )
    except ValueError:
        pass # ถ้า Config ผิดพลาดให้ข้ามการตรวจสอบไปก่อน
    
    # 3. ตรวจสอบว่าเป็นวันหยุดหรือไม่
    is_weekend = ot_data.request_date.weekday() in [5, 6] # 5=Sat, 6=Sun
    
    # 4. คำนวณชั่วโมงใหม่จากฝั่ง Server เพื่อ Validate (Security)
    srv_std, srv_sp = calculate_ot_hours(
        ot_data.start_time, 
        ot_data.end_time, 
        cfg_dict, 
        is_weekend
    )

    # 5. กฎใหม่: พนักงานขอได้แค่ Standard OT เท่านั้น และต้องลงท้ายด้วย :00 หรือ :30
    # เช็คนาที (ต้องเป็น 00 หรือ 30)
    try:
        s_min = int(ot_data.start_time.split(":")[1])
        e_min = int(ot_data.end_time.split(":")[1])
        if s_min not in [0, 30] or e_min not in [0, 30]:
            raise HTTPException(status_code=400, detail="เวลาที่ระบุต้องลงท้ายด้วย :00 หรือ :30 เท่านั้น")
    except:
        raise HTTPException(status_code=400, detail="รูปแบบเวลาไม่ถูกต้อง")

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
