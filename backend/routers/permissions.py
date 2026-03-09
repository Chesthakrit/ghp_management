"""
ไฟล์กำหนดรายการสิทธิ์การเข้าใช้งาน (Permissions Router)
ใช้สำหรับจัดส่งรายการสิทธิ์ (Permissions) ทั้งหมดที่ระบบมี 
เพื่อให้หน้าบ้าน (Frontend) นำไปแสดงผลให้แอดมินเลือกติ๊กถูกเวลาสร้าง Role
"""

from fastapi import APIRouter, Depends
import oauth2
from models import users as models

router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"]
)

# รายการสิทธิ์ทั้งหมดที่ระบบรองรับ (Hardcoded list)
# ในรายละเอียกประกอบด้วย id (ใช้ในโค้ด) และ name (แสดงผลหน้าเว็บ)
AVAILABLE_PERMISSIONS = [
    {"id": "user.view", "name": "ดูรายชื่อพนักงาน (View Users)"},
    {"id": "user.manage", "name": "จัดการข้อมูลพนักงาน/ประเมินผล (Manage Users / Evaluation)"},
    {"id": "role.manage", "name": "จัดการตำแหน่งและสิทธิ์การใช้งาน (Manage Roles)"},
    {"id": "project.view_all", "name": "ดูโปรเจกต์ของทุกคน (View All Projects)"},
    {"id": "project.delete", "name": "ลบโปรเจกต์ (Delete Projects)"},

    {"id": "page.usermanagement", "name": "หน้า: จัดการพนักงาน (User Management Page)"},
    {"id": "action.user.edit_identity", "name": "ปุ่ม: แก้ไขข้อมูลตัวตน (Edit Employee Identity)"},
    {"id": "action.user.edit_employment", "name": "ปุ่ม: จัดการการจ้างงานและสิทธิ์ (Employment & Access Control)"},
    {"id": "action.user.delete", "name": "ปุ่ม: ลบพนักงาน (Delete User)"},
    {"id": "action.user.view_profile", "name": "ปุ่ม: ดูหน้าโปรไฟล์พนักงาน (View Profile Page)"},

    # --- Admin Panel Pages ---
    {"id": "page.hr", "name": "หน้า: ตั้งค่าระบบ HR (HR Settings)"},
    {"id": "action.hr.add_dept", "name": "ปุ่ม: เพิ่มแผนก (Add Department)"},
    {"id": "action.hr.edit_name", "name": "ปุ่ม: แก้ไขชื่อแผนก/ตำแหน่ง (Edit Dept/JT Name)"},
    {"id": "action.hr.delete", "name": "ปุ่ม: ลบแผนก/ตำแหน่ง (Delete Dept/JT)"},
    {"id": "action.hr.add_jt", "name": "ปุ่ม: เพิ่มตำแหน่งงาน (Add Job Title)"},
    {"id": "action.hr.manage_jt_skills", "name": "ปุ่ม: จัดการทักษะของตำแหน่ง (Manage JT Skills)"},
    {"id": "action.hr.add_tag", "name": "ปุ่ม: เพิ่มแท็กทักษะ (Add Skill Tag)"},
    {"id": "action.hr.edit_tag", "name": "ปุ่ม: แก้ไขชื่อแท็ก (Edit Skill Tag)"},
    {"id": "action.hr.delete_tag", "name": "ปุ่ม: ลบแท็กทักษะ (Delete Skill Tag)"},
    {"id": "action.hr.add_skill", "name": "ปุ่ม: เพิ่มทักษะในคลัง (Add Skill to Library)"},
    {"id": "action.hr.edit_skill", "name": "ปุ่ม: แก้ไขทักษะในคลัง (Edit Skill in Library)"},
    {"id": "action.hr.delete_skill", "name": "ปุ่ม: ลบทักษะในคลัง (Delete Skill from Library)"},
    {"id": "page.salary", "name": "หน้า: ตั้งค่าฐานเงินเดือน (Salary Settings)"},
    {"id": "page.access", "name": "หน้า: กำหนดสิทธิ์การเข้าถึง (Access Control)"},

    # --- Other Page Access ---
    {"id": "page.factory", "name": "หน้า: ฝ่ายผลิต (Factory Page)"},
    {"id": "page.sales", "name": "หน้า: ฝ่ายขาย (Sales Page)"},
    {"id": "page.warehouse", "name": "หน้า: คลังสินค้า (Warehouse Page)"},
    {"id": "page.office", "name": "หน้า: สำนักงาน (Office Page)"},
    {"id": "page.accounts", "name": "หน้า: การเงินและบัญชี (Accounts Page)"},
    # สามารถเพิ่มสิทธิ์ใหม่ๆ เข้าไปในอนาคตได้ที่นี่
]

@router.get("/")
def get_permissions(current_user: models.User = Depends(oauth2.get_current_user)):
    """API สำหรับดึงรายการสิทธิ์ทั้งหมดที่แอดมินสามารถนำไปจัดกลุ่มเป็น Role ได้"""
    return AVAILABLE_PERMISSIONS

