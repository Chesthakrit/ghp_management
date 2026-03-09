"""
ไฟล์จัดการข้อมูลผู้ใช้งาน (Users Router)
ทำหน้าที่จัดการการลงทะเบียน, การอัปโหลดไฟล์, การดูข้อมูล และการแก้ไขข้อมูลพนักงาน
"""

import os
import shutil
from datetime import date
from typing import List

from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from database import get_db
from models import users as models
from schemas import users as schemas
from hashing import Hash
import oauth2

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# การกำหนดค่าสำหรับการอัปโหลดไฟล์
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
# สร้างโฟลเดอร์ย่อยรอไว้หากยังไม่มี
os.makedirs(os.path.join(UPLOAD_DIR, "photos"),  exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, "id_docs"), exist_ok=True)

# ─────────────────────────────────────────────
#  สร้าง User ใหม่ (ลงทะเบียนพนักงาน)
# ─────────────────────────────────────────────
@router.post("/", response_model=schemas.UserOut)
def create_user(request: schemas.UserCreate, db: Session = Depends(get_db)):
    """API สำหรับลงทะเบียนพนักงานใหม่เข้าระบบ"""

    # 1. ตรวจสอบข้อมูลที่จำเป็น (Required fields)
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
        raise HTTPException(status_code=400, detail=f"กรุณากรอกข้อมูลให้ครบถ้วน: {', '.join(missing)}")

    # 2. ตรวจสอบข้อมูลซ้ำ (Duplicate checks)
    # เช็ค Username ซ้ำ
    if db.query(models.User).filter(models.User.username == request.username).first():
        raise HTTPException(status_code=400, detail="ชื่อผู้ใช้งาน (Username) นี้ถูกใช้ไปแล้ว")

    # เช็คเลขบัตรประชาชน/พาสปอร์ต ซ้ำ
    if db.query(models.User).filter(models.User.id_card_number == request.id_card_number.strip()).first():
        raise HTTPException(status_code=400, detail="เลขบัตรประชาชน/พาสปอร์ตนี้มีอยู่ในระบบแล้ว")

    # เช็คชื่อ-นามสกุลซ้ำ
    if db.query(models.User).filter(
        models.User.first_name == request.first_name.strip(),
        models.User.last_name  == request.last_name.strip()
    ).first():
        raise HTTPException(status_code=400, detail=f"ชื่อ {request.first_name} {request.last_name} มีอยู่ในระบบแล้ว")

    # 3. เริ่มกระบวนการสร้างผู้ใช้งาน
    # ดึง Role พนักงาน (employee) มาเตรียมไว้
    role_db = db.query(models.Role).filter(models.Role.name == "employee").first()

    new_user = models.User(
        username=request.username,
        nickname=request.nickname or None,
        password=Hash.bcrypt(request.password), # เข้ารหัสผ่านก่อนบันทึก
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

    # 4. สร้างโปรไฟล์พนักงาน (Employee Profile) ควบคู่ไปด้วย
    # กำหนดวันเริ่มงาน (hire_date) เป็นวันที่ลงทะเบียนโดยอัตโนมัติ
    new_profile = models.EmployeeProfile(
        user_id=new_user.id,
        hire_date=str(date.today())
    )
    db.add(new_profile)
    db.commit()
    db.refresh(new_user)

    return new_user


# ─────────────────────────────────────────────
#  อัปโหลดรูปถ่าย และ เอกสารยืนยันตัวตน
# ─────────────────────────────────────────────
@router.post("/{user_id}/upload")
def upload_user_files(
    user_id: int,
    photo: UploadFile = File(None),
    id_doc: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    """API สำหรับอัปโหลดไฟล์รูปภาพพนักงานและรูปบัตรประชาชน"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="ไม่พบผู้ใช้งานนี้")

    def delete_old_files(folder: str, stem: str):
        """Helper: ลบไฟล์เดิมทิ้งก่อนอัปโหลดใหม่ เพื่อประหยัดเนื้อที่"""
        folder_path = os.path.join(UPLOAD_DIR, folder)
        for f in os.listdir(folder_path):
            if f.startswith(stem + ".") or f == stem:
                try:
                    os.remove(os.path.join(folder_path, f))
                except OSError:
                    pass

    # จัดการไฟล์รูปถ่ายหน้าตรง (Portrait)
    if photo and photo.filename:
        ext = os.path.splitext(photo.filename)[-1].lower()
        delete_old_files("photos", f"user_{user_id}")
        path = os.path.join(UPLOAD_DIR, "photos", f"user_{user_id}{ext}")
        with open(path, "wb") as f:
            shutil.copyfileobj(photo.file, f)
        user.photo_path = f"uploads/photos/user_{user_id}{ext}"

    # จัดการไฟล์รูปบัตรประชาชน/พาสปอร์ต
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
#  ดึงรายชื่อผู้ใช้ทั้งหมด (สำหรับ Admin)
# ─────────────────────────────────────────────
@router.get("/", response_model=List[schemas.UserOut])
def get_all_users(db: Session = Depends(get_db), admin: models.User = Depends(oauth2.check_can_manage_users)):
    """API สำหรับดึงรายชื่อพนักงานทุกคนในระบบ"""
    users = db.query(models.User).all()
    # เรียงลำดับให้ Admin ขึ้นก่อน แล้วตามด้วย ID คนอื่นๆ
    users.sort(key=lambda u: (0 if (u.role and u.role.name == 'admin') else 1, u.id))
    return users


# ─────────────────────────────────────────────
#  ดูข้อมูลส่วนตัวของผู้ที่กำลังล็อกอิน (Me)
# ─────────────────────────────────────────────
@router.get("/me", response_model=schemas.UserOut)
def read_users_me(current_user: models.User = Depends(oauth2.get_current_user)):
    """API สำหรับดึงข้อมูลของตัวเอง (ต้องผ่านการ Login มาก่อน)"""
    return current_user


# ─────────────────────────────────────────────
#  ดูข้อมูลพนักงานรายบุคคล
# ─────────────────────────────────────────────
@router.get("/{user_id}", response_model=schemas.UserOut)
def read_user(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(oauth2.get_current_user)
):
    """API สำหรับดูรายละเอียดพนักงานหนึ่งคน (เฉพาะแอดมินหรือเจ้าของข้อมูลเท่านั้น)"""
    # ตรวจสอบสิทธิ์: ต้องเป็นแอดมิน หรือ กำลังดูข้อมูลของตัวเอง
    is_admin = (current_user.role and current_user.role.name.lower() == 'admin') or (current_user.username.lower() == 'admin')
    
    if not is_admin and current_user.id != user_id:
        # เช็ค perms เพิ่มเติม
        perms = current_user.permissions or []
        if not any(p in perms for p in ['user.manage', 'page.usermanagement', 'action.user.view_profile']):
            raise HTTPException(status_code=403, detail="ไม่มีสิทธิ์เข้าถึงข้อมูลผู้ใช้อื่น")
        
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="ไม่พบผู้ใช้งานนี้")
    return user


# ─────────────────────────────────────────────
#  Admin: แก้ไขข้อมูลส่วนตัวพนักงาน
# ─────────────────────────────────────────────
@router.put("/{user_id}", response_model=schemas.UserOut)
def update_user(
    user_id: int,
    request: schemas.UserUpdate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_users)
):
    """API สำหรับแอดมินแก้ไขข้อมูลพื้นฐานของพนักงาน"""

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="ไม่พบผู้ใช้งานนี้")

    # 🔒 ข้อห้าม: ไม่อนุญาตให้ใครแก้ไขข้อมูลของ Master Admin (บัญชี admin หลัก)
    is_target_admin = (user.role and user.role.name.lower() == 'admin') or (user.username.lower() == 'admin')
    if is_target_admin:
        raise HTTPException(status_code=403, detail="ระบบไม่อนุญาตให้แก้ไขข้อมูล Master Admin ได้ครับ")

    # อัปเดตข้อมูลทีละฟิลด์บทความที่มีการส่งมาใน Request (Update logic)
    if request.role is not None:
        new_role = db.query(models.Role).filter(models.Role.name == request.role).first()
        if not new_role:
            raise HTTPException(status_code=400, detail=f"ไม่พบสิทธิ์ (Role): {request.role}")
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
#  Admin: แก้ไขข้อมูลประวัติพนักงาน (Employment Data)
# ─────────────────────────────────────────────
@router.put("/{user_id}/profile", response_model=schemas.UserOut)
def update_employee_profile(
    user_id: int,
    request: schemas.EmployeeProfileUpdate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_users)
):
    """API สำหรับแอดมินแก้ไขข้อมูลการจ้างงาน (แผนก, ตำแหน่ง, สถานะ)"""

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="ไม่พบผู้ใช้งานนี้")

    # 🔒 ข้อห้าม: ไม่อนุญาตให้แก้ไขโปรไฟล์ Master Admin
    is_target_admin = (user.role and user.role.name.lower() == 'admin') or (user.username.lower() == 'admin')
    if is_target_admin:
        raise HTTPException(status_code=403, detail="ระบบไม่อนุญาตให้แก้ไขข้อมูล Master Admin ได้ครับ")

    # ดึงข้อมูลโปรไฟล์มาอัปเดต หรือสร้างใหม่ถ้ายังไม่มี
    profile = db.query(models.EmployeeProfile).filter(models.EmployeeProfile.user_id == user_id).first()
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
        # หากสถานะเปลี่ยนเป็น 'terminated' (ลาออก/ยกเลิกสัญญา) ให้บันทึกวันที่ออกเป็นวันนี้ทันที
        if request.employment_status == 'terminated' and profile.termination_date is None:
            profile.termination_date = str(date.today())
        elif request.employment_status != 'terminated':
            profile.termination_date = None

    db.commit()
    db.refresh(user)
    return user


# ─────────────────────────────────────────────
#  ลบผู้ใช้งาน (Admin Only)
# ─────────────────────────────────────────────
@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_users)
):
    """API สำหรับแอดมินลบผู้ใช้งานออกจากระบบอย่างถาวร"""

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="ไม่พบผู้ใช้งานนี้")

    # 🔒 ข้อห้าม: ห้ามลบบัญชี Master Admin อย่างเด็ดขาด
    if user.username == 'admin':
        raise HTTPException(status_code=403, detail="ไม่สามารถลบบัญชี Master Admin ได้")

    # ลบข้อมูลพ่วงอื่นๆ (Cascade)
    profile = db.query(models.EmployeeProfile).filter(models.EmployeeProfile.user_id == user_id).first()
    if profile:
        db.delete(profile)

    # ฟังก์ชันช่วยลบไฟล์รูปที่อยู่ในเครื่องทิ้งไปด้วย
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

    remove_file(user.photo_path) # ลบรูปถ่าย
    remove_file(user.id_doc_path) # ลบรูปบัตร

    db.delete(user)
    db.commit()
    return

