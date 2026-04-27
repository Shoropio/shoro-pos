from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import time

from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.logging_config import configure_logging
from app.models import *  # noqa: F401,F403
from app.routes import auth_routes, cash_shift_routes, category_routes, customer_routes, exchange_routes, fiscal_routes, health_routes, inventory_routes, product_routes, promotion_routes, report_routes, sale_routes, settings_routes, sync_routes, user_routes
from app.services.auth_service import ensure_default_admin
from app.services.schema_service import ensure_sqlite_columns

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger("shoro_pos")
if settings.auto_create_tables:
    Base.metadata.create_all(bind=engine)
    ensure_sqlite_columns()
with SessionLocal() as db:
    ensure_default_admin(db)

app = FastAPI(title=settings.app_name, version="0.1.0")


class RequestLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        started = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        logger.info("%s %s -> %s %.2fms", request.method, request.url.path, response.status_code, elapsed_ms)
        return response


app.add_middleware(RequestLogMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(health_routes.router)
app.include_router(product_routes.router)
app.include_router(category_routes.router)
app.include_router(customer_routes.router)
app.include_router(exchange_routes.router)
app.include_router(sale_routes.router)
app.include_router(inventory_routes.router)
app.include_router(cash_shift_routes.router)
app.include_router(report_routes.router)
app.include_router(promotion_routes.router)
app.include_router(fiscal_routes.router)
app.include_router(settings_routes.router)
app.include_router(sync_routes.router)
app.include_router(user_routes.router)


@app.get("/")
def root():
    return {"name": settings.app_name, "status": "ok", "country": "Costa Rica"}
