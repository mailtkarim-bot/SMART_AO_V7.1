"""
SMART_AO V7 - chiffrage_pulp.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - Chiffrage PULP Solver
====================================
Optimisation des coûts de chantier par programmation linéaire
Utilise PuLP pour optimiser l'affectation des ressources et minimiser les coûts

Source: ARCHITECTURE_V7_ENGINE.md §3.4
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging

# Import conditionnel pour éviter les erreurs si PuLP n'est pas installé
try:
    import pulp
    PULP_AVAILABLE = True
except ImportError:
    PULP_AVAILABLE = False
    logging.warning("PuLP library not available. ChiffragePulpSolver will use fallback calculations.")

# Import conditionnel pour OR-Tools (scheduling / programmation linéaire)
try:
    from ortools.linear_solver import pywraplp
    ORTOOLS_AVAILABLE = True
except ImportError:
    ORTOOLS_AVAILABLE = False
    logging.warning("OR-Tools library not available. ChiffragePulpSolver will use PuLP or fallback.")

logger = logging.getLogger(__name__)


@dataclass
class Ressource:
    """Représente une ressource de chantier."""
    nom: str
    cout_unitaire: float  # €/unité
    disponibilite: float  # Quantité disponible
    capacite: float = 1.0  # Capacité par unité
    
    def cout_total(self, quantite: float) -> float:
        """Calcul du coût total pour une quantité donnée."""
        return self.cout_unitaire * quantite


@dataclass
class Tache:
    """Représente une tâche de chantier."""
    nom: str
    quantite_requise: float  # Quantité de travail nécessaire
    ressources_requises: Dict[str, float]  # {nom_ressource: quantité_necessaire}
    duree_jours: int = 1
    priorite: int = 1  # 1 = basse, 5 = haute


@dataclass
class SolutionChiffrage:
    """Représente une solution d'optimisation de chiffrage."""
    cout_total: float
    affectation_ressources: Dict[str, Dict[str, float]]  # {nom_tache: {nom_ressource: quantité}}
    temps_total: int
    est_optimale: bool = False
    message: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire."""
        return {
            "cout_total": round(self.cout_total, 2),
            "affectation_ressources": self.affectation_ressources,
            "temps_total": self.temps_total,
            "est_optimale": self.est_optimale,
            "message": self.message
        }


class ChiffragePulpSolver:
    """
    Solveur d'optimisation de chiffrage utilisant PuLP.
    
    Objectif: Minimiser le coût total du chantier tout en respectant:
    - Les contraintes de disponibilité des ressources
    - Les exigences des tâches
    - Les délais de chantier
    """
    
    def __init__(self):
        self.ressources: Dict[str, Ressource] = {}
        self.taches: Dict[str, Tache] = {}
        self.solution: Optional[SolutionChiffrage] = None
    
    def ajouter_ressource(self, nom: str, cout_unitaire: float, disponibilite: float, capacite: float = 1.0) -> None:
        """Ajouter une ressource disponible."""
        self.ressources[nom] = Ressource(nom, cout_unitaire, disponibilite, capacite)
    
    def ajouter_tache(self, nom: str, quantite_requise: float, 
                     ressources_requises: Dict[str, float], 
                     duree_jours: int = 1, priorite: int = 1) -> None:
        """Ajouter une tâche à optimiser."""
        self.taches[nom] = Tache(nom, quantite_requise, ressources_requises, duree_jours, priorite)
    
    def _create_pulp_problem(self) -> Optional['pulp.LpProblem']:
        """Créer le problème PuLP pour l'optimisation."""
        if not PULP_AVAILABLE:
            logger.error("PuLP non disponible. Utilisation de la méthode de fallback.")
            return None
        
        # Créer le problème de minimisation
        prob = pulp.LpProblem("Chiffrage_Optimisation", pulp.LpMinimize)
        
        # Variables de décision: quantité de chaque ressource affectée à chaque tâche
        variables = {}
        for tache_nom, tache in self.taches.items():
            for ressource_nom, quantite_requise in tache.ressources_requises.items():
                if ressource_nom in self.ressources:
                    # x[tache][ressource] = quantité affectée
                    variables[(tache_nom, ressource_nom)] = pulp.LpVariable(
                        f"x_{tache_nom}_{ressource_nom}",
                        lowBound=0,
                        upBound=self.ressources[ressource_nom].disponibilite,
                        cat=pulp.LpContinuous
                    )
        
        # Fonction objectif: minimiser le coût total
        cout_total = pulp.lpSum(
            variables[(t, r)] * self.ressources[r].cout_unitaire * self.taches[t].ressources_requises[r]
            for t, r in variables.keys()
        )
        prob += cout_total, "Coût_Total"
        
        # Contraintes
        # 1. Respecter les besoins de chaque tâche
        for tache_nom, tache in self.taches.items():
            for ressource_nom, quantite_requise in tache.ressources_requises.items():
                if (tache_nom, ressource_nom) in variables:
                    prob += variables[(tache_nom, ressource_nom)] >= quantite_requise, \
                           f"Besoins_{tache_nom}_{ressource_nom}"
        
        # 2. Ne pas dépasser la disponibilité des ressources
        for ressource_nom, ressource in self.ressources.items():
            ressource_vars = [(t, r) for t, r in variables.keys() if r == ressource_nom]
            if ressource_vars:
                prob += pulp.lpSum(variables[var] for var in ressource_vars) <= ressource.disponibilite, \
                       f"Disponibilite_{ressource_nom}"
        
        return prob
    
    def _create_ortools_problem(self) -> Optional['pywraplp.Solver']:
        """Créer le problème OR-Tools (CBC/SCIP) pour l'optimisation."""
        if not ORTOOLS_AVAILABLE:
            return None

        solver = pywraplp.Solver.CreateSolver("SCIP")
        if not solver:
            solver = pywraplp.Solver.CreateSolver("CBC")
        if not solver:
            return None

        variables = {}
        for tache_nom, tache in self.taches.items():
            for ressource_nom in tache.ressources_requises:
                if ressource_nom in self.ressources:
                    var_name = f"x_{tache_nom}_{ressource_nom}"
                    variables[(tache_nom, ressource_nom)] = solver.NumVar(
                        0, self.ressources[ressource_nom].disponibilite, var_name
                    )

        # Fonction objectif : minimiser le coût total
        objective = solver.Objective()
        for (tache_nom, ressource_nom), var in variables.items():
            coef = self.ressources[ressource_nom].cout_unitaire * self.taches[tache_nom].ressources_requises[ressource_nom]
            objective.SetCoefficient(var, coef)
        objective.SetMinimization()

        # Contraintes : respecter les besoins de chaque tâche
        for tache_nom, tache in self.taches.items():
            for ressource_nom, quantite_requise in tache.ressources_requises.items():
                if (tache_nom, ressource_nom) in variables:
                    solver.Add(variables[(tache_nom, ressource_nom)] >= quantite_requise)

        # Contraintes : ne pas dépasser la disponibilité des ressources
        for ressource_nom, ressource in self.ressources.items():
            vars_for_resource = [
                var for (t, r), var in variables.items() if r == ressource_nom
            ]
            if vars_for_resource:
                solver.Add(solver.Sum(vars_for_resource) <= ressource.disponibilite)

        return solver

    def _resolvere_ortools(self) -> Optional[SolutionChiffrage]:
        """Résoudre avec OR-Tools."""
        solver = self._create_ortools_problem()
        if solver is None:
            return None

        status = solver.Solve()
        if status == pywraplp.Solver.OPTIMAL:
            affectation = {}
            cout_total = 0.0
            for tache_nom, tache in self.taches.items():
                for ressource_nom in tache.ressources_requises:
                    if ressource_nom not in self.ressources:
                        continue
                    var_name = f"x_{tache_nom}_{ressource_nom}"
                    var = solver.LookupVariable(var_name)
                    if var is None:
                        continue
                    value = var.solution_value()
                    if value > 1e-9:
                        if tache_nom not in affectation:
                            affectation[tache_nom] = {}
                        affectation[tache_nom][ressource_nom] = float(value)
                        cout_total += value * self.ressources[ressource_nom].cout_unitaire

            temps_total = sum(tache.duree_jours for tache in self.taches.values())
            return SolutionChiffrage(
                cout_total=cout_total,
                affectation_ressources=affectation,
                temps_total=temps_total,
                est_optimale=True,
                message=f"Solution optimale OR-Tools (coût: {cout_total:.2f} €)"
            )
        return None

    def resolvere(self) -> SolutionChiffrage:
        """
        Résoudre le problème d'optimisation de chiffrage.

        Ordre de résolution :
        1. OR-Tools (programmation linéaire CBC/SCIP)
        2. PuLP (CBC embarqué)
        3. Fallback déterministe

        Returns:
            SolutionChiffrage: La solution optimale ou une approximation
        """
        if not self.taches:
            return SolutionChiffrage(
                cout_total=0,
                affectation_ressources={},
                temps_total=0,
                est_optimale=True,
                message="Aucune tâche à optimiser"
            )

        # 1. Essai OR-Tools
        if ORTOOLS_AVAILABLE:
            try:
                solution = self._resolvere_ortools()
                if solution is not None:
                    self.solution = solution
                    return self.solution
            except Exception as e:
                logger.warning(f"OR-Tools a échoué: {e}, passage à PuLP")

        # 2. Essai PuLP
        if not PULP_AVAILABLE:
            return self._resolvere_fallback()

        try:
            prob = self._create_pulp_problem()
            if prob is None:
                return self._resolvere_fallback()

            prob.solve(pulp.PULP_CBC_CMD(msg=0))

            if prob.status == pulp.LpStatusOptimal:
                affectation = {}
                cout_total = 0

                for var in prob.variables():
                    if var.value() > 0:
                        tache_nom, ressource_nom = var.name.replace("x_", "").split("_")
                        if tache_nom not in affectation:
                            affectation[tache_nom] = {}
                        affectation[tache_nom][ressource_nom] = float(var.value())
                        cout_total += var.value() * self.ressources[ressource_nom].cout_unitaire

                temps_total = sum(tache.duree_jours for tache in self.taches.values())

                self.solution = SolutionChiffrage(
                    cout_total=cout_total,
                    affectation_ressources=affectation,
                    temps_total=temps_total,
                    est_optimale=True,
                    message=f"Solution optimale PuLP (coût: {cout_total:.2f} €)"
                )
            else:
                self.solution = self._resolvere_fallback()
                self.solution.message = f"Solution non optimale: {pulp.LpStatus[prob.status]}"

        except Exception as e:
            logger.error(f"Erreur lors de la résolution PuLP: {e}")
            self.solution = self._resolvere_fallback()
            self.solution.message = f"Erreur de résolution: {str(e)}"

        return self.solution

    def _resolvere_fallback(self) -> SolutionChiffrage:
        """
        Méthode de fallback lorsque PuLP n'est pas disponible.
        Affecte les ressources proportionnellement aux besoins.
        """
        affectation = {}
        cout_total = 0
        
        for tache_nom, tache in self.taches.items():
            affectation[tache_nom] = {}
            for ressource_nom, quantite_requise in tache.ressources_requises.items():
                if ressource_nom in self.ressources:
                    ressource = self.ressources[ressource_nom]
                    # Affecter exactement ce dont on a besoin
                    quantite_affectee = min(quantite_requise, ressource.disponibilite)
                    affectation[tache_nom][ressource_nom] = quantite_affectee
                    cout_total += quantite_affectee * ressource.cout_unitaire
        
        temps_total = sum(tache.duree_jours for tache in self.taches.values())
        
        return SolutionChiffrage(
            cout_total=cout_total,
            affectation_ressources=affectation,
            temps_total=temps_total,
            est_optimale=False,
            message="Solution de fallback (PuLP non disponible)"
        )
    
    def calculer_cout_par_tache(self) -> Dict[str, float]:
        """Calculer le coût par tâche."""
        if self.solution is None:
            self.resolvere()
        
        cout_par_tache = {}
        for tache_nom, ressources in self.solution.affectation_ressources.items():
            cout = sum(
                qte * self.ressources[r].cout_unitaire 
                for r, qte in ressources.items()
            )
            cout_par_tache[tache_nom] = round(cout, 2)
        
        return cout_par_tache
    
    def calculer_cout_par_ressource(self) -> Dict[str, float]:
        """Calculer le coût total par ressource."""
        if self.solution is None:
            self.resolvere()
        
        cout_par_ressource = {r: 0 for r in self.ressources.keys()}
        for tache_nom, ressources in self.solution.affectation_ressources.items():
            for ressource_nom, quantite in ressources.items():
                if ressource_nom in cout_par_ressource:
                    cout_par_ressource[ressource_nom] += quantite * self.ressources[ressource_nom].cout_unitaire
        
        for r in cout_par_ressource:
            cout_par_ressource[r] = round(cout_par_ressource[r], 2)
        
        return cout_par_ressource


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def optimiser_chiffrage_chantier(
    ressources: List[Dict[str, Any]],
    taches: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Fonction utilitaire pour optimiser le chiffrage d'un chantier.
    
    Args:
        ressources: Liste de ressources avec nom, cout_unitaire, disponibilite
        taches: Liste de tâches avec nom, quantite_requise, ressources_requises
    
    Returns:
        Dictionnaire avec la solution d'optimisation
    """
    solver = ChiffragePulpSolver()
    
    for ressource in ressources:
        solver.ajouter_ressource(
            nom=ressource["nom"],
            cout_unitaire=ressource["cout_unitaire"],
            disponibilite=ressource["disponibilite"],
            capacite=ressource.get("capacite", 1.0)
        )
    
    for tache in taches:
        solver.ajouter_tache(
            nom=tache["nom"],
            quantite_requise=tache["quantite_requise"],
            ressources_requises=tache["ressources_requises"],
            duree_jours=tache.get("duree_jours", 1),
            priorite=tache.get("priorite", 1)
        )
    
    solution = solver.resolvere()
    return solution.to_dict()

