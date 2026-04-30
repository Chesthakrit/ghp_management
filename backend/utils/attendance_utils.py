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


def calculate_ot_hours(start_time: str, end_time: str, config_dict: dict, is_weekend: bool = False) -> tuple:
    """
    คำนวณชั่วโมง OT แยกเป็น Standard และ Special ตามกฎบริษัท (Server-side validation)
    ส่งคืน: (standard_hours, special_hours)
    """
    def time_to_min(t_str: str) -> int:
        if not t_str:
            return 0
        h, m = map(int, t_str.split(':'))
        return h * 60 + m

    start_min = time_to_min(start_time)
    end_min   = time_to_min(end_time)

    total_min = end_min - start_min
    if total_min <= 0:
        total_min += 1440  # รองรับกรณีข้ามคืน

    if is_weekend:
        return 0.0, float(round(total_min / 60, 1))

    norm_start = time_to_min(config_dict.get('ot_normal_start',  '17:00'))
    norm_end   = time_to_min(config_dict.get('ot_normal_end',    '22:00'))
    morn_start = time_to_min(config_dict.get('ot_morning_start', '05:00'))
    morn_end   = time_to_min(config_dict.get('ot_morning_end',   '08:00'))

    std_min = 0
    sp_min  = 0

    for m in range(total_min):
        current = (start_min + m) % 1440

        if norm_start < norm_end:
            is_evening_std = norm_start <= current < norm_end
        else:
            is_evening_std = current >= norm_start or current < norm_end

        is_morning_std = morn_start <= current < morn_end

        if is_evening_std or is_morning_std:
            std_min += 1
        else:
            sp_min += 1

    return float(round(std_min / 60, 1)), float(round(sp_min / 60, 1))
