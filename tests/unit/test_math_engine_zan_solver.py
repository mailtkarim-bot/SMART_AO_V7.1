"""
SMART_AO V7 - Test unitaire pour zan_solver
=============================================
Tests unitaires complets pour le module math_engine/zan_solver.
Cible: 70%+ couverture
"""

import pytest
import json
import os
import tempfile
from decimal import Decimal, ROUND_HALF_UP
from unittest.mock import patch, MagicMock

from app.engines.math_engine.zan_solver import (
    ZANSolver,
    ZANResult,
    zan_solver,
    get_zan_solver,
    calculer_cout_zan,
    REFERENTIEL_PATH,
)
from app.engines.math_engine.types import Amount, SolverResult


class TestZANResult:
    """Tests pour la classe ZANResult."""

    def test_zan_result_creation(self):
        """Test la création d'un ZANResult."""
        result = ZANResult(
            cout_total=Decimal("1000.00"),
            volume=Decimal("10.00"),
            distance_km=Decimal("50.00"),
            cout_m3=Decimal("100.00"),
            isdi_id="ISDI_001",
            trackterres_obligatoire=True,
            detail_calcul={"test": "value"}
        )
        assert result.cout_total == Decimal("1000.00")
        assert result.volume == Decimal("10.00")
        assert result.distance_km == Decimal("50.00")
        assert result.cout_m3 == Decimal("100.00")
        assert result.isdi_id == "ISDI_001"
        assert result.trackterres_obligatoire is True
        assert result.detail_calcul == {"test": "value"}

    def test_zan_result_to_dict(self):
        """Test la conversion en dictionnaire."""
        result = ZANResult(
            cout_total=Decimal("1000.00"),
            volume=Decimal("10.00"),
            distance_km=Decimal("50.00"),
            cout_m3=Decimal("100.00"),
            isdi_id="ISDI_001",
            trackterres_obligatoire=True,
            detail_calcul={"test": "value"}
        )
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert result_dict["cout_total"] == 1000.00
        assert result_dict["volume"] == 10.00
        assert result_dict["distance_km"] == 50.00
        assert result_dict["cout_m3"] == 100.00
        assert result_dict["isdi_id"] == "ISDI_001"
        assert result_dict["trackterres_obligatoire"] is True
        assert result_dict["detail_calcul"] == {"test": "value"}

    def test_zan_result_to_dict_rounding(self):
        """Test l'arrondi dans to_dict."""
        result = ZANResult(
            cout_total=Decimal("1000.123"),
            volume=Decimal("10.456"),
            distance_km=Decimal("50.789"),
            cout_m3=Decimal("100.123"),
            isdi_id=None,
            trackterres_obligatoire=False,
            detail_calcul={}
        )
        result_dict = result.to_dict()
        
        assert result_dict["cout_total"] == 1000.12
        assert result_dict["volume"] == 10.46
        assert result_dict["distance_km"] == 50.79
        assert result_dict["cout_m3"] == 100.12


