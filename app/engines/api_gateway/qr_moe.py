"""
SMART_AO V7 - qr_moe.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Matrice des Risques MOE - Analyse et gestion des risques Maîtrise d'Ouvrage
Source: ARCHITECTURE_V7_ENGINE.md §4.3
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import logging
from enum import Enum

from app.core.database import get_db
from app.core.auth import get_current_user, TokenData

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/qr-moe", tags=["Matrice Risques MOE"])


class RiskCategory(str, Enum):
    """Catégories de risques MOE."""
    TECHNIQUE = "technique"
    JURIDIQUE = "juridique"
    FINANCIER = "financier"
    ORGANISATIONNEL = "organisationnel"
    ENVIRONNEMENTAL = "environnemental"
    SOCIAL = "social"


class RiskLevel(str, Enum):
    """Niveaux de risque."""
    FAIBLE = "faible"
    MOYEN = "moyen"
    ELEVE = "eleve"
    CRITIQUE = "critique"


class RiskProbability(str, Enum):
    """Probabilités de risque."""
    TRES_FAIBLE = "tres_faible"
    FAIBLE = "faible"
    MOYENNE = "moyenne"
    FORTE = "forte"
    TRES_FORTE = "tres_forte"


class MOERiskItem(BaseModel):
    """Élément de risque MOE."""
    risk_id: str
    mission_id: str
    category: RiskCategory
    description: str
    probability: RiskProbability
    impact: int = Field(ge=1, le=10, description="Impact sur une échelle de 1 à 10")
    level: RiskLevel
    detection_method: Optional[str] = None
    mitigation_measures: List[str] = Field(default_factory=list)
    owner: Optional[str] = None
    detected_at: datetime
    due_date: Optional[datetime] = None
    status: str = Field(default="open", description="open, in_progress, mitigated, closed")


class MOERiskMatrix(BaseModel):
    """Matrice des risques MOE."""
    mission_id: str
    project_name: str
    risks: List[MOERiskItem]
    overall_risk_level: RiskLevel
    critical_risks_count: int
    high_risks_count: int
    medium_risks_count: int
    low_risks_count: int
    generated_at: datetime


class MOERiskAnalysisRequest(BaseModel):
    """Requête d'analyse des risques MOE."""
    mission_id: str
    project_data: Optional[Dict[str, Any]] = None
    scope: Optional[List[str]] = None
    include_mitigation: bool = Field(default=True)


class MOERiskAnalysisResult(BaseModel):
    """Résultat d'analyse des risques MOE."""
    mission_id: str
    matrix: MOERiskMatrix
    recommendations: List[str]
    action_plan: List[Dict[str, Any]]
    confidence_score: float = Field(ge=0.0, le=1.0)


