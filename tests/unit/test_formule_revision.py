"""
SMART_AO V7.1 - test_formule_revision.py
========================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 07/08/2026
Build: 9.5 - Phase: 5
"""

"""
SMART_AO V7.1 - Test Syntax Checker Formules Révision (Module 7.32)
Source: RAPPORT (1).md §7.32
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from app.engines.math_engine.formule_algebra_checker import FormuleAlgebraChecker


def test_formule_somme_incorrecte():
    checker = FormuleAlgebraChecker()
    result = checker.verifier(
        coefficients=[0.5, 0.3, 0.28],
        formule="P = 0.50 BT01 + 0.30 BT03 + 0.28 TP01",
        date_base="2024-01-01",
    )
    assert result.erreur is True
    assert float(result.somme_coefficients) == 1.08
    assert result.indice_inexistant is None
    print(f"✅ Somme coeffs = {result.somme_coefficients}: erreur détectée")


def test_formule_somme_correcte():
    checker = FormuleAlgebraChecker()
    result = checker.verifier(
        coefficients=[0.6, 0.25, 0.15],
        formule="P = 0.60 BT01 + 0.25 BT03 + 0.15 FM0B",
        date_base="2024-01-01",
    )
    assert result.erreur is False
    assert float(result.somme_coefficients) == 1.0
    print(f"✅ Somme coeffs = {result.somme_coefficients}: OK")


def test_formule_indice_invalide():
    checker = FormuleAlgebraChecker()
    result = checker.verifier(
        coefficients=[0.5, 0.5],
        formule="P = 0.50 BT01 + 0.50 BT99",
        date_base="2024-01-01",
    )
    assert result.erreur is True
    assert result.indice_inexistant == "BT99"
    print(f"✅ Indice invalide détecté: {result.indice_inexistant}")


def test_formule_date_base_invalide():
    checker = FormuleAlgebraChecker()
    result = checker.verifier(
        coefficients=[0.5, 0.5],
        formule="P = 0.50 BT01 + 0.50 BT03",
        date_base="2019-01-01",
    )
    assert result.erreur is True
    assert result.date_base_valide is False
    print("✅ Date de base invalide détectée")


if __name__ == "__main__":
    test_formule_somme_incorrecte()
    test_formule_somme_correcte()
    test_formule_indice_invalide()
    test_formule_date_base_invalide()
    print("✅ TESTS PASSED: Syntax Checker Formules Révision")
