"""
SMART_AO V7 - test_engines_agent_runtime.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Tests d'Intégration Agent Registry
==================================================
Tests d'intégration pour l'Agent Registry V7.
Valide les interactions entre AgentRegistry et les agents.

Source: PLAN_DE_CODAGE_PHASE_5_V7.md - Sprint 1 (Jour 2)
Cible: 3 tests AgentRegistry (remplace AgentRuntime)
"""

import pytest
import sys
from pathlib import Path
from typing import List
from datetime import timedelta

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from app.engines.agent_runtime.registry import AgentRegistry, registry
from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from unittest.mock import Mock, AsyncMock, MagicMock
from datetime import datetime, timezone
import asyncio


# Fixtures
@pytest.fixture
def test_registry():
    """Crée un AgentRegistry pour les tests."""
    return AgentRegistry()


class MockTestAgent(BaseAgent):
    """Agent mock pour les tests."""
    @property
    def name(self) -> str:
        return "TEST_AGENT"
    
    @property
    def capabilities(self) -> List[str]:
        return ["TEST_CAP"]
    
    async def execute(self, input: AgentInput) -> AgentOutput:
        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="TEST_CAP",
            confidence=1.0,
            status="SUCCESS",
            findings=[],
            warnings=[],
            execution_time_ms=100,
            source_pages=[]
        )


# Tests AgentRegistry (3 tests)
class TestAgentRegistryIntegration:
    """Tests d'intégration pour AgentRegistry."""
    
    def test_registry_creates_empty(self, test_registry: AgentRegistry):
        """Test qu'un AgentRegistry se crée vide."""
        assert test_registry is not None
        assert len(test_registry.get_all()) == 0
    
    def test_registry_uses_global_instance(self):
        """Test que le registry global est accessible."""
        assert registry is not None
        assert isinstance(registry, AgentRegistry)
    
    def test_registry_registers_and_retrieves_agents(self, test_registry: AgentRegistry):
        """Test que AgentRegistry peut enregistrer et retrouver des agents."""
        # Créer un agent mock
        test_agent = MockTestAgent()
        
        # L'enregistrer via le décorateur (simulation)
        # Le décorateur appeler registry.register avec des capabilities
        test_registry.register(capabilities=["TEST_CAP"])(MockTestAgent)
        
        # Vérifier que l'agent est dans le registry
        all_agents = test_registry.get_all()
        assert len(all_agents) >= 1
        
        # Vérifier qu'on peut retrouver par nom
        agent_by_name = test_registry.get_by_name("TEST_AGENT")
        assert agent_by_name is not None
        assert agent_by_name.name == "TEST_AGENT"
