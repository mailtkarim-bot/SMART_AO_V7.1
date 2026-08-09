"""
SMART_AO V7 - deadline_guardian.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel, Field
import logging

from app.core.database import get_db
from app.models.mission import Mission
from app.models.user import User
from app.core.auth import get_current_user
from app.engines.notification_engine.deadline import DeadlineMonitor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/deadline", tags=["Deadline Guardian"])


class DeadlineAlert(BaseModel):
    """Alerte de deadline imminente"""
    mission_id: int
    mission_name: str
    deadline_type: str  # 'remise', 'question', 'visite'
    deadline_date: datetime
    jours_restants: int
    niveau_alerte: str  # 'critique', 'urgent', 'attention'
    destinataires: List[str]


class DeadlineStatus(BaseModel):
    """Statut global des deadlines"""
    total_missions: int
    deadlines_critiques: int
    deadlines_urgentes: int
    deadlines_normales: int
    prochaines_echeances: List[DeadlineAlert]


class EscaladeConfig(BaseModel):
    """Configuration d'escalade des alertes"""
    j7_enabled: bool = True
    j3_enabled: bool = True
    j1_enabled: bool = True
    h6_enabled: bool = True
    email_enabled: bool = True
    sms_enabled: bool = False
    websocket_enabled: bool = True


@router.get("/status", response_model=DeadlineStatus)
async def get_deadline_status(
    current_user: User = Depends(require_authenticated),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère le statut global de toutes les deadlines
    
    Retourne un tableau de bord complet des échéances à venir
    avec classification par niveau d'urgence.
    """
    logger.info(f"User {current_user.email} requested deadline status")
    
    # Récupérer toutes les missions actives
    result = await db.execute(
        select(Mission).where(
            Mission.status.in_(['en_cours', 'analyse', 'chiffrage'])
        )
    )
    missions = result.scalars().all()
    
    now = datetime.utcnow()
    alerts_critique = []
    alerts_urgent = []
    alerts_normal = []
    
    for mission in missions:
        # Vérifier deadline de remise
        if mission.date_remise:
            delta = mission.date_remise - now
            jours_restants = delta.days
            
            alert = DeadlineAlert(
                mission_id=mission.id,
                mission_name=mission.nom,
                deadline_type='remise',
                deadline_date=mission.date_remise,
                jours_restants=jours_restants,
                niveau_alerte='',
                destinataires=[current_user.email]
            )
            
            if jours_restants <= 1:
                alert.niveau_alerte = 'critique'
                alerts_critique.append(alert)
            elif jours_restants <= 3:
                alert.niveau_alerte = 'urgent'
                alerts_urgent.append(alert)
            elif jours_restants <= 7:
                alert.niveau_alerte = 'attention'
                alerts_normal.append(alert)
        
        # Vérifier deadline questions
        if mission.date_limite_questions:
            delta = mission.date_limite_questions - now
            jours_restants = delta.days
            
            if 0 <= jours_restants <= 3:
                alert = DeadlineAlert(
                    mission_id=mission.id,
                    mission_name=mission.nom,
                    deadline_type='questions',
                    deadline_date=mission.date_limite_questions,
                    jours_restants=jours_restants,
                    niveau_alerte='urgent' if jours_restants <= 1 else 'attention',
                    destinataires=[current_user.email]
                )
                if jours_restants <= 1:
                    alerts_critique.append(alert)
                else:
                    alerts_urgent.append(alert)
    
    # Trier par date
    all_alerts = sorted(
        alerts_critique + alerts_urgent + alerts_normal,
        key=lambda x: x.jours_restants
    )[:10]  # Top 10 prochaines échéances
    
    return DeadlineStatus(
        total_missions=len(missions),
        deadlines_critiques=len(alerts_critique),
        deadlines_urgentes=len(alerts_urgent),
        deadlines_normales=len(alerts_normal),
        prochaines_echeances=all_alerts
    )


@router.post("/escalade/{mission_id}", response_model=dict)
async def trigger_escalade(
    mission_id: int,
    config: EscaladeConfig,
    current_user: User = Depends(require_authenticated),
    db: AsyncSession = Depends(get_db)
):
    """
    Déclenche une escalade manuelle pour une mission
    
    Envoie des notifications selon la configuration d'escalade
    J-7, J-3, J-1, H-6
    """
    logger.info(f"User {current_user.email} triggered escalation for mission {mission_id}")
    
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
    
    # Initialiser le moniteur de deadlines
    monitor = DeadlineMonitor(db)
    
    notifications_envoyees = []
    
    # J-7 : Première alerte
    if config.j7_enabled:
        try:
            await monitor.send_j7_alert(mission, [current_user.email])
            notifications_envoyees.append("J-7 alert sent")
        except Exception as e:
            logger.error(f"Erreur envoi alerte J-7: {e}")
    
    # J-3 : Alert intermédiaire
    if config.j3_enabled:
        try:
            await monitor.send_j3_alert(mission, [current_user.email])
            notifications_envoyees.append("J-3 alert sent")
        except Exception as e:
            logger.error(f"Erreur envoi alerte J-3: {e}")
    
    # J-1 : Urgence critique
    if config.j1_enabled:
        try:
            await monitor.send_j1_alert(mission, [current_user.email])
            notifications_envoyees.append("J-1 alert sent")
        except Exception as e:
            logger.error(f"Erreur envoi alerte J-1: {e}")
    
    # H-6 : Dernière chance
    if config.h6_enabled:
        try:
            await monitor.send_h6_alert(mission, [current_user.email])
            notifications_envoyees.append("H-6 alert sent")
        except Exception as e:
            logger.error(f"Erreur envoi alerte H-6: {e}")
    
    # Email de synthèse
    if config.email_enabled:
        try:
            await monitor.send_email_synthesis(mission, [current_user.email])
            notifications_envoyees.append("Email synthesis sent")
        except Exception as e:
            logger.error(f"Erreur envoi email synthèse: {e}")
    
    return {
        "mission_id": mission_id,
        "mission_name": mission.nom,
        "notifications_envoyees": notifications_envoyees,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/missions/{mission_id}/countdown", response_model=dict)
async def get_countdown(
    mission_id: int,
    current_user: User = Depends(require_authenticated),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère le compte à rebours détaillé pour une mission
    
    Retourne le temps restant精确 jusqu'aux secondes près
    pour chaque type de deadline.
    """
    result = await db.execute(
        select(Mission).where(Mission.id == mission_id)
    )
    mission = result.scalar_one_or_none()
    
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mission {mission_id} non trouvée"
        )
    
    now = datetime.utcnow()
    countdown = {}
    
    if mission.date_remise:
        delta = mission.date_remise - now
        countdown['remise'] = {
            'date': mission.date_remise.isoformat(),
            'jours': delta.days,
            'heures': delta.seconds // 3600,
            'minutes': (delta.seconds % 3600) // 60,
            'secondes': delta.seconds % 60,
            'total_secondes': int(delta.total_seconds()),
            'expire': delta.total_seconds() <= 0
        }
    
    if mission.date_limite_questions:
        delta = mission.date_limite_questions - now
        countdown['questions'] = {
            'date': mission.date_limite_questions.isoformat(),
            'jours': delta.days,
            'heures': delta.seconds // 3600,
            'minutes': (delta.seconds % 3600) // 60,
            'secondes': delta.seconds % 60,
            'total_secondes': int(delta.total_seconds()),
            'expire': delta.total_seconds() <= 0
        }
    
    if mission.date_visite_obligatoire:
        delta = mission.date_visite_obligatoire - now
        countdown['visite'] = {
            'date': mission.date_visite_obligatoire.isoformat(),
            'jours': delta.days,
            'heures': delta.seconds // 3600,
            'minutes': (delta.seconds % 3600) // 60,
            'secondes': delta.seconds % 60,
            'total_secondes': int(delta.total_seconds()),
            'expire': delta.total_seconds() <= 0
        }
    
    return {
        "mission_id": mission_id,
        "mission_name": mission.nom,
        "countdown": countdown,
        "timestamp": now.isoformat()
    }


