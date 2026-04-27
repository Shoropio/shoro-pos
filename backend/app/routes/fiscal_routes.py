import json
from random import randint

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.config import get_settings
from app.database import get_db
from app.fiscal_cr.clave import build_clave
from app.fiscal_cr.consecutivo import next_consecutive
from app.fiscal_cr.hacienda_client import HaciendaClient
from app.fiscal_cr.signer import sign_xml_xades_epes
from app.fiscal_cr.xml_builder import build_comprobante_xml
from app.models.fiscal_document import FiscalDocument, FiscalLog
from app.models.sale import Sale
from app.models.settings import BusinessSettings
from app.schemas.fiscal_schema import FiscalConfigOut, FiscalDocumentCreate, FiscalDocumentOut
from app.security import get_current_user


router = APIRouter(prefix="/fiscal", tags=["fiscal"], dependencies=[Depends(get_current_user)])


@router.get("/config", response_model=FiscalConfigOut)
def config() -> FiscalConfigOut:
    settings = get_settings()
    return FiscalConfigOut(enabled=settings.fiscal_cr_enabled, environment=settings.fiscal_cr_env)


@router.get("/documents", response_model=list[FiscalDocumentOut])
def documents(db: Session = Depends(get_db)):
    return list(db.scalars(select(FiscalDocument).order_by(FiscalDocument.created_at.desc()).limit(200)))


@router.post("/documents", response_model=FiscalDocumentOut)
def create_document(data: FiscalDocumentCreate, db: Session = Depends(get_db)):
    sale = None
    if data.sale_id:
        sale = db.scalar(
            select(Sale)
            .where(Sale.id == data.sale_id)
            .options(selectinload(Sale.items), selectinload(Sale.payments), selectinload(Sale.customer))
        )
        if sale is None:
            raise HTTPException(status_code=404, detail="Venta no encontrada")
    business = db.scalar(select(BusinessSettings).limit(1)) or BusinessSettings()
    env = get_settings().fiscal_cr_env
    consecutive = next_consecutive(db, data.document_type, environment=env)
    clave = build_clave(consecutive, business.identification_number or "0", str(randint(1, 99999999)))
    xml = build_comprobante_xml(
        sale,
        clave=clave,
        consecutivo=consecutive,
        emisor={
            "nombre": business.business_name,
            "tipo": "02" if business.identification_type == "juridica" else "01",
            "numero": business.identification_number or "0000000000",
            "actividad_economica": business.economic_activity or "000000",
            "correo": business.email,
        },
        receptor=None,
        document_type=data.document_type,
    ) if sale else ""
    document = FiscalDocument(
        sale_id=data.sale_id,
        document_type=data.document_type,
        consecutive=consecutive,
        clave=clave,
        environment=env,
        status="pendiente",
        xml_generated=xml,
    )
    db.add(document)
    if sale:
        sale.fiscal_status = "pendiente"
    db.commit()
    db.refresh(document)
    return document


@router.post("/send/{document_id}", response_model=FiscalDocumentOut)
def send_document(document_id: int, db: Session = Depends(get_db)):
    settings = get_settings()
    document = db.get(FiscalDocument, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Documento fiscal no encontrado")
    try:
        signed = sign_xml_xades_epes(document.xml_generated or "", settings.hacienda_p12_path, settings.hacienda_pin)
        document.xml_signed = signed
        client = HaciendaClient(settings.fiscal_cr_env, settings.hacienda_client_id, settings.hacienda_username, settings.hacienda_password)
        response = client.send({"clave": document.clave, "comprobanteXml": signed})
        document.hacienda_response = json.dumps(response)
        document.status = "aceptado" if response["status_code"] in {200, 202} else "pendiente"
    except Exception as exc:
        document.status = "error"
        document.error_message = str(exc)
        db.add(FiscalLog(fiscal_document_id=document.id, level="error", event="send_failed", detail=str(exc)))
    db.commit()
    db.refresh(document)
    return document


@router.get("/status/{clave}")
def fiscal_status(clave: str):
    settings = get_settings()
    client = HaciendaClient(settings.fiscal_cr_env, settings.hacienda_client_id, settings.hacienda_username, settings.hacienda_password)
    return client.status(clave)
