from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from models import users as models
from hashing import Hash # เรียกใช้ตัวเช็ครหัสผ่านที่เราแก้ชื่อไฟล์ไปเมื่อกี้
from datetime import datetime, timedelta
from jose import jwt

router = APIRouter(tags=["Authentication"])

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
    # 1. ค้นหา User จาก username ที่ส่งมา
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