"""
SMART_AO V7 - pab_detector.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Détection PAB avancée - Détection des Pénalités Administratives de Base
Source: ARCHITECTURE_V7_ENGINE.md §4.3
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime, timedelta
import logging
import re

from app.core.database import get_db
from app.core.auth import get_current_user, TokenData

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/pab", tags=["PAB Detector"])


class PABType(str, Enum):
    """Types de PAB (Pénalités Administratives de Base)."""
    RETARD = "retard"
    NON_CONFORMITE = "non_conformite"
    DEFFAUT_QUALITE = "defaut_qualite"
    MANQUEMENT_SECURITE = "manquement_securite"
    ABSENCE_DOCUMENT = "absence_document"


class PABSeverity(str, Enum):
    """Sévérité des PAB."""
    FAIBLE = "faible"
    MOYENNE = "moyenne"
    ELEVEE = "elevee"
    CRITIQUE = "critique"


class PABDetectionResult(BaseModel):
    """Résultat de détection PAB."""
    mission_id: str
    document_id: Optional[str] = None
    pab_type: PABType
    severity: PABSeverity
    description: str
    detected_in: str  # Nom du document ou section
    location: Optional[str] = None  # Emplacement précis dans le document
    evidence: Optional[str] = None
    potential_penalty: float = Field(ge=0.0)
    detected_at: datetime
    confidence: float = Field(ge=0.0, le=1.0)


class PABAnalysisRequest(BaseModel):
    """Requête d'analyse PAB."""
    mission_id: str
    document_text: str
    document_type: Optional[str] = None
    document_id: Optional[str] = None
    threshold: Optional[float] = Field(default=0.85, ge=0.0, le=1.0)


class PABAnalysisResult(BaseModel):
    """Résultat d'analyse PAB."""
    mission_id: str
    document_id: Optional[str] = None
    document_type: Optional[str] = None
    total_pabs: int
    pabs: List[PABDetectionResult]
    summary: Dict[str, Any]
    recommendations: List[str]
    analyzed_at: datetime


class PABPattern(BaseModel):
    """Motif de détection PAB."""
    pattern_id: str
    pab_type: PABType
    regex_pattern: str
    severity: PABSeverity
    description: str
    penalty_multiplier: float


