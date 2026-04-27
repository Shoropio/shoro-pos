from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product_schema import ProductCreate, ProductUpdate
from app.services.barcode_service import barcode_service


def list_products(db: Session, q: str | None = None) -> list[Product]:
    stmt = select(Product).order_by(Product.name)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            or_(
                Product.name.ilike(like),
                Product.internal_code.ilike(like),
                Product.sku.ilike(like),
                Product.barcode.ilike(like),
            )
        )
    return list(db.scalars(stmt))


def create_product(db: Session, data: ProductCreate) -> Product:
    product = Product(**data.model_dump())
    if not product.barcode and product.internal_code:
        product.barcode = barcode_service.generate_internal_barcode(product.internal_code)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product: Product, data: ProductUpdate) -> Product:
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product
