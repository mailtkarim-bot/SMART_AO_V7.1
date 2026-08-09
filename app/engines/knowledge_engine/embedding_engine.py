"""
SMART_AO V7 - embedding_engine.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 07/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - Embedding Engine (BGE-M3)
=======================================
Source: ARCHITECTURE_V7_ENGINE.md §3.2 / ADR-046

Fournisseur d'embeddings dense basé sur BGE-M3 (BAAI/bge-m3, 1024 dimensions).
Utilise sentence-transformers si disponible, sinon flag_embedding, sinon un
fallback aléatoire déterministe pour les tests.
"""

import logging
from typing import List, Optional

import numpy as np

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "BAAI/bge-m3"
DEFAULT_DIM = 1024


class BGEEmbeddingProvider:
    """
    Fournisseur d'embeddings BGE-M3 avec fallback progressif.
    """

    def __init__(self, model_name: str = DEFAULT_MODEL):
        self.model_name = model_name
        self._model = None
        self._backend: Optional[str] = None

    def _load_model(self):
        if self._model is not None:
            return

        # Préférence 1 : sentence-transformers (dépendance principale BGE-M3)
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
            self._backend = "sentence-transformers"
            logger.info(f"BGE-M3 chargé via sentence-transformers ({self.model_name})")
            return
        except Exception as exc:
            logger.warning(f"sentence-transformers indisponible: {exc}")

        # Préférence 2 : flag_embedding (FlagModel)
        try:
            from flag_embedding import FlagModel
            self._model = FlagModel(self.model_name, use_fp16=True)
            self._backend = "flag_embedding"
            logger.info(f"BGE-M3 chargé via flag_embedding ({self.model_name})")
            return
        except Exception as exc:
            logger.warning(f"flag_embedding indisponible: {exc}")

        # Fallback : zéro external dependency
        self._backend = "fallback"
        self._model = "fallback"
        
        # BLOQUANT PRODUCTION : En prod, le fallback aléatoire est interdit
        import os
        env = os.getenv("APP_ENVIRONMENT", "development")
        if env == "production":
            logger.error("BGE-M3 indisponible en production - ARRÊT OBLIGATOIRE")
            raise RuntimeError(
                "CRITIQUE: Modèle BGE-M3 indisponible en production. "
                "Les embeddings aléatoires sont interdits en production car ils génèrent des analyses RAG incohérentes. "
                "Veuillez installer sentence-transformers ou flag_embedding avant de démarrer."
            )
        
        logger.warning("BGE-M3 fallback activé (embeddings aléatoires normalisés) - UNIQUEMENT POUR TESTS/DEV")

    def get_dimension(self) -> int:
        return DEFAULT_DIM

    def embed(self, text: str) -> Optional[List[float]]:
        """Encode un texte en vecteur BGE-M3 normalisé."""
        self._load_model()
        if not text:
            return None

        try:
            if self._backend == "sentence-transformers":
                emb = self._model.encode(text, normalize_embeddings=True)
            elif self._backend == "flag_embedding":
                emb = self._model.encode(text)
                norm = np.linalg.norm(emb)
                emb = emb / norm if norm > 0 else emb
            else:
                # Fallback déterministe par hash pour les tests
                rng = np.random.default_rng(seed=abs(hash(text)) % (2 ** 31))
                emb = rng.random(DEFAULT_DIM).astype(np.float32)
                norm = np.linalg.norm(emb)
                emb = emb / norm if norm > 0 else emb

            return emb.astype(float).tolist()
        except Exception as exc:
            logger.error(f"Erreur embedding BGE-M3: {exc}")
            return None

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Encode un batch de textes."""
        return [self.embed(t) for t in texts if t]

    def backend(self) -> Optional[str]:
        self._load_model()
        return self._backend


# Singleton projet
_embedding_provider: Optional[BGEEmbeddingProvider] = None


def get_embedding_provider(model_name: str = DEFAULT_MODEL) -> BGEEmbeddingProvider:
    global _embedding_provider
    if _embedding_provider is None:
        _embedding_provider = BGEEmbeddingProvider(model_name=model_name)
    return _embedding_provider
