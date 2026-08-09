"""
SMART_AO V7 - app.db.session
============================
Session de base de données SYNCHRONE pour les modules legacy et endpoints
qui n'ont pas encore été migrés vers async SQLAlchemy.

Source unique de vérité : app.core.config.settings
"""
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings


# Construction de l'URL synchrone à partir des mêmes paramètres que database.py
if settings.DATABASE_URL:
    # Remplacer le driver asyncpg par le driver psycopg2 standard
    SYNC_DATABASE_URL = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
else:
    SYNC_DATABASE_URL = (
        f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )

engine = create_engine(SYNC_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dépendance FastAPI synchrone pour obtenir une session DB."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
