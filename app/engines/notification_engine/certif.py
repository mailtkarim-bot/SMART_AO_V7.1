"""
SMART_AO V7 - certif.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Notifications Certifications - Gestion des alertes et notifications pour les certifications
Source: ARCHITECTURE_V7_ENGINE.md §3.4
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, date, timedelta
from dataclasses import dataclass, field
import logging
from enum import Enum

from app.engines.math_engine.decimal_ops import DecimalOps

logger = logging.getLogger(__name__)


class TypeCertification(Enum):
    """Types de certifications BTP."""
    CE = "CE"
    NF = "NF"
    ATEX = "ATEX"
    ISO_9001 = "ISO_9001"
    ISO_14001 = "ISO_14001"
    ISO_45001 = "ISO_45001"
    QUALIBAT = "QUALIBAT"
    QUALIFELEC = "QUALIFELEC"
    QUALIBOIS = "QUALIBOIS"
    RGE = "RGE"
    OPQIBI = "OPQIBI"
    CSTB = "CSTB"
    ACERMI = "ACERMI"


class StatutCertification(Enum):
    """Statuts des certifications."""
    VALIDE = "valide"
    EN_COURS = "en_cours"
    EXPIREE = "expirée"
    SUSPENDUE = "suspendue"
    REVOQUEE = "révoquée"


@dataclass
class Certification:
    """Représente une certification."""
    certification_id: str
    type_certif: str
    nom: str
    organisme: str
    date_obtention: date
    date_expiration: date
    statut: str
    reference: Optional[str] = None
    entreprise_id: Optional[str] = None
    mission_id: Optional[str] = None
    jours_avant_alert: int = 90
    
    def est_valide(self, date_ref: Optional[date] = None) -> bool:
        """Vérifie si la certification est valide à la date de référence."""
        date_ref = date_ref or date.today()
        return self.statut == StatutCertification.VALIDE.value and self.date_expiration >= date_ref
    
    def jours_restants(self, date_ref: Optional[date] = None) -> int:
        """Calcule le nombre de jours restants avant expiration."""
        date_ref = date_ref or date.today()
        return (self.date_expiration - date_ref).days
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire."""
        return {
            "certification_id": self.certification_id,
            "type_certif": self.type_certif,
            "nom": self.nom,
            "organisme": self.organisme,
            "date_obtention": self.date_obtention.isoformat(),
            "date_expiration": self.date_expiration.isoformat(),
            "statut": self.statut,
            "reference": self.reference,
            "entreprise_id": self.entreprise_id,
            "mission_id": self.mission_id,
            "jours_avant_alert": self.jours_avant_alert,
            "est_valide": self.est_valide(),
            "jours_restants": self.jours_restants()
        }


@dataclass
class AlerteCertification:
    """Représente une alerte de certification."""
    alerte_id: str
    certification_id: str
    type_alerte: str
    date_declenchement: datetime
    message: str
    niveau: str
    actions_requises: List[str] = field(default_factory=list)
    statu: str = "active"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire."""
        return {
            "alerte_id": self.alerte_id,
            "certification_id": self.certification_id,
            "type_alerte": self.type_alerte,
            "date_declenchement": self.date_declenchement.isoformat(),
            "message": self.message,
            "niveau": self.niveau,
            "actions_requises": self.actions_requises,
            "statu": self.statu
        }


@dataclass
class RapportCertifications:
    """Rapport complet des certifications et alertes."""
    rapport_id: str
    mission_id: Optional[str]
    date_rapport: datetime
    certifications: List[Certification] = field(default_factory=list)
    alertes: List[AlerteCertification] = field(default_factory=list)
    nb_certifs_valides: int = 0
    nb_certifs_expirees: int = 0
    nb_alertes_critiques: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire."""
        return {
            "rapport_id": self.rapport_id,
            "mission_id": self.mission_id,
            "date_rapport": self.date_rapport.isoformat(),
            "nb_certifs_valides": self.nb_certifs_valides,
            "nb_certifs_expirees": self.nb_certifs_expirees,
            "nb_alertes_critiques": self.nb_alertes_critiques,
            "certifications": [c.to_dict() for c in self.certifications],
            "alertes": [a.to_dict() for a in self.alertes]
        }


