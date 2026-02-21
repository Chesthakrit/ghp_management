from pydantic import BaseModel, validator
from typing import Optional, List

# --- Employee Profile Schema ---
class EmployeeProfileBase(BaseModel):
    department: Optional[str] = None
    job_title: Optional[str] = None
    hire_date: Optional[str] = None
    employment_status: Optional[str] = 'intern'

class EmployeeProfileOut(EmployeeProfileBase):
    id: int
    user_id: int
    termination_date: Optional[str] = None

    class Config:
        from_attributes = True

# --- User Create (ตอนสมัคร) ---
class UserCreate(BaseModel):
    username: str
    nickname: Optional[str] = None   # ชื่อเล่น (แทน email)
    password: str
    role: str = "employee"

    # Personal Info
    first_name: str
    last_name: str
    birth_date: str
    phone: str
    id_card_number: str     # บัตรประชาชน / พาสปอร์ต / เอกสารต่างด้าว
    nationality: str

# --- User Update (Admin แก้ไขข้อมูลส่วนตัว) ---
class UserUpdate(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birth_date: Optional[str] = None
    phone: Optional[str] = None
    nickname: Optional[str] = None
    nationality: Optional[str] = None
    id_card_number: Optional[str] = None

# --- Employee Profile Update ---
class EmployeeProfileUpdate(BaseModel):
    department: Optional[str] = None
    job_title: Optional[str] = None
    hire_date: Optional[str] = None
    employment_status: Optional[str] = None

# --- User Out ---
class UserOut(BaseModel):
    id: int
    username: str
    nickname: Optional[str] = None
    role: str
    permissions: List[str] = []
    is_active: bool

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birth_date: Optional[str] = None
    phone: Optional[str] = None
    nationality: Optional[str] = None
    id_card_number: Optional[str] = None
    photo_path: Optional[str] = None
    id_doc_path: Optional[str] = None

    employee_profile: Optional[EmployeeProfileOut] = None

    class Config:
        from_attributes = True

    @validator('role', pre=True)
    def extract_role_name(cls, v):
        if hasattr(v, 'name'):
            return v.name
        return str(v)
