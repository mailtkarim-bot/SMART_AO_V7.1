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
Endpoints Package
"""
from .health import router as health_router
from .missions import router as missions_router
from .agents import router as agents_router
from .documents import router as documents_router
from .workflows import router as workflows_router
from .enveloppes import router as enveloppes_router

__all__ = [
    "health_router",
    "missions_router",
    "agents_router",
    "documents_router",
    "workflows_router",
    "enveloppes_router",
]