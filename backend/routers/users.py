from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import users as models
from schemas import users as schemas
from hashing import Hash
import oauth2
from typing import List

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

import os

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(os.path.join(UPLOAD_DIR, "photos"),  exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, "id_docs"), exist_ok=True)

# ─────────────────────────────────────────────
#  สร้าง User ใหม่ (Register)
# ─────────────────────────────────────────────
@router.post("/", response_model=schemas.UserOut)
def create_user(request: schemas.UserCreate, db: Session = Depends(get_db)):

    # ── Required field checks ──────────────────
    required = {
        "first_name": request.first_name,
        "last_name":  request.last_name,
        "birth_date": request.birth_date,
        "phone":      request.phone,
        "id_card_number": request.id_card_number,
        "nationality": request.nationality,
    }
    missing = [k for k, v in required.items() if not v or not str(v).strip()]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing required fields: {', '.join(missing)}")

    # ── Duplicate checks ───────────────────────
    if db.query(models.User).filter(models.User.username == request.username).first():
        raise HTTPException(status_code=400, detail="Username นี้มีผู้ใช้งานแล้วครับ")

    if db.query(models.User).filter(models.User.id_card_number == request.id_card_number.strip()).first():
        raise HTTPException(status_code=400, detail="เลขบัตร/พาสปอร์ตนี้มีในระบบแล้วครับ")

    if db.query(models.User).filter(
        models.User.first_name == request.first_name.strip(),
        models.User.last_name  == request.last_name.strip()
    ).first():
        raise HTTPException(status_code=400, detail=f"ชื่อ {request.first_name} {request.last_name} มีในระบบแล้วครับ")

    # ── Create user ────────────────────────────
    role_db = db.query(models.Role).filter(models.Role.name == "employee").first()

    new_user = models.User(
        username=request.username,
        nickname=request.nickname or None,
        password=Hash.bcrypt(request.password),
        role=role_db,
        first_name=request.first_name.strip(),
        last_name=request.last_name.strip(),
        birth_date=request.birth_date.strip(),
        phone=request.phone.strip(),
        id_card_number=request.id_card_number.strip(),
        nationality=request.nationality.strip(),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # สร้าง EmployeeProfile — hire_date = วันที่ register อัตโนมัติ
    from datetime import date
    new_profile = models.EmployeeProfile(
        user_id=new_user.id,
        hire_date=str(date.today())
    )
    db.add(new_profile)
    db.commit()
    db.refresh(new_user)

    return new_user


# ─────────────────────────────────────────────
#  Upload Photo & ID Document
# ─────────────────────────────────────────────
from fastapi import UploadFile, File
import shutil

@router.post("/{user_id}/upload")
def upload_user_files(
    user_id: int,
    photo: UploadFile = File(None),
    id_doc: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    def delete_old_files(folder: str, stem: str):
        """ลบไฟล์เก่าทุก extension เพื่อไม่ให้สะสม"""
        folder_path = os.path.join(UPLOAD_DIR, folder)
        for f in os.listdir(folder_path):
            if f.startswith(stem + ".") or f == stem:
                try:
                    os.remove(os.path.join(folder_path, f))
                except OSError:
                    pass

    if photo and photo.filename:
        ext = os.path.splitext(photo.filename)[-1].lower()
        delete_old_files("photos", f"user_{user_id}")
        path = os.path.join(UPLOAD_DIR, "photos", f"user_{user_id}{ext}")
        with open(path, "wb") as f:
            shutil.copyfileobj(photo.file, f)
        user.photo_path = f"uploads/photos/user_{user_id}{ext}"

    if id_doc and id_doc.filename:
        ext = os.path.splitext(id_doc.filename)[-1].lower()
        delete_old_files("id_docs", f"user_{user_id}")
        path = os.path.join(UPLOAD_DIR, "id_docs", f"user_{user_id}{ext}")
        with open(path, "wb") as f:
            shutil.copyfileobj(id_doc.file, f)
        user.id_doc_path = f"uploads/id_docs/user_{user_id}{ext}"

    db.commit()
    db.refresh(user)
    return {"photo_path": user.photo_path, "id_doc_path": user.id_doc_path}


# ─────────────────────────────────────────────
#  ดูรายชื่อ User ทั้งหมด (Admin Only)
# ─────────────────────────────────────────────
@router.get("/", response_model=List[schemas.UserOut])
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    # admin ขึ้นก่อนเสมอ
    users.sort(key=lambda u: (0 if (u.role and u.role.name == 'admin') else 1, u.id))
    return users


# ─────────────────────────────────────────────
#  ดูข้อมูลส่วนตัว (ต้อง Login)
# ─────────────────────────────────────────────
@router.get("/me", response_model=schemas.UserOut)
def read_users_me(current_user: models.User = Depends(oauth2.get_current_user)):
    return current_user


# ─────────────────────────────────────────────
#  ดูข้อมูลรายบุคคล (Admin Only หรือ เจ้าของ)
# ─────────────────────────────────────────────
@router.get("/{user_id}", response_model=schemas.UserOut)
def read_user(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(oauth2.get_current_user)
):
    # เจ้าของดูได้ หรือ คนที่มีสิทธิ์ admin/manage ดูได้
    is_admin = (current_user.role and current_user.role.name.lower() == 'admin') or (current_user.username.lower() == 'admin')
    
    if not is_admin and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="ไม่มีสิทธิ์เข้าถึงข้อมูลผู้ใช้อื่น")
        
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ─────────────────────────────────────────────
#  Admin: แก้ไขข้อมูลส่วนตัว User
# ─────────────────────────────────────────────
@router.put("/{user_id}", response_model=schemas.UserOut)
def update_user(
    user_id: int,
    request: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    is_admin = (current_user.role and current_user.role.name.lower() == 'admin') or (current_user.username.lower() == 'admin')
    if not is_admin and 'user.manage' not in current_user.permissions:
        raise HTTPException(status_code=403, detail="ไม่มีสิทธิ์จัดการผู้ใช้")


    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 🔒 Block modifying Master Admin entirely
    is_target_admin = (user.role and user.role.name.lower() == 'admin') or (user.username.lower() == 'admin')
    if is_target_admin:
        raise HTTPException(status_code=403, detail="ระบบไม่อนุญาตให้แก้ไขข้อมูล Master Admin ได้ครับ")

    if request.role is not None:
        new_role = db.query(models.Role).filter(models.Role.name == request.role).first()
        if not new_role:
            raise HTTPException(status_code=400, detail=f"ไม่พบ Role: {request.role}")
        user.role = new_role

    if request.is_active is not None:
        user.is_active = request.is_active
    if request.first_name is not None:
        user.first_name = request.first_name
    if request.last_name is not None:
        user.last_name = request.last_name
    if request.birth_date is not None:
        user.birth_date = request.birth_date
    if request.phone is not None:
        user.phone = request.phone
    if request.nickname is not None:
        user.nickname = request.nickname
    if request.nationality is not None:
        user.nationality = request.nationality
    if request.id_card_number is not None:
        user.id_card_number = request.id_card_number

    db.commit()
    db.refresh(user)
    return user


# ─────────────────────────────────────────────
#  Admin: แก้ไขข้อมูลบริษัท (Employee Profile)
# ─────────────────────────────────────────────
@router.put("/{user_id}/profile", response_model=schemas.UserOut)
def update_employee_profile(
    user_id: int,
    request: schemas.EmployeeProfileUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    is_admin = (current_user.role and current_user.role.name.lower() == 'admin') or (current_user.username.lower() == 'admin')
    if not is_admin and 'user.manage' not in current_user.permissions:
        raise HTTPException(status_code=403, detail="ไม่มีสิทธิ์จัดการผู้ใช้")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 🔒 Block modifying Master Admin profile
    is_target_admin = (user.role and user.role.name.lower() == 'admin') or (user.username.lower() == 'admin')
    if is_target_admin:
        raise HTTPException(status_code=403, detail="ระบบไม่อนุญาตให้แก้ไขข้อมูลบริษัทของ Master Admin ได้ครับ")

    # ดึง profile หรือสร้างใหม่ถ้าไม่มี
    profile = db.query(models.EmployeeProfile).filter(
        models.EmployeeProfile.user_id == user_id
    ).first()
    if not profile:
        profile = models.EmployeeProfile(user_id=user_id)
        db.add(profile)

    if request.department is not None:
        profile.department = request.department
    if request.job_title is not None:
        profile.job_title = request.job_title
    if request.hire_date is not None:
        profile.hire_date = request.hire_date
    if request.employment_status is not None:
        profile.employment_status = request.employment_status
        # auto-set termination_date
        if request.employment_status == 'terminated' and profile.termination_date is None:
            from datetime import date
            profile.termination_date = str(date.today())
        elif request.employment_status != 'terminated':
            profile.termination_date = None

    db.commit()
    db.refresh(user)
    return user


# ─────────────────────────────────────────────
#  (Legacy) Update Role only
# ─────────────────────────────────────────────
from pydantic import BaseModel
class UserRoleUpdate(BaseModel):
    role: str

@router.put("/{user_id}/role")
def update_user_role(user_id: int, request: UserRoleUpdate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    new_role = db.query(models.Role).filter(models.Role.name == request.role).first()
    if not new_role:
        raise HTTPException(status_code=400, detail="Invalid role name")
    user.role = new_role
    db.commit()
    return {"message": "Role updated successfully"}


# ─────────────────────────────────────────────
#  Delete User (Admin only)
# ─────────────────────────────────────────────
@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    is_admin = (current_user.role and current_user.role.name.lower() == 'admin') or (current_user.username.lower() == 'admin')
    if not is_admin and 'user.manage' not in current_user.permissions:
        raise HTTPException(status_code=403, detail="Permission denied")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 🔒 Block deleting Master Admin
    if user.role and user.role.name == 'admin':
        raise HTTPException(status_code=403, detail="Cannot delete the Master Admin account")

    # Delete employee profile first (cascade)
    profile = db.query(models.EmployeeProfile).filter(models.EmployeeProfile.user_id == user_id).first()
    if profile:
        db.delete(profile)

    # ลบไฟล์รูปและเอกสารออกจาก disk
    def remove_file(relative_path: str):
        if not relative_path:
            return
        full_path = os.path.join(os.path.dirname(__file__), "..", relative_path)
        full_path = os.path.normpath(full_path)
        try:
            if os.path.isfile(full_path):
                os.remove(full_path)
        except OSError:
            pass

    remove_file(user.photo_path)
    remove_file(user.id_doc_path)

    db.delete(user)
    db.commit()
    return
