"""
SMART_AO V7 - chiffrage.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Chiffrage Schemas - Schémas Pydantic pour la gestion du chiffrage et de la tarification
Source: ARCHITECTURE_V7_ENGINE.md §3.2
"""

from datetime import date, datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class ChiffrageType(str, Enum):
    """Types de chiffrage."""
    DEVIS = "devis"
    OFFRE = "offre"
    MARCHE = "marche"
    ETUDE = "etude"
    SIMULATION = "simulation"
    REVISION = "revision"
    CORRECTIF = "correctif"


class ChiffrageStatut(str, Enum):
    """Statuts du chiffrage."""
    BROUILLON = "brouillon"
    EN_COURS = "en_cours"
    EN_REVISION = "en_revision"
    VALIDE = "valide"
    SIGNE = "signe"
    ARCHIVE = "archive"
    ANNULE = "annule"


class ChiffragePriorite(str, Enum):
    """Niveaux de priorité pour le chiffrage."""
    FAIBLE = "faible"
    MOYENNE = "moyenne"
    ELEVEE = "elevee"
    URGENTE = "urgente"


class TVATaux(str, Enum):
    """Taux de TVA applicables."""
    ZERO = "0.0"
    REDUIT_5_5 = "5.5"
    REDUIT_10 = "10.0"
    NORMAL_20 = "20.0"


class ChiffrageBase(BaseModel):
    """Schéma de base pour un chiffrage."""
    code: str = Field(..., min_length=1, max_length=50, description="Code unique du chiffrage")
    libelle: str = Field(..., min_length=1, max_length=200, description="Libellé du chiffrage")
    description: Optional[str] = Field(default=None, description="Description détaillée")
    
    type: ChiffrageType = Field(default=ChiffrageType.DEVIS, description="Type de chiffrage")
    statut: ChiffrageStatut = Field(default=ChiffrageStatut.BROUILLON, description="Statut actuel")
    priorite: ChiffragePriorite = Field(default=ChiffragePriorite.MOYENNE, description="Niveau de priorité")
    
    montant_ht: float = Field(default=0.0, ge=0.0, description="Montant hors taxes")
    montant_tva: float = Field(default=0.0, ge=0.0, description="Montant de la TVA")
    montant_ttc: float = Field(default=0.0, ge=0.0, description="Montant toutes taxes comprises")
    
    tva_taux: TVATaux = Field(default=TVATaux.NORMAL_20, description="Taux de TVA appliqué")


class ChiffrageCreate(ChiffrageBase):
    """Schéma pour la création d'un chiffrage."""
    mission_id: Optional[int] = Field(default=None, description="ID de la mission associée")
    lot_id: Optional[int] = Field(default=None, description="ID du lot concerné")
    entreprise_id: Optional[int] = Field(default=1, description="ID de l'entreprise")
    
    date_creation: Optional[date] = Field(default=None, description="Date de création")
    date_limite: Optional[date] = Field(default=None, description="Date limite de validité")
    date_signature: Optional[date] = Field(default=None, description="Date de signature")
    
    client_id: Optional[int] = Field(default=None, description="ID du client")
    client_nom: Optional[str] = Field(default=None, max_length=200, description="Nom du client")
    
    responsable_id: Optional[int] = Field(default=None, description="ID du responsable")
    responsable_nom: Optional[str] = Field(default=None, max_length=100, description="Nom du responsable")
    
    postes: Optional[List[dict]] = Field(default=None, description="Liste des postes de chiffrage")
    
    documents: Optional[List[str]] = Field(default=None, description="Liste des documents associés")
    
    reference: Optional[str] = Field(default=None, max_length=100, description="Référence externe")
    commentaire: Optional[str] = Field(default=None, description="Commentaires")
    metadata: Optional[dict] = Field(default=None, description="Métadonnées supplémentaires")


