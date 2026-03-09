"""
ไฟล์กำหนดโครงสร้างตารางฐานข้อมูลสำหรับโครงการ (Project Model)
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Project(Base):
    """ตารางโครงการ (Projects)"""
    __tablename__ = "projects" # ชื่อตารางในฐานข้อมูล

    # --- ข้อมูลพื้นฐาน ---
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)           # ชื่อโครงการ (เช่น งานบิ้วอินบ้านลูกค้า A)
    customer = Column(String)                   # ชื่อลูกค้าหรือผู้ว่าจ้าง
    description = Column(Text, nullable=True)   # รายละเอียดเนื้อหางานโดยรวม
    status = Column(String, default="Pending")  # สถานะ: Pending(รอดำเนินการ), Doing(กำลังทำ), Done(เสร็จสิ้น)
    
    # --- วันเวลา ---
    # บันทึกวันที่สร้างโครงการอัตโนมัติ โดยใช้เวลามาตรฐานสากล (UTC)
    created_at = Column(DateTime, default=datetime.utcnow) 
    due_date = Column(DateTime, nullable=True)             # วันกำหนดส่งงานหรือวันสิ้นสุดโครงการ
    
    # --- ความสัมพันธ์ (Relationships) ---
    # เก็บ ID ของผู้ใช้งานที่เป็นเจ้าของโครงการนี้
    owner_id = Column(Integer, ForeignKey("users.id"))      
    # เชื่อมความสัมพันธ์กลับไปยังตาราง User เพื่อให้รับรู้ว่าใครคือคนดูแลโครงการ
    owner = relationship("User", back_populates="projects") 
