from datetime import datetime, time
from io import BytesIO
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.sale import Sale
from app.security import get_current_user
from app.services.report_service import dashboard, sales_report


router = APIRouter(prefix="/reports", tags=["reports"], dependencies=[Depends(get_current_user)])


@router.get("/dashboard")
def dashboard_report(db: Session = Depends(get_db)):
    return dashboard(db)


@router.get("/sales")
def sales_analytics(start: str | None = None, end: str | None = None, db: Session = Depends(get_db)):
    # Defaults to last 30 days
    end_dt = datetime.utcnow()
    start_dt = datetime.combine(datetime.utcnow().date(), time.min) # Simplified for now
    return sales_report(db, start_dt, end_dt)


def _sales_rows(db: Session):
    sales = db.scalars(select(Sale).order_by(Sale.created_at.desc()).limit(1000))
    return [[s.sale_number, s.created_at.isoformat(), s.currency, float(s.total), float(s.tax_total), s.payment_status, s.fiscal_status] for s in sales]


@router.get("/sales/export.xlsx")
def export_sales_xlsx(db: Session = Depends(get_db)):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Ventas"
    sheet.append(["Venta", "Fecha", "Moneda", "Total", "IVA", "Pago", "Fiscal"])
    for row in _sales_rows(db):
        sheet.append(row)
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=ventas_shoro.xlsx"},
    )


@router.get("/sales/export.pdf")
def export_sales_pdf(db: Session = Depends(get_db)):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(40, 740, "Reporte de ventas - Shoro POS")
    pdf.setFont("Helvetica", 9)
    y = 700
    for row in _sales_rows(db)[:60]:
        pdf.drawString(40, y, f"{row[0]}  {row[1][:16]}  {row[2]} {row[3]:,.2f}  {row[5]} / {row[6]}")
        y -= 16
        if y < 60:
            pdf.showPage()
            pdf.setFont("Helvetica", 9)
            y = 740
    pdf.save()
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=ventas_shoro.pdf"})
