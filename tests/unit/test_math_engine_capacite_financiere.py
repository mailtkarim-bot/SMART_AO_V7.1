"""
SMART_AO V7 - Tests unitaires pour capacite_financiere.py
========================================================
Tests complets pour RatioCalculator, CapaciteFinanciereCalculator
"""

import pytest
from app.engines.math_engine.capacite_financiere import (
    CapaciteStatus, RatioType,
    RatioResult, CapaciteFinanciereResult,
    RatioCalculator, CapaciteFinanciereCalculator
)


# =============================================================================
# TESTS POUR ENUMS
# =============================================================================

class TestCapaciteStatus:
    def test_enum_values(self):
        assert CapaciteStatus.SUFFISANTE == "suffisante"
        assert CapaciteStatus.LIMITE == "limite"
        assert CapaciteStatus.INSUFFISANTE == "insuffisante"
        assert CapaciteStatus.CRITIQUE == "critique"


class TestRatioType:
    def test_enum_values(self):
        assert RatioType.AUTONOMIE_FINANCIERE == "autonomie_financiere"
        assert RatioType.ENDETTEMENT == "endettement"
        assert RatioType.TRESORERIE == "tresorerie"
        assert RatioType.BFR == "bfr"
        assert RatioType.CAPACITE_REMBOURSEMENT == "capacite_remboursement"


# =============================================================================
# TESTS POUR DATA CLASSES
# =============================================================================

class TestRatioResult:
    def test_creation(self):
        result = RatioResult(
            type=RatioType.AUTONOMIE_FINANCIERE,
            valeur=0.50,
            seuil_min=0.30,
            seuil_max=1.00,
            unite="",
            statut=CapaciteStatus.SUFFISANTE,
            description="Ratio d'autonomie financière"
        )
        assert result.type == RatioType.AUTONOMIE_FINANCIERE
        assert result.valeur == 0.50
        assert result.seuil_min == 0.30
        assert result.seuil_max == 1.00
        assert result.statut == CapaciteStatus.SUFFISANTE

    def test_default_values(self):
        result = RatioResult(
            type=RatioType.AUTONOMIE_FINANCIERE,
            valeur=0.50,
            seuil_min=0.30,
            seuil_max=1.00
        )
        assert result.unite == ""
        assert result.statut == CapaciteStatus.SUFFISANTE
        assert result.description == ""


class TestCapaciteFinanciereResult:
    def test_creation(self):
        ratios = {
            "autonomie": RatioResult(
                type=RatioType.AUTONOMIE_FINANCIERE,
                valeur=0.50,
                seuil_min=0.30,
                seuil_max=1.00
            )
        }
        result = CapaciteFinanciereResult(
            score_global=75.0,
            statut=CapaciteStatus.SUFFISANTE,
            ratios=ratios,
            risques=["Risque faible"],
            recommandations=["Améliorer la trésorerie"],
            montant_max_marche=1000000.0
        )
        assert result.score_global == 75.0
        assert result.statut == CapaciteStatus.SUFFISANTE
        assert result.ratios == ratios
        assert result.risques == ["Risque faible"]
        assert result.recommandations == ["Améliorer la trésorerie"]
        assert result.montant_max_marche == 1000000.0


# =============================================================================
# TESTS POUR RatioCalculator
# =============================================================================