class PABDetector:
    """Détecteur de Pénalités Administratives de Base."""
    
    def __init__(self):
        self.patterns = self._build_pab_patterns()
    
    def _build_pab_patterns(self) -> List[PABPattern]:
        """Construit la liste des motifs de détection PAB."""
        return [
            PABPattern(
                pattern_id="PAB-RETARD-001",
                pab_type=PABType.RETARD,
                regex_pattern=r'(?i)(retard|délai\s*dépassé|non\s*respect\s*du\s*calendrier|penalité\s*de\s*retard)',
                severity=PABSeverity.MOYENNE,
                description="Détection de mentions de retard dans les documents",
                penalty_multiplier=1.5
            ),
            PABPattern(
                pattern_id="PAB-RETARD-002",
                pab_type=PABType.RETARD,
                regex_pattern=r'(?i)(j[+\-]\d{1,3}|\d{1,3}\s*jours\s*de\s*retard)',
                severity=PABSeverity.ELEVEE,
                description="Détection de délais de retard explicites",
                penalty_multiplier=2.0
            ),
            PABPattern(
                pattern_id="PAB-CONFORMITE-001",
                pab_type=PABType.NON_CONFORMITE,
                regex_pattern=r'(?i)(non\s*conforme|non\s*conformité|non\s*respect\s*des\s*normes|écart\s*réglementaire)',
                severity=PABSeverity.ELEVEE,
                description="Détection de non-conformité réglementaire",
                penalty_multiplier=2.5
            ),
            PABPattern(
                pattern_id="PAB-QUALITE-001",
                pab_type=PABType.DEFFAUT_QUALITE,
                regex_pattern=r'(?i)(défaut\s*de\s*qualité|malfaçon|non\s*conforme\s*aux\s*exigences)',
                severity=PABSeverity.ELEVEE,
                description="Détection de défauts de qualité",
                penalty_multiplier=2.0
            ),
            PABPattern(
                pattern_id="PAB-SECURITE-001",
                pab_type=PABType.MANQUEMENT_SECURITE,
                regex_pattern=r'(?i)(manquement\s*à\s*la\s*sécurité|non\s*respect\s*des\s*règles\s*de\s*sécurité)',
                severity=PABSeverity.CRITIQUE,
                description="Détection de manquements à la sécurité",
                penalty_multiplier=3.0
            ),
            PABPattern(
                pattern_id="PAB-DOCUMENT-001",
                pab_type=PABType.ABSENCE_DOCUMENT,
                regex_pattern=r'(?i)(document\s*manquant|pièce\s*justificative\s*absente|attestation\s*non\s*fournie)',
                severity=PABSeverity.MOYENNE,
                description="Détection d'absence de documents requis",
                penalty_multiplier=1.0
            ),
            PABPattern(
                pattern_id="PAB-PENALETE-001",
                pab_type=PABType.RETARD,
                regex_pattern=r'(?i)(pénalité\s*[àa]\s*[0-9\s]+%|amende\s*[àa]\s*[0-9\s]+%)',
                severity=PABSeverity.ELEVEE,
                description="Détection de mentions de pénalités en pourcentage",
                penalty_multiplier=2.0
            )
        ]
    
    def detect_pabs(
        self,
        mission_id: str,
        text: str,
        document_id: Optional[str] = None,
        document_type: Optional[str] = None,
        threshold: float = 0.85
    ) -> PABAnalysisResult:
        """Détecte les PAB dans un texte."""
        detected_pabs = []
        
        for pattern in self.patterns:
            matches = list(re.finditer(pattern.regex_pattern, text))
            
            for match in matches:
                start, end = match.span()
                matched_text = text[start:end]
                
                # Calculer la confiance
                confidence = min(1.0, len(matched_text) / 20.0 + 0.5)
                
                if confidence >= threshold:
                    # Calculer la pénalité potentielle
                    base_penalty = len(matched_text) * 100.0
                    potential_penalty = base_penalty * pattern.penalty_multiplier
                    
                    detection = PABDetectionResult(
                        mission_id=mission_id,
                        document_id=document_id,
                        pab_type=pattern.pab_type,
                        severity=pattern.severity,
                        description=pattern.description,
                        detected_in=document_type or "document",
                        location=f"Position {start}-{end}",
                        evidence=matched_text[:100],
                        potential_penalty=round(potential_penalty, 2),
                        detected_at=datetime.utcnow(),
                        confidence=round(confidence, 2)
                    )
                    detected_pabs.append(detection)
        
        # Calculer le résumé
        pabs_by_type = {}
        for pab in detected_pabs:
            pabs_by_type[pab.pab_type.value] = pabs_by_type.get(pab.pab_type.value, 0) + 1
        
        pabs_by_severity = {}
        for pab in detected_pabs:
            pabs_by_severity[pab.severity.value] = pabs_by_severity.get(pab.severity.value, 0) + 1
        
        total_penalty = sum(pab.potential_penalty for pab in detected_pabs)
        avg_confidence = sum(pab.confidence for pab in detected_pabs) / len(detected_pabs) if detected_pabs else 0.0
        
        summary = {
            "by_type": pabs_by_type,
            "by_severity": pabs_by_severity,
            "total_potential_penalty": round(total_penalty, 2),
            "average_confidence": round(avg_confidence, 2),
            "high_confidence_count": sum(1 for pab in detected_pabs if pab.confidence >= 0.95)
        }
        
        # Générer des recommandations
        recommendations = self._generate_recommendations(detected_pabs, summary)
        
        return PABAnalysisResult(
            mission_id=mission_id,
            document_id=document_id,
            document_type=document_type,
            total_pabs=len(detected_pabs),
            pabs=detected_pabs,
            summary=summary,
            recommendations=recommendations,
            analyzed_at=datetime.utcnow()
        )
    
    def _generate_recommendations(self, pabs: List[PABDetectionResult], summary: Dict[str, Any]) -> List[str]:
        """Génère des recommandations basées sur les PAB détectées."""
        recommendations = []
        
        if not pabs:
            recommendations.append("✅ Aucun PAB détecté - document conforme")
            return recommendations
        
        if summary["by_severity"].get("critique", 0) > 0:
            recommendations.append("🔴 PAB CRITIQUE détecté - Intervention immédiate requise")
            recommendations.append("Notifier la direction et les parties prenantes")
        
        if summary["by_severity"].get("elevee", 0) > 3:
            recommendations.append("⚠️ Plusieurs PAB de sévérité élevée - Action corrective prioritaire")
        
        if summary["by_type"].get("retard", 0) > 0:
            recommendations.append("Vérifier le planning et les délais contractuels")
            recommendations.append("Mettre à jour le planning si nécessaire")
        
        if summary["by_type"].get("non_conformite", 0) > 0:
            recommendations.append("Auditer la conformité réglementaire")
            recommendations.append("Corriger les écarts identifiés")
        
        if summary["by_type"].get("defaut_qualite", 0) > 0:
            recommendations.append("Renforcer le contrôle qualité")
            recommendations.append("Vérifier les processus de production")
        
        if summary["by_type"].get("manquement_securite", 0) > 0:
            recommendations.append("🔴 ARRÊT DES TRAVAUX jusqu'à résolution des manquements sécurité")
            recommendations.append("Audit sécurité complet requis")
        
        if summary["by_type"].get("absence_document", 0) > 0:
            recommendations.append("Fournir les documents manquants sous 24-48h")
        
        if summary["total_potential_penalty"] > 10000:
            recommendations.append(f"⚠️ Pénalité potentielle élevée: {summary['total_potential_penalty']:.0f} € - Négociation requise")
        
        return recommendations


