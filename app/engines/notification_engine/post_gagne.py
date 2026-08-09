"""
SMART_AO V7 - post_gagne.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Notifications Post-Gagné - Gestion des notifications après attribution d'un marché
Source: ARCHITECTURE_V7_ENGINE.md §3.4
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, date, timedelta
from dataclasses import dataclass, field
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class TypeNotificationPostGagne(Enum):
    """Types de notifications post-gagné."""
    ATTRIBUTION = "attribution"
    REUNION_LANCEMENT = "reunion_lancement"
    DEPOT_GARANTIE = "depot_garantie"
    SIGNATURE_CONTRAT = "signature_contrat"
    DEBUT_TRAVAUX = "debut_travaux"
    JALON = "jalon"
    RECEPTION = "reception"
    PAIEMENT = "paiement"
    LITIGE = "litige"
    CLOTURE = "cloture"


class StatutNotification(Enum):
    """Statuts des notifications."""
    EN_ATTENTE = "en_attente"
    ENVOYEE = "envoyee"
    LUE = "lue"
    ARCHIVEE = "archivee"


@dataclass
class NotificationPostGagne:
    """Représente une notification post-gagné."""
    notification_id: str
    mission_id: str
    type_notif: str
    titre: str
    message: str
    date_creation: datetime
    date_echeance: Optional[datetime] = None
    statut: str = StatutNotification.EN_ATTENTE.value
    destinataires: List[str] = field(default_factory=list)
    pieces_jointes: List[str] = field(default_factory=list)
    actions_requises: List[str] = field(default_factory=list)
    niveau_priorite: str = "normal"
    
    def est_urgente(self) -> bool:
        """Vérifie si la notification est urgente."""
        if self.date_echeance:
            return (self.date_echeance - datetime.utcnow()).days <= 3
        return self.niveau_priorite == "urgent"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire."""
        return {
            "notification_id": self.notification_id,
            "mission_id": self.mission_id,
            "type_notif": self.type_notif,
            "titre": self.titre,
            "message": self.message,
            "date_creation": self.date_creation.isoformat(),
            "date_echeance": self.date_echeance.isoformat() if self.date_echeance else None,
            "statut": self.statut,
            "destinataires": self.destinataires,
            "pieces_jointes": self.pieces_jointes,
            "actions_requises": self.actions_requises,
            "niveau_priorite": self.niveau_priorite,
            "est_urgente": self.est_urgente()
        }


@dataclass
class Jalon:
    """Représente un jalon du projet."""
    jalon_id: str
    mission_id: str
    nom: str
    description: str
    date_prevue: date
    date_reelle: Optional[date] = None
    statut: str = "a_venir"
    notifications: List[NotificationPostGagne] = field(default_factory=list)
    
    def est_atteint(self) -> bool:
        """Vérifie si le jalon est atteint."""
        return self.statut == "atteint" and self.date_reelle is not None
    
    def retard(self) -> Optional[int]:
        """Calcule le retard en jours."""
        if self.date_reelle:
            return (self.date_reelle - self.date_prevue).days
        if date.today() > self.date_prevue:
            return (date.today() - self.date_prevue).days
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire."""
        return {
            "jalon_id": self.jalon_id,
            "mission_id": self.mission_id,
            "nom": self.nom,
            "description": self.description,
            "date_prevue": self.date_prevue.isoformat(),
            "date_reelle": self.date_reelle.isoformat() if self.date_reelle else None,
            "statut": self.statut,
            "est_atteint": self.est_atteint(),
            "retard": self.retard()
        }


@dataclass
class RapportPostGagne:
    """Rapport complet du suivi post-gagné."""
    rapport_id: str
    mission_id: str
    date_rapport: datetime
    notifications: List[NotificationPostGagne] = field(default_factory=list)
    jalons: List[Jalon] = field(default_factory=list)
    nb_notifications_urgentes: int = 0
    nb_jalons_atteints: int = 0
    nb_jalons_retard: int = 0
    taux_avancement: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire."""
        return {
            "rapport_id": self.rapport_id,
            "mission_id": self.mission_id,
            "date_rapport": self.date_rapport.isoformat(),
            "nb_notifications_urgentes": self.nb_notifications_urgentes,
            "nb_jalons_atteints": self.nb_jalons_atteints,
            "nb_jalons_retard": self.nb_jalons_retard,
            "taux_avancement": self.taux_avancement,
            "notifications": [n.to_dict() for n in self.notifications],
            "jalons": [j.to_dict() for j in self.jalons]
        }


