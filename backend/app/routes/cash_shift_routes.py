from datetime import datetime
from decimal import Decimal
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.cash_shift import CashShift
from app.models.payment import Payment
from app.models.sale import Sale
from app.security import get_current_user

router = APIRouter(prefix="/cash-shifts", tags=["cash-shifts"], dependencies=[Depends(get_current_user)])

class OpenShiftIn(BaseModel):
    opening_balance: Decimal

class CloseShiftIn(BaseModel):
    closing_balance: Decimal
    notes: str | None = None

@router.get("/current")
def get_current_shift(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    shift = db.scalar(select(CashShift).where(CashShift.user_id == current_user.id, CashShift.status == "open"))
    if not shift:
        return None
    
    # Recalcular totales actuales
    sales_data = db.execute(
        select(Payment.method, func.sum(Payment.amount_crc))
        .join(Sale)
        .where(Sale.created_at >= shift.opened_at, Sale.user_id == current_user.id)
        .group_by(Payment.method)
    ).all()
    
    totals = {row[0]: float(row[1]) for row in sales_data}
    shift.cash_sales = Decimal(str(totals.get("cash", 0)))
    shift.card_sales = Decimal(str(totals.get("card", 0)))
    shift.sinpe_sales = Decimal(str(totals.get("sinpe", 0)))
    shift.other_sales = Decimal(str(sum(v for k, v in totals.items() if k not in ["cash", "card", "sinpe"])))
    
    shift.expected_balance = shift.opening_balance + shift.cash_sales
    db.commit()
    
    return shift

@router.post("/open")
def open_shift(data: OpenShiftIn, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    existing = db.scalar(select(CashShift).where(CashShift.user_id == current_user.id, CashShift.status == "open"))
    if existing:
        raise HTTPException(status_code=400, detail="Ya tienes un turno abierto")
    
    shift = CashShift(
        user_id=current_user.id,
        opening_balance=data.opening_balance,
        expected_balance=data.opening_balance,
        status="open"
    )
    db.add(shift)
    db.commit()
    db.refresh(shift)
    return shift

@router.post("/close")
def close_shift(data: CloseShiftIn, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    shift = db.scalar(select(CashShift).where(CashShift.user_id == current_user.id, CashShift.status == "open"))
    if not shift:
        raise HTTPException(status_code=404, detail="No hay un turno abierto")
    
    shift.status = "closed"
    shift.closed_at = datetime.utcnow()
    shift.closing_balance = data.closing_balance
    shift.notes = data.notes
    db.commit()
    return shift


@router.get("/{shift_id}/print", response_class=HTMLResponse)
def print_shift(shift_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    shift = db.get(CashShift, shift_id)
    if shift is None or shift.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    difference = (shift.closing_balance or 0) - (shift.expected_balance or 0)
    return f"""
    <!doctype html>
    <html><head><meta charset='utf-8'><title>Cierre de caja</title>
    <style>body{{font-family:Arial,sans-serif;max-width:360px;margin:24px auto;color:#111}}.row{{display:flex;justify-content:space-between;border-bottom:1px dashed #aaa;padding:6px 0}}@media print{{button{{display:none}}}}</style></head>
    <body>
      <h2>Shoro POS</h2>
      <h3>Cierre de caja #{shift.id}</h3>
      <div class='row'><span>Apertura</span><strong>{shift.opened_at}</strong></div>
      <div class='row'><span>Cierre</span><strong>{shift.closed_at or ''}</strong></div>
      <div class='row'><span>Fondo inicial</span><strong>{shift.opening_balance}</strong></div>
      <div class='row'><span>Efectivo</span><strong>{shift.cash_sales}</strong></div>
      <div class='row'><span>Tarjeta</span><strong>{shift.card_sales}</strong></div>
      <div class='row'><span>SINPE</span><strong>{shift.sinpe_sales}</strong></div>
      <div class='row'><span>Esperado</span><strong>{shift.expected_balance}</strong></div>
      <div class='row'><span>Real</span><strong>{shift.closing_balance or ''}</strong></div>
      <div class='row'><span>Diferencia</span><strong>{difference}</strong></div>
      <p>{shift.notes or ''}</p>
      <button onclick='window.print()'>Imprimir</button>
    </body></html>
    """
