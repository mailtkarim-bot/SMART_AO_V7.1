"""
SMART_AO V7 - resources.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Ressources Humaines et Matérielles - Gestion et optimisation des ressources
Source: ARCHITECTURE_V7_ENGINE.md §3.4
"""

from typing import Dict, List, Optional, Any
from decimal import Decimal, getcontext
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
import logging

from app.engines.math_engine.decimal_ops import DecimalOps

getcontext().prec = 28
logger = logging.getLogger(__name__)


@dataclass
class RessourceHumaine:
    """Représente une ressource humaine."""
    ressource_id: str
    nom: str
    prenom: str
    poste: str  # "ouvrier", "compagnon", "chef_equipe", "ingenieur", "conducteur"
    competence: str = "polyvalent"
    taux_horaire: Decimal = Decimal("0")
    disponibilite: List[date] = field(default_factory=list)
    affectation_actuelle: Optional[str] = None
    
    def cout_journalier(self, heures: int = 8) -> Decimal:
        """Calcule le coût journalier."""
        return self.taux_horaire * Decimal(str(heures))


@dataclass
class RessourceMateriel:
    """Représente une ressource matérielle."""
    ressource_id: str
    nom: str
    type: str  # "engin", "outil", "equipement", "vehicule"
    cout_location_jour: Decimal = Decimal("0")
    cout_achat: Optional[Decimal] = None
    disponibilite: bool = True
    localisation: Optional[str] = None
    
    def cout_utilisation(self, jours: int) -> Decimal:
        """Calcule le coût d'utilisation."""
        return self.cout_location_jour * Decimal(str(jours))


@dataclass
class RessourceSousTraitant:
    """Représente un sous-traitant."""
    sous_traitant_id: str
    nom: str
    specialite: str
    taux_journalier: Decimal = Decimal("0")
    contrat_en_cours: bool = False
    evaluation: Optional[float] = None  # 1.0 à 5.0


@dataclass
class Affectation:
    """Représente une affectation de ressource."""
    affectation_id: str
    mission_id: str
    ressource_id: str
    ressource_type: str  # "humaine", "materiel", "sous_traitant"
    date_debut: date
    date_fin: date
    taux_occupation: float = 1.0  # 0.0 à 1.0
    
    def duree_jours(self) -> int:
        """Calcule la durée en jours."""
        return (self.date_fin - self.date_debut).days + 1
    
    def cout_total(self, cout_journalier: Decimal) -> Decimal:
        """Calcule le coût total de l'affectation."""
        return cout_journalier * Decimal(str(self.duree_jours())) * Decimal(str(self.taux_occupation))


@dataclass
class RessourceAllocation:
    """Allocation des ressources."""
    mission_id: str
    affectations: List[Affectation] = field(default_factory=list)
    ressources_disponibles: List[Dict[str, Any]] = field(default_factory=list)
    ressources_utilisees: List[Dict[str, Any]] = field(default_factory=list)
    cout_total: Decimal = Decimal("0")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "affectations": [
                {
                    "affectation_id": a.affectation_id,
                    "mission_id": a.mission_id,
                    "ressource_id": a.ressource_id,
                    "ressource_type": a.ressource_type,
                    "date_debut": a.date_debut.isoformat(),
                    "date_fin": a.date_fin.isoformat(),
                    "duree_jours": a.duree_jours(),
                    "taux_occupation": a.taux_occupation
                }
                for a in self.affectations
            ],
            "ressources_disponibles": self.ressources_disponibles,
            "ressources_utilisees": self.ressources_utilisees,
            "cout_total": float(self.cout_total)
        }


