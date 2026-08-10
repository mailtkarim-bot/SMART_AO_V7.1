"""
SMART_AO V7 - risques.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Risques Schemas - Schémas Pydantic pour la gestion des risques
Source: ARCHITECTURE_V7_ENGINE.md §3.2
"""

from datetime import date, datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class RisqueType(str, Enum):
    """Types de risques."""
    TECHNIQUE = "technique"
    FINANCIER = "financier"
    REGLEMENTAIRE = "reglementaire"
    SECURITE = "securite"
    ENVIRONNEMENTAL = "environnemental"
    ORGANISATIONNEL = "organisationnel"
    JURIDIQUE = "juridique"


class RisqueNiveau(str, Enum):
    """Niveaux de risque."""
    FAIBLE = "faible"
    MOYEN = "moyen"
    ELEVE = "eleve"
    CRITIQUE = "critique"


class RisqueStatut(str, Enum):
    """Statuts des risques."""
    IDENTIFIE = "identifie"
    ANALYSE = "analyse"
    TRAITE = "traite"
    SURVEILLE = "surveille"
    FERME = "ferme"
    REOUVERT = "reouvert"


class RisqueBase(BaseModel):
    """Schéma de base pour un risque."""
    code: str = Field(..., min_length=1, max_length=50, description="Code unique du risque")
    titre: str = Field(..., min_length=1, max_length=200, description="Titre du risque")
    description: Optional[str] = Field(default=None, description="Description détaillée")
    
    type: RisqueType = Field(default=RisqueType.TECHNIQUE, description="Type de risque")
    niveau: RisqueNiveau = Field(default=RisqueNiveau.MOYEN, description="Niveau de criticité")
    statut: RisqueStatut = Field(default=RisqueStatut.IDENTIFIE, description="Statut actuel")
    
    probabilite: float = Field(default=0.5, ge=0.0, le=1.0, description="Probabilité d'occurrence (0.0-1.0)")
    impact: float = Field(default=0.0, ge=0.0, description="Impact potentiel (en euros)")
    
    mitigation: Optional[str] = Field(default=None, description="Mesures de mitigation")
    responsable: Optional[str] = Field(default=None, max_length=100, description="Responsable du suivi")


class RisqueCreate(RisqueBase):
    """Schéma pour la création d'un risque."""
    mission_id: Optional[int] = Field(default=None, description="ID de la mission")
    lot_id: Optional[int] = Field(default=None, description="ID du lot")
    
    date_identification: Optional[date] = Field(default=None, description="Date d'identification")
    date_echeance: Optional[date] = Field(default=None, description="Date limite pour action")
    
    est_actif: bool = Field(default=True, description="Indique si le risque est actif")
    est_accepté: bool = Field(default=False, description="Indique si le risque est accepté")
    
    plan_action: Optional[List[dict]] = Field(default=None, description="Plan d'action détaillé")
    ventes_liees: Optional[List[int]] = Field(default=None, description="IDs des ventes liées")
    documents: Optional[List[str]] = Field(default=None, description="Liste de documents")
    metadata: Optional[dict] = Field(default=None, description="Métadonnées")


class RisqueUpdate(BaseModel):
    """Schéma pour la mise à jour d'un risque."""
    code: Optional[str] = Field(default=None, min_length=1, max_length=50)
    titre: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    
    type: Optional[RisqueType] = None
    niveau: Optional[RisqueNiveau] = None
    statut: Optional[RisqueStatut] = None
    
    probabilite: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    impact: Optional[float] = Field(default=None, ge=0.0)
    
    mitigation: Optional[str] = None
    responsable: Optional[str] = Field(default=None, max_length=100)
    
    mission_id: Optional[int] = None
    lot_id: Optional[int] = None
    
    date_identification: Optional[date] = None
    date_echeance: Optional[date] = None
    date_fermeture: Optional[date] = None
    
    est_actif: Optional[bool] = None
    est_accepté: Optional[bool] = None
    
    plan_action: Optional[List[dict]] = None
    ventes_liees: Optional[List[int]] = None
    documents: Optional[List[str]] = None
    metadata: Optional[dict] = None


