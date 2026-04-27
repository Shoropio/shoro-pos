from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.settings import BusinessSettings
from app.schemas.settings_schema import BusinessSettingsIn, BusinessSettingsOut
from app.security import get_current_user


router = APIRouter(prefix="/settings", tags=["settings"], dependencies=[Depends(get_current_user)])


def get_or_create(db: Session) -> BusinessSettings:
    settings = db.scalar(select(BusinessSettings).limit(1))
    if settings is None:
        settings = BusinessSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.get("", response_model=BusinessSettingsOut)
def show(db: Session = Depends(get_db)):
    return get_or_create(db)


@router.put("", response_model=BusinessSettingsOut)
def update(data: BusinessSettingsIn, db: Session = Depends(get_db)):
    settings = get_or_create(db)
    for key, value in data.model_dump().items():
        setattr(settings, key, value)
    db.commit()
    db.refresh(settings)
    return settings
