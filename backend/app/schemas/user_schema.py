from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class Token(TokenResponse):
    pass


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str = "cashier"


class UserRead(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    is_active: bool

    model_config = {"from_attributes": True}


class UserOut(UserRead):
    role: str | None = None
