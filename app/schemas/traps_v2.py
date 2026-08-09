"""
SMART_AO V7 - traps_v2.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Traps V2 Schemas - Schémas Pydantic avancés pour la détection intelligente des pièges
Source: ARCHITECTURE_V7_ENGINE.md §3.2
"""

from datetime import date, datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class TrapV2Type(str, Enum):
    """Types de pièges avancés."""
    INCOHERENCE_CCTP_DPGF = "incoherence_cctp_dpgf"
    INCOHERENCE_MEMOIRE_TECHNIQUE = "incoherence_memoire_technique"
    INCOHERENCE_CHIFFRAGE_REALISATION = "incoherence_chiffrage_realisation"
    INCOHERENCE_DELAIS_COUTS = "incoherence_delais_couts"
    SUR_COUT_DETECTE = "sur_cout_detecte"
    SOUS_COUT_RISQUE = "sous_cout_risque"
    RETARD_CRITIQUE = "retard_critique"
    CONFLIT_RESSOURCES = "conflit_ressources"
    NON_CONFORMITE_REGLEMENTAIRE = "non_conformite_reglementaire"
    RISQUE_JURIDIQUE_ELEVE = "risque_juridique_eleve"
    ANOMALIE_DOCUMENT_CRITIQUE = "anomalie_document_critique"
    PROBLEME_QUALITE = "probleme_qualite"
    RISQUE_SECURITE = "risque_securite"


class TrapV2Category(str, Enum):
    """Catégories de pièges avancées."""
    CHIFFRAGE_AVANCE = "chiffrage_avance"
    PLANNING_AVANCE = "planning_avance"
    DOCUMENTATION_AVANCEE = "documentation_avancee"
    REGLEMENTAIRE_AVANCE = "reglementaire_avance"
    TECHNIQUE_AVANCE = "technique_avance"
    FINANCIER_AVANCE = "financier_avance"
    JURIDIQUE_AVANCE = "juridique_avance"
    INTEGRATION_SI = "integration_si"


