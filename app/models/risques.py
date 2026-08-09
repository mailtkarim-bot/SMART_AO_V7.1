"""
SMART_AO V7 - risques.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Risques Model - Gestion des risques projet dans la base de données
Source: ARCHITECTURE_V7_ENGINE.md §3.2
"""

from datetime import date, datetime
from typing import Optional, List
from enum import Enum

from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship, declarative_base

from app.core.database import Base


class RisqueType(str, Enum):
    """Types de risques."""
    TECHNIQUE = "technique"
    FINANCIER = "financier"
    REGLEMENTAIRE = "reglementaire"
    SECURITE = "securite"
    ENVIRONNEMENTAL = "environnemental"
    ORGANISATIONNEL = "organisationnel"
    JURIDIQUE = "juridique"


class RisqueNiveau(str, Enum):
    """Niveaux de risque."""
    FAIBLE = "faible"
    MOYEN = "moyen"
    ELEVE = "eleve"
    CRITIQUE = "critique"


class RisqueStatut(str, Enum):
    """Statuts des risques."""
    IDENTIFIE = "identifie"
    ANALYSE = "analyse"
    TRAITE = "traite"
    SURVEILLE = "surveille"
    FERME = "ferme"
    REOUVERT = "reouvert"


class Risque(Base):
    """
    Modèle des risques projet.
    
    Un risque représente un événement potentiel susceptible d'affecter
    le bon déroulement d'une mission. Ce modèle permet d'identifier,
    d'évaluer et de suivre les mesures de mitigation.
    
    Attributes:
        id: Identifiant unique
        mission_id: Référence vers la mission concernée
        lot_id: Référence vers le lot concerné (optionnel)
        
        # Identification
        code: Code unique du risque
        titre: Titre résumant le risque
        description: Description détaillée
        
        # Classification
        type: Type de risque
        niveau: Niveau de criticité
        statut: Statut actuel
        
        # Évaluation
        probabilite: Probabilité d'occurrence (0.0 - 1.0)
        impact: Impact potentiel (en euros ou score)
        score: Score calculé (probabilité * impact normalisé)
        
        # Mesures
        mitigation: Mesures de mitigation prévues
        plan_action: Plan d'action détaillé
        responsable: Responsable du suivi
        
        # Dates
        date_identification: Date d'identification
        date_echeance: Date limite pour action
        date_fermeture: Date de fermeture (si applicable)
        
        # Suivi
        est_actif: Indicateur d'activité
        est_accepté: Indicateur d'acceptation du risque
        commentaire: Commentaires
        metadata: Métadonnées supplémentaires
    """
    
    __tablename__ = "risques"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Références
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=True, index=True)
    lot_id = Column(Integer, ForeignKey("lots.id"), nullable=True, index=True)
    entreprise_id = Column(Integer, nullable=True, default=1)
    
    # Identification
    code = Column(String(50), nullable=False, index=True)
    titre = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Classification
    type = Column(String(50), default=RisqueType.TECHNIQUE.value, index=True)
    niveau = Column(String(20), default=RisqueNiveau.MOYEN.value, index=True)
    statut = Column(String(20), default=RisqueStatut.IDENTIFIE.value, index=True)
    
    # Évaluation
    probabilite = Column(Float, nullable=True, default=0.5)  # 0.0 - 1.0
    impact = Column(Float, nullable=True, default=0.0)  # Montant en euros ou score
    score = Column(Float, nullable=True, default=0.0)  # Score calculé
    
    # Mesures
    mitigation = Column(Text, nullable=True)
    plan_action = Column(JSON, nullable=True)  # Liste d'actions
    responsable = Column(String(100), nullable=True)
    
    # Dates
    date_identification = Column(Date, default=date.today, nullable=False, index=True)
    date_echeance = Column(Date, nullable=True, index=True)
    date_fermeture = Column(Date, nullable=True, index=True)
    
    # Suivi
    est_actif = Column(Boolean, default=True, index=True)
    est_accepté = Column(Boolean, default=False, index=True)
    
    # Liens
    ventes_liees = Column(JSON, nullable=True)  # Liste de IDs de ventes liées
    documents = Column(JSON, nullable=True)  # Liste de paths de documents
    
    commentaire = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Risque(code={self.code}, titre={self.titre}, niveau={self.niveau})>"
    
    @property
    def score_calcule(self) -> float:
        """Calcule le score de risque."""
        if not self.probabilite or not self.impact:
            return 0.0
        # Normaliser l'impact (supposons un max de 1M€)
        impact_normalise = min(self.impact / 1000000, 1.0)
        return self.probabilite * impact_normalise
    
    @property
    def est_urgent(self) -> bool:
        """Vérifie si le risque est urgent."""
        if self.niveau == RisqueNiveau.CRITIQUE.value:
            return True
        if self.date_echeance and (self.date_echeance - date.today()).days <= 7:
            return True
        return False
    
    @property
    def est_ferme(self) -> bool:
        """Vérifie si le risque est fermé."""
        return self.statut == RisqueStatut.FERME.value
    
    @property
    def jours_restants(self) -> Optional[int]:
        """Calcule les jours restants avant l'échéance."""
        if not self.date_echeance:
            return None
        return (self.date_echeance - date.today()).days
    
    def to_dict(self) -> dict:
        """Convertit l'objet en dictionnaire pour l'API."""
        return {
            "id": self.id,
            "mission_id": self.mission_id,
            "lot_id": self.lot_id,
            "code": self.code,
            "titre": self.titre,
            "description": self.description,
            "type": self.type,
            "niveau": self.niveau,
            "statut": self.statut,
            "probabilite": self.probabilite,
            "impact": self.impact,
            "score": self.score,
            "score_calcule": round(self.score_calcule, 4),
            "mitigation": self.mitigation,
            "plan_action": self.plan_action,
            "responsable": self.responsable,
            "date_identification": self.date_identification.isoformat() if self.date_identification else None,
            "date_echeance": self.date_echeance.isoformat() if self.date_echeance else None,
            "date_fermeture": self.date_fermeture.isoformat() if self.date_fermeture else None,
            "jours_restants": self.jours_restants,
            "est_actif": self.est_actif,
            "est_urgent": self.est_urgent,
            "est_ferme": self.est_ferme,
            "est_accepté": self.est_accepté,
            "ventes_liees": self.ventes_liees,
            "documents": self.documents,
            "commentaire": self.commentaire,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class RisqueCategorie(Base):
    """
    Modèle des catégories de risques.
    
    Permet de regrouper les risques par catégorie pour une meilleure
    organisation et analyse.
    """
    
    __tablename__ = "risques_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Identification
    code = Column(String(50), nullable=False, unique=True, index=True)
    nom = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Hiérarchie
    parent_id = Column(Integer, ForeignKey("risques_categories.id"), nullable=True, index=True)
    
    # Poids
    poids = Column(Float, nullable=True, default=1.0)
    
    # Statut
    est_actif = Column(Boolean, default=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<RisqueCategorie(code={self.code}, nom={self.nom})>"
    
    def to_dict(self) -> dict:
        """Convertit l'objet en dictionnaire."""
        return {
            "id": self.id,
            "code": self.code,
            "nom": self.nom,
            "description": self.description,
            "parent_id": self.parent_id,
            "poids": self.poids,
            "est_actif": self.est_actif,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class RisqueAnalyse(Base):
    """
    Modèle des analyses de risques.
    
    Stocke les résultats des analyses de risques effectuées sur
    une mission ou un portefeuille de projets.
    """
    
    __tablename__ = "risques_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Références
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=True, index=True)
    
    # Identification
    code = Column(String(50), nullable=False, unique=True)
    nom = Column(String(200), nullable=False)
    
    # Résultats
    nb_risques_totaux = Column(Integer, nullable=True, default=0)
    nb_risques_critiques = Column(Integer, nullable=True, default=0)
    nb_risques_eleves = Column(Integer, nullable=True, default=0)
    nb_risques_moyens = Column(Integer, nullable=True, default=0)
    nb_risques_faibles = Column(Integer, nullable=True, default=0)
    
    # Scores
    score_global = Column(Float, nullable=True, default=0.0)
    niveau_global = Column(String(20), nullable=True)
    
    # Recommandations
    recommandations = Column(JSON, nullable=True)  # Liste de recommandations
    
    # Dates
    date_analyse = Column(Date, default=date.today, nullable=False)
    
    # Métadonnées
    metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<RisqueAnalyse(code={self.code}, score={self.score_global})>"
    
    def to_dict(self) -> dict:
        """Convertit l'objet en dictionnaire."""
        return {
            "id": self.id,
            "mission_id": self.mission_id,
            "code": self.code,
            "nom": self.nom,
            "nb_risques_totaux": self.nb_risques_totaux,
            "nb_risques_critiques": self.nb_risques_critiques,
            "nb_risques_eleves": self.nb_risques_eleves,
            "nb_risques_moyens": self.nb_risques_moyens,
            "nb_risques_faibles": self.nb_risques_faibles,
            "score_global": self.score_global,
            "niveau_global": self.niveau_global,
            "recommandations": self.recommandations,
            "date_analyse": self.date_analyse.isoformat() if self.date_analyse else None,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# Relations (optionnel - à activer si nécessaire)
# Risque.mission = relationship("Mission", back_populates="risques")
# Risque.lot = relationship("Lot", back_populates="risques")
# RisqueAnalyse.mission = relationship("Mission", back_populates="analyses_risques")

