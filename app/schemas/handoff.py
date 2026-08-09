"""
SMART_AO V7 - handoff.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Handoff Schemas - Schémas Pydantic pour la gestion des transferts et passations
Source: ARCHITECTURE_V7_ENGINE.md §3.2
"""

from datetime import date, datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class HandoffType(str, Enum):
    """Types de handoff (transfert)."""
    PHASE = "phase"
    LOT = "lot"
    MISSION = "mission"
    RESPONSABILITE = "responsabilite"
    CLIENT = "client"
    FOURNISSEUR = "fournisseur"
    SOUS_TRAITANT = "sous_traitant"
    DOCUMENTATION = "documentation"
    VALIDATION = "validation"
    ARCHIVAGE = "archivage"


class HandoffStatut(str, Enum):
    """Statuts des handoff."""
    PREVU = "prevu"
    EN_COURS = "en_cours"
    EN_REVUE = "en_revue"
    VALIDE = "valide"
    REFUSE = "refuse"
    ANNULE = "annule"
    TERMINE = "termine"


class HandoffPriorite(str, Enum):
    """Niveaux de priorité pour les handoff."""
    FAIBLE = "faible"
    MOYENNE = "moyenne"
    ELEVEE = "elevee"
    URGENTE = "urgente"


class HandoffBase(BaseModel):
    """Schéma de base pour un handoff."""
    code: str = Field(..., min_length=1, max_length=50, description="Code unique du handoff")
    titre: str = Field(..., min_length=1, max_length=200, description="Titre du handoff")
    description: Optional[str] = Field(default=None, description="Description détaillée")
    
    type: HandoffType = Field(default=HandoffType.LOT, description="Type de handoff")
    statut: HandoffStatut = Field(default=HandoffStatut.PREVU, description="Statut actuel")
    priorite: HandoffPriorite = Field(default=HandoffPriorite.MOYENNE, description="Niveau de priorité")
    
    date_prevue: Optional[date] = Field(default=None, description="Date prévue du handoff")
    date_debut: Optional[date] = Field(default=None, description="Date de début effective")
    date_fin: Optional[date] = Field(default=None, description="Date de fin effective")


class HandoffCreate(HandoffBase):
    """Schéma pour la création d'un handoff."""
    mission_id: Optional[int] = Field(default=None, description="ID de la mission concernée")
    lot_id: Optional[int] = Field(default=None, description="ID du lot concerné")
    projet_id: Optional[int] = Field(default=None, description="ID du projet")
    entreprise_id: Optional[int] = Field(default=1, description="ID de l'entreprise")
    
    # Acteurs
    emanateur_id: Optional[int] = Field(default=None, description="ID de l'émetteur")
    emanateur_nom: Optional[str] = Field(default=None, max_length=100, description="Nom de l'émetteur")
    emanateur_role: Optional[str] = Field(default=None, max_length=100, description="Rôle de l'émetteur")
    
    destinataire_id: Optional[int] = Field(default=None, description="ID du destinataire")
    destinataire_nom: Optional[str] = Field(default=None, max_length=100, description="Nom du destinataire")
    destinataire_role: Optional[str] = Field(default=None, max_length=100, description="Rôle du destinataire")
    
    # Suivi
    responsable_id: Optional[int] = Field(default=None, description="ID du responsable du handoff")
    responsable_nom: Optional[str] = Field(default=None, max_length=100, description="Nom du responsable")
    
    # Checklist
    checklist: Optional[List[dict]] = Field(default=None, description="Liste des éléments à vérifier")
    documents: Optional[List[str]] = Field(default=None, description="Liste des documents à transférer")
    
    # Métadonnées
    reference: Optional[str] = Field(default=None, max_length=100, description="Référence externe")
    commentaire: Optional[str] = Field(default=None, description="Commentaires")
    metadata: Optional[dict] = Field(default=None, description="Métadonnées supplémentaires")


class HandoffUpdate(BaseModel):
    """Schéma pour la mise à jour d'un handoff."""
    code: Optional[str] = Field(default=None, min_length=1, max_length=50)
    titre: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    
    type: Optional[HandoffType] = None
    statut: Optional[HandoffStatut] = None
    priorite: Optional[HandoffPriorite] = None
    
    date_prevue: Optional[date] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    
    mission_id: Optional[int] = None
    lot_id: Optional[int] = None
    projet_id: Optional[int] = None
    
    emanateur_id: Optional[int] = None
    emanateur_nom: Optional[str] = Field(default=None, max_length=100)
    emanateur_role: Optional[str] = Field(default=None, max_length=100)
    
    destinataire_id: Optional[int] = None
    destinataire_nom: Optional[str] = Field(default=None, max_length=100)
    destinataire_role: Optional[str] = Field(default=None, max_length=100)
    
    responsable_id: Optional[int] = None
    responsable_nom: Optional[str] = Field(default=None, max_length=100)
    
    checklist: Optional[List[dict]] = None
    documents: Optional[List[str]] = None
    
    reference: Optional[str] = Field(default=None, max_length=100)
    commentaire: Optional[str] = None
    metadata: Optional[dict] = None


