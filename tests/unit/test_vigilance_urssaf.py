"""
SMART_AO V7.1 - test_vigilance_urssaf.py
========================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 07/08/2026
Build: 9.5 - Phase: 5
"""

"""
SMART_AO V7.1 - Test Vigilance URSSAF (Module 7.30)
Source: RAPPORT (1).md §7.30
"""
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from app.engines.math_engine.vigilance_solver import VigilanceSolver


def test_urssaf_valide():
    solver = VigilanceSolver()
    date_valide = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
    result = solver.calculer(date_attestation=date_valide, montant_sous_traite=140000.0)
    assert result.blocage_depot is False
    assert result.attestation_valide is True
    assert float(result.exposition_solidaire) == 0.0
    print("✅ Attestation URSSAF valide: pas de blocage")


def test_urssaf_expiree_12_jours():
    solver = VigilanceSolver()
    # 180 + 12 jours d'expiration
    date_expiree = (datetime.now(timezone.utc) - timedelta(days=192)).isoformat()
    result = solver.calculer(date_attestation=date_expiree, montant_sous_traite=140000.0)
    assert result.blocage_depot is True
    assert result.attestation_valide is False
    assert float(result.exposition_solidaire) == 140000.0
    print(f"✅ Attestation expirée: blocage + exposition {result.exposition_solidaire} €")


def test_urssaf_liquidation():
    solver = VigilanceSolver()
    result = solver.calculer(
        date_attestation=datetime.now(timezone.utc).isoformat(),
        montant_sous_traite=80000.0,
        statut_juridique="liquidation",
    )
    assert result.blocage_depot is True
    assert float(result.exposition_solidaire) == 80000.0
    print("✅ Sous-traitant en liquidation: blocage + exposition totale")


def test_urssaf_absente():
    solver = VigilanceSolver()
    result = solver.calculer(date_attestation=None, montant_sous_traite=50000.0)
    assert result.blocage_depot is True
    assert float(result.exposition_solidaire) == 50000.0
    print("✅ Attestation manquante: blocage + exposition")


if __name__ == "__main__":
    test_urssaf_valide()
    test_urssaf_expiree_12_jours()
    test_urssaf_liquidation()
    test_urssaf_absente()
    print("✅ TESTS PASSED: Vigilance URSSAF")
