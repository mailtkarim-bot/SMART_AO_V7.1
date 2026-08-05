"""
SMART_AO V7 - Test Matériaux Shield (Gate Bloquant Build 4)
"""
import sys
from pathlib import Path
from decimal import Decimal

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from app.engines.math_engine.solvers.materiaux_shield import MateriauxShieldSolver
from app.engines.math_engine.types import Amount

def test_no_variation():
    solver = MateriauxShieldSolver()
    result = solver.solve({'cout_previsionnel': 100000, 'cout_reel': 100000, 'seuil_protection': 0.10, 'currency': 'EUR'})
    assert result.output.value == Decimal('0')
    print("✅ Pas de variation: 0 EUR")

def test_variation_above_seuil():
    solver = MateriauxShieldSolver()
    result = solver.solve({'cout_previsionnel': 100000, 'cout_reel': 115000, 'seuil_protection': 0.10, 'currency': 'EUR'})
    assert result.output.value == Decimal('5000')
    print(f"✅ Bouclier activé: {result.output.value} EUR")

if __name__ == "__main__":
    test_no_variation()
    test_variation_above_seuil()
    print("✅ TESTS PASSED: Matériaux Shield")