class TestZANSolver:
    """Tests pour la classe ZANSolver."""

    def test_solver_initialization(self):
        """Test l'initialisation du solveur."""
        solver = ZANSolver()
        assert solver.referentiel_path == REFERENTIEL_PATH
        assert isinstance(solver.referentiel, dict)

    def test_solver_initialization_custom_path(self):
        """Test l'initialisation avec un chemin personnalisé."""
        custom_path = "/custom/path/referentiel.json"
        solver = ZANSolver(referentiel_path=custom_path)
        assert solver.referentiel_path == custom_path

    def test_load_referentiel_success(self):
        """Test le chargement réussi du référentiel."""
        referentiel_data = {
            "isdi": [
                {"id": "ISDI_001", "lat": 48.8566, "lon": 2.3522, "types_acceptes": ["terre", "deblais"], "tarif_m3": 15.0}
            ],
            "trackterres": {"obligatoire": True, "cout_tracking_m3": 1.2}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(referentiel_data, f)
            temp_path = f.name
        
        try:
            solver = ZANSolver(referentiel_path=temp_path)
            assert solver.referentiel == referentiel_data
        finally:
            os.unlink(temp_path)

    def test_load_referentiel_file_not_found(self):
        """Test le chargement avec un fichier introuvable."""
        solver = ZANSolver(referentiel_path="/nonexistent/path/referentiel.json")
        
        # Doit retourner un référentiel par défaut
        assert "isdi" in solver.referentiel
        assert "trackterres" in solver.referentiel
        assert solver.referentiel["isdi"] == []

    def test_haversine_calculation(self):
        """Test le calcul de distance Haversine."""
        solver = ZANSolver()
        
        # Test avec Paris (48.8566, 2.3522) et Lyon (45.7640, 4.8357)
        distance = solver._haversine(48.8566, 2.3522, 45.7640, 4.8357)
        
        # Distance approximative Paris-Lyon: ~392 km
        assert isinstance(distance, float)
        assert 380 < distance < 410

    def test_haversine_same_point(self):
        """Test la distance entre le même point."""
        solver = ZANSolver()
        distance = solver._haversine(48.8566, 2.3522, 48.8566, 2.3522)
        assert distance == 0.0

    def test_find_nearest_isdi(self):
        """Test la recherche de l'ISDI la plus proche."""
        referentiel_data = {
            "isdi": [
                {"id": "ISDI_001", "lat": 48.8566, "lon": 2.3522, "types_acceptes": ["terre"], "tarif_m3": 15.0},
                {"id": "ISDI_002", "lat": 45.7640, "lon": 4.8357, "types_acceptes": ["terre"], "tarif_m3": 20.0},
            ],
            "trackterres": {"obligatoire": True, "cout_tracking_m3": 1.2}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(referentiel_data, f)
            temp_path = f.name
        
        try:
            solver = ZANSolver(referentiel_path=temp_path)
            
            # Trouver l'ISDI la plus proche de Paris
            nearest = solver._find_nearest_isdi(48.8566, 2.3522, "terre")
            
            assert nearest is not None
            assert nearest["id"] == "ISDI_001"
            assert "distance_km" in nearest
            assert nearest["distance_km"] < 1.0  # Très proche
        finally:
            os.unlink(temp_path)

    def test_find_nearest_isdi_no_match_type(self):
        """Test la recherche quand aucune ISDI n'accepte le type."""
        referentiel_data = {
            "isdi": [
                {"id": "ISDI_001", "lat": 48.8566, "lon": 2.3522, "types_acceptes": ["deblais"], "tarif_m3": 15.0},
            ],
            "trackterres": {"obligatoire": True, "cout_tracking_m3": 1.2}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(referentiel_data, f)
            temp_path = f.name
        
        try:
            solver = ZANSolver(referentiel_path=temp_path)
            
            # Rechercher avec type_terre="terre" (non dans la liste)
            nearest = solver._find_nearest_isdi(48.8566, 2.3522, "terre")
            
            # Doit retourner toutes les ISDI si aucune ne correspond
            assert nearest is not None
            assert nearest["id"] == "ISDI_001"
        finally:
            os.unlink(temp_path)

    def test_find_nearest_isdi_empty_list(self):
        """Test la recherche avec une liste ISDI vide."""
        referentiel_data = {
            "isdi": [],
            "trackterres": {"obligatoire": True, "cout_tracking_m3": 1.2}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(referentiel_data, f)
            temp_path = f.name
        
        try:
            solver = ZANSolver(referentiel_path=temp_path)
            nearest = solver._find_nearest_isdi(48.8566, 2.3522, "terre")
            assert nearest is None
        finally:
            os.unlink(temp_path)

    def test_solve_with_distance_override(self):
        """Test solve avec distance spécifiée."""
        solver = ZANSolver()
        
        data = {
            "volume": 100,
            "distance_km": 50,
            "type_terre": "terre"
        }
        
        result = solver.solve(data)
        
        assert isinstance(result, SolverResult)
        assert result.solver_name == "ZANSolver"
        assert result.output.value > Decimal("0")
        assert result.penalties == []
        assert result.warnings == []
        assert "detail_calcul" in result.metadata

    def test_solve_with_coordinates(self):
        """Test solve avec coordonnées GPS."""
        referentiel_data = {
            "isdi": [
                {"id": "ISDI_001", "lat": 48.8566, "lon": 2.3522, "types_acceptes": ["terre"], "tarif_m3": 15.0},
            ],
            "trackterres": {"obligatoire": True, "cout_tracking_m3": 1.2},
            "unite_transport_eur_km": 0.85
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(referentiel_data, f)
            temp_path = f.name
        
        try:
            solver = ZANSolver(referentiel_path=temp_path)
            
            data = {
                "volume": 100,
                "lat": 48.8566,
                "lon": 2.3522,
                "type_terre": "terre"
            }
            
            result = solver.solve(data)
            
            assert isinstance(result, SolverResult)
            assert result.solver_name == "ZANSolver"
            assert result.output.value > Decimal("0")
        finally:
            os.unlink(temp_path)

    def test_solve_formula_calculation(self):
        """Test le calcul de la formule."""
        solver = ZANSolver()
        
        # Données avec paramètres connus
        data = {
            "volume": 100,
            "distance_km": 10,
            "type_terre": "terre"
        }
        
        result = solver.solve(data)
        detail = result.metadata["detail_calcul"]
        
        # Vérifier la formule: volume × (tri + transport × distance + exutoire + tracking)
        # tri = 5.0, transport = 0.85, distance = 10, exutoire = 15.0, tracking = 1.2
        cout_tri = Decimal("5.00")
        cout_transport = Decimal("0.85") * Decimal("10")
        tarif_exutoire = Decimal("15.00")
        cout_tracking = Decimal("1.2")
        cout_m3 = cout_tri + cout_transport + tarif_exutoire + cout_tracking
        expected_total = Decimal("100") * cout_m3
        
        assert result.output.value.quantize(Decimal("0.01")) == expected_total.quantize(Decimal("0.01"))

    def test_solve_zero_volume(self):
        """Test solve avec volume à zéro."""
        solver = ZANSolver()
        
        data = {
            "volume": 0,
            "distance_km": 10,
            "type_terre": "terre"
        }
        
        result = solver.solve(data)
        
        assert result.output.value == Decimal("0.00")

    def test_solve_custom_currency(self):
        """Test solve avec une devise personnalisée."""
        solver = ZANSolver()
        
        data = {
            "volume": 100,
            "distance_km": 10,
            "type_terre": "terre",
            "currency": "USD"
        }
        
        result = solver.solve(data)
        
        assert result.output.currency == "USD"

    def test_calculer_method(self):
        """Test la méthode calculer."""
        solver = ZANSolver()
        
        result = solver.calculer(
            volume=100,
            lat=48.8566,
            lon=2.3522,
            type_terre="terre",
            distance_km=10
        )
        
        assert isinstance(result, ZANResult)
        assert result.volume == Decimal("100")
        assert result.cout_total > Decimal("0")
        assert result.trackterres_obligatoire is True

    def test_calculer_with_distance_override(self):
        """Test calculer avec distance spécifiée."""
        solver = ZANSolver()
        
        result = solver.calculer(
            volume=50,
            distance_km=20,
            type_terre="deblais"
        )
        
        assert isinstance(result, ZANResult)
        assert result.volume == Decimal("50")
        assert result.distance_km == Decimal("20")


class TestSingleton:
    """Tests pour le singleton zan_solver."""

    def test_zan_solver_singleton(self):
        """Test que zan_solver est un singleton."""
        assert zan_solver is not None
        assert isinstance(zan_solver, ZANSolver)

    def test_get_zan_solver(self):
        """Test la fonction get_zan_solver."""
        solver = get_zan_solver()
        assert solver is zan_solver
        assert isinstance(solver, ZANSolver)


class TestCalculerCoutZan:
    """Tests pour la fonction utilitaire calculer_cout_zan."""

    def test_calculer_cout_zan_function(self):
        """Test la fonction calculer_cout_zan."""
        result = calculer_cout_zan(
            volume=100,
            lat=48.8566,
            lon=2.3522,
            type_terre="terre",
            distance_km=10
        )
        
        assert isinstance(result, dict)
        assert "cout_total" in result
        assert "volume" in result
        assert "distance_km" in result
        assert "cout_m3" in result
        assert "isdi_id" in result
        assert "trackterres_obligatoire" in result
        assert "detail_calcul" in result

    def test_calculer_cout_zan_with_distance(self):
        """Test calculer_cout_zan avec distance spécifiée."""
        result = calculer_cout_zan(
            volume=50,
            distance_km=25
        )
        
        assert result["volume"] == 50.0
        assert result["distance_km"] == 25.0


class TestEdgeCases:
    """Tests pour les cas limites."""

    def test_negative_volume(self):
        """Test avec un volume négatif."""
        solver = ZANSolver()
        data = {"volume": -10, "distance_km": 10}
        
        result = solver.solve(data)
        
        # Le volume négatif devrait donner un coût négatif
        assert result.output.value < Decimal("0")

    def test_very_large_volume(self):
        """Test avec un très grand volume."""
        solver = ZANSolver()
        data = {"volume": 1000000, "distance_km": 100}
        
        result = solver.solve(data)
        
        # Doit retourner un résultat valide
        assert result.output.value > Decimal("0")

    def test_none_values(self):
        """Test avec des valeurs None."""
        solver = ZANSolver()
        data = {"volume": 100}
        
        result = solver.solve(data)
        
        # Doit gérer les valeurs None
        assert isinstance(result, SolverResult)

    def test_string_values(self):
        """Test avec des valeurs string."""
        solver = ZANSolver()
        data = {"volume": "100", "distance_km": "10"}
        
        result = solver.solve(data)
        
        assert isinstance(result, SolverResult)
        assert result.output.value == Decimal("100") * (
            Decimal("5.00") + Decimal("0.85") * Decimal("10") + Decimal("15.00") + Decimal("1.2")
        )

    def test_decimal_precision(self):
        """Test la précision des décimaux."""
        solver = ZANSolver()
        
        data = {
            "volume": 100.123,
            "distance_km": 10.456
        }
        
        result = solver.solve(data)
        
        # Vérifier que le résultat est bien arrondi
        assert result.output.value == result.output.value.quantize(Decimal("0.01"))
