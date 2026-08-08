#!/usr/bin/env python3
"""
SMART_AO V7 - Test de conformité ZERO €
=========================================
Vérifie que tous les agents respectent la règle ZERO € dans leurs findings
"""

import asyncio
import sys
from pathlib import Path

# Ajouter le répertoire app au path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from agents.base_agent import AgentOutput, EURO_REGEX
from agents.agent_contentieux import ContentieuxGeneratorAgent
from agents.agent_cctp_dpgf import CCTPDPGFAgent
from agents.agent_bt01 import BT01Agent
from agents.agent_avenant import AvenantTrackerAgent
from agents.agent_gme import GMEAgent
from agents.agent_mapa import MAPAGeneratorAgent
from agents.agent_memoire_booster import MemoireBoosterAgent
from agents.agent_soged import SOGEDAgent
from agents.agent_penalites import PenalitesAgent
from agents.agent_tresorerie import TresorerieAgent
from agents.agent_pab import PABAgent


async def test_agent_zero_euro(agent, input_data: dict):
    """Tester qu'un agent respecte ZERO € dans ses findings."""
    try:
        output = await agent.execute(input_data)
        
        # Vérifier que findings ne contient pas €, EUR, marge, coeff_vente, BFR
        findings_str = str(output.findings)
        
        violations = []
        for match in EURO_REGEX.finditer(findings_str):
            violations.append(f"  - Violation: {match.group()}")
        
        if violations:
            return False, violations, output.findings
        else:
            return True, [], output.findings
            
    except Exception as e:
        return False, [f"Erreur: {str(e)}"], None


async def main():
    """Exécuter tous les tests ZERO €."""
    print("=" * 80)
    print("TEST DE CONFORMITÉ ZERO € - SMART_AO V7")
    print("=" * 80)
    print()
    
    # Agents à tester
    agents_to_test = [
        ("PenalitesAgent", PenalitesAgent(), {
            "mission_id": "test_001",
            "dce_chunks": [{"text": "retard de 45 jours", "page": 1}],
            "parsed_docs": {},
            "context": {"delai_execution_jours": 30, "delai_reel_jours": 45, "montant_marche_ht": 1000000, "ccag_applicable": True},
            "previous_outputs": {}
        }),
        ("TresorerieAgent", TresorerieAgent(), {
            "mission_id": "test_002",
            "dce_chunks": [],
            "parsed_docs": {},
            "context": {"montant_marche_ht": 500000, "avance_pourcentage": 30, "bfr_mois": {"jan": 50000, "fev": 60000}},
            "previous_outputs": {}
        }),
        ("PABAgent", PABAgent(), {
            "mission_id": "test_003",
            "dce_chunks": [],
            "parsed_docs": {},
            "context": {"estimation_interne": 150000, "prix_moyen_marche": 200000},
            "previous_outputs": {}
        }),
        ("ContentieuxGeneratorAgent", ContentieuxGeneratorAgent(), {
            "mission_id": "test_004",
            "dce_chunks": [],
            "parsed_docs": {},
            "context": {"contentieux": {"montant_risque": 1500000}},
            "previous_outputs": {}
        }),
        ("CCTPDPGFAgent", CCTPDPGFAgent(), {
            "mission_id": "test_005",
            "dce_chunks": [],
            "parsed_docs": {},
            "context": {
                "cctp": {"lots": {"lot1": {"quantite": 100, "prix_moyen_marche": 100}}},
                "dpgf": {"lots": {"lot1": {"prix_unitaire": 80, "quantite": 100}}}
            },
            "previous_outputs": {}
        }),
        ("BT01Agent", BT01Agent(), {
            "mission_id": "test_006",
            "dce_chunks": [{"text": "1.1 Terrassement 1000 m3 25,00 25000,00"}],
            "parsed_docs": {},
            "context": {},
            "previous_outputs": {}
        }),
        ("AvenantTrackerAgent", AvenantTrackerAgent(), {
            "mission_id": "test_007",
            "dce_chunks": [],
            "parsed_docs": {},
            "context": {"avenants": [{"description": "Avenant 1", "impact_financier": 50000}]},
            "previous_outputs": {}
        }),
        ("GMEAgent", GMEAgent(), {
            "mission_id": "test_008",
            "dce_chunks": [],
            "parsed_docs": {},
            "context": {"cout_mo_heure": 45.50, "heures_prevues": 200},
            "previous_outputs": {}
        }),
        ("MAPAGeneratorAgent", MAPAGeneratorAgent(), {
            "mission_id": "test_009",
            "dce_chunks": [],
            "parsed_docs": {},
            "context": {"mapa": {"montant": 250000, "seuils": {"europeen": 140000}}},
            "previous_outputs": {}
        }),
        ("MemoireBoosterAgent", MemoireBoosterAgent(), {
            "mission_id": "test_010",
            "dce_chunks": [],
            "parsed_docs": {},
            "context": {
                "historique_chantiers": [{"nom": "Projet A", "prix_m2": 1500, "type": "neuf"}],
                "projet_actuel": {"prix_m2": 1800, "type": "neuf"}
            },
            "previous_outputs": {}
        }),
        ("SOGEDAgent", SOGEDAgent(), {
            "mission_id": "test_011",
            "dce_chunks": [],
            "parsed_docs": {},
            "context": {
                "dechets": {
                    "bois": {"quantite_tonnes": 5.5, "cout_evacuation": 2000, "dangeroux": False},
                    "amiant": {"quantite_tonnes": 2.0, "cout_evacuation": 5000, "dangeroux": True}
                }
            },
            "previous_outputs": {}
        }),
    ]
    
    all_passed = True
    total_tests = len(agents_to_test)
    passed_tests = 0
    
    for agent_name, agent, input_data in agents_to_test:
        print(f"Test: {agent_name}...", end=" ")
        
        from agents.base_agent import AgentInput
        agent_input = AgentInput(**input_data)
        
        is_compliant, violations, findings = await test_agent_zero_euro(agent, agent_input)
        
        if is_compliant:
            print("✅ PASS")
            passed_tests += 1
        else:
            print("❌ FAIL")
            all_passed = False
            print(f"  Violations ZERO € détectées:")
            for violation in violations:
                print(violation)
            print(f"  Findings: {findings[:200]}...")
    
    print()
    print("=" * 80)
    print(f"RÉSULTAT: {passed_tests}/{total_tests} tests passés")
    
    if all_passed:
        print("✅ TOUS LES AGENTS RESPECTENT ZERO €")
    else:
        print("❌ CERTAINS AGENTS VIOLENT ZERO €")
        sys.exit(1)
    
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
