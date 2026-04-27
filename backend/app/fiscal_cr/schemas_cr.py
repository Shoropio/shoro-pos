from decimal import Decimal

from pydantic import BaseModel


VERSION = "4.4"


DOCUMENT_CODES = {
    "factura_electronica": "01",
    "nota_debito_electronica": "02",
    "nota_credito_electronica": "03",
    "tiquete_electronico": "04",
    "mensaje_receptor": "05",
}


class EmisorCR(BaseModel):
    nombre: str
    tipo_identificacion: str
    numero_identificacion: str
    actividad_economica: str | None = None
    correo: str | None = None


class ReceptorCR(BaseModel):
    nombre: str | None = None
    tipo_identificacion: str | None = None
    numero_identificacion: str | None = None
    correo: str | None = None


class LineaCR(BaseModel):
    numero: int
    cabys: str | None = None
    detalle: str
    cantidad: Decimal
    unidad_medida: str = "Unid"
    precio_unitario: Decimal
    descuento: Decimal = Decimal("0")
    impuesto_tarifa: Decimal = Decimal("13")
    impuesto_monto: Decimal
    total_linea: Decimal
