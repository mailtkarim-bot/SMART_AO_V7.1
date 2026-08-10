"""
SMART_AO V7 - alloti.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Allotissement Schemas - Schémas Pydantic pour la gestion des allotissements
Source: ARCHITECTURE_V7_ENGINE.md §3.2
"""

from datetime import date, datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class AllotissementType(str, Enum):
    """Types d'allotissement."""
    LOT_UNIQUE = "lot_unique"
    LOTS_SEPARES = "lots_separes"
    LOTS_GLOBAUX = "lots_globaux"
    MIXTE = "mixte"


class AllotissementStatut(str, Enum):
    """Statuts des allotissements."""
    BROUILLON = "brouillon"
    EN_COURS = "en_cours"
    VALIDE = "valide"
    SOUMIS = "soumis"
    ATTRIBUE = "attribue"
    REJETE = "rejete"
    ARCHIVE = "archive"


class LotType(str, Enum):
    """Types de lots."""
    GROS_OEUVRE = "gros_oeuvre"
    SECOND_OEUVRE = "second_oeuvre"
    CORPS_ETAT = "corps_etat"
    ELECTRICITE = "electricite"
    PLOMBERIE = "plomberie"
    CVC = "cvc"
    MENUISERIE = "menuiserie"
    REVETEMENTS = "revetements"
    ISOLATION = "isolation"
    COUVERTURE = "couverture"
    AUTRE = "autre"


class LotBase(BaseModel):
    """Schéma de base pour un lot."""
    code: str = Field(..., min_length=1, max_length=50, description="Code unique du lot")
    nom: str = Field(..., min_length=1, max_length=200, description="Nom du lot")
    description: Optional[str] = Field(default=None, description="Description détaillée")
    
    type: LotType = Field(default=LotType.GROS_OEUVRE, description="Type de lot")
    
    budget_previsionnel: Optional[float] = Field(default=None, ge=0.0, description="Budget prévisionnel (€)")
    budget_reel: Optional[float] = Field(default=None, ge=0.0, description="Budget réel (€)")
    
    delai_jours: Optional[int] = Field(default=None, ge=0, description="Délai en jours")
    date_debut: Optional[date] = Field(default=None, description="Date de début")
    date_fin: Optional[date] = Field(default=None, description="Date de fin")
    
    responsable: Optional[str] = Field(default=None, max_length=100, description="Responsable du lot")
    entreprise: Optional[str] = Field(default=None, max_length=200, description="Entreprise attribuée")
    
    statut: AllotissementStatut = Field(default=AllotissementStatut.BROUILLON, description="Statut du lot")
    
    metadata: Optional[dict] = Field(default=None, description="Métadonnées")


class LotCreate(LotBase):
    """Schéma pour la création d'un lot."""
    mission_id: Optional[int] = Field(default=None, description="ID de la mission")
    parent_id: Optional[int] = Field(default=None, description="ID du lot parent")


class LotUpdate(BaseModel):
    """Schéma pour la mise à jour d'un lot."""
    code: Optional[str] = Field(default=None, min_length=1, max_length=50)
    nom: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    
    type: Optional[LotType] = None
    
    budget_previsionnel: Optional[float] = Field(default=None, ge=0.0)
    budget_reel: Optional[float] = Field(default=None, ge=0.0)
    
    delai_jours: Optional[int] = Field(default=None, ge=0)
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    
    responsable: Optional[str] = Field(default=None, max_length=100)
    entreprise: Optional[str] = Field(default=None, max_length=200)
    
    statut: Optional[AllotissementStatut] = None
    
    mission_id: Optional[int] = None
    parent_id: Optional[int] = None
    metadata: Optional[dict] = None


class LotResponse(LotBase):
    """Schéma de réponse pour un lot."""
    id: int = Field(..., description="Identifiant unique")
    mission_id: Optional[int] = Field(default=None, description="ID de la mission")
    parent_id: Optional[int] = Field(default=None, description="ID du lot parent")
    
    avis_technique: Optional[str] = Field(default=None, description="Avis technique")
    avis_financier: Optional[str] = Field(default=None, description="Avis financier")
    
    created_at: datetime = Field(..., description="Date de création")
    updated_at: datetime = Field(..., description="Date de mise à jour")
    
    model_config = ConfigDict(from_attributes=True, json_schema_extra={
        "example": {
            "id": 1,
            "code": "GO-001",
            "nom": "Gros OEuvre",
            "type": "gros_oeuvre",
            "budget_previsionnel": 500000.0,
            "delai_jours": 180,
            "statut": "valide",
            "responsable": "Jean Dupont",
            "entreprise": "Entreprise BTP"
        }
    })


class LotListResponse(BaseModel):
    """Schéma de liste de lots."""
    lots: List[LotResponse] = Field(..., description="Liste des lots")
    total: int = Field(..., description="Nombre total de lots")


class AllotissementBase(BaseModel):
    """Schéma de base pour un allotissement."""
    nom: str = Field(..., min_length=1, max_length=200, description="Nom de l'allotissement")
    description: Optional[str] = Field(default=None, description="Description")
    
    type: AllotissementType = Field(default=AllotissementType.LOTS_SEPARES, description="Type d'allotissement")
    statut: AllotissementStatut = Field(default=AllotissementStatut.BROUILLON, description="Statut")
    
    date_creation: date = Field(..., description="Date de création")
    date_soumission: Optional[date] = Field(default=None, description="Date de soumission")
    date_attribution: Optional[date] = Field(default=None, description="Date d'attribution")
    
    metadata: Optional[dict] = Field(default=None, description="Métadonnées")


class AllotissementCreate(AllotissementBase):
    """Schéma pour la création d'un allotissement."""
    mission_id: Optional[int] = Field(default=None, description="ID de la mission")


class AllotissementResponse(AllotissementBase):
    """Schéma de réponse pour un allotissement."""
    id: int = Field(..., description="Identifiant unique")
    mission_id: Optional[int] = Field(default=None, description="ID de la mission")
    
    nb_lots: int = Field(default=0, description="Nombre de lots")
    budget_total: float = Field(default=0.0, description="Budget total")
    delai_total: int = Field(default=0, description="Délai total en jours")
    
    created_at: datetime = Field(..., description="Date de création")
    updated_at: datetime = Field(..., description="Date de mise à jour")
    
    lots: Optional[List[LotResponse]] = Field(default=None, description="Liste des lots")
    
    model_config = ConfigDict(from_attributes=True)


class AllotissementFilter(BaseModel):
    """Schéma de filtrage des allotissements."""
    mission_id: Optional[int] = Field(default=None, description="Filtrer par mission")
    type: Optional[AllotissementType] = Field(default=None, description="Filtrer par type")
    statut: Optional[AllotissementStatut] = Field(default=None, description="Filtrer par statut")
    
    page: int = Field(default=1, ge=1, description="Numéro de page")
    per_page: int = Field(default=50, ge=1, le=1000, description="Éléments par page")


__all__ = [
    'AllotissementType', 'AllotissementStatut', 'LotType',
    'LotBase', 'LotCreate', 'LotUpdate', 'LotResponse', 'LotListResponse',
    'AllotissementBase', 'AllotissementCreate', 'AllotissementResponse',
    'AllotissementFilter'
]

