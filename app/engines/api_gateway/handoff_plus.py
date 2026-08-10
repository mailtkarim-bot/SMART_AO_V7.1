"""
SMART_AO V7 - handoff_plus.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import logging
import json

from app.db.session import get_db
from app.models.mission import Mission
from app.models.user import User
from app.core.auth import get_current_user
from app.engines.workflow_engine.workflow import WorkflowEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/handoff", tags=["Handoff Plus"])


class HandoffContext(BaseModel):
    """Contexte complet pour le transfert de mission"""
    include_raw_dce: bool = True
    include_extracted_data: bool = True
    include_agent_analysis: bool = True
    include_financial_simulations: bool = True
    include_variants: bool = True
    include_deadlines: bool = True
    custom_fields: Dict[str, Any] = Field(default_factory=dict)


class HandoffPackage(BaseModel):
    """Package de transfert enrichi"""
    mission_id: int
    mission_name: str
    transfer_timestamp: datetime
    source_user: str
    target_users: List[str]
    context_included: List[str]
    data_package: Dict[str, Any]
    checksum: str
    size_bytes: int


class TransferRequest(BaseModel):
    """Demande de transfert de mission"""
    target_user_ids: List[int]
    transfer_type: str  # 'delegate', 'collaborate', 'archive'
    message: Optional[str] = None
    context: HandoffContext = Field(default_factory=HandoffContext)
    notify_target: bool = True


@router.post("/transfer/{mission_id}", response_model=HandoffPackage)
async def transfer_mission(
    mission_id: int,
    request: TransferRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Transfert enrichi d'une mission avec contexte complet
    
    Permet de déléguer une mission à d'autres utilisateurs
    en incluant tout le contexte analytique accumulé.
    """
    logger.info(f"User {current_user.email} initiating transfer of mission {mission_id}")
    
    # Récupérer la mission
    result = await db.execute(
        select(Mission).where(Mission.id == mission_id)
    )
    mission = result.scalar_one_or_none()
    
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mission {mission_id} non trouvée"
        )
    
    # Vérifier les permissions
    if mission.user_id != current_user.id and current_user.role != 'PATRON':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes pour transférer cette mission"
        )
    
    # Récupérer les utilisateurs cibles
    target_users = []
    for user_id in request.target_user_ids:
        user_result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()
        if user:
            target_users.append(user)
        else:
            logger.warning(f"Target user {user_id} not found")
    
    if not target_users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucun utilisateur cible valide trouvé"
        )
    
    # Construire le package de données
    data_package = build_handoff_package(mission, request.context, db)
    
    # Calculer checksum
    import hashlib
    checksum = hashlib.sha256(
        json.dumps(data_package, sort_keys=True, default=str).encode()
    ).hexdigest()[:16]
    
    # Créer le package de transfert
    handoff_package = HandoffPackage(
        mission_id=mission.id,
        mission_name=mission.nom,
        transfer_timestamp=datetime.utcnow(),
        source_user=current_user.email,
        target_users=[u.email for u in target_users],
        context_included=list(request.context.model_dump().keys()),
        data_package=data_package,
        checksum=checksum,
        size_bytes=len(json.dumps(data_package).encode('utf-8'))
    )
    
    # Mettre à jour la mission
    mission.transferred_at = datetime.utcnow()
    mission.transfer_source_id = current_user.id
    await db.commit()
    
    # Notification asynchrone
    if request.notify_target:
        background_tasks.add_task(
            send_transfer_notifications,
            mission,
            current_user,
            target_users,
            request.message
        )
    
    logger.info(f"Mission {mission_id} transferred to {len(target_users)} users")
    return handoff_package


