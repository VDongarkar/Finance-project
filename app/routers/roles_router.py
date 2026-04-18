from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from .. import database, models, schemas, auth

router = APIRouter(tags=["roles"])

class AssignRoleRequest(BaseModel):
    user_id: int
    role_id: int

@router.post("/roles/create", response_model=schemas.Role)
def create_role(role: schemas.RoleCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.require_role(["Admin"]))):
    db_role = db.query(models.Role).filter(models.Role.name == role.name).first()
    if db_role:
        raise HTTPException(status_code=400, detail="Role already exists")
    new_role = models.Role(name=role.name, permissions=role.permissions)
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role

@router.post("/users/assign-role")
def assign_role(request: AssignRoleRequest, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.require_role(["Admin"]))):
    user = db.query(models.User).filter(models.User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    role = db.query(models.Role).filter(models.Role.id == request.role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    if role not in user.roles:
        user.roles.append(role)
        db.commit()
    return {"message": "Role assigned successfully"}

@router.get("/users/{id}/roles")
def get_user_roles(id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    # Assuming Admin or the user themselves can check roles
    if current_user.id != id and not any(r.name == "Admin" for r in current_user.roles):
        raise HTTPException(status_code=403, detail="Not permitted")
        
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"roles": [role.name for role in user.roles]}

@router.get("/users/{id}/permissions")
def get_user_permissions(id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.id != id and not any(r.name == "Admin" for r in current_user.roles):
        raise HTTPException(status_code=403, detail="Not permitted")
        
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    permissions = set()
    for role in user.roles:
        if role.permissions:
            for p in role.permissions.split(","):
                permissions.add(p.strip())
    return {"permissions": list(permissions)}