class RisqueResponse(RisqueBase):
    """Schéma de réponse pour un risque."""
    id: int = Field(..., description="Identifiant unique")
    mission_id: Optional[int] = Field(default=None, description="ID de la mission")
    lot_id: Optional[int] = Field(default=None, description="ID du lot")
    
    date_identification: date = Field(..., description="Date d'identification")
    date_echeance: Optional[date] = Field(default=None, description="Date limite pour action")
    date_fermeture: Optional[date] = Field(default=None, description="Date de fermeture")
    
    est_actif: bool = Field(..., description="Indique si le risque est actif")
    est_accepté: bool = Field(..., description="Indique si le risque est accepté")
    
    score: float = Field(default=0.0, description="Score de risque")
    score_calcule: float = Field(..., description="Score calculé")
    
    est_urgent: bool = Field(..., description="Indique si le risque est urgent")
    est_ferme: bool = Field(..., description="Indique si le risque est fermé")
    jours_restants: Optional[int] = Field(default=None, description="Jours restants avant échéance")
    
    plan_action: Optional[List[dict]] = Field(default=None, description="Plan d'action")
    ventes_liees: Optional[List[int]] = Field(default=None, description="Ventes liées")
    documents: Optional[List[str]] = Field(default=None, description="Documents associés")
    metadata: Optional[dict] = Field(default=None, description="Métadonnées")
    
    created_at: datetime = Field(..., description="Date de création")
    updated_at: datetime = Field(..., description="Date de mise à jour")
    
    model_config = ConfigDict(from_attributes=True, json_schema_extra={
        "example": {
            "id": 1,
            "code": "RISQUE_SOL_001",
            "titre": "Sol instable",
            "description": "Présence de sol argileux nécessitant des fondations spécifiques",
            "type": "technique",
            "niveau": "eleve",
            "statut": "analyse",
            "probabilite": 0.3,
            "impact": 500000,
            "score_calcule": 0.15,
            "mitigation": "Étude géotechnique approfondie",
            "responsable": "Jean Dupont",
            "est_actif": True,
            "est_urgent": False
        }
    })


class RisqueListResponse(BaseModel):
    """Schéma de liste de risques."""
    risques: List[RisqueResponse] = Field(..., description="Liste des risques")
    total: int = Field(..., description="Nombre total de risques")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "risques": [],
            "total": 0
        }
    })


class RisqueCategorieBase(BaseModel):
    """Schéma de base pour une catégorie de risques."""
    code: str = Field(..., min_length=1, max_length=50, description="Code unique")
    nom: str = Field(..., min_length=1, max_length=100, description="Nom de la catégorie")
    description: Optional[str] = Field(default=None, description="Description")
    parent_id: Optional[int] = Field(default=None, description="ID de la catégorie parente")
    poids: float = Field(default=1.0, ge=0.0, description="Poids de la catégorie")
    est_actif: bool = Field(default=True, description="Indique si la catégorie est active")


class RisqueCategorieResponse(RisqueCategorieBase):
    """Schéma de réponse pour une catégorie."""
    id: int = Field(..., description="Identifiant unique")
    created_at: datetime = Field(..., description="Date de création")
    updated_at: datetime = Field(..., description="Date de mise à jour")
    
    model_config = ConfigDict(from_attributes=True)


class RisqueAnalyseBase(BaseModel):
    """Schéma de base pour une analyse de risques."""
    code: str = Field(..., min_length=1, max_length=50, description="Code unique")
    nom: str = Field(..., min_length=1, max_length=200, description="Nom de l'analyse")
    
    nb_risques_totaux: int = Field(default=0, description="Nombre total de risques")
    nb_risques_critiques: int = Field(default=0, description="Nombre de risques critiques")
    nb_risques_eleves: int = Field(default=0, description="Nombre de risques élevés")
    nb_risques_moyens: int = Field(default=0, description="Nombre de risques moyens")
    nb_risques_faibles: int = Field(default=0, description="Nombre de risques faibles")
    
    score_global: float = Field(default=0.0, ge=0.0, le=1.0, description="Score global")
    niveau_global: str = Field(..., description="Niveau global")
    
    recommandations: Optional[List[str]] = Field(default=None, description="Recommandations")
    date_analyse: date = Field(..., description="Date de l'analyse")


class RisqueAnalyseResponse(RisqueAnalyseBase):
    """Schéma de réponse pour une analyse."""
    id: int = Field(..., description="Identifiant unique")
    mission_id: Optional[int] = Field(default=None, description="ID de la mission")
    metadata: Optional[dict] = Field(default=None, description="Métadonnées")
    created_at: datetime = Field(..., description="Date de création")
    updated_at: datetime = Field(..., description="Date de mise à jour")
    
    model_config = ConfigDict(from_attributes=True)


class RisqueFilter(BaseModel):
    """Schéma de filtrage des risques."""
    mission_id: Optional[int] = Field(default=None, description="Filtrer par mission")
    lot_id: Optional[int] = Field(default=None, description="Filtrer par lot")
    type: Optional[RisqueType] = Field(default=None, description="Filtrer par type")
    niveau: Optional[RisqueNiveau] = Field(default=None, description="Filtrer par niveau")
    statut: Optional[RisqueStatut] = Field(default=None, description="Filtrer par statut")
    est_actif: Optional[bool] = Field(default=None, description="Filtrer par activité")
    est_urgent: Optional[bool] = Field(default=None, description="Filtrer par urgence")
    responsable: Optional[str] = Field(default=None, description="Filtrer par responsable")
    
    page: int = Field(default=1, ge=1, description="Numéro de page")
    per_page: int = Field(default=50, ge=1, le=1000, description="Éléments par page")


__all__ = [
    'RisqueType', 'RisqueNiveau', 'RisqueStatut',
    'RisqueBase', 'RisqueCreate', 'RisqueUpdate', 'RisqueResponse',
    'RisqueListResponse', 'RisqueCategorieBase', 'RisqueCategorieResponse',
    'RisqueAnalyseBase', 'RisqueAnalyseResponse', 'RisqueFilter'
]

