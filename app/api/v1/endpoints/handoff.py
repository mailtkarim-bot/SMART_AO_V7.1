"""
Handoff Endpoint - Transfert de missions entre utilisateurs/équipes
Gère les délégations, co-traitances et sous-traitance (DC4)
"""
from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.mission import Mission
from app.models.user import User
from app.security.rbac import require_auth, require_admin_access
from datetime import datetime

router = APIRouter(prefix="/handoff", tags=["Handoff"])

class HandoffRequest(BaseModel):
    target_user_id: int
    role: str  # "co_traitant", "sous_traitant", "conducteur_travaux"
    message: Optional[str] = ""
    dc4_required: bool = False  # Déclaration de sous-traitance

@router.post("/{mission_id}")
async def create_handoff(
    mission_id: int,
    request: HandoffRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """Créer un transfert de mission"""
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission non trouvée")
    
    # Vérification des permissions
    if mission.user_id != current_user.id and current_user.role != "PATRON":
        raise HTTPException(status_code=403, detail="Non autorisé à transférer cette mission")
    
    target_user = db.query(User).filter(User.id == request.target_user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Utilisateur cible non trouvé")
    
    # Création du handoff
    handoff_data = {
        "mission_id": mission_id,
        "from_user_id": current_user.id,
        "to_user_id": request.target_user_id,
        "role": request.role,
        "message": request.message,
        "dc4_required": request.dc4_required,
        "status": "pending",
        "created_at": datetime.utcnow()
    }
    
    # TODO: Sauvegarder dans table handoffs (à créer)
    logger.info(f"Handoff créé: mission {mission_id} -> user {request.target_user_id}")
    
    return {"status": "success", "handoff_id": 1, **handoff_data}

@router.get("/pending")
async def get_pending_handoffs(
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """Récupérer les handoffs en attente pour l'utilisateur courant"""
    # TODO: Requête SQL sur table handoffs
    return {"pending_handoffs": []}

@router.post("/{handoff_id}/accept")
async def accept_handoff(
    handoff_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """Accepter un handoff"""
    # TODO: Logique d'acceptation
    return {"status": "accepted", "handoff_id": handoff_id}

@router.post("/{handoff_id}/reject")
async def reject_handoff(
    handoff_id: int,
    reason: str = Body(...),
    db: Session = Depends(get_db),
    current_user = Depends(require_auth)
):
    """Rejeter un handoff avec motif"""
    # TODO: Logique de rejet
    return {"status": "rejected", "handoff_id": handoff_id, "reason": reason}