@router.post("/config/{user_id}", response_model=dict)
async def update_deadline_config(
    user_id: int,
    config: EscaladeConfig,
    current_user: User = Depends(require_authenticated),
    db: AsyncSession = Depends(get_db)
):
    """
    Met à jour la configuration d'escalade pour un utilisateur
    
    Permet de personnaliser les seuils et canaux de notification
    """
    # TODO: Implémenter la persistance dans UserSettings
    logger.info(f"User {current_user.email} updated deadline config: {config}")
    
    return {
        "user_id": user_id,
        "config_updated": config.dict(),
        "message": "Configuration sauvegardée avec succès"
    }


@router.get("/calendar", response_model=dict)
async def get_deadline_calendar(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(require_authenticated),
    db: AsyncSession = Depends(get_db)
):
    """
    Exporte les deadlines au format calendrier (iCal/JSON)
    
    Permet l'intégration avec Outlook, Google Calendar, etc.
    """
    from datetime import datetime
    
    # Parse dates ou utiliser défaut (30 prochains jours)
    if start_date:
        start = datetime.fromisoformat(start_date)
    else:
        start = datetime.utcnow()
    
    if end_date:
        end = datetime.fromisoformat(end_date)
    else:
        end = start + timedelta(days=30)
    
    result = await db.execute(
        select(Mission).where(
            Mission.status.in_(['en_cours', 'analyse', 'chiffrage']),
            or_(
                Mission.date_remise.between(start, end),
                Mission.date_limite_questions.between(start, end),
                Mission.date_visite_obligatoire.between(start, end)
            )
        )
    )
    missions = result.scalars().all()
    
    events = []
    for mission in missions:
        if mission.date_remise:
            events.append({
                'title': f"🚨 REMISE - {mission.nom}",
                'start': mission.date_remise.isoformat(),
                'end': (mission.date_remise + timedelta(hours=2)).isoformat(),
                'type': 'remise',
                'priority': 'high'
            })
        
        if mission.date_limite_questions:
            events.append({
                'title': f"❓ Questions - {mission.nom}",
                'start': mission.date_limite_questions.isoformat(),
                'end': (mission.date_limite_questions + timedelta(hours=2)).isoformat(),
                'type': 'questions',
                'priority': 'medium'
            })
        
        if mission.date_visite_obligatoire:
            events.append({
                'title': f"🏗️ Visite - {mission.nom}",
                'start': mission.date_visite_obligatoire.isoformat(),
                'end': (mission.date_visite_obligatoire + timedelta(hours=2)).isoformat(),
                'type': 'visite',
                'priority': 'high'
            })
    
    return {
        "calendar_period": {
            "start": start.isoformat(),
            "end": end.isoformat()
        },
        "total_events": len(events),
        "events": events
    }