class QRMoeGenerator:
    """Générateur de matrice des risques MOE."""
    
    RISK_CATEGORIES = [
        RiskCategory.TECHNIQUE,
        RiskCategory.JURIDIQUE,
        RiskCategory.FINANCIER,
        RiskCategory.ORGANISATIONNEL,
        RiskCategory.ENVIRONNEMENTAL,
        RiskCategory.SOCIAL
    ]
    
    def __init__(self):
        self.risk_database = self._build_risk_database()
    
    def _build_risk_database(self) -> Dict[str, List[Dict[str, Any]]]:
        """Base de données des risques standards MOE."""
        return {
            RiskCategory.TECHNIQUE.value: [
                {
                    "id": "TECH-001",
                    "description": "Retard dans la livraison des plans",
                    "base_probability": RiskProbability.MOYENNE,
                    "base_impact": 7,
                    "detection": "Suivi hebdomadaire des livrables",
                    "mitigation": ["Contrat avec pénalités de retard", "Plan de secours avec bureau d'études alternatif"]
                },
                {
                    "id": "TECH-002",
                    "description": "Non-conformité des matériaux livrés",
                    "base_probability": RiskProbability.FAIBLE,
                    "base_impact": 6,
                    "detection": "Contrôle qualité à réception",
                    "mitigation": ["Spécifications techniques détaillées", "Fournisseurs certifiés"]
                }
            ],
            RiskCategory.JURIDIQUE.value: [
                {
                    "id": "JUR-001",
                    "description": "Contentieux avec un fournisseur",
                    "base_probability": RiskProbability.FAIBLE,
                    "base_impact": 9,
                    "detection": "Audit juridique des contrats",
                    "mitigation": ["Clauses contractuelles protectrices", "Assurance responsabilité civile"]
                }
            ],
            RiskCategory.FINANCIER.value: [
                {
                    "id": "FIN-001",
                    "description": "Dépassement budgétaire",
                    "base_probability": RiskProbability.MOYENNE,
                    "base_impact": 8,
                    "detection": "Suivi mensuel des coûts",
                    "mitigation": ["Provisions pour aléas", "Révisions budgétaires régulières"]
                }
            ]
        }
    
    def calculate_risk_level(self, probability: RiskProbability, impact: int) -> RiskLevel:
        """Calcule le niveau de risque à partir de la probabilité et de l'impact."""
        impact_score = impact
        probability_score = {
            RiskProbability.TRES_FAIBLE: 1,
            RiskProbability.FAIBLE: 2,
            RiskProbability.MOYENNE: 3,
            RiskProbability.FORTE: 4,
            RiskProbability.TRES_FORTE: 5
        }.get(probability, 3)
        
        score = impact_score * probability_score
        
        if score >= 30:
            return RiskLevel.CRITIQUE
        elif score >= 20:
            return RiskLevel.ELEVE
        elif score >= 10:
            return RiskLevel.MOYEN
        else:
            return RiskLevel.FAIBLE
    
    def generate_risk_matrix(
        self,
        mission_id: str,
        project_name: str,
        custom_risks: Optional[List[Dict[str, Any]]] = None
    ) -> MOERiskMatrix:
        """Génère une matrice des risques pour une mission."""
        risks = []
        
        # Ajouter les risques standards
        for category, category_risks in self.risk_database.items():
            for risk_data in category_risks:
                risk_item = MOERiskItem(
                    risk_id=f"{mission_id}-{risk_data['id']}",
                    mission_id=mission_id,
                    category=RiskCategory(category),
                    description=risk_data["description"],
                    probability=risk_data["base_probability"],
                    impact=risk_data["base_impact"],
                    level=self.calculate_risk_level(
                        risk_data["base_probability"], 
                        risk_data["base_impact"]
                    ),
                    detection_method=risk_data["detection"],
                    mitigation_measures=risk_data["mitigation"],
                    owner=None,
                    detected_at=datetime.utcnow(),
                    due_date=datetime.utcnow() + timedelta(days=30),
                    status="open"
                )
                risks.append(risk_item)
        
        # Ajouter les risques personnalisés
        if custom_risks:
            for risk_data in custom_risks:
                risk_item = MOERiskItem(
                    risk_id=risk_data.get("risk_id", f"CUST-{len(risks)+1}"),
                    mission_id=mission_id,
                    category=RiskCategory(risk_data.get("category", RiskCategory.TECHNIQUE.value)),
                    description=risk_data["description"],
                    probability=RiskProbability(risk_data.get("probability", RiskProbability.MOYENNE.value)),
                    impact=risk_data.get("impact", 5),
                    level=self.calculate_risk_level(
                        RiskProbability(risk_data.get("probability", RiskProbability.MOYENNE.value)),
                        risk_data.get("impact", 5)
                    ),
                    detection_method=risk_data.get("detection_method"),
                    mitigation_measures=risk_data.get("mitigation_measures", []),
                    owner=risk_data.get("owner"),
                    detected_at=datetime.utcnow(),
                    due_date=risk_data.get("due_date"),
                    status=risk_data.get("status", "open")
                )
                risks.append(risk_item)
        
        # Calculer les statistiques
        critical_count = sum(1 for r in risks if r.level == RiskLevel.CRITIQUE)
        high_count = sum(1 for r in risks if r.level == RiskLevel.ELEVE)
        medium_count = sum(1 for r in risks if r.level == RiskLevel.MOYEN)
        low_count = sum(1 for r in risks if r.level == RiskLevel.FAIBLE)
        
        # Calculer le niveau global
        if critical_count > 0:
            overall_level = RiskLevel.CRITIQUE
        elif high_count > 2:
            overall_level = RiskLevel.ELEVE
        elif high_count > 0 or medium_count > 3:
            overall_level = RiskLevel.MOYEN
        else:
            overall_level = RiskLevel.FAIBLE
        
        return MOERiskMatrix(
            mission_id=mission_id,
            project_name=project_name,
            risks=risks,
            overall_risk_level=overall_level,
            critical_risks_count=critical_count,
            high_risks_count=high_count,
            medium_risks_count=medium_count,
            low_risks_count=low_count,
            generated_at=datetime.utcnow()
        )
    
    def analyze_risks(
        self,
        mission_id: str,
        request: MOERiskAnalysisRequest
    ) -> MOERiskAnalysisResult:
        """Analyse complète des risques MOE."""
        matrix = self.generate_risk_matrix(
            mission_id=mission_id,
            project_name=request.project_data.get("name", "Projet inconnu") if request.project_data else "Projet inconnu"
        )
        
        # Générer des recommandations
        recommendations = self._generate_recommendations(matrix)
        
        # Générer un plan d'action
        action_plan = self._generate_action_plan(matrix)
        
        return MOERiskAnalysisResult(
            mission_id=mission_id,
            matrix=matrix,
            recommendations=recommendations,
            action_plan=action_plan,
            confidence_score=0.95 if request.include_mitigation else 0.85
        )
    
    def _generate_recommendations(self, matrix: MOERiskMatrix) -> List[str]:
        """Génère des recommandations basées sur la matrice des risques."""
        recommendations = []
        
        if matrix.overall_risk_level == RiskLevel.CRITIQUE:
            recommendations.append("🔴 RISQUE CRITIQUE : Arrêt immédiat des opérations recommandé jusqu'à résolution")
            recommendations.append("Réunion d'urgence avec la direction et les parties prenantes")
        elif matrix.overall_risk_level == RiskLevel.ELEVE:
            recommendations.append("⚠️ RISQUE ÉLEVÉ : Surveillance renforcée requise")
            recommendations.append("Plan de mitigation prioritaire pour les risques critiques et élevés")
        
        if matrix.critical_risks_count > 0:
            recommendations.append(f"Traiter les {matrix.critical_risks_count} risque(s) critique(s) en priorité absolue")
        
        if matrix.high_risks_count > 3:
            recommendations.append(f"Réduire le nombre de risques élevés ({matrix.high_risks_count}) par des actions correctives")
        
        if matrix.medium_risks_count > 5:
            recommendations.append("Mettre en place des mesures préventives pour les risques moyens")
        
        return recommendations
    
    def _generate_action_plan(self, matrix: MOERiskMatrix) -> List[Dict[str, Any]]:
        """Génère un plan d'action basé sur la matrice des risques."""
        action_plan = []
        
        # Trier les risques par niveau (critique d'abord)
        sorted_risks = sorted(
            matrix.risks,
            key=lambda r: {
                RiskLevel.CRITIQUE: 0,
                RiskLevel.ELEVE: 1,
                RiskLevel.MOYEN: 2,
                RiskLevel.FAIBLE: 3
            }.get(r.level, 4)
        )
        
        for risk in sorted_risks:
            if risk.level in [RiskLevel.CRITIQUE, RiskLevel.ELEVE]:
                action_plan.append({
                    "risk_id": risk.risk_id,
                    "description": risk.description,
                    "category": risk.category.value,
                    "level": risk.level.value,
                    "action": "Implémenter les mesures de mitigation",
                    "owner": risk.owner or "À assigner",
                    "priority": "high" if risk.level == RiskLevel.CRITIQUE else "medium",
                    "due_date": risk.due_date.isoformat() if risk.due_date else None,
                    "mitigation_measures": risk.mitigation_measures
                })
        
        return action_plan


