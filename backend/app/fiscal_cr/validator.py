def validate_fiscal_ready(document_type: str, issuer_identification: str | None) -> list[str]:
    errors: list[str] = []
    if document_type not in {"factura_electronica", "tiquete_electronico", "nota_credito_electronica", "nota_debito_electronica", "mensaje_receptor"}:
        errors.append("Tipo de documento fiscal no soportado")
    if not issuer_identification:
        errors.append("Configure la identificación del emisor")
    return errors
