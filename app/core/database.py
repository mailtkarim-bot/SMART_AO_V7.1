"""
SMART_AO V7 - database.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Database Configuration
===================================
PostgreSQL persistence layer for Mission, Events, and Vault
Source: ARCHITECTURE_V7_ENGINE.md §4
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from app.core.config import settings

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

# Utiliser les paramètres depuis la configuration centrale (SSoT)
# Si DATABASE_URL est fourni, l'utiliser directement
if settings.DATABASE_URL:
    DATABASE_URL = settings.DATABASE_URL
else:
    # Sinon, construire à partir des composants
    if not all([settings.DB_HOST, settings.DB_PORT, settings.DB_NAME, settings.DB_USER, settings.DB_PASSWORD]):
        missing_vars = []
        if not settings.DB_HOST:
            missing_vars.append("DB_HOST")
        if not settings.DB_PORT:
            missing_vars.append("DB_PORT")
        if not settings.DB_NAME:
            missing_vars.append("DB_NAME")
        if not settings.DB_USER:
            missing_vars.append("DB_USER")
        if not settings.DB_PASSWORD:
            missing_vars.append("DB_PASSWORD")
        raise ValueError(f"Variables d'environnement manquantes pour la base de données: {', '.join(missing_vars)}")
    
    DATABASE_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

# Pool configuration depuis settings
DB_POOL_SIZE = settings.DATABASE_POOL_SIZE
DB_POOL_MAX_OVERFLOW = settings.DATABASE_MAX_OVERFLOW
DB_ECHO = settings.DB_ECHO

# En environnement de test, désactiver le pooling pour éviter les conflits
# d'event loop entre TestClient (sync) et asyncpg.
IS_TEST_ENV = settings.APP_ENVIRONMENT.lower() == "test"

# Arguments communs
engine_kwargs = {
    "echo": DB_ECHO,
    "pool_recycle": 3600,
}

if IS_TEST_ENV:
    # Désactiver le pooling pour éviter les conflits d'event loop en test
    engine_kwargs["poolclass"] = NullPool
else:
    engine_kwargs.update({
        "pool_size": DB_POOL_SIZE,
        "max_overflow": DB_POOL_MAX_OVERFLOW,
        "pool_pre_ping": True,
    })

# Async engine
engine = create_async_engine(DATABASE_URL, **engine_kwargs)

# Session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Declarative base
Base = declarative_base()


# =============================================================================
# SESSION MANAGEMENT
# =============================================================================

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session
    Usage with FastAPI: Depends(get_db)
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


# =============================================================================
# CONNECTION TEST
# =============================================================================

async def test_db_connection() -> bool:
    """Test database connection"""
    from sqlalchemy import text
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


# =============================================================================
# INITIALIZATION
# =============================================================================

def init_db():
    """Initialize database tables (for testing/dev)"""
    import asyncio
    
    async def _init():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    asyncio.run(_init())
