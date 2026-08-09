"""
SMART_AO V7 - rate_limiting.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Rate Limiting Middleware
=======================================
Implémente le rate limiting pour protéger l'API contre les abus.
Utilise slowapi pour une intégration transparente avec FastAPI.

Source: ARCHITECTURE_V7_ENGINE.md §5 + ADR-046
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Limiter global pour l'API
limiter = Limiter(key_func=get_remote_address)


class RateLimitConfig:
    """Configuration centralisée du Rate Limiting."""

    # Limites par défaut (requêtes/minute)
    DEFAULT = "5/minute"

    # Limites pour les endpoints publics
    PUBLIC = "10/minute"

    # Limites pour les endpoints authentifiés
    AUTHENTICATED = "60/minute"

    # Limites pour les endpoints critiques (health, etc.)
    CRITICAL = "120/minute"

    # Limites pour les endpoints sensibles (LLM, exécution workflow, etc.)
    SENSITIVE = "5/minute"

    # Limites pour le développement
    DEVELOPMENT = "1000/minute"


# Configuration par endpoint (peut être override par endpoint)
# NOTE : slowapi applique les limites via le décorateur @limiter.limit.
# Ce dictionnaire sert de référence centrale pour les limites par path.
RATE_LIMITS = {
    # Health check - pas de limite
    "/api/v1/health": None,

    # Endpoints publics
    "/api/v1/missions": RateLimitConfig.PUBLIC,
    "/api/v1/agents": RateLimitConfig.PUBLIC,
    "/api/v1/documents": RateLimitConfig.PUBLIC,
    "/api/v1/workflows": RateLimitConfig.PUBLIC,

    # Endpoints sensibles
    "/api/v1/workflows/{mission_id}/execute": RateLimitConfig.SENSITIVE,
}


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """
    Handler pour les erreurs de rate limiting.
    Retourne une réponse JSON standardisée.
    """
    logger.warning(
        f"Rate limit exceeded: {request.client.host if request.client else 'unknown'} | "
        f"Path: {request.url.path} | "
        f"Detail: {exc.detail}"
    )

    retry_after = exc.retry_after if hasattr(exc, 'retry_after') else 60
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "detail": exc.detail,
            "path": str(request.url.path),
            "method": request.method,
            "retry_after": retry_after
        },
        headers={"Retry-After": str(retry_after)}
    )


def setup_rate_limiting(app: FastAPI, enabled: bool = True):
    """
    Configure le rate limiting pour l'application FastAPI.

    Args:
        app: Instance FastAPI
        enabled: Activer/désactiver le rate limiting

    Usage:
        from app.api.middleware.rate_limiting import setup_rate_limiting
        setup_rate_limiting(app)
    """
    if not enabled:
        logger.info("Rate limiting DÉSACTIVÉ")
        return

    # Attacher le limiter à l'application et ajouter le middleware slowapi
    # (idempotent : ne pas ré-ajouter si l'application a déjà démarré, pour les tests)
    app.state.limiter = limiter
    if getattr(app, "middleware_stack", None) is not None:
        logger.debug("Rate limiting déjà initialisé (application démarrée)")
        return

    app.add_middleware(SlowAPIMiddleware)

    # Ajouter l'exception handler (idempotent)
    if RateLimitExceeded not in app.exception_handlers:
        app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

    logger.info(
        f"Rate limiting ACTIVÉ | "
        f"Default: {RateLimitConfig.DEFAULT}"
    )


def get_rate_limit_for_path(path: str) -> Optional[str]:
    """
    Retourne la limite de rate pour un chemin donné.

    Args:
        path: Chemin de l'endpoint

    Returns:
        str: Limite au format "X/minute" ou None pour pas de limite
    """
    # Recherche exacte
    if path in RATE_LIMITS:
        return RATE_LIMITS[path]

    # Recherche par pattern (pour les paths avec paramètres)
    for pattern, limit in RATE_LIMITS.items():
        if pattern.replace("{", "").replace("}", "") in path:
            return limit

    # Retourne la limite par défaut
    return RateLimitConfig.DEFAULT


def apply_rate_limit(limit: Optional[str] = None):
    """
    Décorateur pour appliquer le rate limiting à un endpoint FastAPI.

    Args:
        limit: Limite spécifique (ex: "10/minute") ou None pour ne pas limiter.

    Usage:
        @app.get("/api/v1/health")
        @apply_rate_limit(None)
        async def health_check(request: Request):
            return {"status": "ok"}

        @app.get("/api/v1/missions")
        @apply_rate_limit(RateLimitConfig.PUBLIC)
        async def list_missions(request: Request):
            ...

    IMPORTANT : l'endpoint décoré DOIT déclarer un paramètre `request: Request`
    pour que slowapi puisse fonctionner correctement.
    """
    if limit is None:
        return lambda func: func
    return limiter.limit(limit)


# Configuration par défaut pour l'import
DEFAULT_RATE_LIMIT = RateLimitConfig.DEFAULT
