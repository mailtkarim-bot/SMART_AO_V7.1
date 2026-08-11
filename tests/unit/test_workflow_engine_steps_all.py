"""
SMART_AO V7 - Test unitaire pour toutes les steps du workflow_engine
======================================================================
Tests unitaires qui exécutent le code de toutes les steps pour améliorer la couverture.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))


class TestBaseStep:
    """Tests pour BaseStep."""
    
    def test_base_step_import(self):
        """Test que BaseStep s'import correctement."""
        from app.engines.workflow_engine.steps.base_step import BaseStep
        assert BaseStep is not None


class TestAgentsStep:
    """Tests pour AgentsStep."""
    
    @pytest.fixture
    def step(self):
        from app.engines.workflow_engine.steps.agents_step import AgentsStep
        return AgentsStep()
    
    def test_initialization(self, step):
        """Test l'initialisation."""
        assert step.name == "agents_step"
        assert step.version == "1.0.0"
    
    @pytest.mark.asyncio
    async def test_execute_no_data(self, step):
        """Test execute sans données."""
        with patch('app.engines.workflow_engine.steps.agents_step.AgentRegistry'):
            result = await step.execute("mission_1", {})
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_rollback(self, step):
        """Test rollback."""
        result = await step.rollback("mission_1", {})
        assert result is True


class TestClassificationStep:
    """Tests pour ClassificationStep."""
    
    @pytest.fixture
    def step(self):
        from app.engines.workflow_engine.steps.classification_step import ClassificationStep
        return ClassificationStep()
    
    def test_initialization(self, step):
        """Test l'initialisation."""
        assert step.name == "classification_step"
    
    def test_evaluer_criticite_deadline(self, step):
        """Test _evaluer_criticite_deadline."""
        assert step._evaluer_criticite_deadline({"jours_restants": 1}) == "critique"
        assert step._evaluer_criticite_deadline({"jours_restants": 5}) == "majeur"
        assert step._evaluer_criticite_deadline({"jours_restants": 10}) == "mineur"
        assert step._evaluer_criticite_deadline({"jours_restants": 30}) == "information"
    
    def test_evaluer_criticite_penalite(self, step):
        """Test _evaluer_criticite_penalite."""
        assert step._evaluer_criticite_penalite({"montant_estime": 20000, "frequence": "ponctuelle"}) == "critique"
        assert step._evaluer_criticite_penalite({"montant_estime": 6000, "frequence": "hebdomadaire"}) == "majeur"
        assert step._evaluer_criticite_penalite({"montant_estime": 2000, "frequence": "ponctuelle"}) == "mineur"
        assert step._evaluer_criticite_penalite({"montant_estime": 500, "frequence": "ponctuelle"}) == "information"
    
    @pytest.mark.asyncio
    async def test_execute_empty(self, step):
        """Test execute avec données vides."""
        result = await step.execute("mission_1", {})
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_execute_with_data(self, step):
        """Test execute avec données."""
        context = {"extracted_data": {"deadlines": [{"jours_restants": 1}]}}
        result = await step.execute("mission_1", context)
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_rollback(self, step):
        """Test rollback."""
        result = await step.rollback("mission_1", {})
        assert result is True


class TestCompilationStep:
    """Tests pour CompilationStep."""
    
    @pytest.fixture
    def step(self):
        from app.engines.workflow_engine.steps.compilation_step import CompilationStep
        return CompilationStep()
    
    def test_initialization(self, step):
        """Test l'initialisation."""
        assert step.name == "compilation_step"
    
    def test_generate_summary(self, step):
        """Test _generate_summary."""
        agents_results = {
            "agent1": {"status": "success", "result": {"findings": [{"type": "test"}]}},
            "agent2": {"status": "error", "error": "Erreur"}
        }
        result = step._generate_summary(agents_results)
        assert result is not None
    
    def test_extract_alertes(self, step):
        """Test _extract_alertes."""
        analyse = {"findings": [{"type": "test", "criticite": "critique"}]}
        result = step._extract_alertes(analyse, "agent1")
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_execute(self, step):
        """Test execute."""
        context = {"agents_results": {"agent1": {"status": "success", "result": {"findings": []}}}}
        result = await step.execute("mission_1", context)
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_rollback(self, step):
        """Test rollback."""
        result = await step.rollback("mission_1", {})
        assert result is True








class TestRapportStep:
    """Tests pour RapportStep."""
    
    @pytest.fixture
    def step(self):
        from app.engines.workflow_engine.steps.rapport_step import RapportStep
        return RapportStep()
    
    def test_initialization(self, step):
        """Test l'initialisation."""
        assert step.name == "rapport_step"
    
    def test_generate_executive_summary(self, step):
        """Test _generate_executive_summary."""
        compiled_report = {"summary": {}, "analyses": {}, "recommandations": [], "alertes": []}
        result = step._generate_executive_summary(compiled_report)
        assert isinstance(result, dict)
    
    def test_calculate_risk_score(self, step):
        """Test _calculate_risk_score."""
        alertes = [{"criticite": "critique"}, {"criticite": "majeur"}]
        score = step._calculate_risk_score(alertes)
        assert isinstance(score, int)
    
    def test_get_risk_level(self, step):
        """Test _get_risk_level."""
        level = step._get_risk_level(50)
        assert isinstance(level, str)
    
    @pytest.mark.asyncio
    async def test_execute(self, step):
        """Test execute."""
        context = {
            "compilation_result": {
                "compiled_report": {"summary": {}, "analyses": {}, "recommandations": [], "alertes": []}
            },
            "mission_id": "mission_1"
        }
        result = await step.execute("mission_1", context)
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_rollback(self, step):
        """Test rollback."""
        result = await step.rollback("mission_1", {})
        assert result is True
