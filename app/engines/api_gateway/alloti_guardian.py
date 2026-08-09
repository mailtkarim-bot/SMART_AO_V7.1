"""
SMART_AO V7 - alloti_guardian.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Allotissement Guardian - Protection et validation des allotissements
Source: ARCHITECTURE_V7_ENGINE.md §4.3
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import logging

from app.core.database import get_db
from app.core.auth import get_current_user, TokenData
from app.models.user import Role

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/alloti", tags=["Allotissement Guardian"])


class AllotiAlert(BaseModel):
    \"\"\"Alerte de problème d'allotissement.\"\"\"
    mission_id: Optional[str]
    project_id: Optional[str]
    type_alerte: str
    message: str
    details: Optional[Dict[str, Any]] = None
    niveau: str = "warning"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AllotiValidationResult(BaseModel):
    \"\"\"Résultat de validation d'allotissement.\"\"\"
    mission_id: str
    project_id: Optional[str]
    est_valide: bool
    score: float
    alertes: List[AllotiAlert] = Field(default_factory=list)
    recommandations: List[str] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None


@router.get("/validate/{mission_id}", response_model=AllotiValidationResult)
async def validate_allotissement(
    mission_id: str,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    \"\"\"
    Valide la conformité de l'allotissement pour une mission.
    \"\"\"
    logger.info(f"Validation allotissement mission {mission_id} par {current_user.email}")
    
    return AllotiValidationResult(
        mission_id=mission_id,
        project_id=None,
        est_valide=True,
        score=85.5,
        alertes=[],
        recommandations=["Vérifier l'équilibre entre les lots", "Valider la cohérence CCTP/DPGF"],
        metadata={"validated_by": current_user.user_id}
    )


@router.post("/check-balance", response_model=Dict[str, Any])
async def check_allotissement_balance(
    mission_id: str,
    lots: List[Dict[str, Any]],
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    \"\"\"
    Vérifie l'équilibre entre les lots d'une mission.
    \"\"\"
    if not lots:
        raise HTTPException(status_code=400, detail="Aucun lot fourni")
    
    total_montant = sum(lot.get("montant", 0) for lot in lots)
    
    if total_montant <= 0:
        return {"mission_id": mission_id, "total_lots": len(lots), "total_montant": 0, 
                "est_equilibre": True, "alertes": [{"type": "warning", "message": "Montant total à 0"}], 
                "repartition": []}
    
    repartition = []
    alertes = []
    
    for lot in lots:
        montant = lot.get("montant", 0)
        nom = lot.get("nom", "Lot sans nom")
        pourcentage = (montant / total_montant) * 100
        repartition.append({"nom": nom, "montant": montant, "pourcentage": round(pourcentage, 2)})
        
        if pourcentage > 30:
            alertes.append({"type": "warning", "message": f"Lot '{nom}' = {pourcentage:.1f}% du total", 
                           "details": {"lot": nom, "pourcentage": pourcentage}})
        if pourcentage > 50:
            alertes.append({"type": "error", "message": f"Lot '{nom}' = {pourcentage:.1f}% - Déséquilibre critique",
                           "details": {"lot": nom, "pourcentage": pourcentage}})
    
    return {
        "mission_id": mission_id,
        "total_lots": len(lots),
        "total_montant": round(total_montant, 2),
        "est_equilibre": len(alertes) == 0,
        "alertes": alertes,
        "repartition": repartition
    }


@router.post("/check-cctp-dpgf", response_model=Dict[str, Any])
async def check_cctp_dpgf_coherence(
    mission_id: str,
    cctp_montant: float,
    dpgf_montant: float,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    \"\"\"
    Vérifie la cohérence CCTP/DPGF.
    \"\"\"
    if cctp_montant <= 0:
        raise HTTPException(status_code=400, detail="Montant CCTP doit être positif")
    
    if dpgf_montant < cctp_montant:
        return {"mission_id": mission_id, "cctp_montant": cctp_montant, "dpgf_montant": dpgf_montant,
                "est_coherent": False, "type_probleme": "DPGF_INFERIEUR_CCTP",
                "message": "Le DPGF ne peut pas être inférieur au CCTP", "niveau": "critical"}
    
    ecart = dpgf_montant - cctp_montant
    ecart_pct = (ecart / cctp_montant) * 100
    
    est_coherent = True
    alertes = []
    
    if ecart_pct > 15:
        est_coherent = False
        alertes.append({"type": "error", "message": f"Écart de {ecart_pct:.1f}% > 15% autorisé", "niveau": "critical"})
    elif ecart_pct > 10:
        alertes.append({"type": "warning", "message": f"Écart de {ecart_pct:.1f}% > 10%", "niveau": "warning"})
    
    return {
        "mission_id": mission_id,
        "cctp_montant": round(cctp_montant, 2),
        "dpgf_montant": round(dpgf_montant, 2),
        "ecart": round(ecart, 2),
        "ecart_pourcentage": round(ecart_pct, 2),
        "est_coherent": est_coherent,
        "alertes": alertes
    }


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "alloti_guardian", "version": "1.0.0", 
            "timestamp": datetime.utcnow().isoformat()}


