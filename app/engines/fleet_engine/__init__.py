"""
SMART_AO V7 - fleet_engine/__init__.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 07/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - Fleet Management Engine
=====================================
Source: ARCHITECTURE_V7_ENGINE.md §3 + ADR-059

Moteur de gestion du parc de VPS clients :
- Pull-based update (le VPS interroge le serveur central)
- Vérification de licence par VPS
- Vérification de signature cosign des images Docker
"""

from app.engines.fleet_engine.license_checker import LicenseChecker, validate_license
from app.engines.fleet_engine.cosign_verifier import CosignVerifier, verify_image_signature
from app.engines.fleet_engine.updater import FleetUpdater, UpdateStatus

__all__ = [
    "LicenseChecker",
    "validate_license",
    "CosignVerifier",
    "verify_image_signature",
    "FleetUpdater",
    "UpdateStatus",
]
