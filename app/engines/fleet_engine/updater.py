"""
SMART_AO V7 - updater.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 07/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - Fleet Updater
===========================
Moteur de mise à jour pull-based pour le parc de VPS clients.

Flux :
1. Le VPS interroge le serveur central (manifest).
2. Vérification de la licence locale.
3. Vérification cosign de l'image Docker proposée.
4. Si tout est vert, l'update est marquée comme applicable.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from app.engines.fleet_engine.license_checker import LicenseChecker
from app.engines.fleet_engine.cosign_verifier import CosignVerifier

logger = logging.getLogger(__name__)


@dataclass
class UpdateStatus:
    available: bool
    version: str
    image: str
    license_valid: bool
    signature_valid: bool
    applicable: bool
    reason: str
    manifest: Dict[str, Any]


class FleetUpdater:
    """
    Updater pull-based sécurisé.
    """

    def __init__(
        self,
        vps_id: str,
        license_payload: Optional[Dict[str, Any]] = None,
        license_checker: Optional[LicenseChecker] = None,
        cosign_verifier: Optional[CosignVerifier] = None,
    ):
        self.vps_id = vps_id
        self.license_payload = license_payload or {}
        self.license_checker = license_checker or LicenseChecker()
        self.cosign_verifier = cosign_verifier or CosignVerifier()

    def fetch_manifest(self, manifest: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Récupère le manifest de mise à jour.
        En production, ferait un appel HTTPS vers le serveur central.
        Ici, on accepte un manifest injecté ou un manifest par défaut.
        """
        if manifest:
            return manifest
        # Manifest par défaut : aucune update
        return {
            "version": "v7.1.0",
            "image": f"smart-ao/engine:{self.vps_id}",
            "channel": "stable",
            "released_at": datetime.now(timezone.utc).isoformat(),
        }

    def check_for_update(
        self,
        current_version: str = "v7.1.0",
        manifest: Optional[Dict[str, Any]] = None,
    ) -> UpdateStatus:
        """
        Vérifie si une mise à jour est disponible et applicable.
        """
        fetched = self.fetch_manifest(manifest)
        new_version = fetched.get("version", current_version)
        image = fetched.get("image", "")

        # 1. Licence
        license_result = self.license_checker.validate(
            self.license_payload, expected_vps_id=self.vps_id
        )
        license_valid = license_result["valid"]

        # 2. Signature cosign
        cosign_result = self.cosign_verifier.verify(image)
        signature_valid = cosign_result.verified

        available = new_version != current_version
        applicable = available and license_valid and signature_valid

        reason_parts = []
        if not available:
            reason_parts.append("already up to date")
        if not license_valid:
            reason_parts.append(f"license invalid: {license_result.get('reason')}")
        if not signature_valid:
            reason_parts.append(f"signature invalid: {cosign_result.reason}")
        if applicable:
            reason_parts.append("update applicable")

        return UpdateStatus(
            available=available,
            version=new_version,
            image=image,
            license_valid=license_valid,
            signature_valid=signature_valid,
            applicable=applicable,
            reason="; ".join(reason_parts) if reason_parts else "no update",
            manifest=fetched,
        )

    def apply_update(self, status: UpdateStatus) -> Dict[str, Any]:
        """
        Applique la mise à jour (simulation).
        En production, exécuterait docker pull + restart orchestré.
        """
        if not status.applicable:
            return {
                "success": False,
                "reason": status.reason,
                "vps_id": self.vps_id,
            }
        logger.info(f"Applying update {status.version} on VPS {self.vps_id}")
        return {
            "success": True,
            "version": status.version,
            "image": status.image,
            "vps_id": self.vps_id,
            "applied_at": datetime.now(timezone.utc).isoformat(),
        }
