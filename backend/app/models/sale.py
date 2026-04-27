from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sale_number: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id"), nullable=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="pagada")
    payment_status: Mapped[str] = mapped_column(String(30), default="pagada")
    fiscal_status: Mapped[str] = mapped_column(String(30), default="sin_enviar")
    currency: Mapped[str] = mapped_column(String(3), default="CRC")
    exchange_rate: Mapped[Decimal] = mapped_column(Numeric(12, 4), default=1)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    discount_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    tax_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    total_crc: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    paid_total_crc: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    change_amount_crc: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    points_earned: Mapped[int] = mapped_column(Integer, default=0)
    points_redeemed: Mapped[int] = mapped_column(Integer, default=0)
    ticket_text: Mapped[str | None] = mapped_column(String(4000))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    customer: Mapped["Customer | None"] = relationship(back_populates="sales")
    user: Mapped["User | None"] = relationship(back_populates="sales")
    items: Mapped[list["SaleItem"]] = relationship(back_populates="sale", cascade="all, delete-orphan")
    payments: Mapped[list["Payment"]] = relationship(back_populates="sale", cascade="all, delete-orphan")
    fiscal_documents: Mapped[list["FiscalDocument"]] = relationship(back_populates="sale")
