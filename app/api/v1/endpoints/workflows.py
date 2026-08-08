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
from app.core.security import get_current_user

router = APIRouter(prefix="/api/v1/workflows", tags=["workflows"])


@router.get("/{mission_id}/status", response_model=WorkflowStatusResponse, summary="Workflow Status")
async def get_workflow_status(
    mission_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    '''Récupérer le statut du workflow pour une mission.'''
    # TODO: Intégrer avec WorkflowEngine
    return WorkflowStatusResponse(
        mission_id=mission_id,
        current_step="PARSER",
        total_steps=6,
        completed_steps=0,
        status="PENDING",
    )


@router.post("/{mission_id}/execute", response_model=WorkflowExecutionResponse, summary="Execute Workflow")
async def execute_workflow(
    mission_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    '''Exécuter le workflow pour une mission.'''
    # TODO: Démarrer l'exécution du workflow
    return WorkflowExecutionResponse(
        mission_id=mission_id,
        execution_id=f"exec_{mission_id}",
        started_at=datetime.now().isoformat(),
        status="STARTED",
    )
