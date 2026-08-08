"""
SMART_AO V7 - __init__.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Core Package
=========================
Core utilities and configuration
Source: ARCHITECTURE_V7_ENGINE.md §3
"""

from app.core.database import engine, async_session_maker, Base, get_db, test_db_connection

__all__ = [
    "engine",
    "async_session_maker",
    "Base",
    "get_db",
    "test_db_connection",
]
