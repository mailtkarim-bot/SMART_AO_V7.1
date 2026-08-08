"""
SMART_AO V7 - test_penalites_cumul_5pct.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Test Pénalités Cumulées (Gate Bloquant Build 4)

Vérifie les règles CCAG réformées en 2024:
- Pénalité = 1/1000 du montant HT par jour de retard.
- Plafond à 5% du montant HT pour les marchés post-2024.
- Seuil d'application : 1 000 €.
"""
import sys
from pathlib import Path
from decimal import Decimal
from datetime import date

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from app.engines.math_engine.penalites_cumul import CCAGCalculator
from app.engines.math_engine.solvers.penalites_cumul import PenalitesCumulSolver
from app.engines.math_engine.types import Amount


def test_penalites_cumul_basic():
    solver = PenalitesCumulSolver()
    result = solver.solve({
        'montant_marche': 1_000_000,
        'retards': [30],
        'currency': 'EUR',
        'date_contrat': '2024-06-01',
    })
    assert result.solver_name == "PenalitesCumulSolver"
    assert result.output.currency == "EUR"
    # 1_000_000 * 30/1000 = 30_000 EUR, plafonné à 5% = 50_000 EUR -> 30_000 EUR
    assert result.output.value == Decimal('30000')
    print(f"✅ Test passé: {result.output.value} EUR")


def test_plafond_5pct_2024():
    calculator = CCAGCalculator()
    result = calculator.calculer(1_000_000, 100, date(2024, 6, 1))
    # 1_000_000 * 100/1000 = 100_000 -> plafond 5% = 50_000
    assert result.montant == 50_000.0
    assert result.details["plafond_pourcentage"] == 0.05
    print(f"✅ Plafond 5% post-2024 respecté: {result.montant} EUR")


def test_plafond_10pct_avant_2024():
    calculator = CCAGCalculator()
    result = calculator.calculer(1_000_000, 100, date(2023, 1, 1))
    # 1_000_000 * 100/1000 = 100_000 -> plafond 10% = 100_000
    assert result.montant == 100_000.0
    assert result.details["plafond_pourcentage"] == 0.10
    print(f"✅ Plafond 10% pré-2024 respecté: {result.montant} EUR")


def test_seuil_1000e():
    calculator = CCAGCalculator()
    # 999_999 * 1/1000 = 999.999 < 1000 -> aucune pénalité
    result = calculator.calculer(999_999, 1, date(2024, 6, 1))
    assert result.montant == 0.0
    assert result.details["seuil_minimal"] == 1000.0
    print(f"✅ Seuil 1000€ respecté: pénalité = {result.montant} EUR")


def test_seuil_1000e_depasse():
    calculator = CCAGCalculator()
    # 1_000_000 * 1/1000 = 1_000 -> pénalité = 1_000
    result = calculator.calculer(1_000_000, 1, date(2024, 6, 1))
    assert result.montant == 1000.0
    print(f"✅ Seuil 1000€ dépassé: pénalité = {result.montant} EUR")


if __name__ == "__main__":
    test_penalites_cumul_basic()
    test_plafond_5pct_2024()
    test_plafond_10pct_avant_2024()
    test_seuil_1000e()
    test_seuil_1000e_depasse()
    print("✅ TESTS PASSED: Pénalités Cumulées")
