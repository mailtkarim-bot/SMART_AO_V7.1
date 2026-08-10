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
import asyncio


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
    '''Lister tous les agents depuis le registry.'''
    # Intégrer avec AgentRegistry
    from app.engines.agent_runtime.registry import registry
    
    # Le registry est synchrone, donc on l'appelle dans un thread
    loop = asyncio.get_event_loop()
    
    def sync_list():
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
    
    return await loop.run_in_executor(None, sync_list)


async def _get_agent(agent_name: str) -> Dict[str, Any]:
    '''Récupérer un agent spécifique depuis le registry.'''
    # Intégrer avec AgentRegistry
    from app.engines.agent_runtime.registry import registry
    
    # Le registry est synchrone
    loop = asyncio.get_event_loop()
    
    def sync_get():
        agent = registry.get_by_name(agent_name)
        if not agent:
            return {"error": f"Agent {agent_name} not found"}
        
        return {
            "name": agent.name,
            "capabilities": agent.capabilities,
            "dependencies": getattr(agent, 'dependencies', []),
            "is_blocking": getattr(agent, 'is_blocking', False),
            "tags": getattr(agent, 'tags', []),
            "estimated_duration_ms": getattr(agent, 'estimated_duration', {}).get('total_seconds', 0) * 1000,
        }
    
    return await loop.run_in_executor(None, sync_get)


async def _run_agent(
    agent_name: str,
    mission_id: str,
    parameters: Dict[str, Any] = None,
) -> Dict[str, Any]:
    '''Exécuter un agent sur une mission.'''
    # Intégrer avec AgentRuntime via registry
    from app.engines.agent_runtime.registry import registry
    from app.agents.base_agent import AgentInput, AgentOutput
    import asyncio
    import uuid
    from datetime import datetime
    
    execution_id = f"exec_{uuid.uuid4().hex[:8]}_{agent_name}_{mission_id}"
    
    # Le registry est synchrone, donc on l'appelle dans un thread
    loop = asyncio.get_event_loop()
    
    def sync_get_agent():
        return registry.get_by_name(agent_name)
    
    agent = await loop.run_in_executor(None, sync_get_agent)
    
    if not agent:
        return {
            "error": f"Agent {agent_name} not found",
            "agent_name": agent_name,
            "mission_id": mission_id,
            "status": "NOT_FOUND",
            "execution_id": execution_id,
        }
    
    try:
        # Construire l'input
        input_data = AgentInput(
            mission_id=mission_id,
            dce_chunks=parameters.get("dce_chunks", []),
            parsed_docs=parameters.get("parsed_docs", {}),
            context=parameters.get("context", {}),
            previous_outputs=parameters.get("previous_outputs", {}),
        )
        
        # Exécuter l'agent
        start_time = datetime.utcnow()
        output: AgentOutput = await agent.execute(input_data)
        end_time = datetime.utcnow()
        
        return {
            "agent_name": agent_name,
            "mission_id": mission_id,
            "parameters": parameters or {},
            "status": output.status,
            "execution_id": execution_id,
            "execution_time_ms": (end_time - start_time).total_seconds() * 1000,
            "capability": output.capability,
            "confidence": output.confidence,
            "findings": output.findings,
            "warnings": output.warnings,
            "source_pages": output.source_pages,
        }
    except Exception as e:
        return {
            "error": f"Execution failed: {str(e)}",
            "agent_name": agent_name,
            "mission_id": mission_id,
            "status": "FAILED",
            "execution_id": execution_id,
            "parameters": parameters or {},
        }


async def _get_agent_capabilities(agent_name: str) -> Dict[str, Any]:
    '''Récupérer les capacités d'un agent.'''
    agent = _get_agent(agent_name)
    return {
        "agent_name": agent_name,
        "capabilities": agent.get("capabilities", []),
    }
