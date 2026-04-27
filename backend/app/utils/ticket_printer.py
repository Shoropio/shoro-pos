from app.models.sale import Sale


def render_ticket(sale: Sale, business_name: str = "Shoro POS") -> str:
    lines = [business_name, f"Venta {sale.sale_number}", "=" * 32]
    for item in sale.items:
        lines.append(f"{item.quantity} x {item.product_name[:18]:18} {item.line_total:>8}")
    lines.extend(["=" * 32, f"Subtotal: {sale.subtotal}", f"IVA: {sale.tax_total}", f"TOTAL: {sale.total}"])
    return "\n".join(lines)
