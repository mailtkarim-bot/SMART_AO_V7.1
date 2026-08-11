"""
SMART_AO V7 - Tests unitaires pour vigilance_solver.py
====================================================
Tests complets pour VigilanceResult, VigilanceSolver
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from app.engines.math_engine.vigilance_solver import (
    VALIDITE_URSSAF_JOURS,
    VigilanceResult, VigilanceSolver
)


# =============================================================================
# TESTS POUR CONSTANTES
# =============================================================================

class TestConstantes:
    def test_validite_urssaf_jours(self):
        assert VALIDITE_URSSAF_JOURS == 180


# =============================================================================
# TESTS POUR VigilanceResult
# =============================================================================

class TestVigilanceResult:
    def test_creation_attestation_valide(self):
        result = VigilanceResult(
            blocage_depot=False,
            attestation_valide=True,
            exposition_solidaire=Decimal("0"),
            motif_blocage="",
            detail_calcul={"test": "value"}
        )
        assert result.blocage_depot is False
        assert result.attestation_valide is True
        assert result.exposition_solidaire == Decimal("0")
        assert result.motif_blocage == ""

    def test_creation_attestation_invalide(self):
        result = VigilanceResult(
            blocage_depot=True,
            attestation_valide=False,
            exposition_solidaire=Decimal("100000.00"),
            motif_blocage="Attestation expirée",
            detail_calcul={"montant": 100000.00}
        )
        assert result.blocage_depot is True
        assert result.attestation_valide is False
        assert result.exposition_solidaire == Decimal("100000.00")

    def test_to_dict(self):
        result = VigilanceResult(
            blocage_depot=True,
            attestation_valide=False,
            exposition_solidaire=Decimal("50000.00"),
            motif_blocage="Test",
            detail_calcul={"test": 123}
        )
        d = result.to_dict()
        
        assert d["blocage_depot"] is True
        assert d["attestation_valide"] is False
        assert d["exposition_solidaire"] == 50000.00
        assert d["motif_blocage"] == "Test"


# =============================================================================
# TESTS POUR VigilanceSolver
# =============================================================================

class TestVigilanceSolver:
    def test_attestation_valide(self):
        """Test avec attestation URSSAF valide"""
        solver = VigilanceSolver()
        result = solver.calculer(
            date_attestation=(datetime.now() - timedelta(days=30)).isoformat(),
            montant_sous_traite=100000.00,
            statut_juridique="actif"
        )
        
        assert result.attestation_valide is True
        assert result.blocage_depot is False

    def test_attestation_expirée(self):
        """Test avec attestation URSSAF expirée (> 6 mois)"""
        solver = VigilanceSolver()
        result = solver.calculer(
            date_attestation=(datetime.now() - timedelta(days=200)).isoformat(),
            montant_sous_traite=100000.00,
            statut_juridique="actif"
        )
        
        assert result.attestation_valide is False
        assert result.blocage_depot is True
        assert result.exposition_solidaire == Decimal("100000.00")

    def test_sous_traitant_en_liquidation(self):
        """Test avec sous-traitant en liquidation"""
        solver = VigilanceSolver()
        result = solver.calculer(
            date_attestation=datetime.now().isoformat(),
            montant_sous_traite=100000.00,
            statut_juridique="liquidation"
        )
        
        assert result.attestation_valide is False
        assert result.blocage_depot is True
        assert result.exposition_solidaire == Decimal("100000.00")

    def test_sous_traitant_en_radiation(self):
        """Test avec sous-traitant en radiation"""
        solver = VigilanceSolver()
        result = solver.calculer(
            date_attestation=datetime.now().isoformat(),
            montant_sous_traite=50000.00,
            statut_juridique="radiation"
        )
        
        assert result.blocage_depot is True
        assert result.exposition_solidaire == Decimal("50000.00")

    def test_montant_zero(self):
        """Test avec montant sous-traité à 0"""
        solver = VigilanceSolver()
        result = solver.calculer(
            date_attestation=(datetime.now() - timedelta(days=200)).isoformat(),
            montant_sous_traite=0.00,
            statut_juridique="actif"
        )
        
        assert result.exposition_solidaire == Decimal("0")

    def test_sans_date_attestation(self):
        """Test sans date d'attestation"""
        solver = VigilanceSolver()
        result = solver.calculer(
            date_attestation=None,
            montant_sous_traite=100000.00,
            statut_juridique="actif"
        )
        
        # Sans date, l'attestation n'est pas valide
        assert result.attestation_valide is False

    def test_attestation_a_la_limite(self):
        """Test attestation exactement à la limite de 6 mois"""
        solver = VigilanceSolver()
        result = solver.calculer(
            date_attestation=(datetime.now() - timedelta(days=180)).isoformat(),
            montant_sous_traite=100000.00,
            statut_juridique="actif"
        )
        
        # À 180 jours exactement, l'attestation est encore valide (<= 180)
        assert result.attestation_valide is True
        assert result.blocage_depot is False

    def test_attestation_juste_valide(self):
        """Test attestation juste valide (179 jours)"""
        solver = VigilanceSolver()
        result = solver.calculer(
            date_attestation=(datetime.now() - timedelta(days=179)).isoformat(),
            montant_sous_traite=100000.00,
            statut_juridique="actif"
        )
        
        assert result.attestation_valide is True
        assert result.blocage_depot is False

    def test_solve_returns_solver_result(self):
        """Test que solve retourne un SolverResult"""
        solver = VigilanceSolver()
        data = {
            "date_attestation": (datetime.now() - timedelta(days=200)).isoformat(),
            "montant_sous_traite": 100000.00,
            "statut_juridique": "actif",
            "currency": "EUR"
        }
        
        result = solver.solve(data)
        
        # SolverResult a metadata avec detail_calcul
        assert result.metadata is not None
        assert "detail_calcul" in result.metadata
        assert result.metadata["detail_calcul"]["blocage_depot"] is True
