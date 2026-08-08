"""
SMART_AO V7 - test_v7_e2e.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
Test E2E V7 - Mission #254 bout en bout avec 3 agents
Source: ARCHITECTURE_V7_ENGINE.md §758
"""
import asyncio
import sys
from pathlib import Path

# Ajouter le root au path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.engines.agent_runtime.registry import registry
from app.engines.event_bus.bus import create_test_event_bus
from app.engines.workflow_engine.workflow import WorkflowEngine

# Import agents DIRECTEMENT (pas via app.agents package __init__)
# pour éviter les circular imports
from app.agents.agent_pab import PABAgent  # noqa: F401
from app.agents.agent_deadline import DeadlineAgent  # noqa: F401


async def test_mission_e2e():
    """Test complet d'une mission avec workflow 6 steps"""
    bus = create_test_event_bus()
    registry.auto_discover()
    
    print(f"\n📊 Registry stats: {registry.stats()}")
    assert registry.stats()["total_agents"] >= 2, "Moins de 2 agents enregistrés"

    engine = WorkflowEngine(registry=registry, event_bus=bus, max_parallel=3)

    # Créer mission
    mission = await engine.create_mission(
        docs=["dpgf.pdf", "rc.pdf", "cctp.pdf"],
        context={
            "type_marche": "MAPA",
            "estimation_interne": 500000,
            "dpgf": True,
            "jours_restants": 5,
            "prix_moyen_marche": 600000
        },
        created_by="test_user",
        project_id="proj_123"
    )
    
    print(f"✅ Mission créée: {mission.id}")
    assert mission.id.startswith("mission_"), "ID mission invalide"
    assert len(mission.workflow) == 6, "Workflow doit avoir 6 étapes"

    # Subscribe pour logging
    events_log = []
    
    @bus.subscribe("AgentTerminé")
    async def log_agent(event):
        events_log.append(event)
        print(f"  -> Event {event.type}: {event.payload.get('agent')} status={event.payload.get('status')}")

    # Exécuter mission
    result = await engine.run(mission)
    
    print(f"✅ Mission terminée: {result.status}")
    assert result.status == "DONE", f"Mission devrait être DONE, got {result.status}"
    
    # Vérifier agents exécutés
    agents_executed = result.context.get('agents_executed', 0)
    print(f"   Agents exécutés: {agents_executed}")
    assert agents_executed >= 2, f"Au moins 2 agents devraient être exécutés, got {agents_executed}"
    
    # Vérifier outputs
    agent_outputs = result.context.get('agent_outputs', {})
    print(f"   Outputs: {list(agent_outputs.keys())}")
    assert len(agent_outputs) >= 2, f"Au moins 2 outputs attendus, got {len(agent_outputs)}"
    
    # Vérifier events
    events = await bus.replay(mission.id)
    print(f"   Events totaux: {len(events)}")
    
    event_types = [e.type for e in events]
    assert "MissionCréée" in event_types, "Event MissionCréée manquant"
    assert "DocumentAnalysé" in event_types, "Event DocumentAnalysé manquant"
    assert "EntitésExtraites" in event_types, "Event EntitésExtraites manquant"
    assert "ClassificationTerminée" in event_types, "Event ClassificationTerminée manquant"
    assert any("AgentDémarré" in et for et in event_types), "Event AgentDémarré manquant"
    assert any("AgentTerminé" in et for et in event_types), "Event AgentTerminé manquant"
    assert "AnalyseTerminée" in event_types, "Event AnalyseTerminée manquant"
    
    # Vérifier que les agents pertinents ont été exécutés
    executed_agents = [o.get('agent_name') for o in agent_outputs.values()]
    assert "PAB Detector" in executed_agents, "PAB Detector devrait être exécuté"
    assert "Deadline Guardian" in executed_agents, "Deadline Guardian devrait être exécuté"
    
    print(f"\n🎉 TEST E2E RÉUSSI!")
    print(f"   - Mission: {mission.id}")
    print(f"   - Statut: {result.status}")
    print(f"   - Agents: {agents_executed}")
    print(f"   - Events: {len(events)}")
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("SMART_AO V7 - Test E2E Complet")
    print("=" * 60)
    
    try:
        result = asyncio.run(test_mission_e2e())
        if result:
            print("\n" + "=" * 60)
            print("✅ TOUS LES TESTS E2E RÉUSSIS")
            print("=" * 60)
            sys.exit(0)
        else:
            print("\n❌ TEST E2E ÉCHOUÉ")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ TEST E2E ÉCHOUÉ AVEC ERREUR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