class HandoffResponse(HandoffBase):
    """Schéma de réponse pour un handoff."""
    id: int = Field(..., description="Identifiant unique")
    mission_id: Optional[int] = Field(default=None, description="ID de la mission")
    lot_id: Optional[int] = Field(default=None, description="ID du lot")
    projet_id: Optional[int] = Field(default=None, description="ID du projet")
    entreprise_id: Optional[int] = Field(default=1, description="ID de l'entreprise")
    
    emanateur_id: Optional[int] = Field(default=None, description="ID de l'émetteur")
    emanateur_nom: Optional[str] = Field(default=None, description="Nom de l'émetteur")
    emanateur_role: Optional[str] = Field(default=None, description="Rôle de l'émetteur")
    
    destinataire_id: Optional[int] = Field(default=None, description="ID du destinataire")
    destinataire_nom: Optional[str] = Field(default=None, description="Nom du destinataire")
    destinataire_role: Optional[str] = Field(default=None, description="Rôle du destinataire")
    
    responsable_id: Optional[int] = Field(default=None, description="ID du responsable")
    responsable_nom: Optional[str] = Field(default=None, description="Nom du responsable")
    
    checklist: Optional[List[dict]] = Field(default=None, description="Checklist")
    documents: Optional[List[str]] = Field(default=None, description="Documents")
    
    reference: Optional[str] = Field(default=None, description="Référence externe")
    commentaire: Optional[str] = Field(default=None, description="Commentaires")
    metadata: Optional[dict] = Field(default=None, description="Métadonnées")
    
    # Champs calculés
    duree_prevue_jours: Optional[int] = Field(default=None, description="Durée prévue en jours")
    duree_reelle_jours: Optional[int] = Field(default=None, description="Durée réelle en jours")
    est_en_retard: bool = Field(..., description="Indique si le handoff est en retard")
    est_terminé: bool = Field(..., description="Indique si le handoff est terminé")
    
    created_at: datetime = Field(..., description="Date de création")
    updated_at: datetime = Field(..., description="Date de mise à jour")
    
    model_config = ConfigDict(from_attributes=True, json_schema_extra={
        "example": {
            "id": 1,
            "code": "HND-2026-001",
            "titre": "Transfert Lot A vers équipe B",
            "type": "lot",
            "statut": "en_cours",
            "priorite": "elevee",
            "date_prevue": "2026-08-15",
            "est_en_retard": False,
            "est_terminé": False
        }
    })


class HandoffListResponse(BaseModel):
    """Schéma de liste de handoff."""
    handoffs: List[HandoffResponse] = Field(..., description="Liste des handoff")
    total: int = Field(..., description="Nombre total de handoff")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "handoffs": [],
            "total": 0
        }
    })


class HandoffFilter(BaseModel):
    """Schéma de filtrage des handoff."""
    mission_id: Optional[int] = Field(default=None, description="Filtrer par mission")
    lot_id: Optional[int] = Field(default=None, description="Filtrer par lot")
    projet_id: Optional[int] = Field(default=None, description="Filtrer par projet")
    type: Optional[HandoffType] = Field(default=None, description="Filtrer par type")
    statut: Optional[HandoffStatut] = Field(default=None, description="Filtrer par statut")
    priorite: Optional[HandoffPriorite] = Field(default=None, description="Filtrer par priorité")
    
    emanateur_id: Optional[int] = Field(default=None, description="Filtrer par émetteur")
    destinataire_id: Optional[int] = Field(default=None, description="Filtrer par destinataire")
    responsable_id: Optional[int] = Field(default=None, description="Filtrer par responsable")
    
    date_debut: Optional[date] = Field(default=None, description="Date de début")
    date_fin: Optional[date] = Field(default=None, description="Date de fin")
    
    est_en_retard: Optional[bool] = Field(default=None, description="Filtrer par retard")
    est_terminé: Optional[bool] = Field(default=None, description="Filtrer par statut terminé")
    
    page: int = Field(default=1, ge=1, description="Numéro de page")
    per_page: int = Field(default=50, ge=1, le=1000, description="Éléments par page")


class HandoffChecklistItem(BaseModel):
    """Schéma pour un élément de checklist de handoff."""
    libelle: str = Field(..., description="Libellé de l'élément")
    est_complet: bool = Field(default=False, description="Indique si l'élément est complet")
    date_completion: Optional[datetime] = Field(default=None, description="Date de complétion")
    responsable: Optional[str] = Field(default=None, description="Responsable")
    commentaire: Optional[str] = Field(default=None, description="Commentaire")
    
    model_config = ConfigDict(from_attributes=True)


__all__ = [
    'HandoffType', 'HandoffStatut', 'HandoffPriorite',
    'HandoffBase', 'HandoffCreate', 'HandoffUpdate', 'HandoffResponse',
    'HandoffListResponse', 'HandoffFilter', 'HandoffChecklistItem'
]


