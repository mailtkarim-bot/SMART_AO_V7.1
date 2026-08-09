"""
SMART_AO V7 - traps.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Traps Schemas - Schémas Pydantic pour la détection des pièges et anomalies
Source: ARCHITECTURE_V7_ENGINE.md §3.2
"""

from datetime import date, datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class TrapType(str, Enum):
    """Types de pièges (traps)."""
    INCOHERENCE_DONNEES = "incoherence_donnees"
    CONFLIT_REGLES = "conflit_regles"
    DEPASSEMENT_BUDGETAIRE = "depassement_budgetaire"
    RETARD_PLANNING = "retard_planning"
    NON_CONFORMITE = "non_conformite"
    RISQUE_JURIDIQUE = "risque_juridique"
    RISQUE_TECHNIQUE = "risque_technique"
    RISQUE_FINANCIER = "risque_financier"
    ANOMALIE_DOCUMENT = "anomalie_document"
    DOUBLON = "doublon"
    MANQUE_INFORMATION = "manque_information"
    INCONSISTANCE_METIER = "inconsistance_metier"


class TrapCategory(str, Enum):
    """Catégories de pièges."""
    CHIFFRAGE = "chiffrage"
    PLANNING = "planning"
    DOCUMENTATION = "documentation"
    REGLEMENTAIRE = "reglementaire"
    TECHNIQUE = "technique"
    FINANCIER = "financier"
    JURIDIQUE = "juridique"
    ORGANISATIONNEL = "organisationnel"


class TrapSeverity(str, Enum):
    """Niveaux de sévérité des pièges."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class TrapStatus(str, Enum):
    """Statuts des pièges."""
    DETECTE = "detecte"
    ANALYSE = "analyse"
    VALIDE = "valide"
    Faux_POSITIF = "faux_positif"
    IGNORE = "ignore"
    CORRIGE = "corrige"
    FERME = "ferme"


class TrapBase(BaseModel):
    """Schéma de base pour un piège (trap)."""
    code: str = Field(..., min_length=1, max_length=50, description="Code unique du piège")
    titre: str = Field(..., min_length=1, max_length=200, description="Titre du piège")
    description: Optional[str] = Field(default=None, description="Description détaillée")
    
    type: TrapType = Field(default=TrapType.INCOHERENCE_DONNEES, description="Type de piège")
    categorie: TrapCategory = Field(default=TrapCategory.CHIFFRAGE, description="Catégorie")
    severite: TrapSeverity = Field(default=TrapSeverity.WARNING, description="Niveau de sévérité")
    statut: TrapStatus = Field(default=TrapStatus.DETECTE, description="Statut actuel")
    
    # Identification de la source
    entite_type: str = Field(..., max_length=50, description="Type de l'entité source")
    entite_id: int = Field(..., description="ID de l'entité source")
    
    # Localisation
    mission_id: Optional[int] = Field(default=None, description="ID de la mission concernée")
    lot_id: Optional[int] = Field(default=None, description="ID du lot concerné")
    projet_id: Optional[int] = Field(default=None, description="ID du projet concerné")


class TrapCreate(TrapBase):
    """Schéma pour la création d'un piège."""
    entreprise_id: Optional[int] = Field(default=1, description="ID de l'entreprise")
    
    date_detection: Optional[datetime] = Field(default=None, description="Date et heure de détection")
    
    # Contexte
    valeurs_anormales: Optional[List[dict]] = Field(default=None, description="Liste des valeurs anormales détectées")
    regles_violees: Optional[List[str]] = Field(default=None, description="Liste des règles violées")
    
    # Impact
    impact_estime: Optional[float] = Field(default=None, ge=0.0, description="Impact estimé")
    probabilite: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Probabilité d'occurrence")
    
    # Détection
    methode_detection: Optional[str] = Field(default=None, max_length=100, description="Méthode de détection")
    detecteur: Optional[str] = Field(default=None, max_length=100, description="Nom du détecteur")
    
    # Responsables
    responsable_id: Optional[int] = Field(default=None, description="ID du responsable")
    responsable_nom: Optional[str] = Field(default=None, max_length=100, description="Nom du responsable")
    
    # Actions
    actions_recommandees: Optional[List[str]] = Field(default=None, description="Liste des actions recommandées")
    actions_prises: Optional[List[str]] = Field(default=None, description="Liste des actions déjà prises")
    
    # Liens
    documents: Optional[List[str]] = Field(default=None, description="Liste des documents liés")
    
    # Métadonnées
    reference: Optional[str] = Field(default=None, max_length=100, description="Référence externe")
    commentaire: Optional[str] = Field(default=None, description="Commentaires")
    metadata: Optional[dict] = Field(default=None, description="Métadonnées supplémentaires")


