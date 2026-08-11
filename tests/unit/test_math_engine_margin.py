"""
SMART_AO V7 - Tests unitaires pour margin.py
============================================
Tests complets pour MarginCalculator, CoefficientCalculator
"""

import pytest
from app.engines.math_engine.margin import (
    MarginType, CoefficientType,
    CoefficientResult, MarginResult, MarginAnalysis,
    CoefficientCalculator, MarginCalculator
)


# =============================================================================
# TESTS POUR ENUMS
# =============================================================================

class TestMarginType:
    def test_enum_values(self):
        assert MarginType.BRUTE == "brute"
        assert MarginType.NETTE == "nette"
        assert MarginType.COMMERCIALE == "commerciale"
        assert MarginType.CIBLE == "cible"


class TestCoefficientType:
    def test_enum_values(self):
        assert CoefficientType.VENTE == "coeff_vente"
        assert CoefficientType.PRODUCTION == "coeff_production"
        assert CoefficientType.SOUS_TRAITANCE == "coeff_sous_traitance"
        assert CoefficientType.RISQUE == "coeff_risque"


# =============================================================================
# TESTS POUR DATA CLASSES
# =============================================================================

class TestCoefficientResult:
    def test_creation(self):
        result = CoefficientResult(
            type=CoefficientType.VENTE,
            valeur=1.20,
            description="Coefficient de vente",
            reference="COEFF_VENTE",
            details={"min": 1.05, "max": 1.50}
        )
        assert result.type == CoefficientType.VENTE
        assert result.valeur == 1.20
        assert result.description == "Coefficient de vente"
        assert result.reference == "COEFF_VENTE"
        assert result.details == {"min": 1.05, "max": 1.50}

    def test_default_values(self):
        result = CoefficientResult(
            type=CoefficientType.VENTE,
            valeur=1.20,
            description="Test"
        )
        assert result.reference == ""
        assert result.details is None


class TestMarginResult:
    def test_creation(self):
        result = MarginResult(
            type=MarginType.BRUTE,
            montant=50000.0,
            pourcentage=25.0,
            base_calcul=200000.0,
            details={"formule": "CA - Coût"}
        )
        assert result.type == MarginType.BRUTE
        assert result.montant == 50000.0
        assert result.pourcentage == 25.0
        assert result.base_calcul == 200000.0
        assert result.details == {"formule": "CA - Coût"}

    def test_default_details(self):
        result = MarginResult(
            type=MarginType.BRUTE,
            montant=50000.0,
            pourcentage=25.0,
            base_calcul=200000.0
        )
        assert result.details is None


class TestMarginAnalysis:
    def test_creation(self):
        marge_brute = MarginResult(
            type=MarginType.BRUTE,
            montant=50000.0,
            pourcentage=25.0,
            base_calcul=200000.0
        )
        marge_nette = MarginResult(
            type=MarginType.NETTE,
            montant=30000.0,
            pourcentage=15.0,
            base_calcul=200000.0
        )
        marge_commerciale = MarginResult(
            type=MarginType.COMMERCIALE,
            montant=40000.0,
            pourcentage=20.0,
            base_calcul=200000.0
        )
        coefficients = {
            "coeff_vente": CoefficientResult(
                type=CoefficientType.VENTE,
                valeur=1.20,
                description="Vente"
            )
        }
        
        analysis = MarginAnalysis(
            marge_brute=marge_brute,
            marge_nette=marge_nette,
            marge_commerciale=marge_commerciale,
            coefficients=coefficients,
            marge_cible=None,
            ecart_vs_cible=0.0,
            niveau_risque="FAIBLE"
        )
        assert analysis.marge_brute == marge_brute
        assert analysis.marge_nette == marge_nette
        assert analysis.marge_commerciale == marge_commerciale
        assert analysis.coefficients == coefficients
        assert analysis.marge_cible is None
        assert analysis.ecart_vs_cible == 0.0
        assert analysis.niveau_risque == "FAIBLE"


# =============================================================================
# TESTS POUR CoefficientCalculator
# =============================================================================

class TestCoefficientCalculator:
    def test_default_coefficients_exist(self):
        """Test que les coefficients par défaut existent"""
        calc = CoefficientCalculator()
        assert CoefficientType.VENTE in calc.DEFAULT_COEFFICIENTS
        assert CoefficientType.PRODUCTION in calc.DEFAULT_COEFFICIENTS
        assert CoefficientType.SOUS_TRAITANCE in calc.DEFAULT_COEFFICIENTS
        assert CoefficientType.RISQUE in calc.DEFAULT_COEFFICIENTS

    def test_calculer_coefficient_vente_default(self):
        """Test calcul coefficient de vente par défaut"""
        calc = CoefficientCalculator()
        result = calc.calculer(CoefficientType.VENTE)
        
        assert result.type == CoefficientType.VENTE
        assert result.valeur == 1.20
        assert "vente" in result.description.lower()
        assert result.details["custom"] is False

    def test_calculer_coefficient_production_default(self):
        """Test calcul coefficient de production par défaut"""
        calc = CoefficientCalculator()
        result = calc.calculer(CoefficientType.PRODUCTION)
        
        assert result.type == CoefficientType.PRODUCTION
        assert result.valeur == 0.90

    def test_calculer_coefficient_custom_value(self):
        """Test calcul coefficient avec valeur personnalisée"""
        calc = CoefficientCalculator()
        result = calc.calculer(CoefficientType.VENTE, custom_value=1.50)
        
        assert result.valeur == 1.50
        assert result.details["custom"] is True

    def test_calculer_tous(self):
        """Test calcul de tous les coefficients"""
        calc = CoefficientCalculator()
        results = calc.calculer_tous()
        
        assert len(results) == 4
        assert CoefficientType.VENTE.value in results
        assert CoefficientType.PRODUCTION.value in results
        assert CoefficientType.SOUS_TRAITANCE.value in results
        assert CoefficientType.RISQUE.value in results


