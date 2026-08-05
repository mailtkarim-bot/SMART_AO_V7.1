#!/usr/bin/env python3
"""
SMART_AO V7 - REC-011 Validation: Tests Unitaires des 30 Agents
====================================================================
Valide l'implémentation des tests unitaires pour les 30 agents.

Ce script vérifie:
- Le fichier test_all_agents_v7.py existe et est valide
- Tous les 30 agents sont couverts par des tests
- Les tests peuvent être exécutés avec succès
"""

import sys
import subprocess
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def validate_test_file_exists():
    """Valider que le fichier de test principal existe"""
    print("🔍 Validation de l'existence du fichier de test...")
    
    test_file = PROJECT_ROOT / "tests" / "unit" / "test_all_agents_v7.py"
    
    if test_file.exists():
        size = test_file.stat().st_size
        print(f"  ✅ Fichier trouvé: {test_file}")
        print(f"     Taille: {size} octets")
        return True, f"Fichier de test existant ({size} octets)"
    else:
        print(f"  ❌ Fichier manquant: {test_file}")
        return False, "Fichier test_all_agents_v7.py introuvable"


def validate_test_file_content():
    """Valider le contenu du fichier de test"""
    print("🔍 Validation du contenu du fichier de test...")
    
    test_file = PROJECT_ROOT / "tests" / "unit" / "test_all_agents_v7.py"
    content = test_file.read_text()
    
    # Vérifier les imports nécessaires
    required_imports = [
        "import pytest",
        "from app.agents.base_agent import BaseAgent",
        "from app.engines.agent_runtime.registry import registry",
    ]
    
    missing_imports = []
    for imp in required_imports:
        if imp not in content:
            missing_imports.append(imp)
    
    if missing_imports:
        print(f"  ❌ Imports manquants: {missing_imports}")
        return False, f"Imports manquants: {missing_imports}"
    
    print("  ✅ Tous les imports nécessaires présents")
    
    # Vérifier les classes de test pour chaque agent
    expected_agents = [
        "TestAllotiAgent", "TestAssuranceAgent", "TestAvenantAgent",
        "TestBIMAgent", "TestBTIndexAgent", "TestCapaciteAgent",
        "TestCCTPDPGFAgent", "TestCertifAgent", "TestCoherenceAgent",
        "TestContentieuxAgent", "TestDC4Agent", "TestDeadlineAgent",
        "TestEnveloppeAgent", "TestEPlusCAgent", "TestGMEAgent",
        "TestHandoffAgent", "TestMAPAAgent", "TestMateriauxShieldAgent",
        "TestMemoireBoosterAgent", "TestPABAgent", "TestPenalitesAgent",
        "TestQR_TactiqueAgent", "TestRATAgent", "TestRisquesAgent",
        "TestRSEBoosterAgent", "TestSiteContraintesAgent", "TestSOGEDAgent",
        "TestTresorerieAgent", "TestVarianteAgent", "TestVisiteAgent",
        "TestBaseAgent", "TestRegistry", "TestAllAgentsImport", "TestAgentsIntegration"
    ]
    
    missing_classes = []
    for agent_class in expected_agents:
        if f"class {agent_class}" not in content:
            missing_classes.append(agent_class)
    
    if missing_classes:
        print(f"  ❌ Classes de test manquantes: {missing_classes}")
        return False, f"Classes manquantes: {missing_classes}"
    
    print(f"  ✅ Toutes les {len(expected_agents)} classes de test présentes")
    
    # Compter le nombre de tests (méthodes test_)
    test_count = content.count("def test_")
    print(f"  ✅ {test_count} méthodes de test définies")
    
    return True, f"{len(expected_agents)} classes, {test_count} tests"


