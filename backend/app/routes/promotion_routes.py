import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.promotion import Promotion
from app.schemas.promotion_schema import PromotionIn
from app.security import get_current_user

router = APIRouter(prefix="/promotions", tags=["promotions"], dependencies=[Depends(get_current_user)])


def serialize(promotion: Promotion) -> dict:
    try:
        product_ids = json.loads(promotion.product_ids or "[]")
    except Exception:
        product_ids = []
    return {
        "id": promotion.id,
        "name": promotion.name,
        "rule_type": promotion.rule_type,
        "product_ids": product_ids,
        "buy_quantity": promotion.buy_quantity,
        "pay_quantity": promotion.pay_quantity,
        "discount_percent": float(promotion.discount_percent),
        "starts_at": promotion.starts_at,
        "ends_at": promotion.ends_at,
        "start_time": promotion.start_time,
        "end_time": promotion.end_time,
        "is_active": promotion.is_active,
    }


@router.get("")
def list_promotions(db: Session = Depends(get_db)):
    return [serialize(row) for row in db.scalars(select(Promotion).order_by(Promotion.created_at.desc()))]


@router.post("")
def create_promotion(data: PromotionIn, db: Session = Depends(get_db)):
    promotion = Promotion(**data.model_dump(exclude={"product_ids"}), product_ids=json.dumps(data.product_ids))
    db.add(promotion)
    db.commit()
    db.refresh(promotion)
    return serialize(promotion)


@router.put("/{promotion_id}")
def update_promotion(promotion_id: int, data: PromotionIn, db: Session = Depends(get_db)):
    promotion = db.get(Promotion, promotion_id)
    if promotion is None:
        raise HTTPException(status_code=404, detail="Promocion no encontrada")
    for key, value in data.model_dump(exclude={"product_ids"}).items():
        setattr(promotion, key, value)
    promotion.product_ids = json.dumps(data.product_ids)
    db.commit()
    db.refresh(promotion)
    return serialize(promotion)
