from decimal import Decimal

from pydantic import BaseModel, EmailStr


class BusinessSettingsRead(BaseModel):
    id: int
    business_name: str
    legal_name: str | None = None
    identification_type: str
    identification_number: str | None = None
    economic_activity: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    address: str | None = None
    logo_url: str | None = None
    main_currency: str
    default_tax_rate: Decimal
    ticket_footer: str | None = None
    theme: str
    fiscal_enabled: bool
    fiscal_environment: str

    model_config = {"from_attributes": True}


class BusinessSettingsUpdate(BaseModel):
    business_name: str | None = None
    legal_name: str | None = None
    identification_type: str | None = None
    identification_number: str | None = None
    economic_activity: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    address: str | None = None
    logo_url: str | None = None
    main_currency: str | None = None
    default_tax_rate: Decimal | None = None
    ticket_footer: str | None = None
    theme: str | None = None
    fiscal_enabled: bool | None = None
    fiscal_environment: str | None = None


BusinessSettingsOut = BusinessSettingsRead
BusinessSettingsIn = BusinessSettingsUpdate
