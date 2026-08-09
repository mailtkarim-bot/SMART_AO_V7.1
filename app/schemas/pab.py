"""
SMART_AO V7 - pab.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

PAB Schemas - Schémas Pydantic pour la gestion des Préavis et Autorisations de Bâtiment
Source: ARCHITECTURE_V7_ENGINE.md §3.2
"""

from datetime import date, datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class PABType(str, Enum):
    """Types de PAB."""
    PREAVIS_DEBUT = "preavis_debut"
    AUTORISATION_BATIMENT = "autorisation_batiment"
    DECLARATION_PREALABLE = "declaration_prealable"
    PERMIS_CONSTRUIRE = "permis_construire"
    DECLARATION_OUVRAGE = "declaration_ouvrage"
    RECEPTE_PROVISOIRE = "reception_provisoire"
    RECEPTE_DEFINITIVE = "reception_definitive"
    AUTORISATION_ENVIRONNEMENTALE = "autorisation_environnementale"
    AUTORISATION_SECURITE = "autorisation_securite"


class PABStatut(str, Enum):
    """Statuts des PAB."""
    A_DEPOSER = "a_deposer"
    EN_INSTRUCTION = "en_instruction"
    COMPLEMENT_DEMANDE = "complement_demande"
    ENQUETE_PUBLIC = "enquete_publique"
    ACCORDE = "accorde"
    REFUSE = "refuse"
    RECURS_GRACIEUX = "recours_gracieux"
    RECURS_CONTENTIEUX = "recours_contentieux"
    ANNULE = "annule"
    EXPIRE = "expire"


class PABPriorite(str, Enum):
    """Niveaux de priorité pour les PAB."""
    FAIBLE = "faible"
    MOYENNE = "moyenne"
    ELEVEE = "elevee"
    CRITIQUE = "critique"


class PABBase(BaseModel):
    """Schéma de base pour un PAB."""
    code: str = Field(..., min_length=1, max_length=50, description="Code unique du PAB")
    reference: str = Field(..., min_length=1, max_length=100, description="Référence officielle")
    libelle: str = Field(..., min_length=1, max_length=200, description="Libellé du PAB")
    description: Optional[str] = Field(default=None, description="Description détaillée")
    
    type: PABType = Field(default=PABType.PREAVIS_DEBUT, description="Type de PAB")
    statut: PABStatut = Field(default=PABStatut.A_DEPOSER, description="Statut actuel")
    priorite: PABPriorite = Field(default=PABPriorite.MOYENNE, description="Niveau de priorité")
    
    date_depot: Optional[date] = Field(default=None, description="Date de dépôt")
    date_instruction: Optional[date] = Field(default=None, description="Date de début d'instruction")
    date_obtention: Optional[date] = Field(default=None, description="Date d'obtention")
    date_expiration: Optional[date] = Field(default=None, description="Date d'expiration")


class PABCreate(PABBase):
    """Schéma pour la création d'un PAB."""
    mission_id: Optional[int] = Field(default=None, description="ID de la mission associée")
    lot_id: Optional[int] = Field(default=None, description="ID du lot concerné")
    projet_id: Optional[int] = Field(default=None, description="ID du projet")
    entreprise_id: Optional[int] = Field(default=1, description="ID de l'entreprise")
    
    # Autorité
    autorite: Optional[str] = Field(default=None, max_length=200, description="Autorité compétente")
    autorite_contact: Optional[str] = Field(default=None, max_length=200, description="Contact à l'autorité")
    autorite_email: Optional[str] = Field(default=None, max_length=255, description="Email de l'autorité")
    
    # Coordonnées du projet
    adresse: Optional[str] = Field(default=None, description="Adresse du projet")
    code_postal: Optional[str] = Field(default=None, max_length=20, description="Code postal")
    ville: Optional[str] = Field(default=None, max_length=100, description="Ville")
    
    # Responsables
    responsable_depot: Optional[str] = Field(default=None, max_length=100, description="Responsable du dépôt")
    responsable_suivi: Optional[str] = Field(default=None, max_length=100, description="Responsable du suivi")
    
    # Documents
    documents_deposes: Optional[List[str]] = Field(default=None, description="Liste des documents déposés")
    documents_recus: Optional[List[str]] = Field(default=None, description="Liste des documents reçus")
    
    # Coûts
    cout_estime: Optional[float] = Field(default=None, ge=0.0, description="Coût estimé des démarches")
    cout_reel: Optional[float] = Field(default=None, ge=0.0, description="Coût réel")
    
    # Métadonnées
    reference_externe: Optional[str] = Field(default=None, max_length=100, description="Référence externe")
    commentaire: Optional[str] = Field(default=None, description="Commentaires")
    metadata: Optional[dict] = Field(default=None, description="Métadonnées supplémentaires")


