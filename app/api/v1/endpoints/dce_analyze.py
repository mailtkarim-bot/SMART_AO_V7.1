"""
SMART_AO V7.1 - API Gateway: DCE Analysis Endpoint
Copyright (c) 2024 SMART_AO. Tous droits réservés.
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from app.core.database import get_db
from app.core.auth import get_current_user, require_admin_access
from app.models.user import User
from app.models.mission import Mission
from app.schemas.mission import MissionCreate, MissionResponse
from app.engines.workflow_engine.workflow import WorkflowEngine
from app.engines.document_engine.parser import DocumentParser

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/analyze", response_model=MissionResponse, status_code=201)
async def analyze_dce(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_access)
):
    """
    Analyse complète d'un DCE (Dossier de Consultation des Entreprises).
    Déclenche le workflow end-to-end : Parser → Extraction → Classification → Agents → Rapport.
    """
    if not files:
        raise HTTPException(status_code=400, detail="Aucun fichier fourni")
    
    # Validation des types de fichiers
    allowed_types = ["application/pdf", "application/zip", "application/msword", 
                     "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    for f in files:
        if f.content_type not in allowed_types and not f.filename.endswith(('.pdf', '.zip', '.docx', '.doc')):
            logger.warning(f"Type de fichier non supporté: {f.content_type}")
    
    try:
        # Création de la mission
        mission_data = MissionCreate(
            name=files[0].filename if files else "DCE Import",
            user_id=current_user.user_id,
            status="processing"
        )
        mission = Mission(**mission_data.dict())
        db.add(mission)
        await db.commit()
        await db.refresh(mission)
        
        # Lancement du workflow en background
        parser = DocumentParser()
        workflow = WorkflowEngine()
        
        async def process_workflow():
            try:
                # Étape 1: Parsing
                parsed_docs = await parser.parse_files(files, mission.id)
                
                # Étape 2-6: Workflow complet
                result = await workflow.execute(mission.id, parsed_docs)
                
                # Mise à jour statut
                mission.status = "completed"
                mission.result = result
                await db.commit()
                
                logger.info(f"Workflow terminé pour mission {mission.id}")
            except Exception as e:
                logger.error(f"Erreur workflow: {e}")
                mission.status = "failed"
                mission.error_message = str(e)
                await db.commit()
        
        background_tasks.add_task(process_workflow)
        
        return MissionResponse.from_orm(mission)
        
    except Exception as e:
        logger.error(f"Erreur analyse DCE: {e}")
        raise HTTPException(status_code=500, detail=f"Échec analyse DCE: {str(e)}")

@router.get("/{mission_id}/status")
async def get_mission_status(
    mission_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère le statut d'avancement d'une mission d'analyse."""
    mission = await db.get(Mission, mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission non trouvée")
    
    if mission.user_id != current_user.id and current_user.role != "PATRON":
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    return {
        "id": mission.id,
        "status": mission.status,
        "progress": mission.progress,
        "created_at": mission.created_at,
        "completed_at": mission.completed_at
    }