class TestRatioCalculator:
    def test_seuils_exist(self):
        """Test que les seuils sont définis"""
        assert RatioType.AUTONOMIE_FINANCIERE in RatioCalculator.SEUILS
        assert RatioType.ENDETTEMENT in RatioCalculator.SEUILS
        assert RatioType.TRESORERIE in RatioCalculator.SEUILS
        assert RatioType.BFR in RatioCalculator.SEUILS
        assert RatioType.CAPACITE_REMBOURSEMENT in RatioCalculator.SEUILS

    def test_calculer_autonomie_financiere_normale(self):
        """Test calcul autonomie financière normale"""
        result = RatioCalculator.calculer_autonomie_financiere(
            capitaux_propres=500000.0,
            total_bilan=1000000.0
        )
        assert result.type == RatioType.AUTONOMIE_FINANCIERE
        assert result.valeur == 0.50
        # 0.50 >= 0.50 (idéal), donc suffisant
        assert result.statut == CapaciteStatus.SUFFISANTE

    def test_calculer_autonomie_financiere_faible(self):
        """Test calcul autonomie financière faible"""
        result = RatioCalculator.calculer_autonomie_financiere(
            capitaux_propres=200000.0,
            total_bilan=1000000.0
        )
        assert result.valeur == 0.20
        # 0.20 < 0.30 (min), donc insuffisant
        assert result.statut == CapaciteStatus.INSUFFISANTE

    def test_calculer_autonomie_financiere_zero_bilan(self):
        """Test calcul autonomie financière avec bilan à 0"""
        result = RatioCalculator.calculer_autonomie_financiere(
            capitaux_propres=100000.0,
            total_bilan=0.0
        )
        assert result.valeur == 0.0
        assert result.statut == CapaciteStatus.INSUFFISANTE

    def test_calculer_endettement_normal(self):
        """Test calcul endettement normal"""
        result = RatioCalculator.calculer_endettement(
            dettes=300000.0,
            capitaux_propres=700000.0
        )
        assert result.type == RatioType.ENDETTEMENT
        assert abs(result.valeur - (300000.0 / 700000.0)) < 0.001

    def test_calculer_tresorerie_normale(self):
        """Test calcul trésorerie normale"""
        result = RatioCalculator.calculer_tresorerie(
            liquidites=500000.0,
            dettes_ct=250000.0
        )
        assert result.type == RatioType.TRESORERIE
        assert result.valeur == 2.0

    def test_calculer_bfr(self):
        """Test calcul BFR"""
        result = RatioCalculator.calculer_bfr(
            bfr=50000.0,
            chiffre_affaires=1000000.0
        )
        assert result.type == RatioType.BFR
        assert result.valeur == 0.05

    def test_calculer_capacite_remboursement(self):
        """Test calcul capacité de remboursement"""
        result = RatioCalculator.calculer_capacite_remboursement(
            resultat_net=100000.0,
            dettes=500000.0
        )
        assert result.type == RatioType.CAPACITE_REMBOURSEMENT
        assert result.valeur == 0.20


# =============================================================================
# TESTS POUR CapaciteFinanciereCalculator
# =============================================================================

class TestCapaciteFinanciereCalculator:
    def test_analyser_capacite_suffisante(self):
        """Test analyse capacité financière suffisante"""
        calc = CapaciteFinanciereCalculator()
        result = calc.analyser(
            capitaux_propres=1000000.0,
            dettes=500000.0,
            dettes_ct=200000.0,
            liquidites=300000.0,
            bfr=100000.0,
            resultat_net=200000.0,
            chiffre_affaires=2000000.0,
            marge_nette=10.0
        )
        assert isinstance(result, CapaciteFinanciereResult)
        assert result.score_global >= 0
        assert result.score_global <= 100
        assert result.statut in [CapaciteStatus.SUFFISANTE, CapaciteStatus.LIMITE, 
                                   CapaciteStatus.INSUFFISANTE, CapaciteStatus.CRITIQUE]

    def test_analyser_capacite_insuffisante(self):
        """Test analyse capacité financière insuffisante"""
        calc = CapaciteFinanciereCalculator()
        result = calc.analyser(
            capitaux_propres=100000.0,
            dettes=900000.0,
            dettes_ct=500000.0,
            liquidites=50000.0,
            bfr=500000.0,
            resultat_net=50000.0,
            chiffre_affaires=1000000.0,
            marge_nette=5.0
        )
        assert isinstance(result, CapaciteFinanciereResult)
        assert result.score_global >= 0
        # Avec ces valeurs faibles, le score doit être bas
        assert result.score_global < 50 or result.statut in [CapaciteStatus.INSUFFISANTE, CapaciteStatus.CRITIQUE]

    def test_calculer_montant_max_marche(self):
        """Test calcul montant max marché"""
        calc = CapaciteFinanciereCalculator()
        montant = calc._calculer_montant_max(
            capitaux_propres=500000.0,
            dettes=200000.0,
            marge_nette=10.0,
            engagement_max=30.0
        )
        # 500000 * 0.30 = 150000
        # resultat_annuel_estime = 500000 * 0.10 = 50000
        # montant_max_remboursement = 50000 * 2 = 100000
        # min(150000, 100000) = 100000
        assert montant == 100000.0

    def test_calculer_montant_max_marche_zero_capacite(self):
        """Test calcul montant max marché avec capacité à 0"""
        calc = CapaciteFinanciereCalculator()
        montant = calc._calculer_montant_max(
            capitaux_propres=0.0,
            dettes=0.0,
            marge_nette=0.0
        )
        assert montant == 0.0
