import json
from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.promotion import Promotion


def active_promotions(db: Session) -> list[Promotion]:
    now = datetime.utcnow()
    rows = db.scalars(select(Promotion).where(Promotion.is_active.is_(True))).all()
    active: list[Promotion] = []
    for promo in rows:
        if promo.starts_at and now < promo.starts_at:
            continue
        if promo.ends_at and now > promo.ends_at:
            continue
        if promo.start_time and promo.end_time:
            current = now.time()
            if not (promo.start_time <= current <= promo.end_time):
                continue
        active.append(promo)
    return active


def _product_ids(promotion: Promotion) -> set[int]:
    if not promotion.product_ids:
        return set()
    try:
        return {int(value) for value in json.loads(promotion.product_ids)}
    except Exception:
        return set()


def promotion_discount_for_line(db: Session, product: Product, quantity: Decimal, line_subtotal: Decimal) -> Decimal:
    discount = Decimal("0")
    for promo in active_promotions(db):
        ids = _product_ids(promo)
        if ids and product.id not in ids:
            continue
        if promo.rule_type == "buy_x_pay_y" and promo.buy_quantity > promo.pay_quantity > 0:
            groups = int(quantity) // promo.buy_quantity
            free_units = groups * (promo.buy_quantity - promo.pay_quantity)
            discount += product.sale_price * free_units
        elif promo.rule_type == "percent_discount" and promo.discount_percent > 0:
            discount += line_subtotal * promo.discount_percent / Decimal("100")
    return discount
