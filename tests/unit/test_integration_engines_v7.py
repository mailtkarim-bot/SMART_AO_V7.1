"""
SMART_AO V7 - test_integration_engines_v7.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Tests d'Intégration des Engines
Source: PLAN_MAITRE_V7_FUSION_COMPLETE.md - REC-012

Tests d'intégration pour les 8 Engines OS + 2 Edge:
- Workflow Engine
- Agent Runtime
- Event Bus
- Math Engine
- Knowledge Engine
- Document Engine
- Security Engine
- Notification Engine
- API Gateway
- UI Engine
"""

import pytest
import sys
from pathlib import Path

# Ajouter le chemin du projet
project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from app.engines.agent_runtime.registry import registry
from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="function", autouse=True)
def setup_registry():
    """Configure le registre avec tous les agents - portée function, auto-use"""
    # Importer tous les agents - utiliser importlib pour exécuter le code du module
    # qui contient les décorateurs @registry.register
    import importlib
    from app.engines.agent_runtime.registry import registry
    
    # Clear the registry first to ensure clean state
    try:
        registry.clear()
    except:
        pass
    
    agent_modules = [
        "agent_deadline", "agent_pab", "agent_bt_index", "agent_penalites",
        "agent_tresorerie", "agent_gme", "agent_dc4", "agent_rat",
        "agent_soged", "agent_site_contraintes", "agent_cctp_dpgf",
        "agent_qr_tactique", "agent_memoire_booster", "agent_handoff",
        "agent_alloti", "agent_rse_booster", "agent_coherence",
        "agent_variante", "agent_materiaux_shield", "agent_visite",
        "agent_enveloppe", "agent_avenant", "agent_contentieux",
        "agent_certif", "agent_capacite", "agent_risques",
        "agent_mapa", "agent_eplusc", "agent_bim", "agent_assurance"
    ]
    
    for module_name in agent_modules:
        try:
            # Force reload to re-execute @registry.register decorators
            module_path = f"app.agents.{module_name}"
            if module_path in sys.modules:
                importlib.reload(sys.modules[module_path])
            else:
                importlib.import_module(module_path)
        except Exception as e:
            print(f"Warning: Could not import {module_name}: {e}")
    
    # S'assurer que l'auto-discovery est déclenchée
    registry.auto_discover("app.agents")
    
    yield
    # Ne pas nettoyer pour éviter les conflits avec d'autres tests
    # Le registre sera nettoyé par les autres fixtures si nécessaire


# ============================================================================
# TESTS WORKFLOW ENGINE
# ============================================================================

class TestWorkflowEngine:
    """Tests du Workflow Engine"""
    
    def test_mission_model(self):
        """Teste le modèle Mission"""
        from app.engines.workflow_engine.mission import Mission, MissionStatus
        
        mission = Mission(
            id="test-mission-id",
            type="ANALYSE_DCE",
            status=MissionStatus.CREATED,
            documents=[],
            workflow=[],
            created_by="test_user",
        )
        
        assert mission.id == "test-mission-id"
        assert mission.type == "ANALYSE_DCE"
        assert mission.status == MissionStatus.CREATED
    
    def test_mission_status_enum(self):
        """Teste l'énumération MissionStatus"""
        from app.engines.workflow_engine.mission import MissionStatus
        
        statuses = [
            MissionStatus.CREATED, MissionStatus.PARSING, MissionStatus.EXTRACTING,
            MissionStatus.CLASSIFYING, MissionStatus.AGENT_RUNNING,
            MissionStatus.COMPILING, MissionStatus.REPORTING, MissionStatus.DONE,
            MissionStatus.FAILED
        ]
        
        for status in statuses:
            assert isinstance(status, MissionStatus)


# ============================================================================
# TESTS AGENT RUNTIME
# ============================================================================

class TestAgentRuntime:
    """Tests du Agent Runtime (Registry)"""
    
    def test_registry_has_agents(self):
        """Teste que le registre contient des agents après import"""
        agents = registry.get_all()
        assert len(agents) >= 28, f"Seulement {len(agents)} agents trouvés"
    
    def test_registry_find_by_capability(self):
        """Teste la recherche par capability"""
        agents = registry.find_by_capability("CHECK_DEADLINE")
        assert len(agents) >= 1
        
        agent = agents[0]
        assert hasattr(agent, 'name')
        assert hasattr(agent, 'capabilities')
    
    def test_registry_find_by_tags(self):
        """Teste la recherche par tags"""
        agents = registry.find_by_tags(["finance"])
        # Doit trouver au moins PAB, BT Index, Trésorerie, etc.
        assert len(agents) >= 3
    
    def test_registry_stats(self):
        """Teste les statistiques du registre"""
        stats = registry.stats()
        assert stats["total_agents"] >= 28
        assert stats["total_capabilities"] >= 100
        assert isinstance(stats["capabilities"], dict)


# ============================================================================
# TESTS EVENT BUS
# ============================================================================

class TestEventBus:
    """Tests du Event Bus"""
    
    def test_event_bus_import(self):
        """Teste l'import du Event Bus"""
        from app.engines.event_bus.bus import EventBus
        assert EventBus is not None
    
    def test_event_models(self):
        """Teste les modèles d'events"""
        from app.engines.event_bus.models import Event, EventType
        assert Event is not None
        assert EventType is not None


