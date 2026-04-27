from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class SaleItemCreate(BaseModel):
    product_id: int
    quantity: Decimal = Field(gt=0)
    discount_amount: Decimal = Field(default=0, ge=0, alias="discount")

    model_config = {"populate_by_name": True}


class PaymentCreate(BaseModel):
    method: str
    amount: Decimal = Field(gt=0)
    reference: str | None = None


class SaleCreate(BaseModel):
    customer_id: int | None = None
    currency: str = "CRC"
    exchange_rate: Decimal = 1
    global_discount: Decimal = 0
    items: list[SaleItemCreate]
    payments: list[PaymentCreate]
    fiscal_document_type: str | None = None


class SaleItemRead(BaseModel):
    id: int
    product_id: int
    product_name: str
    cabys_code: str | None
    quantity: Decimal
    unit_price: Decimal
    discount_amount: Decimal
    tax_rate: Decimal
    tax_amount: Decimal
    line_total: Decimal

    model_config = {"from_attributes": True}


class PaymentRead(BaseModel):
    id: int
    method: str
    amount: Decimal
    reference: str | None

    model_config = {"from_attributes": True}


class SaleRead(BaseModel):
    id: int
    sale_number: str
    customer_id: int | None
    currency: str
    subtotal: Decimal
    discount_total: Decimal
    tax_total: Decimal
    total: Decimal
    payment_status: str
    fiscal_status: str
    status: str
    created_at: datetime
    ticket_text: str | None = None
    items: list[SaleItemRead] = []
    payments: list[PaymentRead] = []

    model_config = {"from_attributes": True}


SaleOut = SaleRead


SaleOut = SaleRead
