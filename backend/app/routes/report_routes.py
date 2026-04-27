from datetime import datetime, time
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
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
