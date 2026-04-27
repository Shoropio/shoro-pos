from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.security import get_current_user
from app.services.exchange_service import get_usd_crc_rate

router = APIRouter(prefix="/exchange", tags=["exchange"], dependencies=[Depends(get_current_user)])


@router.get("/usd-crc")
def usd_crc(refresh: bool = False, db: Session = Depends(get_db)):
    return get_usd_crc_rate(db, refresh)
