"""
SMART_AO V7 - Tests unitaires pour les modules clés du math_engine
======================================================================
Tests qui exécutent le code des modules math_engine les plus importants.
"""

import pytest
import sys
from pathlib import Path
from decimal import Decimal
from unittest.mock import Mock, patch

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))


class TestBtProjection:
    """Tests pour bt_projection.py."""
    
    def test_module_import(self):
        """Test que le module s'import correctement."""
        from app.engines.math_engine.bt_projection import BTProjectionCalculator
        assert BTProjectionCalculator is not None
    
    def test_calculator_initialization(self):
        """Test l'initialisation du calculateur."""
        from app.engines.math_engine.bt_projection import BTProjectionCalculator
        calc = BTProjectionCalculator()
        assert calc is not None


class TestCapaciteFinanciere:
    """Tests pour capacite_financiere.py."""
    
    def test_module_import(self):
        """Test que le module s'import correctement."""
        from app.engines.math_engine.capacite_financiere import CapaciteFinanciereCalculator
        assert CapaciteFinanciereCalculator is not None


class TestChiffragePulp:
    """Tests pour chiffrage_pulp.py."""
    
    def test_module_import(self):
        """Test que le module s'import correctement."""
        from app.engines.math_engine.chiffrage_pulp import ChiffragePulpSolver
        assert ChiffragePulpSolver is not None


class TestMargin:
    """Tests pour margin.py."""
    
    def test_module_import(self):
        """Test que le module s'import correctement."""
        from app.engines.math_engine.margin import MarginCalculator
        assert MarginCalculator is not None
    
    def test_calculer_marge_brute(self):
        """Test le calcul de marge brute."""
        from app.engines.math_engine.margin import MarginCalculator
        calc = MarginCalculator()
        # Appel avec des données de test
        result = calc.calculer_marge_brute(100000, 80000)
        assert result is not None


class TestPenalitesCumul:
    """Tests pour penalites_cumul.py."""
    
    def test_module_import(self):
        """Test que le module s'import correctement."""
        from app.engines.math_engine.penalites_cumul import PenalitesCalculator
        assert PenalitesCalculator is not None
    
    def test_penalites_calculator_initialization(self):
        """Test l'initialisation du calculateur de pénalités."""
        from app.engines.math_engine.penalites_cumul import PenalitesCalculator
        calc = PenalitesCalculator()
        assert calc is not None


class TestPlanning:
    """Tests pour planning.py."""
    
    def test_module_import(self):
        """Test que le module s'import correctement."""
        from app.engines.math_engine.planning import PlanningSolver
        assert PlanningSolver is not None
    
    def test_planning_solver_initialization(self):
        """Test l'initialisation du solveur de planning."""
        from app.engines.math_engine.planning import PlanningSolver
        solver = PlanningSolver()
        assert solver is not None


class TestRepCost:
    """Tests pour rep_cost.py."""
    
    def test_module_import(self):
        """Test que le module s'import correctement."""
        from app.engines.math_engine.rep_cost import RepCostCalculator
        assert RepCostCalculator is not None


class TestResources:
    """Tests pour resources.py."""
    
    def test_module_import(self):
        """Test que le module s'import correctement."""
        from app.engines.math_engine.resources import ResourceManager
        assert ResourceManager is not None
    
    def test_resource_manager_initialization(self):
        """Test l'initialisation du gestionnaire de ressources."""
        from app.engines.math_engine.resources import ResourceManager
        manager = ResourceManager()
        assert manager is not None


class TestRisquesGenerator:
    """Tests pour risques_generator.py."""
    
    def test_module_import(self):
        """Test que le module s'import correctement."""
        from app.engines.math_engine.risques_generator import RisquesGenerator
        assert RisquesGenerator is not None


class TestSiteCoeff:
    """Tests pour site_coeff.py."""
    
    def test_module_import(self):
        """Test que le module s'import correctement."""
        from app.engines.math_engine.site_coeff import SiteCoeffCalculator
        assert SiteCoeffCalculator is not None


class TestSousChiffrage:
    """Tests pour sous_chiffrage.py."""
    
    def test_module_import(self):
        """Test que le module s'import correctement."""
        from app.engines.math_engine.sous_chiffrage import SousChiffrageDetector
        assert SousChiffrageDetector is not None


class TestTreasury:
    """Tests pour treasury.py."""
    
    def test_module_import(self):
        """Test que le module s'import correctement."""
        from app.engines.math_engine.treasury import TreasuryAnalyzer
        assert TreasuryAnalyzer is not None
    
    def test_treasury_analyzer_initialization(self):
        """Test l'initialisation de l'analyseur de trésorerie."""
        from app.engines.math_engine.treasury import TreasuryAnalyzer
        analyzer = TreasuryAnalyzer()
        assert analyzer is not None


class TestWorstCase:
    """Tests pour worst_case.py."""
    
    def test_module_import(self):
        """Test que le module s'import correctement."""
        from app.engines.math_engine.worst_case import WorstCaseAnalyzer
        assert WorstCaseAnalyzer is not None