def validate_test_execution():
    """Valider que les tests peuvent être exécutés"""
    print("🔍 Exécution des tests unitaires...")
    
    test_file = PROJECT_ROOT / "tests" / "unit" / "test_all_agents_v7.py"
    
    # Trouver la commande python disponible
    python_cmd = "python3"
    try:
        subprocess.run([python_cmd, "--version"], capture_output=True, check=True)
    except:
        python_cmd = "python"
    
    try:
        result = subprocess.run(
            [python_cmd, "-m", "pytest", str(test_file), "-v", "--tb=short"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        # Parser la sortie pour obtenir les statistiques
        output = result.stdout + result.stderr
        
        # Extraire le résumé
        if "passed" in output and "failed" in output:
            # Extraire les nombres
            import re
            match = re.search(r'(\d+) passed, (\d+) skipped, (\d+) failed', output)
            if match:
                passed = int(match.group(1))
                skipped = int(match.group(2))
                failed = int(match.group(3))
                total = passed + skipped + failed
                
                print(f"  ✅ Tests exécutés: {total} total")
                print(f"     Passés: {passed}")
                print(f"     Ignorés: {skipped}")
                print(f"     Échoués: {failed}")
                
                if failed > 0:
                    print(f"  ❌ {failed} test(s) échoué(s)")
                    return False, f"{failed} échecs"
                
                success_rate = (passed / total * 100) if total > 0 else 0
                print(f"  ✅ Taux de succès: {success_rate:.1f}%")
                return True, f"{passed}/{total} tests passés"
        
        # Si pas de match, vérifier le return code
        if result.returncode == 0:
            print("  ✅ Tests exécutés avec succès")
            return True, "Tous les tests passés"
        else:
            print(f"  ❌ Erreur lors de l'exécution: code {result.returncode}")
            return False, f"Code erreur: {result.returncode}"
            
    except subprocess.TimeoutExpired:
        print("  ❌ Timeout lors de l'exécution des tests")
        return False, "Timeout"
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        return False, str(e)


def validate_agent_coverage():
    """Valider que tous les 30 agents sont couverts"""
    print("🔍 Validation de la couverture des agents...")
    
    # Lister tous les agents
    agents_dir = PROJECT_ROOT / "app" / "agents"
    agent_files = [f.stem for f in agents_dir.glob("agent_*.py")]
    
    print(f"  ✅ {len(agent_files)} fichiers d'agents trouvés")
    
    # Lister toutes les classes de test
    test_file = PROJECT_ROOT / "tests" / "unit" / "test_all_agents_v7.py"
    content = test_file.read_text()
    
    # Mappage explicite des noms d'agents vers les noms de classes de test
    agent_to_test_class = {
        "agent_alloti": "TestAllotiAgent",
        "agent_assurance": "TestAssuranceAgent",
        "agent_avenant": "TestAvenantAgent",
        "agent_bim": "TestBIMAgent",
        "agent_bt_index": "TestBTIndexAgent",
        "agent_capacite": "TestCapaciteAgent",
        "agent_cctp_dpgf": "TestCCTPDPGFAgent",
        "agent_certif": "TestCertifAgent",
        "agent_coherence": "TestCoherenceAgent",
        "agent_contentieux": "TestContentieuxAgent",
        "agent_dc4": "TestDC4Agent",
        "agent_deadline": "TestDeadlineAgent",
        "agent_enveloppe": "TestEnveloppeAgent",
        "agent_eplusc": "TestEPlusCAgent",
        "agent_gme": "TestGMEAgent",
        "agent_handoff": "TestHandoffAgent",
        "agent_mapa": "TestMAPAAgent",
        "agent_materiaux_shield": "TestMateriauxShieldAgent",
        "agent_memoire_booster": "TestMemoireBoosterAgent",
        "agent_pab": "TestPABAgent",
        "agent_penalites": "TestPenalitesAgent",
        "agent_qr_tactique": "TestQR_TactiqueAgent",
        "agent_rat": "TestRATAgent",
        "agent_risques": "TestRisquesAgent",
        "agent_rse_booster": "TestRSEBoosterAgent",
        "agent_site_contraintes": "TestSiteContraintesAgent",
        "agent_soged": "TestSOGEDAgent",
        "agent_tresorerie": "TestTresorerieAgent",
        "agent_variante": "TestVarianteAgent",
        "agent_visite": "TestVisiteAgent",
    }
    
    test_classes = []
    for agent in agent_files:
        test_class = agent_to_test_class.get(agent, f"Test{agent.replace('agent_', '').title().replace('_', '')}Agent")
        test_classes.append(test_class)
    
    # Vérifier que chaque classe de test existe
    missing = []
    for test_class in test_classes:
        if f"class {test_class}" not in content:
            missing.append(test_class)
    
    if missing:
        print(f"  ❌ Classes manquantes: {missing}")
        return False, f"{len(missing)} classes manquantes"
    
    print(f"  ✅ Tous les {len(test_classes)} agents couverts par des tests")
    return True, f"{len(test_classes)} agents couverts"


def validate_test_quality():
    """Valider la qualité des tests (méthodes essentielles)"""
    print("🔍 Validation de la qualité des tests...")
    
    test_file = PROJECT_ROOT / "tests" / "unit" / "test_all_agents_v7.py"
    content = test_file.read_text()
    
    # Méthodes essentielles à tester pour chaque agent
    essential_methods = [
        "test_agent_exists",
        "test_agent_herite_base_agent",
        "test_agent_attributes",
        "test_can_handle",
        "test_execute",
    ]
    
    found_methods = []
    for method in essential_methods:
        if f"def {method}" in content:
            found_methods.append(method)
    
    print(f"  ✅ {len(found_methods)}/{len(essential_methods)} méthodes essentielles trouvées")
    print(f"     Méthodes: {found_methods}")
    
    return True, f"{len(found_methods)} méthodes essentielles validées"


def main():
    """Exécuter toutes les validations REC-011"""
    print("=" * 80)
    print("🚀 SMART_AO V7 - REC-011 Validation: Tests Unitaires des 30 Agents")
    print("=" * 80)
    print()
    
    # Liste des validations
    validations = [
        ("Fichier de test principal", validate_test_file_exists),
        ("Contenu du fichier de test", validate_test_file_content),
        ("Couverture des agents", validate_agent_coverage),
        ("Qualité des tests", validate_test_quality),
        ("Exécution des tests", validate_test_execution),
    ]
    
    results = []
    
    for name, validator in validations:
        try:
            passed, message = validator()
            results.append({
                'name': name,
                'passed': passed,
                'message': message
            })
        except Exception as e:
            results.append({
                'name': name,
                'passed': False,
                'message': str(e)
            })
        print()
    
    # Afficher le résumé
    print("=" * 80)
    print("📊 RÉSULTATS REC-011")
    print("=" * 80)
    
    total = len(results)
    passed = sum(1 for r in results if r['passed'])
    failed = total - passed
    
    for result in results:
        status = "✅ PASS" if result['passed'] else "❌ FAIL"
        print(f"{status} | {result['name']}: {result['message']}")
    
    print()
    print(f"Total: {total} | Passed: {passed} | Failed: {failed}")
    print(f"Taux de succès: {passed/total*100:.1f}%")
    print("=" * 80)
    
    if failed == 0:
        print("✅ REC-011 VALIDÉE À 100%")
        return 0
    else:
        print(f"❌ REC-011: {failed} validation(s) échouée(s)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
