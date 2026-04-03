"""
ไฟล์กำหนดโครงสร้างตารางฐานข้อมูลที่เกี่ยวข้องกับพนักงานและทักษะ (Models for Users and HR)
ใช้ SQLAlchemy ORM เพื่อเชื่อมต่อคลาส Python กับตารางใน PostgreSQL
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint, Table
from sqlalchemy.orm import relationship
from database import Base
import json

# ตารางกลาง (Association Table) สำหรับเชื่อมความสัมพันธ์แบบ Many-to-Many
# ระหว่างชื่อตำแหน่ง (JobTitles) กับ ทักษะงาน (Duties)
# หนึ่งตำแหน่งมีได้หลายทักษะ และหนึ่งทักษะสามารถอยู่ในหลายตำแหน่งได้
job_title_duty_link = Table(
    'job_title_duty_link',
    Base.metadata,
    Column('job_title_id', Integer, ForeignKey('job_titles.id', ondelete="CASCADE"), primary_key=True),
    Column('duty_id', Integer, ForeignKey('duties.id', ondelete="CASCADE"), primary_key=True)
)

class Role(Base):
    """ตารางเก็บสิทธิ์การใช้งานระบบ (Roles)"""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True) # ชื่อ Role เช่น 'admin', 'user'
    permissions = Column(String)  # เก็บรายการสิทธิ์แบบข้อความ JSON เช่น '["user.manage", "project.view"]'

    # ความสัมพันธ์: หนึ่ง Role มีผู้ใช้งานได้หลายคน
    users = relationship("User", back_populates="role")


class User(Base):
    """ตารางผู้ใช้งานระบบหลัก (Users)"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True) # ชื่อล็อกอิน
    password = Column(String)                           # รหัสผ่าน (ที่ผ่านการเข้ารหัสแล้ว)
    nickname = Column(String, nullable=True)          # ชื่อเล่น

    # เชื่อมไปยังตาราง Role (สิทธิ์การใช้งาน)
    role_id = Column(Integer, ForeignKey("roles.id"))
    role = relationship("Role", back_populates="users")

    is_active = Column(Boolean, default=True) # สถานะการเปิดใช้งานบัญชี

    # ข้อมูลส่วนตัว (Personal Information)
    first_name = Column(String, nullable=True)     # ชื่อจริง
    last_name = Column(String, nullable=True)      # นามสกุล
    birth_date = Column(String, nullable=True)     # วันเกิด
    phone = Column(String, nullable=True)          # เบอร์โทรศัพท์
    id_card_number = Column(String, nullable=True, unique=True) # เลขบัตรประชาชน/พาสปอร์ต
    nationality = Column(String, nullable=True)    # สัญชาติ

    # ข้อมูลไฟล์เอกสารและรูปภาพ
    photo_path = Column(String, nullable=True)     # ที่อยู่ไฟล์รูปถ่ายหน้าตรง
    id_doc_path = Column(String, nullable=True)    # ที่อยู่ไฟล์รูปบัตรประชาชน/พาสปอร์ต

    # ความสัมพันธ์กับตารางอื่นๆ
    projects = relationship("Project", back_populates="owner") # โครงการที่ดูแล
    employee_profile = relationship("EmployeeProfile", back_populates="user", uselist=False) # ข้อมูลพนักงาน (1-to-1)
    duty_evaluations = relationship("UserDutyEvaluation", foreign_keys="[UserDutyEvaluation.user_id]", back_populates="user", cascade="all, delete-orphan")

    @property
    def permissions(self):
        """Helper function สำหรับดึงสิทธิ์ที่รวมกันระหว่าง Role และ ตำแหน่ง (Job Title)"""
        from sqlalchemy.orm import object_session
        perms = []
        
        # 1. ดึงสิทธิ์จาก Role (admin/employee)
        if self.role and self.role.permissions:
            try:
                perms.extend(json.loads(self.role.permissions))
            except:
                pass
        
        # 2. ดึงสิทธิ์จากตำแหน่งงาน (Job Title) ผ่านโปรไฟล์พนักงาน
        if self.employee_profile and self.employee_profile.job_title:
            session = object_session(self)
            if session:
                # ค้นหา JobTitle ที่ชื่อตรงกันและอยู่ในแผนกเดียวกัน (ถ้ามีระบุแผนก)
                query = session.query(JobTitle).filter(JobTitle.name == self.employee_profile.job_title)
                
                # หากโปรไฟล์ระบุแผนก ให้เช็คแผนกด้วยเพื่อให้ได้ข้อมูลที่ถูกต้องแม่นยำ
                if self.employee_profile.department:
                    query = query.join(Department).filter(Department.value == self.employee_profile.department)
                
                jt = query.first()
                if jt and jt.permissions:
                    try:
                        perms.extend(json.loads(jt.permissions))
                    except:
                        pass
        
        # ส่งค่ากลับแบบไม่ซ้ำกัน (Distinct List)
        return list(set(perms))

    # ข้อกำหนดเพิ่มเติม: ชื่อและนามสกุลจริงรวมกันต้องไม่ซ้ำกัน
    __table_args__ = (
        UniqueConstraint('first_name', 'last_name', name='unique_fullname'),
    )

