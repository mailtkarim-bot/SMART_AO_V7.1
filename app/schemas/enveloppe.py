"""
SMART_AO V7 - enveloppe.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Enveloppe Schemas - Schémas Pydantic pour la gestion des enveloppes budgétaires
Source: ARCHITECTURE_V7_ENGINE.md §3.2
"""

from datetime import date, datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class EnveloppeType(str, Enum):
    """Types d'enveloppes budgétaires."""
    GLOBALE = "globale"
    MISSION = "mission"
    LOT = "lot"
    POSTE = "poste"
    PHASE = "phase"
    SOUS_TRAITANCE = "sous_traitance"
    ACHATS = "achats"
    FRAIS_GENERAUX = "frais_generaux"


class EnveloppeStatut(str, Enum):
    """Statuts des enveloppes."""
    PREVISIONNELLE = "previsionnelle"
    VALIDEE = "validee"
    ENGAGEE = "engagee"
    REALISEE = "realisee"
    DEPASSEE = "depasee"
    ANNULEE = "annulee"
    CLOTUREE = "cloturee"


class EnveloppeOrigine(str, Enum):
    """Origines des enveloppes."""
    DEVIS = "devis"
    COMMANDE = "commande"
    MARCHE = "marche"
    CONTRAT = "contrat"
    BUDGET = "budget"
    REVISION = "revision"
    COMPLEMENT = "complement"


class EnveloppeBase(BaseModel):
    """Schéma de base pour une enveloppe budgétaire."""
    code: str = Field(..., min_length=1, max_length=50, description="Code unique de l'enveloppe")
    libelle: str = Field(..., min_length=1, max_length=200, description="Libellé de l'enveloppe")
    description: Optional[str] = Field(default=None, description="Description détaillée")
    
    type: EnveloppeType = Field(default=EnveloppeType.MISSION, description="Type d'enveloppe")
    statut: EnveloppeStatut = Field(default=EnveloppeStatut.PREVISIONNELLE, description="Statut actuel")
    origine: EnveloppeOrigine = Field(default=EnveloppeOrigine.DEVIS, description="Origine de l'enveloppe")
    
    budget_previsionnel: float = Field(default=0.0, ge=0.0, description="Budget prévisionnel")
    budget_valide: float = Field(default=0.0, ge=0.0, description="Budget validé")
    budget_engage: float = Field(default=0.0, ge=0.0, description="Budget engagé")
    budget_realise: float = Field(default=0.0, ge=0.0, description="Budget réalisé")
    
    pourcentage_avancement: float = Field(default=0.0, ge=0.0, le=100.0, description="Pourcentage d'avancement")


class EnveloppeCreate(EnveloppeBase):
    """Schéma pour la création d'une enveloppe."""
    mission_id: Optional[int] = Field(default=None, description="ID de la mission associée")
    lot_id: Optional[int] = Field(default=None, description="ID du lot concerné")
    projet_id: Optional[int] = Field(default=None, description="ID du projet")
    entreprise_id: Optional[int] = Field(default=1, description="ID de l'entreprise")
    
    date_debut: Optional[date] = Field(default=None, description="Date de début de validité")
    date_fin: Optional[date] = Field(default=None, description="Date de fin de validité")
    date_validation: Optional[date] = Field(default=None, description="Date de validation")
    
    responsable_id: Optional[int] = Field(default=None, description="ID du responsable")
    responsable_nom: Optional[str] = Field(default=None, max_length=100, description="Nom du responsable")
    
    # Références
    reference: Optional[str] = Field(default=None, max_length=100, description="Référence externe")
    reference_contrat: Optional[str] = Field(default=None, max_length=100, description="Référence du contrat")
    reference_devis: Optional[str] = Field(default=None, max_length=100, description="Référence du devis")
    
    # Répartition
    sous_enveloppes: Optional[List[dict]] = Field(default=None, description="Liste des sous-enveloppes")
    
    # TVA
    tva_taux: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="Taux de TVA (%)")
    
    # Suivi
    ecarts: Optional[List[dict]] = Field(default=None, description="Liste des écarts constates")
    alertes: Optional[List[dict]] = Field(default=None, description="Liste des alertes")
    
    commentaire: Optional[str] = Field(default=None, description="Commentaires")
    metadata: Optional[dict] = Field(default=None, description="Métadonnées supplémentaires")