class ChiffrageUpdate(BaseModel):
    """Schéma pour la mise à jour d'un chiffrage."""
    code: Optional[str] = Field(default=None, min_length=1, max_length=50)
    libelle: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    
    type: Optional[ChiffrageType] = None
    statut: Optional[ChiffrageStatut] = None
    priorite: Optional[ChiffragePriorite] = None
    
    montant_ht: Optional[float] = Field(default=None, ge=0.0)
    montant_tva: Optional[float] = Field(default=None, ge=0.0)
    montant_ttc: Optional[float] = Field(default=None, ge=0.0)
    tva_taux: Optional[TVATaux] = None
    
    mission_id: Optional[int] = None
    lot_id: Optional[int] = None
    
    date_limite: Optional[date] = None
    date_signature: Optional[date] = None
    
    client_id: Optional[int] = None
    client_nom: Optional[str] = Field(default=None, max_length=200)
    
    responsable_id: Optional[int] = None
    responsable_nom: Optional[str] = Field(default=None, max_length=100)
    
    postes: Optional[List[dict]] = None
    documents: Optional[List[str]] = None
    
    reference: Optional[str] = Field(default=None, max_length=100)
    commentaire: Optional[str] = None
    metadata: Optional[dict] = None


class ChiffrageResponse(ChiffrageBase):
    """Schéma de réponse pour un chiffrage."""
    id: int = Field(..., description="Identifiant unique")
    mission_id: Optional[int] = Field(default=None, description="ID de la mission")
    lot_id: Optional[int] = Field(default=None, description="ID du lot")
    entreprise_id: Optional[int] = Field(default=1, description="ID de l'entreprise")
    
    date_creation: date = Field(..., description="Date de création")
    date_limite: Optional[date] = Field(default=None, description="Date limite de validité")
    date_signature: Optional[date] = Field(default=None, description="Date de signature")
    date_mise_a_jour: Optional[datetime] = Field(default=None, description="Date de dernière mise à jour")
    
    client_id: Optional[int] = Field(default=None, description="ID du client")
    client_nom: Optional[str] = Field(default=None, description="Nom du client")
    
    responsable_id: Optional[int] = Field(default=None, description="ID du responsable")
    responsable_nom: Optional[str] = Field(default=None, description="Nom du responsable")
    
    postes: Optional[List[dict]] = Field(default=None, description="Liste des postes")
    documents: Optional[List[str]] = Field(default=None, description="Documents associés")
    
    reference: Optional[str] = Field(default=None, description="Référence externe")
    commentaire: Optional[str] = Field(default=None, description="Commentaires")
    metadata: Optional[dict] = Field(default=None, description="Métadonnées")
    
    est_valide: bool = Field(..., description="Indique si le chiffrage est valide")
    est_signe: bool = Field(..., description="Indique si le chiffrage est signé")
    est_archive: bool = Field(..., description="Indique si le chiffrage est archivé")
    
    created_at: datetime = Field(..., description="Date de création")
    updated_at: datetime = Field(..., description="Date de mise à jour")
    
    model_config = ConfigDict(from_attributes=True, json_schema_extra={
        "example": {
            "id": 1,
            "code": "DEV-2026-001",
            "libelle": "Chiffrage Mission XYZ",
            "type": "devis",
            "statut": "valide",
            "montant_ht": 150000.0,
            "montant_tva": 30000.0,
            "montant_ttc": 180000.0,
            "tva_taux": "20.0",
            "client_nom": "Client SA",
            "est_valide": True,
            "est_signe": True
        }
    })


class ChiffrageListResponse(BaseModel):
    """Schéma de liste de chiffrages."""
    chiffrages: List[ChiffrageResponse] = Field(..., description="Liste des chiffrages")
    total: int = Field(..., description="Nombre total de chiffrages")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "chiffrages": [],
            "total": 0
        }
    })


class PosteChiffrageBase(BaseModel):
    """Schéma de base pour un poste de chiffrage."""
    code: str = Field(..., min_length=1, max_length=50, description="Code du poste")
    libelle: str = Field(..., min_length=1, max_length=200, description="Libellé du poste")
    description: Optional[str] = Field(default=None, description="Description")
    
    quantite: float = Field(default=1.0, ge=0.0, description="Quantité")
    unite: str = Field(default="u", max_length=20, description="Unité de mesure")
    
    prix_unitaire_ht: float = Field(default=0.0, ge=0.0, description="Prix unitaire HT")
    prix_total_ht: float = Field(default=0.0, ge=0.0, description="Prix total HT")
    
    categorie: Optional[str] = Field(default=None, max_length=50, description="Catégorie du poste")
    sous_categorie: Optional[str] = Field(default=None, max_length=50, description="Sous-catégorie")
    
    tva_taux: Optional[TVATaux] = Field(default=None, description="Taux de TVA spécifique")


