"""
SMART_AO V7 - test_math_engine_chiffrage_pulp.py
==================================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 07/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - Test Chiffrage PULP / OR-Tools Solver
Vérifie que le solveur d'optimisation de ressources fonctionne avec
OR-Tools (prioritaire) ou PuLP (fallback).
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from app.engines.math_engine.chiffrage_pulp import ChiffragePulpSolver


def test_optimisation_chantier():
    solver = ChiffragePulpSolver()
    solver.ajouter_ressource("main_oeuvre", cout_unitaire=35.0, disponibilite=200.0)
    solver.ajouter_ressource("materiaux", cout_unitaire=80.0, disponibilite=150.0)
    solver.ajouter_tache(
        "fondations",
        quantite_requise=1.0,
        ressources_requises={"main_oeuvre": 100.0, "materiaux": 80.0},
        duree_jours=10,
    )
    solver.ajouter_tache(
        "elevation",
        quantite_requise=1.0,
        ressources_requises={"main_oeuvre": 80.0, "materiaux": 60.0},
        duree_jours=15,
    )

    solution = solver.resolvere()
    assert solution.est_optimale is True
    assert solution.cout_total > 0
    assert "fondations" in solution.affectation_ressources
    assert "elevation" in solution.affectation_ressources
    print(f"✅ Solution optimale trouvée: {solution.cout_total:.2f} €")


def test_aucune_tache():
    solver = ChiffragePulpSolver()
    solution = solver.resolvere()
    assert solution.cout_total == 0
    assert solution.est_optimale is True
    print("✅ Pas de tâche = solution vide")


if __name__ == "__main__":
    test_optimisation_chantier()
    test_aucune_tache()
    print("✅ TESTS PASSED: Chiffrage PULP / OR-Tools")
