"""
SMART_AO V7 - certif.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Certification Schemas - Schémas Pydantic pour les certifications
Source: ARCHITECTURE_V7_ENGINE.md §3.2
"""

from datetime import date, datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing_extensions import Annotated


class CertificationType(str, Enum):
    """Types de certifications reconnues dans le BTP."""
    QUALIBAT = "qualibat"
    RGE = "rge"
    QUALIFELEC = "qualifelec"
    QUALIBAT_ECO = "qualibat_eco"
    CSTB = "cstb"
    CE = "ce"
    NF = "nf"
    ATEX = "atex"
    ISO_9001 = "iso_9001"
    ISO_14001 = "iso_14001"
    ISO_45001 = "iso_45001"
    AUTRE = "autre"


class CertificationStatut(str, Enum):
    """Statuts possibles pour une certification."""
    EN_COURS = "en_cours"
    VALIDE = "valide"
    EXPIREE = "expiree"
    SUSPENDUE = "suspendue"
    RETIREE = "retiree"


class CertificationBase(BaseModel):
    """Schéma de base pour une certification."""
    type: CertificationType = Field(..., description="Type de certification")
    nom: str = Field(..., min_length=1, max_length=200, description="Nom de la certification")
    numero: str = Field(..., min_length=1, max_length=100, description="Numéro unique de la certification")
    statut: CertificationStatut = Field(default=CertificationStatut.VALIDE, description="Statut de la certification")
    
    organisme: Optional[str] = Field(default=None, max_length=100, description="Organisme certificateur")
    domaine: Optional[str] = Field(default=None, max_length=100, description="Domaine technique couvert")
    niveau: Optional[str] = Field(default=None, max_length=50, description="Niveau ou classe")
    
    date_obtention: Optional[date] = Field(default=None, description="Date d'obtention")
    date_expiration: Optional[date] = Field(default=None, description="Date d'expiration")
    date_renouvellement: Optional[date] = Field(default=None, description="Date de renouvellement")
    
    commentaire: Optional[str] = Field(default=None, description="Commentaires")
    document_path: Optional[str] = Field(default=None, max_length=255, description="Chemin du document")
    
    est_critique: bool = Field(default=False, description="Indique si la certification est critique")
    est_actif: bool = Field(default=True, description="Indique si la certification est active")
    metadata: Optional[dict] = Field(default=None, description="Métadonnées supplémentaires")


class CertificationCreate(CertificationBase):
    """Schéma pour la création d'une certification."""
    entreprise_id: Optional[int] = Field(default=1, description="ID de l'entreprise")


class CertificationUpdate(BaseModel):
    """Schéma pour la mise à jour d'une certification."""
    type: Optional[CertificationType] = None
    nom: Optional[str] = Field(default=None, min_length=1, max_length=200)
    numero: Optional[str] = Field(default=None, min_length=1, max_length=100)
    statut: Optional[CertificationStatut] = None
    
    organisme: Optional[str] = Field(default=None, max_length=100)
    domaine: Optional[str] = Field(default=None, max_length=100)
    niveau: Optional[str] = Field(default=None, max_length=50)
    
    date_obtention: Optional[date] = None
    date_expiration: Optional[date] = None
    date_renouvellement: Optional[date] = None
    
    commentaire: Optional[str] = None
    document_path: Optional[str] = Field(default=None, max_length=255)
    
    est_critique: Optional[bool] = None
    est_actif: Optional[bool] = None
    metadata: Optional[dict] = None


class CertificationResponse(CertificationBase):
    """Schéma de réponse pour une certification."""
    id: int = Field(..., description="Identifiant unique")
    entreprise_id: int = Field(default=1, description="ID de l'entreprise")
    
    est_valide: bool = Field(..., description="Indique si la certification est valide")
    jours_restants: Optional[int] = Field(default=None, description="Jours restants avant expiration")
    est_bientot_expirée: bool = Field(default=False, description="Indique si expiration dans < 30 jours")
    
    created_at: datetime = Field(..., description="Date de création")
    updated_at: datetime = Field(..., description="Date de mise à jour")
    
    model_config = ConfigDict(from_attributes=True, json_schema_extra={
        "example": {
            "id": 1,
            "type": "qualibat",
            "nom": "Qualibat RGE",
            "numero": "RGE-2026-001",
            "statut": "valide",
            "organisme": "QUALIBAT",
            "domaine": "Isolation thermique",
            "niveau": "1",
            "date_obtention": "2024-01-15",
            "date_expiration": "2027-01-15",
            "est_valide": True,
            "jours_restants": 365,
            "est_critique": True
        }
    })


