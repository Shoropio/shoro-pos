from sqlalchemy import select
from sqlalchemy.orm import Session

from app.fiscal_cr.schemas_cr import DOCUMENT_CODES
from app.models.fiscal_document import FiscalConsecutive


def next_consecutive(
    db: Session,
    document_type: str,
    branch_code: str = "001",
    terminal_code: str = "00001",
    environment: str = "sandbox",
) -> str:
    record = db.scalar(
        select(FiscalConsecutive).where(
            FiscalConsecutive.document_type == document_type,
            FiscalConsecutive.branch_code == branch_code,
            FiscalConsecutive.terminal_code == terminal_code,
            FiscalConsecutive.environment == environment,
        )
    )
    if record is None:
        record = FiscalConsecutive(
            document_type=document_type,
            branch_code=branch_code,
            terminal_code=terminal_code,
            environment=environment,
            current_number=0,
        )
        db.add(record)
        db.flush()
    record.current_number += 1
    code = DOCUMENT_CODES.get(document_type, "04")
    return f"{branch_code}{terminal_code}{code}{record.current_number:010d}"
