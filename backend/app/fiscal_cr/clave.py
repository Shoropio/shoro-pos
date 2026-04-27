from datetime import datetime


def build_clave(
    consecutive: str,
    issuer_identification: str,
    security_code: str,
    country_code: str = "506",
    date: datetime | None = None,
    situation: str = "1",
) -> str:
    issued_at = date or datetime.utcnow()
    day = issued_at.strftime("%d")
    month = issued_at.strftime("%m")
    year = issued_at.strftime("%y")
    issuer = "".join(ch for ch in issuer_identification if ch.isdigit()).zfill(12)[-12:]
    security = "".join(ch for ch in security_code if ch.isdigit()).zfill(8)[-8:]
    return f"{country_code}{day}{month}{year}{issuer}{consecutive}{situation}{security}"
