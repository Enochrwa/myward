"""
Application settings using Pydantic Settings v2.
All config is read from environment variables or .env file.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any

from pydantic import Field, PostgresDsn, RedisDsn, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ──────────────────────────────────────────────────────────────────
    APP_NAME: str = "MyWard API"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = Field(default="production", pattern="^(development|staging|production)$")

    # ── Security ─────────────────────────────────────────────────────────────
    SECRET_KEY: str = Field(..., min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 h

    # ── PostgreSQL ────────────────────────────────────────────────────────────
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "myward"
    POSTGRES_PASSWORD: str = "myward"
    POSTGRES_DB: str = "myward"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_TIMEOUT: int = 30

    # Computed — override with DATABASE_URL env var if desired
    DATABASE_URL: PostgresDsn | None = None

    @model_validator(mode="after")
    def assemble_db_url(self) -> "Settings":
        if self.DATABASE_URL is None:
            self.DATABASE_URL = PostgresDsn(  # type: ignore[assignment]
                f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        return self

    # ── Redis / Celery ────────────────────────────────────────────────────────
    REDIS_URL: RedisDsn = RedisDsn("redis://localhost:6379/0")
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # ── Storage ───────────────────────────────────────────────────────────────
    UPLOAD_DIR: str = "uploads"
    STATIC_DIR: str = "static"
    MAX_FILE_SIZE_MB: int = 10
    MAX_FILES_PER_REQUEST: int = 20
    ALLOWED_IMAGE_TYPES: list[str] = ["image/jpeg", "image/png", "image/webp"]

    # ── CORS ─────────────────────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
    ]

    # ── Weather API ───────────────────────────────────────────────────────────
    WEATHER_API_KEY: str = ""
    WEATHER_API_URL: str = "https://api.openweathermap.org/data/2.5"

    # ── Sentry ───────────────────────────────────────────────────────────────
    SENTRY_DSN: str = ""

    # ── Superadmin seed ───────────────────────────────────────────────────────
    SUPERADMIN_USERNAME: str = "promesse"
    SUPERADMIN_EMAIL: str = "promesse@gmail.com"
    SUPERADMIN_PASSWORD: str = "promesse"

    @field_validator("MAX_FILE_SIZE_MB")
    @classmethod
    def validate_file_size(cls, v: int) -> int:
        if v < 1 or v > 100:
            raise ValueError("MAX_FILE_SIZE_MB must be between 1 and 100")
        return v

    @property
    def max_file_size_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    def get_db_url(self) -> str:
        return str(self.DATABASE_URL)

    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    def model_post_init(self, __context: Any) -> None:
        import os

        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
        os.makedirs(self.STATIC_DIR, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
