"""Database initialisation — create tables, seed initial data."""
from __future__ import annotations

from sqlalchemy.orm import Session

from myward.core.logging import get_logger
from myward.core.settings import settings
from myward.db.base import Base
from myward.db.session import engine
from myward.models.orm import User, UserRole
from myward.services.security import get_password_hash

logger = get_logger(__name__)


def create_tables() -> None:
    """Create all tables defined in the ORM metadata."""
    # Import all models so they are registered on Base.metadata
    from myward.models import orm  # noqa: F401

    Base.metadata.create_all(bind=engine)
    logger.info("database_tables_created")


def seed_superadmin(db: Session) -> None:
    """Create superadmin user if it does not exist."""
    existing = db.query(User).filter(User.username == settings.SUPERADMIN_USERNAME).first()
    if not existing:
        superadmin = User(
            username=settings.SUPERADMIN_USERNAME,
            email=settings.SUPERADMIN_EMAIL,
            hashed_password=get_password_hash(settings.SUPERADMIN_PASSWORD),
            full_name="Promesse",
            gender="female",
            role=UserRole.superadmin.value,
            is_active=True,
        )
        db.add(superadmin)
        db.commit()
        logger.info("superadmin_created", username=settings.SUPERADMIN_USERNAME)
    else:
        logger.info("superadmin_exists", username=settings.SUPERADMIN_USERNAME)


def init_db(db: Session) -> None:
    """Run all initialisation tasks."""
    create_tables()
    seed_superadmin(db)
