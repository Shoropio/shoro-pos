from decimal import Decimal

from pydantic import BaseModel, EmailStr


class CustomerBase(BaseModel):
    name: str
    identification_type: str = "fisica"
    identification_number: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None
    credit_limit: Decimal = 0
    points_balance: int = 0
    lifetime_points: int = 0
    is_active: bool = True


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: str | None = None
    identification_type: str | None = None
    identification_number: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None
    credit_limit: Decimal | None = None
    points_balance: int | None = None
    is_active: bool | None = None


class CustomerRead(CustomerBase):
    id: int

    model_config = {"from_attributes": True}


CustomerOut = CustomerRead
