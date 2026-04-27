from pathlib import Path


def sign_xml_xades_epes(xml: str, p12_path: str | None, pin: str | None) -> str:
    if not p12_path or not pin:
        raise ValueError("Configure HCIENDA_P12_PATH y HACIENDA_PIN para firmar XML")
    if not Path(p12_path).exists():
        raise FileNotFoundError("No se encontró la llave criptográfica .p12")
    # Punto de extensión: integrar firma XAdES-EPES con RSA 2048 + SHA-256.
    # En producción se recomienda validar contra los XSD oficiales antes del envío.
    return xml.replace("</", "<!-- signed-placeholder:XAdES-EPES -->\n</", 1)
