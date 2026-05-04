"""
โมดูลคำนวณสถานะการเข้างาน (Attendance Logic)
"""
from datetime import datetime


def calculate_attendance_status(user_id: int, check_in_dt: datetime, config_dict: dict) -> tuple:
    """
    คำนวณสถานะการมาทำงาน: เปรียบเทียบเวลาจริงกับกฎบริษัทแล้วส่งคืน (status, late_minutes)
    - present  : มาตรงเวลาหรืออยู่ในช่วงผ่อนผัน
    - late_t1/t2/t3 : สายตามระดับที่กำหนดใน Attendance Settings
    """
    actual_h = check_in_dt.hour
    actual_m = check_in_dt.minute

    rule_checkin_time = config_dict.get('check_in_time', '08:30')
    target_h, target_m = map(int, rule_checkin_time.split(':'))

    grace_1 = int(config_dict.get('late_grace_period_mins') or 0)
    grace_2 = int(config_dict.get('late_grace_period_mins_t2') or 15)
    grace_3 = int(config_dict.get('late_grace_period_mins_t3') or 30)

    status = "present"
    diff_mins = 0

    try:
        actual_total_mins = (actual_h * 60) + actual_m
        target_total_mins = (target_h * 60) + target_m
        diff_mins = actual_total_mins - target_total_mins

        if diff_mins <= 0 or diff_mins <= grace_1:
            status = "present"
        elif diff_mins <= grace_2:
            status = "late_t1"
        elif diff_mins <= grace_3:
            status = "late_t2"
        else:
            status = "late_t3"

    except Exception:
        status = "present"
        diff_mins = 0

    return status, max(0, diff_mins)



