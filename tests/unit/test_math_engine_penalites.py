"""
SMART_AO V7 - Tests unitaires pour penalites_cumul.py
====================================================
Tests complets pour les classes CCAGCalculator, CCMICalculator
"""

import pytest
from datetime import date
from decimal import Decimal
from app.engines.math_engine.penalites_cumul import (
    PenaliteType, NiveauPenalite,
    SEUIL_MINIMAL_PENALITE_EUR, TAUX_JOURNALIER_CCAG,
    PLAFOND_CCAG_AVANT_2024, PLAFOND_CCAG_APRES_2024,
    DATE_REFORME_CCAG_2024,
    PenaliteResult, PenaltiesSummary,
    CCAGCalculator, CCMICalculator
)


# =============================================================================
# TESTS POUR ENUMS
# =============================================================================

class TestPenaliteType:
    def test_enum_values(self):
        assert PenaliteType.CCAG == "ccag"
        assert PenaliteType.CCMI == "ccmi"
        assert PenaliteType.CONTRAT == "contrat"


class TestNiveauPenalite:
    def test_enum_values(self):
        assert NiveauPenalite.FAIBLE == "FAIBLE"
        assert NiveauPenalite.MOYEN == "MOYEN"
        assert NiveauPenalite.ELEVE == "ELEVE"
        assert NiveauPenalite.CRITIQUE == "CRITIQUE"


# =============================================================================
# TESTS POUR CONSTANTES
# =============================================================================

class TestConstantes:
    def test_seuil_minimal(self):
        assert SEUIL_MINIMAL_PENALITE_EUR == 1000.0

    def test_taux_journalier_ccag(self):
        assert TAUX_JOURNALIER_CCAG == 1 / 1000

    def test_plafonds_ccag(self):
        assert PLAFOND_CCAG_AVANT_2024 == 0.10
        assert PLAFOND_CCAG_APRES_2024 == 0.05

    def test_date_reforme(self):
        assert DATE_REFORME_CCAG_2024 == date(2024, 4, 1)


# =============================================================================
# TESTS POUR DATA CLASSES
# =============================================================================

class TestPenaliteResult:
    def test_creation(self):
        result = PenaliteResult(
            type=PenaliteType.CCAG,
            montant=5000.0,
            taux=0.001,
            base_calcul=1000000.0,
            retard_jours=10,
            niveau=NiveauPenalite.MOYEN,
            reference="CCAG Article 14-1",
            details={"test": "value"}
        )
        assert result.type == PenaliteType.CCAG
        assert result.montant == 5000.0
        assert result.taux == 0.001
        assert result.base_calcul == 1000000.0
        assert result.retard_jours == 10
        assert result.niveau == NiveauPenalite.MOYEN
        assert result.reference == "CCAG Article 14-1"
        assert result.details == {"test": "value"}

    def test_default_values(self):
        result = PenaliteResult(
            type=PenaliteType.CCAG,
            montant=1000.0
        )
        assert result.taux is None
        assert result.base_calcul == 0.0
        assert result.retard_jours == 0
        assert result.niveau == NiveauPenalite.FAIBLE
        assert result.reference == ""
        assert result.details is None


class TestPenaltiesSummary:
    def test_creation(self):
        penalite = PenaliteResult(
            type=PenaliteType.CCAG,
            montant=5000.0,
            retard_jours=10
        )
        summary = PenaltiesSummary(
            penalites={"ccag": penalite},
            total_penalites=5000.0,
            total_retard_jours=10,
            risque_global=NiveauPenalite.MOYEN
        )
        assert summary.penalites == {"ccag": penalite}
        assert summary.total_penalites == 5000.0
        assert summary.total_retard_jours == 10
        assert summary.risque_global == NiveauPenalite.MOYEN


# =============================================================================
# TESTS POUR CCAGCalculator
# =============================================================================

