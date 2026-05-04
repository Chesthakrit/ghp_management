from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import time
from database import get_db
from models import users as models
import storage
from schemas import hr as schemas
import oauth2
from datetime import datetime

router = APIRouter(prefix="", tags=["HR - Evaluations"])

@router.get("/evaluations/{user_id}", response_model=List[schemas.UserDutyEvaluation])
def get_user_evaluations(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    """ดึงคะแนนการประเมินทักษะของพนักงานรายบุคคล"""
    return db.query(models.UserDutyEvaluation).filter(models.UserDutyEvaluation.user_id == user_id).all()

@router.post("/evaluations", response_model=schemas.UserDutyEvaluation)
def save_user_evaluation(
    eval_req: schemas.UserDutyEvaluationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    """บันทึกผลการประเมินทักษะ (คะแนน 0-5) ให้กับพนักงาน"""
    db_eval = db.query(models.UserDutyEvaluation).filter(
        models.UserDutyEvaluation.user_id == eval_req.user_id,
        models.UserDutyEvaluation.duty_id == eval_req.duty_id
    ).first()
    
    if db_eval:
        db_eval.score = eval_req.score
        db_eval.evaluated_by_id = current_user.id
        db_eval.updated_at = datetime.now().isoformat()
    else:
        db_eval = models.UserDutyEvaluation(
            **eval_req.dict(),
            evaluated_by_id=current_user.id,
            updated_at=datetime.now().isoformat()
        )
        db.add(db_eval)

    db.commit()
    db.refresh(db_eval)
    return db_eval

@router.get("/sub-evaluations/{user_id}", response_model=List[schemas.UserSubDutyEvaluation])
def get_user_sub_evaluations(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    """ดึงข้อมูลเช็คลิสต์ทักษะย่อยของพนักงาน (ผ่าน/ไม่ผ่าน)"""
    return db.query(models.UserSubDutyEvaluation).filter(models.UserSubDutyEvaluation.user_id == user_id).all()

@router.post("/sub-evaluations", response_model=schemas.UserSubDutyEvaluation)
def save_user_sub_evaluation(
    eval_req: schemas.UserSubDutyEvaluationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    """บันทึกการตรวจเช็คทักษะย่อย (ติ๊กเลือกให้พนักงานว่าผ่านหัวข้อนี้แล้ว)"""
    db_eval = db.query(models.UserSubDutyEvaluation).filter(
        models.UserSubDutyEvaluation.user_id == eval_req.user_id,
        models.UserSubDutyEvaluation.sub_duty_id == eval_req.sub_duty_id
    ).first()
    
    if db_eval:
        db_eval.is_completed = eval_req.is_completed
        db_eval.updated_at = datetime.now().isoformat()
    else:
        db_eval = models.UserSubDutyEvaluation(
            **eval_req.dict(),
            updated_at=datetime.now().isoformat()
        )
        db.add(db_eval)

    db.commit()
    db.refresh(db_eval)
    return db_eval

@router.post("/upload-video")
async def upload_video(
    file: UploadFile = File(...),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    """อัปโหลดวิดีโอสอนงานมาเก็บไว้ในระบบ"""
    timestamp = int(time.time())
    safe_filename = file.filename.replace(" ", "_").replace("(", "").replace(")", "")
    unique_name = f"{timestamp}_{safe_filename}"

    try:
        file_bytes = await file.read()
        url = storage.save_file(file_bytes, "videos", unique_name, file.content_type or "video/mp4")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

    return {"url": url if storage.USE_SPACES else f"/hr/videos/{unique_name}"}

@router.get("/videos/{filename}")
def get_video(
    filename: str,
    token: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """ส่งไฟล์วิดีโอให้ดูเฉพาะผู้ที่มีสิทธิ์ (ล็อคกุญแจ)"""
    username = oauth2.verify_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="คุณไม่มีสิทธิ์เข้าดูวิดีโอนี้ กรุณา Login ก่อน"
        )
    
    VIDEO_DIR = os.path.join(os.getcwd(), "uploads", "videos")
    file_path = os.path.join(VIDEO_DIR, filename)
    
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="ไม่พบไฟล์วิดีโอในระบบ")
        
    return FileResponse(file_path, media_type="video/mp4")
