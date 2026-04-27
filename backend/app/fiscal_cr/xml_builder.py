from decimal import Decimal
from xml.etree.ElementTree import Element, SubElement, tostring

from app.models.sale import Sale


NS_44 = "https://cdn.comprobanteselectronicos.go.cr/xml-schemas/v4.4/facturaElectronica"


def text(parent: Element, name: str, value: object | None) -> Element:
    child = SubElement(parent, name)
    child.text = "" if value is None else str(value)
    return child


def build_comprobante_xml(
    sale: Sale,
    clave: str = "",
    consecutivo: str = "",
    emisor: dict | None = None,
    receptor: dict | None = None,
    document_type: str = "tiquete_electronico",
) -> str:
    root_name = "FacturaElectronica" if document_type == "factura_electronica" else "TiqueteElectronico"
    root = Element(root_name, {"xmlns": NS_44})
    text(root, "Clave", clave)
    text(root, "CodigoActividadEmisor", (emisor or {}).get("actividad_economica", "000000"))
    text(root, "NumeroConsecutivo", consecutivo)
    text(root, "FechaEmision", sale.created_at.isoformat())
    add_party(root, "Emisor", emisor or {"nombre": "Shoro POS", "tipo": "02", "numero": "0000000000"})
    if receptor:
        add_party(root, "Receptor", receptor)
    text(root, "CondicionVenta", "01")
    text(root, "MedioPago", sale.payments[0].method if sale.payments else "01")
    detalle = SubElement(root, "DetalleServicio")
    for idx, item in enumerate(sale.items, start=1):
        line = SubElement(detalle, "LineaDetalle")
        text(line, "NumeroLinea", idx)
        if item.cabys_code:
            text(line, "CodigoCABYS", item.cabys_code)
        text(line, "Cantidad", item.quantity)
        text(line, "UnidadMedida", "Unid")
        text(line, "Detalle", item.product_name)
        text(line, "PrecioUnitario", item.unit_price)
        text(line, "MontoTotal", item.unit_price * item.quantity)
        if item.discount_amount > Decimal("0"):
            discount = SubElement(line, "Descuento")
            text(discount, "MontoDescuento", item.discount_amount)
            text(discount, "NaturalezaDescuento", "Descuento comercial")
        text(line, "SubTotal", item.line_total - item.tax_amount)
        tax = SubElement(line, "Impuesto")
        text(tax, "Codigo", "01")
        text(tax, "CodigoTarifaIVA", "08" if item.tax_rate == Decimal("13") else "01")
        text(tax, "Tarifa", item.tax_rate)
        text(tax, "Monto", item.tax_amount)
        text(line, "MontoTotalLinea", item.line_total)
    resumen = SubElement(root, "ResumenFactura")
    moneda = SubElement(resumen, "CodigoTipoMoneda")
    text(moneda, "CodigoMoneda", sale.currency)
    text(moneda, "TipoCambio", sale.exchange_rate)
    text(resumen, "TotalVenta", sale.subtotal)
    text(resumen, "TotalDescuentos", sale.discount_total)
    text(resumen, "TotalVentaNeta", sale.subtotal - sale.discount_total)
    text(resumen, "TotalImpuesto", sale.tax_total)
    text(resumen, "TotalComprobante", sale.total)
    return tostring(root, encoding="unicode")


def add_party(parent: Element, name: str, data: dict) -> None:
    party = SubElement(parent, name)
    text(party, "Nombre", data.get("nombre") or data.get("name"))
    identification = SubElement(party, "Identificacion")
    text(identification, "Tipo", data.get("tipo") or data.get("tipo_identificacion") or "02")
    text(identification, "Numero", data.get("numero") or data.get("numero_identificacion") or "0000000000")
    if data.get("correo"):
        text(party, "CorreoElectronico", data["correo"])
