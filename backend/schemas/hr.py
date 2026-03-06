from pydantic import BaseModel
from typing import List, Optional

class JobTitleBase(BaseModel):
    name: str

class JobTitleCreate(JobTitleBase):
    department_id: int

class JobTitle(JobTitleBase):
    id: int
    department_id: int
    class Config:
        from_attributes = True

class DepartmentBase(BaseModel):
    name: str
    value: str

class DepartmentCreate(DepartmentBase):
    pass

class Department(DepartmentBase):
    id: int
    job_titles: List[JobTitle] = []
    class Config:
        from_attributes = True
