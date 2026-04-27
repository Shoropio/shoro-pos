from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class BusinessSettings(Base):
    __tablename__ = "business_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    business_name: Mapped[str] = mapped_column(String(180), default="Shoro POS")
    legal_name: Mapped[str | None] = mapped_column(String(180))
    logo_url: Mapped[str | None] = mapped_column(String(500))
    identification_type: Mapped[str] = mapped_column(String(20), default="juridica")
    identification_number: Mapped[str | None] = mapped_column(String(40))
    economic_activity: Mapped[str | None] = mapped_column(String(20))
    address: Mapped[str | None] = mapped_column(Text)
    phone: Mapped[str | None] = mapped_column(String(40))
    email: Mapped[str | None] = mapped_column(String(160))
    main_currency: Mapped[str] = mapped_column(String(3), default="CRC")
    default_tax_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=13)
    ticket_footer: Mapped[str | None] = mapped_column(String(500))
    theme: Mapped[str] = mapped_column(String(20), default="light")
    dark_mode: Mapped[bool] = mapped_column(Boolean, default=False)
    fiscal_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    fiscal_environment: Mapped[str] = mapped_column(String(20), default="sandbox")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
