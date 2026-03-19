"""
ไฟล์กำหนดโครงสร้างข้อมูล (Schemas) สำหรับผู้ใช้งาน (Users)
ใช้ Pydantic เพื่อตรวจสอบความถูกต้องของข้อมูล (Validation) ที่รับ-ส่งผ่าน API
"""

from pydantic import BaseModel, validator
from typing import Optional, List

# --- โครงสร้างข้อมูลประวัติพนักงาน (Employee Profile Schema) ---
class EmployeeProfileBase(BaseModel):
    department: Optional[str] = None      # แผนก
    job_title: Optional[str] = None       # ชื่อตำแหน่ง
    hire_date: Optional[str] = None       # วันเริ่มงาน
    employment_status: Optional[str] = 'intern' # สถานะการจ้างงาน
    salary_type: Optional[str] = 'monthly'      # รูปแบบการจ่ายเงิน
    base_salary: Optional[int] = 0        # ยอดเงินเดือน/ค่าจ้าง
    bank_account: Optional[str] = None    # เลขบัญชีธนาคาร (ถ้ามี)

class EmployeeProfileOut(EmployeeProfileBase):
    """ข้อมูลประวัติพนักงานสำหรับส่งออกไปยัง Frontend"""
    id: int
    user_id: int
    termination_date: Optional[str] = None # วันที่ลาออก (ถ้ามี)

    class Config:
        from_attributes = True

# --- ข้อมูลสำหรับการสร้างผู้ใช้งานใหม่ (User Create - ตอนสมัคร/ลงทะเบียน) ---
class UserCreate(BaseModel):
    username: str                   # ชื่อผู้ใช้งานสำหรับล็อกอิน
    nickname: Optional[str] = None  # ชื่อเล่น
    password: str                   # รหัสผ่าน
    role: str = "employee"          # บทบาทพนักงาน (เริ่มต้นเป็น employee)

    # ข้อมูลส่วนตัว (Personal Info)
    first_name: str                 # ชื่อจริง
    last_name: str                  # นามสกุล
    birth_date: str                 # วันเกิด
    phone: str                      # เบอร์โทรศัพท์
    id_card_number: str             # เลขบัตรประชาชน / พาสปอร์ต
    nationality: str                 # สัญชาติ

# --- ข้อมูลสำหรับการแก้ไขผู้ใช้งาน (User Update - โดย Admin) ---
class UserUpdate(BaseModel):
    role: Optional[str] = None             # แก้ไขบทบาท
    is_active: Optional[bool] = None       # เปิด/ปิด การใช้งานบัญชี
    first_name: Optional[str] = None       # แก้ไขชื่อจริง
    last_name: Optional[str] = None        # แก้ไขนามสกุล
    birth_date: Optional[str] = None       # แก้ไขวันเกิด
    phone: Optional[str] = None            # แก้ไขเบอร์โทร
    nickname: Optional[str] = None         # แก้ไขชื่อเล่น
    nationality: Optional[str] = None      # แก้ไขสัญชาติ
    id_card_number: Optional[str] = None   # แก้ไขเลขบัตรประชาชน

# --- ข้อมูลสำหรับการแก้ไขประวัติพนักงาน (Employee Profile Update) ---
class EmployeeProfileUpdate(BaseModel):
    department: Optional[str] = None       # แก้ไขแผนก
    job_title: Optional[str] = None        # แก้ไขตำแหน่ง
    hire_date: Optional[str] = None        # แก้ไขวันเริ่มงาน
    employment_status: Optional[str] = None # แก้ไขสถานะการจ้างงาน
    salary_type: Optional[str] = None       # แก้ไขรูปแบบการจ่ายเงิน
    base_salary: Optional[int] = None       # แก้ไขยอดเงินเดือน/ค่าจ้าง
    bank_account: Optional[str] = None      # แก้ไขเลขบัญชีธนาคาร

# --- ข้อมูลผู้ใช้งานสำหรับส่งออก (User Out - ส่งข้อมูลกลับไปยังหน้าจอ) ---
class UserOut(BaseModel):
    id: int
    username: str
    nickname: Optional[str] = None
    role: str                       # ส่งเป็นชื่อ Role
    permissions: List[str] = []     # รายการสิทธิ์การใช้งาน
    is_active: bool

    # ข้อมูลส่วนตัวเพิ่มเติม
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birth_date: Optional[str] = None
    phone: Optional[str] = None
    nationality: Optional[str] = None
    id_card_number: Optional[str] = None
    photo_path: Optional[str] = None       # พาร์ทของรูปถ่าย
    id_doc_path: Optional[str] = None      # พาร์ทของรูปบัตรประชาชน

    employee_profile: Optional[EmployeeProfileOut] = None # ข้อมูลการจ้างงานพ่วงไปด้วย

    class Config:
        from_attributes = True

    # Validator สำหรับแปลง Object ของ Role ให้กลายเป็นแค่ข้อความภาษาอังกฤษ (String)
    @validator('role', pre=True)
    def extract_role_name(cls, v):
        if hasattr(v, 'name'):
            return v.name
        return str(v)

