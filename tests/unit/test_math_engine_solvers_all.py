"""
SMART_AO V7 - Test unitaire pour tous les solvers du math_engine
===============================================================
Tests unitaires qui exécutent le code de tous les solvers pour améliorer la couverture.
"""

import pytest
import sys
from pathlib import Path
from decimal import Decimal

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))


class TestAvance2024Calculator:
    """Tests pour Avance2024Calculator."""
    
    @pytest.fixture
    def calculator(self):
        from app.engines.math_engine.solvers.avance_2024_calculator import Avance2024Calculator
        return Avance2024Calculator()
    
    def test_solve_travaux(self, calculator):
        """Test solve avec type de marché travaux."""
        data = {
            'montant_ht': 1000000,
            'type_marche': 'travaux',
            'avancement_pct': 50,
            'currency': 'EUR'
        }
        result = calculator.solve(data)
        assert result is not None
        assert result.solver_name == "Avance2024Calculator"
        assert result.metadata['status'] == 'calculated'
    
    def test_solve_fournitures(self, calculator):
        """Test solve avec type de marché fournitures."""
        data = {
            'montant_ht': 1000000,
            'type_marche': 'fournitures',
            'avancement_pct': 30,
            'currency': 'EUR'
        }
        result = calculator.solve(data)
        assert result is not None
        assert result.metadata['status'] == 'calculated'
    
    def test_solve_plafond(self, calculator):
        """Test solve avec montant dépassant le plafond."""
        data = {
            'montant_ht': 20000000,  # Très élevé
            'type_marche': 'travaux',
            'avancement_pct': 10,
            'currency': 'EUR'
        }
        result = calculator.solve(data)
        assert result is not None
        assert result.metadata['plafond_atteint'] is True


class TestCCAGCalculator:
    """Tests pour CCAGCalculator."""
    
    @pytest.fixture
    def calculator(self):
        from app.engines.math_engine.solvers.ccag_calculator import CCAGCalculator
        return CCAGCalculator()
    
    def test_solve(self, calculator):
        """Test solve de base."""
        data = {
            'montant_ht': 500000,
            'type_marche': 'travaux',
            'duree_mois': 12
        }
        result = calculator.solve(data)
        assert result is not None
        assert result.solver_name == "CCAGCalculator"


class TestFdesproduits:
    """Tests pour Fdesproduits."""
    
    @pytest.fixture
    def calculator(self):
        from app.engines.math_engine.solvers.fdes_produits import Fdesproduits
        return Fdesproduits()
    
    def test_solve(self, calculator):
        """Test solve de base."""
        data = {
            'produits': [
                {'nom': 'Ciment', 'quantite': 100, 'prix_unitaire': 10.50},
                {'nom': 'Acier', 'quantite': 50, 'prix_unitaire': 25.00}
            ]
        }
        result = calculator.solve(data)
        assert result is not None


class TestIndicesmateriaux:
    """Tests pour Indicesmateriaux."""
    
    @pytest.fixture
    def calculator(self):
        from app.engines.math_engine.solvers.indices_materiaux import Indicesmateriaux
        return Indicesmateriaux()
    
    def test_solve(self, calculator):
        """Test solve de base."""
        data = {
            'materiaux': ['acier', 'beton'],
            'mois': 8,
            'annee': 2026
        }
        result = calculator.solve(data)
        assert result is not None


class TestJurisprudencecontentieux:
    """Tests pour Jurisprudencecontentieux."""
    
    @pytest.fixture
    def calculator(self):
        from app.engines.math_engine.solvers.jurisprudence_contentieux import Jurisprudencecontentieux
        return Jurisprudencecontentieux()
    
    def test_solve(self, calculator):
        """Test solve de base."""
        data = {
            'clauses': ['clause 1', 'clause 2'],
            'montant': 100000
        }
        result = calculator.solve(data)
        assert result is not None


class TestMateriauxShieldSolver:
    """Tests pour MateriauxShieldSolver."""
    
    @pytest.fixture
    def calculator(self):
        from app.engines.math_engine.solvers.materiaux_shield import MateriauxShieldSolver
        return MateriauxShieldSolver()
    
    def test_solve(self, calculator):
        """Test solve de base."""
        data = {
            'materiaux': [{'nom': 'acier', 'quantite': 100}],
            'budget': 500000
        }
        result = calculator.solve(data)
        assert result is not None


class TestPenalitesCumulSolver:
    """Tests pour PenalitesCumulSolver."""
    
    @pytest.fixture
    def calculator(self):
        from app.engines.math_engine.solvers.penalites_cumul import PenalitesCumulSolver
        return PenalitesCumulSolver()
    
    def test_solve(self, calculator):
        """Test solve de base."""
        data = {
            'penalites': [
                {'montant': 10000, 'delai': 30, 'type': 'retard'}
            ]
        }
        result = calculator.solve(data)
        assert result is not None


class TestRatiosfinanciers:
    """Tests pour Ratiosfinanciers."""
    
    @pytest.fixture
    def calculator(self):
        from app.engines.math_engine.solvers.ratios_financiers import Ratiosfinanciers
        return Ratiosfinanciers()
    
    def test_solve(self, calculator):
        """Test solve de base."""
        data = {
            'ca': 1000000,
            'capitaux_propres': 200000,
            'dettes': 300000
        }
        result = calculator.solve(data)
        assert result is not None


class TestSeuileplusc:
    """Tests pour Seuileplusc."""
    
    @pytest.fixture
    def calculator(self):
        from app.engines.math_engine.solvers.seuil_eplusc import Seuileplusc
        return Seuileplusc()
    
    def test_solve(self, calculator):
        """Test solve de base."""
        data = {
            'lots': [
                {'nom': 'Lot 1', 'montant': 100000},
                {'nom': 'Lot 2', 'montant': 150000}
            ]
        }
        result = calculator.solve(data)
        assert result is not None


class TestTresoreriecalculator:
    """Tests pour Tresoreriecalculator."""
    
    @pytest.fixture
    def calculator(self):
        from app.engines.math_engine.solvers.tresorerie_calculator import Tresoreriecalculator
        return Tresoreriecalculator()
    
    def test_solve(self, calculator):
        """Test solve de base."""
        data = {
            'entrees': [100000, 150000, 200000],
            'sorties': [50000, 75000, 100000],
            'duree_mois': 12
        }
        result = calculator.solve(data)
        assert result is not None
