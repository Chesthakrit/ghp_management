"""
ไฟล์กำหนดโครงสร้างข้อมูล (Schemas) สำหรับโครงการ (Projects)
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# --- โครงสร้างพื้นฐานของโครงการ (Project Base) ---
class ProjectBase(BaseModel):
    name: str                           # ชื่อโครงการ
    customer: str                       # ชื่อลูกค้า
    description: Optional[str] = None   # รายละเอียดงาน
    due_date: Optional[datetime] = None # วันที่ต้องส่งงาน

# --- โครงสร้างสำหรับการสร้างโครงการใหม่ (Project Create) ---
class ProjectCreate(ProjectBase):
    """ใช้รับข้อมูลใหม่จาก Frontend แต่อาจจะมีการเพิ่มฟิลด์ในอนาคต"""
    pass 

# --- โครงสร้างสำหรับการส่งข้อมูลโครงการกลับไปยัง Frontend (Project Out) ---
class ProjectOut(ProjectBase):
    id: int                             # ไอดีโครงการ (จาก DB)
    status: str                         # สถานะปัจจุบัน
    created_at: datetime                # วันที่สร้าง
    owner_id: int                       # ไอดีผู้รับผิดชอบโครงการ

    class Config:
        # อนุญาตให้ Pydantic อ่านข้อมูลจาก SQLAlchemy Model ได้โดยตรง
        from_attributes = True
