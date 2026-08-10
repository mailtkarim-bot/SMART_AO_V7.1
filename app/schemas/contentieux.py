"""
SMART_AO V7 - contentieux.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Contentieux Schemas - Schémas Pydantic pour la gestion des litiges
Source: ARCHITECTURE_V7_ENGINE.md §3.2
"""

from datetime import date, datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class ContentieuxType(str, Enum):
    """Types de contentieux."""
    RETARD_PAIEMENT = "retard_paiement"
    NON_CONFORMITE = "non_conformite"
    LITIGE_QUALITE = "litige_qualite"
    RECLAMATION_CLIENT = "reclamation_client"
    LITIGE_FOURNISSEUR = "litige_fournisseur"
    DIFFEREND_CONTRAT = "differend_contrat"
    RESPONSABILITE_DECENNALE = "responsabilite_decennale"
    GARANTIE_BIENNALE = "garantie_biennale"
    ASSURANCE = "assurance"
    AUTRE = "autre"


class ContentieuxStatut(str, Enum):
    """Statuts des contentieux."""
    OUVERT = "ouvert"
    EN_COURS = "en_cours"
    EN_MEDIATION = "en_mediation"
    EN_ARBITRAGE = "en_arbitrage"
    EN_JUSTICE = "en_justice"
    RESOLU = "resolu"
    CLOTURE = "cloture"
    ARCHIVE = "archive"


class ContentieuxPriorite(str, Enum):
    """Niveaux de priorité pour les contentieux."""
    FAIBLE = "faible"
    MOYENNE = "moyenne"
    ELEVEE = "elevee"
    CRITIQUE = "critique"


class ContentieuxBase(BaseModel):
    """Schéma de base pour un contentieux."""
    type: ContentieuxType = Field(..., description="Type de contentieux")
    titre: str = Field(..., min_length=1, max_length=200, description="Titre résumant le contentieux")
    description: Optional[str] = Field(default=None, description="Description détaillée")
    
    statut: ContentieuxStatut = Field(default=ContentieuxStatut.OUVERT, description="Statut actuel")
    priorite: ContentieuxPriorite = Field(default=ContentieuxPriorite.MOYENNE, description="Niveau de priorité")
    
    montant_estime: Optional[float] = Field(default=None, ge=0.0, description="Montant estimé du litige")
    montant_reel: Optional[float] = Field(default=None, ge=0.0, description="Montant réel final")
    
    date_ouverture: date = Field(..., description="Date d'ouverture")
    date_cloture: Optional[date] = Field(default=None, description="Date de clôture")
    date_echeance: Optional[date] = Field(default=None, description="Date limite pour action")
    
    partie_adverse: Optional[str] = Field(default=None, max_length=200, description="Partie adverse")
    responsable: Optional[str] = Field(default=None, max_length=100, description="Responsable interne")
    avocat: Optional[str] = Field(default=None, max_length=200, description="Avocat assigné")
    tribunal: Optional[str] = Field(default=None, max_length=200, description="Tribunal compétent")
    
    reference_dossier: Optional[str] = Field(default=None, max_length=100, description="Référence du dossier")
    reference_contrat: Optional[str] = Field(default=None, max_length=100, description="Référence du contrat")
    
    commentaire: Optional[str] = Field(default=None, description="Commentaires")


class ContentieuxCreate(ContentieuxBase):
    """Schéma pour la création d'un contentieux."""
    mission_id: Optional[int] = Field(default=None, description="ID de la mission concernée")
    
    pieces_jointes: Optional[List[str]] = Field(default=None, description="Liste des pièces jointes")
    actions_prevues: Optional[List[str]] = Field(default=None, description="Actions prévues")
    historique: Optional[List[dict]] = Field(default=None, description="Historique des actions")
    metadata: Optional[dict] = Field(default=None, description="Métadonnées")


class ContentieuxUpdate(BaseModel):
    """Schéma pour la mise à jour d'un contentieux."""
    type: Optional[ContentieuxType] = None
    titre: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    
    statut: Optional[ContentieuxStatut] = None
    priorite: Optional[ContentieuxPriorite] = None
    
    montant_estime: Optional[float] = Field(default=None, ge=0.0)
    montant_reel: Optional[float] = Field(default=None, ge=0.0)
    
    date_ouverture: Optional[date] = None
    date_cloture: Optional[date] = None
    date_echeance: Optional[date] = None
    
    partie_adverse: Optional[str] = Field(default=None, max_length=200)
    responsable: Optional[str] = Field(default=None, max_length=100)
    avocat: Optional[str] = Field(default=None, max_length=200)
    tribunal: Optional[str] = Field(default=None, max_length=200)
    
    reference_dossier: Optional[str] = Field(default=None, max_length=100)
    reference_contrat: Optional[str] = Field(default=None, max_length=100)
    
    mission_id: Optional[int] = None
    
    pieces_jointes: Optional[List[str]] = None
    actions_prevues: Optional[List[str]] = None
    historique: Optional[List[dict]] = None
    commentaire: Optional[str] = None
    metadata: Optional[dict] = None


