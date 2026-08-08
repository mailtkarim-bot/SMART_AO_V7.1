"""
SMART_AO V7 - test_registry_discovery.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Tests Registry Discovery
=======================================
Tests unitaires pour l'auto-discovery du registry.
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from app.engines.agent_runtime.registry import registry


class TestRegistryDiscovery:
    """Tests du registry et de l'auto-discovery."""
    
    def test_registry_initialization(self):
        """Test de l'initialisation du registry."""
        assert registry is not None
    
    def test_register_agent(self):
        """Test de l'enregistrement d'un agent."""
        from app.agents.base_agent import BaseAgent
        from typing import List
        from pydantic import Field
        
        class TestAgent(BaseAgent):
            @property
            def name(self) -> str:
                return "TestAgent"
            
            @property
            def capabilities(self) -> List[str]:
                return ["TEST_CAPABILITY"]
            
            async def execute(self, input):
                from app.agents.base_agent import AgentOutput
                return AgentOutput(
                    agent_name=self.name,
                    mission_id=input.mission_id,
                    capability="TEST_CAPABILITY",
                    confidence=1.0,
                    status="SUCCESS",
                    findings=[],
                    warnings=[],
                    execution_time_ms=10
                )
        
        agent = TestAgent()
        registry.register(["TEST_CAPABILITY"])(TestAgent)
        
        assert "TestAgent" in registry.get_agent_names()
    
    def test_get_agent(self):
        """Test de récupération d'un agent."""
        from app.agents.base_agent import BaseAgent
        from typing import List
        
        class TestAgent2(BaseAgent):
            @property
            def name(self) -> str:
                return "TestAgent2"
            
            @property
            def capabilities(self) -> List[str]:
                return ["TEST_CAPABILITY_2"]
            
            async def execute(self, input):
                from app.agents.base_agent import AgentOutput
                return AgentOutput(
                    agent_name=self.name,
                    mission_id=input.mission_id,
                    capability="TEST_CAPABILITY_2",
                    confidence=1.0,
                    status="SUCCESS",
                    findings=[],
                    warnings=[],
                    execution_time_ms=10
                )
        
        # Utiliser le decorator register
        registry.register(["TEST_CAPABILITY_2"])(TestAgent2)
        
        retrieved = registry.get_by_name("TestAgent2")
        assert retrieved is not None
        assert retrieved.name == "TestAgent2"
    
    def test_get_agent_names(self):
        """Test de récupération des noms d'agents."""
        names = registry.get_agent_names()
        assert isinstance(names, list)
        # S'assurer que la méthode retourne bien une liste
        assert isinstance(names, list)
    
    def test_auto_discover(self):
        """Test de l'auto-discovery."""
        # Importer tous les agents (déclenche l'enregistrement via @registry.register)
        try:
            import importlib
            agents_dir = project_root / "app" / "agents"
            
            for agent_file in agents_dir.glob("agent_*.py"):
                module_name = f"app.agents.{agent_file.stem}"
                try:
                    importlib.import_module(module_name)
                except Exception as e:
                    # Ignorer les erreurs d'import (agents non implémentés)
                    pass
        except:
            pass
        
        names = registry.get_agent_names()
        assert len(names) > 0
        print(f"✅ {len(names)} agents découverts par auto-discovery")
    
    def test_clear_registry(self):
        """Test de l'effacement du registry."""
        # Nettoyer d'abord
        registry.clear()
        # Vérifier que c'est vide
        assert len(registry.get_agent_names()) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