detector = PABDetector()


@router.post("/detect", response_model=PABAnalysisResult)
async def detect_pabs(
    request: PABAnalysisRequest,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Détecte les PAB dans un document.
    
    Analyse le texte fourni à la recherche de Pénalités Administratives de Base
    et retourne une liste des PAB détectées avec leur sévérité et recommandations.
    """
    logger.info(f"Détection PAB pour mission {request.mission_id} par {current_user.user_id}")
    
    result = detector.detect_pabs(
        mission_id=request.mission_id,
        text=request.document_text,
        document_id=request.document_id,
        document_type=request.document_type,
        threshold=request.threshold
    )
    
    return result


@router.get("/history/{mission_id}", response_model=List[PABAnalysisResult])
async def get_pab_history(
    mission_id: str,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère l'historique des analyses PAB pour une mission.
    """
    logger.info(f"Historique PAB pour mission {mission_id} par {current_user.user_id}")
    
    return []


@router.get("/patterns", response_model=List[PABPattern])
async def list_pab_patterns(
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Liste tous les motifs de détection PAB.
    """
    logger.info(f"Liste des motifs PAB par {current_user.user_id}")
    
    return detector.patterns


@router.post("/patterns/{pattern_id}/test", response_model=List[Dict[str, Any]])
async def test_pab_pattern(
    pattern_id: str,
    test_text: str,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Teste un motif PAB spécifique sur un texte.
    """
    logger.info(f"Test motif PAB {pattern_id} par {current_user.user_id}")
    
    pattern = next((p for p in detector.patterns if p.pattern_id == pattern_id), None)
    
    if not pattern:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Motif PAB {pattern_id} non trouvé"
        )
    
    matches = list(re.finditer(pattern.regex_pattern, test_text))
    
    return [
        {
            "match": test_text[start:end],
            "start": start,
            "end": end
        }
        for match in matches
        for start, end in [match.span()]
    ]


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "pab_detector",
        "version": "1.0.0",
        "patterns_count": len(detector.patterns),
        "timestamp": datetime.utcnow().isoformat()
    }

