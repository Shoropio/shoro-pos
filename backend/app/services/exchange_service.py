from datetime import date, datetime
from decimal import Decimal
from xml.etree import ElementTree

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exchange_rate import ExchangeRate
from app.models.settings import BusinessSettings

BCCR_ENDPOINT = "https://gee.bccr.fi.cr/Indicadores/Suscripciones/WS/wsindicadoreseconomicos.asmx/ObtenerIndicadoresEconomicosXML"
USD_SELL_INDICATOR = "318"
USD_BUY_INDICATOR = "317"


def get_settings_row(db: Session) -> BusinessSettings:
    settings = db.scalar(select(BusinessSettings).limit(1))
    if settings is None:
        settings = BusinessSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


def latest_exchange_rate(db: Session) -> ExchangeRate | None:
    return db.scalar(select(ExchangeRate).order_by(ExchangeRate.fetched_at.desc()).limit(1))


def _parse_bccr_value(xml_text: str) -> Decimal:
    root = ElementTree.fromstring(xml_text)
    value = root.find(".//NUM_VALOR")
    if value is None or not value.text:
        raise ValueError("BCCR no devolvio NUM_VALOR")
    return Decimal(value.text.strip())


def fetch_bccr_indicator(indicator: str, email: str, token: str, target_date: date) -> Decimal:
    formatted = target_date.strftime("%d/%m/%Y")
    data = {
        "Indicador": indicator,
        "FechaInicio": formatted,
        "FechaFinal": formatted,
        "Nombre": "Shoro POS",
        "SubNiveles": "N",
        "CorreoElectronico": email,
        "Token": token,
    }
    response = httpx.post(BCCR_ENDPOINT, data=data, timeout=20)
    response.raise_for_status()
    return _parse_bccr_value(response.text)


def get_usd_crc_rate(db: Session, refresh: bool = False) -> dict:
    settings = get_settings_row(db)
    latest = latest_exchange_rate(db)
    if latest and not refresh and latest.fetched_at.date() == date.today():
        return {
            "buy_rate": float(latest.buy_rate),
            "sell_rate": float(latest.sell_rate),
            "source": latest.source,
            "fetched_at": latest.fetched_at.isoformat(),
        }

    source = "fallback"
    buy_rate = sell_rate = Decimal(settings.fallback_usd_crc_rate or 520)
    if settings.bccr_email and settings.bccr_token:
        try:
            buy_rate = fetch_bccr_indicator(USD_BUY_INDICATOR, settings.bccr_email, settings.bccr_token, date.today())
            sell_rate = fetch_bccr_indicator(USD_SELL_INDICATOR, settings.bccr_email, settings.bccr_token, date.today())
            source = "bccr"
        except Exception:
            source = "fallback"

    row = ExchangeRate(buy_rate=buy_rate, sell_rate=sell_rate, source=source, fetched_at=datetime.utcnow())
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"buy_rate": float(row.buy_rate), "sell_rate": float(row.sell_rate), "source": row.source, "fetched_at": row.fetched_at.isoformat()}