class Department(Base):
    """ตารางแผนก (Departments)"""
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)  # ชื่อแผนกภาษาอังกฤษ
    name_th = Column(String, nullable=True)         # ชื่อแผนกภาษาไทย
    name_v3 = Column(String, nullable=True)         # ชื่อแผนกภาษาที่สาม
    value = Column(String, unique=True, index=True) # ค่าที่ใช้ในระบบ เช่น 'office', 'production'
    display_order = Column(Integer, default=100)    # ลำดับการแสดงผล (ใช้สำหรับ Drag & Drop)
    
    # ความสัมพันธ์: หนึ่งแผนกมีได้หลายชื่อตำแหน่ง
    job_titles = relationship("JobTitle", back_populates="department", cascade="all, delete-orphan")

class JobTitle(Base):
    """ตารางชื่อตำแหน่ง (Job Titles)"""
    __tablename__ = "job_titles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)   # ชื่อตำแหน่งภาษาอังกฤษ
    name_th = Column(String, nullable=True) # ภาษาไทย
    name_v3 = Column(String, nullable=True) # ภาษาที่สาม
    level = Column(Integer, default=0) # ระดับความเชี่ยวชาญ (เช่น 1 = Junior, 2 = Senior)
    display_order = Column(Integer, default=100)  # ลำดับการแสดงผล (ใช้สำหรับ Drag & Drop)
    
    # เชื่อมกับแผนก (Department)
    department_id = Column(Integer, ForeignKey("departments.id"))
    department = relationship("Department", back_populates="job_titles")
    
    # ข้อมูลการกำหนดเงินเดือน (Salary Settings)
    min_salary_monthly = Column(Integer, default=0) # เงินเดือนเริ่มต้น (รายเดือน)
    max_salary_monthly = Column(Integer, default=0) # เงินเดือนสูงสุด (รายเดือน)
    min_salary_daily = Column(Integer, default=0)   # ค่าแรงเริ่มต้น (รายวัน)
    max_salary_daily = Column(Integer, default=0)   # ค่าแรงสูงสุด (รายวัน)
    permissions = Column(String, nullable=True)     # เก็บรายการสิทธิ์แบบ JSON เช่น '["page.factory", "page.office"]'
    
    # รายละเอียดงานและความสัมพันธ์กับทักษะ
    descriptions = relationship("JobDescription", back_populates="job_title", cascade="all, delete-orphan")
    duties = relationship("Duty", secondary=job_title_duty_link, back_populates="job_titles")

class DutyCategory(Base):
    """หมวดหมู่ของทักษะ (Duty Categories) เช่น ทักษะงานไม้, ทักษะงานเขียนแบบ"""
    __tablename__ = "duty_categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True) # ภาษาอังกฤษ
    name_th = Column(String, nullable=True)         # ภาษาไทย
    name_v3 = Column(String, nullable=True)         # ภาษาที่สาม
    display_order = Column(Integer, default=100)
    duties = relationship("Duty", back_populates="category", cascade="all, delete-orphan", order_by="Duty.display_order.asc()")

class Duty(Base):
    """รายการทักษะความสามารถ (Duties/Skills)"""
    __tablename__ = "duties"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True) # ชื่อทักษะ
    name_th = Column(String, nullable=True)
    name_v3 = Column(String, nullable=True)
    description = Column(String, nullable=True)    # รายละเอียดทักษะ
    description_th = Column(String, nullable=True)
    description_v3 = Column(String, nullable=True)
    display_order = Column(Integer, default=100) # สำหรับการ Drag & Drop
    
    # เชื่อมกับหมวดหมู่ทักษะ
    category_id = Column(Integer, ForeignKey("duty_categories.id"), nullable=True)
    category = relationship("DutyCategory", back_populates="duties")
    
    # เชื่อมกับตำแหน่งงานและทักษะย่อย
    job_titles = relationship("JobTitle", secondary=job_title_duty_link, back_populates="duties")
    sub_duties = relationship("SubDuty", back_populates="duty", cascade="all, delete-orphan", order_by="SubDuty.display_order.asc()")

