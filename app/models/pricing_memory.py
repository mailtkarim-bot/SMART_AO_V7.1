"""
SMART_AO V7 - pricing_memory.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Pricing Memory Model - Mémoire des prix et historiques de chiffrage
Source: ARCHITECTURE_V7_ENGINE.md §3.2
"""

from datetime import date, datetime
from typing import Optional
from enum import Enum

from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship, declarative_base

from app.core.database import Base


class PricingCategory(str, Enum):
    """Catégories de prix."""
    MATERIAUX = "materiaux"
    MAIN_D_OEUVRE = "main_d_oeuvre"
    MATERIEL = "materiel"
    SOUS_TRAITANCE = "sous_traitance"
    PRESTATION = "prestation"
    FRAIS_GENERAUX = "frais_generaux"
    MARGE = "marge"
    AUTRE = "autre"


class PricingType(str, Enum):
    """Types de pricing."""
    UNITAIRE = "unitaire"
    FORFAITAIRE = "forfaitaire"
    HORAIRE = "horaire"
    JOURNALIER = "journalier"
    MENSUEL = "mensuel"
    GLOBAL = "global"


class PricingSource(str, Enum):
    """Sources des données de pricing."""
    DEVIS = "devis"
    FACTURE = "facture"
    COMMANDE = "commande"
    MARCHE = "marche"
    FOURNISSEUR = "fournisseur"
    REFERENTIEL = "referentiel"
    ESTIMATION = "estimation"
    MANUEL = "manuel"


