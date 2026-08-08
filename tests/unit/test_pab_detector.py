"""
SMART_AO V7 - test_pab_detector.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Test PAB Detector (Gate Bloquant Build 4)

Le PAB (Prix Anormalement Bas) se calcule par comparaison du prix proposé
au prix moyen du marché, et non pas par rapport à des dates de retard.
Source: CCAG Article 53
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from app.engines.math_engine.pab_detector import PABDetector


def test_pab_conforme():
    detector = PABDetector()
    result = detector.detecter_pab(100000, 100000)
    assert result.est_pab is False
    assert result.niveau_risque == "FAIBLE"
    print(f"✅ Prix conforme: PAB={result.est_pab}, risque={result.niveau_risque}")


def test_pab_legere():
    detector = PABDetector()
    result = detector.detecter_pab(80000, 100000)
    assert result.est_pab is False
    assert result.niveau_risque == "MOYEN"
    print(f"✅ Prix -20%: PAB={result.est_pab}, risque={result.niveau_risque}")


def test_pab_detecte():
    detector = PABDetector()
    result = detector.detecter_pab(60000, 100000)
    assert result.est_pab is True
    assert result.niveau_risque == "ELEVE"
    print(f"✅ PAB -40%: PAB={result.est_pab}, risque={result.niveau_risque}")


def test_pab_critique():
    detector = PABDetector()
    result = detector.detecter_pab(40000, 100000)
    assert result.est_pab is True
    assert result.niveau_risque == "CRITIQUE"
    print(f"✅ PAB critique -60%: PAB={result.est_pab}, risque={result.niveau_risque}")


def test_pab_seuil_justification():
    detector = PABDetector()
    seuil = detector.calculer_seuil_justification(100000)
    assert seuil == 70000.0
    print(f"✅ Seuil justification 30%: {seuil} EUR")


if __name__ == "__main__":
    test_pab_conforme()
    test_pab_legere()
    test_pab_detecte()
    test_pab_critique()
    test_pab_seuil_justification()
    print("✅ TESTS PASSED: PAB Detector")
