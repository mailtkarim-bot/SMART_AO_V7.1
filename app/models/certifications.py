"""
SMART_AO V7 - certifications.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 09/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - Certifications Model
==================================
Modèle SQLAlchemy pour la gestion des certifications (Qualibat, RGE, etc.)
Source: ARCHITECTURE_V7_ENGINE.md §3.2
"""

from datetime import date, datetime
from typing import Optional, List
from enum import Enum

from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship, declarative_base

from app.core.database import Base


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


class CertificationStatus(str, Enum):
    """Statuts possibles pour une certification."""
    EN_COURS = "en_cours"
    VALIDE = "valide"
    EXPIREE = "expiree"
    SUSPENDUE = "suspendue"
    RETIREE = "retiree"


class Certification(Base):
    """
    Modèle des certifications d'une entreprise.
    
    Une certification est un document officiel qui atteste des compétences
    d'une entreprise dans un domaine spécifique (ex: Qualibat RGE pour les
    travaux d'isolation).
    
    Attributes:
        id: Identifiant unique
        entreprise_id: Référence vers l'entreprise (single-tenant: toujours 1)
        type: Type de certification (Qualibat, RGE, etc.)
        numero: Numéro de la certification
        statut: Statut actuel (valide, expirée, etc.)
        date_obtention: Date d'obtention de la certification
        date_expiration: Date d'expiration de la certification
        organisme: Organisme certificateur
        domaine: Domaine technique couvert
        niveau: Niveau ou classe de la certification
        commentaire: Commentaires divers
        document_path: Chemin vers le document de certification
        est_critique: Indique si cette certification est critique
        metadata: Métadonnées supplémentaires en JSON
    """
    
    __tablename__ = "certifications"
    
    id = Column(Integer, primary_key=True, index=True)
    
    entreprise_id = Column(Integer, nullable=True, default=1)
    
    type = Column(String(50), nullable=False, index=True)
    numero = Column(String(100), nullable=False, unique=True, index=True)
    statut = Column(String(20), default=CertificationStatus.VALIDE.value, index=True)
    
    date_obtention = Column(Date, nullable=True)
    date_expiration = Column(Date, nullable=True, index=True)
    date_renouvellement = Column(Date, nullable=True)
    
    organisme = Column(String(100), nullable=True)
    domaine = Column(String(100), nullable=True, index=True)
    niveau = Column(String(50), nullable=True)
    
    commentaire = Column(Text, nullable=True)
    
    document_path = Column(String(255), nullable=True)
    
    est_critique = Column(Boolean, default=False, index=True)
    est_actif = Column(Boolean, default=True, index=True)
    
    metadata = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Certification(type={self.type}, numero={self.numero}, statut={self.statut})>"
    
    @property
    def est_valide(self) -> bool:
        """Vérifie si la certification est actuellement valide."""
        if self.statut != CertificationStatus.VALIDE.value:
            return False
        if self.date_expiration and self.date_expiration < date.today():
            return False
        return self.est_actif
    
    @property
    def jours_restants(self) -> Optional[int]:
        """Calcule le nombre de jours restants avant expiration."""
        if not self.date_expiration:
            return None
        return (self.date_expiration - date.today()).days
    
    @property
    def est_bientot_expirée(self) -> bool:
        """Vérifie si la certification expire dans moins de 30 jours."""
        jours = self.jours_restants
        return jours is not None and 0 <= jours <= 30
    
    def to_dict(self) -> dict:
        """Convertit l'objet en dictionnaire pour l'API."""
        return {
            "id": self.id,
            "type": self.type,
            "numero": self.numero,
            "statut": self.statut,
            "organisme": self.organisme,
            "domaine": self.domaine,
            "niveau": self.niveau,
            "date_obtention": self.date_obtention.isoformat() if self.date_obtention else None,
            "date_expiration": self.date_expiration.isoformat() if self.date_expiration else None,
            "date_renouvellement": self.date_renouvellement.isoformat() if self.date_renouvellement else None,
            "est_valide": self.est_valide,
            "jours_restants": self.jours_restants,
            "est_critique": self.est_critique,
            "commentaire": self.commentaire,
            "document_path": self.document_path,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