class CertificationListResponse(BaseModel):
    """Schéma de liste de certifications."""
    certifications: List[CertificationResponse] = Field(..., description="Liste des certifications")
    total: int = Field(..., description="Nombre total de certifications")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "certifications": [],
            "total": 0
        }
    })


class AlerteCertificationBase(BaseModel):
    """Schéma de base pour une alerte de certification."""
    certification_id: int = Field(..., description="ID de la certification concernée")
    type_alerte: str = Field(..., description="Type d'alerte")
    niveau: str = Field(..., description="Niveau de criticité")
    message: str = Field(..., description="Message de l'alerte")
    actions_requises: List[str] = Field(default_factory=list, description="Actions requises")


class AlerteCertificationResponse(AlerteCertificationBase):
    """Schéma de réponse pour une alerte."""
    alerte_id: str = Field(..., description="Identifiant unique de l'alerte")
    date_declenchement: datetime = Field(..., description="Date de déclenchement")
    statu: str = Field(default="active", description="Statut de l'alerte")


class AlerteCertificationListResponse(BaseModel):
    """Schéma de liste d'alertes."""
    alertes: List[AlerteCertificationResponse] = Field(..., description="Liste des alertes")
    total: int = Field(..., description="Nombre total d'alertes")
    nb_critiques: int = Field(default=0, description="Nombre d'alertes critiques")


class RapportCertifications(BaseModel):
    """Schéma de rapport complet des certifications."""
    rapport_id: str = Field(..., description="ID du rapport")
    mission_id: Optional[int] = Field(default=None, description="ID de la mission")
    date_rapport: datetime = Field(..., description="Date du rapport")
    
    nb_certifs_valides: int = Field(..., description="Nombre de certifications valides")
    nb_certifs_expirees: int = Field(..., description="Nombre de certifications expirées")
    nb_alertes_critiques: int = Field(..., description="Nombre d'alertes critiques")
    
    certifications: List[CertificationResponse] = Field(default_factory=list, description="Liste des certifications")
    alertes: List[AlerteCertificationResponse] = Field(default_factory=list, description="Liste des alertes")


# Schémas pour les requêtes de filtrage
class CertificationFilter(BaseModel):
    """Schéma de filtrage des certifications."""
    type: Optional[CertificationType] = Field(default=None, description="Filtrer par type")
    statut: Optional[CertificationStatut] = Field(default=None, description="Filtrer par statut")
    est_valide: Optional[bool] = Field(default=None, description="Filtrer par validité")
    est_critique: Optional[bool] = Field(default=None, description="Filtrer par criticité")
    organisme: Optional[str] = Field(default=None, description="Filtrer par organisme")
    
    page: int = Field(default=1, ge=1, description="Numéro de page")
    per_page: int = Field(default=50, ge=1, le=1000, description="Éléments par page")


# Schémas pour les notifications
class CertificationNotification(BaseModel):
    """Schéma pour les notifications de certification."""
    certification_id: int = Field(..., description="ID de la certification")
    event_type: str = Field(..., description="Type d'événement")
    message: str = Field(..., description="Message de notification")
    recipients: List[str] = Field(default_factory=list, description="Destinataires")


__all__ = [
    'CertificationType', 'CertificationStatut',
    'CertificationBase', 'CertificationCreate', 'CertificationUpdate',
    'CertificationResponse', 'CertificationListResponse',
    'AlerteCertificationBase', 'AlerteCertificationResponse',
    'AlerteCertificationListResponse', 'RapportCertifications',
    'CertificationFilter', 'CertificationNotification'
]

