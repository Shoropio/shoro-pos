from datetime import datetime, time
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Promotion(Base):
    __tablename__ = "promotions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    rule_type: Mapped[str] = mapped_column(String(40), nullable=False)  # buy_x_pay_y, percent_discount
    product_ids: Mapped[str | None] = mapped_column(Text)
    buy_quantity: Mapped[int] = mapped_column(Integer, default=0)
    pay_quantity: Mapped[int] = mapped_column(Integer, default=0)
    discount_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    starts_at: Mapped[datetime | None] = mapped_column(DateTime)
    ends_at: Mapped[datetime | None] = mapped_column(DateTime)
    start_time: Mapped[time | None] = mapped_column(Time)
    end_time: Mapped[time | None] = mapped_column(Time)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
