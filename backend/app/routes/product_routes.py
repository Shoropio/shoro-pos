from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, File, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.schemas.product_schema import ProductCreate, ProductOut, ProductUpdate
from app.security import get_current_user
from app.services.product_service import create_product, list_products, update_product
from app.services.barcode_service import barcode_service
from app.services.auth_service import require_permission
from app.services.import_service import import_products_excel


router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductOut])
def index(q: str | None = None, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> list[Product]:
    return list_products(db, q)


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create(data: ProductCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> Product:
    return create_product(db, data)


@router.post("/import")
async def import_excel(file: UploadFile = File(...), db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    require_permission(current_user, "products.import")
    if not file.filename.lower().endswith((".xlsx", ".xlsm")):
        raise HTTPException(status_code=400, detail="Suba un archivo Excel .xlsx")
    content = await file.read()
    try:
        return import_products_excel(db, content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{product_id}", response_model=ProductOut)
def show(product_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


@router.put("/{product_id}", response_model=ProductOut)
def update(product_id: int, data: ProductUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return update_product(db, product, data)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(product_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> Response:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    product.is_active = False
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{product_id}/barcode")
def generate_barcode(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    code = product.barcode or product.internal_code
    if not code:
        raise HTTPException(status_code=400, detail="El producto no tiene código de barras ni código interno")
        
    img_buffer = barcode_service.generate_code128(code)
    return StreamingResponse(img_buffer, media_type="image/png")
