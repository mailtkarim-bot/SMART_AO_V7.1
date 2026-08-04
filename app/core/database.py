"""
SMART_AO V7 - Database Configuration
===================================
PostgreSQL persistence layer for Mission, Events, and Vault
Source: ARCHITECTURE_V7_ENGINE.md §4
"""

import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "smart_ao_v7")
DB_USER = os.getenv("DB_USER", "smart_ao")
DB_PASSWORD = os.getenv("DB_PASSWORD", "your_secure_password")
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "20"))
DB_POOL_MAX_OVERFLOW = int(os.getenv("DB_POOL_MAX_OVERFLOW", "10"))
DB_ECHO = os.getenv("DB_ECHO", "False").lower() == "true"

# =============================================================================
# SQLALCHEMY SETUP
# =============================================================================

# Database URL
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Async engine
engine = create_async_engine(
    DATABASE_URL,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_POOL_MAX_OVERFLOW,
    echo=DB_ECHO,
    pool_pre_ping=True,
    pool_recycle=3600,
)

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
    try:
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
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
