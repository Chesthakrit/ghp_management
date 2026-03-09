"""
ไฟล์กำหนดโครงสร้างข้อมูล (Schemas) สำหรับโมดูลบริหารงานบุคคล (HR)
ประกอบด้วย แผนก, ตำแหน่งงาน, หมวดหมู่ทักษะ และการประเมินทักษะ
"""

from pydantic import BaseModel
from typing import List, Optional

# --- หมวดหมู่ทักษะ (Duty Category) ---
class DutyCategoryBase(BaseModel):
    name: str                           # ชื่อหมวดหมู่ (EN)
    name_th: Optional[str] = None       # ชื่อหมวดหมู่ (TH)
    name_v3: Optional[str] = None       # ชื่อหมวดหมู่ (ภาษาที่สาม)

class DutyCategoryCreate(DutyCategoryBase):
    """ใช้รับข้อมูลตอนสร้างหมวดหมู่ใหม่"""
    pass

class DutyCategoryUpdate(BaseModel):
    """ใช้รับข้อมูลตอนแก้ไขหมวดหมู่"""
    name: Optional[str] = None
    name_th: Optional[str] = None
    name_v3: Optional[str] = None

class DutyCategory(DutyCategoryBase):
    """ข้อมูลหมวดหมู่สำหรับส่งออก"""
    id: int
    class Config:
        from_attributes = True

# --- รายการทักษะ (Duty) ---
class DutyBase(BaseModel):
    name: str                           # ชื่อทักษะ (EN)
    name_th: Optional[str] = None       # ชื่อทักษะ (TH)
    name_v3: Optional[str] = None       # ชื่อทักษะ (ภาษาที่สาม)
    description: Optional[str] = None   # รายละเอียด (EN)
    description_th: Optional[str] = None # รายละเอียด (TH)
    description_v3: Optional[str] = None # รายละเอียด (ภาษาที่สาม)
    category_id: Optional[int] = None   # รหัสหมวดหมู่ที่สังกัด

class DutyCreate(DutyBase):
    """ใช้รับข้อมูลตอนสร้างทักษะใหม่"""
    pass

class DutyUpdate(BaseModel):
    """ใช้รับข้อมูลตอนแก้ไขทักษะ"""
    name: Optional[str] = None
    name_th: Optional[str] = None
    name_v3: Optional[str] = None
    description: Optional[str] = None
    description_th: Optional[str] = None
    description_v3: Optional[str] = None
    category_id: Optional[int] = None

# --- รายการทักษะย่อย (Sub Duty) ---
class SubDutyBase(BaseModel):
    name: str                           # ชื่อทักษะย่อย (EN)
    name_th: Optional[str] = None
    name_v3: Optional[str] = None
    duty_id: int                        # รหัสทักษะหลักที่สังกัด

class SubDutyCreate(SubDutyBase):
    """ใช้รับข้อมูลตอนสร้างทักษะย่อยใหม่"""
    pass

class SubDuty(SubDutyBase):
    """ข้อมูลทักษะย่อยสำหรับส่งออก"""
    id: int
    class Config:
        from_attributes = True

class Duty(DutyBase):
    """ข้อมูลทักษะหลักสำหรับส่งออก (รวมหมวดหมู่และทักษะย่อย)"""
    id: int
    category: Optional[DutyCategory] = None
    sub_duties: List[SubDuty] = []
    class Config:
        from_attributes = True

# --- รายละเอียดงาน (Job Description) ---
class JobDescriptionBase(BaseModel):
    description: str                    # เนื้อหาคำอธิบายงาน
    description_th: Optional[str] = None
    description_v3: Optional[str] = None

class JobDescriptionCreate(JobDescriptionBase):
    """ใช้รับข้อมูลตอนเพิ่มคำอธิบายงานให้ตำแหน่งใดตำแหน่งหนึ่ง"""
    job_title_id: int

class JobDescription(JobDescriptionBase):
    """ข้อมูลคำอธิบายงานสำหรับส่งออก"""
    id: int
    job_title_id: int
    class Config:
        from_attributes = True

# --- ชื่อตำแหน่ง (Job Title) ---
class JobTitleBase(BaseModel):
    name: str                           # ชื่อตำแหน่ง (EN)
    name_th: Optional[str] = None       # ชื่อตำแหน่ง (TH)
    name_v3: Optional[str] = None       # ชื่อตำแหน่ง (ภาษาที่สาม)
    level: int = 1                      # ระดับของตำแหน่ง (เช่น 1, 2, 3)
    min_salary_monthly: int = 0
    max_salary_monthly: int = 0
    min_salary_daily: int = 0
    max_salary_daily: int = 0
    permissions: Optional[str] = None   # JSON string of permissions

