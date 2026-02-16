from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import users as models
from schemas import users as schemas
from hashing import Hash
import oauth2 

# สร้าง Router (แผนกย่อย) สำหรับจัดการเรื่อง Users โดยเฉพาะ
router = APIRouter(
    prefix="/users",    # เวลายิง API จะขึ้นต้นด้วย /users เสมอ
    tags=["Users"]      # จัดหมวดหมู่ในหน้าคู่มือ (Swagger UI) ให้หาง่ายๆ
)

# --- ฟังก์ชันสร้าง User ใหม่ (Register) ---
@router.post("/", response_model=schemas.UserOut)
def create_user(request: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1. เช็คก่อนว่า Email นี้เคยสมัครหรือยัง?
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if user:
        # ถ้ามีแล้ว ให้แจ้ง Error กลับไป
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email นี้มีผู้ใช้งานแล้วครับ"
        )

    # 2. สร้าง User ใหม่ โดยการเอาข้อมูลจาก Request มาใส่
    new_user = models.User(
        username=request.username,
        email=request.email,
        password=Hash.bcrypt(request.password), # สำคัญ! เข้ารหัสผ่านก่อนเก็บ
        role=request.role
    )

    # 3. บันทึกลง Database
    db.add(new_user)
    db.commit()      # ยืนยันการบันทึก
    db.refresh(new_user) # ดึงข้อมูลล่าสุดกลับมา (เพื่อให้ได้ ID ที่ Database สร้างให้)

    # 4. ส่งข้อมูลผู้ใช้กลับไป (โดยไม่มีรหัสผ่าน เพราะใช้ Schema UserOut)
    return new_user


# --- API ดูข้อมูลส่วนตัว (ต้อง Login เท่านั้น) ---
@router.get("/me", response_model=schemas.UserOut)
def read_users_me(current_user: models.User = Depends(oauth2.get_current_user)):
    # ฟังก์ชันนี้จะทำงานได้ก็ต่อเมื่อ get_current_user ตรวจสอบผ่านแล้วเท่านั้น
    return current_user