class PABUpdate(BaseModel):
    """Schéma pour la mise à jour d'un PAB."""
    code: Optional[str] = Field(default=None, min_length=1, max_length=50)
    reference: Optional[str] = Field(default=None, min_length=1, max_length=100)
    libelle: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    
    type: Optional[PABType] = None
    statut: Optional[PABStatut] = None
    priorite: Optional[PABPriorite] = None
    
    date_depot: Optional[date] = None
    date_instruction: Optional[date] = None
    date_obtention: Optional[date] = None
    date_expiration: Optional[date] = None
    
    mission_id: Optional[int] = None
    lot_id: Optional[int] = None
    projet_id: Optional[int] = None
    
    autorite: Optional[str] = Field(default=None, max_length=200)
    autorite_contact: Optional[str] = Field(default=None, max_length=200)
    autorite_email: Optional[str] = Field(default=None, max_length=255)
    
    adresse: Optional[str] = None
    code_postal: Optional[str] = Field(default=None, max_length=20)
    ville: Optional[str] = Field(default=None, max_length=100)
    
    responsable_depot: Optional[str] = Field(default=None, max_length=100)
    responsable_suivi: Optional[str] = Field(default=None, max_length=100)
    
    documents_deposes: Optional[List[str]] = None
    documents_recus: Optional[List[str]] = None
    
    cout_estime: Optional[float] = Field(default=None, ge=0.0)
    cout_reel: Optional[float] = Field(default=None, ge=0.0)
    
    reference_externe: Optional[str] = Field(default=None, max_length=100)
    commentaire: Optional[str] = None
    metadata: Optional[dict] = None


class PABResponse(PABBase):
    """Schéma de réponse pour un PAB."""
    id: int = Field(..., description="Identifiant unique")
    mission_id: Optional[int] = Field(default=None, description="ID de la mission")
    lot_id: Optional[int] = Field(default=None, description="ID du lot")
    projet_id: Optional[int] = Field(default=None, description="ID du projet")
    entreprise_id: Optional[int] = Field(default=1, description="ID de l'entreprise")
    
    autorite: Optional[str] = Field(default=None, description="Autorité compétente")
    autorite_contact: Optional[str] = Field(default=None, description="Contact à l'autorité")
    autorite_email: Optional[str] = Field(default=None, description="Email de l'autorité")
    
    adresse: Optional[str] = Field(default=None, description="Adresse")
    code_postal: Optional[str] = Field(default=None, description="Code postal")
    ville: Optional[str] = Field(default=None, description="Ville")
    
    responsable_depot: Optional[str] = Field(default=None, description="Responsable du dépôt")
    responsable_suivi: Optional[str] = Field(default=None, description="Responsable du suivi")
    
    documents_deposes: Optional[List[str]] = Field(default=None, description="Documents déposés")
    documents_recus: Optional[List[str]] = Field(default=None, description="Documents reçus")
    
    cout_estime: Optional[float] = Field(default=None, description="Coût estimé")
    cout_reel: Optional[float] = Field(default=None, description="Coût réel")
    
    reference_externe: Optional[str] = Field(default=None, description="Référence externe")
    commentaire: Optional[str] = Field(default=None, description="Commentaires")
    metadata: Optional[dict] = Field(default=None, description="Métadonnées")
    
    # Champs calculés
    duree_instruction_jours: Optional[int] = Field(default=None, description="Durée d'instruction en jours")
    jours_restants: Optional[int] = Field(default=None, description="Jours restants avant expiration")
    est_valide: bool = Field(..., description="Indique si le PAB est valide")
    est_expire: bool = Field(..., description="Indique si le PAB est expiré")
    est_urgent: bool = Field(..., description="Indique si le PAB est urgent")
    
    created_at: datetime = Field(..., description="Date de création")
    updated_at: datetime = Field(..., description="Date de mise à jour")
    
    model_config = ConfigDict(from_attributes=True, json_schema_extra={
        "example": {
            "id": 1,
            "code": "PAB-2026-001",
            "reference": "PC-2026-12345",
            "libelle": "Permis de construire - Projet XYZ",
            "type": "permis_construire",
            "statut": "en_instruction",
            "priorite": "elevee",
            "date_depot": "2026-06-01",
            "est_valide": False,
            "est_urgent": True
        }
    })


class PABListResponse(BaseModel):
    """Schéma de liste de PAB."""
    pabs: List[PABResponse] = Field(..., description="Liste des PAB")
    total: int = Field(..., description="Nombre total de PAB")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "pabs": [],
            "total": 0
        }
    })


class PABFilter(BaseModel):
    """Schéma de filtrage des PAB."""
    mission_id: Optional[int] = Field(default=None, description="Filtrer par mission")
    lot_id: Optional[int] = Field(default=None, description="Filtrer par lot")
    projet_id: Optional[int] = Field(default=None, description="Filtrer par projet")
    type: Optional[PABType] = Field(default=None, description="Filtrer par type")
    statut: Optional[PABStatut] = Field(default=None, description="Filtrer par statut")
    priorite: Optional[PABPriorite] = Field(default=None, description="Filtrer par priorité")
    
    autorite: Optional[str] = Field(default=None, max_length=200, description="Filtrer par autorité")
    ville: Optional[str] = Field(default=None, max_length=100, description="Filtrer par ville")
    
    date_depot_debut: Optional[date] = Field(default=None, description="Date de dépôt début")
    date_depot_fin: Optional[date] = Field(default=None, description="Date de dépôt fin")
    date_expiration_debut: Optional[date] = Field(default=None, description="Date expiration début")
    date_expiration_fin: Optional[date] = Field(default=None, description="Date expiration fin")
    
    est_valide: Optional[bool] = Field(default=None, description="Filtrer par validité")
    est_expire: Optional[bool] = Field(default=None, description="Filtrer par expiration")
    est_urgent: Optional[bool] = Field(default=None, description="Filtrer par urgence")
    
    page: int = Field(default=1, ge=1, description="Numéro de page")
    per_page: int = Field(default=50, ge=1, le=1000, description="Éléments par page")


__all__ = [
    'PABType', 'PABStatut', 'PABPriorite',
    'PABBase', 'PABCreate', 'PABUpdate', 'PABResponse',
    'PABListResponse', 'PABFilter'
]


