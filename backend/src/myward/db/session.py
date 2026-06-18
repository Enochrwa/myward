"""
Database engine, session factory, and dependency injection.
PostgreSQL backend via psycopg2 (sync) + SQLAlchemy 2.x.
"""
from __future__ import annotations

from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker

from myward.core.logging import get_logger
from myward.core.settings import settings

logger = get_logger(__name__)


def _build_engine() -> Any:
    url = settings.get_db_url()
    engine = create_engine(
        url,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        pool_timeout=settings.DATABASE_POOL_TIMEOUT,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=settings.is_development(),
        future=True,
    )

    @event.listens_for(engine, "connect")
    def set_search_path(dbapi_connection: Any, connection_record: Any) -> None:  # noqa: ARG001
        cursor = dbapi_connection.cursor()
        cursor.execute("SET search_path TO public")
        cursor.close()

    return engine


engine = _build_engine()

SessionLocal: sessionmaker[Session] = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# ── Dependency ────────────────────────────────────────────────────────────────


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency — yields a database session."""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ── Health check ─────────────────────────────────────────────────────────────


def ping_database() -> bool:
    """Return True if the database is reachable."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.error("database_ping_failed", error=str(exc))
        return False
