"""
SMART_AO V7 - resilience.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Circuit Breakers & Resilience
===========================================
Module de résilience pour éviter les cascades d'échecs.
Utilise une implémentation native du pattern Circuit Breaker.

Source: ARCHITECTURE_V7_ENGINE.md §5 + ADR-045
"""

from app.core.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerError,
    CircuitState
)
from functools import wraps
import logging
from typing import Callable, TypeVar, Any, Optional, List, Dict
import time

logger = logging.getLogger(__name__)

# Type variable pour les fonctions génériques
T = TypeVar('T')


class CircuitBreakerConfig:
    """Configuration centralisée des Circuit Breakers."""
    
    # Configuration par défaut pour les appels externes
    DEFAULT = {
        'fail_max': 3,
        'reset_timeout': 60,
        'excluded_exceptions': []
    }
    
    # Configuration pour les appels critiques (DB, LLM)
    CRITICAL = {
        'fail_max': 2,
        'reset_timeout': 120,
        'excluded_exceptions': []
    }
    
    # Configuration pour les appels non-critiques (API externes)
    EXTERNAL = {
        'fail_max': 5,
        'reset_timeout': 30,
        'excluded_exceptions': [ConnectionError]
    }


def create_circuit_breaker(name: str, config_type: str = 'DEFAULT') -> CircuitBreaker:
    """Fabrique un CircuitBreaker avec la configuration appropriée."""
    config = getattr(CircuitBreakerConfig, config_type, CircuitBreakerConfig.DEFAULT)
    
    breaker = CircuitBreaker(
        name=name,
        fail_max=config['fail_max'],
        reset_timeout=config['reset_timeout'],
        excluded_exceptions=tuple(config['excluded_exceptions'])
    )
    
    logger.info(f"CircuitBreaker créé: {name} | "
                f"fail_max={config['fail_max']}, "
                f"reset_timeout={config['reset_timeout']}s")
    
    return breaker


# Circuit Breakers (Singleton)
_circuit_breakers: Dict[str, CircuitBreaker] = {}

def get_circuit_breaker(name: str, config_type: str = 'DEFAULT') -> CircuitBreaker:
    """Récupère ou crée un CircuitBreaker (cache singleton)."""
    key = f"{name}:{config_type}"
    if key not in _circuit_breakers:
        _circuit_breakers[key] = create_circuit_breaker(name, config_type)
    return _circuit_breakers[key]


# Circuit Breakers par défaut pour V7
DB_BREAKER = get_circuit_breaker("db_access", "CRITICAL")
LLM_BREAKER = get_circuit_breaker("llm_calls", "CRITICAL")
QDRANT_BREAKER = get_circuit_breaker("qdrant_queries", "CRITICAL")
API_EXTERNAL_BREAKER = get_circuit_breaker("api_external", "EXTERNAL")
MINIO_BREAKER = get_circuit_breaker("minio_storage", "CRITICAL")


def circuit_breaker(breaker: CircuitBreaker = None, 
                  breaker_name: str = None,
                  config_type: str = 'DEFAULT'):
    """Decorateur Circuit Breaker pour fonctions sync."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            if breaker is not None:
                cb = breaker
            elif breaker_name:
                cb = get_circuit_breaker(breaker_name, config_type)
            else:
                cb = get_circuit_breaker(func.__name__)
            return cb.call(func, *args, **kwargs)
        return wrapper
    return decorator


def async_circuit_breaker(breaker: CircuitBreaker = None,
                              breaker_name: str = None,
                              config_type: str = 'DEFAULT'):
    """Decorateur Circuit Breaker pour fonctions async."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            if breaker is not None:
                cb = breaker
            elif breaker_name:
                cb = get_circuit_breaker(breaker_name, config_type)
            else:
                cb = get_circuit_breaker(func.__name__)
            return await cb.call_async(func, *args, **kwargs)
        return wrapper
    return decorator


def retry_on_failure(max_retries: int = 3, 
                    delay: float = 1.0,
                    backoff: float = 2.0,
                    exceptions: tuple = (Exception,)):
    """Decorateur Retry avec backoff exponentiel."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            current_delay = delay
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"Échec {attempt + 1}/{max_retries + 1} dans {func.__name__}: {e}. Retry dans {current_delay}s...")
                        time.sleep(current_delay)
                        current_delay *= backoff
            logger.error(f"Échec final dans {func.__name__} après {max_retries + 1} tentatives")
            raise last_exception
        return wrapper
    return decorator


def async_retry_on_failure(max_retries: int = 3,
                                 delay: float = 1.0,
                                 backoff: float = 2.0,
                                 exceptions: tuple = (Exception,)):
    """Decorateur Retry pour fonctions async."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None
            current_delay = delay
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"Échec async {attempt + 1}/{max_retries + 1} dans {func.__name__}: {e}. Retry dans {current_delay}s...")
                        time.sleep(current_delay)
                        current_delay *= backoff
            logger.error(f"Échec async final dans {func.__name__} après {max_retries + 1} tentatives")
            raise last_exception
        return wrapper
    return decorator


def with_fallback(fallback_value: Any = None, 
                 fallback_func: Callable = None):
    """Decorateur Fallback - Retourne une valeur par défaut en cas d'échec."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Fallback déclenché dans {func.__name__}: {e}")
                if fallback_func:
                    return fallback_func(e)
                return fallback_value
        return wrapper
    return decorator


def get_circuit_breaker_stats() -> dict:
    """Retourne les statistiques de tous les Circuit Breakers."""
    stats = {}
    for key, breaker in _circuit_breakers.items():
        stats[key] = {
            'state': breaker.current_state,
            'fail_count': breaker.fail_counter,
            'success_count': breaker.success_counter,
        }
    return stats


def reset_all_circuit_breakers():
    """Remet à zéro tous les Circuit Breakers."""
    for breaker in _circuit_breakers.values():
        breaker.reset()
    logger.info("Tous les Circuit Breakers ont été reset")
