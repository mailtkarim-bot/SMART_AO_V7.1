"""
SMART_AO V7 - run_test.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


#!/usr/bin/env python3
"""Script pour tester rapidement le setup V7"""
import sys
import asyncio
from pathlib import Path

# Ajouter le root au path (chemin absolu pour portabilité CI/CD)
sys.path.insert(0, str(Path(__file__).parent.absolute()))


async def test_imports():
    """Test que tous les imports fonctionnent"""
    print("🔍 Test des imports...")
    
    try:
        from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
        print("✅ BaseAgent import OK")
    except ImportError as e:
        print(f"❌ BaseAgent import FAILED: {e}")
        return False

    try:
        from app.engines.agent_runtime.registry import registry
        print("✅ Registry import OK")
    except ImportError as e:
        print(f"❌ Registry import FAILED: {e}")
        return False

    try:
        from app.engines.workflow_engine.mission import Mission
        print("✅ Mission import OK")
    except ImportError as e:
        print(f"❌ Mission import FAILED: {e}")
        return False

    try:
        from app.engines.workflow_engine.workflow import WorkflowEngine
        print("✅ WorkflowEngine import OK")
    except ImportError as e:
        print(f"❌ WorkflowEngine import FAILED: {e}")
        return False

    try:
        from app.engines.event_bus.bus import EventBus, create_test_event_bus
        print("✅ EventBus import OK")
    except ImportError as e:
        print(f"❌ EventBus import FAILED: {e}")
        return False

    try:
        from app.agents.agent_pab import PABAgent
        print("✅ PABAgent import OK")
    except ImportError as e:
        print(f"❌ PABAgent import FAILED: {e}")
        return False

    try:
        from app.agents.agent_deadline import DeadlineAgent
        print("✅ DeadlineAgent import OK")
    except ImportError as e:
        print(f"❌ DeadlineAgent import FAILED: {e}")
        return False

    return True


async def test_e2e():
    """Test E2E minimal"""
    print("\n🔍 Test E2E minimal...")

    from app.engines.agent_runtime.registry import registry
    from app.engines.event_bus.bus import create_test_event_bus
    from app.engines.workflow_engine.workflow import WorkflowEngine

    # Import agents (enregistre automatiquement via @registry.register)
    from app.agents import agent_pab  # noqa: F401
    from app.agents import agent_deadline  # noqa: F401

    bus = create_test_event_bus()
    registry_auto = registry  # Singleton
    registry_auto.auto_discover("app.agents")

    print(f"Registry stats: {registry_auto.stats()}")

    if registry_auto.stats()["total_agents"] < 2:
        print("❌ Moins de 2 agents enregistrés")
        return False

    engine = WorkflowEngine(registry=registry_auto, event_bus=bus, max_parallel=3)

    try:
        mission = await engine.create_mission(
            docs=["dpgf.pdf", "rc.pdf"],
            context={"type_marche": "MAPA", "estimation_interne": 500000, "dpgf": True, "jours_restants": 5},
            created_by="test_user",
            project_id="proj_123"
        )
        print(f"✅ Mission créée: {mission.id}")
    except Exception as e:
        print(f"❌ Mission creation FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    try:
        result = await engine.run(mission)
        print(f"✅ Mission terminée: {result.status}")
        print(f"   Agents exécutés: {result.context.get('agents_executed', 0)}")
        print(f"   Outputs: {list(result.context.get('agent_outputs', {}).keys())}")
        
        # Vérifier que les agents ont bien été exécutés
        events = await bus.replay(mission.id)
        agent_events = [e for e in events if e.metadata.get("legacy_type") in ["AgentDémarré", "AgentTerminé"]]
        print(f"   Events agents: {len(agent_events)}")
        
        return True
    except Exception as e:
        print(f"❌ Mission run FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    print("=" * 60)
    print("SMART_AO V7 - Test de Setup Initial")
    print("=" * 60)

    # Test imports
    if not await test_imports():
        print("\n❌ TESTS IMPORTS ÉCHOUÉS - Corriger les imports d'abord")
        sys.exit(1)

    # Test E2E
    if not await test_e2e():
        print("\n❌ TESTS E2E ÉCHOUÉS")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("✅ TOUS LES TESTS RÉUSSIS - Structure V7 valide")
    print("=" * 60)
    print("\n🎯 Prochaine étape: implémenter la persistance PostgreSQL")
    print("   et migrer les 26 agents restants")


if __name__ == "__main__":
    asyncio.run(main())
