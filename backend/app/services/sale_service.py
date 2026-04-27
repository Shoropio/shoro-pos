from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.fiscal_cr.xml_builder import build_comprobante_xml
from app.models.payment import Payment
from app.models.product import Product
from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.schemas.sale_schema import SaleCreate
from app.services.inventory_service import register_movement


TWOPLACES = Decimal("0.01")


def money(value: Decimal) -> Decimal:
    return value.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def next_sale_number(db: Session) -> str:
    today = datetime.utcnow().strftime("%Y%m%d")
    count = db.scalar(select(Sale).where(Sale.sale_number.like(f"V-{today}-%")).count()) if False else None
    last_id = db.scalar(select(Sale.id).order_by(Sale.id.desc()).limit(1)) or 0
    return f"V-{today}-{last_id + 1:06d}"


def create_sale(db: Session, data: SaleCreate, user_id: int | None) -> Sale:
    if not data.items:
        raise HTTPException(status_code=400, detail="La venta debe incluir productos")

    sale = Sale(sale_number=next_sale_number(db), customer_id=data.customer_id, user_id=user_id, currency=data.currency)
    db.add(sale)
    db.flush()

    subtotal = Decimal("0")
    discount_total = data.global_discount
    tax_total = Decimal("0")

    for item_in in data.items:
        product = db.get(Product, item_in.product_id)
        if product is None or not product.is_active:
            raise HTTPException(status_code=404, detail=f"Producto {item_in.product_id} no encontrado")
        if product.stock < item_in.quantity:
            raise HTTPException(status_code=400, detail=f"Stock insuficiente para {product.name}")

        line_subtotal = money(product.sale_price * item_in.quantity)
        taxable_base = max(Decimal("0"), line_subtotal - item_in.discount_amount)
        tax_amount = money(taxable_base * product.tax_rate / Decimal("100"))
        line_total = money(taxable_base + tax_amount)

        sale_item = SaleItem(
            sale_id=sale.id,
            product_id=product.id,
            product_name=product.name,
            cabys_code=product.cabys_code,
            quantity=item_in.quantity,
            unit_price=product.sale_price,
            discount_amount=item_in.discount_amount,
            tax_rate=product.tax_rate,
            tax_amount=tax_amount,
            line_total=line_total,
        )
        db.add(sale_item)
        register_movement(db, product, "venta", item_in.quantity, "Venta POS", user_id=user_id, reference=sale.sale_number)
        subtotal += line_subtotal
        discount_total += item_in.discount_amount
        tax_total += tax_amount

    total = money(subtotal - discount_total + tax_total)
    paid = sum((payment.amount for payment in data.payments), Decimal("0"))
    if paid < total:
        raise HTTPException(status_code=400, detail="El pago no cubre el total de la venta")

    for payment_in in data.payments:
        db.add(Payment(sale_id=sale.id, **payment_in.model_dump()))

    sale.subtotal = money(subtotal)
    sale.discount_total = money(discount_total)
    sale.tax_total = money(tax_total)
    sale.total = total
    sale.ticket_text = build_ticket(sale)
    if data.fiscal_document_type:
        sale.fiscal_status = "pendiente"

    db.commit()
    return get_sale(db, sale.id)


def get_sale(db: Session, sale_id: int) -> Sale:
    sale = db.scalar(
        select(Sale)
        .where(Sale.id == sale_id)
        .options(selectinload(Sale.items), selectinload(Sale.payments), selectinload(Sale.customer))
    )
    if sale is None:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return sale


def list_sales(db: Session) -> list[Sale]:
    return list(
        db.scalars(
            select(Sale)
            .order_by(Sale.created_at.desc())
            .options(selectinload(Sale.items), selectinload(Sale.payments))
            .limit(200)
        )
    )


def build_ticket(sale: Sale) -> str:
    lines = ["SHORO POS", f"Venta: {sale.sale_number}", "-" * 32]
    for item in sale.items:
        lines.append(f"{item.product_name} x {item.quantity} = {item.line_total}")
    lines.extend(["-" * 32, f"Subtotal: {sale.subtotal}", f"IVA: {sale.tax_total}", f"Total: {sale.total}"])
    return "\n".join(lines)
