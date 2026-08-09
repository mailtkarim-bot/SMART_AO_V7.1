"""
SMART_AO V7 - Knowledge Engine __init__.py
==========================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Knowledge Engine - Moteur de connaissances pour SMART_AO V7
Source: ARCHITECTURE_V7_ENGINE.md §3.4
"""

from .embedding_engine import BGEEmbeddingProvider, get_embedding_provider
from .local_llm import LocalLLMClient, get_local_llm_client
from .confidentialite_detector import ConfidentialiteDetector, detect_confidentialite

__all__ = [
    "BGEEmbeddingProvider",
    "get_embedding_provider",
    "LocalLLMClient",
    "get_local_llm_client",
    "ConfidentialiteDetector",
    "detect_confidentialite",
]