class PostGagneTracker:
    """
    Gestionnaire du suivi post-gagné.
    
    Gère les notifications, jalons et alertes après l'attribution d'un marché.
    """
    
    JALONS_STANDARDS = [
        {
            "code": "JALON_REUNION_LANCEMENT",
            "nom": "Réunion de lancement",
            "description": "Réunion de lancement du projet avec le maître d'ouvrage",
            "delai_jours": 7
        },
        {
            "code": "JALON_DEPOT_GARANTIE",
            "nom": "Dépôt de la garantie de bon achèvement",
            "description": "Dépôt de la garantie financière",
            "delai_jours": 14
        },
        {
            "code": "JALON_SIGNATURE_CONTRAT",
            "nom": "Signature du contrat",
            "description": "Signature du contrat avec toutes les parties",
            "delai_jours": 21
        },
        {
            "code": "JALON_DEBUT_TRAVAUX",
            "nom": "Début des travaux",
            "description": "Début effectif des travaux sur site",
            "delai_jours": 30
        },
        {
            "code": "JALON_PREMIER_JALON",
            "nom": "Premier jalon technique",
            "description": "Premier jalon technique du projet",
            "delai_jours": 60
        },
        {
            "code": "JALON_MOYEN",
            "nom": "Jalon à mi-parcours",
            "description": "Point d'avancement à 50%",
            "delai_jours": 180
        },
        {
            "code": "JALON_FINAL",
            "nom": "Jalon final",
            "description": "Fin des travaux prévisionnelle",
            "delai_jours": 365
        }
    ]
    
    def __init__(self):
        self.notifications: Dict[str, NotificationPostGagne] = {}
        self.jalons: Dict[str, Jalon] = {}
        self.callbacks: List[callable] = []
    
    def creer_notification(
        self,
        mission_id: str,
        type_notif: str,
        titre: str,
        message: str,
        destinataires: List[str],
        date_echeance: Optional[datetime] = None,
        actions_requises: Optional[List[str]] = None,
        niveau_priorite: str = "normal"
    ) -> NotificationPostGagne:
        """Crée une nouvelle notification post-gagné."""
        notification_id = f"NOTIF_PG_{mission_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        notification = NotificationPostGagne(
            notification_id=notification_id,
            mission_id=mission_id,
            type_notif=type_notif,
            titre=titre,
            message=message,
            date_creation=datetime.utcnow(),
            date_echeance=date_echeance,
            destinataires=destinataires,
            actions_requises=actions_requises or [],
            niveau_priorite=niveau_priorite
        )
        
        self.notifications[notification_id] = notification
        logger.info(f"Notification post-gagne creee: {titre} (mission {mission_id})")
        
        # Envoyer la notification
        self.notifier(notification)
        
        return notification
    
    def creer_notification_attribution(
        self,
        mission_id: str,
        nom_mission: str,
        montant: float,
        client: str,
        destinataires: List[str]
    ) -> NotificationPostGagne:
        """Crée une notification d'attribution."""
        return self.creer_notification(
            mission_id=mission_id,
            type_notif=TypeNotificationPostGagne.ATTRIBUTION.value,
            titre=f"Attribution du marché: {nom_mission}",
            message=f"Le marché '{nom_mission}' d'un montant de {montant:,.2f} € a été attribué par {client}.",
            destinataires=destinataires,
            niveau_priorite="haut"
        )
    
    def creer_notification_jalon(
        self,
        mission_id: str,
        jalon_nom: str,
        date_prevue: date,
        destinataires: List[str]
    ) -> NotificationPostGagne:
        """Crée une notification de jalon."""
        return self.creer_notification(
            mission_id=mission_id,
            type_notif=TypeNotificationPostGagne.JALON.value,
            titre=f"Jalon à venir: {jalon_nom}",
            message=f"Le jalon '{jalon_nom}' est prévu pour le {date_prevue.isoformat()}.",
            destinataires=destinataires,
            date_echeance=datetime.combine(date_prevue, datetime.min.time()),
            actions_requises=["Confirmer la date", "Préparer les documents nécessaires"]
        )
    
    def noter_jalon_atteint(self, jalon_id: str, date_reelle: date) -> bool:
        """Note un jalon comme atteint."""
        jalon = self.jalons.get(jalon_id)
        if jalon:
            jalon.date_reelle = date_reelle
            jalon.statut = "atteint"
            logger.info(f"Jalon atteint: {jalon.nom} (mission {jalon.mission_id})")
            return True
        return False
    
    def initialiser_jalons_mission(
        self,
        mission_id: str,
        date_attribution: date
    ) -> List[Jalon]:
        """Initialise les jalons standards pour une mission."""
        jalons_crees = []
        
        for jalon_data in self.JALONS_STANDARDS:
            date_prevue = date_attribution + timedelta(days=jalon_data["delai_jours"])
            
            jalon = Jalon(
                jalon_id=f"JALON_{mission_id}_{jalon_data['code']}",
                mission_id=mission_id,
                nom=jalon_data["nom"],
                description=jalon_data["description"],
                date_prevue=date_prevue
            )
            
            self.jalons[jalon.jalon_id] = jalon
            jalons_crees.append(jalon)
            
            # Créer une notification pour le jalon
            self.creer_notification_jalon(
                mission_id=mission_id,
                jalon_nom=jalon.nom,
                date_prevue=date_prevue,
                destinataires=[]  # À compléter avec les destinataires réels
            )
        
        logger.info(f"Jalons initialises pour mission {mission_id}: {len(jalons_crees)} jalons")
        return jalons_crees
    
    def notifier(self, notification: NotificationPostGagne) -> None:
        """Envoie une notification."""
        logger.info(f"Notification envoyee: {notification.titre} - {notification.type_notif}")
        
        # Appeler les callbacks
        for callback in self.callbacks:
            try:
                callback(notification)
            except Exception as e:
                logger.error(f"Erreur dans le callback: {e}")
    
    def register_callback(self, callback: callable) -> None:
        """Enregistre un callback pour les notifications."""
        self.callbacks.append(callback)
        logger.info("Callback de notification post-gagne enregistre")
    
    def get_notifications_mission(self, mission_id: str) -> List[NotificationPostGagne]:
        """Récupère toutes les notifications pour une mission."""
        return [n for n in self.notifications.values() if n.mission_id == mission_id]
    
    def get_notifications_urgentes(self) -> List[NotificationPostGagne]:
        """Récupère les notifications urgentes."""
        return [n for n in self.notifications.values() if n.est_urgente()]
    
    def get_jalons_mission(self, mission_id: str) -> List[Jalon]:
        """Récupère tous les jalons pour une mission."""
        return [j for j in self.jalons.values() if j.mission_id == mission_id]
    
    def get_jalons_retard(self, mission_id: Optional[str] = None) -> List[Jalon]:
        """Récupère les jalons en retard."""
        if mission_id:
            jalons = self.get_jalons_mission(mission_id)
        else:
            jalons = list(self.jalons.values())
        
        return [j for j in jalons if j.retard() and j.retard() > 0]
    
    def generer_rapport(
        self,
        mission_id: str,
        date_rapport: Optional[datetime] = None
    ) -> RapportPostGagne:
        """Génère un rapport complet post-gagné."""
        date_rapport = date_rapport or datetime.utcnow()
        
        notifications = self.get_notifications_mission(mission_id)
        jalons = self.get_jalons_mission(mission_id)
        
        nb_urgentes = sum(1 for n in notifications if n.est_urgente())
        nb_atteints = sum(1 for j in jalons if j.est_atteint())
        nb_retard = len(self.get_jalons_retard(mission_id))
        
        # Calcul du taux d'avancement
        total_jalons = len(jalons)
        taux_avancement = (nb_atteints / total_jalons * 100) if total_jalons > 0 else 0.0
        
        rapport_id = f"RAPPORT_PG_{mission_id}_{date_rapport.strftime('%Y%m%d%H%M%S')}"
        
        return RapportPostGagne(
            rapport_id=rapport_id,
            mission_id=mission_id,
            date_rapport=date_rapport,
            notifications=notifications,
            jalons=jalons,
            nb_notifications_urgentes=nb_urgentes,
            nb_jalons_atteints=nb_atteints,
            nb_jalons_retard=nb_retard,
            taux_avancement=round(taux_avancement, 2)
        )
    
    def marquer_notification_lue(self, notification_id: str) -> bool:
        """Marque une notification comme lue."""
        notification = self.notifications.get(notification_id)
        if notification:
            notification.statut = StatutNotification.LUE.value
            logger.info(f"Notification marquee comme lue: {notification_id}")
            return True
        return False
    
    def archiver_notification(self, notification_id: str) -> bool:
        """Archive une notification."""
        notification = self.notifications.get(notification_id)
        if notification:
            notification.statut = StatutNotification.ARCHIVEE.value
            logger.info(f"Notification archivee: {notification_id}")
            return True
        return False


