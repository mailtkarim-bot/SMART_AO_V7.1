"""
SMART_AO V7.1 - test_fleet_update.py
====================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 07/08/2026
Build: 9.5 - Phase: 5
"""

"""
SMART_AO V7.1 - Test Fleet Engine Update (ADR-059)
Source: ARCHITECTURE_V7_ENGINE.md ADR-059
"""
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from app.engines.fleet_engine import FleetUpdater, LicenseChecker, CosignVerifier


def test_license_valid():
    checker = LicenseChecker(secret="TEST_SECRET")
    expires = datetime.now(timezone.utc) + timedelta(days=30)
    license_payload = checker.issue_license(
        vps_id="vps-test-001",
        siret="12345678900012",
        expires_at=expires,
        modules=["all"],
    )
    result = checker.validate(license_payload, expected_vps_id="vps-test-001")
    assert result["valid"] is True
    assert result["license"] is not None
    print("✅ Licence valide pour VPS test")


def test_license_wrong_vps():
    checker = LicenseChecker(secret="TEST_SECRET")
    expires = datetime.now(timezone.utc) + timedelta(days=30)
    payload = checker.issue_license(vps_id="vps-a", siret="123", expires_at=expires)
    result = checker.validate(payload, expected_vps_id="vps-b")
    assert result["valid"] is False
    print("✅ Licence liée au mauvais VPS rejetée")


def test_cosign_verify_smart_ao_image():
    os.environ["COSIGN_MOCK"] = "1"
    verifier = CosignVerifier()
    result = verifier.verify("smart-ao/engine:v7.1.1")
    assert result.verified is True
    assert result.mock is True
    print("✅ Signature cosign mock validée")


def test_fleet_update_applicable():
    os.environ["COSIGN_MOCK"] = "1"
    checker = LicenseChecker(secret="TEST_SECRET")
    expires = datetime.now(timezone.utc) + timedelta(days=30)
    license_payload = checker.issue_license(
        vps_id="vps-fleet-01",
        siret="12345678900012",
        expires_at=expires,
    )

    updater = FleetUpdater(
        vps_id="vps-fleet-01",
        license_payload=license_payload,
        license_checker=checker,
        cosign_verifier=CosignVerifier(),
    )

    manifest = {
        "version": "v7.1.1",
        "image": "smart-ao/engine:v7.1.1",
        "channel": "stable",
    }
    status = updater.check_for_update(current_version="v7.1.0", manifest=manifest)
    assert status.available is True
    assert status.license_valid is True
    assert status.signature_valid is True
    assert status.applicable is True

    apply_result = updater.apply_update(status)
    assert apply_result["success"] is True
    assert apply_result["version"] == "v7.1.1"
    print("✅ Mise à jour Fleet applicable et appliquée")


if __name__ == "__main__":
    test_license_valid()
    test_license_wrong_vps()
    test_cosign_verify_smart_ao_image()
    test_fleet_update_applicable()
    print("✅ TESTS PASSED: Fleet Engine Update")
