"""
SMART_AO V7 - mission_tools.py
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
    '''Récupérer les outils pour la gestion des missions.'''
    return [
        Tool(
            name="create_mission",
            description="Créer une nouvelle mission SMART_AO",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "ID du projet"},
                    "documents": {"type": "array", "items": {"type": "string"}, "description": "Liste des IDs de documents"},
                    "context": {"type": "object", "description": "Contexte de la mission"},
                    "priority": {"type": "string", "enum": ["BASSE", "NORMALE", "HAUTE", "URGENTE"], "default": "NORMALE"},
                },
                "required": ["project_id"],
            },
            func=_create_mission,
        ),
        Tool(
            name="list_missions",
            description="Lister toutes les missions",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {"type": "string", "description": "Filtrer par statut"},
                    "limit": {"type": "integer", "default": 100},
                    "offset": {"type": "integer", "default": 0},
                },
            },
            func=_list_missions,
        ),
        Tool(
            name="get_mission",
            description="Récupérer une mission spécifique",
            inputSchema={
                "type": "object",
                "properties": {
                    "mission_id": {"type": "string", "description": "ID de la mission"},
                },
                "required": ["mission_id"],
            },
            func=_get_mission,
        ),
        Tool(
            name="execute_workflow",
            description="Exécuter le workflow pour une mission",
            inputSchema={
                "type": "object",
                "properties": {
                    "mission_id": {"type": "string", "description": "ID de la mission"},
                },
                "required": ["mission_id"],
            },
            func=_execute_workflow,
        ),
        Tool(
            name="get_workflow_status",
            description="Récupérer le statut du workflow",
            inputSchema={
                "type": "object",
                "properties": {
                    "mission_id": {"type": "string", "description": "ID de la mission"},
                },
                "required": ["mission_id"],
            },
            func=_get_workflow_status,
        ),
    ]


async def _create_mission(
    project_id: str,
    documents: List[str] = None,
    context: Dict[str, Any] = None,
    priority: str = "NORMALE",
) -> Dict[str, Any]:
    '''Créer une nouvelle mission via WorkflowEngine.'''
    from app.engines.workflow_engine.workflow import WorkflowEngine
    from app.models.mission import Mission
    
    try:
        engine = WorkflowEngine()
        mission = await engine.create_mission(
            project_id=project_id,
            document_ids=documents or [],
            context=context or {},
            priority=priority
        )
        
        return {
            "status": "success",
            "mission_id": mission.id,
            "project_id": project_id,
            "documents": documents or [],
            "context": context or {},
            "priority": priority,
            "message": "Mission créée avec succès"
        }
    except Exception as e:
        logger.error(f"Erreur création mission: {e}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Échec de la création de mission"
        }


async def _list_missions(
    status: str = None,
    limit: int = 100,
    offset: int = 0,
) -> Dict[str, Any]:
    '''Lister toutes les missions depuis la base.'''
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.db.session import get_db_session
    from app.models.mission import Mission
    
    try:
        async with get_db_session() as session:
            query = select(Mission)
            if status:
                query = query.where(Mission.status == status)
            query = query.offset(offset).limit(limit)
            
            result = await session.execute(query)
            missions = result.scalars().all()
            
            return {
                "missions": [
                    {
                        "id": m.id,
                        "project_id": m.project_id,
                        "status": m.status,
                        "priority": m.priority,
                        "created_at": m.created_at.isoformat()
                    }
                    for m in missions
                ],
                "total": len(missions),
                "limit": limit,
                "offset": offset
            }
    except Exception as e:
        logger.error(f"Erreur liste missions: {e}")
        return {"missions": [], "total": 0, "error": str(e)}


async def _get_mission(mission_id: str) -> Dict[str, Any]:
    '''Récupérer une mission spécifique depuis la base.'''
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.db.session import get_db_session
    from app.models.mission import Mission
    from sqlalchemy import select
    
    try:
        async with get_db_session() as session:
            result = await session.execute(
                select(Mission).where(Mission.id == mission_id)
            )
            mission = result.scalar_one_or_none()
            
            if not mission:
                return {"error": "Mission non trouvée", "status": "not_found"}
            
            return {
                "id": mission.id,
                "project_id": mission.project_id,
                "status": mission.status,
                "documents": [d.id for d in mission.documents],
                "context": mission.context,
                "priority": mission.priority,
                "workflow_state": mission.workflow_state,
                "created_at": mission.created_at.isoformat(),
                "updated_at": mission.updated_at.isoformat()
            }
    except Exception as e:
        logger.error(f"Erreur récupération mission: {e}")
        return {"error": str(e), "status": "error"}


async def _execute_workflow(mission_id: str) -> Dict[str, Any]:
    '''Exécuter le workflow pour une mission via WorkflowEngine.'''
    from app.engines.workflow_engine.workflow import WorkflowEngine
    
    try:
        engine = WorkflowEngine()
        execution = await engine.execute_workflow(mission_id)
        
        return {
            "mission_id": mission_id,
            "execution_id": execution.id,
            "status": "STARTED",
            "started_at": execution.started_at.isoformat(),
            "message": "Workflow démarré avec succès"
        }
    except Exception as e:
        logger.error(f"Erreur exécution workflow: {e}")
        return {
            "mission_id": mission_id,
            "status": "ERROR",
            "error": str(e)
        }


async def _get_workflow_status(mission_id: str) -> Dict[str, Any]:
    '''Récupérer le statut du workflow depuis WorkflowEngine.'''
    from app.engines.workflow_engine.workflow import WorkflowEngine
    
    try:
        engine = WorkflowEngine()
        status = await engine.get_workflow_status(mission_id)
        
        return {
            "mission_id": mission_id,
            "current_step": status.current_step,
            "total_steps": status.total_steps,
            "completed_steps": status.completed_steps,
            "status": status.overall_status,
            "progress_percent": int((status.completed_steps / status.total_steps) * 100) if status.total_steps > 0 else 0,
            "last_updated": status.last_updated.isoformat() if status.last_updated else None
        }
    except Exception as e:
        logger.error(f"Erreur statut workflow: {e}")
        return {
            "mission_id": mission_id,
            "status": "ERROR",
            "error": str(e)
        }
