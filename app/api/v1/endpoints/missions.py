"""
SMART_AO V7 - missions.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.mission import MissionCreate, MissionResponse, MissionListResponse, MissionStatus, MissionType
from app.schemas.response import ErrorResponse
from app.engines.workflow_engine.mission import Mission as WorkflowMission
from app.models.mission import Mission as MissionModel, MissionStatus as MissionStatusModel
from app.core.security import get_current_user
from app.core.database import get_db

router = APIRouter(prefix="/api/v1/missions", tags=["missions"])


@router.get("", response_model=MissionListResponse, summary="List Missions")
async def list_missions(
    status: Optional[MissionStatus] = None,
    page: int = 1,
    per_page: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    '''Lister toutes les missions avec pagination.'''
    
    # Construction de la requête (single-tenant pur : pas de filtre tenant)
    query = select(MissionModel)
    
    # Filtre par status si spécifié
    if status:
        # Mapper MissionStatus (schema) vers MissionStatusModel (SQLAlchemy)
        status_map = {
            MissionStatus.PENDING: MissionStatusModel.PENDING,
            MissionStatus.CREATED: MissionStatusModel.CREATED,
            MissionStatus.RUNNING: MissionStatusModel.PARSING,  # RUNNING = tout statut actif
            MissionStatus.COMPLETED: MissionStatusModel.DONE,
            MissionStatus.FAILED: MissionStatusModel.FAILED,
        }
        db_status = status_map.get(status, status)
        if isinstance(db_status, str):
            query = query.where(MissionModel.status == db_status)
    
    # Compter le total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Calculer le nombre total de pages
    total_pages = max(1, (total + per_page - 1) // per_page)
    
    # Appliquer pagination
    offset = (page - 1) * per_page
    query = query.order_by(desc(MissionModel.created_at)).offset(offset).limit(per_page)
    
    # Exécuter la requête
    result = await db.execute(query)
    missions_models = result.scalars().all()
    
    # Convertir en MissionResponse
    missions = []
    for mission_model in missions_models:
        # Mapper status
        status_map = {
            MissionStatusModel.PENDING: MissionStatus.PENDING,
            MissionStatusModel.CREATED: MissionStatus.PENDING,
            MissionStatusModel.PARSING: MissionStatus.RUNNING,
            MissionStatusModel.EXTRACTING: MissionStatus.RUNNING,
            MissionStatusModel.CLASSIFYING: MissionStatus.RUNNING,
            MissionStatusModel.AGENT_RUNNING: MissionStatus.RUNNING,
            MissionStatusModel.COMPILING: MissionStatus.RUNNING,
            MissionStatusModel.REPORTING: MissionStatus.RUNNING,
            MissionStatusModel.DONE: MissionStatus.COMPLETED,
            MissionStatusModel.FAILED: MissionStatus.FAILED,
        }
        
        priority_map = {1: "BASSE", 2: "NORMALE", 3: "HAUTE", 4: "URGENTE", 5: "URGENTE"}
        priority_value = 2  # NORMALE par défaut
        if mission_model.extra_metadata and "priority" in mission_model.extra_metadata:
            priority_str = mission_model.extra_metadata["priority"]
            priority_value = {v: k for k, v in priority_map.items()}.get(priority_str, 2)
        
        mission_type = MissionType.ANALYSIS
        if mission_model.extra_metadata and "mission_type" in mission_model.extra_metadata:
            mission_type = mission_model.extra_metadata["mission_type"]
        
        missions.append(MissionResponse(
            id=mission_model.mission_id,
            name=mission_model.name,
            mission_type=mission_type,
            description=mission_model.description,
            status=status_map.get(mission_model.status, MissionStatus.PENDING),
            priority=priority_value,
            parameters=mission_model.extra_metadata.get("parameters") if mission_model.extra_metadata else None,
            agent_name=mission_model.extra_metadata.get("agent_name") if mission_model.extra_metadata else None,
            created_at=mission_model.created_at,
            updated_at=mission_model.updated_at,
            completed_at=mission_model.completed_at,
            result=mission_model.extra_metadata.get("result") if mission_model.extra_metadata else None,
            error=mission_model.error_message,
        ))
    
    return MissionListResponse(
        missions=missions,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.post("", response_model=MissionResponse, status_code=status.HTTP_201_CREATED, summary="Create Mission")
async def create_mission(
    mission_data: MissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    '''Créer une nouvelle mission avec persistance PostgreSQL.'''
    user_id = current_user.get("user_id", "unknown")
    
    # Convertir priority int vers string
    priority_map = {1: "BASSE", 2: "NORMALE", 3: "HAUTE", 4: "URGENTE", 5: "URGENTE"}
    priority_str = priority_map.get(mission_data.priority, "NORMALE")
    
    # Générer mission_id unique
    mission_id = f"mission_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    
    # Créer le modèle Mission pour la base de données
    mission_model = MissionModel(
        mission_id=mission_id,
        name=mission_data.name,
        description=mission_data.description,
        status=MissionStatusModel.CREATED,
        total_steps=0,
        completed_steps=0,
        project_id=mission_data.parameters.get("project_id") if mission_data.parameters else None,
        extra_metadata={
            "priority": priority_str,
            "mission_type": mission_data.mission_type.value if mission_data.mission_type else "ANALYSIS",
            "parameters": mission_data.parameters,
            "agent_name": mission_data.agent_name,
            "created_by": user_id,
        }
    )
    
    # Sauvegarder en base de données
    db.add(mission_model)
    await db.commit()
    await db.refresh(mission_model)
    
    # Créer MissionResponse
    priority_reverse_map = {"BASSE": 1, "NORMALE": 2, "HAUTE": 3, "URGENTE": 4}
    
    return MissionResponse(
        id=mission_model.mission_id,
        name=mission_model.name,
        mission_type=mission_data.mission_type or MissionType.ANALYSIS,
        description=mission_model.description,
        status=MissionStatus.PENDING,
        priority=priority_reverse_map.get(priority_str, 2),
        parameters=mission_data.parameters,
        agent_name=mission_data.agent_name,
        created_at=mission_model.created_at,
        updated_at=mission_model.updated_at,
        completed_at=None,
        result=None,
        error=None,
    )


@router.get("/{mission_id}", response_model=MissionResponse, summary="Get Mission")
async def get_mission(
    mission_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    '''Récupérer une mission spécifique.'''
    
    # Récupérer depuis PostgreSQL (single-tenant pur : pas de filtre tenant)
    result = await db.execute(
        select(MissionModel).where(
            MissionModel.mission_id == mission_id
        )
    )
    mission_model = result.scalar_one_or_none()
    
    if not mission_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mission {mission_id} non trouvée ou accès refusé"
        )
    
    # Mapper status
    status_map = {
        MissionStatusModel.PENDING: MissionStatus.PENDING,
        MissionStatusModel.CREATED: MissionStatus.PENDING,
        MissionStatusModel.PARSING: MissionStatus.RUNNING,
        MissionStatusModel.EXTRACTING: MissionStatus.RUNNING,
        MissionStatusModel.CLASSIFYING: MissionStatus.RUNNING,
        MissionStatusModel.AGENT_RUNNING: MissionStatus.RUNNING,
        MissionStatusModel.COMPILING: MissionStatus.RUNNING,
        MissionStatusModel.REPORTING: MissionStatus.RUNNING,
        MissionStatusModel.DONE: MissionStatus.COMPLETED,
        MissionStatusModel.FAILED: MissionStatus.FAILED,
    }
    
    # Mapper priority
    priority_map = {"BASSE": 1, "NORMALE": 2, "HAUTE": 3, "URGENTE": 4}
    priority_value = 2  # NORMALE par défaut
    if mission_model.extra_metadata and "priority" in mission_model.extra_metadata:
        priority_str = mission_model.extra_metadata["priority"]
        priority_value = priority_map.get(priority_str, 2)
    
    # Mapper mission_type
    mission_type = MissionType.ANALYSIS
    if mission_model.extra_metadata and "mission_type" in mission_model.extra_metadata:
        mission_type = mission_model.extra_metadata["mission_type"]
    
    return MissionResponse(
        id=mission_model.mission_id,
        name=mission_model.name,
        mission_type=mission_type,
        description=mission_model.description,
        status=status_map.get(mission_model.status, MissionStatus.PENDING),
        priority=priority_value,
        parameters=mission_model.extra_metadata.get("parameters") if mission_model.extra_metadata else None,
        agent_name=mission_model.extra_metadata.get("agent_name") if mission_model.extra_metadata else None,
        created_at=mission_model.created_at,
        updated_at=mission_model.updated_at,
        completed_at=mission_model.completed_at,
        result=mission_model.extra_metadata.get("result") if mission_model.extra_metadata else None,
        error=mission_model.error_message,
    )
