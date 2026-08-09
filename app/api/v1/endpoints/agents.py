"""
SMART_AO V7 - agents.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional, Dict, Any

from app.schemas.agent import AgentListResponse, AgentResponse
from app.engines.agent_runtime.registry import AgentRegistry, registry
from app.core.auth import get_current_user, TokenData

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


@router.get("", response_model=AgentListResponse, summary="List Agents")
async def list_agents(
    capability: Optional[str] = None,
    is_blocking: Optional[bool] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    '''Lister tous les agents enregistrés.'''
    agents = registry.get_all()
    
    if capability:
        agents = [a for a in agents if capability in a.capabilities]
    if is_blocking is not None:
        agents = [a for a in agents if a.is_blocking == is_blocking]
    
    return AgentListResponse(
        agents=agents,
        total=len(agents),
    )


@router.get("/{agent_name}", response_model=AgentResponse, summary="Get Agent")
async def get_agent(
    agent_name: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    '''Récupérer un agent spécifique.'''
    agent = registry.get_by_name(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")
    return AgentResponse.model_validate(agent, from_attributes=True)
