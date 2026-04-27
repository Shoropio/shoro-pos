from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import ROLE_ADMIN, Role, User
from app.security import create_access_token, get_password_hash, verify_password


def ensure_default_admin(db: Session) -> None:
    admin_role = db.scalar(select(Role).where(Role.name == ROLE_ADMIN))
    if admin_role is None:
        admin_role = Role(name=ROLE_ADMIN, permissions='{"all": true}')
        db.add(admin_role)
        db.flush()
    if db.scalar(select(User).where(User.email == "admin@shoropos.local")) is None:
        db.add(
            User(
                full_name="Administrador",
                email="admin@shoropos.local",
                hashed_password=get_password_hash("admin123"),
                role_id=admin_role.id,
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
    return create_access_token(str(user.id), {"role": role_name})
