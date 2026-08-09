"""
SMART_AO V7 - post_gagne_tracker.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Suivi Post-Gagné - Suivi des missions après attribution
Source: ARCHITECTURE_V7_ENGINE.md §4.3
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import logging
from decimal import Decimal

from app.core.database import get_db
from app.core.auth import get_current_user, TokenData

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/post-gagne", tags=["Post-Gagné Tracker"])


class PostGagneStatus(str):
    """Statuts des missions post-gagné."""
    EN_ATTENTE = "en_attente"
    DEMARRAGE = "demarrage"
    EN_COURS = "en_cours"
    SUSPENDU = "suspendu"
    TERMINE = "termine"
    CLOTURE = "cloture"


class PostGagneMission(BaseModel):
    """Mission post-gagné."""
    mission_id: str
    project_name: str
    client_name: str
    attribution_date: datetime
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: PostGagneStatus
    contract_amount: Decimal
    current_progress: float = Field(default=0.0, ge=0.0, le=100.0)
    spent_amount: Decimal = Field(default=Decimal(0))
    remaining_budget: Decimal
    key_milestones: List[Dict[str, Any]] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    issues: List[str] = Field(default_factory=list)
    last_update: datetime


class PostGagneTrackingRequest(BaseModel):
    """Requête de suivi post-gagné."""
    mission_id: str
    progress_update: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    spent_amount_update: Optional[Decimal] = None
    milestone_completed: Optional[str] = None
    new_risk: Optional[str] = None
    new_issue: Optional[str] = None
    status_update: Optional[PostGagneStatus] = None


class PostGagneTrackingResponse(BaseModel):
    """Réponse de suivi post-gagné."""
    mission_id: str
    previous_status: PostGagneStatus
    new_status: PostGagneStatus
    progress: float
    budget_consumption: float  # Pourcentage du budget consommé
    updated_at: datetime
    changes: Dict[str, Any]


class PostGagneDashboard(BaseModel):
    """Tableau de bord post-gagné."""
    total_missions: int
    missions_by_status: Dict[PostGagneStatus, int]
    total_contract_amount: Decimal
    total_spent: Decimal
    overall_progress: float
    active_missions: int
    at_risk_missions: int
    over_budget_missions: int
    recent_updates: List[Dict[str, Any]]


class PostGagneAlert(BaseModel):
    """Alerte post-gagné."""
    mission_id: str
    alert_type: str  # "retard", "budget", "risque", "qualite"
    severity: str  # "faible", "moyen", "eleve", "critique"
    message: str
    details: Optional[Dict[str, Any]] = None
    created_at: datetime
    acknowledged: bool = False


class PostGagneTracker:
    """Suivi des missions post-gagné."""
    
    def __init__(self):
        self.missions = {}  # En production: remplacé par requêtes DB
    
    def track_mission(
        self,
        mission_id: str,
        request: PostGagneTrackingRequest
    ) -> PostGagneTrackingResponse:
        """Met à jour le suivi d'une mission post-gagné."""
        # En production: récupérer depuis la base de données
        mission = self.missions.get(mission_id, {
            "status": PostGagneStatus.EN_ATTENTE,
            "progress": 0.0,
            "spent_amount": Decimal(0),
            "contract_amount": Decimal(100000)
        })
        
        previous_status = mission.get("status", PostGagneStatus.EN_ATTENTE)
        current_progress = mission.get("progress", 0.0)
        current_spent = mission.get("spent_amount", Decimal(0))
        contract_amount = mission.get("contract_amount", Decimal(100000))
        
        # Appliquer les mises à jour
        new_status = request.status_update or previous_status
        new_progress = request.progress_update or current_progress
        new_spent = request.spent_amount_update or current_spent
        
        # Calculer la consommation du budget
        if contract_amount > 0:
            budget_consumption = float(new_spent / contract_amount) * 100
        else:
            budget_consumption = 0.0
        
        # Construire les changements
        changes = {}
        if request.progress_update is not None:
            changes["progress"] = {"old": current_progress, "new": new_progress}
        if request.spent_amount_update is not None:
            changes["spent_amount"] = {"old": str(current_spent), "new": str(new_spent)}
        if request.status_update is not None:
            changes["status"] = {"old": previous_status.value, "new": new_status.value}
        if request.milestone_completed:
            changes["milestone"] = request.milestone_completed
        if request.new_risk:
            changes["new_risk"] = request.new_risk
        if request.new_issue:
            changes["new_issue"] = request.new_issue
        
        # Mettre à jour la mission en mémoire
        self.missions[mission_id] = {
            "status": new_status,
            "progress": new_progress,
            "spent_amount": new_spent,
            "contract_amount": contract_amount
        }
        
        return PostGagneTrackingResponse(
            mission_id=mission_id,
            previous_status=previous_status,
            new_status=new_status,
            progress=new_progress,
            budget_consumption=budget_consumption,
            updated_at=datetime.utcnow(),
            changes=changes
        )
    
    def generate_dashboard(self, mission_ids: Optional[List[str]] = None) -> PostGagneDashboard:
        """Génère un tableau de bord post-gagné."""
        missions = []
        
        if mission_ids:
            missions = [
                self.missions.get(mid, {"status": PostGagneStatus.EN_ATTENTE, "contract_amount": Decimal(0)})
                for mid in mission_ids
            ]
        else:
            missions = list(self.missions.values())
        
        if not missions:
            return PostGagneDashboard(
                total_missions=0,
                missions_by_status={},
                total_contract_amount=Decimal(0),
                total_spent=Decimal(0),
                overall_progress=0.0,
                active_missions=0,
                at_risk_missions=0,
                over_budget_missions=0,
                recent_updates=[]
            )
        
        # Compter par statut
        missions_by_status = {}
        for status in [s for s in PostGagneStatus]:
            missions_by_status[status] = sum(
                1 for m in missions if m.get("status") == status
            )
        
        # Calculer les totaux
        total_contract_amount = sum(
            m.get("contract_amount", Decimal(0)) for m in missions
        )
        total_spent = sum(
            m.get("spent_amount", Decimal(0)) for m in missions
        )
        
        # Calculer le progrès moyen
        progresses = [m.get("progress", 0.0) for m in missions if m.get("progress") is not None]
        overall_progress = sum(progresses) / len(progresses) if progresses else 0.0
        
        # Missions actives
        active_missions = missions_by_status.get(PostGagneStatus.EN_COURS, 0)
        
        # Missions à risque (retard ou budget dépassé)
        at_risk_missions = sum(
            1 for m in missions 
            if m.get("status") == PostGagneStatus.SUSPENDU or 
               (m.get("spent_amount", Decimal(0)) > m.get("contract_amount", Decimal(0)))
        )
        
        # Missions en dépassement de budget
        over_budget_missions = sum(
            1 for m in missions 
            if m.get("spent_amount", Decimal(0)) > m.get("contract_amount", Decimal(0))
        )
        
        return PostGagneDashboard(
            total_missions=len(missions),
            missions_by_status=missions_by_status,
            total_contract_amount=total_contract_amount,
            total_spent=total_spent,
            overall_progress=overall_progress,
            active_missions=active_missions,
            at_risk_missions=at_risk_missions,
            over_budget_missions=over_budget_missions,
            recent_updates=[]
        )
    
    def detect_alerts(self, mission_id: str) -> List[PostGagneAlert]:
        """Détecte les alertes pour une mission post-gagné."""
        mission = self.missions.get(mission_id, {})
        alerts = []
        
        progress = mission.get("progress", 0.0)
        spent = mission.get("spent_amount", Decimal(0))
        contract = mission.get("contract_amount", Decimal(0))
        status = mission.get("status", PostGagneStatus.EN_ATTENTE)
        
        # Alerte de retard
        if status == PostGagneStatus.EN_COURS and progress < 10.0:
            alerts.append(PostGagneAlert(
                mission_id=mission_id,
                alert_type="retard",
                severity="eleve",
                message=f"Progrès insuffisant: {progress}% après démarrage",
                created_at=datetime.utcnow()
            ))
        
        # Alerte de budget
        if contract > 0:
            budget_ratio = float(spent / contract)
            if budget_ratio > 0.9:
                alerts.append(PostGagneAlert(
                    mission_id=mission_id,
                    alert_type="budget",
                    severity="eleve" if budget_ratio < 1.0 else "critique",
                    message=f"Budget consommé à {budget_ratio*100:.1f}%",
                    created_at=datetime.utcnow()
                ))
        
        # Alerte de dépassement
        if spent > contract:
            alerts.append(PostGagneAlert(
                mission_id=mission_id,
                alert_type="budget",
                severity="critique",
                message=f"Dépassement de budget: {float(spent - contract):.0f} €",
                created_at=datetime.utcnow()
            ))
        
        return alerts