tracker = PostGagneTracker()


def creer_notification(
    mission_id: str,
    type_notif: str,
    titre: str,
    message: str,
    destinataires: List[str],
    date_echeance: Optional[str] = None,
    actions_requises: Optional[List[str]] = None,
    niveau_priorite: str = "normal"
) -> Dict[str, Any]:
    """Cree une notification post-gagne."""
    date_echeance_dt = datetime.fromisoformat(date_echeance) if date_echeance else None
    notification = tracker.creer_notification(
        mission_id=mission_id,
        type_notif=type_notif,
        titre=titre,
        message=message,
        destinataires=destinataires,
        date_echeance=date_echeance_dt,
        actions_requises=actions_requises,
        niveau_priorite=niveau_priorite
    )
    return notification.to_dict()


def initialiser_jalons(mission_id: str, date_attribution: str) -> List[Dict[str, Any]]:
    """Initialise les jalons pour une mission."""
    date_attribution_dt = datetime.fromisoformat(date_attribution).date()
    jalons = tracker.initialiser_jalons_mission(mission_id, date_attribution_dt)
    return [j.to_dict() for j in jalons]


def noter_jalon_atteint_api(jalon_id: str, date_reelle: str) -> bool:
    """Note un jalon comme atteint."""
    date_reelle_dt = datetime.fromisoformat(date_reelle).date()
    return tracker.noter_jalon_atteint(jalon_id, date_reelle_dt)


def get_rapport_post_gagne(mission_id: str) -> Dict[str, Any]:
    """Genere un rapport post-gagne."""
    rapport = tracker.generer_rapport(mission_id)
    return rapport.to_dict()


def get_notifications_mission(mission_id: str, urgentes_only: bool = False) -> List[Dict[str, Any]]:
    """Recupere les notifications d'une mission."""
    if urgentes_only:
        notifications = tracker.get_notifications_urgentes()
    else:
        notifications = tracker.get_notifications_mission(mission_id)
    return [n.to_dict() for n in notifications]


def get_jalons_mission(mission_id: str, retard_only: bool = False) -> List[Dict[str, Any]]:
    """Recupere les jalons d'une mission."""
    if retard_only:
        jalons = tracker.get_jalons_retard(mission_id)
    else:
        jalons = tracker.get_jalons_mission(mission_id)
    return [j.to_dict() for j in jalons]


