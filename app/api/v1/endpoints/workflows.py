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
from typing import Optional, Dict, Any
from datetime import datetime

from app.schemas.workflow import WorkflowStatusResponse, WorkflowExecutionResponse
from app.engines.workflow_engine.workflow import WorkflowEngine
from app.core.auth import get_current_user, TokenData

router = APIRouter(prefix="/api/v1/workflows", tags=["workflows"])


@router.get("/{mission_id}/status", response_model=WorkflowStatusResponse, summary="Workflow Status")
async def get_workflow_status(
    mission_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    '''Récupérer le statut du workflow pour une mission.'''
    # Intégration avec WorkflowEngine
    from app.engines.workflow_engine.workflow import WorkflowEngine
    workflow_engine = WorkflowEngine()
    
    # Obtenir l'état du workflow pour cette mission
    workflow_state = workflow_engine.get_state(mission_id)
    
    return WorkflowStatusResponse(
        mission_id=mission_id,
        current_step=workflow_state.get("current_step", "PARSER"),
        total_steps=workflow_state.get("total_steps", 6),
        completed_steps=workflow_state.get("completed_steps", 0),
        status=workflow_state.get("status", "PENDING"),
    )


@router.post("/{mission_id}/execute", response_model=WorkflowExecutionResponse, summary="Execute Workflow")
async def execute_workflow(
    mission_id: str,
    current_user: TokenData = Depends(get_current_user),
):
    '''Exécuter le workflow pour une mission.'''
    # Démarrer l'exécution du workflow
    from app.engines.workflow_engine.workflow import WorkflowEngine
    workflow_engine = WorkflowEngine()
    
    # Démarrer le workflow
    execution_id = workflow_engine.start_execution(mission_id, current_user.user_id)
    
    return WorkflowExecutionResponse(
        mission_id=mission_id,
        execution_id=execution_id or f"exec_{mission_id}",
        started_at=datetime.now().isoformat(),
        status="STARTED",
    )