class JobTitleCreate(JobTitleBase):
    """ใช้สร้างตำแหน่งใหม่ภายใต้แผนกที่ระบุ"""
    department_id: int

class JobTitleUpdate(BaseModel):
    """ใช้แก้ไขข้อมูลพื้นฐานของตำแหน่ง"""
    name: Optional[str] = None
    name_th: Optional[str] = None
    name_v3: Optional[str] = None
    level: Optional[int] = None
    min_salary_monthly: Optional[int] = None
    max_salary_monthly: Optional[int] = None
    min_salary_daily: Optional[int] = None
    max_salary_daily: Optional[int] = None
    permissions: Optional[str] = None

class JobTitleDutiesUpdate(BaseModel):
    """ใช้สำหรับแก้ไขรายการทักษะที่เกี่ยวข้องกับตำแหน่งนี้"""
    duty_ids: List[int]

class JobTitle(JobTitleBase):
    """ข้อมูลตำแหน่งงานสำหรับส่งออก (รวมคำอธิบายและทักษะที่ต้องมี)"""
    id: int
    department_id: int
    display_order: int = 100
    descriptions: List[JobDescription] = []
    duties: List[Duty] = []
    class Config:
        from_attributes = True

# --- แผนก (Department) ---
class DepartmentBase(BaseModel):
    name: str                           # ชื่อแผนกสวยๆ (EN)
    name_th: Optional[str] = None       # ชื่อแผนกสวยๆ (TH)
    name_v3: Optional[str] = None       # ชื่อแผนกสวยๆ (ภาษาที่สาม)
    value: str                          # ค่าคงที่ที่ใช้ในระบบ (เช่น 'office', 'production')

class DepartmentCreate(DepartmentBase):
    """ใช้รับข้อมูลตอนสร้างแผนกใหม่"""
    pass

class DepartmentUpdate(BaseModel):
    """ใช้รับข้อมูลตอนแก้ไขแผนก"""
    name: Optional[str] = None
    name_th: Optional[str] = None
    name_v3: Optional[str] = None
    value: Optional[str] = None

class Department(DepartmentBase):
    """ข้อมูลแผนกสำหรับส่งออก (รวมรายการตำแหน่งในแผนกนั้นๆ)"""
    id: int
    display_order: int = 100
    job_titles: List[JobTitle] = []
    class Config:
        from_attributes = True

# --- schemas สำหรับ Drag-and-Drop Reordering ---
class ReorderItem(BaseModel):
    """คู่ id และ display_order ที่ต้องการอัปเดต"""
    id: int
    display_order: int

class ReorderRequest(BaseModel):
    """รายการลำดับใหม่ทั้งหมดหลังการ Drag & Drop"""
    items: List[ReorderItem]

# --- การประเมินทักษะรายบุคคล (User Duty Evaluation) ---
class UserDutyEvaluationBase(BaseModel):
    user_id: int                        # รหัสพนักงาน
    duty_id: int                        # รหัสทักษะ
    score: int                          # คะแนนที่ได้ (0-5)

class UserDutyEvaluationCreate(UserDutyEvaluationBase):
    """ใช้รับข้อมูลตอนทำการประเมินพนักงาน"""
    pass

class UserDutyEvaluation(UserDutyEvaluationBase):
    """ข้อมูลผลการประเมินทักษะหลักสำหรับส่งออก"""
    id: int
    evaluated_by_id: Optional[int] = None # รหัสผู้ประเมิน
    updated_at: Optional[str] = None      # วันที่ประเมินล่าสุด
    duty: Optional[Duty] = None         # ข้อมูลทักษะนั้นๆ
    class Config:
        from_attributes = True

# --- การตรวจเช็คทักษะย่อย (User Sub Duty Evaluation / Checklist) ---
class UserSubDutyEvaluationBase(BaseModel):
    user_id: int                        # รหัสพนักงาน
    sub_duty_id: int                     # รหัสทักษะย่อย
    is_completed: bool                  # ผลการตรวจ (ผ่าน/ไม่ผ่าน)

class UserSubDutyEvaluationCreate(UserSubDutyEvaluationBase):
    """ใช้รับข้อมูลตอนติ๊กเช็คลิสต์ทักษะย่อย"""
    pass

class UserSubDutyEvaluation(UserSubDutyEvaluationBase):
    """ข้อมูลผลการตรวจทักษะย่อยสำหรับส่งออก"""
    id: int
    updated_at: Optional[str] = None
    class Config:
        from_attributes = True

