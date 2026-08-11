"""
SMART_AO V7 - Tests unitaires pour bt_projection.py
==================================================
Tests complets pour FluxTresorerie, ProjectionBT, BTProjectionCalculator
"""

import pytest
from datetime import date
from app.engines.math_engine.bt_projection import FluxTresorerie, ProjectionBT, BTProjectionCalculator


# =============================================================================
# TESTS POUR FluxTresorerie
# =============================================================================

class TestFluxTresorerie:
    def test_creation(self):
        flux = FluxTresorerie(
            mois=1,
            annee=2026,
            entrees=50000.0,
            sorties=30000.0,
            solde=20000.0
        )
        assert flux.mois == 1
        assert flux.annee == 2026
        assert flux.entrees == 50000.0
        assert flux.sorties == 30000.0
        assert flux.solde == 20000.0

    def test_creation_default(self):
        flux = FluxTresorerie(mois=1, annee=2026)
        assert flux.entrees == 0.0
        assert flux.sorties == 0.0
        assert flux.solde == 0.0

    def test_solde_cumule(self):
        flux = FluxTresorerie(
            mois=1,
            annee=2026,
            entrees=50000.0,
            sorties=30000.0,
            solde=0.0
        )
        assert flux.solde_cumule == 20000.0


# =============================================================================
# TESTS POUR ProjectionBT
# =============================================================================

class TestProjectionBT:
    def test_creation_simple(self):
        projection = ProjectionBT(
            montant_marche=1000000.0,
            duree_mois=12
        )
        assert projection.montant_marche == 1000000.0
        assert projection.duree_mois == 12
        assert projection.avance_pourcentage == 30.0
        assert projection.retentions_pourcentage == 5.0

    def test_to_dict(self):
        projection = ProjectionBT(
            montant_marche=1000000.0,
            duree_mois=12
        )
        result = projection.to_dict()
        
        assert result["montant_marche"] == 1000000.0
        assert result["duree_mois"] == 12


# =============================================================================
# TESTS POUR BTProjectionCalculator
# =============================================================================

class TestBTProjectionCalculator:
    def test_calculer_projection_simple(self):
        """Test calcul de projection simple"""
        calculator = BTProjectionCalculator()
        projection = calculator.calculer_projection(
            montant_marche=1000000.0,
            duree_mois=3
        )
        
        assert isinstance(projection, ProjectionBT)
        assert projection.montant_marche == 1000000.0
        assert projection.duree_mois == 3
        assert len(projection.flux_mensuels) == 3

    def test_calculer_projection_with_params(self):
        """Test calcul de projection avec paramètres"""
        calculator = BTProjectionCalculator()
        projection = calculator.calculer_projection(
            montant_marche=2000000.0,
            duree_mois=6,
            avance_pourcentage=25.0,
            retentions_pourcentage=10.0,
            taux_marge=0.20
        )
        
        assert isinstance(projection, ProjectionBT)
        assert projection.montant_marche == 2000000.0
        assert len(projection.flux_mensuels) == 6

    def test_projection_stored(self):
        """Test que la projection est stockée dans le calculator"""
        calculator = BTProjectionCalculator()
        projection = calculator.calculer_projection(
            montant_marche=1000000.0,
            duree_mois=3
        )
        
        assert calculator.projection is not None
        assert calculator.projection.montant_marche == 1000000.0
