from decimal import Decimal

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str
    description: str | None = None


class CategoryRead(CategoryCreate):
    id: int
    is_active: bool

    model_config = {"from_attributes": True}


class ProductBase(BaseModel):
    internal_code: str
    barcode: str | None = None
    sku: str | None = None
    name: str
    description: str | None = None
    cabys_code: str | None = None
    category_id: int | None = None
    purchase_price: Decimal = Field(default=0, ge=0)
    sale_price: Decimal = Field(ge=0)
    tax_rate: Decimal = Field(default=13, ge=0)
    unit: str = "Unid"
    stock: Decimal = 0
    min_stock: Decimal = 0
    image_url: str | None = None
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    internal_code: str | None = None
    barcode: str | None = None
    sku: str | None = None
    name: str | None = None
    description: str | None = None
    cabys_code: str | None = None
    category_id: int | None = None
    purchase_price: Decimal | None = None
    sale_price: Decimal | None = None
    tax_rate: Decimal | None = None
    unit: str | None = None
    stock: Decimal | None = None
    min_stock: Decimal | None = None
    image_url: str | None = None
    is_active: bool | None = None


class ProductRead(ProductBase):
    id: int

    model_config = {"from_attributes": True}


ProductOut = ProductRead
