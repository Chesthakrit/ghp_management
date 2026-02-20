# --------------------------------------------------------------------------------
# ไฟล์: backend/routers/auth.py
# หน้าที่: จัดการระบบล็อกอิน (Login) และออกใบผ่านทาง (JWT Token)
# --------------------------------------------------------------------------------
# รายละเอียด:
# - รับ Username/Password จากหน้าเว็บ
# - ตรวจสอบว่ามี User นี้จริงไหม และรหัสผ่านถูกไหม (Verify Password)
# - ถ้าถูกต้อง จะสร้าง "Access Token" (เหมือนบัตรผ่านเข้างาน) ส่งกลับไปให้หน้าเว็บ
# - ใช้ Token นี้ยืนยันตัวตนในการเรียกใช้งาน API อื่นๆ ต่อไป
# --------------------------------------------------------------------------------
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from models import users as models
from hashing import Hash # เรียกใช้ตัวเช็ครหัสผ่านที่เราแก้ชื่อไฟล์ไปเมื่อกี้
from datetime import datetime, timedelta
from jose import jwt

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# --- ตั้งค่าความลับของบัตรผ่าน (JWT Config) ---
# ในงานจริง โค้ดลับนี้ต้องซ่อนไว้อย่างดี ห้ามให้ใครรู้
SECRET_KEY = "1900"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # บัตรหมดอายุใน 30 นาที

# ฟังก์ชันสร้างบัตรผ่าน (Create Token)
def create_access_token(data: dict):
    to_encode = data.copy()
    # กำหนดเวลาหมดอายุ
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # สร้างรหัส JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- API สำหรับ Login ---
@router.post("/login")
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 1. พิเศษ: เช็คว่าเป็น "Master Admin" หรือไม่ (User: admin / Pass: admin9999)
    if request.username == "admin" and request.password == "admin9999":
        # เช็คว่ามี User admin ในระบบหรือยัง
        user = db.query(models.User).filter(models.User.username == "admin").first()
        if not user:
            # ถ้ายังไม่มี ให้สร้างใหม่เลย (Auto-Register Admin)
            # Find Admin Role
            admin_role = db.query(models.Role).filter(models.Role.name == "admin").first()
            
            new_admin = models.User(
                username="admin",
                password=Hash.bcrypt("admin9999"), # เข้ารหัสก่อนเก็บ
                role=admin_role, # กำหนดเป็น Admin Role Object
                email="admin@ghp.com",
                first_name="Master",
                last_name="Admin"
            )
            db.add(new_admin)
            db.commit()
            db.refresh(new_admin)
            user = new_admin 
        # ถ้ามีแล้ว หรือเพิ่งสร้างเสร็จ ก็ให้ผ่านไปขั้นตอนสร้าง Token ได้เลย
    else:
        # 1. (ปกติ) ค้นหา User จาก username ที่ส่งมา
        user = db.query(models.User).filter(models.User.username == request.username).first()

        # 2. ถ้าหาไม่เจอ ให้บอกว่าข้อมูลผิด (ไม่บอกว่าผิดที่ username เพื่อความปลอดภัย)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials")

        # 3. เช็ค Password ว่าตรงกันไหม (ใช้ hashing.py)
        if not Hash.verify(request.password, user.password):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials")

    # 4. ถ้าผ่านหมด ให้สร้างบัตรผ่าน (Token)
    access_token = create_access_token(data={"sub": user.username})

    # 5. ส่งบัตรผ่านกลับไปให้ User
    return {"access_token": access_token, "token_type": "bearer"}

# --- API สำหรับเช็ครหัส Admin (ก่อนสมัครสมาชิก) ---
from pydantic import BaseModel

class AdminCodeRequest(BaseModel):
    code: str

@router.post("/verify-admin-code")
def verify_admin_code(request: AdminCodeRequest):
    # รหัสลับสำหรับปลดล็อกหน้าสมัครสมาชิก
    if request.code == "admin9999":
        return {"valid": True}
    else:
        # ถ้าผิด ให้ส่ง Error กลับไป
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid Admin Code"
        )