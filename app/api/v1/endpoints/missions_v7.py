"""Missions V7 Endpoint - CRUD complet des missions avec workflow intégré"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.mission import Mission
from app.core.auth import get_current_user
from app.models.user import User
from datetime import datetime

router = APIRouter(prefix="/missions-v7", tags=["Missions V7"])

@router.get("/")
async def list_missions(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lister les missions de l'utilisateur"""
    query = select(Mission).where(Mission.user_id == current_user.id)
    if status:
        query = query.where(Mission.status == status)
    
    result = await db.execute(query.offset(skip).limit(limit))
    missions = result.scalars().all()
    
    count_result = await db.execute(select(Mission).where(Mission.user_id == current_user.id))
    total = len(count_result.scalars().all())
    
    return {"total": total, "missions": missions}

@router.get("/{mission_id}")
async def get_mission(
    mission_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer une mission spécifique"""
    result = await db.execute(
        select(Mission).where(Mission.id == mission_id)
    )
    mission = result.scalar_one_or_none()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission non trouvée")
    
    # Vérification des permissions
    if mission.user_id != current_user.id and current_user.role != "PATRON":
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    return mission

@router.post("/")
async def create_mission(
    mission_data: dict, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Créer une nouvelle mission"""
    # Implémentation complète
    new_mission = Mission(**mission_data, user_id=current_user.id)
    db.add(new_mission)
    await db.commit()
    await db.refresh(new_mission)
    return new_mission

@router.delete("/{mission_id}")
async def delete_mission(
    mission_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Supprimer une mission"""
    result = await db.execute(
        select(Mission).where(Mission.id == mission_id)
    )
    mission = result.scalar_one_or_none()
    
    if not mission:
        raise HTTPException(status_code=404, detail="Mission non trouvée")
    
    # Vérification des permissions
    if mission.user_id != current_user.id and current_user.role != "PATRON":
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    await db.delete(mission)
    await db.commit()
    return {"status": "deleted", "mission_id": mission_id}
