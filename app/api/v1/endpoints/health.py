"""
SMART_AO V7 - health.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


from fastapi import APIRouter, Depends
from app.core.config import settings

router = APIRouter(prefix="/api/v1/health", tags=["health"])


@router.get("", summary="Health Check")
async def health_check():
    return {
        "status": "healthy",
        "version": "V7",
        "build": "7-8",
        "phase": "4",
    }
