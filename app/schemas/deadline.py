"""
SMART_AO V7 - deadline.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Deadline Schemas - Schémas Pydantic pour la gestion des échéances et délais
Source: ARCHITECTURE_V7_ENGINE.md §3.2
"""

from datetime import date, datetime, time
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class DeadlineType(str, Enum):
    """Types de deadlines."""
    LEGALE = "legale"
    CONTRACTUELLE = "contractuelle"
    REGLEMENTAIRE = "reglementaire"
    INTERNE = "interne"
    CLIENT = "client"
    FOURNISSEUR = "fournisseur"
    ADMINISTRATIVE = "administrative"
    TECHNIQUE = "technique"
    FINANCIERE = "financiere"


class DeadlineStatut(str, Enum):
    """Statuts des deadlines."""
    A_VENIR = "a_venir"
    EN_COURS = "en_cours"
    PROCHE = "proche"
    URGENTE = "urgente"
    DEPASSEE = "depasee"
    ATTEINTE = "atteinte"
    ANNULEE = "annulee"


class DeadlinePriorite(str, Enum):
    """Niveaux de priorité pour les deadlines."""
    FAIBLE = "faible"
    MOYENNE = "moyenne"
    ELEVEE = "elevee"
    CRITIQUE = "critique"


class DeadlineBase(BaseModel):
    """Schéma de base pour une deadline."""
    code: str = Field(..., min_length=1, max_length=50, description="Code unique de la deadline")
    titre: str = Field(..., min_length=1, max_length=200, description="Titre de la deadline")
    description: Optional[str] = Field(default=None, description="Description détaillée")
    
    type: DeadlineType = Field(default=DeadlineType.CONTRACTUELLE, description="Type de deadline")
    statut: DeadlineStatut = Field(default=DeadlineStatut.A_VENIR, description="Statut actuel")
    priorite: DeadlinePriorite = Field(default=DeadlinePriorite.MOYENNE, description="Niveau de priorité")
    
    date_echeance: date = Field(..., description="Date limite d'échéance")
    heure_echeance: Optional[time] = Field(default=None, description="Heure limite (si applicable)")
    
    duree_estimee_jours: Optional[int] = Field(default=None, ge=0, description="Durée estimée en jours")
    duree_estimee_heures: Optional[int] = Field(default=None, ge=0, description="Durée estimée en heures")


class DeadlineCreate(DeadlineBase):
    """Schéma pour la création d'une deadline."""
    mission_id: Optional[int] = Field(default=None, description="ID de la mission associée")
    lot_id: Optional[int] = Field(default=None, description="ID du lot concerné")
    entreprise_id: Optional[int] = Field(default=1, description="ID de l'entreprise")
    
    date_creation: Optional[date] = Field(default=None, description="Date de création")
    date_debut: Optional[date] = Field(default=None, description="Date de début du suivi")
    date_rappel: Optional[date] = Field(default=None, description="Date de rappel")
    
    responsable_id: Optional[int] = Field(default=None, description="ID du responsable")
    responsable_nom: Optional[str] = Field(default=None, max_length=100, description="Nom du responsable")
    
    # Liens
    projet_id: Optional[int] = Field(default=None, description="ID du projet")
    contrat_id: Optional[int] = Field(default=None, description="ID du contrat")
    document_id: Optional[int] = Field(default=None, description="ID du document")
    
    # Conséquences
    penalite_jour: Optional[float] = Field(default=None, ge=0.0, description="Pénalité par jour de retard")
    penalite_maximale: Optional[float] = Field(default=None, ge=0.0, description="Pénalité maximale")
    
    # Notifications
    notifier_responsable: bool = Field(default=True, description="Notifier le responsable")
    notifier_equipe: bool = Field(default=False, description="Notifier l'équipe")
    notifier_client: bool = Field(default=False, description="Notifier le client")
    
    reference: Optional[str] = Field(default=None, max_length=100, description="Référence externe")
    commentaire: Optional[str] = Field(default=None, description="Commentaires")
    metadata: Optional[dict] = Field(default=None, description="Métadonnées supplémentaires")


class DeadlineUpdate(BaseModel):
    """Schéma pour la mise à jour d'une deadline."""
    code: Optional[str] = Field(default=None, min_length=1, max_length=50)
    titre: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    
    type: Optional[DeadlineType] = None
    statut: Optional[DeadlineStatut] = None
    priorite: Optional[DeadlinePriorite] = None
    
    date_echeance: Optional[date] = None
    heure_echeance: Optional[time] = None
    
    duree_estimee_jours: Optional[int] = Field(default=None, ge=0)
    duree_estimee_heures: Optional[int] = Field(default=None, ge=0)
    
    mission_id: Optional[int] = None
    lot_id: Optional[int] = None
    
    date_rappel: Optional[date] = None
    
    responsable_id: Optional[int] = None
    responsable_nom: Optional[str] = Field(default=None, max_length=100)
    
    projet_id: Optional[int] = None
    contrat_id: Optional[int] = None
    document_id: Optional[int] = None
    
    penalite_jour: Optional[float] = Field(default=None, ge=0.0)
    penalite_maximale: Optional[float] = Field(default=None, ge=0.0)
    
    notifier_responsable: Optional[bool] = None
    notifier_equipe: Optional[bool] = None
    notifier_client: Optional[bool] = None
    
    reference: Optional[str] = Field(default=None, max_length=100)
    commentaire: Optional[str] = None
    metadata: Optional[dict] = None


