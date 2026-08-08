"""
SMART_AO V7 - worst_case.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - Worst Case Scenario Analyzer
=============================================
Analyse des scénarios catastrophe pour les chantiers BTP
Calcul des pertes maximales et probabilités de dépassement

Source: ARCHITECTURE_V7_ENGINE.md §3.4
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging
import statistics
from datetime import date, timedelta

logger = logging.getLogger(__name__)


@dataclass
class Risque:
    """Représente un risque identifié."""
    nom: str
    probabilite: float  # 0-1
    impact_financier: float  # €
    impact_delai: int = 0  # jours
    categorie: str = "TECHNIQUE"  # TECHNIQUE, FINANCIER, JURIDIQUE, ENVIRONNEMENTAL
    
    @property
    def risque_calcule(self) -> float:
        """Calcul du risque (probabilité × impact)."""
        return self.probabilite * self.impact_financier


@dataclass
class Scenario:
    """Représente un scénario catastrophe."""
    nom: str
    probabilite: float  # 0-1
    description: str
    impact_financier: float  # €
    impact_delai: int  # jours
    risques: List[str]  # Noms des risques inclus
    
    @property
    def risque_calcule(self) -> float:
        """Calcul du risque total du scénario."""
        return self.probabilite * self.impact_financier


@dataclass
class WorstCaseResult:
    """Résultat de l'analyse du pire scénario."""
    scenarios: List[Scenario]
    perte_maximale: float  # € (pire cas)
    perte_moyenne: float  # € (moyenne pondérée)
    probabilite_globale: float  # Probabilité d'avoir au moins un problème majeur
    scenario_pire: Optional[Scenario] = None
    recommandations: List[str] = None
    
    def __post_init__(self):
        if self.recommandations is None:
            self.recommandations = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire."""
        return {
            "scenarios": [
                {
                    "nom": s.nom,
                    "probabilite": round(s.probabilite, 4),
                    "description": s.description,
                    "impact_financier": round(s.impact_financier, 2),
                    "impact_delai": s.impact_delai,
                    "risque_calcule": round(s.risque_calcule, 2),
                    "risques": s.risques
                }
                for s in self.scenarios
            ],
            "perte_maximale": round(self.perte_maximale, 2),
            "perte_moyenne": round(self.perte_moyenne, 2),
            "probabilite_globale": round(self.probabilite_globale, 4),
            "scenario_pire": self.scenario_pire.nom if self.scenario_pire else None,
            "recommandations": self.recommandations
        }


class WorstCaseAnalyzer:
    """
    Analyseur de scénarios catastrophe pour les chantiers.
    
    Méthode:
    1. Identifier les risques individuels
    2. Combiner les risques en scénarios plausibles
    3. Calculer les impacts financiers et probabilités
    4. Déterminer le pire scénario crédible
    5. Générer des recommandations de couverture
    """
    
    def __init__(self):
        self.risques: Dict[str, Risque] = {}
        self.scenarios: List[Scenario] = []
        self.result: Optional[WorstCaseResult] = None
    
    def ajouter_risque(
        self,
        nom: str,
        probabilite: float,
        impact_financier: float,
        impact_delai: int = 0,
        categorie: str = "TECHNIQUE"
    ) -> None:
        """Ajouter un risque individuel."""
        self.risques[nom] = Risque(
            nom=nom,
            probabilite=probabilite,
            impact_financier=impact_financier,
            impact_delai=impact_delai,
            categorie=categorie
        )
    
    def analyser_scenarios(self) -> WorstCaseResult:
        """
        Analyser tous les scénarios possibles à partir des risques.
        
        Returns:
            WorstCaseResult: Résultat complet
        """
        if not self.risques:
            return WorstCaseResult(
                scenarios=[],
                perte_maximale=0,
                perte_moyenne=0,
                probabilite_globale=0,
                scenario_pire=None,
                recommandations=["Aucun risque identifié"]
            )
        
        # Générer des scénarios à partir des risques
        self._generer_scenarios()
        
        # Calculer les indicateurs
        perte_maximale = max(s.impact_financier for s in self.scenarios) if self.scenarios else 0
        perte_moyenne = sum(s.risque_calcule for s in self.scenarios) if self.scenarios else 0
        
        # Calculer la probabilité globale (1 - probabilité qu'aucun risque ne se réalise)
        prob_aucun_risque = 1.0
        for risque in self.risques.values():
            prob_aucun_risque *= (1 - risque.probabilite)
        probabilite_globale = 1 - prob_aucun_risque
        
        # Trouver le scénario le plus risqué
        scenario_pire = max(self.scenarios, key=lambda s: s.impact_financier) if self.scenarios else None
        
        # Générer des recommandations
        recommandations = self._generer_recommandations(
            perte_maximale, perte_moyenne, probabilite_globale, scenario_pire
        )
        
        self.result = WorstCaseResult(
            scenarios=self.scenarios,
            perte_maximale=perte_maximale,
            perte_moyenne=perte_moyenne,
            probabilite_globale=probabilite_globale,
            scenario_pire=scenario_pire,
            recommandations=recommandations
        )
        
        return self.result
    
    def _generer_scenarios(self) -> None:
        """Générer des scénarios à partir des risques."""
        # Scénario 1: Tous les risques se réalisent (pire cas)
        if self.risques:
            nom_risques = list(self.risques.keys())
            
            # Pire scénario: tous les risques
            impact_total = sum(r.impact_financier for r in self.risques.values())
            delai_total = sum(r.impact_delai for r in self.risques.values())
            prob_pire = 1.0
            for r in self.risques.values():
                prob_pire *= r.probabilite
            
            self.scenarios.append(Scenario(
                nom="Pire cas - Tous les risques",
                probabilite=prob_pire,
                description="Tous les risques identifiés se réalisent simultanément",
                impact_financier=impact_total,
                impact_delai=delai_total,
                risques=nom_risques
            ))
            
            # Scénario 2: Risques majeurs uniquement (probabilité > 50%)
            risques_majors = [r for r in self.risques.values() if r.probabilite > 0.5]
            if risques_majors:
                impact_majors = sum(r.impact_financier for r in risques_majors)
                delai_majors = sum(r.impact_delai for r in risques_majors)
                prob_majors = 1.0
                for r in risques_majors:
                    prob_majors *= r.probabilite
                
                self.scenarios.append(Scenario(
                    nom="Risques majeurs > 50%",
                    probabilite=prob_majors,
                    description="Seuls les risques avec probabilité > 50% se réalisent",
                    impact_financier=impact_majors,
                    impact_delai=delai_majors,
                    risques=[r.nom for r in risques_majors]
                ))
            
            # Scénario 3: Risque unique le plus impactant
            risque_max = max(self.risques.values(), key=lambda r: r.impact_financier)
            self.scenarios.append(Scenario(
                nom=f"Risque unique - {risque_max.nom}",
                probabilite=risque_max.probabilite,
                description=f"Seul le risque le plus impactant se réalise: {risque_max.nom}",
                impact_financier=risque_max.impact_financier,
                impact_delai=risque_max.impact_delai,
                risques=[risque_max.nom]
            ))
            
            # Scénario 4: Combinaison des 2 risques les plus probables
            risques_tries = sorted(self.risques.values(), key=lambda r: r.probabilite, reverse=True)
            if len(risques_tries) >= 2:
                r1, r2 = risques_tries[0], risques_tries[1]
                self.scenarios.append(Scenario(
                    nom=f"2 risques les plus probables",
                    probabilite=r1.probabilite * r2.probabilite,
                    description=f"Combinaison des 2 risques les plus probables: {r1.nom} et {r2.nom}",
                    impact_financier=r1.impact_financier + r2.impact_financier,
                    impact_delai=r1.impact_delai + r2.impact_delai,
                    risques=[r1.nom, r2.nom]
                ))
    
    def _generer_recommandations(
        self,
        perte_maximale: float,
        perte_moyenne: float,
        probabilite_globale: float,
        scenario_pire: Optional[Scenario]
    ) -> List[str]:
        """Générer des recommandations de couverture."""
        recommandations = []
        
        if probabilite_globale < 0.1:
            recommandations.append(
                f"✅ Risque global faible ({probabilite_globale*100:.1f}%)"
            )
        elif probabilite_globale < 0.3:
            recommandations.append(
                f"⚠️ Risque global modéré ({probabilite_globale*100:.1f}%)"
            )
            recommandations.append(
                "Recommandé: prévoir une provision pour aléas"
            )
        elif probabilite_globale < 0.6:
            recommandations.append(
                f"🔴 Risque global élevé ({probabilite_globale*100:.1f}%)"
            )
            recommandations.append(
                "Urgent: provision minimale de 5% du montant du marché"
            )
        else:
            recommandations.append(
                f"💥 Risque global très élevé ({probabilite_globale*100:.1f}%)"
            )
            recommandations.append(
                "Critique: provision minimale de 10-15% du montant du marché"
            )
        
        # Recommandations financières
        if perte_maximale > 0:
            recommandations.append(
                f"💰 Perte maximale estimée: {perte_maximale:.2f} €"
            )
            recommandations.append(
                f"📊 Provision recommandée: {perte_maximale * 0.5:.2f} € (50% de couverture)"
            )
        
        # Recommandations spécifiques au pire scénario
        if scenario_pire:
            recommandations.append(
                f"🎯 Scénario le plus risqué: {scenario_pire.nom}"
            )
            recommandations.append(
                f"   - Impact: {scenario_pire.impact_financier:.2f} €"
            )
            recommandations.append(
                f"   - Délai: +{scenario_pire.impact_delai} jours"
            )
        
        return recommandations


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def analyser_pire_scenario(
    risques: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Analyser le pire scénario à partir d'une liste de risques.
    
    Args:
        risques: Liste de risques avec nom, probabilite, impact_financier
    
    Returns:
        Résultat de l'analyse du pire scénario
    """
    analyzer = WorstCaseAnalyzer()
    
    for risque in risques:
        analyzer.ajouter_risque(
            nom=risque.get("nom", "Inconnu"),
            probabilite=risque.get("probabilite", 0),
            impact_financier=risque.get("impact_financier", 0),
            impact_delai=risque.get("impact_delai", 0),
            categorie=risque.get("categorie", "TECHNIQUE")
        )
    
    result = analyzer.analyser_scenarios()
    return result.to_dict()


