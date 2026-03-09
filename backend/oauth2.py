"""
ไฟล์สำหรับจัดการระบบความปลอดภัยและการยืนยันตัวตนด้วย OAuth2 และ JWT (JSON Web Token)
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from database import get_db
from models import users as models

# --- การกำหนดค่าความปลอดภัย (Configuration) ---
# SECRET_KEY: ใช้สำหรับเข้ารหัสและถอดรหัส Token (ควรเก็บเป็นอิสระและมีความปลอดภัยสูง)
SECRET_KEY = "1900" 
# ALGORITHM: อัลกอริทึมที่ใช้ในการสร้างรหัส Digital Signature
ALGORITHM = "HS256"

# กำหนดรูปแบบการรับ Token จาก Header ของคำขอ
# tokenUrl="login" บอกว่าพาร์ทที่ใช้รับรหัสผ่านเพื่อแลก Token คือ /login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# --- ฟังก์ชันตรวจสอบบัตรผ่าน (Dependency: get_current_user) ---
# ทำหน้าที่เหมือน "ยามเฝ้าประตู" ที่ตรวจบัตร (Token) ก่อนอนุญาตให้เข้าถึง API
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # เตรียม Exception สำหรับกรณีที่ยืนยันตัวตนไม่ผ่าน
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="บัตรผ่านไม่ถูกต้อง หรือหมดอายุแล้ว",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 1. ถอดรหัส Token (Decoding)
        # ตรวจสอบว่า Token ถูกสร้างด้วย SECRET_KEY และ ALGORITHM ที่ถูกต้องหรือไม่
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # ดึงชื่อผู้ใช้ (username) จากฟิลด์ "sub" (Subject) ใน payload
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
            
    except JWTError:
        # หากเกิดข้อผิดพลาดในการแกะรหัส (เช่น Token ถูกแก้ไข หรือหมดอายุ)
        raise credentials_exception

    # 2. ค้นหาข้อมูลผู้ใช้ในฐานข้อมูล
    # หลังจากได้ username จาก Token แล้ว ต้องเช็คอีกทีว่ามีตัวตนอยู่ในระบบจริงๆ หรือไม่
    user = db.query(models.User).filter(models.User.username == username).first()
    
    if user is None:
        raise credentials_exception
    
    # 3. ส่งคืนข้อมูลผู้ใช้ออกไป
    # หากทุกอย่างถูกต้อง ฟังก์ชันนี้จะส่ง Object ของ User คนนั้นกลับไปให้ Endpoint ใช้งาน
    return user

# --- ฟังก์ชันตรวจสอบสิทธิ์แอดมิน (Dependency: check_admin) ---
def check_admin(current_user: models.User = Depends(get_current_user)):
    """ยามเฝ้าประตูชั้นที่ 2: ตรวจสอบว่าเป็น Admin หรือไม่"""
    is_admin = (current_user.role and current_user.role.name.lower() == 'admin') or \
               (current_user.username.lower() == 'admin')
    
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ไม่มีสิทธิ์ในการดำเนินการนี้ (เฉพาะแอดมินเท่านั้น)"
        )
    return current_user

# --- ฟังก์ชันตรวจสอบสิทธิ์จัดการข้อมูลพนักงาน (Dependency: check_can_manage_users) ---
def check_can_manage_users(current_user: models.User = Depends(get_current_user)):
    """ยามเฝ้าประตูสำหรับ HR: ตรวจสอบว่าเป็น Admin หรือมีสิทธิ์จัดการพนักงาน"""
    is_admin = (current_user.role and current_user.role.name.lower() == 'admin') or \
               (current_user.username.lower() == 'admin')
    
    perms = current_user.permissions or []
    if not is_admin and 'user.manage' not in perms:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ไม่มีสิทธิ์เข้าถึงหรือจัดการข้อมูลพนักงาน"
        )
    return current_user
