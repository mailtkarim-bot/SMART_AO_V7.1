"""
SMART_AO V7 - Test Pénalités Cumulées (Gate Bloquant Build 4)
"""
import sys
from pathlib import Path
from decimal import Decimal

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from app.engines.math_engine.solvers.penalites_cumul import PenalitesCumulSolver
from app.engines.math_engine.types import Amount

def test_penalites_cumul_basic():
    solver = PenalitesCumulSolver()
    result = solver.solve({'montant_marche': 1000000, 'retards': [10, 5], 'taux': [0.10, 0.05], 'currency': 'EUR'})
    assert result.solver_name == "PenalitesCumulSolver"
    assert result.output.currency == "EUR"
    assert result.output.value >= Decimal('0')
    print(f"✅ Test passé: {result.output.value} EUR")

def test_seuil_1000e():
    solver = PenalitesCumulSolver()
    result = solver.solve({'montant_marche': 1000000, 'retards': [100], 'taux': [0.10], 'currency': 'EUR'})
    assert result.output.value > Decimal('1000')
    print(f"✅ Seuil 1000€ dépassé: {result.output.value} EUR")

if __name__ == "__main__":
    test_penalites_cumul_basic()
    test_seuil_1000e()
    print("✅ TESTS PASSED: Pénalités Cumulées")
