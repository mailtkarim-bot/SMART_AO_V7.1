"""
SMART_AO V7 - rep_cost.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Coûts de Réparation - Calcul des coûts de réparation et maintenance
Source: ARCHITECTURE_V7_ENGINE.md §3.4
"""

from typing import Dict, List, Optional, Any
from decimal import Decimal, getcontext
from dataclasses import dataclass, field
from datetime import datetime
import logging

from app.engines.math_engine.decimal_ops import DecimalOps

getcontext().prec = 28
logger = logging.getLogger(__name__)


@dataclass
class Reparation:
    """Représente une réparation."""
    reparation_id: str
    type_travaux: str  # "gros_oeuvre", "second_oeuvre", "finitions", "equipements"
    description: str
    quantite: Decimal = Decimal("1")
    unite: str = "u"
    cout_unitaire: Decimal = Decimal("0")
    main_d_oeuvre: Decimal = Decimal("0")  # Heures
    cout_total: Decimal = Decimal("0")
    
    def calculer_cout_total(self, taux_horaire: Decimal = Decimal("40")) -> Decimal:
        """Calcule le coût total avec main d'oeuvre."""
        self.cout_total = (self.cout_unitaire * self.quantite) + (self.main_d_oeuvre * taux_horaire)
        return self.cout_total


@dataclass
class CategorieReparation:
    """Catégorie de réparations."""
    categorie_id: str
    nom: str
    description: str
    reparations: List[Reparation] = field(default_factory=list)
    cout_moyen_par_m2: Optional[Decimal] = None
    
    def cout_total(self) -> Decimal:
        """Calcule le coût total de la catégorie."""
        return sum(r.calculer_cout_total() for r in self.reparations)