class TrapV2Severity(str, Enum):
    """Niveaux de sévérité avancés."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    CRITICAL = "critical"


class TrapV2Status(str, Enum):
    """Statuts des pièges avancés."""
    DETECTED = "detected"
    ANALYZING = "analyzing"
    ESCALATED = "escalated"
    VALIDATED = "validated"
    FALSE_POSITIVE = "false_positive"
    IGNORED = "ignored"
    RESOLVING = "resolving"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TrapV2Base(BaseModel):
    """Schéma de base pour un piège V2."""
    code: str = Field(..., min_length=1, max_length=50, description="Code unique du piège V2")
    titre: str = Field(..., min_length=1, max_length=200, description="Titre du piège")
    description: Optional[str] = Field(default=None, description="Description détaillée")
    description_technique: Optional[str] = Field(default=None, description="Description technique détaillée")
    
    type: TrapV2Type = Field(default=TrapV2Type.INCOHERENCE_CCTP_DPGF, description="Type de piège V2")
    categorie: TrapV2Category = Field(default=TrapV2Category.CHIFFRAGE_AVANCE, description="Catégorie V2")
    severite: TrapV2Severity = Field(default=TrapV2Severity.MEDIUM, description="Niveau de sévérité V2")
    statut: TrapV2Status = Field(default=TrapV2Status.DETECTED, description="Statut actuel V2")
    
    # Identification
    entite_type: str = Field(..., max_length=50, description="Type de l'entité source")
    entite_id: int = Field(..., description="ID de l'entité source")
    
    # Localisation
    mission_id: Optional[int] = Field(default=None, description="ID de la mission concernée")
    lot_id: Optional[int] = Field(default=None, description="ID du lot concerné")
    projet_id: Optional[int] = Field(default=None, description="ID du projet concerné")
    
    # Score
    score_risque: float = Field(default=0.0, ge=0.0, le=100.0, description="Score de risque (0-100)")
    score_impact: float = Field(default=0.0, ge=0.0, le=100.0, description="Score d'impact (0-100)")
    score_probabilite: float = Field(default=0.0, ge=0.0, le=100.0, description="Score de probabilité (0-100)")


class TrapV2Create(TrapV2Base):
    """Schéma pour la création d'un piège V2."""
    entreprise_id: Optional[int] = Field(default=1, description="ID de l'entreprise")
    
    date_detection: Optional[datetime] = Field(default=None, description="Date de détection")
    date_premiere_occurrence: Optional[datetime] = Field(default=None, description="Date de première occurrence")
    
    # Contexte avancé
    contexte: Optional[Dict[str, Any]] = Field(default=None, description="Contexte complet de détection")
    valeurs: Optional[Dict[str, Any]] = Field(default=None, description="Valeurs concernées")
    regles: Optional[List[Dict[str, Any]]] = Field(default=None, description="Règles appliquées")
    
    # Analyse
    impact_estime_euros: Optional[float] = Field(default=None, ge=0.0, description="Impact estimé en euros")
    probabilite: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Probabilité")
    
    # Détection
    detecteur: str = Field(..., max_length=100, description="Nom du détecteur")
    methode_detection: str = Field(..., max_length=100, description="Méthode de détection")
    algorithme: Optional[str] = Field(default=None, max_length=100, description="Algorithme utilisé")
    version_detecteur: Optional[str] = Field(default=None, max_length=20, description="Version du détecteur")
    
    # Correlations
    traps_lies: Optional[List[int]] = Field(default=None, description="IDs des traps liés")
    events_lies: Optional[List[int]] = Field(default=None, description="IDs des événements liés")
    
    # Responsables
    responsable_detection_id: Optional[int] = Field(default=None, description="ID du responsable de la détection")
    responsable_detection_nom: Optional[str] = Field(default=None, max_length=100, description="Nom du responsable de la détection")
    responsable_resolution_id: Optional[int] = Field(default=None, description="ID du responsable de résolution")
    responsable_resolution_nom: Optional[str] = Field(default=None, max_length=100, description="Nom du responsable de résolution")
    
    # Workflow
    workflow_etat: Optional[str] = Field(default=None, max_length=100, description="État dans le workflow")
    workflow_priorite: Optional[str] = Field(default=None, max_length=50, description="Priorité dans le workflow")
    
    # Actions
    actions_automatiques: Optional[List[str]] = Field(default=None, description="Actions automatiques exécutées")
    actions_manuelles: Optional[List[str]] = Field(default=None, description="Actions manuelles recommandées")
    
    # Liens
    documents: Optional[List[str]] = Field(default=None, description="Documents liés")
    
    # Métadonnées
    tags: Optional[List[str]] = Field(default=None, description="Tags pour classification")
    reference: Optional[str] = Field(default=None, max_length=100, description="Référence externe")
    metadata: Optional[dict] = Field(default=None, description="Métadonnées supplémentaires")


class TrapV2Update(BaseModel):
    """Schéma pour la mise à jour d'un piège V2."""
    titre: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    description_technique: Optional[str] = None
    
    type: Optional[TrapV2Type] = None
    categorie: Optional[TrapV2Category] = None
    severite: Optional[TrapV2Severity] = None
    statut: Optional[TrapV2Status] = None
    
    mission_id: Optional[int] = None
    lot_id: Optional[int] = None
    projet_id: Optional[int] = None
    
    score_risque: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    score_impact: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    score_probabilite: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    
    contexte: Optional[Dict[str, Any]] = None
    valeurs: Optional[Dict[str, Any]] = None
    regles: Optional[List[Dict[str, Any]]] = None
    
    impact_estime_euros: Optional[float] = Field(default=None, ge=0.0)
    probabilite: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    
    detecteur: Optional[str] = Field(default=None, max_length=100)
    methode_detection: Optional[str] = Field(default=None, max_length=100)
    algorithme: Optional[str] = Field(default=None, max_length=100)
    version_detecteur: Optional[str] = Field(default=None, max_length=20)
    
    traps_lies: Optional[List[int]] = None
    events_lies: Optional[List[int]] = None
    
    responsable_detection_id: Optional[int] = None
    responsable_detection_nom: Optional[str] = Field(default=None, max_length=100)
    responsable_resolution_id: Optional[int] = None
    responsable_resolution_nom: Optional[str] = Field(default=None, max_length=100)
    
    workflow_etat: Optional[str] = Field(default=None, max_length=100)
    workflow_priorite: Optional[str] = Field(default=None, max_length=50)
    
    actions_automatiques: Optional[List[str]] = None
    actions_manuelles: Optional[List[str]] = None
    
    documents: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    reference: Optional[str] = Field(default=None, max_length=100)
    metadata: Optional[dict] = None


