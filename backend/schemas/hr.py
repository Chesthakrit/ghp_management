from pydantic import BaseModel
from typing import List, Optional

class DutyCategoryBase(BaseModel):
    name: str

class DutyCategoryCreate(DutyCategoryBase):
    pass

class DutyCategoryUpdate(BaseModel):
    name: Optional[str] = None

class DutyCategory(DutyCategoryBase):
    id: int
    class Config:
        from_attributes = True

class DutyBase(BaseModel):
    name: str
    description: Optional[str] = None
    category_id: Optional[int] = None

class DutyCreate(DutyBase):
    pass

class DutyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None

class Duty(DutyBase):
    id: int
    category: Optional[DutyCategory] = None
    class Config:
        from_attributes = True

class JobDescriptionBase(BaseModel):
    description: str

class JobDescriptionCreate(JobDescriptionBase):
    job_title_id: int

class JobDescription(JobDescriptionBase):
    id: int
    job_title_id: int
    class Config:
        from_attributes = True

class JobTitleBase(BaseModel):
    name: str
    level: int = 1

class JobTitleCreate(JobTitleBase):
    department_id: int

class JobTitleUpdate(BaseModel):
    name: Optional[str] = None
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
    value: str

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
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