class PricingMemory(Base):
    """
    Modèle de mémoire des prix.
    
    Stocke les prix historiques et les données de référence pour le chiffrage
    des missions. Permet de capitaliser sur l'expérience passée et d'améliorer
    la précision des estimations futures.
    
    Attributes:
        id: Identifiant unique
        mission_id: Référence vers la mission (optionnel)
        lot_id: Référence vers le lot concerné
        
        # Identification
        code: Code unique de l'article ou prestation
        libelle: Libellé descriptif
        categorie: Catégorie de prix
        type: Type de pricing
        
        # Valeurs
        prix_unitaire: Prix unitaire (HT)
        quantite: Quantité associée
        prix_total: Prix total (HT)
        
        # Unité
        unite: Unité de mesure (m², m³, h, j, etc.)
        
        # Source
        source: Source de la donnée
        source_reference: Référence de la source (numéro de devis, facture, etc.)
        
        # Dates
        date_valeur: Date à laquelle le prix était valable
        date_expiration: Date d'expiration de validité
        
        # Contexte
        fournisseur: Fournisseur associé
        region: Région géographique
        conditions: Conditions particulières
        
        # Suivi
        est_valide: Indicateur de validité
        commentaire: Commentaires
        metadata: Métadonnées supplémentaires
    """
    
    __tablename__ = "pricing_memory"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Références
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=True, index=True)
    lot_id = Column(Integer, ForeignKey("lots.id"), nullable=True, index=True)
    entreprise_id = Column(Integer, nullable=True, default=1)
    
    # Identification
    code = Column(String(50), nullable=False, index=True)
    libelle = Column(String(200), nullable=False)
    categorie = Column(String(50), default=PricingCategory.MATERIAUX.value, index=True)
    type = Column(String(50), default=PricingType.UNITAIRE.value, index=True)
    
    # Valeurs (en euros)
    prix_unitaire = Column(Float, nullable=False, default=0.0)
    quantite = Column(Float, nullable=True, default=1.0)
    prix_total = Column(Float, nullable=True, default=0.0)
    
    # Unité
    unite = Column(String(20), nullable=True, default="u")
    
    # TVA
    tva_taux = Column(Float, nullable=True, default=20.0)  # Taux de TVA en %
    
    # Source
    source = Column(String(50), default=PricingSource.MANUEL.value, index=True)
    source_reference = Column(String(100), nullable=True)
    
    # Dates
    date_valeur = Column(Date, default=date.today, nullable=False, index=True)
    date_expiration = Column(Date, nullable=True, index=True)
    
    # Contexte
    fournisseur = Column(String(200), nullable=True)
    fournisseur_contact = Column(String(200), nullable=True)
    region = Column(String(100), nullable=True, index=True)
    conditions = Column(Text, nullable=True)
    
    # Indices
    indice_relation = Column(String(50), nullable=True)  # Ex: "BT01", "INSEE_Materiaux"
    indice_valeur = Column(Float, nullable=True)  # Valeur de l'indice au moment du prix
    
    # Suivi
    est_valide = Column(Boolean, default=True, index=True)
    est_referentiel = Column(Boolean, default=False, index=True)  # Prix de référence
    commentaire = Column(Text, nullable=True)
    
    # Métadonnées
    metadata = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)  # Liste de tags pour classification
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<PricingMemory(code={self.code}, libelle={self.libelle}, prix={self.prix_unitaire})>"
    
    @property
    def prix_unitaire_ttc(self) -> float:
        """Calcule le prix unitaire TTC."""
        if self.tva_taux:
            return self.prix_unitaire * (1 + self.tva_taux / 100)
        return self.prix_unitaire
    
    @property
    def prix_total_ht(self) -> float:
        """Calcule le prix total HT."""
        return self.prix_unitaire * (self.quantite or 1)
    
    @property
    def prix_total_ttc(self) -> float:
        """Calcule le prix total TTC."""
        return self.prix_total_ht * (1 + (self.tva_taux or 20) / 100)
    
    @property
    def est_actuel(self) -> bool:
        """Vérifie si le prix est actuel (non expiré)."""
        if not self.est_valide:
            return False
        if self.date_expiration and self.date_expiration < date.today():
            return False
        return True
    
    @property
    def age_jours(self) -> Optional[int]:
        """Calcule l'âge du prix en jours."""
        if not self.date_valeur:
            return None
        return (date.today() - self.date_valeur).days
    
    def to_dict(self) -> dict:
        """Convertit l'objet en dictionnaire pour l'API."""
        return {
            "id": self.id,
            "mission_id": self.mission_id,
            "lot_id": self.lot_id,
            "code": self.code,
            "libelle": self.libelle,
            "categorie": self.categorie,
            "type": self.type,
            "prix_unitaire": self.prix_unitaire,
            "prix_unitaire_ttc": round(self.prix_unitaire_ttc, 4),
            "quantite": self.quantite,
            "prix_total_ht": round(self.prix_total_ht, 4),
            "prix_total_ttc": round(self.prix_total_ttc, 4),
            "unite": self.unite,
            "tva_taux": self.tva_taux,
            "source": self.source,
            "source_reference": self.source_reference,
            "date_valeur": self.date_valeur.isoformat() if self.date_valeur else None,
            "date_expiration": self.date_expiration.isoformat() if self.date_expiration else None,
            "age_jours": self.age_jours,
            "fournisseur": self.fournisseur,
            "fournisseur_contact": self.fournisseur_contact,
            "region": self.region,
            "indice_relation": self.indice_relation,
            "indice_valeur": self.indice_valeur,
            "est_valide": self.est_valide,
            "est_actuel": self.est_actuel,
            "est_referentiel": self.est_referentiel,
            "conditions": self.conditions,
            "commentaire": self.commentaire,
            "tags": self.tags,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class PricingIndex(Base):
    """
    Modèle des indices économiques.
    
    Stocke les indices économiques (INSEE, BT, etc.) utilisés pour
    l'indexation des prix dans le temps.
    """
    
    __tablename__ = "pricing_indices"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Identification
    code = Column(String(20), nullable=False, unique=True, index=True)
    nom = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Type
    type = Column(String(50), nullable=True)  # "mensuel", "trimestriel", "annuel"
    frequence = Column(String(20), nullable=True)  # "M", "T", "A"
    
    # Valeurs
    base_value = Column(Float, nullable=True)  # Valeur de base (100 par défaut)
    base_date = Column(Date, nullable=True)  # Date de la valeur de base
    current_value = Column(Float, nullable=True)  # Valeur actuelle
    current_date = Column(Date, nullable=True)  # Date de la valeur actuelle
    
    # Source
    source = Column(String(100), nullable=True)
    source_url = Column(String(255), nullable=True)
    
    # Statut
    est_actif = Column(Boolean, default=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<PricingIndex(code={self.code}, current_value={self.current_value})>"
    
    @property
    def variation_pct(self) -> Optional[float]:
        """Calcule la variation en pourcentage depuis la base."""
        if not self.base_value or not self.current_value:
            return None
        return ((self.current_value - self.base_value) / self.base_value) * 100
    
    def to_dict(self) -> dict:
        """Convertit l'objet en dictionnaire."""
        return {
            "id": self.id,
            "code": self.code,
            "nom": self.nom,
            "description": self.description,
            "type": self.type,
            "frequence": self.frequence,
            "base_value": self.base_value,
            "base_date": self.base_date.isoformat() if self.base_date else None,
            "current_value": self.current_value,
            "current_date": self.current_date.isoformat() if self.current_date else None,
            "variation_pct": round(self.variation_pct, 4) if self.variation_pct else None,
            "source": self.source,
            "source_url": self.source_url,
            "est_actif": self.est_actif,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class PricingHistorique(Base):
    """
    Historique des évolutions de prix.
    
    Cette table permet de suivre l'évolution des prix dans le temps
    pour chaque article ou prestation.
    """
    
    __tablename__ = "pricing_historique"
    
    id = Column(Integer, primary_key=True, index=True)
    
    pricing_memory_id = Column(Integer, ForeignKey("pricing_memory.id"), nullable=False, index=True)
    
    # Valeurs historiques
    prix_unitaire = Column(Float, nullable=False)
    quantite = Column(Float, nullable=True)
    tva_taux = Column(Float, nullable=True)
    
    # Date
    date_effet = Column(Date, nullable=False, index=True)
    
    # Cause de la modification
    cause = Column(String(200), nullable=True)
    utilisateur_id = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<PricingHistorique(pricing_memory_id={self.pricing_memory_id}, date={self.date_effet})>"
    
    def to_dict(self) -> dict:
        """Convertit l'objet en dictionnaire."""
        return {
            "id": self.id,
            "pricing_memory_id": self.pricing_memory_id,
            "prix_unitaire": self.prix_unitaire,
            "quantite": self.quantite,
            "tva_taux": self.tva_taux,
            "date_effet": self.date_effet.isoformat() if self.date_effet else None,
            "cause": self.cause,
            "utilisateur_id": self.utilisateur_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

