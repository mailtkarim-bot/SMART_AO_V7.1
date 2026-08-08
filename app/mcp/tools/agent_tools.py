"""
SMART_AO V7 - agent_tools.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


from typing import List, Dict, Any
from mcp.types import Tool


def get_tools() -> List[Tool]:
    '''Récupérer les outils pour la gestion des agents.'''
    return [
        Tool(
            name="list_agents",
            description="Lister tous les agents disponibles",
            inputSchema={
                "type": "object",
                "properties": {
                    "capability": {"type": "string", "description": "Filtrer par capacité"},
                    "is_blocking": {"type": "boolean", "description": "Filtrer par bloquant"},
                },
            },
            func=_list_agents,
        ),
        Tool(
            name="get_agent",
            description="Récupérer un agent spécifique",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_name": {"type": "string", "description": "Nom de l'agent"},
                },
                "required": ["agent_name"],
            },
            func=_get_agent,
        ),
        Tool(
            name="run_agent",
            description="Exécuter un agent sur une mission",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_name": {"type": "string", "description": "Nom de l'agent"},
                    "mission_id": {"type": "string", "description": "ID de la mission"},
                    "parameters": {"type": "object", "description": "Paramètres de l'agent"},
                },
                "required": ["agent_name", "mission_id"],
            },
            func=_run_agent,
        ),
        Tool(
            name="get_agent_capabilities",
            description="Récupérer les capacités d'un agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_name": {"type": "string", "description": "Nom de l'agent"},
                },
                "required": ["agent_name"],
            },
            func=_get_agent_capabilities,
        ),
    ]


async def _list_agents(
    capability: str = None,
    is_blocking: bool = None,
) -> Dict[str, Any]:
    '''Lister tous les agents.'''
    # TODO: Intégrer avec AgentRegistry
    from app.engines.agent_runtime.registry import registry
    
    agents = registry.get_all()
    result = []
    
    for agent in agents:
        if capability and capability not in agent.capabilities:
            continue
        if is_blocking is not None and agent.is_blocking != is_blocking:
            continue
        
        result.append({
            "name": agent.name,
            "capabilities": agent.capabilities,
            "is_blocking": agent.is_blocking,
            "tags": agent.tags,
        })
    
    return {"agents": result, "total": len(result)}


async def _get_agent(agent_name: str) -> Dict[str, Any]:
    '''Récupérer un agent spécifique.'''
    # TODO: Intégrer avec AgentRegistry
    from app.engines.agent_runtime.registry import registry
    
    agent = registry.get_agent(agent_name)
    if not agent:
        return {"error": f"Agent {agent_name} not found"}
    
    return {
        "name": agent.name,
        "capabilities": agent.capabilities,
        "dependencies": agent.dependencies,
        "is_blocking": agent.is_blocking,
        "tags": agent.tags,
        "estimated_duration_ms": agent.estimated_duration.total_seconds() * 1000,
    }


async def _run_agent(
    agent_name: str,
    mission_id: str,
    parameters: Dict[str, Any] = None,
) -> Dict[str, Any]:
    '''Exécuter un agent sur une mission.'''
    # TODO: Intégrer avec AgentRuntime
    return {
        "agent_name": agent_name,
        "mission_id": mission_id,
        "parameters": parameters or {},
        "status": "STARTED",
        "execution_id": f"exec_{agent_name}_{mission_id}",
    }


async def _get_agent_capabilities(agent_name: str) -> Dict[str, Any]:
    '''Récupérer les capacités d'un agent.'''
    agent = _get_agent(agent_name)
    return {
        "agent_name": agent_name,
        "capabilities": agent.get("capabilities", []),
    }