generator = QRMoeGenerator()


@router.post("/analyze", response_model=MOERiskAnalysisResult)
async def analyze_moe_risks(
    request: MOERiskAnalysisRequest,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyse les risques MOE pour une mission.
    
    Effectue une analyse complète des risques de Maîtrise d'Ouvrage
    et génère une matrice des risques avec recommandations.
    """
    logger.info(f"Analyse risques MOE pour mission {request.mission_id} par {current_user.user_id}")
    
    result = generator.analyze_risks(request.mission_id, request)
    
    return result


@router.get("/matrix/{mission_id}", response_model=MOERiskMatrix)
async def get_risk_matrix(
    mission_id: str,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère la matrice des risques MOE pour une mission.
    """
    logger.info(f"Récupération matrice risques MOE pour mission {mission_id} par {current_user.user_id}")
    
    matrix = generator.generate_risk_matrix(
        mission_id=mission_id,
        project_name=f"Projet-{mission_id}"
    )
    
    return matrix


@router.post("/matrix", response_model=MOERiskMatrix)
async def create_risk_matrix(
    mission_id: str,
    project_name: str,
    custom_risks: Optional[List[Dict[str, Any]]] = None,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Crée ou met à jour une matrice des risques MOE.
    """
    logger.info(f"Création matrice risques MOE pour {project_name} ({mission_id}) par {current_user.user_id}")
    
    matrix = generator.generate_risk_matrix(
        mission_id=mission_id,
        project_name=project_name,
        custom_risks=custom_risks
    )
    
    return matrix


@router.get("/levels/{mission_id}", response_model=Dict[str, Any])
async def get_risk_levels(
    mission_id: str,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère les niveaux de risque par catégorie pour une mission.
    """
    logger.info(f"Niveaux de risque pour mission {mission_id} par {current_user.user_id}")
    
    matrix = generator.generate_risk_matrix(
        mission_id=mission_id,
        project_name=f"Projet-{mission_id}"
    )
    
    levels_by_category = {}
    for category in generator.RISK_CATEGORIES:
        category_risks = [r for r in matrix.risks if r.category == category]
        if category_risks:
            max_level = max(
                category_risks,
                key=lambda r: {
                    RiskLevel.CRITIQUE: 0,
                    RiskLevel.ELEVE: 1,
                    RiskLevel.MOYEN: 2,
                    RiskLevel.FAIBLE: 3
                }.get(r.level, 4)
            )
            levels_by_category[category.value] = {
                "max_level": max_level.level.value,
                "risk_count": len(category_risks),
                "risks": [
                    {
                        "risk_id": r.risk_id,
                        "description": r.description,
                        "level": r.level.value,
                        "probability": r.probability.value,
                        "impact": r.impact
                    }
                    for r in category_risks
                ]
            }
    
    return {
        "mission_id": mission_id,
        "overall_level": matrix.overall_risk_level.value,
        "levels_by_category": levels_by_category,
        "generated_at": matrix.generated_at.isoformat()
    }


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "qr_moe",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

