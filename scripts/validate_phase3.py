"""
SMART_AO V7 - validate_phase3.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Validation Phase 3
=================================
Valide l'implémentation de la Phase 3 (Builds 5-6).
"""

import sys
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def validate_build5():
    """Valider Build 5."""
    print("🔍 Validation Build 5...")
    
    # Vérifier les fichiers Event Bus
    eb_dir = PROJECT_ROOT / "app" / "engines" / "event_bus"
    required_eb = ["__init__.py", "bus.py", "models.py", "replay.py"]
    missing_eb = [f for f in required_eb if not (eb_dir / f).exists()]
    
    if missing_eb:
        print(f"  ❌ Event Bus: {missing_eb}")
        return False
    print("  ✅ Event Bus complet")
    
    # Vérifier les fichiers Workflow Engine
    wf_dir = PROJECT_ROOT / "app" / "engines" / "workflow_engine"
    required_wf = ["__init__.py", "mission.py", "workflow.py", "persistence.py"]
    missing_wf = [f for f in required_wf if not (wf_dir / f).exists()]
    
    if missing_wf:
        print(f"  ❌ Workflow Engine: {missing_wf}")
        return False
    print("  ✅ Workflow Engine complet")
    
    # Vérifier Agent Runtime
    ar_dir = PROJECT_ROOT / "app" / "engines" / "agent_runtime"
    required_ar = ["__init__.py", "registry.py", "lifecycle.py"]
    missing_ar = [f for f in required_ar if not (ar_dir / f).exists()]
    
    if missing_ar:
        print(f"  ❌ Agent Runtime: {missing_ar}")
        return False
    print("  ✅ Agent Runtime complet")
    
    # Vérifier agent_certif.py
    certif_file = PROJECT_ROOT / "app" / "agents" / "agent_certif.py"
    if not certif_file.exists():
        print("  ❌ agent_certif.py manquant")
        return False
    print("  ✅ agent_certif.py présent")
    
    return True


def validate_build6():
    """Valider Build 6."""
    print("🔍 Validation Build 6...")
    
    agents_dir = PROJECT_ROOT / "app" / "agents"
    
    # Liste des 30 agents attendus
    expected_agents = [
        "agent_alloti", "agent_assurance", "agent_avenant",
        "agent_bim", "agent_bt_index", "agent_capacite",
        "agent_cctp_dpgf", "agent_certif", "agent_coherence",
        "agent_contentieux", "agent_deadline", "agent_dc4",
        "agent_enveloppe", "agent_eplusc", "agent_gme",
        "agent_handoff", "agent_mapa", "agent_materiaux_shield",
        "agent_memoire_booster", "agent_pab", "agent_penalites",
        "agent_qr_tactique", "agent_rat", "agent_risques",
        "agent_rse_booster", "agent_site_contraintes",
        "agent_soged", "agent_tresorerie", "agent_variante",
        "agent_visite",
    ]
    
    missing = []
    present = []
    
    for agent_file in expected_agents:
        if (agents_dir / f"{agent_file}.py").exists():
            present.append(agent_file)
        else:
            missing.append(agent_file)
    
    print(f"  ✅ {len(present)}/{len(expected_agents)} agents présents")
    
    if missing:
        print(f"  ⚠️  Agents manquants: {missing}")
        return False
    
    return True


def validate_tests_build5():
    """Valider les tests Build 5."""
    print("🔍 Validation des tests Build 5...")
    
    python_cmd = "python3"
    test_files = [
        "test_event_bus.py",
        "test_workflow_engine.py",
        "test_persistence.py",
        "test_registry_discovery.py",
    ]
    
    passed = 0
    failed = 0
    
    for test_file in test_files:
        test_path = PROJECT_ROOT / "tests" / "unit" / test_file
        if not test_path.exists():
            print(f"  ❌ {test_file} manquant")
            failed += 1
            continue
        
        try:
            result = subprocess.run(
                [python_cmd, str(test_path)],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                print(f"  ✅ {test_file}: PASSE")
                passed += 1
            else:
                print(f"  ❌ {test_file}: FAIL")
                failed += 1
        except Exception as e:
            print(f"  ❌ {test_file}: ERROR - {e}")
            failed += 1
    
    return failed == 0


def main():
    print("=" * 80)
    print("🚀 SMART_AO V7 - VALIDATION PHASE 3")
    print("=" * 80)
    print()
    
    # Valider Build 5
    if validate_build5():
        print("✅ Build 5 validé")
    else:
        print("❌ Build 5 incomplet")
    print()
    
    # Valider Build 6
    if validate_build6():
        print("✅ Build 6 validé")
    else:
        print("❌ Build 6 incomplet")
    print()
    
    # Valider les tests
    if validate_tests_build5():
        print("✅ Tests Build 5 passés")
    else:
        print("❌ Tests Build 5 échoués")
    print()
    
    print("=" * 80)
    print("Prochaine étape: Compléter les agents manquants")
    print("=" * 80)


if __name__ == "__main__":
    main()
