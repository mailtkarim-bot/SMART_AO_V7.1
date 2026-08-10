"""Pricing Endpoint - Gestion des prix unitaires et bordereaux"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.auth import require_financial_access

router = APIRouter(prefix="/pricing", tags=["Pricing"])

@router.get("/bpu")
async def get_bpu(db: AsyncSession = Depends(get_db)):
    """Récupérer le Bordereau de Prix Unitaires"""
    return {"bpu": [], "total": 0}

@router.post("/optimize")
async def optimize_pricing(data: dict):
    """Optimiser les prix via le Math Engine"""
    from app.engines.math_engine.chiffrage_pulp import optimiser_marge
    result = optimiser_marge(data)
    return result