class CertifNotificator:
    """
    Gestionnaire des notifications de certifications.
    
    Vérifie les dates d'expiration, génère des alertes et envoie
    des notifications pour le renouvellement des certifications.
    """
    
    NIVEAUX_ALERTE = {
        "critique": {"seuil": 30, "message": "Certification expirant dans moins de 30 jours"},
        "eleve": {"seuil": 60, "message": "Certification expirant dans moins de 60 jours"},
        "moyen": {"seuil": 90, "message": "Certification expirant dans moins de 90 jours"},
        "faible": {"seuil": 180, "message": "Certification expirant dans moins de 180 jours"}
    }
    
    ORGANISMES = {
        TypeCertification.CE.value: ["AFNOR", "Bureau Veritas", "SGS"],
        TypeCertification.NF.value: ["AFNOR"],
        TypeCertification.ATEX.value: ["INERIS", "LNE"],
        TypeCertification.ISO_9001.value: ["AFNOR", "Bureau Veritas", "DNV"],
        TypeCertification.ISO_14001.value: ["AFNOR", "Bureau Veritas", "DNV"],
        TypeCertification.ISO_45001.value: ["AFNOR", "Bureau Veritas", "DNV"],
        TypeCertification.QUALIBAT.value: ["QUALIBAT"],
        TypeCertification.QUALIFELEC.value: ["QUALIFELEC"],
        TypeCertification.QUALIBOIS.value: ["QUALIBOIS"],
        TypeCertification.RGE.value: ["QUALIBAT", "CSTB"],
        TypeCertification.OPQIBI.value: ["OPQIBI"],
        TypeCertification.CSTB.value: ["CSTB"],
        TypeCertification.ACERMI.value: ["CSTB"]
    }
    
    DUREE_VALIDITE = {
        TypeCertification.CE.value: 365 * 5,
        TypeCertification.NF.value: 365 * 3,
        TypeCertification.ATEX.value: 365 * 3,
        TypeCertification.ISO_9001.value: 365 * 3,
        TypeCertification.ISO_14001.value: 365 * 3,
        TypeCertification.ISO_45001.value: 365 * 3,
        TypeCertification.QUALIBAT.value: 365 * 4,
        TypeCertification.QUALIFELEC.value: 365 * 3,
        TypeCertification.QUALIBOIS.value: 365 * 4,
        TypeCertification.RGE.value: 365 * 4,
        TypeCertification.OPQIBI.value: 365 * 5,
        TypeCertification.CSTB.value: 365 * 5,
        TypeCertification.ACERMI.value: 365 * 5
    }
    
    def __init__(self):
        self.certifications: Dict[str, Certification] = {}
        self.alertes: Dict[str, AlerteCertification] = {}
        self.callbacks: List[callable] = []
    
    def ajouter_certification(self, certif: Certification) -> str:
        """Ajoute ou met à jour une certification."""
        certif_id = certif.certification_id
        self.certifications[certif_id] = certif
        logger.info(f"Certification ajoutee: {certif.nom} ({certif.type_certif})")
        
        # Vérifier les alertes
        self.verifier_alertes_certif(certif)
        
        return certif_id
    
    def supprimer_certification(self, certification_id: str) -> bool:
        """Supprime une certification."""
        if certification_id in self.certifications:
            del self.certifications[certification_id]
            logger.info(f"Certification supprimee: {certification_id}")
            return True
        return False
    
    def get_certification(self, certification_id: str) -> Optional[Certification]:
        """Récupère une certification par son ID."""
        return self.certifications.get(certification_id)
    
    def verifier_alertes_certif(self, certif: Certification) -> List[AlerteCertification]:
        """Vérifie et génère les alertes pour une certification."""
        alertes = []
        date_aujourdhui = date.today()
        
        if not certif.est_valide(date_aujourdhui):
            if certif.statut != StatutCertification.EXPIREE.value:
                alerte = self.creer_alerte(
                    certif.certification_id,
                    "expiration",
                    "CRITIQUE",
                    f"Certification {certif.nom} est EXPIREE depuis {(date_aujourdhui - certif.date_expiration).days} jours",
                    ["Renouveler immédiatement", "Vérifier les délais de traitement"]
                )
                alertes.append(alerte)
        else:
            jours_restants = certif.jours_restants(date_aujourdhui)
            
            for niveau, config in self.NIVEAUX_ALERTE.items():
                if jours_restants <= config["seuil"]:
                    alerte = self.creer_alerte(
                        certif.certification_id,
                        "expiration_proche",
                        niveau.upper(),
                        f"{config['message']}: {certif.nom} (expire le {certif.date_expiration.isoformat()})",
                        [
                            "Lancer la procédure de renouvellement",
                            "Vérifier les documents nécessaires",
                            f"Contacter l'organisme: {certif.organisme}"
                        ]
                    )
                    alertes.append(alerte)
                    break  # Une seule alerte par certification
        
        # Enregistrer les alertes
        for alerte in alertes:
            self.alertes[alerte.alerte_id] = alerte
            self.notifier(alerte)
        
        return alertes
    
    def creer_alerte(
        self,
        certification_id: str,
        type_alerte: str,
        niveau: str,
        message: str,
        actions: List[str]
    ) -> AlerteCertification:
        """Crée une nouvelle alerte."""
        alerte_id = f"ALERTE_CERTIF_{certification_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        return AlerteCertification(
            alerte_id=alerte_id,
            certification_id=certification_id,
            type_alerte=type_alerte,
            date_declenchement=datetime.utcnow(),
            message=message,
            niveau=niveau,
            actions_requises=actions
        )
    
    def verifier_toutes_certifications(self) -> List[AlerteCertification]:
        """Vérifie toutes les certifications et génère les alertes."""
        toutes_alertes = []
        for certif in self.certifications.values():
            alertes = self.verifier_alertes_certif(certif)
            toutes_alertes.extend(alertes)
        return toutes_alertes
    
    def notifier(self, alerte: AlerteCertification) -> None:
        """Envoie une notification pour une alerte."""
        logger.info(f"Notification envoyee: {alerte.type_alerte} - {alerte.message}")
        
        # Appeler les callbacks enregistrés
        for callback in self.callbacks:
            try:
                callback(alerte)
            except Exception as e:
                logger.error(f"Erreur dans le callback de notification: {e}")
    
    def register_callback(self, callback: callable) -> None:
        """Enregistre un callback pour les notifications."""
        self.callbacks.append(callback)
        logger.info("Callback de notification enregistré")
    
    def generer_rapport(
        self,
        mission_id: Optional[str] = None,
        date_rapport: Optional[datetime] = None
    ) -> RapportCertifications:
        """Génère un rapport complet des certifications."""
        date_rapport = date_rapport or datetime.utcnow()
        
        if mission_id:
            certifs = [c for c in self.certifications.values() if c.mission_id == mission_id]
        else:
            certifs = list(self.certifications.values())
        
        alertes = [a for a in self.alertes.values() if a.certification_id in [c.certification_id for c in certifs]]
        
        nb_valides = sum(1 for c in certifs if c.est_valide(date_rapport.date()))
        nb_expirees = len(certifs) - nb_valides
        nb_alertes_critiques = sum(1 for a in alertes if a.niveau == "CRITIQUE")
        
        rapport_id = f"RAPPORT_CERTIF_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        if mission_id:
            rapport_id += f"_{mission_id}"
        
        return RapportCertifications(
            rapport_id=rapport_id,
            mission_id=mission_id,
            date_rapport=date_rapport,
            certifications=certifs,
            alertes=alertes,
            nb_certifs_valides=nb_valides,
            nb_certifs_expirees=nb_expirees,
            nb_alertes_critiques=nb_alertes_critiques
        )
    
    def get_alertes_par_niveau(self, niveau: str) -> List[AlerteCertification]:
        """Récupère les alertes par niveau de criticité."""
        return [a for a in self.alertes.values() if a.niveau == niveau.upper()]
    
    def get_certifications_expirant_dans(self, jours: int) -> List[Certification]:
        """Récupère les certifications expirant dans un délai donné."""
        date_ref = date.today() + timedelta(days=jours)
        return [
            c for c in self.certifications.values()
            if c.date_expiration <= date_ref and c.est_valide()
        ]
    
    def get_certifications_by_type(self, type_certif: str) -> List[Certification]:
        """Récupère les certifications par type."""
        return [c for c in self.certifications.values() if c.type_certif == type_certif]
    
    def get_certifications_by_entreprise(self, entreprise_id: str) -> List[Certification]:
        """Récupère les certifications par entreprise."""
        return [c for c in self.certifications.values() if c.entreprise_id == entreprise_id]
    
    def get_certifications_by_mission(self, mission_id: str) -> List[Certification]:
        """Récupère les certifications par mission."""
        return [c for c in self.certifications.values() if c.mission_id == mission_id]


