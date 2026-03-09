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
    # สิทธิ์การเข้าถึงหน้าเพจหลัก (Page Access)
    {"id": "page.factory", "name": "เข้าถึงหน้า: ฝ่ายผลิต (Factory Page)"},
    {"id": "page.sales", "name": "เข้าถึงหน้า: ฝ่ายขาย (Sales Page)"},
    {"id": "page.warehouse", "name": "เข้าถึงหน้า: คลังสินค้า (Warehouse Page)"},
    {"id": "page.office", "name": "เข้าถึงหน้า: สำนักงาน (Office Page)"},
    {"id": "page.accounts", "name": "เข้าถึงหน้า: การเงินและบัญชี (Accounts Page)"},
    # สามารถเพิ่มสิทธิ์ใหม่ๆ เข้าไปในอนาคตได้ที่นี่
]

@router.get("/")
def get_permissions(current_user: models.User = Depends(oauth2.get_current_user)):
    """API สำหรับดึงรายการสิทธิ์ทั้งหมดที่แอดมินสามารถนำไปจัดกลุ่มเป็น Role ได้"""
    return AVAILABLE_PERMISSIONS

