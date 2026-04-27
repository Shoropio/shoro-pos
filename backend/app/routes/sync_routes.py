import json
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.offline_sale import OfflineSaleSync
from app.schemas.sale_schema import SaleCreate
from app.security import get_current_user
from app.services.sale_service import create_sale

router = APIRouter(prefix="/sync", tags=["sync"], dependencies=[Depends(get_current_user)])


class OfflineSaleIn(BaseModel):
    client_uuid: str
    payload: SaleCreate


@router.post("/sales")
def sync_sales(items: list[OfflineSaleIn], db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    results = []
    for item in items:
        existing = db.query(OfflineSaleSync).filter(OfflineSaleSync.client_uuid == item.client_uuid).first()
        if existing and existing.status == "synced":
            results.append({"client_uuid": item.client_uuid, "status": "already_synced", "sale_id": existing.sale_id})
            continue
        record = existing or OfflineSaleSync(client_uuid=item.client_uuid, user_id=current_user.id, payload=item.payload.model_dump_json())
        if not existing:
            db.add(record)
            db.flush()
        try:
            sale = create_sale(db, item.payload, current_user.id)
            record.status = "synced"
            record.sale_id = sale.id
            record.synced_at = datetime.utcnow()
            record.error_message = None
            record.payload = item.payload.model_dump_json()
            results.append({"client_uuid": item.client_uuid, "status": "synced", "sale_id": sale.id})
        except Exception as exc:
            record.status = "error"
            record.error_message = str(exc)
            record.payload = json.dumps(item.payload.model_dump(mode="json"))
            results.append({"client_uuid": item.client_uuid, "status": "error", "error": str(exc)})
        db.commit()
    return {"results": results}
