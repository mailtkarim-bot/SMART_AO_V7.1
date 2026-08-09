"""
SMART_AO V7 - contentieux.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Contentieux Model - Gestion des litiges et contentieux juridiques
Source: ARCHITECTURE_V7_ENGINE.md §3.2
"""

from datetime import date, datetime
from typing import Optional, List
from enum import Enum

from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship, declarative_base

from app.core.database import Base


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


class Contentieux(Base):
    """
    Modèle des contentieux (litiges juridiques).
    
    Un contentieux représente un litige ou différend impliquant l'entreprise,
    un client, un fournisseur ou un partenaire. Ce modèle permet de suivre
    l'évolution des litiges et leurs résolutions.
    
    Attributes:
        id: Identifiant unique
        mission_id: Référence vers la mission concernée (si applicable)
        type: Type de contentieux
        titre: Titre résumant le contentieux
        description: Description détaillée du litige
        statut: Statut actuel
        priorite: Niveau de priorité
        montant_estime: Montant financier estimé du litige
        montant_reel: Montant réel final (si résolu)
        date_ouverture: Date d'ouverture du contentieux
        date_cloture: Date de clôture (si applicable)
        partie_adverse: Nom de la partie adverse
        responsable: Responsable du suivi interne
        avocat: Avocat ou conseil juridique assigné
        tribunal: Tribunal ou instance compétente
        reference_dossier: Référence du dossier juridique
        pieces_jointes: Liste des documents associés
        actions_prevues: Actions prévues pour résolution
        commentaire: Commentaires divers
        metadata: Métadonnées supplémentaires
    """
    
    __tablename__ = "contentieux"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Références
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=True, index=True)
    entreprise_id = Column(Integer, nullable=True, default=1)
    
    # Informations principales
    type = Column(String(50), nullable=False, index=True)
    titre = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Statut et priorité
    statut = Column(String(20), default=ContentieuxStatut.OUVERT.value, index=True)
    priorite = Column(String(20), default=ContentieuxPriorite.MOYENNE.value, index=True)
    
    # Montants (en euros)
    montant_estime = Column(Float, nullable=True, default=0.0)
    montant_reel = Column(Float, nullable=True)
    
    # Dates
    date_ouverture = Column(Date, nullable=False, index=True)
    date_cloture = Column(Date, nullable=True, index=True)
    date_echeance = Column(Date, nullable=True, index=True)  # Date limite pour action
    
    # Parties impliquées
    partie_adverse = Column(String(200), nullable=True)
    responsable = Column(String(100), nullable=True)
    avocat = Column(String(200), nullable=True)
    tribunal = Column(String(200), nullable=True)
    
    # Références
    reference_dossier = Column(String(100), nullable=True, unique=True)
    reference_contrat = Column(String(100), nullable=True)
    
    # Suivi
    pieces_jointes = Column(JSON, nullable=True)  # Liste des paths de fichiers
    actions_prevues = Column(JSON, nullable=True)  # Liste d'actions
    historique = Column(JSON, nullable=True)  # Historique des actions
    
    commentaire = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Contentieux(type={self.type}, titre={self.titre}, statut={self.statut})>"
    
    @property
    def est_actif(self) -> bool:
        """Vérifie si le contentieux est actif (non résolu/archivé)."""
        return self.statut in [ContentieuxStatut.OUVERT.value, ContentieuxStatut.EN_COURS.value, 
                               ContentieuxStatut.EN_MEDIATION.value, ContentieuxStatut.EN_ARBITRAGE.value,
                               ContentieuxStatut.EN_JUSTICE.value]
    
    @property
    def duree_jours(self) -> Optional[int]:
        """Calcule la durée du contentieux en jours."""
        if not self.date_ouverture:
            return None
        end_date = self.date_cloture or date.today()
        return (end_date - self.date_ouverture).days
    
    @property
    def est_urgent(self) -> bool:
        """Vérifie si le contentieux est urgent."""
        if self.priorite == ContentieuxPriorite.CRITIQUE.value:
            return True
        if self.date_echeance and (self.date_echeance - date.today()).days <= 7:
            return True
        return False
    
    def to_dict(self) -> dict:
        """Convertit l'objet en dictionnaire pour l'API."""
        return {
            "id": self.id,
            "mission_id": self.mission_id,
            "type": self.type,
            "titre": self.titre,
            "description": self.description,
            "statut": self.statut,
            "priorite": self.priorite,
            "montant_estime": self.montant_estime,
            "montant_reel": self.montant_reel,
            "date_ouverture": self.date_ouverture.isoformat() if self.date_ouverture else None,
            "date_cloture": self.date_cloture.isoformat() if self.date_cloture else None,
            "date_echeance": self.date_echeance.isoformat() if self.date_echeance else None,
            "duree_jours": self.duree_jours,
            "partie_adverse": self.partie_adverse,
            "responsable": self.responsable,
            "avocat": self.avocat,
            "tribunal": self.tribunal,
            "reference_dossier": self.reference_dossier,
            "reference_contrat": self.reference_contrat,
            "est_actif": self.est_actif,
            "est_urgent": self.est_urgent,
            "pieces_jointes": self.pieces_jointes,
            "actions_prevues": self.actions_prevues,
            "commentaire": self.commentaire,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ContentieuxHistorique(Base):
    """
    Historique des actions sur un contentieux.
    
    Cette table permet de tracer toutes les actions, décisions et événements
    liés à un contentieux.
    """
    
    __tablename__ = "contentieux_historique"
    
    id = Column(Integer, primary_key=True, index=True)
    contentieux_id = Column(Integer, ForeignKey("contentieux.id"), nullable=False, index=True)
    
    # Action
    action = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    type_action = Column(String(50), nullable=True)  # email, reunion, courrier, etc.
    
    # Utilisateur
    utilisateur_id = Column(Integer, nullable=True)
    utilisateur_nom = Column(String(100), nullable=True)
    
    # Dates
    date_action = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Documents
    document_path = Column(String(255), nullable=True)
    
    # Métadonnées
    metadata = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<ContentieuxHistorique(contentieux_id={self.contentieux_id}, action={self.action})>"
    
    def to_dict(self) -> dict:
        """Convertit l'objet en dictionnaire."""
        return {
            "id": self.id,
            "contentieux_id": self.contentieux_id,
            "action": self.action,
            "description": self.description,
            "type_action": self.type_action,
            "utilisateur_id": self.utilisateur_id,
            "utilisateur_nom": self.utilisateur_nom,
            "date_action": self.date_action.isoformat() if self.date_action else None,
            "document_path": self.document_path,
            "metadata": self.metadata,
        }


# Relations (optionnel - à activer si les relations sont nécessaires)
# Contentieux.mission = relationship("Mission", back_populates="contentieux")
# Contentieux.historique = relationship("ContentieuxHistorique", backref="contentieux", lazy="dynamic")

