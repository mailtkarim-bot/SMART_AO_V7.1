"""
SMART_AO V7.1 - test_sourcing_api.py
====================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 07/08/2026
Build: 9.5 - Phase: 5
"""

"""
SMART_AO V7.1 - Test Sourcing & API Profil Acheteur (Module 7.33)
Source: RAPPORT (1).md §7.33
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from app.engines.math_engine.sourcing_api_solver import SourcingAPISolver


def test_dume_assembly():
    solver = SourcingAPISolver()
    result = solver.assembler(
        siret="12345678900012",
        plateforme="PLACE",
        dc1={"candidat": "TEST"},
        dume={"reference": "DUME-001"},
        pieces_jointes=["KBIS.pdf", "DC2.pdf"],
    )
    assert result.dume_json["version"] == "DUME-JSON-1.0"
    assert result.dume_json["plateforme"] == "PLACE"
    assert result.dume_json["statut"] == "PRET_A_ENVOI"
    assert len(result.empreinte_sha256) == 64
    assert result.statut_envoi == "SIMULATION_OK"
    assert result.detail_calcul["nb_pieces_jointes"] == 2
    print("✅ DUME JSON assemblé avec empreinte SHA-256")


def test_dume_hash_changes_with_input():
    solver = SourcingAPISolver()
    r1 = solver.assembler(siret="12345678900012", dume={"ref": "A"})
    r2 = solver.assembler(siret="12345678900012", dume={"ref": "B"})
    assert r1.empreinte_sha256 != r2.empreinte_sha256
    assert len(r1.empreinte_sha256) == 64
    print("✅ Empreinte SHA-256 dépendante des données")


if __name__ == "__main__":
    test_dume_assembly()
    test_dume_hash_changes_with_input()
    print("✅ TESTS PASSED: Sourcing & API Profil Acheteur")
