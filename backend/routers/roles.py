from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import users as models
from pydantic import BaseModel
from typing import List, Optional
import json
import oauth2

router = APIRouter(
    prefix="/roles",
    tags=["Roles"]
)

# --- Pydantic Models for Request/Response ---
class RoleBase(BaseModel):
    name: str
    permissions: List[str] # รับเป็น List เช่น ["user.view", "project.delete"]

class RoleCreate(RoleBase):
    pass

class RoleUpdate(RoleBase):
    pass

class RoleResponse(RoleBase):
    id: int
    
    class Config:
        from_attributes = True
        
    # Helper to convert JSON string back to list for response
    @staticmethod
    def resolve_permissions(role_db):
        return json.loads(role_db.permissions) if role_db.permissions else []

# --- Helper to check if user is admin (Has 'role.manage' permission) ---
def check_admin_access(current_user: models.User):
    # 1. Get User's Role
    if not current_user.role:
        raise HTTPException(status_code=403, detail="User has no role assigned")
    
    # 2. Get Permissions of that Role
    try:
        perms = json.loads(current_user.role.permissions)
    except:
        perms = []
        
    # 3. Check specific permission
    if "role.manage" not in perms:
        raise HTTPException(status_code=403, detail="Access Denied: You need 'role.manage' permission.")

# --- Endpoints ---

@router.get("/", response_model=List[RoleResponse])
def get_roles(db: Session = Depends(get_db)):
    roles = db.query(models.Role).all()
    # Convert permissions string to list manually for response match
    # Pydantic might complain if we don't handle the transformation.
    # Let's map it manually to be safe.
    result = []
    for r in roles:
        result.append({
            "id": r.id,
            "name": r.name,
            "permissions": json.loads(r.permissions) if r.permissions else []
        })
    return result

@router.post("/", response_model=RoleResponse)
def create_role(
    role: RoleCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    check_admin_access(current_user)
    
    # Check if role exists
    existing = db.query(models.Role).filter(models.Role.name == role.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Role name already exists")
    
    new_role = models.Role(
        name=role.name,
        permissions=json.dumps(role.permissions) # Store as JSON String
    )
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    
    return {
        "id": new_role.id,
        "name": new_role.name,
        "permissions": json.loads(new_role.permissions)
    }

@router.put("/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: int, 
    role_update: RoleUpdate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    check_admin_access(current_user)
    
    role_db = db.query(models.Role).filter(models.Role.id == role_id).first()
    if not role_db:
        raise HTTPException(status_code=404, detail="Role not found")
    
    role_db.name = role_update.name
    role_db.permissions = json.dumps(role_update.permissions)
    
    db.commit()
    db.refresh(role_db)
    
    return {
        "id": role_db.id,
        "name": role_db.name,
        "permissions": json.loads(role_db.permissions)
    }
