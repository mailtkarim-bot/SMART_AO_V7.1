"""
SMART_AO V7.1 - test_zan_trackterres.py
========================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 07/08/2026
Build: 9.5 - Phase: 5
"""

"""
SMART_AO V7.1 - Test ZAN & Trackterres (Module 7.31)
Source: RAPPORT (1).md §7.31
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from app.engines.math_engine.zan_solver import ZANSolver


def test_zan_lyon_proche():
    solver = ZANSolver()
    # Coordonnées proches de l'ISDI Lyon Saint-Priest
    result = solver.calculer(
        volume=1200,
        lat=45.70,
        lon=4.95,
        type_terre="terre",
    )
    assert result.trackterres_obligatoire is True
    assert float(result.cout_total) > 0
    # Doit être proche de 28 000 € (distance faible)
    assert 25000 <= float(result.cout_total) <= 30000
    print(f"✅ ZAN Lyon 1200m3: {result.cout_total} € (ISDI {result.isdi_id})")


def test_zan_distance_fixe():
    solver = ZANSolver()
    result = solver.calculer(volume=500, distance_km=45, type_terre="terre")
    assert float(result.distance_km) == 45.0
    assert float(result.cout_total) > 0
    print(f"✅ ZAN distance fixe 45km: {result.cout_total} €")


def test_zan_volume_zero():
    solver = ZANSolver()
    result = solver.calculer(volume=0, distance_km=10)
    assert float(result.cout_total) == 0.0
    print("✅ ZAN volume 0 = 0 €")


if __name__ == "__main__":
    test_zan_lyon_proche()
    test_zan_distance_fixe()
    test_zan_volume_zero()
    print("✅ TESTS PASSED: ZAN & Trackterres")
