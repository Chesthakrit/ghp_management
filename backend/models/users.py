from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint, Table
from sqlalchemy.orm import relationship
from database import Base
import json

# Association table for Many-to-Many JobTitles <-> Duties
job_title_duty_link = Table(
    'job_title_duty_link',
    Base.metadata,
    Column('job_title_id', Integer, ForeignKey('job_titles.id', ondelete="CASCADE"), primary_key=True),
    Column('duty_id', Integer, ForeignKey('duties.id', ondelete="CASCADE"), primary_key=True)
)

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    permissions = Column(String)  # JSON string e.g. '["user.manage", "project.view"]'

    users = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    nickname = Column(String, nullable=True)  # ชื่อเล่น

    # Link to Role
    role_id = Column(Integer, ForeignKey("roles.id"))
    role = relationship("Role", back_populates="users")

    is_active = Column(Boolean, default=True)

    # Personal Info (ข้อมูลส่วนตัว)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    birth_date = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    id_card_number = Column(String, nullable=True, unique=True)
    nationality = Column(String, nullable=True)

    # Documents & Photos
    photo_path = Column(String, nullable=True)     # path to portrait photo
    id_doc_path = Column(String, nullable=True)    # path to ID/passport/work-permit image

    # Relationships
    projects = relationship("Project", back_populates="owner")
    employee_profile = relationship("EmployeeProfile", back_populates="user", uselist=False)
    duty_evaluations = relationship("UserDutyEvaluation", foreign_keys="[UserDutyEvaluation.user_id]", back_populates="user", cascade="all, delete-orphan")

    @property
    def permissions(self):
        if self.role and self.role.permissions:
            try:
                return json.loads(self.role.permissions)
            except:
                return []
        return []

    __table_args__ = (
        UniqueConstraint('first_name', 'last_name', name='unique_fullname'),
    )

class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)  # Display name e.g., 'Office'
    value = Column(String, unique=True, index=True) # Value name e.g., 'office'
    job_titles = relationship("JobTitle", back_populates="department", cascade="all, delete-orphan")

class JobTitle(Base):
    __tablename__ = "job_titles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True) # e.g., 'Admin'
    level = Column(Integer, default=0) # e.g. 1 for junior, 2 for senior. Higher level implies skills of lower levels.
    department_id = Column(Integer, ForeignKey("departments.id"))
    department = relationship("Department", back_populates="job_titles")
    descriptions = relationship("JobDescription", back_populates="job_title", cascade="all, delete-orphan")
    duties = relationship("Duty", secondary=job_title_duty_link, back_populates="job_titles")

class DutyCategory(Base):
    __tablename__ = "duty_categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True) # "SketchUp Skill", "Handtool Skill"
    duties = relationship("Duty", back_populates="category", cascade="all, delete-orphan")

class Duty(Base):
    __tablename__ = "duties"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True) # "Skill / Duty name"
    description = Column(String, nullable=True) # "Skill detailed explanation"
    category_id = Column(Integer, ForeignKey("duty_categories.id"), nullable=True)
    category = relationship("DutyCategory", back_populates="duties")
    job_titles = relationship("JobTitle", secondary=job_title_duty_link, back_populates="duties")

class JobDescription(Base):
    __tablename__ = "job_descriptions"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String) # the actual text of the duty
    job_title_id = Column(Integer, ForeignKey("job_titles.id"))
    job_title = relationship("JobTitle", back_populates="descriptions")

class UserDutyEvaluation(Base):
    __tablename__ = "user_duty_evaluations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    duty_id = Column(Integer, ForeignKey("duties.id", ondelete="CASCADE"))
    score = Column(Integer, default=0) # 0-5 stars
    evaluated_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_at = Column(String, nullable=True)

    user = relationship("User", foreign_keys=[user_id], back_populates="duty_evaluations")
    duty = relationship("Duty", backref="user_evaluations")
    evaluator = relationship("User", foreign_keys=[evaluated_by_id])

class EmployeeProfile(Base):
    """ข้อมูลที่เกี่ยวกับบริษัท (Company / HR Information)"""
    __tablename__ = "employee_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)  # 1-to-1 กับ User

    # ตำแหน่งและฝ่าย
    department = Column(String, nullable=True)     # office, center, draftman, production, installation
    job_title = Column(String, nullable=True)      # e.g., CNC Operator, QC Inspector

    # ข้อมูลการจ้างงาน
    hire_date = Column(String, nullable=True)              # วันที่รับสมัคร (YYYY-MM-DD)
    employment_status = Column(String, default='intern')   # intern, permanent, terminated
    termination_date = Column(String, nullable=True)       # วันที่ออกจากงาน (auto-set)

    user = relationship("User", back_populates="employee_profile")