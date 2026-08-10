"""
SMART_AO V7 - eplusc_calculator.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Calculateur E+C- - Calcul des indicateurs Environnementaux et Climatiques
Source: ARCHITECTURE_V7_ENGINE.md §3.4
"""

from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal, getcontext
from dataclasses import dataclass, field
import logging

from app.engines.math_engine.decimal_ops import DecimalOps

# Configuration de la précision pour Decimal
getcontext().prec = 28

logger = logging.getLogger(__name__)


@dataclass
class EplusCComponent:
    """Composant du calcul E+C-."""
    nom: str
    valeur: Decimal
    unite: str
    description: str = ""
    poids: Decimal = Decimal("1.0")
    
    def contribution_ponderee(self) -> Decimal:
        """Calcule la contribution pondérée du composant."""
        return self.valeur * self.poids


@dataclass
class EplusCResult:
    """Résultat du calcul E+C-."""
    score_energie: Decimal
    score_carbone: Decimal
    score_eplusc: Decimal
    classe_energie: str
    classe_carbone: str
    classe_eplusc: str
    details: Dict[str, EplusCComponent] = field(default_factory=dict)
    recommandations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire."""
        return {
            "score_energie": float(self.score_energie),
            "score_carbone": float(self.score_carbone),
            "score_eplusc": float(self.score_eplusc),
            "classe_energie": self.classe_energie,
            "classe_carbone": self.classe_carbone,
            "classe_eplusc": self.classe_eplusc,
            "details": {k: {"nom": v.nom, "valeur": float(v.valeur), "unite": v.unite} 
                       for k, v in self.details.items()},
            "recommandations": self.recommandations
        }


class EplusCCalculator:
    """
    Calculateur des indicateurs E+C- (Énergie et Carbone) pour les bâtiments.
    
    Conforme à la réglementation RE2020 et aux normes en vigueur.
    Calcul les indicateurs BES (Besoin en Énergie du Bâtiment), 
    CEP (Consommation d'Énergie Primaire), et IC (Impact Carbone).
    """
    
    # Seuil pour les classes E+C-
    SEUILS_ENERGIE = {
        "A": Decimal("200"),
        "B": Decimal("250"),
        "C": Decimal("300"),
        "D": Decimal("350"),
        "E": Decimal("400"),
        "F": Decimal("450"),
        "G": Decimal("500"),
    }
    
    SEUILS_CARBONE = {
        "A+": Decimal("800"),
        "A": Decimal("1000"),
        "B": Decimal("1200"),
        "C": Decimal("1400"),
        "D": Decimal("1600"),
        "E": Decimal("1800"),
    }
    
    def __init__(self):
        self.decimal_ops = DecimalOps()
    
    def calculer_eplusc(
        self,
        surface: Decimal,
        bes: Decimal,  # Besoin en Énergie du Bâtiment (kWh/m²/an)
        cep: Decimal,  # Consommation Énergie Primaire (kWh/m²/an)
        ic: Decimal,   # Impact Carbone (kgCO2e/m²)
        details: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> EplusCResult:
        """
        Calcule le score E+C- à partir des indicateurs de base.
        
        Args:
            surface: Surface du bâtiment en m²
            bes: Besoin en Énergie du Bâtiment (kWh/m²/an)
            cep: Consommation Énergie Primaire (kWh/m²/an)
            ic: Impact Carbone (kgCO2e/m²)
            details: Dictionnaire optionnel avec des détails par composant
        
        Returns:
            EplusCResult avec les scores et classes calculés
        """
        # Calculer le score énergie (basé sur CEP)
        score_energie = self._calculer_score_energie(cep)
        classe_energie = self._determiner_classe_energie(score_energie)
        
        # Calculer le score carbone (basé sur IC)
        score_carbone = self._calculer_score_carbone(ic)
        classe_carbone = self._determiner_classe_carbone(score_carbone)
        
        # Calculer le score E+C- global
        score_eplusc = self._calculer_score_eplusc(score_energie, score_carbone)
        classe_eplusc = self._determiner_classe_eplusc(score_energie, score_carbone)
        
        # Construire les détails
        result_details = {
            "bes": EplusCComponent(
                nom="BES",
                valeur=bes,
                unite="kWh/m²/an",
                description="Besoin en Énergie du Bâtiment"
            ),
            "cep": EplusCComponent(
                nom="CEP",
                valeur=cep,
                unite="kWh/m²/an",
                description="Consommation Énergie Primaire"
            ),
            "ic": EplusCComponent(
                nom="IC",
                valeur=ic,
                unite="kgCO2e/m²",
                description="Impact Carbone"
            ),
        }
        
        # Ajouter les détails supplémentaires si fournis
        if details:
            for nom, data in details.items():
                result_details[nom] = EplusCComponent(
                    nom=nom,
                    valeur=Decimal(str(data.get("valeur", 0))),
                    unite=data.get("unite", ""),
                    description=data.get("description", ""),
                    poids=Decimal(str(data.get("poids", 1.0)))
                )
        
        # Générer des recommandations
        recommandations = self._generer_recommandations(
            score_energie, score_carbone, classe_eplusc
        )
        
        return EplusCResult(
            score_energie=score_energie,
            score_carbone=score_carbone,
            score_eplusc=score_eplusc,
            classe_energie=classe_energie,
            classe_carbone=classe_carbone,
            classe_eplusc=classe_eplusc,
            details=result_details,
            recommandations=recommandations
        )
    
    def _calculer_score_energie(self, cep: Decimal) -> Decimal:
        """Calcule le score énergie à partir du CEP."""
        # Normalisation sur une échelle de 0 à 500
        return min(Decimal("500"), max(Decimal("0"), cep * Decimal("1")))
    
    def _calculer_score_carbone(self, ic: Decimal) -> Decimal:
        """Calcule le score carbone à partir de l'IC."""
        # Normalisation sur une échelle de 0 à 2000
        return min(Decimal("2000"), max(Decimal("0"), ic * Decimal("1")))
    
    def _calculer_score_eplusc(self, score_energie: Decimal, score_carbone: Decimal) -> Decimal:
        """Calcule le score E+C- global."""
        # Moyenne pondérée (50% énergie, 50% carbone)
        return (score_energie * Decimal("0.5") + score_carbone * Decimal("0.25"))
    
    def _determiner_classe_energie(self, score: Decimal) -> str:
        """Détermine la classe énergie à partir du score."""
        for classe, seuil in sorted(self.SEUILS_ENERGIE.items(), key=lambda x: x[1]):
            if score <= seuil:
                return classe
        return "G"
    
    def _determiner_classe_carbone(self, score: Decimal) -> str:
        """Détermine la classe carbone à partir du score."""
        for classe, seuil in sorted(self.SEUILS_CARBONE.items(), key=lambda x: x[1]):
            if score <= seuil:
                return classe
        return "E"
    
    def _determiner_classe_eplusc(self, score_energie: Decimal, score_carbone: Decimal) -> str:
        """Détermine la classe E+C- globale."""
        # La classe globale est la moins bonne des deux classes
        classe_energie = self._determiner_classe_energie(score_energie)
        classe_carbone = self._determiner_classe_carbone(score_carbone)
        
        # Ordre des classes (meilleure à moins bonne)
        ordre_classes = ["A+", "A", "B", "C", "D", "E", "F", "G"]
        
        idx_energie = ordre_classes.index(classe_energie) if classe_energie in ordre_classes else len(ordre_classes)
        idx_carbone = ordre_classes.index(classe_carbone) if classe_carbone in ordre_classes else len(ordre_classes)
        
        # Prendre la pire classe
        return ordre_classes[max(idx_energie, idx_carbone)]
    
    def _generer_recommandations(
        self, 
        score_energie: Decimal, 
        score_carbone: Decimal, 
        classe_eplusc: str
    ) -> List[str]:
        """Génère des recommandations pour améliorer le score E+C-."""
        recommandations = []
        
        if classe_eplusc in ["A+", "A"]:
            recommandations.append("✅ Excellente performance E+C- - maintenir les bonnes pratiques")
        elif classe_eplusc in ["B", "C"]:
            recommandations.append("⚠️ Bonne performance mais des améliorations sont possibles")
            if score_energie > self.SEUILS_ENERGIE["B"]:
                recommandations.append("Améliorer l'isolation thermique pour réduire le BES")
            if score_carbone > self.SEUILS_CARBONE["B"]:
                recommandations.append("Utiliser des matériaux bas-carbone pour réduire l'IC")
        else:
            recommandations.append("🔴 Performance insuffisante - actions correctives nécessaires")
            recommandations.append("Réviser la conception du bâtiment")
            recommandations.append("Optimiser les systèmes de chauffage/climatisation")
            recommandations.append("Choisir des matériaux à faible impact carbone")
        
        return recommandations
    
    def calculer_scenarios_amelioration(
        self,
        cep_actuel: Decimal,
        ic_actuel: Decimal,
        ameliorations: Dict[str, Dict[str, Any]]
    ) -> List[EplusCResult]:
        """
        Calcule l'impact de différentes améliorations sur le score E+C-.
        
        Args:
            cep_actuel: CEP actuel
            ic_actuel: IC actuel
            ameliorations: Dictionnaire de scénarios d'amélioration
        
        Returns:
            Liste des résultats E+C- pour chaque scénario
        """
        scenarios = []
        
        for nom, data in ameliorations.items():
            cep_ameliore = cep_actuel - Decimal(str(data.get("reduction_cep", 0)))
            ic_ameliore = ic_actuel - Decimal(str(data.get("reduction_ic", 0)))
            
            result = self.calculer_eplusc(
                surface=Decimal("1000"),  # Surface par défaut
                bes=Decimal("100"),
                cep=cep_ameliore,
                ic=ic_ameliore
            )
            scenarios.append(result)
        
        return scenarios


# Instance globale du calculateur
calculateur_eplusc = EplusCCalculator()


# Fonctions utilitaires
def calculer_eplusc(
    surface: float,
    bes: float,
    cep: float,
    ic: float,
    details: Optional[Dict[str, Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Fonction utilitaire pour calculer E+C-."""
    result = calculateur_eplusc.calculer_eplusc(
        surface=Decimal(str(surface)),
        bes=Decimal(str(bes)),
        cep=Decimal(str(cep)),
        ic=Decimal(str(ic)),
        details=details
    )
    return result.to_dict()


def verifier_conformite_re2020(
    cep: float,
    ic: float,
    type_batiment: str = "logement"
) -> Dict[str, Any]:
    """
    Vérifie la conformité RE2020 d'un bâtiment.
    
    Args:
        cep: Consommation Énergie Primaire (kWh/m²/an)
        ic: Impact Carbone (kgCO2e/m²)
        type_batiment: Type de bâtiment (logement, bureau, etc.)
    
    Returns:
        Dictionnaire avec le statut de conformité
    """
    result = calculateur_eplusc.calculer_eplusc(
        surface=Decimal("1000"),
        bes=Decimal("100"),
        cep=Decimal(str(cep)),
        ic=Decimal(str(ic))
    )
    
    # Seuil RE2020 pour le logement (exemple)
    seuil_cep_re2020 = {"logement": 200, "bureau": 150}
    seuil_ic_re2020 = {"logement": 1000, "bureau": 800}
    
    cep_seuil = seuil_cep_re2020.get(type_batiment, 200)
    ic_seuil = seuil_ic_re2020.get(type_batiment, 1000)
    
    return {
        "conforme_re2020": cep <= cep_seuil and ic <= ic_seuil,
        "conforme_cep": cep <= cep_seuil,
        "conforme_ic": ic <= ic_seuil,
        "details": result.to_dict()
    }