class DeadlineResponse(DeadlineBase):
    """Schéma de réponse pour une deadline."""
    id: int = Field(..., description="Identifiant unique")
    mission_id: Optional[int] = Field(default=None, description="ID de la mission")
    lot_id: Optional[int] = Field(default=None, description="ID du lot")
    entreprise_id: Optional[int] = Field(default=1, description="ID de l'entreprise")
    
    date_creation: date = Field(..., description="Date de création")
    date_debut: Optional[date] = Field(default=None, description="Date de début")
    date_rappel: Optional[date] = Field(default=None, description="Date de rappel")
    date_atteinte: Optional[datetime] = Field(default=None, description="Date à laquelle la deadline a été atteinte")
    
    responsable_id: Optional[int] = Field(default=None, description="ID du responsable")
    responsable_nom: Optional[str] = Field(default=None, description="Nom du responsable")
    
    projet_id: Optional[int] = Field(default=None, description="ID du projet")
    contrat_id: Optional[int] = Field(default=None, description="ID du contrat")
    document_id: Optional[int] = Field(default=None, description="ID du document")
    
    penalite_jour: Optional[float] = Field(default=None, description="Pénalité par jour")
    penalite_maximale: Optional[float] = Field(default=None, description="Pénalité maximale")
    penalite_encourue: Optional[float] = Field(default=None, description="Pénalité réellement encourue")
    
    notifier_responsable: bool = Field(default=True, description="Notifier le responsable")
    notifier_equipe: bool = Field(default=False, description="Notifier l'équipe")
    notifier_client: bool = Field(default=False, description="Notifier le client")
    
    reference: Optional[str] = Field(default=None, description="Référence externe")
    commentaire: Optional[str] = Field(default=None, description="Commentaires")
    metadata: Optional[dict] = Field(default=None, description="Métadonnées")
    
    # Champs calculés
    jours_restants: Optional[int] = Field(default=None, description="Jours restants avant échéance")
    heures_restantes: Optional[int] = Field(default=None, description="Heures restantes avant échéance")
    est_depasee: bool = Field(..., description="Indique si la deadline est dépassée")
    jours_retard: Optional[int] = Field(default=None, description="Jours de retard (si dépassée)")
    
    created_at: datetime = Field(..., description="Date de création")
    updated_at: datetime = Field(..., description="Date de mise à jour")
    
    model_config = ConfigDict(from_attributes=True, json_schema_extra={
        "example": {
            "id": 1,
            "code": "DL-2026-001",
            "titre": "Dépôt dossier permis de construire",
            "type": "reglementaire",
            "statut": "proche",
            "priorite": "elevee",
            "date_echeance": "2026-12-31",
            "jours_restants": 15,
            "est_depasee": False
        }
    })


class DeadlineListResponse(BaseModel):
    """Schéma de liste de deadlines."""
    deadlines: List[DeadlineResponse] = Field(..., description="Liste des deadlines")
    total: int = Field(..., description="Nombre total de deadlines")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "deadlines": [],
            "total": 0
        }
    })


class DeadlineFilter(BaseModel):
    """Schéma de filtrage des deadlines."""
    mission_id: Optional[int] = Field(default=None, description="Filtrer par mission")
    lot_id: Optional[int] = Field(default=None, description="Filtrer par lot")
    type: Optional[DeadlineType] = Field(default=None, description="Filtrer par type")
    statut: Optional[DeadlineStatut] = Field(default=None, description="Filtrer par statut")
    priorite: Optional[DeadlinePriorite] = Field(default=None, description="Filtrer par priorité")
    
    responsable_id: Optional[int] = Field(default=None, description="Filtrer par responsable")
    projet_id: Optional[int] = Field(default=None, description="Filtrer par projet")
    contrat_id: Optional[int] = Field(default=None, description="Filtrer par contrat")
    
    date_debut: Optional[date] = Field(default=None, description="Date de début")
    date_fin: Optional[date] = Field(default=None, description="Date de fin")
    
    est_depasee: Optional[bool] = Field(default=None, description="Filtrer par deadline dépassée")
    jours_restants_max: Optional[int] = Field(default=None, ge=0, description="Maximum de jours restants")
    
    page: int = Field(default=1, ge=1, description="Numéro de page")
    per_page: int = Field(default=50, ge=1, le=1000, description="Éléments par page")


__all__ = [
    'DeadlineType', 'DeadlineStatut', 'DeadlinePriorite',
    'DeadlineBase', 'DeadlineCreate', 'DeadlineUpdate', 'DeadlineResponse',
    'DeadlineListResponse', 'DeadlineFilter'
]


