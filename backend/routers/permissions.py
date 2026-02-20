from fastapi import APIRouter

router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"]
)

# Hardcoded list of available permissions
# ในอนาคตอาจจะเก็บใน DB ถ้าต้องการ Dynamic กว่านี้ แต่สำหรับตอนนี้ Hardcode ก็พอ
AVAILABLE_PERMISSIONS = [
    {"id": "user.view", "name": "View Users (ดูรายชื่อผู้ใช้)"},
    {"id": "user.manage", "name": "Manage Users (จัดการผู้ใช้ - เปลี่ยน Role)"},
    {"id": "role.manage", "name": "Manage Roles (จัดการตำแหน่ง - สร้าง/แก้สิทธิ์)"},
    {"id": "project.view_all", "name": "View All Projects (ดูโปรเจกต์ทั้งหมด)"},
    {"id": "project.delete", "name": "Delete Projects (ลบโปรเจกต์)"},
    # เพิ่มสิทธิ์อื่นๆ ที่นี่
]

@router.get("/")
def get_permissions():
    return AVAILABLE_PERMISSIONS
