from datetime import datetime, time
from decimal import Decimal

from pydantic import BaseModel


class PromotionIn(BaseModel):
    name: str
    rule_type: str
    product_ids: list[int] = []
    buy_quantity: int = 0
    pay_quantity: int = 0
    discount_percent: Decimal = 0
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    start_time: time | None = None
    end_time: time | None = None
    is_active: bool = True


class PromotionOut(PromotionIn):
    id: int

    model_config = {"from_attributes": True}