class TrapV2Response(TrapV2Base):
    """Schéma de réponse pour un piège V2."""
    id: int = Field(..., description="Identifiant unique")
    entreprise_id: Optional[int] = Field(default=1, description="ID de l'entreprise")
    
    date_detection: datetime = Field(..., description="Date de détection")
    date_premiere_occurrence: Optional[datetime] = Field(default=None, description="Première occurrence")
    date_analyse: Optional[datetime] = Field(default=None, description="Date d'analyse")
    date_escalation: Optional[datetime] = Field(default=None, description="Date d'escalation")
    date_resolution: Optional[datetime] = Field(default=None, description="Date de résolution")
    date_fermeture: Optional[datetime] = Field(default=None, description="Date de fermeture")
    
    contexte: Optional[Dict[str, Any]] = Field(default=None, description="Contexte")
    valeurs: Optional[Dict[str, Any]] = Field(default=None, description="Valeurs")
    regles: Optional[List[Dict[str, Any]]] = Field(default=None, description="Règles")
    
    impact_estime_euros: Optional[float] = Field(default=None, description="Impact en euros")
    probabilite: Optional[float] = Field(default=None, description="Probabilité")
    
    detecteur: str = Field(..., description="Détecteur")
    methode_detection: str = Field(..., description="Méthode de détection")
    algorithme: Optional[str] = Field(default=None, description="Algorithme")
    version_detecteur: Optional[str] = Field(default=None, description="Version détecteur")
    
    traps_lies: Optional[List[int]] = Field(default=None, description="Traps liés")
    events_lies: Optional[List[int]] = Field(default=None, description="Événements liés")
    
    responsable_detection_id: Optional[int] = Field(default=None, description="ID détecteur")
    responsable_detection_nom: Optional[str] = Field(default=None, description="Nom détecteur")
    responsable_resolution_id: Optional[int] = Field(default=None, description="ID résolution")
    responsable_resolution_nom: Optional[str] = Field(default=None, description="Nom résolution")
    
    workflow_etat: Optional[str] = Field(default=None, description="État workflow")
    workflow_priorite: Optional[str] = Field(default=None, description="Priorité workflow")
    
    actions_automatiques: Optional[List[str]] = Field(default=None, description="Actions automatiques")
    actions_manuelles: Optional[List[str]] = Field(default=None, description="Actions manuelles")
    
    documents: Optional[List[str]] = Field(default=None, description="Documents")
    tags: Optional[List[str]] = Field(default=None, description="Tags")
    reference: Optional[str] = Field(default=None, description="Référence")
    metadata: Optional[dict] = Field(default=None, description="Métadonnées")
    
    # Champs calculés
    score_global: float = Field(default=0.0, description="Score global (0-100)")
    est_actif: bool = Field(..., description="Indique si le piège est actif")
    est_escalade: bool = Field(..., description="Indique si le piège est escaladé")
    est_resolu: bool = Field(..., description="Indique si le piège est résolu")
    est_recurrent: bool = Field(..., description="Indique si le piège est récurrent")
    
    created_at: datetime = Field(..., description="Date de création")
    updated_at: datetime = Field(..., description="Date de mise à jour")
    
    model_config = ConfigDict(from_attributes=True, json_schema_extra={
        "example": {
            "id": 1,
            "code": "TRP2-2026-001",
            "titre": "Incohérence critique CCTP/DPGF",
            "type": "incoherence_cctp_dpgf",
            "categorie": "chiffrage_avance",
            "severite": "critical",
            "statut": "detected",
            "entite_type": "mission",
            "entite_id": 42,
            "score_global": 98.5,
            "est_actif": True,
            "est_escalade": False,
            "est_resolu": False
        }
    })


