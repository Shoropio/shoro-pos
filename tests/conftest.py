import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

TEST_DB = ROOT / "database" / "test_shoro_pos.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["AUTO_CREATE_TABLES"] = "true"

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models.category import Category  # noqa: E402
from app.models.product import Product  # noqa: E402
from app.services.auth_service import ensure_default_admin  # noqa: E402


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        ensure_default_admin(db)
        category = Category(name="General", description="Test")
        db.add(category)
        db.flush()
        db.add(
            Product(
                internal_code="TEST-001",
                barcode="744000000001",
                sku="TEST-001",
                cabys_code="7316150100000",
                name="Producto test",
                category_id=category.id,
                purchase_price=500,
                sale_price=1000,
                tax_rate=13,
                stock=100,
                min_stock=5,
            )
        )
        db.commit()
    yield


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def auth_headers(client):
    response = client.post("/auth/login", json={"email": "admin@shoropos.local", "password": "admin123"})
    response.raise_for_status()
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
