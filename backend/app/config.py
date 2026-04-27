from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE_URL = f"sqlite:///{(PROJECT_ROOT / 'database' / 'shoro_pos.db').as_posix()}"


class Settings(BaseSettings):
    app_name: str = "Shoro POS"
    environment: str = "local"
    database_url: str = DEFAULT_DATABASE_URL
    secret_key: str = "dev-secret-change-me"
    log_level: str = "INFO"
    auto_create_tables: bool = True
    access_token_expire_minutes: int = 480
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    fiscal_cr_enabled: bool = False
    fiscal_cr_env: str = "sandbox"
    hacienda_client_id: str | None = None
    hacienda_username: str | None = None
    hacienda_password: str | None = None
    hacienda_api_base: str | None = None
    hacienda_token_url: str | None = None
    p12_path: str | None = None
    p12_pin: str | None = None

    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from: str | None = None
    bccr_email: str | None = None
    bccr_token: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
