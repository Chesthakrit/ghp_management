from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base
import json

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