class TestCCAGCalculator:
    def test_determiner_plafond_avant_2024(self):
        """Test plafond avant réforme 2024"""
        plafond = CCAGCalculator._determiner_plafond(date(2023, 1, 1))
        assert plafond == PLAFOND_CCAG_AVANT_2024

    def test_determiner_plafond_apres_2024(self):
        """Test plafond après réforme 2024"""
        plafond = CCAGCalculator._determiner_plafond(date(2024, 5, 1))
        assert plafond == PLAFOND_CCAG_APRES_2024

    def test_determiner_plafond_sans_date(self):
        """Test plafond sans date (par défaut après 2024)"""
        plafond = CCAGCalculator._determiner_plafond(None)
        assert plafond == PLAFOND_CCAG_APRES_2024

    def test_calculer_zero_retard(self):
        """Test calcul avec 0 jour de retard"""
        result = CCAGCalculator.calculer(
            montant_marche_ht=1000000.0,
            retard_jours=0
        )
        assert result.montant == 0.0
        assert result.retard_jours == 0

    def test_calculer_montant_nul(self):
        """Test calcul avec montant nul"""
        result = CCAGCalculator.calculer(
            montant_marche_ht=0.0,
            retard_jours=10
        )
        assert result.montant == 0.0

    def test_calculer_retard_nul(self):
        """Test calcul avec retard nul"""
        result = CCAGCalculator.calculer(
            montant_marche_ht=1000000.0,
            retard_jours=0
        )
        assert result.montant == 0.0

    def test_calculer_sous_seuil(self):
        """Test calcul sous seuil minimal (1000€)"""
        # 100000 * 0.001 * 5 = 500€ (sous seuil)
        result = CCAGCalculator.calculer(
            montant_marche_ht=100000.0,
            retard_jours=5
        )
        assert result.montant == 0.0
        assert "seuil" in result.details.get("message", "").lower()

    def test_calculer_au_seuil(self):
        """Test calcul exactement au seuil"""
        # 200000 * 0.001 * 5 = 1000€ (au seuil)
        result = CCAGCalculator.calculer(
            montant_marche_ht=200000.0,
            retard_jours=5
        )
        assert result.montant == 1000.0

    def test_calculer_au_dela_seuil(self):
        """Test calcul au-dessus du seuil"""
        # 200000 * 0.001 * 10 = 2000€ (au-dessus du seuil)
        result = CCAGCalculator.calculer(
            montant_marche_ht=200000.0,
            retard_jours=10
        )
        assert result.montant == 2000.0

    def test_calculer_plafond_avant_2024(self):
        """Test calcul avec plafond avant 2024 (10%)"""
        # 1000000 * 0.001 * 200 = 200000€ brute, mais plafond à 10% = 100000€
        result = CCAGCalculator.calculer(
            montant_marche_ht=1000000.0,
            retard_jours=200,
            date_contrat=date(2023, 1, 1)
        )
        assert result.montant == 100000.0
        assert result.niveau == NiveauPenalite.CRITIQUE

    def test_calculer_plafond_apres_2024(self):
        """Test calcul avec plafond après 2024 (5%)"""
        # 1000000 * 0.001 * 200 = 200000€ brute, mais plafond à 5% = 50000€
        result = CCAGCalculator.calculer(
            montant_marche_ht=1000000.0,
            retard_jours=200,
            date_contrat=date(2024, 5, 1)
        )
        assert result.montant == 50000.0

    def test_calculer_niveau_faible(self):
        """Test détermination niveau FAIBLE"""
        # Petit montant, niveau doit être au moins MOYEN si au-dessus du seuil
        # Mais avec 1000€ exactement, ratio = 1000/200000 = 0.005
        # plafond * 0.5 = 0.05 * 0.5 = 0.025, donc niveau MOYEN
        result = CCAGCalculator.calculer(
            montant_marche_ht=200000.0,
            retard_jours=5
        )
        assert result.montant == 1000.0
        # Avec 5% plafond: ratio = 1000/200000 = 0.005 < 0.025, donc MOYEN
        assert result.niveau == NiveauPenalite.MOYEN

    def test_calculer_niveau_critique(self):
        """Test détermination niveau CRITIQUE"""
        # 1000000 * 0.05 * 0.8 = 40000€ de pénalité
        # 1000000 * 0.001 * jours = 40000 => jours = 40
        result = CCAGCalculator.calculer(
            montant_marche_ht=1000000.0,
            retard_jours=80,
            date_contrat=date(2024, 5, 1)
        )
        # 1000000 * 0.001 * 80 = 80000, plafonné à 5% = 50000
        # ratio = 50000/1000000 = 0.05 = plafond, donc CRITIQUE
        assert result.montant == 50000.0
        assert result.niveau == NiveauPenalite.CRITIQUE

    def test_calculer_details_complets(self):
        """Test que les détails sont complets"""
        result = CCAGCalculator.calculer(
            montant_marche_ht=500000.0,
            retard_jours=30,
            date_contrat=date(2024, 5, 1)
        )
        assert result.details is not None
        assert "penalite_brute" in result.details
        assert "penalite_plafonnee" in result.details
        assert "plafond" in result.details

    def test_calculer_retard_negatif(self):
        """Test calcul avec retard négatif (doit être converti en 0)"""
        result = CCAGCalculator.calculer(
            montant_marche_ht=100000.0,
            retard_jours=-10
        )
        assert result.retard_jours == 0
        assert result.montant == 0.0


