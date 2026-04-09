"""
เปรียบเสมือนหัวสมองคำนวณสเตตัสการเข้างาน (Attendance Logic Module)
"""
from datetime import datetime
from sqlalchemy.orm import Session
from models import attendance as models

def calculate_attendance_status(user_id: int, check_in_dt: datetime, config_dict: dict) -> str:
    """
    หัวสมองคำนวณสถานะ: หักลบเวลาจริงกับกฎบริษัทออกมาเป็นนาที แล้วตัดสินเกรดการสาย
    """
    # 1. ข้อมูลพนักงานและเวลาที่เช็คอินจริง
    emp_id = user_id
    actual_h = check_in_dt.hour
    actual_m = check_in_dt.minute
    
    # 2. กฎเวลาจาก Settings (Default: 08:30)
    rule_checkin_time = config_dict.get('check_in_time', '08:30')
    target_h, target_m = map(int, rule_checkin_time.split(':'))
    
    # 3. เกณฑ์ผ่อนผัน (Grace Periods)
    grace_1 = int(config_dict.get('late_grace_period_mins') or 0)
    grace_2 = int(config_dict.get('late_grace_period_mins_t2') or 15)
    grace_3 = int(config_dict.get('late_grace_period_mins_t3') or 30)
    
    status = "present"
    
    try:
        # --- [STEP 1: แปลงเป็นนาทีทั้งหมด] ---
        actual_total_mins = (actual_h * 60) + actual_m
        target_total_mins = (target_h * 60) + target_m
        
        # --- [STEP 2: หักลบเพื่อหาเศษนาทีที่เกินมา] ---
        diff_mins = actual_total_mins - target_total_mins
        
        # --- [DEBUG LOG: กางการหักลบให้คุณพี่เห็นชัดๆ] ---
        print(f"\n--- [ATTENDANCE MATH FOR ID: {emp_id}] ---")
        print(f"ACTUAL: {actual_h}:{actual_m} -> ({actual_h}*60)+{actual_m} = {actual_total_mins} mins")
        print(f"TARGET: {target_h}:{target_m} -> ({target_h}*60)+{target_m} = {target_total_mins} mins")
        print(f"RESULT: {actual_total_mins} - {target_total_mins} = {diff_mins} minutes diff")
        
        # --- [STEP 3: ตัดสินเกรดด้วยกฎ Grace Period] ---
        if diff_mins <= 0:
            status = "present"
            print(f"Status: บนเวลาปกติ (On-time)")
        elif diff_mins <= grace_1:
            status = "present"
            print(f"Status: ช่วงผ่อนผันระดับ 0 (Grace)")
        elif diff_mins <= grace_2:
            status = "late_t1"
            print(f"Status: สายระดับ 1 (Late T1)")
        elif diff_mins <= grace_3:
            status = "late_t2"
            print(f"Status: สายระดับ 2 (Late T2)")
        else:
            status = "late_t3"
            print(f"Status: สายระดับ 3 (Late T3)")
            
        print(f"G1={grace_1}, G2={grace_2}, G3={grace_3}")
        print(f"----------------------------------------------\n")
            
    except Exception as e:
        print(f"!!! MATH ERROR FOR ID {emp_id}: {e}")
        status = "present"
        
    return status
