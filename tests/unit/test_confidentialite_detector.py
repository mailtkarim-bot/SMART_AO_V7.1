"""
SMART_AO V7.1 - test_confidentialite_detector.py
==================================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 07/08/2026
Build: 9.5 - Phase: 5
"""

"""
SMART_AO V7.1 - Test Confidentialité Detector (ADR-060)
Source: ARCHITECTURE_V7_ENGINE.md ADR-060
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from app.engines.knowledge_engine.confidentialite_detector import ConfidentialiteDetector


def test_detect_confidential():
    detector = ConfidentialiteDetector()
    result = detector.detect("DCE CONFIDENTIEL DÉFENSE — site Seveso")
    assert result["confidential"] is True
    assert result["risk_level"] == "HIGH"
    assert result["recommended_handler"] == "local_llm"
    print("✅ Détection confidentialité haute")


def test_detect_public():
    detector = ConfidentialiteDetector()
    result = detector.detect("Avis d'appel d'offres public — construction école")
    assert result["confidential"] is False
    assert result["risk_level"] == "NONE"
    print("✅ Document public détecté")


if __name__ == "__main__":
    test_detect_confidential()
    test_detect_public()
    print("✅ TESTS PASSED: Confidentialité Detector")
