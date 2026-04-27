from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.settings import BusinessSettings
from app.models.product import Product
from app.schemas.sale_schema import SaleCreate, SaleOut
from app.security import get_current_user
from app.services.auth_service import require_permission
from app.services.sale_service import create_sale, get_sale, list_sales
from app.services.ticket_service import ticket_service


router = APIRouter(prefix="/sales", tags=["sales"])


@router.get("", response_model=list[SaleOut])
def index(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return list_sales(db)


@router.post("", response_model=SaleOut)
def create(data: SaleCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if data.global_discount > 0 or any(item.discount_amount > 0 for item in data.items):
        require_permission(current_user, "pos.apply_discount")
    for item in data.items:
        product = db.get(Product, item.product_id)
        if product and item.discount_amount > 0 and item.discount_amount >= product.sale_price * item.quantity * 0.5:
            require_permission(current_user, "pos.apply_discount_50")
    return create_sale(db, data, current_user.id)


@router.get("/{sale_id}", response_model=SaleOut)
def show(sale_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return get_sale(db, sale_id)


@router.get("/{sale_id}/ticket", response_class=HTMLResponse)
def get_ticket(sale_id: int, db: Session = Depends(get_db)):
    sale = get_sale(db, sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    
    settings = db.query(BusinessSettings).first()
    if not settings:
        settings = BusinessSettings() # Defaults if not configured
        
    html = ticket_service.generate_html_ticket(sale, settings)
    return HTMLResponse(content=html)
