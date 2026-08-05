"""
SMART_AO V7 - Test PAB Detector (Gate Bloquant Build 4)
"""
import sys
from pathlib import Path
from decimal import Decimal
from datetime import date

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from app.engines.math_engine.solvers.pab_detector import PABDetector
from app.engines.math_engine.types import Amount, PenaltyType

def test_pab_20pct():
    detector = PABDetector()
    result = detector.solve({'montant_marche_ht': 1000000, 'date_previsionnelle': '2024-01-01', 'date_reelle': '2024-01-15', 'currency': 'EUR'})
    assert result.output.value == Decimal('200000')
    assert result.penalties[0].penalty_type == PenaltyType.PAB_20PCT
    print(f"✅ PAB 20%: {result.output.value} EUR")

def test_pab_30pct():
    detector = PABDetector()
    result = detector.solve({'montant_marche_ht': 1000000, 'date_previsionnelle': '2024-01-01', 'date_reelle': '2024-02-01', 'currency': 'EUR'})
    assert result.output.value == Decimal('300000')
    assert result.penalties[0].penalty_type == PenaltyType.PAB_30PCT
    print(f"✅ PAB 30%: {result.output.value} EUR")

if __name__ == "__main__":
    test_pab_20pct()
    test_pab_30pct()
    print("✅ TESTS PASSED: PAB Detector")
