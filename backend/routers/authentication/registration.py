from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from datetime import date
import os

from database import get_db
from models import users as models
from schemas import users as schemas
from hashing import Hash
import storage

router = APIRouter(prefix="", tags=["Authentication"])

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
os.makedirs(os.path.join(UPLOAD_DIR, "photos"),  exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, "id_docs"), exist_ok=True)

@router.post("/register", response_model=schemas.UserOut)
def register_user(
    request: schemas.UserCreate, 
    db: Session = Depends(get_db)
):
    """API สำหรับลงทะเบียนพนักงานใหม่เข้าระบบ"""
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

    if db.query(models.User).filter(models.User.username == request.username).first():
        raise HTTPException(status_code=400, detail="ชื่อผู้ใช้งาน (Username) นี้ถูกใช้ไปแล้ว")

    if db.query(models.User).filter(models.User.id_card_number == request.id_card_number.strip()).first():
        raise HTTPException(status_code=400, detail="เลขบัตรประชาชน/พาสปอร์ตนี้มีอยู่ในระบบแล้ว")

    if db.query(models.User).filter(
        models.User.first_name == request.first_name.strip(),
        models.User.last_name  == request.last_name.strip()
    ).first():
        raise HTTPException(status_code=400, detail=f"ชื่อ {request.first_name} {request.last_name} มีอยู่ในระบบแล้ว")

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

    new_profile = models.EmployeeProfile(
        user_id=new_user.id,
        hire_date=str(date.today())
    )
    db.add(new_profile)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/register/{user_id}/upload")
def upload_user_files(
    user_id: int,
    photo: UploadFile = File(None),
    id_doc: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    """API สำหรับอัปโหลดไฟล์รูปภาพพนักงานและรูปบัตรประชาชนตอนสมัคร"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="ไม่พบผู้ใช้งานนี้")

    def delete_old_local_files(folder: str, stem: str):
        folder_path = os.path.join(UPLOAD_DIR, folder)
        try:
            entries = os.listdir(folder_path)
        except FileNotFoundError:
            return
        for f in entries:
            if f.startswith(stem + ".") or f == stem:
                try:
                    os.remove(os.path.join(folder_path, f))
                except OSError:
                    pass

    if photo and photo.filename:
        ext = os.path.splitext(photo.filename)[-1].lower()
        if not storage.USE_SPACES:
            delete_old_local_files("photos", f"user_{user_id}")
        file_bytes = photo.file.read()
        user.photo_path = storage.save_file(file_bytes, "photos", f"user_{user_id}{ext}", photo.content_type or "image/jpeg")

    if id_doc and id_doc.filename:
        ext = os.path.splitext(id_doc.filename)[-1].lower()
        if not storage.USE_SPACES:
            delete_old_local_files("id_docs", f"user_{user_id}")
        file_bytes = id_doc.file.read()
        user.id_doc_path = storage.save_file(file_bytes, "id_docs", f"user_{user_id}{ext}", id_doc.content_type or "image/jpeg")

    db.commit()
    db.refresh(user)
    return {"photo_path": user.photo_path, "id_doc_path": user.id_doc_path}
