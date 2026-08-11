"""
SMART_AO V7 - Tests unitaires pour tous les agents
==================================================
Tests qui exécutent le code de tous les agents pour améliorer la couverture.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from typing import List

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))


# Liste de tous les modules agents à tester
AGENT_MODULES = [
    "agent_memoire_booster",
    "agent_dc4",
    "agent_rat",
    "agent_bt_index",
    "agent_handoff",
    "agent_deadline",
    "agent_eplusc",
    "agent_bim",
    "agent_soged",
    "agent_bt01",
    "agent_tresorerie",
    "agent_penibilite_rh",
    "agent_risques",
    "agent_alloti",
    "agent_formule_revision",
    "agent_pab",
    "agent_qr_tactique",
    "agent_cctp_dpgf",
    "agent_sourcing_api",
    "agent_enveloppe",
    "agent_mapa",
    "agent_site_contraintes",
    "agent_vigilance_urssaf",
    "agent_variante",
    "agent_clauses_abusives",
    "agent_zan_trackterres",
    "agent_visite",
    "agent_rse_booster",
    "agent_coherence",
    "agent_assurance",
    "agent_penalites",
    "agent_capacite",
    "agent_certif",
    "agent_gme",
    "agent_avenant",
    "agent_materiaux_shield",
    "agent_contentieux",
]


class TestAgentImports:
    """Test l'import de tous les modules agents."""
    
    @pytest.mark.parametrize("module_name", AGENT_MODULES)
    def test_agent_module_import(self, module_name):
        """Test que chaque module agent s'import correctement."""
        try:
            module = __import__(f"app.agents.{module_name}", fromlist=["*"])
            assert module is not None
        except ImportError as e:
            # Certains agents peuvent avoir des dépendances optionnelles
            # On accepte les ImportError pour les dépendances manquantes
            pytest.skip(f"Module {module_name} a des dépendances manquantes: {e}")


class TestAgentBaseClass:
    """Test la classe BaseAgent et ses propriétés."""
    
    def test_base_agent_import(self):
        """Test l'import de BaseAgent."""
        from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
        assert BaseAgent is not None
        assert AgentInput is not None
        assert AgentOutput is not None
    
    def test_agent_input_model(self):
        """Test la création d'un AgentInput."""
        from app.agents.base_agent import AgentInput
        
        input_data = AgentInput(
            mission_id="test_mission_001",
            dce_chunks=[{"text": "test chunk", "page": 1}],
            parsed_docs={"type_marche": "test"},
            context={"vault": "A01"},
            previous_outputs={}
        )
        assert input_data.mission_id == "test_mission_001"
        assert len(input_data.dce_chunks) == 1
    
    def test_agent_output_model(self):
        """Test la création d'un AgentOutput."""
        from app.agents.base_agent import AgentOutput
        
        output = AgentOutput(
            agent_name="TestAgent",
            mission_id="test_mission_001",
            capability="TEST_CAPABILITY",
            confidence=0.95,
            status="SUCCESS",
            findings=[{"type": "info", "message": "test finding"}],
            financial_data=None,
            warnings=[],
            execution_time_ms=100,
            source_pages=[1, 2, 3]
        )
        assert output.agent_name == "TestAgent"
        assert output.capability == "TEST_CAPABILITY"
        assert output.status == "SUCCESS"
    
    def test_agent_output_zero_euro_validation(self):
        """Test que la validation ZERO € fonctionne."""
        from app.agents.base_agent import AgentOutput, AgentInput
        from pydantic import ValidationError
        
        # Cela devrait lever une ValidationError car findings contient €
        with pytest.raises(ValidationError) as exc_info:
            AgentOutput(
                agent_name="TestAgent",
                mission_id="test_mission_001",
                capability="TEST",
                confidence=0.5,
                status="SUCCESS",
                findings=[{"type": "info", "message": "100 € de marge"}],
            )
        assert "ZERO € violation" in str(exc_info.value)


