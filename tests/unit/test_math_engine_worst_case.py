"""
SMART_AO V7 - Tests unitaires pour worst_case.py
===============================================
Tests complets pour Risque, Scenario, WorstCaseResult, WorstCaseAnalyzer
"""

import pytest
from datetime import date, timedelta
from app.engines.math_engine.worst_case import (
    Risque, Scenario, WorstCaseResult, WorstCaseAnalyzer
)


# =============================================================================
# TESTS POUR Risque
# =============================================================================

class TestRisque:
    def test_creation(self):
        risque = Risque(
            nom="Retard fournisseur",
            probabilite=0.3,
            impact_financier=50000.0,
            impact_delai=30,
            categorie="TECHNIQUE"
        )
        assert risque.nom == "Retard fournisseur"
        assert risque.probabilite == 0.3
        assert risque.impact_financier == 50000.0
        assert risque.impact_delai == 30
        assert risque.categorie == "TECHNIQUE"

    def test_creation_default(self):
        risque = Risque(
            nom="Test",
            probabilite=0.5,
            impact_financier=10000.0
        )
        assert risque.impact_delai == 0
        assert risque.categorie == "TECHNIQUE"

    def test_risque_calcule(self):
        risque = Risque(
            nom="Test",
            probabilite=0.25,
            impact_financier=100000.0
        )
        assert risque.risque_calcule == 25000.0


# =============================================================================
# TESTS POUR Scenario
# =============================================================================

class TestScenario:
    def test_creation(self):
        scenario = Scenario(
            nom="Faillite sous-traitant",
            probabilite=0.1,
            description="Sous-traitant principal en faillite",
            impact_financier=500000.0,
            impact_delai=90,
            risques=["retard", "cout_supplementaire"]
        )
        assert scenario.nom == "Faillite sous-traitant"
        assert scenario.probabilite == 0.1
        assert scenario.impact_financier == 500000.0
        assert scenario.impact_delai == 90

    def test_risque_calcule(self):
        scenario = Scenario(
            nom="Test",
            probabilite=0.2,
            description="Test",
            impact_financier=200000.0,
            impact_delai=0,
            risques=[]
        )
        assert scenario.risque_calcule == 40000.0


# =============================================================================
# TESTS POUR WorstCaseResult
# =============================================================================

class TestWorstCaseResult:
    def test_creation(self):
        scenario = Scenario(
            nom="Test",
            probabilite=0.5,
            description="Test",
            impact_financier=100000.0,
            impact_delai=0,
            risques=[]
        )
        
        result = WorstCaseResult(
            scenarios=[scenario],
            perte_maximale=200000.0,
            perte_moyenne=100000.0,
            probabilite_globale=0.5,
            scenario_pire=scenario,
            recommandations=["Revoir le planning"]
        )
        
        assert len(result.scenarios) == 1
        assert result.perte_maximale == 200000.0
        assert result.perte_moyenne == 100000.0
        assert result.probabilite_globale == 0.5

    def test_to_dict(self):
        scenario = Scenario(
            nom="Test",
            probabilite=0.5,
            description="Test",
            impact_financier=100000.0,
            impact_delai=0,
            risques=[]
        )
        
        result = WorstCaseResult(
            scenarios=[scenario],
            perte_maximale=200000.0,
            perte_moyenne=100000.0,
            probabilite_globale=0.5
        )
        
        d = result.to_dict()
        assert "scenarios" in d
        assert d["perte_maximale"] == 200000.0


# =============================================================================
# TESTS POUR WorstCaseAnalyzer
# =============================================================================

class TestWorstCaseAnalyzer:
    def test_creation_vide(self):
        analyzer = WorstCaseAnalyzer()
        assert analyzer.risques == {}
        assert analyzer.scenarios == []

    def test_ajouter_risque(self):
        analyzer = WorstCaseAnalyzer()
        analyzer.ajouter_risque(
            nom="Retard",
            probabilite=0.3,
            impact_financier=50000.0,
            impact_delai=30
        )
        
        assert "Retard" in analyzer.risques
        assert analyzer.risques["Retard"].probabilite == 0.3

    def test_analyser_scenarios_vide(self):
        analyzer = WorstCaseAnalyzer()
        result = analyzer.analyser_scenarios()
        
        assert result.scenarios == []
        assert result.perte_maximale == 0
        assert result.probabilite_globale == 0

    def test_analyser_scenarios_avec_risques(self):
        analyzer = WorstCaseAnalyzer()
        analyzer.ajouter_risque("R1", 0.2, 50000.0)
        analyzer.ajouter_risque("R2", 0.1, 100000.0)
        
        result = analyzer.analyser_scenarios()
        
        assert len(result.scenarios) > 0
        assert result.perte_maximale > 0
        assert result.probabilite_globale > 0

    def test_result_stored(self):
        analyzer = WorstCaseAnalyzer()
        analyzer.ajouter_risque("R1", 0.2, 50000.0)
        result = analyzer.analyser_scenarios()
        
        assert analyzer.result is not None
        assert analyzer.result == result

    def test_scenario_pire_existe(self):
        analyzer = WorstCaseAnalyzer()
        analyzer.ajouter_risque("R1", 0.2, 50000.0)
        analyzer.ajouter_risque("R2", 0.1, 100000.0)
        
        result = analyzer.analyser_scenarios()
        
        assert result.scenario_pire is not None

    def test_recommandations_generes(self):
        analyzer = WorstCaseAnalyzer()
        analyzer.ajouter_risque("R1", 0.2, 500000.0)
        
        result = analyzer.analyser_scenarios()
        
        assert len(result.recommandations) > 0
