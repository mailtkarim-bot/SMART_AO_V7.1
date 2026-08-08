"""
SMART_AO V7 - test_engines_workflow.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Tests d'Intégration Workflow Engine
===================================================
Tests d'intégration pour le Workflow Engine V7.
Valide les interactions entre WorkflowEngine, Mission, EventBus et AgentRegistry.

Source: PLAN_DE_CODAGE_PHASE_5_V7.md - Sprint 1 (Jour 2)
Cible: 3 tests WorkflowEngine
"""

import pytest
import sys
from pathlib import Path
from typing import List

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from app.engines.workflow_engine.workflow import WorkflowEngine, Workflow
from app.engines.workflow_engine.mission import Mission, MissionStatus, MissionStep, StepStatus
from app.engines.agent_runtime.registry import AgentRegistry
from app.engines.event_bus.bus import EventBus
from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput


# Agents mock complets
class MockParserAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "MOCK_PARSER"
    
    @property
    def capabilities(self) -> List[str]:
        return ["PARSER"]
    
    async def execute(self, input: AgentInput) -> AgentOutput:
        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="PARSER",
            confidence=1.0,
            status="SUCCESS",
            findings=[],
            warnings=[],
            execution_time_ms=100,
            source_pages=[]
        )


class MockExtractorAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "MOCK_EXTRACTOR"
    
    @property
    def capabilities(self) -> List[str]:
        return ["EXTRACTION"]
    
    async def execute(self, input: AgentInput) -> AgentOutput:
        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="EXTRACTION",
            confidence=1.0,
            status="SUCCESS",
            findings=[],
            warnings=[],
            execution_time_ms=100,
            source_pages=[]
        )


# Fixtures
@pytest.fixture
def registry():
    """Crée un AgentRegistry avec des agents mock."""
    registry = AgentRegistry()
    registry.register(capabilities=["PARSER"])(MockParserAgent)
    registry.register(capabilities=["EXTRACTION"])(MockExtractorAgent)
    return registry


@pytest.fixture
def event_bus():
    """Crée un EventBus pour les tests."""
    return EventBus()


@pytest.fixture
def workflow_engine(registry, event_bus):
    """Crée un WorkflowEngine avec les dépendances."""
    return WorkflowEngine(registry=registry, event_bus=event_bus)


@pytest.fixture
def sample_mission():
    """Crée une mission d'exemple."""
    return Mission(
        documents=["DCE_001.pdf", "DCE_002.pdf"],
        context={
            "project_id": "PROJ_001",
            "mission_type": "ANALYSE_DCE",
            "priority": "HAUTE"
        },
        created_by="test_user",
        status=MissionStatus.PENDING
    )


# Tests WorkflowEngine (3 tests)
class TestWorkflowEngineIntegration:
    """Tests d'intégration pour WorkflowEngine."""
    
    def test_workflow_engine_creates_workflow(self, workflow_engine: WorkflowEngine, sample_mission: Mission):
        """Test que WorkflowEngine peut créer un workflow pour une mission."""
        # Créer un workflow directement
        workflow = Workflow(sample_mission)
        
        assert workflow is not None
        assert workflow.mission_id == sample_mission.id
        assert len(workflow.steps) == 6  # 6 étapes canoniques V7
        assert workflow.status == "PENDING"

    def test_workflow_engine_workflow_steps(self, workflow_engine: WorkflowEngine, sample_mission: Mission):
        """Test que Workflow a les 6 étapes canoniques V7."""
        # Créer un workflow
        workflow = Workflow(sample_mission)

        # Vérifier les étapes
        assert len(workflow.steps) == 6

        # Vérifier les noms des étapes
        step_names = [step.step_name for step in workflow.steps]
        expected_steps = [
            "parser_step", "extraction_step", "classification_step",
            "agents_step", "compilation_step", "rapport_step",
        ]
        assert step_names == expected_steps
    
    def test_workflow_current_step(self, workflow_engine: WorkflowEngine, sample_mission: Mission):
        """Test que Workflow gère correctement l'étape courante."""
        # Créer un workflow
        workflow = Workflow(sample_mission)
        
        # Vérifier l'étape courante initiale
        current_step = workflow.get_current_step()
        assert current_step is not None
        assert current_step.step_number == 0
        
        # Avancer à l'étape suivante
        workflow.advance()
        current_step = workflow.get_current_step()
        assert current_step.step_number == 1
