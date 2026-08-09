"""
SMART_AO V7 - event.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Event Schemas - Schémas Pydantic pour la gestion des événements et du journal d'activité
Source: ARCHITECTURE_V7_ENGINE.md §3.2
"""

from datetime import date, datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class EventType(str, Enum):
    """Types d'événements."""
    CREATION = "creation"
    MODIFICATION = "modification"
    SUPPRESSION = "suppression"
    VALIDATION = "validation"
    SIGNATURE = "signature"
    EXPORT = "export"
    IMPORT = "import"
    SYNCHRONISATION = "synchronisation"
    NOTIFICATION = "notification"
    ERREUR = "erreur"
    AVERTISSEMENT = "avertissement"
    INFORMATION = "information"
    ACTION = "action"
    DECISION = "decision"


class EventCategorie(str, Enum):
    """Catégories d'événements."""
    MISSION = "mission"
    LOT = "lot"
    CHIFFRAGE = "chiffrage"
    DEADLINE = "deadline"
    ENVELOPPE = "enveloppe"
    RISQUE = "risque"
    CONTENTIEUX = "contentieux"
    DOCUMENT = "document"
    UTILISATEUR = "utilisateur"
    SYSTEME = "systeme"
    SECURITE = "securite"
    INTEGRATION = "integration"


class EventNiveau(str, Enum):
    """Niveaux de sévérité des événements."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class EventStatut(str, Enum):
    """Statuts des événements."""
    NOUVEAU = "nouveau"
    LU = "lu"
    TRAITE = "traite"
    ARCHIVE = "archive"


class EventBase(BaseModel):
    """Schéma de base pour un événement."""
    code: str = Field(..., min_length=1, max_length=50, description="Code unique de l'événement")
    titre: str = Field(..., min_length=1, max_length=200, description="Titre de l'événement")
    message: str = Field(..., min_length=1, description="Message détaillé de l'événement")
    
    type: EventType = Field(default=EventType.INFORMATION, description="Type d'événement")
    categorie: EventCategorie = Field(default=EventCategorie.SYSTEME, description="Catégorie de l'événement")
    niveau: EventNiveau = Field(default=EventNiveau.INFO, description="Niveau de sévérité")
    statut: EventStatut = Field(default=EventStatut.NOUVEAU, description="Statut de l'événement")
    
    date_evenement: datetime = Field(..., description="Date et heure de l'événement")


class EventCreate(EventBase):
    """Schéma pour la création d'un événement."""
    mission_id: Optional[int] = Field(default=None, description="ID de la mission concernée")
    lot_id: Optional[int] = Field(default=None, description="ID du lot concerné")
    projet_id: Optional[int] = Field(default=None, description="ID du projet concerné")
    entreprise_id: Optional[int] = Field(default=1, description="ID de l'entreprise")
    
    utilisateur_id: Optional[int] = Field(default=None, description="ID de l'utilisateur")
    utilisateur_nom: Optional[str] = Field(default=None, max_length=100, description="Nom de l'utilisateur")
    utilisateur_email: Optional[str] = Field(default=None, max_length=255, description="Email de l'utilisateur")
    
    # Contexte
    ip_address: Optional[str] = Field(default=None, max_length=45, description="Adresse IP")
    user_agent: Optional[str] = Field(default=None, description="User Agent")
    endpoint: Optional[str] = Field(default=None, max_length=500, description="Endpoint API")
    
    # Liens
    entite_id: Optional[int] = Field(default=None, description="ID de l'entité concernée")
    entite_type: Optional[str] = Field(default=None, max_length=50, description="Type de l'entité concernée")
    
    # Données avant/après (pour modifications)
    old_values: Optional[dict] = Field(default=None, description="Anciennes valeurs (pour modification)")
    new_values: Optional[dict] = Field(default=None, description="Nouvelles valeurs (pour modification)")
    
    # Pièces jointes
    documents: Optional[List[str]] = Field(default=None, description="Liste des documents associés")
    
    # Métadonnées
    tags: Optional[List[str]] = Field(default=None, description="Tags pour classification")
    reference: Optional[str] = Field(default=None, max_length=100, description="Référence externe")
    metadata: Optional[dict] = Field(default=None, description="Métadonnées supplémentaires")


class EventUpdate(BaseModel):
    """Schéma pour la mise à jour d'un événement."""
    titre: Optional[str] = Field(default=None, min_length=1, max_length=200)
    message: Optional[str] = Field(default=None, min_length=1)
    
    type: Optional[EventType] = None
    categorie: Optional[EventCategorie] = None
    niveau: Optional[EventNiveau] = None
    statut: Optional[EventStatut] = None
    
    mission_id: Optional[int] = None
    lot_id: Optional[int] = None
    projet_id: Optional[int] = None
    
    utilisateur_id: Optional[int] = None
    utilisateur_nom: Optional[str] = Field(default=None, max_length=100)
    
    entite_id: Optional[int] = None
    entite_type: Optional[str] = Field(default=None, max_length=50)
    
    old_values: Optional[dict] = None
    new_values: Optional[dict] = None
    
    documents: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    reference: Optional[str] = Field(default=None, max_length=100)
    metadata: Optional[dict] = None


