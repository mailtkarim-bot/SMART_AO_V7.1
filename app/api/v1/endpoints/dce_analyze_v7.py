"""
DCE Analysis V7 Endpoint - Point d'entrée principal pour l'analyse des DCE
Gère l'upload, le parsing initial et le lancement du workflow L5
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from typing import Optional, List
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.schemas.mission import MissionCreate, MissionResponse
from app.models.mission import Mission
from app.models.user import User
from app.core.database import get_db
from app.core.auth import get_current_user, TokenData, require_admin_access
from app.engines.workflow_engine.workflow import WorkflowEngine

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dce-v7", tags=["DCE Analysis V7"])

@router.post("/upload", response_model=MissionResponse)
async def upload_dce(
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_access)
):
    """
    Upload d'un lot de fichiers DCE (ZIP ou PDF multiples)
    Déclenche le workflow d'analyse asynchrone
    """
    if not files:
        raise HTTPException(status_code=400, detail="Aucun fichier fourni")
    
    # Validation basique des extensions
    allowed_extensions = {".pdf", ".zip", ".docx", ".txt"}
    for file in files:
        ext = file.filename.split(".")[-1].lower()
        if f".{ext}" not in allowed_extensions:
            logger.warning(f"Fichier rejeté: {file.filename} (ext: {ext})")
            
    # Création de la mission
    mission_data = MissionCreate(
        user_id=current_user.id,
        status="processing",
        file_count=len(files)
    )
    db_mission = Mission(**mission_data.dict())
    db.add(db_mission)
    await db.commit()
    await db.refresh(db_mission)
    
    # Lancement du workflow en background
    if background_tasks:
        background_tasks.add_task(
            run_dce_analysis_workflow,
            mission_id=db_mission.id,
            files=files
        )
    
    return db_mission

async def run_dce_analysis_workflow(mission_id: int, files: List[UploadFile]):
    """Exécution séquentielle du workflow L5"""
    try:
        engine = WorkflowEngine()
        await engine.execute_full_pipeline(mission_id, files)
        logger.info(f"Workflow terminé pour mission {mission_id}")
    except Exception as e:
        logger.error(f"Échec workflow mission {mission_id}: {str(e)}")
        # Notification d'échec via Event Bus
        from app.engines.event_bus.engine import event_bus
        await event_bus.publish("mission.failed", {"mission_id": mission_id, "error": str(e)})

@router.get("/{mission_id}/status")
async def get_analysis_status(
    mission_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupération du statut d'analyse en temps réel"""
    result = await db.execute(
        select(Mission).where(Mission.id == mission_id)
    )
    mission = result.scalar_one_or_none()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission non trouvée")
    
    # Vérification des permissions
    if mission.user_id != current_user.id and current_user.role != "PATRON":
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    return {
        "mission_id": mission.id,
        "status": mission.status,
        "progress": mission.progress_percent,
        "current_step": mission.current_step,
        "errors": mission.errors_log
    }
