from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.models import *  # noqa: F401,F403
from app.routes import auth_routes, customer_routes, fiscal_routes, inventory_routes, product_routes, report_routes, sale_routes, settings_routes
from app.services.auth_service import ensure_default_admin

settings = get_settings()
Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    ensure_default_admin(db)

app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(product_routes.router)
app.include_router(customer_routes.router)
app.include_router(sale_routes.router)
app.include_router(inventory_routes.router)
app.include_router(report_routes.router)
app.include_router(fiscal_routes.router)
app.include_router(settings_routes.router)


@app.get("/")
def root():
    return {"name": settings.app_name, "status": "ok", "country": "Costa Rica"}
