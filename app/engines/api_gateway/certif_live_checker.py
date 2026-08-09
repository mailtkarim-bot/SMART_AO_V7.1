"""
SMART_AO V7 - certif_live_checker.py
=======================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Certification Live Checker - Vérification en temps réel des certifications
Source: ARCHITECTURE_V7_ENGINE.md §4.3
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import logging

from app.core.database import get_db
from app.core.auth import get_current_user, TokenData

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/certifications", tags=["Certification Live Checker"])


class CertifStatus(BaseModel):
    """Statut d'une certification."""
    id: int
    type: str
    numero: str
    statut: str
    est_valide: bool
    jours_restants: Optional[int]
    date_expiration: Optional[date]
    alerte: Optional[str] = None


class CertifBulkCheckResponse(BaseModel):
    """Résultat du check en masse des certifications."""
    total: int
    valides: int
    expirees: int
    bientot_expirees: List[CertifStatus]
    critiques: List[CertifStatus]
    timestamp: datetime


@router.get("/check/all", response_model=CertifBulkCheckResponse)
async def check_all_certifications(
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Vérifie toutes les certifications et retourne leur statut.
    """
    logger.info(f"Check toutes certifications par {current_user.email}")
    
    from app.models.certifications import Certification, CertificationStatus, CertificationType
    
    result = await db.execute(select(Certification))
    certifications = result.scalars().all()
    
    valides = []
    expirees = []
    bientot_expirees = []
    critiques = []
    
    today = date.today()
    
    for cert in certifications:
        cert_status = CertifStatus(
            id=cert.id,
            type=cert.type,
            numero=cert.numero,
            statut=cert.statut,
            est_valide=cert.est_valide,
            jours_restants=cert.jours_restants,
            date_expiration=cert.date_expiration
        )
        
        if cert.est_valide:
            valides.append(cert_status)
        elif cert.statut == CertificationStatus.EXPIREE.value:
            expirees.append(cert_status)
        elif cert.est_bientot_expirée:
            bientot_expirees.append(cert_status)
        
        if cert.est_critique and not cert.est_valide:
            critiques.append(cert_status)
    
    return CertifBulkCheckResponse(
        total=len(certifications),
        valides=len(valides),
        expirees=len(expirees),
        bientot_expirees=bientot_expirees,
        critiques=critiques,
        timestamp=datetime.utcnow()
    )


@router.get("/check/{certif_id}", response_model=CertifStatus)
async def check_certification(
    certif_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Vérifie le statut d'une certification spécifique.
    """
    from app.models.certifications import Certification
    
    result = await db.execute(select(Certification).where(Certification.id == certif_id))
    cert = result.scalar_one_or_none()
    
    if not cert:
        raise HTTPException(status_code=404, detail=f"Certification {certif_id} non trouvée")
    
    alerte = None
    if not cert.est_valide:
        if cert.statut == "expiree":
            alerte = "CERTIFICATION EXPIREE"
        elif cert.est_bientot_expirée:
            alerte = f"CERTIFICATION EXPIRE DANS {cert.jours_restants} JOURS"
    
    return CertifStatus(
        id=cert.id,
        type=cert.type,
        numero=cert.numero,
        statut=cert.statut,
        est_valide=cert.est_valide,
        jours_restants=cert.jours_restants,
        date_expiration=cert.date_expiration,
        alerte=alerte
    )


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "certif_live_checker", "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat()}
