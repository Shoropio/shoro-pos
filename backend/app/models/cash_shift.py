from datetime import datetime
from decimal import Decimal

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.database import Base


class CashShift(Base):
    __tablename__ = "cash_shifts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    opened_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    
    opening_balance = Column(Numeric(12, 2), default=0)
    expected_balance = Column(Numeric(12, 2), default=0)
    closing_balance = Column(Numeric(12, 2), nullable=True)
    
    cash_sales = Column(Numeric(12, 2), default=0)
    card_sales = Column(Numeric(12, 2), default=0)
    sinpe_sales = Column(Numeric(12, 2), default=0)
    other_sales = Column(Numeric(12, 2), default=0)
    
    status = Column(String, default="open")  # open, closed
    notes = Column(String, nullable=True)

    user = relationship("User")
