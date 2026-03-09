"""
เครื่องมือเติมข้อมูลตั้งต้นสำหรับระบบบริหารงานบุคคล (HR Data Seed Tool)
ไฟล์นี้ใช้สำหรับเพิ่มข้อมูล "แผนก" และ "ตำแหน่งงาน" พื้นฐานเข้าระบบโดยอัตโนมัติ
ช่วยให้ระบบมีข้อมูลพื้นฐานพร้อมใช้งานทันทีหลังจากการติดตั้ง
"""

import sys
import os

# เพิ่มพาธปัจจุบันเข้าไปเพื่อให้หาโมดูลอื่นๆ ในโปรเจกต์เจอ
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import users as models
from models import projects # ตรวจสอบให้แน่ใจว่าโหลดโมเดล Project มาด้วย

def seed_hr_data():
    """ฟังก์ชันสำหรับเพิ่มข้อมูลแผนกและตำแหน่งงานลงในฐานข้อมูล"""
    db = SessionLocal()
    try:
        # ตรวจสอบก่อนว่าเคยเติมข้อมูลไปแล้วหรือยัง เพื่อป้องกันข้อมูลซ้ำ
        if db.query(models.Department).count() > 0:
            print("ข้อมูล HR มีอยู่ในระบบอยู่แล้ว ข้ามขั้นตอนการ Seed.")
            return

        print("กำลังเติมข้อมูลแผนกและตำแหน่งงานเบื้องต้น...")
        
        # รายการข้อมูลแผนกและตำแหน่งงานย่อยในแต่ละแผนก
        dept_data = {
            'office':       ['Admin', 'Accounting', 'Purchasing', 'Manager', 'Supervisor'],
            'draftman':     ['Master Draftman', 'Senior Draftman', 'Junior Draftman'],
            'production':   ['QC', 'CNC-Edge', 'Custom', 'Packing'],
            'installation': ['Supervisor', 'Installer', 'Assistant'],
            'management':   ['CEO'],
        }
        
        # ชื่อเรียกภาษาไทย/อังกฤษของแต่ละแผนก
        dept_labels = {
            'office': 'Office',
            'draftman': 'Draftman',
            'production': 'Production',
            'installation': 'Installation',
            'management': 'Management'
        }

        # วนลูปเพื่อสร้างข้อมูลแผนกและตำแหน่งงาน
        for value, titles in dept_data.items():
            name = dept_labels[value]
            dept = models.Department(name=name, value=value)
            db.add(dept)
            db.flush() # เรียกเพื่อให้ได้ ID ของแผนกมาใช้สำหรับตำแหน่งงานย่อย
            
            for title in titles:
                jt = models.JobTitle(name=title, department_id=dept.id)
                db.add(jt)
        
        db.commit()
        print("เติมข้อมูลสำเร็จ!")
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")
        db.rollback() # ย้อนกลับการทำรายการหากเกิดข้อผิดพลาด
    finally:
        db.close()

if __name__ == "__main__":
    seed_hr_data()

