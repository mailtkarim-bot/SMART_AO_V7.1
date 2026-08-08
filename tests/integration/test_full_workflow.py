"""
SMART_AO V7 - test_full_workflow.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Tests d'Intégration Full Workflow
================================================
Tests d'intégration pour le workflow complet V7.

Source: PLAN_DE_CODAGE_PHASE_5_V7.md - Sprint 1 (Jour 3)
Cible: 5 tests Full Workflow
"""

import pytest
import sys
from pathlib import Path
from typing import List

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from app.engines.workflow_engine.workflow import WorkflowEngine, Workflow
from app.engines.workflow_engine.mission import Mission, MissionStatus, MissionStep, StepStatus
from app.engines.agent_runtime.registry import AgentRegistry, registry
from app.engines.event_bus.bus import EventBus
from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# Agent mock complet pour le full workflow
class FullWorkflowTestAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "FULL_WORKFLOW_TEST_AGENT"
    
    @property
    def capabilities(self) -> List[str]:
        return ["FULL_WORKFLOW_TEST"]
    
    async def execute(self, input: AgentInput) -> AgentOutput:
        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="FULL_WORKFLOW_TEST",
            confidence=1.0,
            status="SUCCESS",
            findings=[{"type": "test", "description": "Full workflow test"}],
            warnings=[],
            execution_time_ms=100,
            source_pages=[]
        )


class TestFullWorkflowIntegration:
    """Tests d'intégration pour le workflow complet."""
    
    def test_full_workflow_components_exist(self):
        """Test que tous les composants du full workflow existent."""
        # WorkflowEngine
        registry = AgentRegistry()
        event_bus = EventBus()
        workflow_engine = WorkflowEngine(registry=registry, event_bus=event_bus)
        assert workflow_engine is not None
        
        # Workflow
        mission = Mission(documents=["test.pdf"], context={}, created_by="test")
        workflow = Workflow(mission)
        assert workflow is not None
        assert len(workflow.steps) == 6
    
    def test_full_workflow_registry_integration(self):
        """Test que le registry est intégré dans le full workflow."""
        registry = AgentRegistry()
        registry.register(capabilities=["FULL_WORKFLOW_TEST"])(FullWorkflowTestAgent)
        
        # Vérifier que l'agent est enregistré
        all_agents = registry.get_all()
        assert len(all_agents) >= 1
        
        # Vérifier qu'on peut retrouver par capability
        agents = registry.find_by_capability("FULL_WORKFLOW_TEST")
        assert len(agents) >= 1
    
    def test_full_workflow_event_bus_integration(self):
        """Test que l'EventBus est intégré dans le full workflow."""
        event_bus = EventBus()
        
        # Vérifier qu'on peut publier et s'abonner
        received_events = []
        
        def test_subscriber(event):
            received_events.append(event)
        
        from app.engines.event_bus.models import EventType
        event_bus.subscribe(EventType.MISSION_CREATED, test_subscriber)
        
        # Publier un événement
        from app.engines.event_bus.models import MissionCreated
        event = MissionCreated(
            mission_id="TEST_MISSION",
            project_id="TEST_PROJ",
            mission_type="ANALYSE_DCE",
            context={}
        )
        event_bus.publish(event)
        
        assert len(received_events) == 1
    
    def test_full_workflow_api_integration(self):
        """Test que l'API est intégrée avec le full workflow."""
        # Tester l'endpoint health qui utilise plusieurs composants
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_full_workflow_mission_lifecycle(self):
        """Test le cycle de vie d'une mission dans le full workflow."""
        # Créer une mission
        mission = Mission(
            documents=["DCE_001.pdf"],
            context={"project_id": "PROJ_001"},
            created_by="test_user",
            status=MissionStatus.PENDING
        )
        
        # Créer un workflow
        workflow = Workflow(mission)
        
        # Vérifier le workflow
        assert workflow.mission_id == mission.id
        assert len(workflow.steps) == 6
        
        # Vérifier l'étape courante
        current_step = workflow.get_current_step()
        assert current_step is not None
        assert current_step.step_number == 0
        
        # Avancer
        workflow.advance()
        assert workflow.get_current_step().step_number == 1
