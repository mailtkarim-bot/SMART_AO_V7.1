"""
SMART_AO V7 - license_checker.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 07/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - License Checker
=============================
Vérifie la licence d'un VPS SMART_AO.
Chaque client a une licence liée à son vps_id + SIRET.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class LicenseInfo:
    vps_id: str
    siret: str
    expires_at: datetime
    tier: str
    modules: list
    signature: str

    def is_valid(self) -> bool:
        return datetime.now(timezone.utc) < self.expires_at


class LicenseChecker:
    """
    Vérificateur de licence basé sur HMAC-SHA256 (production : RSA via pyjwt).
    """

    def __init__(self, secret: Optional[str] = None):
        self.secret = secret or "SMART_AO_LICENSE_SECRET_CHANGE_IN_PROD"

    def validate(
        self,
        license_payload: Dict[str, Any],
        expected_vps_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Valide une licence.

        Args:
            license_payload: dict contenant vps_id, siret, expires_at, tier,
                             modules, signature.
            expected_vps_id: vps_id du VPS local (optionnel, mais recommandé).

        Returns:
            {"valid": bool, "reason": str, "license": LicenseInfo|None}
        """
        try:
            import hmac
            import hashlib

            payload_sig = license_payload.get("signature", "")
            vps_id = license_payload.get("vps_id", "")
            siret = license_payload.get("siret", "")
            expires_at_str = license_payload.get("expires_at", "")
            tier = license_payload.get("tier", "standard")
            modules = license_payload.get("modules", [])

            if expected_vps_id and vps_id != expected_vps_id:
                return {
                    "valid": False,
                    "reason": f"vps_id mismatch: {vps_id} != {expected_vps_id}",
                    "license": None,
                }

            try:
                expires_at = datetime.fromisoformat(expires_at_str)
                if expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=timezone.utc)
            except Exception as exc:
                return {"valid": False, "reason": f"invalid expires_at: {exc}", "license": None}

            if datetime.now(timezone.utc) >= expires_at:
                return {"valid": False, "reason": "license expired", "license": None}

            # Recompute signature
            message = f"{vps_id}:{siret}:{expires_at_str}:{tier}:{','.join(sorted(modules))}"
            expected_sig = hmac.new(
                self.secret.encode(), message.encode(), hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(expected_sig, payload_sig):
                return {"valid": False, "reason": "invalid signature", "license": None}

            info = LicenseInfo(
                vps_id=vps_id,
                siret=siret,
                expires_at=expires_at,
                tier=tier,
                modules=modules,
                signature=payload_sig,
            )
            return {"valid": True, "reason": "ok", "license": info}

        except Exception as exc:
            logger.error(f"License validation error: {exc}")
            return {"valid": False, "reason": f"validation error: {exc}", "license": None}

    def issue_license(
        self,
        vps_id: str,
        siret: str,
        expires_at: datetime,
        tier: str = "standard",
        modules: Optional[list] = None,
    ) -> Dict[str, Any]:
        """Génère une licence signée (usage interne / tests)."""
        import hmac
        import hashlib

        modules = modules or []
        expires_at_str = expires_at.isoformat()
        message = f"{vps_id}:{siret}:{expires_at_str}:{tier}:{','.join(sorted(modules))}"
        signature = hmac.new(
            self.secret.encode(), message.encode(), hashlib.sha256
        ).hexdigest()

        return {
            "vps_id": vps_id,
            "siret": siret,
            "expires_at": expires_at_str,
            "tier": tier,
            "modules": modules,
            "signature": signature,
        }


def validate_license(
    license_payload: Dict[str, Any],
    expected_vps_id: Optional[str] = None,
    secret: Optional[str] = None,
) -> Dict[str, Any]:
    """Helper statique."""
    return LicenseChecker(secret=secret).validate(license_payload, expected_vps_id)