class TrapUpdate(BaseModel):
    """Schéma pour la mise à jour d'un piège."""
    titre: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    
    type: Optional[TrapType] = None
    categorie: Optional[TrapCategory] = None
    severite: Optional[TrapSeverity] = None
    statut: Optional[TrapStatus] = None
    
    mission_id: Optional[int] = None
    lot_id: Optional[int] = None
    projet_id: Optional[int] = None
    
    valeurs_anormales: Optional[List[dict]] = None
    regles_violees: Optional[List[str]] = None
    
    impact_estime: Optional[float] = Field(default=None, ge=0.0)
    probabilite: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    
    methode_detection: Optional[str] = Field(default=None, max_length=100)
    detecteur: Optional[str] = Field(default=None, max_length=100)
    
    responsable_id: Optional[int] = None
    responsable_nom: Optional[str] = Field(default=None, max_length=100)
    
    actions_recommandees: Optional[List[str]] = None
    actions_prises: Optional[List[str]] = None
    
    documents: Optional[List[str]] = None
    
    reference: Optional[str] = Field(default=None, max_length=100)
    commentaire: Optional[str] = None
    metadata: Optional[dict] = None


class TrapResponse(TrapBase):
    """Schéma de réponse pour un piège."""
    id: int = Field(..., description="Identifiant unique")
    entreprise_id: Optional[int] = Field(default=1, description="ID de l'entreprise")
    
    date_detection: datetime = Field(..., description="Date de détection")
    date_analyse: Optional[datetime] = Field(default=None, description="Date d'analyse")
    date_fermeture: Optional[datetime] = Field(default=None, description="Date de fermeture")
    
    valeurs_anormales: Optional[List[dict]] = Field(default=None, description="Valeurs anormales")
    regles_violees: Optional[List[str]] = Field(default=None, description="Règles violées")
    
    impact_estime: Optional[float] = Field(default=None, description="Impact estimé")
    probabilite: Optional[float] = Field(default=None, description="Probabilité")
    
    methode_detection: Optional[str] = Field(default=None, description="Méthode de détection")
    detecteur: Optional[str] = Field(default=None, description="Détecteur")
    
    responsable_id: Optional[int] = Field(default=None, description="ID du responsable")
    responsable_nom: Optional[str] = Field(default=None, description="Nom du responsable")
    
    actions_recommandees: Optional[List[str]] = Field(default=None, description="Actions recommandées")
    actions_prises: Optional[List[str]] = Field(default=None, description="Actions prises")
    
    documents: Optional[List[str]] = Field(default=None, description="Documents")
    
    reference: Optional[str] = Field(default=None, description="Référence externe")
    commentaire: Optional[str] = Field(default=None, description="Commentaires")
    metadata: Optional[dict] = Field(default=None, description="Métadonnées")
    
    # Champs calculés
    score: float = Field(default=0.0, description="Score de criticité (0-100)")
    est_actif: bool = Field(..., description="Indique si le piège est actif")
    est_resolu: bool = Field(..., description="Indique si le piège est résolu")
    
    created_at: datetime = Field(..., description="Date de création")
    updated_at: datetime = Field(..., description="Date de mise à jour")
    
    model_config = ConfigDict(from_attributes=True, json_schema_extra={
        "example": {
            "id": 1,
            "code": "TRP-2026-001",
            "titre": "Incohérence entre devis et commande",
            "type": "incoherence_donnees",
            "categorie": "chiffrage",
            "severite": "critical",
            "statut": "detecte",
            "entite_type": "chiffrage",
            "entite_id": 42,
            "score": 95.5,
            "est_actif": True,
            "est_resolu": False
        }
    })


class TrapListResponse(BaseModel):
    """Schéma de liste de pièges."""
    traps: List[TrapResponse] = Field(..., description="Liste des pièges")
    total: int = Field(..., description="Nombre total de pièges")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "traps": [],
            "total": 0
        }
    })


class TrapFilter(BaseModel):
    """Schéma de filtrage des pièges."""
    mission_id: Optional[int] = Field(default=None, description="Filtrer par mission")
    lot_id: Optional[int] = Field(default=None, description="Filtrer par lot")
    projet_id: Optional[int] = Field(default=None, description="Filtrer par projet")
    
    type: Optional[TrapType] = Field(default=None, description="Filtrer par type")
    categorie: Optional[TrapCategory] = Field(default=None, description="Filtrer par catégorie")
    severite: Optional[TrapSeverity] = Field(default=None, description="Filtrer par sévérité")
    statut: Optional[TrapStatus] = Field(default=None, description="Filtrer par statut")
    
    entite_type: Optional[str] = Field(default=None, max_length=50, description="Filtrer par type d'entité")
    entite_id: Optional[int] = Field(default=None, description="Filtrer par ID d'entité")
    
    responsable_id: Optional[int] = Field(default=None, description="Filtrer par responsable")
    detecteur: Optional[str] = Field(default=None, max_length=100, description="Filtrer par détecteur")
    
    date_debut: Optional[datetime] = Field(default=None, description="Date de début")
    date_fin: Optional[datetime] = Field(default=None, description="Date de fin")
    
    est_actif: Optional[bool] = Field(default=None, description="Filtrer par piège actif")
    est_resolu: Optional[bool] = Field(default=None, description="Filtrer par piège résolu")
    
    score_min: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="Score minimum")
    score_max: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="Score maximum")
    
    page: int = Field(default=1, ge=1, description="Numéro de page")
    per_page: int = Field(default=50, ge=1, le=1000, description="Éléments par page")


__all__ = [
    'TrapType', 'TrapCategory', 'TrapSeverity', 'TrapStatus',
    'TrapBase', 'TrapCreate', 'TrapUpdate', 'TrapResponse',
    'TrapListResponse', 'TrapFilter'
]