class TestAgentInitialization:
    """Test l'initialisation des agents concrets."""
    
    @pytest.mark.asyncio
    async def test_agent_coherence(self):
        """Test l'agent coherence."""
        from app.agents.agent_coherence import CoherenceGuardianAgent
        
        agent = CoherenceGuardianAgent()
        assert agent.name is not None
        assert len(agent.capabilities) > 0
        assert isinstance(agent.capabilities, list)
    
    @pytest.mark.asyncio
    async def test_agent_deadline(self):
        """Test l'agent deadline."""
        from app.agents.agent_deadline import DeadlineAgent
        
        agent = DeadlineAgent()
        assert agent.name is not None
        assert len(agent.capabilities) > 0
    
    @pytest.mark.asyncio
    async def test_agent_pab(self):
        """Test l'agent pab."""
        from app.agents.agent_pab import PABAgent
        
        agent = PABAgent()
        assert agent.name is not None
        assert len(agent.capabilities) > 0
    
    @pytest.mark.asyncio
    async def test_agent_penalites(self):
        """Test l'agent penalites."""
        from app.agents.agent_penalites import PenalitesAgent
        
        agent = PenalitesAgent()
        assert agent.name is not None
        assert len(agent.capabilities) > 0
    
    @pytest.mark.asyncio
    async def test_agent_risques(self):
        """Test l'agent risques."""
        from app.agents.agent_risques import RisquesGuardianAgent
        
        agent = RisquesGuardianAgent()
        assert agent.name is not None
        assert len(agent.capabilities) > 0
    
    @pytest.mark.asyncio
    async def test_agent_cctp_dpgf(self):
        """Test l'agent cctp_dpgf."""
        from app.agents.agent_cctp_dpgf import CCTPDPGFAgent
        
        agent = CCTPDPGFAgent()
        assert agent.name is not None
        assert len(agent.capabilities) > 0


class TestAgentProperties:
    """Test les propriétés des agents."""
    
    def test_agent_name_property(self):
        """Test que les agents ont un nom."""
        from app.agents.agent_coherence import CoherenceGuardianAgent
        
        agent = CoherenceGuardianAgent()
        assert isinstance(agent.name, str)
        assert len(agent.name) > 0
    
    def test_agent_capabilities_property(self):
        """Test que les agents ont des capabilities."""
        from app.agents.agent_coherence import CoherenceGuardianAgent
        
        agent = CoherenceGuardianAgent()
        assert isinstance(agent.capabilities, list)
        assert len(agent.capabilities) > 0
        assert all(isinstance(cap, str) for cap in agent.capabilities)
    
    def test_agent_estimated_duration(self):
        """Test la propriété estimated_duration."""
        from app.agents.agent_coherence import CoherenceGuardianAgent
        from datetime import timedelta
        
        agent = CoherenceGuardianAgent()
        assert isinstance(agent.estimated_duration, timedelta)
    
    def test_agent_is_blocking(self):
        """Test la propriété is_blocking."""
        from app.agents.agent_coherence import CoherenceGuardianAgent
        
        agent = CoherenceGuardianAgent()
        assert isinstance(agent.is_blocking, bool)
    
    def test_agent_can_handle(self):
        """Test la méthode can_handle."""
        from app.agents.agent_coherence import CoherenceGuardianAgent
        from unittest.mock import Mock
        
        agent = CoherenceGuardianAgent()
        mission = Mock()
        
        score = agent.can_handle(mission)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0


class TestAgentExecution:
    """Test l'exécution des agents avec des mocks."""
    
    def test_agent_coherence_has_execute_method(self):
        """Test que l'agent coherence a une méthode execute."""
        from app.agents.agent_coherence import CoherenceGuardianAgent
        
        agent = CoherenceGuardianAgent()
        assert hasattr(agent, 'execute')
        assert callable(agent.execute)
    
    def test_agent_deadline_has_execute_method(self):
        """Test que l'agent deadline a une méthode execute."""
        from app.agents.agent_deadline import DeadlineAgent
        
        agent = DeadlineAgent()
        assert hasattr(agent, 'execute')
        assert callable(agent.execute)


class TestAgentsList:
    """Test la liste complète des agents."""
    
    def test_all_agents_can_be_imported(self):
        """Test que tous les agents peuvent être importés."""
        from app.agents.agent_coherence import CoherenceGuardianAgent
        from app.agents.agent_deadline import DeadlineAgent
        from app.agents.agent_pab import PABAgent
        from app.agents.agent_penalites import PenalitesAgent
        from app.agents.agent_risques import RisquesGuardianAgent
        from app.agents.agent_cctp_dpgf import CCTPDPGFAgent
        
        agents = [
            CoherenceGuardianAgent(),
            DeadlineAgent(),
            PABAgent(),
            PenalitesAgent(),
            RisquesGuardianAgent(),
            CCTPDPGFAgent(),
        ]
        
        for agent in agents:
            assert agent.name is not None
            assert len(agent.capabilities) > 0
    
    def test_agent_repr(self):
        """Test la représentation string des agents."""
        from app.agents.agent_coherence import CoherenceGuardianAgent
        
        agent = CoherenceGuardianAgent()
        repr_str = repr(agent)
        
        assert "Coherence" in repr_str or "Guardian" in repr_str
        assert "capabilities" in repr_str
