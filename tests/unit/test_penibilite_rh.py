"""
SMART_AO V7.1 - test_penibilite_rh.py
=====================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 07/08/2026
Build: 9.5 - Phase: 5
"""

"""
SMART_AO V7.1 - Test Pénibilité RH (Module 7.29)
Source: RAPPORT (1).md §7.29
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from app.engines.math_engine.penibilite_solver import PenibiliteSolver


def test_penibilite_coffreur_idf():
    solver = PenibiliteSolver()
    result = solver.calculer(
        nb_manquants=3,
        metier="coffreur",
        duree_semaines=12,
        heures_par_semaine=35,
        region="IDF",
        contrainte="penibilite_standard",
    )
    assert result.surcout_estime > 0
    # 3 x 24.50 x 1.35 x 35 x 12 ≈ 41 869.5 €
    assert 40000 <= float(result.surcout_estime) <= 43000
    print(f"✅ Surcoût intérim 3 coffreurs IDF: {result.surcout_estime} €")


def test_penibilite_manoeuvre_default():
    solver = PenibiliteSolver()
    result = solver.calculer(
        nb_manquants=2,
        metier="manoeuvre",
        duree_semaines=8,
        heures_par_semaine=35,
    )
    assert result.surcout_estime > 0
    print(f"✅ Surcoût intérim 2 manœuvres: {result.surcout_estime} €")


def test_penibilite_zero_manquant():
    solver = PenibiliteSolver()
    result = solver.calculer(nb_manquants=0, metier="coffreur", duree_semaines=12)
    assert float(result.surcout_estime) == 0.0
    print("✅ Aucun manquant = 0 €")


if __name__ == "__main__":
    test_penibilite_coffreur_idf()
    test_penibilite_manoeuvre_default()
    test_penibilite_zero_manquant()
    print("✅ TESTS PASSED: Pénibilité RH")
