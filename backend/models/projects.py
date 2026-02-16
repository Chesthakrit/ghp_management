from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Project(Base):
    __tablename__ = "projects" # ชื่อตารางใน Database

    # --- ข้อมูลพื้นฐาน ---
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)           # ชื่อโครงการ (เช่น งานบิ้วอินบ้านคุณเอ)
    customer = Column(String)                   # ชื่อลูกค้า
    description = Column(Text, nullable=True)   # รายละเอียดงาน (ยาวๆ ได้)
    status = Column(String, default="Pending")  # สถานะ: Pending(รอ), Doing(ทำ), Done(เสร็จ)
    
    # --- วันเวลา ---
    created_at = Column(DateTime, default=datetime.utcnow) # วันที่สร้าง (ออโต้)
    due_date = Column(DateTime, nullable=True)             # วันกำหนดส่งงาน
    
    # --- ความสัมพันธ์ (ใครเป็นคนสร้าง/ดูแล) ---
    owner_id = Column(Integer, ForeignKey("users.id"))      # ผูกกับ ID ของ User
    owner = relationship("User", back_populates="projects") # เชื่อมกลับไปหา User