class EnveloppeUpdate(BaseModel):
    """Schéma pour la mise à jour d'une enveloppe."""
    code: Optional[str] = Field(default=None, min_length=1, max_length=50)
    libelle: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    
    type: Optional[EnveloppeType] = None
    statut: Optional[EnveloppeStatut] = None
    origine: Optional[EnveloppeOrigine] = None
    
    budget_previsionnel: Optional[float] = Field(default=None, ge=0.0)
    budget_valide: Optional[float] = Field(default=None, ge=0.0)
    budget_engage: Optional[float] = Field(default=None, ge=0.0)
    budget_realise: Optional[float] = Field(default=None, ge=0.0)
    
    pourcentage_avancement: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    
    mission_id: Optional[int] = None
    lot_id: Optional[int] = None
    projet_id: Optional[int] = None
    
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    date_validation: Optional[date] = None
    
    responsable_id: Optional[int] = None
    responsable_nom: Optional[str] = Field(default=None, max_length=100)
    
    reference: Optional[str] = Field(default=None, max_length=100)
    reference_contrat: Optional[str] = Field(default=None, max_length=100)
    reference_devis: Optional[str] = Field(default=None, max_length=100)
    
    sous_enveloppes: Optional[List[dict]] = None
    tva_taux: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    
    ecarts: Optional[List[dict]] = None
    alertes: Optional[List[dict]] = None
    
    commentaire: Optional[str] = None
    metadata: Optional[dict] = None


class EnveloppeResponse(EnveloppeBase):
    """Schéma de réponse pour une enveloppe."""
    id: int = Field(..., description="Identifiant unique")
    mission_id: Optional[int] = Field(default=None, description="ID de la mission")
    lot_id: Optional[int] = Field(default=None, description="ID du lot")
    projet_id: Optional[int] = Field(default=None, description="ID du projet")
    entreprise_id: Optional[int] = Field(default=1, description="ID de l'entreprise")
    
    date_debut: Optional[date] = Field(default=None, description="Date de début")
    date_fin: Optional[date] = Field(default=None, description="Date de fin")
    date_validation: Optional[date] = Field(default=None, description="Date de validation")
    date_cloture: Optional[date] = Field(default=None, description="Date de clôture")
    
    responsable_id: Optional[int] = Field(default=None, description="ID du responsable")
    responsable_nom: Optional[str] = Field(default=None, description="Nom du responsable")
    
    reference: Optional[str] = Field(default=None, description="Référence externe")
    reference_contrat: Optional[str] = Field(default=None, description="Référence du contrat")
    reference_devis: Optional[str] = Field(default=None, description="Référence du devis")
    
    sous_enveloppes: Optional[List[dict]] = Field(default=None, description="Sous-enveloppes")
    tva_taux: Optional[float] = Field(default=None, description="Taux de TVA")
    
    ecarts: Optional[List[dict]] = Field(default=None, description="Écarts")
    alertes: Optional[List[dict]] = Field(default=None, description="Alertes")
    
    commentaire: Optional[str] = Field(default=None, description="Commentaires")
    metadata: Optional[dict] = Field(default=None, description="Métadonnées")
    
    # Champs calculés
    budget_restant: float = Field(default=0.0, description="Budget restant à engager")
    ecart_absolu: float = Field(default=0.0, description="Écart absolu entre validé et réalisé")
    ecart_relatif: float = Field(default=0.0, description="Écart relatif en pourcentage")
    
    est_depasse: bool = Field(..., description="Indique si l'enveloppe est dépassée")
    est_fermee: bool = Field(..., description="Indique si l'enveloppe est fermée")
    
    created_at: datetime = Field(..., description="Date de création")
    updated_at: datetime = Field(..., description="Date de mise à jour")
    
    model_config = ConfigDict(from_attributes=True, json_schema_extra={
        "example": {
            "id": 1,
            "code": "ENV-2026-001",
            "libelle": "Enveloppe Mission ABC",
            "type": "mission",
            "statut": "validee",
            "budget_previsionnel": 1000000.0,
            "budget_valide": 950000.0,
            "budget_realise": 450000.0,
            "pourcentage_avancement": 47.37,
            "est_depasse": False
        }
    })


