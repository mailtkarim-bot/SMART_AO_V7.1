"""
SMART_AO V7 - confidentialite_detector.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 07/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - Confidentialité Detector
======================================
Source: ARCHITECTURE_V7_ENGINE.md ADR-060

Détecte les marqueurs de confidentialité dans un DCE avant tout traitement
par un service externe. Si un document est confidentiel, le workflow bascule
automatiquement sur le Local LLM Fallback (Mistral 7B/Llama 3 8B via Ollama).
"""

from typing import Dict, List, Any
from app.engines.knowledge_engine.local_llm import LocalLLMClient, CONFIDENTIAL_MARKERS


class ConfidentialiteDetector:
    """
    Détecteur de documents confidentiels (Défense, Nucléaire, Seveso, ICPE...).
    """

    def __init__(self, client: LocalLLMClient = None):
        self.client = client or LocalLLMClient()

    def detect(self, text: str) -> Dict[str, Any]:
        """
        Analyse un texte et retourne le verdict de confidentialité.

        Returns:
            {
                "confidential": bool,
                "markers": list[str],
                "risk_level": "NONE" | "HIGH",
                "recommended_handler": "local_llm" | "standard"
            }
        """
        is_conf, markers = self.client.detect_confidentialite(text)
        return {
            "confidential": is_conf,
            "markers": markers,
            "risk_level": "HIGH" if is_conf else "NONE",
            "recommended_handler": "local_llm" if is_conf else "standard",
        }

    def get_markers(self) -> List[str]:
        """Retourne la liste des marqueurs de confidentialité configurés."""
        return list(CONFIDENTIAL_MARKERS)


def detect_confidentialite(text: str) -> Dict[str, Any]:
    """Fonction utilitaire."""
    return ConfidentialiteDetector().detect(text)
