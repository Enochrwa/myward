"""
MyWard FastAPI application factory.
"""
from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from myward.api.v1.router import api_router
from myward.core.logging import get_logger, setup_logging
from myward.core.settings import settings
from myward.db.init_db import init_db
from myward.db.session import SessionLocal, ping_database

logger = get_logger(__name__)


def configure_sentry() -> None:
    if settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.ENVIRONMENT,
            integrations=[FastApiIntegration(), SqlalchemyIntegration()],
            traces_sample_rate=0.1,
        )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:  # noqa: ARG001
    setup_logging(debug=settings.is_development())
    configure_sentry()

    logger.info("startup_begin", env=settings.ENVIRONMENT, version=settings.APP_VERSION)

    if not ping_database():
        logger.error("startup_database_unreachable")
        raise RuntimeError("Cannot connect to PostgreSQL — aborting startup")

    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()

    logger.info("startup_complete")
    yield
    logger.info("shutdown_complete")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="AI-powered digital wardrobe & outfit recommendation system",
        docs_url="/docs" if settings.is_development() else None,
        redoc_url="/redoc" if settings.is_development() else None,
        lifespan=lifespan,
    )

    # ── CORS ─────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Static files ─────────────────────────────────────────────────────────
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.STATIC_DIR, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
    app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(api_router, prefix="/api/v1")

    # ── Health ────────────────────────────────────────────────────────────────
    @app.get("/health", tags=["system"])
    async def health() -> dict[str, object]:
        db_ok = ping_database()
        return {
            "status": "healthy" if db_ok else "degraded",
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "database": "ok" if db_ok else "unreachable",
        }

    @app.get("/", tags=["system"])
    async def root() -> dict[str, str]:
        return {"message": f"{settings.APP_NAME} v{settings.APP_VERSION}"}

    return app


app = create_app()