class TrapV2ListResponse(BaseModel):
    """Schéma de liste de pièges V2."""
    traps: List[TrapV2Response] = Field(..., description="Liste des pièges V2")
    total: int = Field(..., description="Nombre total de pièges V2")
    stats: Optional[Dict[str, Any]] = Field(default=None, description="Statistiques agrégées")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "traps": [],
            "total": 0,
            "stats": {}
        }
    })


class TrapV2Filter(BaseModel):
    """Schéma de filtrage des pièges V2."""
    mission_id: Optional[int] = Field(default=None, description="Filtrer par mission")
    lot_id: Optional[int] = Field(default=None, description="Filtrer par lot")
    projet_id: Optional[int] = Field(default=None, description="Filtrer par projet")
    
    type: Optional[TrapV2Type] = Field(default=None, description="Filtrer par type V2")
    categorie: Optional[TrapV2Category] = Field(default=None, description="Filtrer par catégorie V2")
    severite: Optional[TrapV2Severity] = Field(default=None, description="Filtrer par sévérité V2")
    statut: Optional[TrapV2Status] = Field(default=None, description="Filtrer par statut V2")
    
    entite_type: Optional[str] = Field(default=None, max_length=50, description="Filtrer par type d'entité")
    detecteur: Optional[str] = Field(default=None, max_length=100, description="Filtrer par détecteur")
    
    score_min: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="Score minimum")
    score_max: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="Score maximum")
    
    date_debut: Optional[datetime] = Field(default=None, description="Date de début")
    date_fin: Optional[datetime] = Field(default=None, description="Date de fin")
    
    est_actif: Optional[bool] = Field(default=None, description="Filtrer par actif")
    est_escalade: Optional[bool] = Field(default=None, description="Filtrer par escaladé")
    est_resolu: Optional[bool] = Field(default=None, description="Filtrer par résolu")
    est_recurrent: Optional[bool] = Field(default=None, description="Filtrer par récurrent")
    
    tags: Optional[List[str]] = Field(default=None, description="Filtrer par tags")
    
    page: int = Field(default=1, ge=1, description="Numéro de page")
    per_page: int = Field(default=50, ge=1, le=1000, description="Éléments par page")


class TrapV2Aggregation(BaseModel):
    """Schéma pour l'agrégation des pièges V2."""
    count: int = Field(..., description="Nombre de pièges")
    by_type: Optional[Dict[str, int]] = Field(default=None, description="Répartition par type")
    by_severity: Optional[Dict[str, int]] = Field(default=None, description="Répartition par sévérité")
    by_category: Optional[Dict[str, int]] = Field(default=None, description="Répartition par catégorie")
    by_status: Optional[Dict[str, int]] = Field(default=None, description="Répartition par statut")
    score_moyen: float = Field(default=0.0, description="Score moyen")
    
    model_config = ConfigDict(from_attributes=True)


__all__ = [
    'TrapV2Type', 'TrapV2Category', 'TrapV2Severity', 'TrapV2Status',
    'TrapV2Base', 'TrapV2Create', 'TrapV2Update', 'TrapV2Response',
    'TrapV2ListResponse', 'TrapV2Filter', 'TrapV2Aggregation'
]


