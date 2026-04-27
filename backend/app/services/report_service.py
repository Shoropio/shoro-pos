from datetime import datetime, time
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.sale import Sale
from app.models.sale_item import SaleItem


def dashboard(db: Session) -> dict:
    start = datetime.combine(datetime.utcnow().date(), time.min)
    sales_today = db.scalar(select(func.count(Sale.id)).where(Sale.created_at >= start)) or 0
    total_today = db.scalar(select(func.coalesce(func.sum(Sale.total), 0)).where(Sale.created_at >= start)) or Decimal("0")
    tax_today = db.scalar(select(func.coalesce(func.sum(Sale.tax_total), 0)).where(Sale.created_at >= start)) or Decimal("0")
    low_stock = list(db.scalars(select(Product).where(Product.stock <= Product.min_stock, Product.is_active.is_(True)).limit(10)))
    top_products = db.execute(
        select(SaleItem.product_name, func.sum(SaleItem.quantity).label("qty"))
        .group_by(SaleItem.product_name)
        .order_by(func.sum(SaleItem.quantity).desc())
        .limit(5)
    ).all()
    recent_sales = list(db.scalars(select(Sale).order_by(Sale.created_at.desc()).limit(8)))
    return {
        "sales_today": sales_today,
        "sales_count": sales_today,
        "total_today": float(total_today),
        "total_billed": float(total_today),
        "tax_today": float(tax_today),
        "estimated_profit": 0,
        "low_stock": [{"id": p.id, "name": p.name, "stock": float(p.stock)} for p in low_stock],
        "top_products": [{"name": name, "quantity": float(qty)} for name, qty in top_products],
        "recent_sales": [{"id": s.id, "sale_number": s.sale_number, "total": float(s.total), "fiscal_status": s.fiscal_status} for s in recent_sales],
    }
