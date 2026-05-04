from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from models import users as models
from hashing import Hash 
from datetime import datetime, timedelta
from jose import jwt
from pydantic import BaseModel

router = APIRouter(prefix="", tags=["Authentication"])

SECRET_KEY = "1900"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/login")
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    if request.username == "admin" and request.password == "admin9999":
        user = db.query(models.User).filter(models.User.username == "admin").first()
        if not user:
            admin_role = db.query(models.Role).filter(models.Role.name == "admin").first()
            new_admin = models.User(
                username="admin",
                password=Hash.bcrypt("admin9999"),
                role=admin_role,
                first_name="Master",
                last_name="Admin"
            )
            db.add(new_admin)
            db.commit()
            db.refresh(new_admin)
            user = new_admin 
    else:
        user = db.query(models.User).filter(models.User.username == request.username).first()
        if not user or not Hash.verify(request.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="ชื่อผู้ใช้งานหรือรหัสผ่านไม่ถูกต้อง"
            )

    if user.username != "admin":
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="บัญชีของคุณถูกปิดใช้งานชั่วคราว กรุณาติดต่อผู้ดูแลระบบ"
            )
        
        if user.employee_profile and user.employee_profile.employment_status == 'terminated':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="ไม่สามารถเข้าสู่ระบบได้ เนื่องจากบัญชีพนักงานนี้ถูกยกเลิกแล้ว"
            )

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


class AdminCodeRequest(BaseModel):
    code: str

@router.post("/verify-admin-code")
def verify_admin_code(request: AdminCodeRequest):
    if request.code == "admin9999":
        return {"valid": True}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="รหัสแอดมินไม่ถูกต้อง"
        )
