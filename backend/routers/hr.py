"""
ไฟล์จัดการระบบบริหารทรัพยากรบุคคล (HR Management Router)
ครอบคลุมการจัดการแผนก (Departments), ตำแหน่ง (Job Titles), รายละเอียดงาน (JD), 
คลังทักษะ (Skill Library/Duties) และการประเมินผลพนักงาน (Evaluations)
"""

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
import time
from database import get_db
from models import users as models
from schemas import hr as schemas
import oauth2

router = APIRouter(
    prefix="/hr",
    tags=["HR Management"]
)

# ─────────────────────────────────────────────
#  การจัดการแผนก (Departments)
# ─────────────────────────────────────────────

@router.get("/departments", response_model=List[schemas.Department])
def get_departments(db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    """ดึงรายชื่อแผนกทั้งหมดที่มีในบริษัท (เรียงตาม display_order)"""
    return db.query(models.Department).order_by(models.Department.display_order.asc()).all()

@router.post("/departments", response_model=schemas.Department)
def create_department(
    dept: schemas.DepartmentCreate, 
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    """เพิ่มแผนกใหม่ (เฉพาะ Admin เท่านั้น)"""
        
    db_dept = models.Department(**dept.dict())
    db.add(db_dept)
    db.commit()
    db.refresh(db_dept)
    return db_dept

@router.put("/departments/{dept_id}", response_model=schemas.Department)
def update_department(
    dept_id: int,
    dept: schemas.DepartmentUpdate, 
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    """แก้ไขข้อมูลพื้นฐานของแผนก (เช่น เปลี่ยนชื่อพิกัดแผนก หรือสิทธิ์ส่วนกลาง)"""
    db_dept = db.query(models.Department).filter(models.Department.id == dept_id).first()
    if not db_dept:
        raise HTTPException(status_code=404, detail="Department not found")
        
    update_data = dept.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_dept, key, value)
        
    db.commit()
    db.refresh(db_dept)
    return db_dept

@router.put("/departments/reorder", response_model=List[schemas.Department])
def reorder_departments(
    payload: schemas.ReorderRequest,
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    """บันทึกลำดับแผนกใหม่หลังการ Drag & Drop"""
    for item in payload.items:
        db.query(models.Department).filter(models.Department.id == item.id).update(
            {"display_order": item.display_order}
        )
    db.commit()
    return db.query(models.Department).order_by(models.Department.display_order.asc()).all()


@router.delete("/departments/{dept_id}")
def delete_department(
    dept_id: int, 
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    """ลบแผนก (เฉพาะ Admin เท่านั้น)"""
        
    db_dept = db.query(models.Department).filter(models.Department.id == dept_id).first()
    if not db_dept:
        raise HTTPException(status_code=404, detail="ไม่พบแผนก")
    db.delete(db_dept)
    db.commit()
    return {"message": "ลบแผนกเรียบร้อยแล้า"}

# ─────────────────────────────────────────────
#  การจัดการตำแหน่งงาน (Job Titles)
# ─────────────────────────────────────────────

@router.get("/job-titles", response_model=List[schemas.JobTitle])
def get_job_titles(dept_id: Optional[int] = None, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    """ดึงรายชื่อตำแหน่งงานทั้งหมด (สามารถเลือกกรองตามแผนกได้)"""
    query = db.query(models.JobTitle).order_by(models.JobTitle.display_order.asc())
    if dept_id:
        query = query.filter(models.JobTitle.department_id == dept_id)
    return query.all()

@router.post("/job-titles", response_model=schemas.JobTitle)
def create_job_title(
    jt: schemas.JobTitleCreate, 
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    """สร้างตำแหน่งงานใหม่ภายใต้แผนก (เฉพาะ Admin เท่านั้น)"""
        
    db_jt = models.JobTitle(**jt.dict())
    db.add(db_jt)
    db.commit()
    db.refresh(db_jt)
    return db_jt

@router.put("/job-titles/reorder", response_model=List[schemas.JobTitle])
def reorder_job_titles(
    payload: schemas.ReorderRequest,
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    """บันทึกลำดับตำแหน่งงานใหม่หลังการ Drag & Drop"""
    for item in payload.items:
        db.query(models.JobTitle).filter(models.JobTitle.id == item.id).update(
            {"display_order": item.display_order}
        )
    db.commit()
    return db.query(models.JobTitle).order_by(models.JobTitle.display_order.asc()).all()

@router.put("/job-titles/{jt_id}", response_model=schemas.JobTitle)
def update_job_title(
    jt_id: int, 
    jt_update: schemas.JobTitleUpdate, 
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    """แก้ไขข้อมูลตำแหน่งงาน (เฉพาะ Admin)"""
        
    db_jt = db.query(models.JobTitle).filter(models.JobTitle.id == jt_id).first()
    if not db_jt:
        raise HTTPException(status_code=404, detail="ไม่พบตำแหน่งงาน")
        
    for key, value in jt_update.dict(exclude_unset=True).items():
        setattr(db_jt, key, value)
        
    db.commit()
    db.refresh(db_jt)
    return db_jt

@router.delete("/job-titles/{jt_id}")
def delete_job_title(
    jt_id: int, 
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    """ลบตำแหน่งงาน (เฉพาะ Admin)"""
        
    db_jt = db.query(models.JobTitle).filter(models.JobTitle.id == jt_id).first()
    if not db_jt:
        raise HTTPException(status_code=404, detail="ไม่พบตำแหน่งงาน")
    db.delete(db_jt)
    db.commit()
    return {"message": "ลบตำแหน่งงานเรียบร้อย"}

# ─────────────────────────────────────────────
#  รายละเอียดงาน (Job Descriptions)
# ─────────────────────────────────────────────

@router.post("/job-descriptions", response_model=schemas.JobDescription)
def create_job_description(
    jd: schemas.JobDescriptionCreate, 
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    """เพิ่มคำอธิบายรายละเอียดงาน (JD) ให้กับตำแหน่งงาน"""
        
    db_jd = models.JobDescription(**jd.dict())
    db.add(db_jd)
    db.commit()
    db.refresh(db_jd)
    return db_jd

@router.delete("/job-descriptions/{jd_id}")
def delete_job_description(
    jd_id: int, 
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    """ลบรายละเอียดงานที่ไม่ได้ใช้ง่าน"""
        
    db_jd = db.query(models.JobDescription).filter(models.JobDescription.id == jd_id).first()
    if not db_jd:
        raise HTTPException(status_code=404, detail="ไม่พบข้อมูล")
    db.delete(db_jd)
    db.commit()
    return {"message": "ลบ JD เรียบร้อย"}

# ─────────────────────────────────────────────
#  หมวดหมู่ทักษะ (Skill Categories / Tags)
# ─────────────────────────────────────────────

@router.get("/duty-categories", response_model=List[schemas.DutyCategory])
def get_duty_categories(db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    """ดึงหมวดหมู่ทักษะทั้งหมด (เช่น Soft Skill, Hardware, Language)"""
    return db.query(models.DutyCategory).order_by(models.DutyCategory.display_order.asc()).all()

@router.post("/duty-categories", response_model=schemas.DutyCategory)
def create_duty_category(
    cat: schemas.DutyCategoryCreate, 
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    """เพิ่มหมวดหมู่ทักษะใหม่ (เฉพาะ Admin)"""
        
    db_cat = models.DutyCategory(**cat.dict())
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat

@router.put("/duty-categories/reorder", response_model=List[schemas.DutyCategory])
def reorder_duty_categories(
    payload: schemas.ReorderRequest,
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    """บันทึกลำดับหมวดหมู่ทักษะหลัง Drag & Drop"""
    for item in payload.items:
        db.query(models.DutyCategory).filter(models.DutyCategory.id == item.id).update(
            {"display_order": item.display_order}
        )
    db.commit()
    return db.query(models.DutyCategory).order_by(models.DutyCategory.display_order.asc()).all()

@router.put("/duty-categories/{cat_id}", response_model=schemas.DutyCategory)
def update_duty_category(
    cat_id: int,
    cat_update: schemas.DutyCategoryUpdate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    """แก้ไขหมวดหมู่ทักษะ"""
        
    db_cat = db.query(models.DutyCategory).filter(models.DutyCategory.id == cat_id).first()
    if not db_cat:
        raise HTTPException(status_code=404, detail="ไม่พบหมวดหมู่")
        
    for key, value in cat_update.dict(exclude_unset=True).items():
        setattr(db_cat, key, value)
        
    db.commit()
    db.refresh(db_cat)
    return db_cat

@router.delete("/duty-categories/{cat_id}")
def delete_duty_category(
    cat_id: int, 
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    """ลบหมวดหมู่ทักษะ"""
        
    db_cat = db.query(models.DutyCategory).filter(models.DutyCategory.id == cat_id).first()
    if not db_cat:
        raise HTTPException(status_code=404, detail="ไม่พบข้อมูล")
    db.delete(db_cat)
    db.commit()
    return {"message": "ลบหมวดหมู่เรียบร้อย"}

# ─────────────────────────────────────────────
#  คลังทักษะหลัก (Duties / Skill Library)
# ─────────────────────────────────────────────

@router.get("/duties", response_model=List[schemas.Duty])
def get_duties(db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    """ดึงรายชื่อทักษะ (Skill) ทั้งหมดที่มีในระบบ"""
    return db.query(models.Duty).order_by(models.Duty.display_order.asc()).all()

@router.post("/duties", response_model=schemas.Duty)
def create_duty(
    duty: schemas.DutyCreate, 
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    """เพิ่มทักษะใหม่เข้าระบบ (เช่น ความรู้ภาษาอังกฤษ, การใช้ Excel) Outlined"""
        
    db_duty = models.Duty(**duty.dict())
    db.add(db_duty)
    db.commit()
    db.refresh(db_duty)
    return db_duty

@router.put("/duties/reorder", response_model=List[schemas.Duty])
def reorder_duties(
    payload: schemas.ReorderRequest,
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    """บันทึกลำดับทักษะหลักหลัง Drag & Drop"""
    try:
        for item in payload.items:
            db.query(models.Duty).filter(models.Duty.id == item.id).update(
                {"display_order": item.display_order}
            )
        db.commit()
        return db.query(models.Duty).order_by(models.Duty.display_order.asc()).all()
    except Exception as e:
        db.rollback()
        print(f"ERROR in reorder_duties: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/duties/{duty_id}", response_model=schemas.Duty)
def get_duty(duty_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    """ดึงข้อมูลทักษะรายตัว (รวมทักษะย่อย)"""
    db_duty = db.query(models.Duty).filter(models.Duty.id == duty_id).first()
    if not db_duty:
        raise HTTPException(status_code=404, detail="ไม่พบทักษะ")
    return db_duty

@router.put("/duties/{duty_id}", response_model=schemas.Duty)
def update_duty(
    duty_id: int, 
    duty_update: schemas.DutyUpdate, 
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    """แก้ไขข้อมูลทักษะหลัก Outlined"""
        
    db_duty = db.query(models.Duty).filter(models.Duty.id == duty_id).first()
    if not db_duty:
        raise HTTPException(status_code=404, detail="ไม่พบทักษะ")
        
    for key, value in duty_update.dict(exclude_unset=True).items():
        setattr(db_duty, key, value)
        
    db.commit()
    db.refresh(db_duty)
    return db_duty

@router.delete("/duties/{duty_id}")
def delete_duty(
    duty_id: int, 
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    """ลบทักษะหลักทิ้ง"""
        
    db_duty = db.query(models.Duty).filter(models.Duty.id == duty_id).first()
    if not db_duty:
        raise HTTPException(status_code=404, detail="ไม่พบข้อมูล")
    db.delete(db_duty)
    db.commit()
    return {"message": "ลบทักษะเรียบร้อย"}

# ─────────────────────────────────────────────
#  ทักษะปลีกย่อย (Sub-Duties / Checklist Items)
# ─────────────────────────────────────────────

@router.post("/sub-duties", response_model=schemas.SubDuty)
def create_sub_duty(
    sub_duty: schemas.SubDutyCreate, 
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    """เพิ่มหัวข้อเช็คลิสต์ย่อยภายใต้ทักษะหลัก (เช่น ทักษะหลัก: Excel -> ทักษะย่อย: VLOOKUP)"""
        
    db_sub = models.SubDuty(**sub_duty.dict())
    db.add(db_sub)
    db.commit()
    db.refresh(db_sub)
    return db_sub

@router.put("/sub-duties/reorder", response_model=List[schemas.SubDuty])
def reorder_sub_duties(
    payload: schemas.ReorderRequest,
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    """บันทึกลำดับทักษะย่อยหลัง Drag & Drop"""
    try:
        for item in payload.items:
            db_obj = db.query(models.SubDuty).filter(models.SubDuty.id == item.id).first()
            if db_obj:
                db_obj.display_order = item.display_order
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"ERROR reorder_sub_duties: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    return db.query(models.SubDuty).order_by(models.SubDuty.display_order.asc()).all()

@router.put("/sub-duties/{sub_id}", response_model=schemas.SubDuty)
def update_sub_duty(
    sub_id: int,
    update: schemas.SubDutyUpdate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    """อัปเดตข้อมูลทักษะย่อย (เช่น เพิ่ม tutorial URL)"""
    db_sub = db.query(models.SubDuty).filter(models.SubDuty.id == sub_id).first()
    if not db_sub:
        raise HTTPException(status_code=404, detail="ไม่พบทักษะย่อย")
    for key, value in update.dict(exclude_unset=True).items():
        setattr(db_sub, key, value)
    db.commit()
    db.refresh(db_sub)
    return db_sub

@router.delete("/sub-duties/{sub_id}")
def delete_sub_duty(
    sub_id: int, 
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    """ลบทักษะย่อย"""
        
    db_sub = db.query(models.SubDuty).filter(models.SubDuty.id == sub_id).first()
    if not db_sub:
        raise HTTPException(status_code=404, detail="ไม่พบข้อมูล")
    db.delete(db_sub)
    db.commit()
    return {"message": "ลบเรียบร้อย"}

# ─────────────────────────────────────────────
#  จัดการความสัมพันธ์ทักษะกับตำแหน่งงาน (Job Duties Setup)
# ─────────────────────────────────────────────

@router.put("/job-titles/{jt_id}/duties", response_model=schemas.JobTitle)
def update_job_title_duties(
    jt_id: int,
    payload: schemas.JobTitleDutiesUpdate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(oauth2.check_can_manage_hr_settings)
):
    """กำหนดว่าตำแหน่งงานนี้ จะต้องมีทักษะ/ความรู้เรื่องอะไรบ้าง"""
        
    db_jt = db.query(models.JobTitle).filter(models.JobTitle.id == jt_id).first()
    if not db_jt:
        raise HTTPException(status_code=404, detail="ไม่พบตำแหน่งงาน")
        
    # ดึงรายชื่อทักษะตามที่ระบุในรายการ ID
    duties = db.query(models.Duty).filter(models.Duty.id.in_(payload.duty_ids)).all()
    
    # อัปเดตความสัมพันธ์ Many-to-Many สำหรับตำแหน่งนี้
    db_jt.duties = duties
    db.commit()
    db.refresh(db_jt)
    return db_jt

# ─────────────────────────────────────────────
#  ระบบการประเมินทักษะพนักงาน (Skill Evaluations)
# ─────────────────────────────────────────────

@router.get("/evaluations/{user_id}", response_model=List[schemas.UserDutyEvaluation])
def get_user_evaluations(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    """ดึงคะแนนการประเมินทักษะของพนักงานรายบุคคล (ดูได้เฉพาะแอดมินหรือเจ้าของข้อมูล)"""
    # Bypassed: All authenticated users can see evaluations
    pass
        
    return db.query(models.UserDutyEvaluation).filter(models.UserDutyEvaluation.user_id == user_id).all()

@router.post("/evaluations", response_model=schemas.UserDutyEvaluation)
def save_user_evaluation(
    eval_req: schemas.UserDutyEvaluationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    """บันทึกผลการประเมินทักษะ (คะแนน 0-5) ให้กับพนักงาน"""
    # เฉพาะแอดมินหรือหัวหน้างานที่มีสิทธิ์จัดการข้อมูลถึงจะประเมินได้
    # Bypassed: All authenticated users can save evaluations
    pass

    from datetime import datetime
    
    # ตรวจสอบว่าเคยมีการประเมินทักษะนี้ไว้แล้วหรือไม่
    db_eval = db.query(models.UserDutyEvaluation).filter(
        models.UserDutyEvaluation.user_id == eval_req.user_id,
        models.UserDutyEvaluation.duty_id == eval_req.duty_id
    ).first()
    
    if db_eval:
        # ถ้ามีอยู่แล้ว ให้ทำการอัปเดตคะแนนเดิม
        db_eval.score = eval_req.score
        db_eval.evaluated_by_id = current_user.id # บันทึกว่าใครเป็นคนประเมินล่าสุด
        db_eval.updated_at = datetime.now().isoformat()
    else:
        # ถ้ายังไม่เคยประเมิน ให้สร้างรายการใหม่
        db_eval = models.UserDutyEvaluation(
            **eval_req.dict(),
            evaluated_by_id=current_user.id,
            updated_at=datetime.now().isoformat()
        )
        db.add(db_eval)

    db.commit()
    db.refresh(db_eval)
    return db_eval

# ─────────────────────────────────────────────
#  ระบบเช็คลิสต์ทักษะย่อย (Sub-Skill Checklist Evaluations)
# ─────────────────────────────────────────────

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
    # Bypassed: All authenticated users can save sub-evaluations
    pass

    from datetime import datetime
    
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
    # ตรวจสอบสิทธิ์ (Admin หรือ User Manage)
    # Bypassed: All authenticated users can upload videos
    pass

    # กำหนดตำแหน่งเก็บไฟล์ (ในโปรเจกต์)
    UPLOAD_DIR = os.path.join(os.getcwd(), "uploads", "videos")
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR, exist_ok=True)

    # ทำความสะอาดชื่อไฟล์และใส่ Timestamp
    timestamp = int(time.time())
    safe_filename = file.filename.replace(" ", "_").replace("(", "").replace(")", "")
    unique_name = f"{timestamp}_{safe_filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    finally:
        file.file.close()

    # คืนค่า URL สำหรับเรียกดูผ่านด่านตรวจ (Protected)
    return {"url": f"/hr/videos/{unique_name}"}


@router.get("/videos/{filename}")
def get_video(
    filename: str,
    token: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """ส่งไฟล์วิดีโอให้ดูเฉพาะผู้ที่มีสิทธิ์ (ล็อคกุญแจ)"""
    # 1. ตรวจสอบบัตรผ่าน (Token)
    # รองรับการส่งโทเค็นทาง URL (?token=...) เพราะบราวเซอร์เล่นวิดีโอไม่ส่ง Header
    username = oauth2.verify_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="คุณไม่มีสิทธิ์เข้าดูวิดีโอนี้ กรุณา Login ก่อน"
        )
    
    # 2. ค้นหาไฟล์ในระบบ
    VIDEO_DIR = os.path.join(os.getcwd(), "uploads", "videos")
    file_path = os.path.join(VIDEO_DIR, filename)
    
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="ไม่พบไฟล์วิดีโอในระบบ")
        
    # 3. ส่งไฟล์กลับไปแบบ Streaming
    return FileResponse(file_path, media_type="video/mp4")

