"""
SMART_AO V7 - Test unitaire pour PenibiliteRHAgent
===============================================
Tests unitaires de base pour l'agent agent_penibilite_rh.
Généré automatiquement par generate_agent_tests.py
"""

import pytest
from unittest.mock import MagicMock

from app.agents.agent_penibilite_rh import PenibiliteRHAgent


class TestPenibiliteRHAgent:
    """Tests pour l'agent PenibiliteRHAgent."""

    def test_module_import(self):
        """Test que le module s'import correctement."""
        assert PenibiliteRHAgent is not None

    def test_agent_class_exists(self):
        """Test que la classe PenibiliteRHAgent existe."""
        agent = PenibiliteRHAgent()
        assert agent is not None
        assert isinstance(agent, PenibiliteRHAgent)

    def test_agent_name(self):
        """Test que l'agent a un nom."""
        agent = PenibiliteRHAgent()
        assert hasattr(agent, "name")
        assert agent.name is not None
        assert isinstance(agent.name, str)

    def test_agent_capabilities(self):
        """Test que l'agent a des capacités définies."""
        agent = PenibiliteRHAgent()
        assert hasattr(agent, "capabilities")
        assert agent.capabilities is not None
        assert isinstance(agent.capabilities, list)
        assert len(agent.capabilities) > 0

    def test_agent_tags(self):
        """Test que l'agent a des tags."""
        agent = PenibiliteRHAgent()
        assert hasattr(agent, "tags")
        assert agent.tags is not None
        assert isinstance(agent.tags, list)

    def test_agent_estimated_duration(self):
        """Test que l'agent a une durée estimée."""
        agent = PenibiliteRHAgent()
        assert hasattr(agent, "estimated_duration")
        assert agent.estimated_duration is not None

    def test_agent_is_blocking(self):
        """Test que l'agent a un attribut is_blocking."""
        agent = PenibiliteRHAgent()
        assert hasattr(agent, "is_blocking")
        assert isinstance(agent.is_blocking, bool)

    def test_can_handle_method_exists(self):
        """Test que la méthode can_handle existe."""
        agent = PenibiliteRHAgent()
        assert hasattr(agent, "can_handle")
        assert callable(agent.can_handle)

    def test_can_handle_with_mock_mission(self):
        """Test la méthode can_handle avec une mission mock."""
        agent = PenibiliteRHAgent()
        
        # Créer une mission mock
        mock_mission = MagicMock()
        mock_mission.has_document_type.return_value = False
        mock_mission.context = {}
        
        # Appeler can_handle
        score = agent.can_handle(mock_mission)
        
        # Vérifier que ça retourne un float entre 0 et 1
        assert isinstance(score, (int, float))
        assert 0 <= score <= 1

    def test_can_handle_with_empty_context(self):
        """Test can_handle avec un contexte vide."""
        agent = PenibiliteRHAgent()
        
        mock_mission = MagicMock()
        mock_mission.has_document_type.return_value = False
        mock_mission.context = {}
        
        score = agent.can_handle(mock_mission)
        
        assert isinstance(score, (int, float))
        assert 0 <= score <= 1

    def test_agent_attributes(self):
        """Test les attributs standard de l'agent."""
        agent = PenibiliteRHAgent()
        
        # Vérifier les attributs standard
        assert hasattr(agent, "name")
        assert hasattr(agent, "capabilities")
        assert hasattr(agent, "tags")
        assert hasattr(agent, "estimated_duration")
        assert hasattr(agent, "is_blocking")
        assert hasattr(agent, "can_handle")
        assert hasattr(agent, "execute")


class TestPenibiliteRHAgentEdgeCases:
    """Tests pour les cas limites."""

    def test_agent_instantiation(self):
        """Test l'instantiation de l'agent."""
        agent = PenibiliteRHAgent()
        assert agent is not None

    def test_agent_multiple_instances(self):
        """Test la création de multiples instances."""
        agent1 = PenibiliteRHAgent()
        agent2 = PenibiliteRHAgent()
        
        # Ce sont des instances différentes
        assert agent1 is not agent2

    def test_agent_capabilities_not_empty(self):
        """Test que les capacités ne sont pas vides."""
        agent = PenibiliteRHAgent()
        assert len(agent.capabilities) > 0

    def test_agent_tags_not_empty(self):
        """Test que les tags ne sont pas vides."""
        agent = PenibiliteRHAgent()
        assert len(agent.tags) > 0

    def test_agent_name_not_empty(self):
        """Test que le nom n'est pas vide."""
        agent = PenibiliteRHAgent()
        assert len(agent.name) > 0
