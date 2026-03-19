from pydantic import BaseModel
from typing import Optional, List

# --- โครงสร้างสำหรับการตั้งค่าส่วนกลาง (Global Settings) ---
class PayrollSettingBase(BaseModel):
    key: str            # เช่น 'ot_rate_normal'
    value: float        # เช่น 1.5
    description: Optional[str] = None
    type: str = "float" # float or int

class PayrollSettingUpdate(BaseModel):
    value: float        # อนุญาตให้แอดมินแก้ไขแค่ค่างาน (Value)

class PayrollSettingOut(PayrollSettingBase):
    id: int
    class Config:
        from_attributes = True

# --- โครงสร้างสำหรับการขอคำนวณเงินรายคน (Request Calculation) ---
class PayrollCalculationRequest(BaseModel):
    user_id: int
    month: int # 1 - 12
    year: int  # 2024, 2025
