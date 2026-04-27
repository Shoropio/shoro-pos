from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.category import Category
from app.schemas.product_schema import CategoryRead, CategoryCreate
from app.security import get_current_user

router = APIRouter(prefix="/categories", tags=["categories"], dependencies=[Depends(get_current_user)])

@router.get("", response_model=List[CategoryRead])
def index(db: Session = Depends(get_db)):
    return list(db.scalars(select(Category).where(Category.is_active.is_(True))))

@router.post("", response_model=CategoryRead)
def create(data: CategoryCreate, db: Session = Depends(get_db)):
    category = Category(name=data.name, description=data.description)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

@router.get("/{id}", response_model=CategoryRead)
def show(id: int, db: Session = Depends(get_db)):
    category = db.get(Category, id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return category
