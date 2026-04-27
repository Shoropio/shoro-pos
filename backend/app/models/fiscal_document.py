from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class FiscalDocument(Base):
    __tablename__ = "fiscal_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sale_id: Mapped[int | None] = mapped_column(ForeignKey("sales.id"), nullable=True)
    document_type: Mapped[str] = mapped_column(String(40), nullable=False)
    consecutive: Mapped[str | None] = mapped_column(String(30), unique=True)
    clave: Mapped[str | None] = mapped_column(String(60), unique=True, index=True)
    environment: Mapped[str] = mapped_column(String(20), default="sandbox")
    status: Mapped[str] = mapped_column(String(30), default="pendiente")
    xml_generated: Mapped[str | None] = mapped_column(Text)
    xml_signed: Mapped[str | None] = mapped_column(Text)
    hacienda_response: Mapped[str | None] = mapped_column(Text)
    error_message: Mapped[str | None] = mapped_column(Text)
    customer_email_sent_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sale: Mapped["Sale | None"] = relationship(back_populates="fiscal_documents")


class FiscalLog(Base):
    __tablename__ = "fiscal_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fiscal_document_id: Mapped[int | None] = mapped_column(ForeignKey("fiscal_documents.id"), nullable=True)
    level: Mapped[str] = mapped_column(String(20), default="info")
    event: Mapped[str] = mapped_column(String(120), nullable=False)
    detail: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class FiscalConsecutive(Base):
    __tablename__ = "fiscal_consecutives"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_type: Mapped[str] = mapped_column(String(40), nullable=False)
    branch_code: Mapped[str] = mapped_column(String(3), default="001")
    terminal_code: Mapped[str] = mapped_column(String(5), default="00001")
    current_number: Mapped[int] = mapped_column(Integer, default=0)
    environment: Mapped[str] = mapped_column(String(20), default="sandbox")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
