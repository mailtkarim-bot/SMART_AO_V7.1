"""
SMART_AO V7 - env.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Alembic Environment Configuration
================================================
PostgreSQL migrations configuration
Source: ARCHITECTURE_V7_ENGINE.md §4
"""

from logging.config import fileConfig
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Alembic Config
from alembic import context

# Database models
from app.core.database import Base, DATABASE_URL

# Import models to ensure they're registered with Base.metadata
from app.models.mission import Mission, MissionStep  # noqa: F401
from app.models.events import Event, MissionEvent  # noqa: F401
from app.models.project import Project  # noqa: F401
from app.models.vault_core import VaultDocument, DocumentChunk  # noqa: F401

# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata - Base.metadata already includes all models
# that inherit from Base (Mission, MissionStep, Event, MissionEvent)
target_metadata = Base.metadata


# =============================================================================
# DATABASE URL CONFIGURATION
# =============================================================================

def get_sync_database_url():
    """Get synchronous database URL (for Alembic which doesn't support async)"""
    # Convert asyncpg URL to psycopg2 URL
    return DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")


# =============================================================================
# RUN MIGRATIONS
# =============================================================================

def run_migrations():
    """Run migrations - called by Alembic automatically"""
    if context.is_offline_mode():
        # Offline mode - use synchronous URL
        url = get_sync_database_url()
        context.configure(
            url=url,
            target_metadata=target_metadata,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
        )
    else:
        # Online mode - use synchronous engine for Alembic compatibility
        from sqlalchemy import create_engine
        sync_url = get_sync_database_url()
        connectable = create_engine(sync_url, pool_pre_ping=True)
        
        # Connect to the database
        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,
                compare_server_default=True,
            )
            
            with context.begin_transaction():
                context.run_migrations()
    
    # For offline mode, run migrations directly
    if context.is_offline_mode():
        with context.begin_transaction():
            context.run_migrations()


# =============================================================================
# ENTRY POINT - Alembic calls run_migrations() automatically
# =============================================================================

run_migrations()