class SubDuty(Base):
    """รายการทักษะย่อย (Sub-Duties) ที่อยู่ในทักษะหลักอีกที"""
    __tablename__ = "sub_duties"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True) # ชื่อทักษะย่อย
    name_th = Column(String, nullable=True)
    name_v3 = Column(String, nullable=True)
    duty_id = Column(Integer, ForeignKey("duties.id", ondelete="CASCADE"))
    tutorial_url = Column(String, nullable=True) # ลิงก์วิดีโอสอน
    display_order = Column(Integer, default=100) # สำหรับการ Drag & Drop
    
    duty = relationship("Duty", back_populates="sub_duties")

class JobDescription(Base):
    """คำอธิบายลักษณะงาน (Job Descriptions) ของแต่ละตำแหน่ง"""
    __tablename__ = "job_descriptions"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String) # เนื้อหาคำอธิบาย
    description_th = Column(String, nullable=True)
    description_v3 = Column(String, nullable=True)
    job_title_id = Column(Integer, ForeignKey("job_titles.id"))
    job_title = relationship("JobTitle", back_populates="descriptions")

class UserDutyEvaluation(Base):
    """ตารางการประเมินทักษะของพนักงาน (Skill Evaluation)"""
    __tablename__ = "user_duty_evaluations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE")) # พนักงานที่ถูกประเมิน
    duty_id = Column(Integer, ForeignKey("duties.id", ondelete="CASCADE")) # ทักษะที่ถูกประเมิน
    score = Column(Integer, default=0) # คะแนน (ดาว 0-5)
    evaluated_by_id = Column(Integer, ForeignKey("users.id"), nullable=True) # ใครเป็นคนประเมิน
    updated_at = Column(String, nullable=True) # วันที่ประเมินล่าสุด

    user = relationship("User", foreign_keys=[user_id], back_populates="duty_evaluations")
    duty = relationship("Duty", backref="user_evaluations")
    evaluator = relationship("User", foreign_keys=[evaluated_by_id])

class UserSubDutyEvaluation(Base):
    """ตารางเช็คลิสต์ทักษะย่อยของพนักงาน (Sub-skill Checklist)"""
    __tablename__ = "user_sub_duty_evaluations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    sub_duty_id = Column(Integer, ForeignKey("sub_duties.id", ondelete="CASCADE"))
    is_completed = Column(Boolean, default=False) # ทำสำเร็จแล้วหรือไม่ (Checklist)
    updated_at = Column(String, nullable=True)

    user = relationship("User", backref="sub_duty_evaluations")
    sub_duty = relationship("SubDuty", backref="user_evaluations")

class EmployeeProfile(Base):
    """ข้อมูลรายละเอียดการจ้างงานของพนักงาน (Employment Information)"""
    __tablename__ = "employee_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)  # เชื่อมกับ User (แบบหนึ่งต่อหนึ่ง)

    # ข้อมูลฝ่ายและตำแหน่งปัจจุบัน
    department = Column(String, nullable=True)     # เช่น office, factory
    job_title = Column(String, nullable=True)      # ชื่อตำแหน่งปัจจุบันเช่น ช่างไม้, พนักงานขาย

    # ข้อมูลการทำงาน
    hire_date = Column(String, nullable=True)              # วันที่เริ่มงาน (YYYY-MM-DD)
    employment_status = Column(String, default='intern')   # สถานะการจ้างงาน (ฝึกงาน, พนักงานประจำ)
    salary_type = Column(String, default='monthly')        # รูปแบบการจ่ายเงิน (monthly, daily)
    base_salary = Column(Integer, default=0)               # ยอดเงินเดือนพื้นฐาน หรือ ค่าจ้างรายวัน
    bank_account = Column(String, nullable=True)           # เลขบัญชีธนาคาร (ถ้ามี)
    termination_date = Column(String, nullable=True)       # วันลาออก (ถ้ามี)

    user = relationship("User", back_populates="employee_profile")
