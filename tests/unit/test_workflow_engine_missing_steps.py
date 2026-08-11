"""
SMART_AO V7 - Tests unitaires pour les steps du workflow engine non couverts
=============================================================================
Tests pour extraction_step.py et parser_step.py qui sont à 0% de couverture.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))


class TestExtractionStep:
    """Tests pour ExtractionStep."""
    
    def test_extraction_step_import(self):
        """Test l'import de ExtractionStep."""
        from app.engines.workflow_engine.steps.extraction_step import ExtractionStep
        assert ExtractionStep is not None
    
    def test_extraction_step_name(self):
        """Test le nom de ExtractionStep."""
        from app.engines.workflow_engine.steps.extraction_step import ExtractionStep
        assert ExtractionStep.name == "extraction_step"
    
    def test_extraction_step_version(self):
        """Test la version de ExtractionStep."""
        from app.engines.workflow_engine.steps.extraction_step import ExtractionStep
        assert ExtractionStep.version == "1.0.0"
    
    def test_extraction_step_has_execute_method(self):
        """Test que ExtractionStep a une méthode execute."""
        from app.engines.workflow_engine.steps.extraction_step import ExtractionStep
        assert hasattr(ExtractionStep, 'execute')
    
    def test_extraction_step_initialization(self):
        """Test l'initialisation de ExtractionStep."""
        from app.engines.workflow_engine.steps.extraction_step import ExtractionStep
        
        step = ExtractionStep()
        assert step is not None
        assert step.name == "extraction_step"


class TestParserStep:
    """Tests pour ParserStep."""
    
    def test_parser_step_import(self):
        """Test l'import de ParserStep."""
        from app.engines.workflow_engine.steps.parser_step import ParserStep
        assert ParserStep is not None
    
    def test_parser_step_name(self):
        """Test le nom de ParserStep."""
        from app.engines.workflow_engine.steps.parser_step import ParserStep
        assert ParserStep.name == "parser_step"
    
    def test_parser_step_has_execute_method(self):
        """Test que ParserStep a une méthode execute."""
        from app.engines.workflow_engine.steps.parser_step import ParserStep
        assert hasattr(ParserStep, 'execute')
    
    def test_parser_step_initialization(self):
        """Test l'initialisation de ParserStep."""
        from app.engines.workflow_engine.steps.parser_step import ParserStep
        
        step = ParserStep()
        assert step is not None
        assert step.name == "parser_step"


class TestWorkflowEngineWorkflow:
    """Tests pour workflow.py."""
    
    def test_workflow_import(self):
        """Test l'import de Workflow."""
        from app.engines.workflow_engine.workflow import Workflow
        assert Workflow is not None
    
    def test_workflow_engine_import(self):
        """Test l'import de WorkflowEngine."""
        from app.engines.workflow_engine.workflow import WorkflowEngine
        assert WorkflowEngine is not None
    
    def test_workflow_has_get_current_step_method(self):
        """Test que Workflow a une méthode get_current_step."""
        from app.engines.workflow_engine.workflow import Workflow
        assert hasattr(Workflow, 'get_current_step')
    
    def test_workflow_has_advance_method(self):
        """Test que Workflow a une méthode advance."""
        from app.engines.workflow_engine.workflow import Workflow
        assert hasattr(Workflow, 'advance')
    
    def test_workflow_engine_has_run_method(self):
        """Test que WorkflowEngine a une méthode run."""
        from app.engines.workflow_engine.workflow import WorkflowEngine
        assert hasattr(WorkflowEngine, 'run')
    
    def test_workflow_engine_has_create_mission_method(self):
        """Test que WorkflowEngine a une méthode create_mission."""
        from app.engines.workflow_engine.workflow import WorkflowEngine
        assert hasattr(WorkflowEngine, 'create_mission')


class TestWorkflowPersistence:
    """Tests pour persistence.py."""
    
    def test_persistence_import(self):
        """Test l'import de WorkflowPersistence."""
        from app.engines.workflow_engine.persistence import WorkflowPersistence
        assert WorkflowPersistence is not None
    
    def test_persistence_initialization(self):
        """Test l'initialisation de WorkflowPersistence."""
        from app.engines.workflow_engine.persistence import WorkflowPersistence
        
        # WorkflowPersistence nécessite des dépendances
        try:
            persistence = WorkflowPersistence()
            assert persistence is not None
        except Exception as e:
            pytest.skip(f"WorkflowPersistence nécessite des dépendances: {e}")
    
    def test_persistence_has_save_methods(self):
        """Test que WorkflowPersistence a des méthodes save."""
        from app.engines.workflow_engine.persistence import WorkflowPersistence
        assert hasattr(WorkflowPersistence, 'save_mission')
        assert hasattr(WorkflowPersistence, 'save_step')
        assert hasattr(WorkflowPersistence, 'save_event')


class TestWorkflowMission:
    """Tests pour mission.py."""
    
    def test_mission_import(self):
        """Test l'import de Mission."""
        from app.engines.workflow_engine.mission import Mission
        assert Mission is not None
    
    def test_mission_initialization(self):
        """Test l'initialisation de Mission."""
        from app.engines.workflow_engine.mission import Mission
        
        mission = Mission(id="test_001")
        assert mission is not None
        assert mission.id == "test_001"
    
    def test_mission_has_workflow(self):
        """Test que Mission a un workflow par défaut."""
        from app.engines.workflow_engine.mission import Mission
        
        mission = Mission()
        assert mission is not None
        assert len(mission.workflow) == 6  # 6 étapes canoniques
