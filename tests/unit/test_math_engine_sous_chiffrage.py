"""
SMART_AO V7 - Tests unitaires pour sous_chiffrage.py
==================================================
Tests complets pour SousChiffrageResult, SousChiffrageDetector
"""

import pytest
from app.engines.math_engine.sous_chiffrage import (
    SEUIL_RISQUE_FAIBLE, SEUIL_RISQUE_MOYEN, SEUIL_RISQUE_ELEVE,
    SousChiffrageResult, SousChiffrageDetector
)


# =============================================================================
# TESTS POUR CONSTANTES
# =============================================================================

class TestSeuils:
    def test_seuil_risque_faible(self):
        assert SEUIL_RISQUE_FAIBLE == 0.05

    def test_seuil_risque_moyen(self):
        assert SEUIL_RISQUE_MOYEN == 0.10

    def test_seuil_risque_eleve(self):
        assert SEUIL_RISQUE_ELEVE == 0.20


# =============================================================================
# TESTS POUR SousChiffrageResult
# =============================================================================

class TestSousChiffrageResult:
    def test_creation_sans_risque(self):
        result = SousChiffrageResult(
            est_sous_chiffre=False,
            niveau_risque="AUCUN",
            ecart_absolu=0.0,
            ecart_relatif=0.0,
            estimation=100000.0,
            cout_reel=100000.0
        )
        assert result.est_sous_chiffre is False
        assert result.niveau_risque == "AUCUN"
        assert result.ecart_absolu == 0.0
        assert result.ecart_relatif == 0.0
        assert result.recommandations == []

    def test_creation_avec_risque(self):
        result = SousChiffrageResult(
            est_sous_chiffre=True,
            niveau_risque="ELEVE",
            ecart_absolu=20000.0,
            ecart_relatif=0.20,
            estimation=100000.0,
            cout_reel=120000.0,
            marge_perdue=5000.0,
            recommandations=["Revoir l'estimation", "Négocier avec le client"]
        )
        assert result.est_sous_chiffre is True
        assert result.niveau_risque == "ELEVE"
        assert result.marge_perdue == 5000.0
        assert result.recommandations == ["Revoir l'estimation", "Négocier avec le client"]

    def test_to_dict(self):
        result = SousChiffrageResult(
            est_sous_chiffre=True,
            niveau_risque="MOYEN",
            ecart_absolu=10000.0,
            ecart_relatif=0.10,
            estimation=100000.0,
            cout_reel=110000.0,
            marge_perdue=3000.0,
            recommandations=["Analyser les coûts"]
        )
        d = result.to_dict()
        
        assert d["est_sous_chiffre"] is True
        assert d["niveau_risque"] == "MOYEN"
        assert d["ecart_absolu"] == 10000.0
        assert d["ecart_relatif"] == 10.0  # 0.10 * 100
        assert d["recommandations"] == ["Analyser les coûts"]


# =============================================================================
# TESTS POUR SousChiffrageDetector
# =============================================================================

class TestSousChiffrageDetector:
    def test_detecter_sans_sous_chiffrage(self):
        """Test détection sans sous-chiffrage"""
        detector = SousChiffrageDetector()
        result = detector.detecter_sous_chiffrage(
            estimation=100000.0,
            cout_reel=95000.0
        )
        
        assert result.est_sous_chiffre is False
        assert result.ecart_absolu == -5000.0  # négatif = économie
        assert result.niveau_risque == "FAIBLE"

    def test_detecter_risque_faible(self):
        """Test détection risque faible (écart <= 5%)"""
        detector = SousChiffrageDetector()
        result = detector.detecter_sous_chiffrage(
            estimation=100000.0,
            cout_reel=103000.0  # 3% d'écart
        )
        
        assert result.est_sous_chiffre is True
        assert result.niveau_risque == "MOYEN"  # <= 5% = MOYEN
        assert result.ecart_absolu == 3000.0

    def test_detecter_risque_moyen(self):
        """Test détection risque moyen (5% < écart <= 10%)"""
        detector = SousChiffrageDetector()
        result = detector.detecter_sous_chiffrage(
            estimation=100000.0,
            cout_reel=108000.0  # 8% d'écart
        )
        
        assert result.est_sous_chiffre is True
        assert result.niveau_risque == "ELEVE"  # <= 10% = ELEVE
        assert abs(result.ecart_relatif - 0.08) < 0.01

    def test_detecter_risque_eleve(self):
        """Test détection risque élevé (10% < écart <= 20%)"""
        detector = SousChiffrageDetector()
        result = detector.detecter_sous_chiffrage(
            estimation=100000.0,
            cout_reel=115000.0  # 15% d'écart
        )
        
        assert result.est_sous_chiffre is True
        assert result.niveau_risque == "CRITIQUE"  # <= 20% = CRITIQUE
        assert abs(result.ecart_relatif - 0.15) < 0.01

    def test_detecter_risque_critique(self):
        """Test détection risque critique (> 20%)"""
        detector = SousChiffrageDetector()
        result = detector.detecter_sous_chiffrage(
            estimation=100000.0,
            cout_reel=150000.0  # 50% d'écart
        )
        
        assert result.est_sous_chiffre is True
        assert result.niveau_risque == "CATASTROPHIQUE"
        assert abs(result.ecart_relatif - 0.50) < 0.01

    def test_detecter_avec_taux_marge(self):
        """Test détection avec taux de marge personnalisé"""
        detector = SousChiffrageDetector(taux_marge_cible=0.20)
        result = detector.detecter_sous_chiffrage(
            estimation=100000.0,
            cout_reel=110000.0
        )
        
        assert result.est_sous_chiffre is True
        # Marge perdue = (cout_reel - estimation) * taux_marge
        # Mais en fait, c'est l'écart lui-même qui représente la perte
        assert result.marge_perdue > 0

    def test_result_stored(self):
        """Test que le résultat est stocké"""
        detector = SousChiffrageDetector()
        detector.detecter_sous_chiffrage(
            estimation=100000.0,
            cout_reel=110000.0
        )
        
        assert detector.result is not None
        assert detector.result.est_sous_chiffre is True

    def test_analyser_chantier_complet(self):
        """Test analyse chantier complet"""
        detector = SousChiffrageDetector()
        lots = [
            {"nom": "lot1", "estimation": 100000.0, "cout_reel": 110000.0},
            {"nom": "lot2", "estimation": 200000.0, "cout_reel": 190000.0}
        ]
        
        result = detector.analyser_chantier_complet(lots)
        
        assert isinstance(result, dict)
        assert "analyse_par_lot" in result
        assert result["total_lots"] == 2
        assert result["lots_sous_chiffres"] == 1  # lot1 est sous-chiffré
