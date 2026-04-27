import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "backend"))

from sqlalchemy import select

from app.database import SessionLocal, init_db
from app.models.category import Category
from app.models.product import Product
from app.services.auth_service import ensure_default_admin


def run() -> None:
    init_db()
    db = SessionLocal()
    try:
        ensure_default_admin(db)
        if db.scalar(select(Category).where(Category.name == "General")) is None:
            category = Category(name="General", description="Productos generales")
            db.add(category)
            db.flush()
        else:
            category = db.scalar(select(Category).where(Category.name == "General"))
        if db.scalar(select(Product).where(Product.internal_code == "DEMO-001")) is None:
            db.add(
                Product(
                    internal_code="DEMO-001",
                    barcode="744000000001",
                    sku="DEMO-001",
                    cabys_code="7316150100000",
                    name="Producto demo",
                    category_id=category.id,
                    purchase_price=500,
                    sale_price=1000,
                    tax_rate=13,
                    stock=25,
                    min_stock=5,
                )
            )
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    run()
    print("Seed completado. Usuarios: admin@shoropos.local / admin123 | cajero@shoropos.local / cajero123")