class ResourceManager:
    """
    Gestionnaire des ressources humaines et matérielles.
    
    Alloue, suit et optimise les ressources pour les missions.
    """
    
    def __init__(self):
        self.decimal_ops = DecimalOps()
        self.ressources_humaines: Dict[str, RessourceHumaine] = {}
        self.ressources_materielles: Dict[str, RessourceMateriel] = {}
        self.sous_traitants: Dict[str, RessourceSousTraitant] = {}
        self.affectations: Dict[str, Affectation] = {}
        self._initialiser_ressources()
    
    def _initialiser_ressources(self) -> None:
        """Initialise les ressources par défaut."""
        # Ressources humaines
        self.ressources_humaines = {
            "RH-001": RessourceHumaine(
                ressource_id="RH-001",
                nom="Dupont",
                prenom="Jean",
                poste="conducteur",
                competence="gestion",
                taux_horaire=Decimal("60")
            ),
            "RH-002": RessourceHumaine(
                ressource_id="RH-002",
                nom="Martin",
                prenom="Pierre",
                poste="chef_equipe",
                competence="beton",
                taux_horaire=Decimal("45")
            ),
            "RH-003": RessourceHumaine(
                ressource_id="RH-003",
                nom="Durand",
                prenom="Marie",
                poste="compagnon",
                competence="maconnerie",
                taux_horaire=Decimal("35")
            ),
        }
        
        # Ressources matérielles
        self.ressources_materielles = {
            "MAT-001": RessourceMateriel(
                ressource_id="MAT-001",
                nom="Pelle hydraulique",
                type="engin",
                cout_location_jour=Decimal("250"),
                cout_achat=Decimal("150000")
            ),
            "MAT-002": RessourceMateriel(
                ressource_id="MAT-002",
                nom="Camion benne",
                type="vehicule",
                cout_location_jour=Decimal("180")
            ),
            "MAT-003": RessourceMateriel(
                ressource_id="MAT-003",
                nom="Échafaudage",
                type="equipement",
                cout_location_jour=Decimal("100")
            ),
        }
        
        # Sous-traitants
        self.sous_traitants = {
            "ST-001": RessourceSousTraitant(
                sous_traitant_id="ST-001",
                nom="Société XYZ",
                specialite="électricité",
                taux_journalier=Decimal("500"),
                contrat_en_cours=True,
                evaluation=4.5
            ),
            "ST-002": RessourceSousTraitant(
                sous_traitant_id="ST-002",
                nom="Entreprise ABC",
                specialite="plomberie",
                taux_journalier=Decimal("450"),
                contrat_en_cours=False,
                evaluation=4.0
            ),
        }
    
    def allouer_ressource(
        self,
        mission_id: str,
        ressource_id: str,
        ressource_type: str,
        date_debut: date,
        date_fin: date,
        taux_occupation: float = 1.0
    ) -> Optional[Affectation]:
        """
        Alloue une ressource à une mission.
        
        Args:
            mission_id: ID de la mission
            ressource_id: ID de la ressource
            ressource_type: Type de ressource
            date_debut: Date de début
            date_fin: Date de fin
            taux_occupation: Taux d'occupation (0.0 à 1.0)
        
        Returns:
            Affectation créée ou None si la ressource n'est pas disponible
        """
        # Vérifier la disponibilité
        if not self.est_ressource_disponible(ressource_id, ressource_type, date_debut, date_fin):
            logger.warning(f"Ressource {ressource_id} non disponible pour la période demandée")
            return None
        
        affectation_id = f"AFF-{mission_id}-{ressource_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        affectation = Affectation(
            affectation_id=affectation_id,
            mission_id=mission_id,
            ressource_id=ressource_id,
            ressource_type=ressource_type,
            date_debut=date_debut,
            date_fin=date_fin,
            taux_occupation=taux_occupation
        )
        
        self.affectations[affectation_id] = affectation
        
        return affectation
    
    def est_ressource_disponible(
        self,
        ressource_id: str,
        ressource_type: str,
        date_debut: date,
        date_fin: date
    ) -> bool:
        """
        Vérifie si une ressource est disponible pour une période.
        
        Args:
            ressource_id: ID de la ressource
            ressource_type: Type de ressource
            date_debut: Date de début
            date_fin: Date de fin
        
        Returns:
            True si la ressource est disponible
        """
        # Vérifier les affectations existantes
        for affectation in self.affectations.values():
            if affectation.ressource_id == ressource_id and affectation.ressource_type == ressource_type:
                # Vérifier le chevauchement de dates
                if not (date_fin < affectation.date_debut or date_debut > affectation.date_fin):
                    return False
        
        return True
    
    def obtenir_ressources_disponibles(
        self,
        date_debut: date,
        date_fin: date,
        competence: Optional[str] = None,
        type_ressource: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtient la liste des ressources disponibles pour une période.
        
        Args:
            date_debut: Date de début
            date_fin: Date de fin
            competence: Compétence requise (optionnel)
            type_ressource: Type de ressource (optionnel)
        
        Returns:
            Liste des ressources disponibles
        """
        ressources = []
        
        # Vérifier les ressources humaines
        for rh_id, rh in self.ressources_humaines.items():
            if self.est_ressource_disponible(rh_id, "humaine", date_debut, date_fin):
                if competence is None or competence in rh.competence:
                    ressources.append({
                        "ressource_id": rh_id,
                        "type": "humaine",
                        "nom": f"{rh.prenom} {rh.nom}",
                        "poste": rh.poste,
                        "competence": rh.competence,
                        "taux_horaire": float(rh.taux_horaire)
                    })
        
        # Vérifier les ressources matérielles
        if type_ressource is None or type_ressource == "materiel":
            for mat_id, mat in self.ressources_materielles.items():
                if mat.disponibilite:
                    ressources.append({
                        "ressource_id": mat_id,
                        "type": "materiel",
                        "nom": mat.nom,
                        "type_equipement": mat.type,
                        "cout_location_jour": float(mat.cout_location_jour)
                    })
        
        # Vérifier les sous-traitants
        if type_ressource is None or type_ressource == "sous_traitant":
            for st_id, st in self.sous_traitants.items():
                ressources.append({
                    "ressource_id": st_id,
                    "type": "sous_traitant",
                    "nom": st.nom,
                    "specialite": st.specialite,
                    "taux_journalier": float(st.taux_journalier),
                    "evaluation": st.evaluation
                })
        
        return ressources
    
    def calculer_cout_allocation(
        self,
        allocation: RessourceAllocation
    ) -> Decimal:
        """
        Calcule le coût total d'une allocation.
        
        Args:
            allocation: Allocation à calculer
        
        Returns:
            Coût total
        """
        cout_total = Decimal("0")
        
        for affectation in allocation.affectations:
            if affectation.ressource_type == "humaine" and affectation.ressource_id in self.ressources_humaines:
                rh = self.ressources_humaines[affectation.ressource_id]
                cout_total += rh.cout_journalier() * Decimal(str(affectation.duree_jours())) * Decimal(str(affectation.taux_occupation))
            
            elif affectation.ressource_type == "materiel" and affectation.ressource_id in self.ressources_materielles:
                mat = self.ressources_materielles[affectation.ressource_id]
                cout_total += mat.cout_utilisation(affectation.duree_jours())
            
            elif affectation.ressource_type == "sous_traitant" and affectation.ressource_id in self.sous_traitants:
                st = self.sous_traitants[affectation.ressource_id]
                cout_total += st.taux_journalier * Decimal(str(affectation.duree_jours()))
        
        return cout_total
    
    def optimiser_allocation(
        self,
        mission_id: str,
        besoins: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Optimise l'allocation des ressources pour une mission.
        
        Args:
            mission_id: ID de la mission
            besoins: Liste des besoins en ressources
        
        Returns:
            Dictionnaire avec l'allocation optimisée
        """
        affectations = []
        cout_total = Decimal("0")
        
        for besoin in besoins:
            ressource_type = besoin.get("type", "humaine")
            competence = besoin.get("competence")
            date_debut = datetime.fromisoformat(besoin.get("date_debut")).date()
            date_fin = datetime.fromisoformat(besoin.get("date_fin")).date()
            
            # Trouver une ressource disponible
            ressources_disponibles = self.obtenir_ressources_disponibles(
                date_debut, date_fin, competence, ressource_type
            )
            
            if ressources_disponibles:
                # Prendre la première ressource disponible (en production: optimiser)
                ressource = ressources_disponibles[0]
                
                affectation = self.allouer_ressource(
                    mission_id,
                    ressource["ressource_id"],
                    ressource_type,
                    date_debut,
                    date_fin
                )
                
                if affectation:
                    affectations.append(affectation.to_dict())
        
        return {
            "mission_id": mission_id,
            "affectations": affectations,
            "cout_total_estime": float(cout_total)
        }


manager = ResourceManager()


def allouer_ressource(mission_id: str, ressource_id: str, ressource_type: str, date_debut: str, date_fin: str) -> Optional[Dict[str, Any]]:
    """Alloue une ressource à une mission."""
    date_debut_obj = datetime.fromisoformat(date_debut).date()
    date_fin_obj = datetime.fromisoformat(date_fin).date()
    affectation = manager.allouer_ressource(mission_id, ressource_id, ressource_type, date_debut_obj, date_fin_obj)
    return affectation.to_dict() if affectation else None


def obtenir_ressources_disponibles(date_debut: str, date_fin: str, competence: Optional[str] = None) -> List[Dict[str, Any]]:
    """Obtient les ressources disponibles."""
    date_debut_obj = datetime.fromisoformat(date_debut).date()
    date_fin_obj = datetime.fromisoformat(date_fin).date()
    return manager.obtenir_ressources_disponibles(date_debut_obj, date_fin_obj, competence)


def calculer_cout_allocation(allocation: Dict[str, Any]) -> Dict[str, Any]:
    """Calcule le coût d'une allocation."""
    # Convertir l'allocation
    affectations = [
        Affectation(
            affectation_id=a.get("affectation_id", ""),
            mission_id=a.get("mission_id", ""),
            ressource_id=a.get("ressource_id", ""),
            ressource_type=a.get("ressource_type", ""),
            date_debut=datetime.fromisoformat(a.get("date_debut")).date() if a.get("date_debut") else date.today(),
            date_fin=datetime.fromisoformat(a.get("date_fin")).date() if a.get("date_fin") else date.today(),
            taux_occupation=a.get("taux_occupation", 1.0)
        )
        for a in allocation.get("affectations", [])
    ]
    alloc = RessourceAllocation(mission_id=allocation.get("mission_id", ""), affectations=affectations)
    cout = manager.calculer_cout_allocation(alloc)
    return {"cout_total": float(cout)}

