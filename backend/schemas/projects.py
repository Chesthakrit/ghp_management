from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# --- ฟอร์มพื้นฐาน (ใช้ร่วมกัน) ---
class ProjectBase(BaseModel):
    name: str
    customer: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None

# --- ฟอร์มตอนสร้างงาน (รับแค่ข้อมูลพื้นฐาน) ---
class ProjectCreate(ProjectBase):
    pass 

# --- ฟอร์มตอนส่งข้อมูลกลับ (เพิ่ม ID, Status, Owner) ---
class ProjectOut(ProjectBase):
    id: int
    status: str
    created_at: datetime
    owner_id: int

    class Config:
        from_attributes = True