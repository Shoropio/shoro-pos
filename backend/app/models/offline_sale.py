from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class OfflineSaleSync(Base):
    __tablename__ = "offline_sale_sync"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_uuid: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(30), default="pending")
    payload: Mapped[str] = mapped_column(Text)
    sale_id: Mapped[int | None] = mapped_column(ForeignKey("sales.id"))
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    synced_at: Mapped[datetime | None] = mapped_column(DateTime)