notificator = CertifNotificator()


def ajouter_certification(
    certification_id: str,
    type_certif: str,
    nom: str,
    organisme: str,
    date_obtention: str,
    date_expiration: str,
    statut: str,
    reference: Optional[str] = None,
    entreprise_id: Optional[str] = None,
    mission_id: Optional[str] = None,
    jours_avant_alert: int = 90
) -> Dict[str, Any]:
    """Ajoute une certification."""
    certif = Certification(
        certification_id=certification_id,
        type_certif=type_certif,
        nom=nom,
        organisme=organisme,
        date_obtention=datetime.fromisoformat(date_obtention).date(),
        date_expiration=datetime.fromisoformat(date_expiration).date(),
        statut=statut,
        reference=reference,
        entreprise_id=entreprise_id,
        mission_id=mission_id,
        jours_avant_alert=jours_avant_alert
    )
    notificator.ajouter_certification(certif)
    return certif.to_dict()


def verifier_certifications(mission_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Verifie toutes les certifications et retourne les alertes."""
    alertes = notificator.verifier_toutes_certifications()
    return [a.to_dict() for a in alertes]


def get_rapport_certifications(mission_id: Optional[str] = None) -> Dict[str, Any]:
    """Genere un rapport des certifications."""
    rapport = notificator.generer_rapport(mission_id)
    return rapport.to_dict()


def get_certification(certification_id: str) -> Optional[Dict[str, Any]]:
    """Recupere une certification."""
    certif = notificator.get_certification(certification_id)
    return certif.to_dict() if certif else None


def get_alertes_certifications(niveau: Optional[str] = None) -> List[Dict[str, Any]]:
    """Recupere les alertes de certifications."""
    if niveau:
        alertes = notificator.get_alertes_par_niveau(niveau)
    else:
        alertes = list(notificator.alertes.values())
    return [a.to_dict() for a in alertes]


def get_certifications_expirant_dans(jours: int) -> List[Dict[str, Any]]:
    """Recupere les certifications expirant dans un delai."""
    certifs = notificator.get_certifications_expirant_dans(jours)
    return [c.to_dict() for c in certifs]


