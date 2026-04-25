from sqlalchemy import Column, Integer, String, Boolean, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import datetime

class AttendanceLog(Base):
    """ตารางเก็บประวัติการเช็คอิน (เข้า-ออกงาน) สำหรับระบบ Attendance Tracker"""
    __tablename__ = "attendance_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    
    # ข้อมูลวันที่และเวลาเข้าออก
    date = Column(Date, nullable=False, index=True) # วันที่ที่ทำรายการ (เช่น 2026-03-10) ไว้ให้ดึงข้อมูลง่ายรายเดือน
    check_in_time = Column(DateTime, nullable=True) # เวลาที่เข้างาน
    check_out_time = Column(DateTime, nullable=True) # เวลาที่ออกงาน

    status = Column(String, default="present") # สถานะ (เช่น present, late, absent, half_day)
    
    # โหมดและช่องทางการเช็คอิน (On-Factory vs On-Site)
    check_in_type = Column(String, default="factory") # 'factory' (จาก ZKTeco) หรือ 'site' (จากแอปมือถือ)
    
    # พิกัดและ Network (เฉพาะโหมดที่ใช้แอป หรือ ไว้ตรวจสอบ IP wifi บริษัท)
    location_lat = Column(Float, nullable=True)
    location_lon = Column(Float, nullable=True)
    ip_address = Column(String, nullable=True)
    
    # ข้อมูลสำหรับ On-Site (ที่ต้องถ่ายรูปเซลฟี่หน้าไซด์งาน)
    site_name = Column(String, nullable=True)
    check_in_image = Column(String, nullable=True) # Path URL รูปเซลฟี่ตอนเช็คอิน
    check_out_image = Column(String, nullable=True) # Path URL รูปเซลฟี่ตอนเช็คเอาท์
    
    # อื่นๆ
    note = Column(String, nullable=True) # พนักงานสามารถโน้ตบอกได้ เช่น "รถเสีย"
    is_approved = Column(Boolean, default=False) # หัวหน้าได้กดอนุมัติสำหรับกรณีลดย่อนหรือมาสายหรือยัง
    late_minutes = Column(Integer, default=0)    # จำนวนนาทีที่สายจริง (ใช้แสดงผลแทน Tier)

    # Relationship ไปยังตาราง User
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
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True) # เชื่อมกับโปรเจกต์ (ถ้ามี)
    
    # Relationship (Optional: to project if needed later)
    project = relationship("Project", backref="attendance_locations")

class OTRequest(Base):
    """ตารางเก็บคำขอทำโอที (Overtime Requests)"""
    __tablename__ = "ot_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    
    request_date = Column(Date, nullable=False, index=True) # วันที่ที่ขอทำ OT
    start_time = Column(String, nullable=False)            # เวลาเริ่ม เช่น "17:30"
    end_time = Column(String, nullable=False)              # เวลาเลิก เช่น "20:30"
    
    standard_hours = Column(Float, default=0.0)            # จำนวนชั่วโมงเรทปกติ (1.5x)
    special_hours = Column(Float, default=0.0)             # จำนวนชั่วโมงเรทพิเศษ (3.0x / ชดเชย)
    total_hours = Column(Float, default=0.0)               # รวมทั้งหมด
    
    reason = Column(String, nullable=True)                 # เหตุผล/ลักษณะงาน
    status = Column(String, default="pending")             # pending, approved, rejected
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True) # ใครเป็นผู้อนุมัติ
    
    # Relationship
    user = relationship("User", foreign_keys=[user_id], backref="ot_requests")
    approver = relationship("User", foreign_keys=[approved_by_id])
