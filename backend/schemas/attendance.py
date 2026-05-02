from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class AttendanceLogResponse(BaseModel):

    id: int
    user_id: int
    date: date
    check_in_time:  Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    actual_check_in:  Optional[datetime] = None
    actual_check_out: Optional[datetime] = None
    status:        str
    site_name:     Optional[str] = None
    note:          Optional[str] = None
    is_approved:   bool
    late_minutes:  int = 0
    ot_request:    Optional['OTRequestResponse'] = None # Join info

    class Config:
        from_attributes = True
        orm_mode = True


class CompanyHolidayCreate(BaseModel):
    year: int
    date: date
    name: str

class CompanyHolidayResponse(BaseModel):
    id: int
    year: int
    date: date
    name: str
    is_active: bool

    class Config:
        from_attributes = True

class AttendanceConfigUpdate(BaseModel):
    key: str
    value: str

class AttendanceConfigResponse(BaseModel):
    key: str
    value: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class AttendanceLocationCreate(BaseModel):
    name: str
    lat: float
    lon: float
    radius: int = 100
    is_fixed: bool = True
    project_id: Optional[int] = None

class AttendanceLocationResponse(BaseModel):
    id: int
    name: str
    lat: float
    lon: float
    radius: int
    is_fixed: bool
    project_id: Optional[int] = None

    class Config:
        from_attributes = True

class OTRequestCreate(BaseModel):
    request_date: date
    start_time: str
    end_time: str
    reason: Optional[str] = None
    standard_hours: float = 0.0
    special_hours: float = 0.0
    total_hours: float = 0.0

class OTRequestResponse(BaseModel):
    id: int
    user_id: int
    request_date: date
    start_time: str
    end_time: str
    standard_hours: float
    special_hours: float
    total_hours: float
    reason: Optional[str] = None
    status: str
    
    class Config:
        from_attributes = True
        orm_mode = True
