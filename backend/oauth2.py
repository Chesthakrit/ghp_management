"""
ระบบความปลอดภัยและการยืนยันตัวตนด้วย OAuth2 + JWT (JSON Web Token)
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from database import get_db
from models import users as models

# ─── Configuration ───────────────────────────────────────────────────────────
SECRET_KEY = "1900"
ALGORITHM  = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# ─── Internal Helpers ─────────────────────────────────────────────────────────

def _is_admin(user: models.User) -> bool:
    """ตรวจสอบว่า user เป็น Admin (ตาม Role หรือ Username) หรือไม่"""
    return (
        (user.role and user.role.name.lower() == "admin")
        or user.username.lower() == "admin"
    )


def _has_perm(user: models.User, perm: str) -> bool:
    """ตรวจสอบว่า user มีสิทธิ์ที่ระบุหรือไม่"""
    return perm in (user.permissions or [])


def _require(user: models.User, perm: str, detail: str):
    """ตรวจสอบสิทธิ์ — ถ้าไม่ผ่านให้ raise 403 พร้อม detail ที่กำหนด"""
    if not _is_admin(user) and not _has_perm(user, perm):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


# ─── Core Auth ────────────────────────────────────────────────────────────────

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    """ถอดรหัส JWT Token และส่งคืน User Object (ใช้เป็น Dependency)"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="บัตรผ่านไม่ถูกต้อง หรือหมดอายุแล้ว",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload  = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user


def verify_token(token: str):
    """ถอดรหัส Token โดยตรง (ใช้กับไฟล์/วิดีโอ) — คืน username หรือ None"""
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


# ─── Permission Guards ────────────────────────────────────────────────────────

def check_admin(current_user: models.User = Depends(get_current_user)) -> models.User:
    """อนุญาตเฉพาะ Admin เท่านั้น"""
    if not _is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="หน้านี้เฉพาะแอดมินระบบเท่านั้นที่เข้าถึงได้")
    return current_user


def check_can_manage_access(current_user: models.User = Depends(get_current_user)) -> models.User:
    """ต้องเป็น Admin หรือมีสิทธิ์ 'page.access'"""
    _require(current_user, "page.access", "ไม่มีสิทธิ์เข้าถึงหรือจัดการระบบสิทธิ์พนักงาน")
    return current_user


def check_can_manage_users(current_user: models.User = Depends(get_current_user)) -> models.User:
    """ต้องเป็น Admin หรือมีสิทธิ์ 'page.usermanagement' หรือ 'user.manage'"""
    if not _is_admin(current_user) and not any(
        _has_perm(current_user, p) for p in ("user.manage", "page.usermanagement")
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="ไม่มีสิทธิ์เข้าถึงหรือจัดการข้อมูลพนักงาน")
    return current_user


def check_can_manage_hr_settings(current_user: models.User = Depends(get_current_user)) -> models.User:
    """ต้องเป็น Admin หรือมีสิทธิ์ 'page.hr'"""
    _require(current_user, "page.hr", "ไม่มีสิทธิ์จัดการข้อมูลโครงสร้างองค์กร (แผนก/ตำแหน่ง)")
    return current_user


def check_can_add_user(current_user: models.User = Depends(get_current_user)) -> models.User:
    """ต้องเป็น Admin หรือมีสิทธิ์ 'action.user.add'"""
    _require(current_user, "action.user.add", "ไม่มีสิทธิ์เพิ่มพนักงานใหม่")
    return current_user


def check_can_edit_user_id(current_user: models.User = Depends(get_current_user)) -> models.User:
    """ต้องเป็น Admin หรือมีสิทธิ์ 'action.user.edit_id'"""
    _require(current_user, "action.user.edit_id", "ไม่มีสิทธิ์แก้ไขบัตรพนักงาน")
    return current_user


def check_can_edit_user_profile(current_user: models.User = Depends(get_current_user)) -> models.User:
    """ต้องเป็น Admin หรือมีสิทธิ์ 'action.user.edit_profile'"""
    _require(current_user, "action.user.edit_profile", "ไม่มีสิทธิ์แก้ไขข้อมูลพนักงาน")
    return current_user


def check_can_delete_user(current_user: models.User = Depends(get_current_user)) -> models.User:
    """ต้องเป็น Admin หรือมีสิทธิ์ 'action.user.delete'"""
    _require(current_user, "action.user.delete", "ไม่มีสิทธิ์ลบรายชื่อพนักงาน")
    return current_user
