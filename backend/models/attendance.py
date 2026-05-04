from sqlalchemy import Column, Integer, String, Boolean, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import datetime

class AttendanceLog(Base):
    """ตารางเก็บประวัติการเช็คอิน/ออกงาน (ZKTeco Face Scanner)"""
    __tablename__ = "attendance_logs"

    id      = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)

    date           = Column(Date,     nullable=False, index=True)
    check_in_time  = Column(DateTime, nullable=True) # Effective Check-in
    check_out_time = Column(DateTime, nullable=True) # Effective Check-out (Cutoff applied)

    # เก็บเวลาจริงจากเครื่องสแกนเพื่อตรวจสอบย้อนหลัง
    actual_check_in  = Column(DateTime, nullable=True)
    actual_check_out = Column(DateTime, nullable=True)

    status       = Column(String,  default="present")
    late_minutes = Column(Integer, default=0)

    site_name    = Column(String,  nullable=True)
    note         = Column(String,  nullable=True)
    is_approved  = Column(Boolean, default=False)

    user = relationship("User", backref="attendance_logs")


class CompanyHoliday(Base):
    """ตารางเก็บวันหยุดประจำปี (Public Holidays) จัดการแยกรายปี"""
    __tablename__ = "company_holidays"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, index=True) # เช่น 2026
    date = Column(Date, nullable=False, index=True) # เช่น 2026-04-13
    name = Column(String, nullable=False) # เช่น Songkran Festival
    is_active = Column(Boolean, default=True)

class AttendanceConfig(Base):
    """ตารางเก็บการตั้งค่าแบบ Key-Value (เวลาเข้างาน, โควตาวันลา, เวลาโอที)"""
    __tablename__ = "attendance_configs"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False) # เช่น check_in_time
    value = Column(String, nullable=False) # เช่น 08:00
    description = Column(String, nullable=True) # คำอธิบาย (ใส่ไว้ให้ admin อ่านใน DB ง่ายๆ)

class AttendanceLocation(Base):
    """ตารางเก็บสถานที่อนุญาตให้เช็คอิน (Fixed และ Onsite)"""
    __tablename__ = "attendance_locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False) # ชื่อสถานที่ เช่น สำนักงานใหญ่, โปรเจกต์ A
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    radius = Column(Integer, default=100) # รัศมีที่ยอมให้เช็คอินได้ (เป็นเมตร)
    is_fixed = Column(Boolean, default=True) # True=Fixed (โรงงาน/ออฟฟิศ), False=Onsite (ดึงมาจากโปรเจกต์)


