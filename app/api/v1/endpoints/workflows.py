"""
SMART_AO V7 - workflows.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from datetime import datetime

from app.schemas.workflow import WorkflowStatusResponse, WorkflowExecutionResponse
from app.engines.workflow_engine.workflow import WorkflowEngine
from app.engines.agent_runtime.registry import registry
from app.engines.event_bus.bus import event_bus
from app.core.auth import get_current_user, TokenData

router = APIRouter(prefix="/api/v1/workflows", tags=["workflows"])


@router.get("/{mission_id}/status", response_model=WorkflowStatusResponse, summary="Workflow Status")
async def get_workflow_status(
    mission_id: str,
    current_user: TokenData = Depends(get_current_user),
):
    '''Récupérer le statut du workflow pour une mission.'''
    # Récupérer directement depuis la persistance
    from app.engines.workflow_engine.persistence import get_mission_by_id
    
    mission_record = await get_mission_by_id(mission_id)
    
    if mission_record is None:
        return WorkflowStatusResponse(
            mission_id=mission_id,
            current_step="PARSER",
            total_steps=6,
            completed_steps=0,
            status="PENDING",
        )
    
    # Mapper le statut
    status_map = {
        "CREATED": "PENDING",
        "PARSING": "PARSING",
        "EXTRACTING": "EXTRACTING",
        "CLASSIFYING": "CLASSIFYING",
        "AGENT_RUNNING": "AGENT_RUNNING",
        "COMPILING": "COMPILING",
        "REPORTING": "REPORTING",
        "DONE": "COMPLETED",
        "FAILED": "FAILED",
    }
    
    # Calculer current_step à partir de completed_steps et total_steps
    current_step_idx = mission_record.completed_steps
    step_names = ["PARSER", "EXTRACTION", "CLASSIFICATION", "AGENTS", "COMPILATION", "RAPPORT"]
    current_step = step_names[min(current_step_idx, len(step_names) - 1)] if step_names else "PARSER"
    
    return WorkflowStatusResponse(
        mission_id=mission_id,
        current_step=current_step,
        total_steps=mission_record.total_steps or 6,
        completed_steps=mission_record.completed_steps or 0,
        status=status_map.get(mission_record.status, "PENDING"),
    )


@router.post("/{mission_id}/execute", response_model=WorkflowExecutionResponse, summary="Execute Workflow")
async def execute_workflow(
    mission_id: str,
    current_user: TokenData = Depends(get_current_user),
):
    '''Exécuter le workflow pour une mission.'''
    # Récupérer la mission depuis la persistance et démarrer le workflow
    from app.engines.workflow_engine.persistence import get_mission_by_id
    from app.engines.workflow_engine.mission import Mission
    
    # Pour l'instant, retourner une réponse simulée
    # (L'implémentation complète nécessiterait de créer une Mission et d'appeler workflow_engine.run())
    execution_id = f"exec_{mission_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return WorkflowExecutionResponse(
        mission_id=mission_id,
        execution_id=execution_id,
        started_at=datetime.now().isoformat(),
        status="STARTED",
    )
