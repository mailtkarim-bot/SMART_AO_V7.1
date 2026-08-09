"""
SMART_AO V7.1 - dce_analyze_v7.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5

API Gateway: Endpoint principal d'analyse DCE v7
Orchestre le workflow complet : Upload → Parser → Extraction → Classification → Agents → Rapport
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks, Security
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
import logging
import hashlib
from datetime import datetime

from app.db.session import get_db
from app.api.dependencies.auth import get_current_user, require_patron_access
from app.models.user import User
from app.models.mission import Mission
from app.schemas.mission import MissionCreate, MissionResponse, MissionStatus
from app.engines.workflow_engine.workflow import WorkflowEngine
from app.engines.document_engine.parser import DocumentParser
from app.engines.security_engine.audit_logger import AuditLogger

logger = logging.getLogger(__name__)
router = APIRouter()
audit_logger = AuditLogger()

@router.post("/analyze", response_model=MissionResponse, status_code=201)
async def analyze_dce_v7(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(..., description="Fichiers du DCE (PDF, ZIP, DOCX)"),
    options: Optional[Dict[str, Any]] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_patron_access)
):
    """
    Analyse complète d'un DCE (Dossier de Consultation des Entreprises) - Version 7.
    
    Déclenche le workflow end-to-end :
    1. Parser: Extraction texte depuis PDF/ZIP/DOCX
    2. Extraction: Deadlines, pénalités, PAB, critères de jugement
    3. Classification: Criticité et priorisation
    4. Agents IA: Analyse multi-agents spécialisés
    5. Compilation: Agrégation résultats
    6. Rapport: Génération livrables finaux
    
    Args:
        files: Liste des fichiers du DCE
        options: Options d'analyse (agents spécifiques, seuils, etc.)
        db: Session database
        current_user: Utilisateur authentifié (PATRON requis)
    
    Returns:
        MissionResponse: Informations sur la mission créée
        
    Raises:
        HTTPException: Si erreur lors de l'analyse
    """
    # Audit log
    await audit_logger.log_action(
        user_id=current_user.id,
        action="DCE_ANALYZE_V7",
        resource_type="mission",
        details={"files_count": len(files), "options": options}
    )
    
    if not files:
        raise HTTPException(status_code=400, detail="Aucun fichier fourni")
    
    # Validation des types de fichiers
    allowed_extensions = ['.pdf', '.zip', '.docx', '.doc', '.txt']
    validation_errors = []
    
    for f in files:
        has_valid_ext = any(f.filename.lower().endswith(ext) for ext in allowed_extensions)
        if not has_valid_ext:
            validation_errors.append(f"Fichier non supporté: {f.filename}")
    
    if validation_errors:
        raise HTTPException(status_code=400, detail="; ".join(validation_errors))
    
    try:
        # Hash des fichiers pour traçabilité
        file_hashes = []
        total_size = 0
        for f in files:
            content = await f.read()
            file_hash = hashlib.sha256(content).hexdigest()
            file_hashes.append({"filename": f.filename, "hash": file_hash, "size": len(content)})
            total_size += len(content)
            await f.seek(0)  # Reset file pointer
        
        logger.info(f"Upload DCE: {len(files)} fichiers, {total_size} octets")
        
        # Création de la mission
        mission_name = files[0].filename if files else "DCE Import"
        mission = Mission(
            name=mission_name,
            user_id=current_user.id,
            status="processing",
            progress=0,
            file_hashes=file_hashes,
            total_size=total_size,
            options=options or {}
        )
        
        db.add(mission)
        await db.commit()
        await db.refresh(mission)
        
        # Lancement du workflow en background
        async def process_workflow():
            async with db.begin():
                try:
                    parser = DocumentParser()
                    workflow = WorkflowEngine()
                    
                    # Étape 1: Parsing
                    await db.execute(Mission.__table__.update()
                        .where(Mission.id == mission.id)
                        .values(progress=10, status="parsing"))
                    
                    parsed_docs = await parser.parse_files(files, mission.id)
                    logger.info(f"Parsing terminé: {len(parsed_docs)} documents")
                    
                    # Étape 2-6: Workflow complet
                    await db.execute(Mission.__table__.update()
                        .where(Mission.id == mission.id)
                        .values(progress=20, status="workflow_running"))
                    
                    result = await workflow.execute(mission.id, parsed_docs, options)
                    
                    # Mise à jour statut final
                    await db.execute(Mission.__table__.update()
                        .where(Mission.id == mission.id)
                        .values(
                            status="completed",
                            progress=100,
                            result=result,
                            completed_at=datetime.utcnow()
                        ))
                    
                    logger.info(f"Workflow terminé pour mission {mission.id}")
                    
                except Exception as e:
                    logger.error(f"Erreur workflow: {e}", exc_info=True)
                    await db.execute(Mission.__table__.update()
                        .where(Mission.id == mission.id)
                        .values(
                            status="failed",
                            error_message=str(e),
                            completed_at=datetime.utcnow()
                        ))
        
        background_tasks.add_task(process_workflow)
        
        return MissionResponse.from_orm(mission)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur analyse DCE: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Échec analyse DCE: {str(e)}")


@router.get("/{mission_id}/status", response_model=MissionStatus)
async def get_mission_status(
    mission_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère le statut d'avancement d'une mission d'analyse.
    
    Args:
        mission_id: ID de la mission
        db: Session database
        current_user: Utilisateur authentifié
    
    Returns:
        MissionStatus: Statut actuel de la mission
    """
    mission = await db.get(Mission, mission_id)
    
    if not mission:
        raise HTTPException(status_code=404, detail="Mission non trouvée")
    
    # Vérification des droits d'accès
    if mission.user_id != current_user.id and current_user.role != "PATRON":
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    return MissionStatus.from_orm(mission)


@router.get("/{mission_id}/result")
async def get_mission_result(
    mission_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère les résultats complets d'une mission terminée.
    
    Args:
        mission_id: ID de la mission
        db: Session database
        current_user: Utilisateur authentifié
    
    Returns:
        Dict: Résultats complets de l'analyse
    """
    mission = await db.get(Mission, mission_id)
    
    if not mission:
        raise HTTPException(status_code=404, detail="Mission non trouvée")
    
    if mission.user_id != current_user.id and current_user.role != "PATRON":
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    if mission.status != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Mission non terminée. Statut actuel: {mission.status}"
        )
    
    return {
        "mission_id": mission.id,
        "status": mission.status,
        "result": mission.result,
        "completed_at": mission.completed_at,
        "file_hashes": mission.file_hashes
    }

