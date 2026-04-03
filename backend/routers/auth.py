"""
ไฟล์จัดการระบบการยืนยันตัวตน (Authentication Router)
ทำหน้าที่ดูแลการเข้าสู่ระบบ (Login) และการสร้าง Token สำหรับเข้าใช้งาน API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from models import users as models
from hashing import Hash 
from datetime import datetime, timedelta
from jose import jwt

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"] # จัดหมวดหมู่ในหน้า Swagger UI
)

# --- การตั้งค่าสำหรับการสร้าง Token (JWT Config) ---
SECRET_KEY = "1900"             # กุญแจลับสำหรับเข้ารหัส
ALGORITHM = "HS256"              # อัลกอริทึมที่ใช้
ACCESS_TOKEN_EXPIRE_MINUTES = 1440 # ระยะเวลาที่ Token สามารถใช้งานได้ (24 ชม.)

def create_access_token(data: dict):
    """ฟังก์ชันสำหรับสร้างรหัส JWT (Access Token)"""
    to_encode = data.copy()
    # กำหนดเวลาหมดอายุของบัตรผ่านใบนี้
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # เข้ารหัสข้อมูลทั้งหมดเป็นสายอักขระ JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/login")
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """API สำหรับการเข้าสู่ระบบ"""
    
    # 1. ตรวจสอบกรณีพิเศษ: การล็อกอินด้วยบัญชี Master Admin
    # (หากระบุ username เป็น admin และ password ตามที่กำหนด)
    if request.username == "admin" and request.password == "admin9999":
        user = db.query(models.User).filter(models.User.username == "admin").first()
        if not user:
            # หากยังไม่มี User admin ในฐานข้อมูล ให้สร้างขึ้นมาใหม่อัตโนมัติ
            admin_role = db.query(models.Role).filter(models.Role.name == "admin").first()
            new_admin = models.User(
                username="admin",
                password=Hash.bcrypt("admin9999"), # เข้ารหัสก่อนบันทึก
                role=admin_role,
                first_name="Master",
                last_name="Admin"
            )
            db.add(new_admin)
            db.commit()
            db.refresh(new_admin)
            user = new_admin 
    else:
        # 2. กรณีการล็อกอินปกติ: ค้นหาชื่อผู้ใช้จากฐานข้อมูล
        user = db.query(models.User).filter(models.User.username == request.username).first()

        # หากไม่พบผู้ใช้งาน หรือรหัสผ่านไม่ถูกต้อง (Verify Password)
        if not user or not Hash.verify(request.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="ชื่อผู้ใช้งานหรือรหัสผ่านไม่ถูกต้อง"
            )

    # 3. ตรวจสอบสถานะการใช้งานพนักงาน (Block logic)
    if user.username != "admin": # บัญชี admin หลักจะเข้าได้เสมอ
        # 3.1 ตรวจสอบว่าบัญชีถูกปิดใช้งาน (Deactivated) หรือไม่
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="บัญชีของคุณถูกปิดใช้งานชั่วคราว กรุณาติดต่อผู้ดูแลระบบ"
            )
        
        # 3.2 ตรวจสอบสถานะการจ้างงาน (เช่น หากลาออกไปแล้วจะเข้าไม่ได้)
        if user.employee_profile and user.employee_profile.employment_status == 'terminated':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="ไม่สามารถเข้าสู่ระบบได้ เนื่องจากบัญชีพนักงานนี้ถูกยกเลิกแล้ว"
            )

    # 4. หากผ่านการตรวจสอบทั้งหมด ให้สร้าง Token และส่งกลับไป
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

from pydantic import BaseModel

class AdminCodeRequest(BaseModel):
    code: str

@router.post("/verify-admin-code")
def verify_admin_code(request: AdminCodeRequest):
    """API สำหรับตรวจสอบรหัสแอดมินก่อนอนุญาตให้เข้าหน้าสมัครสมาชิก"""
    if request.code == "admin9999":
        return {"valid": True}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="รหัสแอดมินไม่ถูกต้อง"
        )
