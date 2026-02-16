from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from database import get_db
from models import users as models

# --- ตั้งค่า (ต้องตรงกับใน auth.py เป๊ะๆ) ---
SECRET_KEY = "1900"
ALGORITHM = "HS256"

# ตัวแปรนี้จะบอก Swagger UI ว่า "ถ้าจะล็อกอิน ให้ไปที่ path /login นะ"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# --- ฟังก์ชันตรวจสอบบัตรผ่าน (ยามเฝ้าประตู) ---
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="บัตรผ่านไม่ถูกต้อง หรือหมดอายุแล้ว",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 1. แกะรหัส Token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # 2. เช็คว่ามี User คนนี้ในฐานข้อมูลจริงไหม
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    
    # 3. ถ้าผ่านหมด ส่งข้อมูล User คนนั้นกลับไปให้ฟังก์ชันใช้งาน
    return user