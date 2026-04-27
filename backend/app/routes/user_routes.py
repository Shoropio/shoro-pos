import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import Role, User
from app.security import get_current_user, get_password_hash
from app.services.auth_service import require_permission

router = APIRouter(prefix="/users", tags=["users"])


class RoleIn(BaseModel):
    name: str
    permissions: dict = {}


class UserIn(BaseModel):
    full_name: str
    email: str
    password: str
    role_id: int | None = None
    is_active: bool = True


def role_out(role: Role) -> dict:
    try:
        permissions = json.loads(role.permissions or "{}")
    except json.JSONDecodeError:
        permissions = {}
    return {"id": role.id, "name": role.name, "permissions": permissions}


@router.get("/roles")
def list_roles(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    require_permission(current_user, "users.manage")
    return [role_out(role) for role in db.scalars(select(Role).order_by(Role.name))]


@router.post("/roles")
def create_role(data: RoleIn, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    require_permission(current_user, "users.manage")
    role = Role(name=data.name, permissions=json.dumps(data.permissions))
    db.add(role)
    db.commit()
    db.refresh(role)
    return role_out(role)


@router.put("/roles/{role_id}")
def update_role(role_id: int, data: RoleIn, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    require_permission(current_user, "users.manage")
    role = db.get(Role, role_id)
    if role is None:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    role.name = data.name
    role.permissions = json.dumps(data.permissions)
    db.commit()
    return role_out(role)


@router.get("")
def list_users(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    require_permission(current_user, "users.manage")
    rows = db.scalars(select(User).order_by(User.full_name))
    return [
        {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role.name if user.role else None,
            "is_active": user.is_active,
        }
        for user in rows
    ]


@router.post("")
def create_user(data: UserIn, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    require_permission(current_user, "users.manage")
    if db.scalar(select(User).where(User.email == data.email)):
        raise HTTPException(status_code=400, detail="Correo ya registrado")
    user = User(
        full_name=data.full_name,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        role_id=data.role_id,
        is_active=data.is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "email": user.email}
