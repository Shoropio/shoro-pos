from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.inventory import InventoryMovement
from app.models.product import Product


def register_movement(
    db: Session,
    product: Product,
    movement_type: str,
    quantity: Decimal,
    reason: str,
    user_id: int | None = None,
    reference: str | None = None,
) -> InventoryMovement:
    if movement_type in {"entrada", "ajuste_positivo"}:
        product.stock += quantity
    elif movement_type in {"salida", "venta", "ajuste_negativo"}:
        product.stock -= quantity
    else:
        raise ValueError("Tipo de movimiento inválido")

    movement = InventoryMovement(
        product_id=product.id,
        user_id=user_id,
        movement_type=movement_type,
        quantity=quantity,
        reason=reason,
        reference=reference,
    )
    db.add(movement)
    return movement