class ContentieuxResponse(ContentieuxBase):
    """Schéma de réponse pour un contentieux."""
    id: int = Field(..., description="Identifiant unique")
    mission_id: Optional[int] = Field(default=None, description="ID de la mission")
    
    est_actif: bool = Field(..., description="Indique si le contentieux est actif")
    est_urgent: bool = Field(..., description="Indique si le contentieux est urgent")
    duree_jours: Optional[int] = Field(default=None, description="Durée en jours")
    
    pieces_jointes: Optional[List[str]] = Field(default=None, description="Pièces jointes")
    actions_prevues: Optional[List[str]] = Field(default=None, description="Actions prévues")
    historique: Optional[List[dict]] = Field(default=None, description="Historique")
    metadata: Optional[dict] = Field(default=None, description="Métadonnées")
    
    created_at: datetime = Field(..., description="Date de création")
    updated_at: datetime = Field(..., description="Date de mise à jour")
    
    model_config = ConfigDict(from_attributes=True, json_schema_extra={
        "example": {
            "id": 1,
            "type": "retard_paiement",
            "titre": "Retard de paiement client XYZ",
            "description": "Retard de 45 jours sur le paiement de la facture n°FACT-2026-001",
            "statut": "en_cours",
            "priorite": "elevee",
            "montant_estime": 150000.0,
            "date_ouverture": "2026-01-01",
            "date_echeance": "2026-02-15",
            "partie_adverse": "Client XYZ",
            "responsable": "Jean Dupont",
            "est_actif": True,
            "est_urgent": True
        }
    })


class ContentieuxListResponse(BaseModel):
    """Schéma de liste de contentieux."""
    contentieux: List[ContentieuxResponse] = Field(..., description="Liste des contentieux")
    total: int = Field(..., description="Nombre total de contentieux")
    nb_actifs: int = Field(default=0, description="Nombre de contentieux actifs")
    nb_urgents: int = Field(default=0, description="Nombre de contentieux urgents")


class ContentieuxHistoriqueBase(BaseModel):
    """Schéma de base pour un historique de contentieux."""
    contentieux_id: int = Field(..., description="ID du contentieux")
    action: str = Field(..., description="Action effectuée")
    description: Optional[str] = Field(default=None, description="Description de l'action")
    type_action: Optional[str] = Field(default=None, max_length=50, description="Type d'action")
    
    utilisateur_id: Optional[int] = Field(default=None, description="ID de l'utilisateur")
    utilisateur_nom: Optional[str] = Field(default=None, max_length=100, description="Nom de l'utilisateur")
    
    document_path: Optional[str] = Field(default=None, max_length=255, description="Chemin du document")


class ContentieuxHistoriqueResponse(ContentieuxHistoriqueBase):
    """Schéma de réponse pour un historique."""
    id: int = Field(..., description="Identifiant unique")
    date_action: datetime = Field(..., description="Date de l'action")
    metadata: Optional[dict] = Field(default=None, description="Métadonnées")
    
    model_config = ConfigDict(from_attributes=True)


class ContentieuxFilter(BaseModel):
    """Schéma de filtrage des contentieux."""
    mission_id: Optional[int] = Field(default=None, description="Filtrer par mission")
    type: Optional[ContentieuxType] = Field(default=None, description="Filtrer par type")
    statut: Optional[ContentieuxStatut] = Field(default=None, description="Filtrer par statut")
    priorite: Optional[ContentieuxPriorite] = Field(default=None, description="Filtrer par priorité")
    est_actif: Optional[bool] = Field(default=None, description="Filtrer par activité")
    est_urgent: Optional[bool] = Field(default=None, description="Filtrer par urgence")
    responsable: Optional[str] = Field(default=None, description="Filtrer par responsable")
    partie_adverse: Optional[str] = Field(default=None, description="Filtrer par partie adverse")
    
    page: int = Field(default=1, ge=1, description="Numéro de page")
    per_page: int = Field(default=50, ge=1, le=1000, description="Éléments par page")


__all__ = [
    'ContentieuxType', 'ContentieuxStatut', 'ContentieuxPriorite',
    'ContentieuxBase', 'ContentieuxCreate', 'ContentieuxUpdate',
    'ContentieuxResponse', 'ContentieuxListResponse',
    'ContentieuxHistoriqueBase', 'ContentieuxHistoriqueResponse',
    'ContentieuxFilter'
]