if __name__ == "__main__":
    # Exemple d'utilisation
    analyzer = WorstCaseAnalyzer()
    
    # Ajouter des risques typiques pour un chantier
    analyzer.ajouter_risque(
        nom="Retard fournisseur",
        probabilite=0.30,
        impact_financier=15000,
        impact_delai=30,
        categorie="TECHNIQUE"
    )
    
    analyzer.ajouter_risque(
        nom="Hausse prix matériaux",
        probabilite=0.60,
        impact_financier=25000,
        impact_delai=0,
        categorie="FINANCIER"
    )
    
    analyzer.ajouter_risque(
        nom="Grève",
        probabilite=0.20,
        impact_financier=10000,
        impact_delai=21,
        categorie="SOCIAL"
    )
    
    analyzer.ajouter_risque(
        nom="Contentieux",
        probabilite=0.15,
        impact_financier=50000,
        impact_delai=60,
        categorie="JURIDIQUE"
    )
    
    # Analyser
    result = analyzer.analyser_scenarios()
    
    print("Analyse des scénarios catastrophe:")
    print(f"Perte maximale: {result.perte_maximale:.2f} €")
    print(f"Perte moyenne pondérée: {result.perte_moyenne:.2f} €")
    print(f"Probabilité globale: {result.probabilite_globale*100:.1f}%")
    print(f"Scénario le plus risqué: {result.scenario_pire}")
    print("\nScénarios:")
    for s in result.scenarios:
        print(f"  - {s.nom}: {s.impact_financier:.2f} € (prob: {s.probabilite*100:.1f}%)")
    print(f"\nRecommandations:")
    for r in result.recommandations:
        print(f"  - {r}")

