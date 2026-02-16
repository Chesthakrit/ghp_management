from pydantic import BaseModel, EmailStr
from typing import Optional

# --- ฟอร์มขาเข้า (ตอนสมัคร) ---
class UserCreate(BaseModel):
    username: str
    email: EmailStr  # บังคับว่าเป็นรูปแบบอีเมล (มี @, มี .com)
    password: str
    role: str = "employee" # ถ้าไม่ระบุ ให้ถือว่าเป็นพนักงานทั่วไป

# --- ฟอร์มขาออก (ส่งข้อมูลกลับไปให้ดู) ---
class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    is_active: bool

    # บรรทัดนี้สำคัญ! บอกให้ Pydantic อ่านข้อมูลจาก Database (ORM) ได้
    class Config:
        from_attributes = True