# =============================================================================
# TESTS POUR MarginCalculator
# =============================================================================

class TestMarginCalculatorCalculerMargeBrute:
    def test_marge_brute_simple(self):
        """Test calcul marge brute simple"""
        result = MarginCalculator.calculer_marge_brute(
            chiffre_affaires=200000.0,
            cout_revient=150000.0
        )
        assert result.type == MarginType.BRUTE
        assert result.montant == 50000.0
        assert result.pourcentage == 25.0
        assert result.base_calcul == 200000.0

    def test_marge_brute_zero(self):
        """Test calcul marge brute avec CA = coût"""
        result = MarginCalculator.calculer_marge_brute(
            chiffre_affaires=100000.0,
            cout_revient=100000.0
        )
        assert result.montant == 0.0
        assert result.pourcentage == 0.0

    def test_marge_brute_negative(self):
        """Test calcul marge brute négative"""
        result = MarginCalculator.calculer_marge_brute(
            chiffre_affaires=100000.0,
            cout_revient=150000.0
        )
        assert result.montant == -50000.0
        assert result.pourcentage == -50.0

    def test_marge_brute_zero_ca(self):
        """Test calcul marge brute avec CA = 0"""
        result = MarginCalculator.calculer_marge_brute(
            chiffre_affaires=0.0,
            cout_revient=100000.0
        )
        assert result.montant == -100000.0
        assert result.pourcentage == 0.0


class TestMarginCalculatorCalculerMargeNette:
    def test_marge_nette_simple(self):
        """Test calcul marge nette simple"""
        result = MarginCalculator.calculer_marge_nette(
            marge_brute=50000.0,
            charges=10000.0
        )
        assert result.type == MarginType.NETTE
        assert result.montant == 40000.0
        # base = 50000 + 10000 = 60000, pourcentage = 40000/60000 * 100 = 66.67%
        assert result.pourcentage == pytest.approx(66.67, abs=0.01)
        assert result.base_calcul == 60000.0

    def test_marge_nette_zero_charges(self):
        """Test calcul marge nette sans charges"""
        result = MarginCalculator.calculer_marge_nette(
            marge_brute=50000.0,
            charges=0.0
        )
        assert result.montant == 50000.0
        assert result.pourcentage == 100.0

    def test_marge_nette_negative(self):
        """Test calcul marge nette négative"""
        result = MarginCalculator.calculer_marge_nette(
            marge_brute=10000.0,
            charges=20000.0
        )
        assert result.montant == -10000.0


class TestMarginCalculatorCalculerMargeCommerciale:
    def test_marge_commerciale_default_coeff(self):
        """Test calcul marge commerciale avec coefficient par défaut"""
        result = MarginCalculator.calculer_marge_commerciale(
            chiffre_affaires=100000.0
        )
        assert result.type == MarginType.COMMERCIALE
        assert result.montant == pytest.approx(20000.0, abs=0.01)
        assert result.pourcentage == pytest.approx(20.0, abs=0.01)
        assert result.base_calcul == 100000.0

    def test_marge_commerciale_custom_coeff(self):
        """Test calcul marge commerciale avec coefficient personnalisé"""
        result = MarginCalculator.calculer_marge_commerciale(
            chiffre_affaires=100000.0,
            coefficient_vente=1.30
        )
        assert result.montant == pytest.approx(30000.0, abs=0.01)
        assert result.pourcentage == pytest.approx(30.0, abs=0.01)

    def test_marge_commerciale_coeff_1(self):
        """Test calcul marge commerciale avec coefficient = 1"""
        result = MarginCalculator.calculer_marge_commerciale(
            chiffre_affaires=100000.0,
            coefficient_vente=1.0
        )
        assert result.montant == 0.0
        assert result.pourcentage == 0.0

    def test_marge_commerciale_coeff_0(self):
        """Test calcul marge commerciale avec coefficient = 0"""
        result = MarginCalculator.calculer_marge_commerciale(
            chiffre_affaires=100000.0,
            coefficient_vente=0.0
        )
        assert result.montant == -100000.0
        assert result.pourcentage == 0.0