@dataclass
class DevisReparation:
    """Devis complet de réparation."""
    devis_id: str
    mission_id: str
    nom_projet: str
    categories: List[CategorieReparation] = field(default_factory=list)
    cout_total_ht: Decimal = Decimal("0")
    cout_total_ttc: Decimal = Decimal("0")
    tva: Decimal = Decimal("0.20")  # 20%
    date_creation: Optional[str] = None
    validite_jours: int = 30
    
    def calculer_totaux(self) -> None:
        """Calcule les totaux HT et TTC."""
        self.cout_total_ht = sum(c.cout_total() for c in self.categories)
        self.cout_total_ttc = self.cout_total_ht * (Decimal("1") + self.tva)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire."""
        self.calculer_totaux()
        return {
            "devis_id": self.devis_id,
            "mission_id": self.mission_id,
            "nom_projet": self.nom_projet,
            "cout_total_ht": float(self.cout_total_ht),
            "cout_total_ttc": float(self.cout_total_ttc),
            "tva": float(self.tva),
            "date_creation": self.date_creation,
            "validite_jours": self.validite_jours,
            "categories": [
                {
                    "categorie_id": c.categorie_id,
                    "nom": c.nom,
                    "description": c.description,
                    "cout_total": float(c.cout_total()),
                    "reparations": [
                        {
                            "reparation_id": r.reparation_id,
                            "type_travaux": r.type_travaux,
                            "description": r.description,
                            "quantite": float(r.quantite),
                            "unite": r.unite,
                            "cout_unitaire": float(r.cout_unitaire),
                            "cout_total": float(r.calculer_cout_total())
                        }
                        for r in c.reparations
                    ]
                }
                for c in self.categories
            ]
        }


class RepCostCalculator:
    """
    Calculateur de coûts de réparation.
    
    Estime les coûts de réparation pour différents types de travaux
    (gros œuvre, second œuvre, finitions, etc.) avec prise en compte
    des matériaux, de la main d'œuvre et des marges.
    """
    
    # Tarifs moyens par type de travaux (€/m² ou €/u)
    TARIFS_MOYENS = {
        "gros_oeuvre": {
            "demolition": Decimal("50"),
            "fondations": Decimal("120"),
            "structure_beton": Decimal("150"),
            "structure_acier": Decimal("200")
        },
        "second_oeuvre": {
            "maconnerie": Decimal("80"),
            "charpente": Decimal("100"),
            "menuiserie": Decimal("150"),
            "isolation": Decimal("40"),
            "plomberie": Decimal("70"),
            "electricite": Decimal("85")
        },
        "finitions": {
            "peinture": Decimal("30"),
            "revetement_sol": Decimal("60"),
            "carrelage": Decimal("80"),
            "plafond": Decimal("45")
        },
        "equipements": {
            "chauffage": Decimal("200"),
            "climatisation": Decimal("180"),
            "ventilation": Decimal("100")
        }
    }
    
    # Coûts de main d'œuvre (€/heure)
    TAUX_HORAIRES = {
        "ouvrier": Decimal("35"),
        "compagnon": Decimal("45"),
        "chef_equipe": Decimal("60"),
        "expert": Decimal("80")
    }
    
    def __init__(self):
        self.decimal_ops = DecimalOps()
    
    def calculer_cout_reparation(
        self,
        mission_id: str,
        devis_id: str,
        reparations: List[Dict[str, Any]]
    ) -> DevisReparation:
        """
        Calcule le coût des réparations.
        
        Args:
            mission_id: ID de la mission
            devis_id: ID du devis
            reparations: Liste des réparations à calculer
        
        Returns:
            Devis de réparation avec coûts calculés
        """
        categories_map = {}
        
        for rep_data in reparations:
            categorie_nom = rep_data.get("categorie", "autre")
            type_travaux = rep_data.get("type_travaux", "inconnu")
            
            # Créer ou récupérer la catégorie
            if categorie_nom not in categories_map:
                categories_map[categorie_nom] = CategorieReparation(
                    categorie_id=f"CAT-{categorie_nom}",
                    nom=categorie_nom,
                    description=f"Travaux de {categorie_nom}"
                )
            
            # Calculer le coût unitaire
            cout_unitaire = self._obtenir_tarif(type_travaux, categorie_nom)
            
            # Créer la réparation
            reparation = Reparation(
                reparation_id=rep_data.get("reparation_id", f"REP-{len(categories_map[categorie_nom].reparations)+1}"),
                type_travaux=type_travaux,
                description=rep_data.get("description", ""),
                quantite=Decimal(str(rep_data.get("quantite", 1))),
                unite=rep_data.get("unite", "u"),
                cout_unitaire=cout_unitaire,
                main_d_oeuvre=Decimal(str(rep_data.get("main_d_oeuvre", 0)))
            )
            
            categories_map[categorie_nom].reparations.append(reparation)
        
        # Créer le devis
        devis = DevisReparation(
            devis_id=devis_id,
            mission_id=mission_id,
            nom_projet=rep_data.get("nom_projet", f"Devis-{devis_id}"),
            categories=list(categories_map.values()),
            tva=Decimal(str(rep_data.get("tva", 0.20)))
        )
        
        devis.calculer_totaux()
        
        return devis
    
    def _obtenir_tarif(self, type_travaux: str, categorie: str) -> Decimal:
        """Obtient le tarif moyen pour un type de travaux."""
        if categorie in self.TARIFS_MOYENS:
            if type_travaux in self.TARIFS_MOYENS[categorie]:
                return self.TARIFS_MOYENS[categorie][type_travaux]
        
        # Retourner un tarif par défaut
        return Decimal("50")
    
    def estimer_cout_par_m2(
        self,
        surface: Decimal,
        type_batiment: str,
        niveau_degradation: str = "moyen"
    ) -> Dict[str, Any]:
        """
        Estime le coût de réparation par m².
        
        Args:
            surface: Surface à réparer en m²
            type_batiment: Type de bâtiment ("logement", "bureau", "industriel")
            niveau_degradation: Niveau de dégradation ("leger", "moyen", "important")
        
        Returns:
            Dictionnaire avec l'estimation des coûts
        """
        # Coûts moyens par type de bâtiment (€/m²)
        couts_par_type = {
            "logement": {"leger": Decimal("100"), "moyen": Decimal("200"), "important": Decimal("400")},
            "bureau": {"leger": Decimal("120"), "moyen": Decimal("250"), "important": Decimal("500")},
            "industriel": {"leger": Decimal("150"), "moyen": Decimal("300"), "important": Decimal("600")}
        }
        
        cout_m2 = couts_par_type.get(type_batiment, {}).get(niveau_degradation, Decimal("200"))
        
        cout_total_ht = surface * cout_m2
        cout_total_ttc = cout_total_ht * Decimal("1.20")  # TVA 20%
        
        return {
            "surface": float(surface),
            "type_batiment": type_batiment,
            "niveau_degradation": niveau_degradation,
            "cout_par_m2": float(cout_m2),
            "cout_total_ht": float(cout_total_ht),
            "cout_total_ttc": float(cout_total_ttc),
            "tva": 0.20
        }
    
    def generer_devis_complet(
        self,
        mission_id: str,
        surface: Decimal,
        type_batiment: str,
        reparations: List[Dict[str, Any]]
    ) -> DevisReparation:
        """
        Génère un devis complet avec estimation et détails.
        
        Args:
            mission_id: ID de la mission
            surface: Surface totale
            type_batiment: Type de bâtiment
            reparations: Liste des réparations spécifiques
        
        Returns:
            Devis complet
        """
        # Estimer le coût global
        estimation = self.estimer_cout_par_m2(surface, type_batiment)
        
        # Créer le devis avec les réparations
        devis_id = f"DEVIS-{mission_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        # Ajouter les réparations du devis
        for rep in reparations:
            rep["devis_id"] = devis_id
        
        devis = self.calculer_cout_reparation(mission_id, devis_id, reparations)
        
        return devis


calculateur_rep = RepCostCalculator()


def calculer_cout_reparation(mission_id: str, reparations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calcule le coût de réparation."""
    devis_id = f"DEVIS-{mission_id}-REP-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    devis = calculateur_rep.calculer_cout_reparation(mission_id, devis_id, reparations)
    return devis.to_dict()


def estimer_cout_par_m2(surface: float, type_batiment: str = "logement", niveau: str = "moyen") -> Dict[str, Any]:
    """Estime le coût de réparation par m²."""
    return calculateur_rep.estimer_cout_par_m2(Decimal(str(surface)), type_batiment, niveau)


def generer_devis_reparation(mission_id: str, surface: float, type_batiment: str, reparations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Génère un devis complet de réparation."""
    devis = calculateur_rep.generer_devis_complet(mission_id, Decimal(str(surface)), type_batiment, reparations)
    return devis.to_dict()


