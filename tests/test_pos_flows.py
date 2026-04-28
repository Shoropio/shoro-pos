from io import BytesIO

from openpyxl import Workbook


def test_health_and_login(client):
    assert client.get("/health").json()["status"] == "ok"
    assert client.get("/ready").json()["database"] == "ok"
    response = client.post("/auth/login", json={"email": "admin@shoropos.local", "password": "admin123"})
    assert response.status_code == 200
    assert response.json()["permissions"]["all"] is True
    cashier = client.post("/auth/login", json={"email": "cajero@shoropos.local", "password": "cajero123"})
    assert cashier.status_code == 200
    assert cashier.json()["role"] == "cajero"
    assert cashier.json()["permissions"]["sales.create"] is True


def test_multicurrency_sale_with_promotion(client, auth_headers):
    product = client.get("/products", headers=auth_headers).json()[0]
    promo = client.post(
        "/promotions",
        headers=auth_headers,
        json={
            "name": "3x2 test",
            "rule_type": "buy_x_pay_y",
            "product_ids": [product["id"]],
            "buy_quantity": 3,
            "pay_quantity": 2,
            "discount_percent": 0,
            "is_active": True,
        },
    )
    assert promo.status_code == 200
    sale = client.post(
        "/sales",
        headers=auth_headers,
        json={
            "items": [{"product_id": product["id"], "quantity": 3, "discount": 0}],
            "payments": [{"method": "cash", "amount": 20, "currency": "USD", "exchange_rate": 520}],
        },
    )
    assert sale.status_code == 200, sale.text
    data = sale.json()
    assert float(data["discount_total"]) == 1000
    assert float(data["paid_total_crc"]) == 10400
    assert data["change_amount_crc"] != "0.00"


def test_customer_loyalty_points(client, auth_headers):
    customer = client.post("/customers", headers=auth_headers, json={"name": "Cliente puntos", "email": "puntos@example.com"})
    assert customer.status_code == 201
    product = client.get("/products", headers=auth_headers).json()[0]
    sale = client.post(
        "/sales",
        headers=auth_headers,
        json={
            "customer_id": customer.json()["id"],
            "items": [{"product_id": product["id"], "quantity": 2, "discount": 0}],
            "payments": [{"method": "cash", "amount": 2260, "currency": "CRC", "exchange_rate": 1}],
        },
    )
    assert sale.status_code == 200
    customers = client.get("/customers", headers=auth_headers).json()
    updated = next(row for row in customers if row["id"] == customer.json()["id"])
    assert updated["points_balance"] >= 2


def test_excel_import(client, auth_headers):
    wb = Workbook()
    ws = wb.active
    ws.append(["codigo", "nombre", "precio", "stock", "iva"])
    ws.append(["IMP-001", "Importado", 1500, 10, 13])
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    response = client.post(
        "/products/import",
        headers=auth_headers,
        files={"file": ("productos.xlsx", buffer.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert response.status_code == 200, response.text
    assert response.json()["created"] == 1


def test_offline_sync_is_idempotent(client, auth_headers):
    product = client.get("/products", headers=auth_headers).json()[0]
    payload = {
        "client_uuid": "offline-1",
        "payload": {
            "items": [{"product_id": product["id"], "quantity": 1, "discount": 0}],
            "payments": [{"method": "cash", "amount": 1130, "currency": "CRC", "exchange_rate": 1}],
        },
    }
    first = client.post("/sync/sales", headers=auth_headers, json=[payload])
    second = client.post("/sync/sales", headers=auth_headers, json=[payload])
    assert first.status_code == 200
    assert second.json()["results"][0]["status"] == "already_synced"