class PosteChiffrageCreate(PosteChiffrageBase):
    """Schéma pour la création d'un poste."""
    chiffrage_id: Optional[int] = Field(default=None, description="ID du chiffrage parent")
    lot_id: Optional[int] = Field(default=None, description="ID du lot associé")
    
    fournisseur: Optional[str] = Field(default=None, max_length=200, description="Fournisseur")
    reference_fournisseur: Optional[str] = Field(default=None, max_length=100, description="Référence fournisseur")
    
    indice: Optional[str] = Field(default=None, max_length=50, description="Indice applicable")
    indice_valeur: Optional[float] = Field(default=None, description="Valeur de l'indice")
    
    commentaire: Optional[str] = Field(default=None, description="Commentaires")
    metadata: Optional[dict] = Field(default=None, description="Métadonnées")


class PosteChiffrageResponse(PosteChiffrageBase):
    """Schéma de réponse pour un poste de chiffrage."""
    id: int = Field(..., description="Identifiant unique")
    chiffrage_id: Optional[int] = Field(default=None, description="ID du chiffrage parent")
    lot_id: Optional[int] = Field(default=None, description="ID du lot")
    
    fournisseur: Optional[str] = Field(default=None, description="Fournisseur")
    reference_fournisseur: Optional[str] = Field(default=None, description="Référence fournisseur")
    
    indice: Optional[str] = Field(default=None, description="Indice")
    indice_valeur: Optional[float] = Field(default=None, description="Valeur de l'indice")
    
    prix_unitaire_ttc: float = Field(..., description="Prix unitaire TTC calculé")
    prix_total_ttc: float = Field(..., description="Prix total TTC calculé")
    
    commentaire: Optional[str] = Field(default=None, description="Commentaires")
    metadata: Optional[dict] = Field(default=None, description="Métadonnées")
    
    created_at: datetime = Field(..., description="Date de création")
    updated_at: datetime = Field(..., description="Date de mise à jour")
    
    model_config = ConfigDict(from_attributes=True)


class ChiffrageFilter(BaseModel):
    """Schéma de filtrage des chiffrages."""
    mission_id: Optional[int] = Field(default=None, description="Filtrer par mission")
    lot_id: Optional[int] = Field(default=None, description="Filtrer par lot")
    type: Optional[ChiffrageType] = Field(default=None, description="Filtrer par type")
    statut: Optional[ChiffrageStatut] = Field(default=None, description="Filtrer par statut")
    priorite: Optional[ChiffragePriorite] = Field(default=None, description="Filtrer par priorité")
    client_id: Optional[int] = Field(default=None, description="Filtrer par client")
    responsable_id: Optional[int] = Field(default=None, description="Filtrer par responsable")
    
    montant_min: Optional[float] = Field(default=None, ge=0.0, description="Montant minimum")
    montant_max: Optional[float] = Field(default=None, ge=0.0, description="Montant maximum")
    
    date_debut: Optional[date] = Field(default=None, description="Date de début")
    date_fin: Optional[date] = Field(default=None, description="Date de fin")
    
    est_valide: Optional[bool] = Field(default=None, description="Filtrer par validité")
    est_signe: Optional[bool] = Field(default=None, description="Filtrer par signature")
    
    page: int = Field(default=1, ge=1, description="Numéro de page")
    per_page: int = Field(default=50, ge=1, le=1000, description="Éléments par page")


__all__ = [
    'ChiffrageType', 'ChiffrageStatut', 'ChiffragePriorite', 'TVATaux',
    'ChiffrageBase', 'ChiffrageCreate', 'ChiffrageUpdate', 'ChiffrageResponse',
    'ChiffrageListResponse', 'PosteChiffrageBase', 'PosteChiffrageCreate',
    'PosteChiffrageResponse', 'ChiffrageFilter'
]