class EnveloppeListResponse(BaseModel):
    """Schéma de liste d'enveloppes."""
    enveloppes: List[EnveloppeResponse] = Field(..., description="Liste des enveloppes")
    total: int = Field(..., description="Nombre total d'enveloppes")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "enveloppes": [],
            "total": 0
        }
    })


class EnveloppeFilter(BaseModel):
    """Schéma de filtrage des enveloppes."""
    mission_id: Optional[int] = Field(default=None, description="Filtrer par mission")
    lot_id: Optional[int] = Field(default=None, description="Filtrer par lot")
    projet_id: Optional[int] = Field(default=None, description="Filtrer par projet")
    type: Optional[EnveloppeType] = Field(default=None, description="Filtrer par type")
    statut: Optional[EnveloppeStatut] = Field(default=None, description="Filtrer par statut")
    origine: Optional[EnveloppeOrigine] = Field(default=None, description="Filtrer par origine")
    
    responsable_id: Optional[int] = Field(default=None, description="Filtrer par responsable")
    
    budget_min: Optional[float] = Field(default=None, ge=0.0, description="Budget minimum")
    budget_max: Optional[float] = Field(default=None, ge=0.0, description="Budget maximum")
    
    date_debut: Optional[date] = Field(default=None, description="Date de début")
    date_fin: Optional[date] = Field(default=None, description="Date de fin")
    
    est_depasse: Optional[bool] = Field(default=None, description="Filtrer par enveloppe dépassée")
    est_fermee: Optional[bool] = Field(default=None, description="Filtrer par enveloppe fermée")
    
    page: int = Field(default=1, ge=1, description="Numéro de page")
    per_page: int = Field(default=50, ge=1, le=1000, description="Éléments par page")


class EcartEnveloppe(BaseModel):
    """Schéma pour un écart d'enveloppe."""
    type: str = Field(..., description="Type d'écart")
    montant: float = Field(..., description="Montant de l'écart")
    pourcentage: float = Field(..., description="Pourcentage de l'écart")
    cause: Optional[str] = Field(default=None, description="Cause de l'écart")
    date_constat: date = Field(..., description="Date de constat")
    action_corrective: Optional[str] = Field(default=None, description="Action corrective")
    
    model_config = ConfigDict(from_attributes=True)


class AlerteEnveloppe(BaseModel):
    """Schéma pour une alerte d'enveloppe."""
    type: str = Field(..., description="Type d'alerte")
    niveau: str = Field(..., description="Niveau de sévérité")
    message: str = Field(..., description="Message d'alerte")
    seuil: float = Field(..., description="Seuil déclencheur")
    date_declenchement: datetime = Field(..., description="Date de déclenchement")
    
    model_config = ConfigDict(from_attributes=True)


__all__ = [
    'EnveloppeType', 'EnveloppeStatut', 'EnveloppeOrigine',
    'EnveloppeBase', 'EnveloppeCreate', 'EnveloppeUpdate', 'EnveloppeResponse',
    'EnveloppeListResponse', 'EnveloppeFilter', 'EcartEnveloppe', 'AlerteEnveloppe'
]


