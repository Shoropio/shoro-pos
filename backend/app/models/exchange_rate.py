from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    base_currency: Mapped[str] = mapped_column(String(3), default="USD", index=True)
    target_currency: Mapped[str] = mapped_column(String(3), default="CRC", index=True)
    buy_rate: Mapped[Decimal] = mapped_column(Numeric(12, 4), default=0)
    sell_rate: Mapped[Decimal] = mapped_column(Numeric(12, 4), default=0)
    source: Mapped[str] = mapped_column(String(40), default="manual")
    fetched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
