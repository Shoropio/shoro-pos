import json

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import ROLE_ADMIN, ROLE_CASHIER, ROLE_SUPERVISOR, Role, User
from app.security import create_access_token, get_password_hash, verify_password


def ensure_default_admin(db: Session) -> None:
    defaults = {
        ROLE_ADMIN: {"all": True},
        ROLE_SUPERVISOR: {
            "pos.apply_discount": True,
            "pos.apply_discount_50": True,
            "pos.remove_cart_item": True,
            "sales.create": True,
            "products.import": True,
        },
        ROLE_CASHIER: {
            "sales.create": True,
            "pos.remove_cart_item": False,
            "pos.apply_discount": False,
            "pos.apply_discount_50": False,
        },
    }
    roles: dict[str, Role] = {}
    for role_name, permissions in defaults.items():
        role = db.scalar(select(Role).where(Role.name == role_name))
        if role is None:
            role = Role(name=role_name, permissions=json.dumps(permissions))
            db.add(role)
            db.flush()
        roles[role_name] = role
    if db.scalar(select(User).where(User.email == "admin@shoropos.local")) is None:
        db.add(
            User(
                full_name="Administrador",
                email="admin@shoropos.local",
                hashed_password=get_password_hash("admin123"),
                role_id=roles[ROLE_ADMIN].id,
            )
        )
    db.commit()


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.scalar(select(User).where(User.email == email, User.is_active.is_(True)))
    if user is None or not verify_password(password, user.hashed_password):
        return None
    return user


def token_for_user(user: User) -> str:
    role_name = user.role.name if user.role else None
    return create_access_token(str(user.id), {"role": role_name, "permissions": permissions_for_user(user)})


def permissions_for_user(user: User) -> dict:
    if not user.role:
        return {}
    try:
        return json.loads(user.role.permissions or "{}")
    except json.JSONDecodeError:
        return {}


def has_permission(user: User, permission: str) -> bool:
    permissions = permissions_for_user(user)
    return bool(permissions.get("all") or permissions.get(permission))


def require_permission(user: User, permission: str) -> None:
    if not has_permission(user, permission):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Permiso requerido: {permission}")
