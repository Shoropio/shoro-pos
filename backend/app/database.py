from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

settings = get_settings()


def resolve_database_url(url: str) -> str:
    if not url.startswith("sqlite:///./"):
        return url
    project_root = Path(__file__).resolve().parents[2]
    relative = url.replace("sqlite:///./", "", 1)
    db_path = project_root / relative
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{db_path.as_posix()}"


database_url = resolve_database_url(settings.database_url)
connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
engine = create_engine(database_url, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from app.models import (  # noqa: F401
        category,
        customer,
        fiscal_document,
        inventory,
        payment,
        product,
        sale,
        sale_item,
        settings,
        user,
    )

    Base.metadata.create_all(bind=engine)
