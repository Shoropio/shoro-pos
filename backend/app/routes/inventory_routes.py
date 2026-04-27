from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.inventory import InventoryMovement
from app.models.product import Product
from app.security import get_current_user
from app.services.inventory_service import register_movement


router = APIRouter(prefix="/inventory", tags=["inventory"], dependencies=[Depends(get_current_user)])


class MovementIn(BaseModel):
    product_id: int
    movement_type: str
    quantity: Decimal = Field(gt=0)
    reason: str


@router.get("/movements")
def movements(db: Session = Depends(get_db)):
    rows = db.scalars(select(InventoryMovement).order_by(InventoryMovement.created_at.desc()).limit(200))
    return [
        {
            "id": row.id,
            "product_id": row.product_id,
            "movement_type": row.movement_type,
            "quantity": float(row.quantity),
            "reason": row.reason,
            "created_at": row.created_at,
        }
        for row in rows
    ]


@router.get("/low-stock")
def low_stock(db: Session = Depends(get_db)):
    rows = db.scalars(select(Product).where(Product.stock <= Product.min_stock, Product.is_active.is_(True)))
    return [{"id": p.id, "name": p.name, "stock": float(p.stock), "min_stock": float(p.min_stock)} for p in rows]


@router.post("/movements")
def create_movement(data: MovementIn, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    product = db.get(Product, data.product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    movement = register_movement(db, product, data.movement_type, data.quantity, data.reason, current_user.id)
    db.commit()
    return {"id": movement.id, "stock": float(product.stock)}
