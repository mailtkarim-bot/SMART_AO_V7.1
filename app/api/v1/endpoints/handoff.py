"""
Handoff Endpoint - Transfert de missions entre utilisateurs/équipes
Gère les délégations, co-traitances et sous-traitance (DC4)
"""
from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.mission import Mission
from app.models.user import User
from app.core.auth import get_current_user, require_admin_access
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
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
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Créer un transfert de mission"""
    result = await db.execute(
        select(Mission).where(Mission.id == mission_id)
    )
    mission = result.scalar_one_or_none()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission non trouvée")
    
    # Vérification des permissions
    if mission.user_id != current_user.id and current_user.role != "PATRON":
        raise HTTPException(status_code=403, detail="Non autorisé à transférer cette mission")
    
    result = await db.execute(
        select(User).where(User.id == request.target_user_id)
    )
    target_user = result.scalar_one_or_none()
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
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Sauvegarder dans table handoffs (solution temporaire avant migration DB)
    import json
    from pathlib import Path
    handoffs_db = Path("data/handoffs.json")
    handoffs_db.parent.mkdir(parents=True, exist_ok=True)
    
    handoffs = []
    if handoffs_db.exists():
        try:
            with open(handoffs_db, 'r') as f:
                handoffs = json.load(f)
        except:
            pass
    
    handoff_id = len(handoffs) + 1
    handoff_data["id"] = handoff_id
    handoffs.append(handoff_data)
    
    with open(handoffs_db, 'w') as f:
        json.dump(handoffs, f, indent=2)
    
    logger.info(f"Handoff créé: mission {mission_id} -> user {request.target_user_id}")
    
    return {"status": "success", "handoff_id": handoff_id, **handoff_data}

@router.get("/pending")
async def get_pending_handoffs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupérer les handoffs en attente pour l'utilisateur courant"""
    # Requête sur table handoffs
    import json
    from pathlib import Path
    handoffs_db = Path("data/handoffs.json")
    
    if not handoffs_db.exists():
        return {"pending_handoffs": []}
    
    try:
        with open(handoffs_db, 'r') as f:
            handoffs = json.load(f)
        
        # Filtrer les handoffs en attente pour l'utilisateur courant
        pending = [
            h for h in handoffs 
            if h.get("to_user_id") == current_user.id and h.get("status") == "pending"
        ]
        
        return {"pending_handoffs": pending}
    except:
        return {"pending_handoffs": []}

@router.post("/{handoff_id}/accept")
async def accept_handoff(
    handoff_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Accepter un handoff"""
    # Logique d'acceptation
    import json
    from pathlib import Path
    handoffs_db = Path("data/handoffs.json")
    
    if handoffs_db.exists():
        with open(handoffs_db, 'r') as f:
            handoffs = json.load(f)
        
        for h in handoffs:
            if h.get("id") == handoff_id:
                h["status"] = "accepted"
                h["accepted_at"] = datetime.utcnow().isoformat()
                h["accepted_by"] = current_user.id
                break
        
        with open(handoffs_db, 'w') as f:
            json.dump(handoffs, f, indent=2)
    
    return {"status": "accepted", "handoff_id": handoff_id, "accepted_by": current_user.id}

@router.post("/{handoff_id}/reject")
async def reject_handoff(
    handoff_id: int,
    reason: str = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Rejeter un handoff avec motif"""
    # Logique de rejet
    import json
    from pathlib import Path
    handoffs_db = Path("data/handoffs.json")
    
    if handoffs_db.exists():
        with open(handoffs_db, 'r') as f:
            handoffs = json.load(f)
        
        for h in handoffs:
            if h.get("id") == handoff_id:
                h["status"] = "rejected"
                h["rejected_at"] = datetime.utcnow().isoformat()
                h["rejected_by"] = current_user.id
                h["rejection_reason"] = reason
                break
        
        with open(handoffs_db, 'w') as f:
            json.dump(handoffs, f, indent=2)
    
    return {"status": "rejected", "handoff_id": handoff_id, "reason": reason, "rejected_by": current_user.id}
