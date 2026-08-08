"""
SMART_AO V7 - local_llm.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 07/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - Local LLM Fallback
================================
Source: ARCHITECTURE_V7_ENGINE.md ADR-060 + ENGINEERING-HANDBOOK_V7.md

Pour les DCE marqués "Confidentiel Défense / Nucléaire / Seveso", aucun appel
API externe n'est autorisé. Ce module bascule vers un modèle local quantizé
(Mistral 7B / Llama 3 8B) via Ollama ou un fallback déterministe si le serveur
local n'est pas disponible.

Garage Math ZERO LLM reste inchangé : les euros ne sont JAMAIS calculés par LLM.
"""

import logging
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple

logger = logging.getLogger(__name__)

# Mots-clés de confidentialité déclenchant le fallback local
CONFIDENTIAL_MARKERS = [
    "confidentiel défense",
    "confidentiel-défense",
    "secret défense",
    "nucléaire",
    "installation nucléaire",
    "seveso",
    "icpe",
    "sensitive",
    "restricted",
    "classifié",
    "non divulgation",
]


@dataclass
class LocalLLMResponse:
    """Réponse standardisée du fallback LLM local."""
    text: str
    model: str
    local: bool
    fallback: bool
    confidential: bool
    metadata: Dict[str, Any]


class LocalLLMClient:
    """
    Client LLM local pour documents sensibles.

    Ordre de priorité :
    1. Serveur Ollama local (OLLAMA_URL / OLLAMA_MODEL).
    2. Réponse déterministe locale (zero external call).
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 60.0,
    ):
        self.base_url = base_url or os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "mistral:7b")
        self.timeout = timeout

    def detect_confidentialite(self, text: str) -> Tuple[bool, List[str]]:
        """
        Détecte si un DCE contient des marqueurs de confidentialité.

        Returns:
            (is_confidential, matched_markers)
        """
        lower = text.lower()
        matched = [m for m in CONFIDENTIAL_MARKERS if m in lower]
        return bool(matched), matched

    async def generate(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        force_local: bool = False,
    ) -> LocalLLMResponse:
        """
        Génère une réponse en local. Si Ollama est injoignable, retourne un
        fallback déterministe qui reste entièrement sur le VPS.
        """
        context = context or {}
        is_confidential = force_local or context.get("confidential", False)

        # 1. Essai Ollama
        try:
            response_text = await self._call_ollama(prompt)
            return LocalLLMResponse(
                text=response_text,
                model=self.model,
                local=True,
                fallback=False,
                confidential=is_confidential,
                metadata={"provider": "ollama", "base_url": self.base_url},
            )
        except Exception as e:
            logger.warning(f"Ollama indisponible ({e}), fallback local activé")

        # 2. Fallback local déterministe
        fallback_text = self._deterministic_fallback(prompt, is_confidential)
        return LocalLLMResponse(
            text=fallback_text,
            model=f"{self.model}-fallback",
            local=True,
            fallback=True,
            confidential=is_confidential,
            metadata={"provider": "local_fallback", "reason": "ollama_unavailable"},
        )

    async def _call_ollama(self, prompt: str) -> str:
        """Appel HTTP vers l'API Ollama /api/generate."""
        try:
            import httpx
        except ImportError as exc:
            raise RuntimeError("httpx non installé") from exc

        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2, "num_predict": 512},
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", "").strip()

    def _deterministic_fallback(self, prompt: str, confidential: bool) -> str:
        """
        Fallback 100 % offline. Il structure la réponse sans inventer de chiffres.
        """
        markers = "[CONFIDENTIEL] " if confidential else ""
        return (
            f"{markers}[FALLBACK LOCAL] Analyse qualitative du DCE effectuée hors ligne. "
            "Points de vigilance à vérifier : clauses de confidentialité, périmètre exact, "
            "échéances et pièces administratives obligatoires. Aucun montant financier n'a "
            "été calculé par ce module (Garage Math dédié)."
        )

    async def analyze_dce(self, dce_text: str) -> LocalLLMResponse:
        """
        Analyse un DCE : détecte la confidentialité puis bascule sur LLM local si
        nécessaire.
        """
        confidential, markers = self.detect_confidentialite(dce_text)
        prompt = (
            "Analyse qualitative ce DCE pour un entrepreneur du BTP. "
            "Identifie les risques juridiques, techniques et administratifs. "
            "Ne donne aucun montant en euros."
        )
        if len(dce_text) > 2000:
            prompt += f"\n\nExtrait du DCE :\n{dce_text[:2000]}..."
        else:
            prompt += f"\n\nDCE :\n{dce_text}"

        response = await self.generate(
            prompt, context={"confidential": confidential, "markers": markers}, force_local=confidential
        )
        response.metadata["markers"] = markers
        return response


# Singleton projet
_local_llm_client: Optional[LocalLLMClient] = None


def get_local_llm_client() -> LocalLLMClient:
    global _local_llm_client
    if _local_llm_client is None:
        _local_llm_client = LocalLLMClient()
    return _local_llm_client
