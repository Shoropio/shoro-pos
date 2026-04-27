from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user_schema import LoginRequest, TokenResponse, UserRead
from app.security import get_current_user
from app.services.auth_service import authenticate_user, ensure_default_admin, permissions_for_user, token_for_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    ensure_default_admin(db)
    user = authenticate_user(db, payload.email, payload.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contrasena invalidos")
    return TokenResponse(
        access_token=token_for_user(user),
        role=user.role.name if user.role else None,
        permissions=permissions_for_user(user),
    )


@router.get("/me", response_model=UserRead)
def me(current_user=Depends(get_current_user)) -> UserRead:
    return UserRead(
        id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        role=current_user.role.name if current_user.role else "cajero",
        is_active=current_user.is_active,
    )


@router.get("/permissions")
def permissions(current_user=Depends(get_current_user)):
    return {"role": current_user.role.name if current_user.role else None, "permissions": permissions_for_user(current_user)}
