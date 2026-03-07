from pydantic import BaseModel
from typing import List, Optional

class DutyCategoryBase(BaseModel):
    name: str
    name_th: Optional[str] = None
    name_v3: Optional[str] = None

class DutyCategoryCreate(DutyCategoryBase):
    pass

class DutyCategoryUpdate(BaseModel):
    name: Optional[str] = None
    name_th: Optional[str] = None
    name_v3: Optional[str] = None

class DutyCategory(DutyCategoryBase):
    id: int
    class Config:
        from_attributes = True

class DutyBase(BaseModel):
    name: str
    name_th: Optional[str] = None
    name_v3: Optional[str] = None
    description: Optional[str] = None
    description_th: Optional[str] = None
    description_v3: Optional[str] = None
    category_id: Optional[int] = None

class DutyCreate(DutyBase):
    pass

class DutyUpdate(BaseModel):
    name: Optional[str] = None
    name_th: Optional[str] = None
    name_v3: Optional[str] = None
    description: Optional[str] = None
    description_th: Optional[str] = None
    description_v3: Optional[str] = None
    category_id: Optional[int] = None

class SubDutyBase(BaseModel):
    name: str
    name_th: Optional[str] = None
    name_v3: Optional[str] = None
    duty_id: int

class SubDutyCreate(SubDutyBase):
    pass

class SubDuty(SubDutyBase):
    id: int
    class Config:
        from_attributes = True

class Duty(DutyBase):
    id: int
    category: Optional[DutyCategory] = None
    sub_duties: List[SubDuty] = []
    class Config:
        from_attributes = True

class JobDescriptionBase(BaseModel):
    description: str
    description_th: Optional[str] = None
    description_v3: Optional[str] = None

class JobDescriptionCreate(JobDescriptionBase):
    job_title_id: int

class JobDescription(JobDescriptionBase):
    id: int
    job_title_id: int
    class Config:
        from_attributes = True

class JobTitleBase(BaseModel):
    name: str
    name_th: Optional[str] = None
    name_v3: Optional[str] = None
    level: int = 1

class JobTitleCreate(JobTitleBase):
    department_id: int

class JobTitleUpdate(BaseModel):
    name: Optional[str] = None
    name_th: Optional[str] = None
    name_v3: Optional[str] = None
    level: Optional[int] = None

class JobTitleDutiesUpdate(BaseModel):
    duty_ids: List[int]

class JobTitle(JobTitleBase):
    id: int
    department_id: int
    descriptions: List[JobDescription] = []
    duties: List[Duty] = []
    class Config:
        from_attributes = True

class DepartmentBase(BaseModel):
    name: str
    name_th: Optional[str] = None
    name_v3: Optional[str] = None
    value: str

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    name_th: Optional[str] = None
    name_v3: Optional[str] = None
    value: Optional[str] = None

class Department(DepartmentBase):
    id: int
    job_titles: List[JobTitle] = []
    class Config:
        from_attributes = True

class UserDutyEvaluationBase(BaseModel):
    user_id: int
    duty_id: int
    score: int

class UserDutyEvaluationCreate(UserDutyEvaluationBase):
    pass

class UserDutyEvaluation(UserDutyEvaluationBase):
    id: int
    evaluated_by_id: Optional[int] = None
    updated_at: Optional[str] = None
    duty: Optional[Duty] = None
    class Config:
        from_attributes = True

class UserSubDutyEvaluationBase(BaseModel):
    user_id: int
    sub_duty_id: int
    is_completed: bool

class UserSubDutyEvaluationCreate(UserSubDutyEvaluationBase):
    pass

class UserSubDutyEvaluation(UserSubDutyEvaluationBase):
    id: int
    updated_at: Optional[str] = None
    class Config:
        from_attributes = True