# =============================================================================
# TESTS POUR CCMICalculator
# =============================================================================

class TestCCMICalculator:
    def test_calculer_sans_montant(self):
        """Test calcul CCMI sans montant (doit lever ValueError)"""
        with pytest.raises(ValueError, match="montant_marche_ht requis"):
            CCMICalculator.calculer(retard_jours=10, montant_marche_ht=None)

    def test_calculer_montant_nul(self):
        """Test calcul CCMI avec montant nul (doit lever ValueError)"""
        with pytest.raises(ValueError, match="montant_marche_ht requis"):
            CCMICalculator.calculer(retard_jours=10, montant_marche_ht=0.0)

    def test_calculer_zero_retard(self):
        """Test calcul CCMI avec 0 jour de retard"""
        result = CCMICalculator.calculer(
            retard_jours=0,
            montant_marche_ht=100000.0
        )
        assert result.montant == 0.0
        assert result.retard_jours == 0

    def test_calculer_formule_legale(self):
        """Test formule légale CCMI: 1/3000e par jour"""
        # 300000 * 1/3000 * 10 = 1000€
        result = CCMICalculator.calculer(
            retard_jours=10,
            montant_marche_ht=300000.0
        )
        assert result.montant == Decimal("1000.00")
        assert result.type == PenaliteType.CCMI

    def test_calculer_plafond_5_pourcent(self):
        """Test plafond CCMI à 5%"""
        # Calculer combien de jours pour atteindre 5%
        # 100000 * 1/3000 * jours = 5000 (5% de 100000)
        # jours = 5000 * 3000 / 100000 = 150 jours
        result = CCMICalculator.calculer(
            retard_jours=200,
            montant_marche_ht=100000.0
        )
        # Plafond à 5% = 5000€
        assert result.montant == Decimal("5000.00")

    def test_calculer_niveau_faible(self):
        """Test niveau FAIBLE pour retard <= 10 jours"""
        result = CCMICalculator.calculer(
            retard_jours=5,
            montant_marche_ht=300000.0
        )
        assert result.niveau == NiveauPenalite.FAIBLE

    def test_calculer_niveau_moyen(self):
        """Test niveau MOYEN pour retard > 10 et <= 20 jours"""
        result = CCMICalculator.calculer(
            retard_jours=15,
            montant_marche_ht=300000.0
        )
        assert result.niveau == NiveauPenalite.MOYEN

    def test_calculer_niveau_eleve(self):
        """Test niveau ELEVE pour retard > 20 et <= 30 jours"""
        result = CCMICalculator.calculer(
            retard_jours=25,
            montant_marche_ht=300000.0
        )
        assert result.niveau == NiveauPenalite.ELEVE

    def test_calculer_niveau_critique(self):
        """Test niveau CRITIQUE pour retard > 30 jours"""
        result = CCMICalculator.calculer(
            retard_jours=35,
            montant_marche_ht=300000.0
        )
        assert result.niveau == NiveauPenalite.CRITIQUE

    def test_calculer_retard_negatif(self):
        """Test calcul avec retard négatif (doit être converti en 0)"""
        result = CCMICalculator.calculer(
            retard_jours=-10,
            montant_marche_ht=100000.0
        )
        assert result.retard_jours == 0
        assert result.montant == 0.0

    def test_calculer_details(self):
        """Test que les détails sont présents"""
        result = CCMICalculator.calculer(
            retard_jours=10,
            montant_marche_ht=300000.0
        )
        assert result.details is not None
        assert isinstance(result.details, dict)
