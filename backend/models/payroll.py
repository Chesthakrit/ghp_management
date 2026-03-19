from sqlalchemy import Column, Integer, String, Float, Boolean
from database import Base

class PayrollSetting(Base):
    """ตารางเก็บค่าตั้งค่าส่วนกลางสำหรับการคำนวณเงินเดือน (Global Payroll Settings)"""
    __tablename__ = "payroll_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)  # ชื่อการตั้งค่า เช่น 'ot_rate_normal'
    value = Column(Float)                          # ค่าที่เป็นตัวเลข
    description = Column(String, nullable=True)     # อรรถาธิบาย
    type = Column(String, default="float")          # ประเภทข้อมูล (float, int)

    # ตัวอย่างข้อมูลเริ่มต้นที่จะ Seed:
    # 'ot_rate_normal' : 1.5
    # 'ot_rate_holiday' : 3.0
    # 'work_hours_per_day' : 8.0
    # 'standard_days_per_month' : 30.0