tracker = PostGagneTracker()


@router.post("/track", response_model=PostGagneTrackingResponse)
async def update_post_gagne_tracking(
    request: PostGagneTrackingRequest,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Met à jour le suivi d'une mission post-gagné.
    """
    logger.info(f"Mise à jour suivi post-gagné pour mission {request.mission_id} par {current_user.user_id}")
    
    result = tracker.track_mission(request.mission_id, request)
    
    return result


@router.get("/missions", response_model=List[PostGagneMission])
async def list_post_gagne_missions(
    status: Optional[PostGagneStatus] = None,
    min_progress: Optional[float] = None,
    max_progress: Optional[float] = None,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Liste les missions post-gagné.
    """
    logger.info(f"Liste missions post-gagné par {current_user.user_id}")
    
    # En production: requête SQL
    return []


@router.get("/missions/{mission_id}", response_model=PostGagneMission)
async def get_post_gagne_mission(
    mission_id: str,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère les détails d'une mission post-gagné.
    """
    logger.info(f"Détails mission post-gagné {mission_id} par {current_user.user_id}")
    
    # En production: requête SQL
    return PostGagneMission(
        mission_id=mission_id,
        project_name=f"Projet-{mission_id}",
        client_name="Client Exemple",
        attribution_date=datetime.utcnow() - timedelta(days=30),
        start_date=datetime.utcnow() - timedelta(days=15),
        end_date=datetime.utcnow() + timedelta(days=180),
        status=PostGagneStatus.EN_COURS,
        contract_amount=Decimal(100000),
        current_progress=50.0,
        spent_amount=Decimal(45000),
        remaining_budget=Decimal(55000),
        key_milestones=[
            {"name": "Démarrage", "due_date": (datetime.utcnow() - timedelta(days=15)).isoformat(), "completed": True},
            {"name": "Mi-projet", "due_date": (datetime.utcnow() + timedelta(days=75)).isoformat(), "completed": False}
        ],
        risks=[],
        issues=[],
        last_update=datetime.utcnow()
    )


@router.get("/dashboard", response_model=PostGagneDashboard)
async def get_post_gagne_dashboard(
    mission_ids: Optional[List[str]] = None,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère le tableau de bord post-gagné.
    """
    logger.info(f"Tableau de bord post-gagné par {current_user.user_id}")
    
    dashboard = tracker.generate_dashboard(mission_ids)
    
    return dashboard


@router.get("/alerts", response_model=List[PostGagneAlert])
async def get_post_gagne_alerts(
    mission_id: Optional[str] = None,
    severity: Optional[str] = None,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère les alertes post-gagné.
    """
    logger.info(f"Alertes post-gagné par {current_user.user_id}")
    
    if mission_id:
        return tracker.detect_alerts(mission_id)
    
    return []


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "post_gagne_tracker",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