class EventResponse(EventBase):
    """Schéma de réponse pour un événement."""
    id: int = Field(..., description="Identifiant unique")
    mission_id: Optional[int] = Field(default=None, description="ID de la mission")
    lot_id: Optional[int] = Field(default=None, description="ID du lot")
    projet_id: Optional[int] = Field(default=None, description="ID du projet")
    entreprise_id: Optional[int] = Field(default=1, description="ID de l'entreprise")
    
    utilisateur_id: Optional[int] = Field(default=None, description="ID de l'utilisateur")
    utilisateur_nom: Optional[str] = Field(default=None, description="Nom de l'utilisateur")
    utilisateur_email: Optional[str] = Field(default=None, description="Email de l'utilisateur")
    
    ip_address: Optional[str] = Field(default=None, description="Adresse IP")
    user_agent: Optional[str] = Field(default=None, description="User Agent")
    endpoint: Optional[str] = Field(default=None, description="Endpoint API")
    
    entite_id: Optional[int] = Field(default=None, description="ID de l'entité")
    entite_type: Optional[str] = Field(default=None, description="Type de l'entité")
    
    old_values: Optional[dict] = Field(default=None, description="Anciennes valeurs")
    new_values: Optional[dict] = Field(default=None, description="Nouvelles valeurs")
    
    documents: Optional[List[str]] = Field(default=None, description="Documents associés")
    tags: Optional[List[str]] = Field(default=None, description="Tags")
    reference: Optional[str] = Field(default=None, description="Référence externe")
    metadata: Optional[dict] = Field(default=None, description="Métadonnées")
    
    # Champs calculés
    est_nouveau: bool = Field(..., description="Indique si l'événement est nouveau")
    est_lu: bool = Field(..., description="Indique si l'événement a été lu")
    
    created_at: datetime = Field(..., description="Date de création")
    updated_at: datetime = Field(..., description="Date de mise à jour")
    
    model_config = ConfigDict(from_attributes=True, json_schema_extra={
        "example": {
            "id": 1,
            "code": "EVT-2026-001",
            "titre": "Création mission XYZ",
            "message": "Une nouvelle mission a été créée",
            "type": "creation",
            "categorie": "mission",
            "niveau": "info",
            "statut": "nouveau",
            "date_evenement": "2026-08-09T10:00:00"
        }
    })


class EventListResponse(BaseModel):
    """Schéma de liste d'événements."""
    events: List[EventResponse] = Field(..., description="Liste des événements")
    total: int = Field(..., description="Nombre total d'événements")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "events": [],
            "total": 0
        }
    })


class EventFilter(BaseModel):
    """Schéma de filtrage des événements."""
    mission_id: Optional[int] = Field(default=None, description="Filtrer par mission")
    lot_id: Optional[int] = Field(default=None, description="Filtrer par lot")
    projet_id: Optional[int] = Field(default=None, description="Filtrer par projet")
    type: Optional[EventType] = Field(default=None, description="Filtrer par type")
    categorie: Optional[EventCategorie] = Field(default=None, description="Filtrer par catégorie")
    niveau: Optional[EventNiveau] = Field(default=None, description="Filtrer par niveau")
    statut: Optional[EventStatut] = Field(default=None, description="Filtrer par statut")
    
    utilisateur_id: Optional[int] = Field(default=None, description="Filtrer par utilisateur")
    entite_id: Optional[int] = Field(default=None, description="Filtrer par entité")
    entite_type: Optional[str] = Field(default=None, max_length=50, description="Filtrer par type d'entité")
    
    date_debut: Optional[datetime] = Field(default=None, description="Date de début")
    date_fin: Optional[datetime] = Field(default=None, description="Date de fin")
    
    est_lu: Optional[bool] = Field(default=None, description="Filtrer par statut lu/non lu")
    
    tags: Optional[List[str]] = Field(default=None, description="Filtrer par tags")
    
    page: int = Field(default=1, ge=1, description="Numéro de page")
    per_page: int = Field(default=50, ge=1, le=1000, description="Éléments par page")


class AuditLog(BaseModel):
    """Schéma pour le journal d'audit."""
    event_id: int = Field(..., description="ID de l'événement")
    action: str = Field(..., description="Action effectuée")
    resource: str = Field(..., description="Ressource concernée")
    resource_id: int = Field(..., description="ID de la ressource")
    
    utilisateur_id: Optional[int] = Field(default=None, description="ID de l'utilisateur")
    timestamp: datetime = Field(..., description="Timestamp")
    old_value: Optional[dict] = Field(default=None, description="Ancienne valeur")
    new_value: Optional[dict] = Field(default=None, description="Nouvelle valeur")
    
    model_config = ConfigDict(from_attributes=True)


__all__ = [
    'EventType', 'EventCategorie', 'EventNiveau', 'EventStatut',
    'EventBase', 'EventCreate', 'EventUpdate', 'EventResponse',
    'EventListResponse', 'EventFilter', 'AuditLog'
]


