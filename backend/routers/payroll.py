"""
ไฟล์จัดการระบบเงินเดือน (Payroll Router)
รับผิดชอบเรื่องการตั้งค่าเงินเดือน และการคำนวณเงินเดือนร่วมกับค่าล่วงเวลา (OT)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime, timedelta
import calendar

from database import get_db
from models import users as model_users
from models import attendance as model_attendance
from models import payroll as model_payroll
from schemas import payroll as schemas_payroll
import oauth2

router = APIRouter(
    prefix="/payroll",
    tags=["Payroll"]
)

# ─────────────────────────────────────────────
#  1. ตั้งค่าส่วนกลาง (Global Settings)
# ─────────────────────────────────────────────

@router.get("/settings", response_model=List[schemas_payroll.PayrollSettingOut])
def get_payroll_settings(
    db: Session = Depends(get_db),
    current_user = Depends(oauth2.get_current_user)
):
    """ดึงค่าคอนฟิกส่วนกลางทั้งหมดของการตั้งค่าระบบเงินเดือน"""
    # รายการคีย์ข้อมูลการตั้งค่าเริ่มต้นที่จำเป็นสำหรับระบบ
    required_settings = [
        {'key': 'common_work_hours_per_day', 'value': 8.0, 'description': 'Standard work hours per shift', 'type': 'float'},
        {'key': 'monthly_ot_rate', 'value': 1.5, 'description': 'OT Multiplier for Monthly employees', 'type': 'float'},
        {'key': 'monthly_divisor_days', 'value': 30.0, 'description': 'Days used to calculate hourly rate for Monthly', 'type': 'float'},
        {'key': 'daily_ot_rate', 'value': 1.5, 'description': 'OT Multiplier for Daily employees', 'type': 'float'},
        {'key': 'daily_holiday_rate', 'value': 3.0, 'description': 'Holiday OT Multiplier for Daily employees', 'type': 'float'},
    ]

    # ตรวจสอบว่ามีการตั้งค่าครบทุกรายการหรือไม่ ถ้าไม่มีให้สร้างเพิ่ม
    existing_keys = {s.key for s in db.query(model_payroll.PayrollSetting).all()}
    
    needs_commit = False
    for s in required_settings:
        if s['key'] not in existing_keys:
            db.add(model_payroll.PayrollSetting(**s))
            needs_commit = True
    
    if needs_commit:
        db.commit()

    return db.query(model_payroll.PayrollSetting).all()

@router.put("/settings/{key}", response_model=schemas_payroll.PayrollSettingOut)
def update_payroll_setting(
    key: str,
    update_data: schemas_payroll.PayrollSettingUpdate,
    db: Session = Depends(get_db),
    admin = Depends(oauth2.check_can_manage_users) # เฉพาะแอดมินหรือ HR เท่านั้นที่แก้ได้
):
    """แอดมินแก้ไขการตั้งค่าส่วนกลางของระบบเงินเดือน"""
    setting = db.query(model_payroll.PayrollSetting).filter(model_payroll.PayrollSetting.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting key not found")
    
    setting.value = update_data.value
    db.commit()
    db.refresh(setting)
    return setting

# ─────────────────────────────────────────────
#  2. Logic การคำนวณเบื้องต้น (Calculation Core)
# ─────────────────────────────────────────────

@router.get("/calculate/{user_id}")
def calculate_user_salary(
    user_id: int,
    month: int,
    year: int,
    db: Session = Depends(get_db),
    admin = Depends(oauth2.check_can_manage_users)
):
    """
    ฟังก์ชันหลักในการประมวลผลเงินเดือน
    ใช้ข้อมูลจากการลงเวลาเข้า-ออกงาน (AttendanceLog) และโปรไฟล์ของพนักงานมาคำนวณ
    """
    
    # 1. ดึงข้อมูลโปรไฟล์ของพนักงาน
    user = db.query(model_users.User).filter(model_users.User.id == user_id).first()
    if not user or not user.employee_profile:
        raise HTTPException(status_code=404, detail="Employee profile not found")
    profile = user.employee_profile
    base_salary = profile.base_salary or 0
    salary_type = profile.salary_type or "monthly"
    
    # 2. ดึงการตั้งค่าส่วนกลางทั้งหมดของระบบเงินเดือน
    settings = {s.key: s.value for s in db.query(model_payroll.PayrollSetting).all()}
    
    # จัดเตรียมตัวแปรการคำนวณโดยแยกตามประเภทรายเดือนและรายวัน
    std_work_hours = settings.get('common_work_hours_per_day', 8.0)
    
    if salary_type == "monthly":
        ot_rate = settings.get('monthly_ot_rate', 1.5)
        std_days_month = settings.get('monthly_divisor_days', 30.0)
    else:
        ot_rate = settings.get('daily_ot_rate', 1.5)
        std_days_month = 1.0 # รายวันไม่ใช้ตัวหารนี้ แต่วางไว้กัน Error
    
    holiday_rate = settings.get('daily_holiday_rate', 3.0) if salary_type == "daily" else ot_rate

    # 3. ดึงประวัติการลงเวลาของพนักงานในช่วงเดือนที่ต้องการคำนวณ
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    logs = db.query(model_attendance.AttendanceLog).filter(
        model_attendance.AttendanceLog.user_id == user_id,
        model_attendance.AttendanceLog.date >= start_date,
        model_attendance.AttendanceLog.date <= end_date,
        model_attendance.AttendanceLog.status == "present"
    ).all()

    # 4. ประมวลผลรายละเอียดจำนวนวันเข้าทำงานและชั่วโมงล่วงเวลา
    total_present_days = len(logs)
    total_ot_hours = 0.0
    
    for l in logs:
        if l.check_in_time and l.check_out_time:
            work_duration = l.check_out_time - l.check_in_time
            hours = work_duration.total_seconds() / 3600
            if hours > 5: hours -= 1.0 # หักพัก 1 ชม.
            
            if hours > std_work_hours:
                total_ot_hours += (hours - std_work_hours)

    # 5. สรุปตัวเลขจำนวนเงินที่ได้รับทั้งหมด
    earned_salary = 0
    if salary_type == "monthly":
        earned_salary = base_salary 
    else:
        earned_salary = base_salary * total_present_days
    
    # สูตรคำนวณเงินเดือนรายชั่วโมง
    if salary_type == "monthly":
        # รายเดือน: (เงินเดือนพื้นฐาน / จำนวนวันทำงานตามเกณฑ์ / จำนวนชั่วโมงกะต่อวัน)
        hourly_rate = (base_salary / std_days_month / std_work_hours)
    else:
        # รายวัน: (ค่าจ้างรายวัน / จำนวนชั่วโมงกะต่อวัน)
        hourly_rate = (base_salary / std_work_hours)

    ot_income = hourly_rate * ot_rate * total_ot_hours
    grand_total = earned_salary + ot_income

    return {
        "user": f"{user.first_name} {user.last_name}",
        "period": f"{month}/{year}",
        "salary_type": salary_type,
        "base_salary": base_salary,
        "summary": {
            "work_days": total_present_days,
            "ot_hours": round(total_ot_hours, 2),
            "earned_salary": round(earned_salary, 2),
            "ot_income": round(ot_income, 2),
            "grand_total": round(grand_total, 2)
        }
    }