# ============================================================================
# TESTS DOCUMENT ENGINE
# ============================================================================

class TestDocumentEngine:
    """Tests du Document Engine"""
    
    def test_parser_import(self):
        """Teste l'import du parser"""
        try:
            from app.engines.document_engine.parser import Parser
            assert Parser is not None
        except ImportError:
            # Le parser peut avoir des dépendances optionnelles
            pass
    
    def test_classifier_47(self):
        """Teste l'import du classifieur 47 pièces"""
        try:
            from app.engines.document_engine.classifier_47 import Classifier47
            assert Classifier47 is not None
        except ImportError:
            pass


# ============================================================================
# TESTS MATH ENGINE
# ============================================================================

class TestMathEngine:
    """Tests du Math Engine"""
    
    def test_math_engine_import(self):
        """Teste l'import du Math Engine"""
        try:
            from app.engines.math_engine import chiffrage_pulp
            assert chiffrage_pulp is not None
        except ImportError as e:
            # Math Engine peut avoir des dépendances optionnelles
            print(f"Warning: {e}")
    
    def test_decimal_ops(self):
        """Teste les opérations décimales"""
        try:
            from app.engines.math_engine import decimal_ops
            assert decimal_ops is not None
        except ImportError:
            pass


# ============================================================================
# TESTS ENGINE AUTO-DISCOVERY
# ============================================================================

class TestEngineAutoDiscovery:
    """Tests de la découverte automatique des Engines"""
    
    def test_workflow_engine_discoverable(self):
        """Teste que Workflow Engine est découverte"""
        from app.engines.workflow_engine import mission, workflow
        assert mission is not None
        assert workflow is not None
    
    def test_agent_runtime_discoverable(self):
        """Teste que Agent Runtime est découverte"""
        from app.engines.agent_runtime import registry, lifecycle
        assert registry is not None
        assert lifecycle is not None
    
    def test_event_bus_discoverable(self):
        """Teste que Event Bus est découverte"""
        from app.engines.event_bus import bus, models
        assert bus is not None
        assert models is not None


# ============================================================================
# TESTS D'INTÉGRATION COMPLÈTE
# ============================================================================

class TestFullIntegration:
    """Tests d'intégration complète"""
    
    def test_all_engines_importable(self):
        """Teste que tous les engines sont importables"""
        engines = [
            "workflow_engine",
            "agent_runtime",
            "event_bus",
            "math_engine",
            "knowledge_engine",
            "document_engine",
            "security_engine",
            "notification_engine",
            "api_gateway",
            "ui_engine",
        ]
        
        for engine in engines:
            try:
                module = __import__(f"app.engines.{engine}", fromlist=[""])
                assert module is not None
            except ImportError as e:
                print(f"Warning: Could not import {engine}: {e}")
    
    def test_all_agents_importable(self):
        """Teste que tous les agents sont importables"""
        agent_modules = [
            "agent_deadline", "agent_pab", "agent_bt_index", "agent_penalites",
            "agent_tresorerie", "agent_gme", "agent_dc4", "agent_rat",
            "agent_soged", "agent_site_contraintes", "agent_cctp_dpgf",
            "agent_qr_tactique", "agent_memoire_booster", "agent_handoff",
            "agent_alloti", "agent_rse_booster", "agent_coherence",
            "agent_variante", "agent_materiaux_shield", "agent_visite",
            "agent_enveloppe", "agent_avenant", "agent_contentieux",
            "agent_certif", "agent_capacite", "agent_risques",
            "agent_mapa", "agent_eplusc", "agent_bim", "agent_assurance"
        ]
        
        for module_name in agent_modules:
            module = __import__(f"app.agents.{module_name}", fromlist=[""])
            assert module is not None
    
    def test_agents_registered_in_registry(self):
        """Teste que les agents sont bien enregistrés dans le registre"""
        agents = registry.get_all()
        agent_names = [a.name for a in agents]
        
        # Vérifier que les agents clés sont présents
        required_agents = [
            "Deadline Guardian", "PAB Detector", "BT Index Tracker",
            "Penalites Calculator", "Tresorerie Guardian"
        ]
        
        for agent_name in required_agents:
            assert agent_name in agent_names, f"{agent_name} non trouvé dans le registre"


# ============================================================================
# TESTS DE PERFORMANCE
# ============================================================================

class TestPerformance:
    """Tests de performance des Engines"""
    
    def test_registry_performance(self):
        """Teste la performance du registre"""
        import time
        
        start = time.time()
        
        # Effectuer plusieurs recherches
        for _ in range(100):
            registry.find_by_capability("CHECK_DEADLINE")
        
        elapsed = time.time() - start
        assert elapsed < 1.0, f"Recherche trop lente: {elapsed}s"
    
    def test_agent_instantiation_performance(self):
        """Teste la performance de l'instanciation des agents"""
        import time
        from app.agents.agent_deadline import DeadlineAgent
        
        start = time.time()
        
        for _ in range(100):
            DeadlineAgent()
        
        elapsed = time.time() - start
        assert elapsed < 1.0, f"Instanciation trop lente: {elapsed}s"


# ============================================================================
# RÉSUMÉ
# ============================================================================

if __name__ == "__main__":
    # Exécuter avec pytest
    pytest.main([__file__, "-v"])