def build_handoff_package(
    mission: Mission,
    context: HandoffContext,
    db: AsyncSession
) -> Dict[str, Any]:
    """Construit le package de données complet"""
    package = {
        "mission_metadata": {
            "id": mission.id,
            "nom": mission.nom,
            "reference": mission.reference_ao,
            "status": mission.status,
            "created_at": mission.created_at.isoformat() if mission.created_at else None,
            "deadlines": {
                "remise": mission.date_remise.isoformat() if mission.date_remise else None,
                "questions": mission.date_limite_questions.isoformat() if mission.date_limite_questions else None,
                "visite": mission.date_visite_obligatoire.isoformat() if mission.date_visite_obligatoire else None
            }
        }
    }
    
    # Inclure DCE brut si demandé
    if context.include_raw_dce and mission.fichier_dce_path:
        import os
        try:
            file_size_bytes = os.path.getsize(mission.fichier_dce_path)
            file_size_mb = round(file_size_bytes / (1024 * 1024), 2)
        except (OSError, TypeError):
            file_size_mb = 0
        
        package["raw_dce"] = {
            "path": mission.fichier_dce_path,
            "size_mb": file_size_mb,
            "pages": mission.nb_pages or 0
        }
    
    # Inclure données extraites
    if context.include_extracted_data:
        package["extracted_data"] = {
            "pab": mission.pab_detected or [],
            "penalites": mission.penalites_identifiees or [],
            "certifications": mission.certifications_requises or [],
            "criteres_jugement": mission.criteres_jugement or []
        }
    
    # Inclure analyse des agents
    if context.include_agent_analysis:
        # Récupérer analyses agents depuis les steps de la mission
        try:
            agent_steps = [
                step for step in mission.steps 
                if step.agent_name and step.output_data
            ]
            agents_data = {
                step.agent_name: {
                    "status": step.status,
                    "execution_time_ms": step.execution_time_ms,
                    "output_summary": step.output_data.get("summary", "") if step.output_data else ""
                }
                for step in agent_steps
            }
            package["agent_analysis"] = {
                "status": "included",
                "agents_count": len(agent_steps),
                "agents": agents_data
            }
        except Exception as e:
            logger.warning(f"Failed to retrieve agent analysis: {e}")
            package["agent_analysis"] = {
                "status": "error",
                "agents_count": 0,
                "error": str(e)
            }
    
    # Inclure simulations financières
    if context.include_financial_simulations:
        package["financial_simulations"] = {
            "status": "included",
            "scenarios": []
        }
    
    # Inclure variantes
    if context.include_variants:
        package["variants"] = {
            "status": "included",
            "count": 0
        }
    
    # Champs personnalisés
    if context.custom_fields:
        package["custom"] = context.custom_fields
    
    return package


async def send_transfer_notifications(
    mission: Mission,
    source_user: User,
    target_users: List[User],
    message: Optional[str]
):
    """Envoie les notifications de transfert"""
    from app.engines.notification_engine.email import EmailSender
    
    sender = EmailSender()
    
    for target in target_users:
        subject = f"📋 Mission transférée: {mission.nom}"
        body = f"""
        Bonjour {target.prenom or target.email},
        
        {source_user.prenom or source_user.email} vous a transféré la mission:
        
        🏗️ {mission.nom}
        📅 Remise: {mission.date_remise.strftime('%d/%m/%Y') if mission.date_remise else 'N/A'}
        
        Message: {message or 'Aucun message'}
        
        Connectez-vous à SMART_AO pour accéder au dossier complet.
        """
        
        try:
            await sender.send_email(
                to=target.email,
                subject=subject,
                body=body
            )
            logger.info(f"Transfer notification sent to {target.email}")
        except Exception as e:
            logger.error(f"Failed to send notification to {target.email}: {e}")


@router.get("/{mission_id}/history", response_model=dict)
async def get_transfer_history(
    mission_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Récupère l'historique des transferts d'une mission"""
    result = await db.execute(
        select(Mission).where(Mission.id == mission_id)
    )
    mission = result.scalar_one_or_none()
    
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mission {mission_id} non trouvée"
        )
    
    # Implémenter historique complet - récupérer tous les transferts depuis les events
    from app.models.events import MissionEvent
    
    result = await db.execute(
        select(MissionEvent).where(
            MissionEvent.mission_id == mission_id,
            MissionEvent.event_type == "transfer"
        ).order_by(MissionEvent.created_at.desc())
    )
    transfer_events = result.scalars().all()
    
    transfers = []
    if mission.transferred_at:
        transfers.append({
            "timestamp": mission.transferred_at.isoformat(),
            "from_user_id": mission.transfer_source_id,
            "to_user_id": mission.user_id,
            "type": "current"
        })
    
    for event in transfer_events:
        transfers.append({
            "timestamp": event.created_at.isoformat() if event.created_at else None,
            "from_user_id": event.data.get("from_user_id") if event.data else None,
            "to_user_id": event.data.get("to_user_id") if event.data else None,
            "type": "event",
            "message": event.data.get("message") if event.data else None
        })
    
    return {
        "mission_id": mission_id,
        "transfers": transfers
    }


@router.post("/accept/{mission_id}", response_model=dict)
async def accept_transfer(
    mission_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Accepte un transfert de mission"""
    result = await db.execute(
        select(Mission).where(Mission.id == mission_id)
    )
    mission = result.scalar_one_or_none()
    
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mission {mission_id} non trouvée"
        )
    
    # Transférer la propriété
    mission.user_id = current_user.id
    mission.status = 'en_cours'
    await db.commit()
    
    logger.info(f"User {current_user.email} accepted transfer of mission {mission_id}")
    
    return {
        "mission_id": mission_id,
        "status": "accepted",
        "new_owner": current_user.email
    }

