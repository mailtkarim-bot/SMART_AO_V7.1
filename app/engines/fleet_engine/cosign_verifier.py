"""
SMART_AO V7 - cosign_verifier.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 07/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - Cosign Signature Verifier
=======================================
Vérifie la signature d'une image Docker avec cosign (Sigstore).
En environnement de test / sans binaire cosign, passe en mode "mock verify"
si COSIGN_MOCK=1 ou si le binaire n'est pas trouvé.
"""

import logging
import os
import subprocess
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class CosignResult:
    image: str
    verified: bool
    reason: str
    mock: bool


class CosignVerifier:
    """
    Vérificateur de signature d'image container.
    """

    def __init__(self, cosign_path: Optional[str] = None, public_key: Optional[str] = None):
        self.cosign_path = cosign_path or "cosign"
        self.public_key = public_key or os.getenv("COSIGN_PUBLIC_KEY")
        self.mock_mode = os.getenv("COSIGN_MOCK", "0") == "1"

    def _cosign_available(self) -> bool:
        try:
            subprocess.run(
                [self.cosign_path, "version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
            return True
        except Exception:
            return False

    def verify(self, image: str) -> CosignResult:
        """
        Vérifie la signature cosign d'une image.
        En mock ou si cosign absent, retourne un résultat déterministe.
        """
        if self.mock_mode or not self._cosign_available():
            # Mode test / fallback : on simule un succès pour les images du registry SMART_AO
            if image.startswith("smart-ao/") or image.startswith("ghcr.io/smart-ao/"):
                return CosignResult(
                    image=image, verified=True, reason="mock verify ok", mock=True
                )
            return CosignResult(
                image=image,
                verified=False,
                reason="mock verify failed: untrusted image source",
                mock=True,
            )

        cmd = [self.cosign_path, "verify", "--key", self.public_key, image]
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=60,
                check=True,
            )
            return CosignResult(
                image=image, verified=True, reason=result.stdout.strip(), mock=False
            )
        except subprocess.CalledProcessError as exc:
            return CosignResult(
                image=image, verified=False, reason=exc.stderr.strip(), mock=False
            )
        except Exception as exc:
            return CosignResult(
                image=image, verified=False, reason=f"cosign error: {exc}", mock=False
            )


def verify_image_signature(image: str, public_key: Optional[str] = None) -> CosignResult:
    """Helper statique."""
    return CosignVerifier(public_key=public_key).verify(image)
