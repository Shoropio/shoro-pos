from datetime import datetime

from pydantic import BaseModel


class FiscalDocumentCreate(BaseModel):
    sale_id: int | None = None
    document_type: str = "tiquete_electronico"


class FiscalDocumentRead(BaseModel):
    id: int
    sale_id: int | None
    document_type: str
    clave: str | None
    consecutive: str | None
    environment: str = "sandbox"
    status: str
    error_message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class FiscalConfigRead(BaseModel):
    enabled: bool
    environment: str
    api_base_configured: bool = False
    token_url_configured: bool = False
    p12_configured: bool = False


FiscalDocumentOut = FiscalDocumentRead


class FiscalConfigOut(BaseModel):
    enabled: bool
    environment: str
    version: str = "4.4"
