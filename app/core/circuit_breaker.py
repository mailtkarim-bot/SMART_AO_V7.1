"""
SMART_AO V7 - circuit_breaker.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Circuit Breaker (Implémentation Native)
====================================================
Implémentation native du pattern Circuit Breaker compatible Python 3.12+.
Inspiré de pybreaker mais sans dépendances externes.

Source: ENGINEERING-HANDBOOK_V7.md §7 + ADR-045
"""

import asyncio
import time
import threading
from enum import Enum
from functools import wraps
from typing import Callable, TypeVar, Any, Optional, List, Tuple, Union
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


class CircuitState(Enum):
    """États possibles d'un Circuit Breaker."""
    CLOSED = "closed"      # Fonctionne normalement
    OPEN = "open"          # Circuit ouvert, ne passe pas les appels
    HALF_OPEN = "half_open"  # En test pour voir si le service est revenu


class CircuitBreakerError(Exception):
    """Exception levée quand le circuit est ouvert."""
    pass


class CircuitBreaker:
    """
    Implémentation native du Circuit Breaker pattern.
    Thread-safe pour une utilisation multi-thread.
    """
    
    def __init__(
        self,
        name: str = "default",
        fail_max: int = 3,
        reset_timeout: int = 60,
        excluded_exceptions: Optional[Tuple[type]] = None,
        success_threshold: int = 1
    ):
        """
        Initialise un Circuit Breaker.
        
        Args:
            name: Nom du circuit breaker (pour logging)
            fail_max: Nombre max d'échecs consécutifs avant ouverture
            reset_timeout: Temps en secondes avant réessai (half-open)
            excluded_exceptions: Exceptions à ne pas compter comme échecs
            success_threshold: Nombre de succès nécessaires pour fermer depuis half-open
        """
        self.name = name
        self.fail_max = fail_max
        self.reset_timeout = reset_timeout
        self.excluded_exceptions = excluded_exceptions or ()
        self.success_threshold = success_threshold
        
        # État interne
        self._state = CircuitState.CLOSED
        self._fail_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[float] = None
        self._last_success_time: Optional[float] = None
        self._last_reset_time: Optional[float] = None
        
        # Verrou pour thread-safety
        self._lock = threading.RLock()
        
        logger.info(
            f"CircuitBreaker créé: {name} | "
            f"fail_max={fail_max}, reset_timeout={reset_timeout}s"
        )
    
    @property
    def state(self) -> CircuitState:
        """Retourne l'état actuel du circuit."""
        return self._state
    
    @property
    def current_state(self) -> str:
        """Retourne l'état actuel sous forme de string."""
        return self._state.value
    
    @property
    def fail_counter(self) -> int:
        """Retourne le compteur d'échecs."""
        return self._fail_count
    
    @property
    def success_counter(self) -> int:
        """Retourne le compteur de succès."""
        return self._success_count
    
    def _should_exclude(self, exception: Exception) -> bool:
        """Vérifie si l'exception doit être exclue."""
        return isinstance(exception, self.excluded_exceptions)
    
    def _can_retry(self) -> bool:
        """Vérifie si on peut réessayer (reset_timeout écoulé)."""
        if self._state != CircuitState.OPEN:
            return False
        
        if self._last_failure_time is None:
            return True
        
        elapsed = time.time() - self._last_failure_time
        return elapsed >= self.reset_timeout
    
    def _transition_to_open(self):
        """Passe à l'état OPEN."""
        with self._lock:
            self._state = CircuitState.OPEN
            self._last_failure_time = time.time()
            self._last_reset_time = time.time()
            logger.warning(f"Circuit {self.name} PASSE EN ÉTAT OPEN")
    
    def _transition_to_half_open(self):
        """Passe à l'état HALF_OPEN."""
        with self._lock:
            self._state = CircuitState.HALF_OPEN
            logger.info(f"Circuit {self.name} PASSE EN ÉTAT HALF_OPEN")
    
    def _transition_to_closed(self):
        """Passe à l'état CLOSED."""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._fail_count = 0
            self._success_count = 0
            self._last_reset_time = time.time()
            logger.info(f"Circuit {self.name} PASSE EN ÉTAT CLOSED")
    
    def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """
        Appelle une fonction sync avec circuit breaker.
        
        Args:
            func: Fonction à appeler
            *args: Arguments positionnels
            **kwargs: Arguments nommés
        
        Returns:
            Résultat de la fonction
        
        Raises:
            CircuitBreakerError: Si le circuit est ouvert
            Exception: Si la fonction échoue
        """
        with self._lock:
            # Vérifier l'état
            if self._state == CircuitState.OPEN:
                if not self._can_retry():
                    raise CircuitBreakerError(
                        f"Circuit {self.name} est OPEN. "
                        f"Réessayez dans {self.reset_timeout - (time.time() - self._last_failure_time):.1f}s."
                    )
                else:
                    # Passer en HALF_OPEN pour un essai
                    self._transition_to_half_open()
            
            # Si HALF_OPEN, on compte les succès
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
        
        try:
            result = func(*args, **kwargs)
            
            with self._lock:
                # Réussite
                if self._state == CircuitState.HALF_OPEN:
                    if self._success_count >= self.success_threshold:
                        self._transition_to_closed()
                self._last_success_time = time.time()
                self._fail_count = 0
            
            return result
            
        except Exception as e:
            with self._lock:
                # Vérifier si on exclut cette exception
                if self._should_exclude(e):
                    logger.warning(f"Exception exclue dans {self.name}: {type(e).__name__}")
                    raise
                
                # Échec
                self._fail_count += 1
                self._last_failure_time = time.time()
                
                if self._state == CircuitState.HALF_OPEN:
                    # Un échec en HALF_OPEN → OPEN
                    self._transition_to_open()
                elif self._fail_count >= self.fail_max:
                    # Assez d'échecs → OPEN
                    self._transition_to_open()
            
            raise
    
    async def call_async(self, func: Callable[..., T], *args, **kwargs) -> T:
        """
        Appelle une fonction async avec circuit breaker.
        
        Args:
            func: Fonction async à appeler
            *args: Arguments positionnels
            **kwargs: Arguments nommés
        
        Returns:
            Résultat de la fonction
        
        Raises:
            CircuitBreakerError: Si le circuit est ouvert
            Exception: Si la fonction échoue
        """
        with self._lock:
            # Vérifier l'état
            if self._state == CircuitState.OPEN:
                if not self._can_retry():
                    raise CircuitBreakerError(
                        f"Circuit {self.name} est OPEN. "
                        f"Réessayez dans {self.reset_timeout - (time.time() - self._last_failure_time):.1f}s."
                    )
                else:
                    # Passer en HALF_OPEN pour un essai
                    self._transition_to_half_open()
            
            # Si HALF_OPEN, on compte les succès
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
        
        try:
            result = await func(*args, **kwargs)
            
            with self._lock:
                # Réussite
                if self._state == CircuitState.HALF_OPEN:
                    if self._success_count >= self.success_threshold:
                        self._transition_to_closed()
                self._last_success_time = time.time()
                self._fail_count = 0
            
            return result
            
        except Exception as e:
            with self._lock:
                # Vérifier si on exclut cette exception
                if self._should_exclude(e):
                    logger.warning(f"Exception exclue dans {self.name}: {type(e).__name__}")
                    raise
                
                # Échec
                self._fail_count += 1
                self._last_failure_time = time.time()
                
                if self._state == CircuitState.HALF_OPEN:
                    # Un échec en HALF_OPEN → OPEN
                    self._transition_to_open()
                elif self._fail_count >= self.fail_max:
                    # Assez d'échecs → OPEN
                    self._transition_to_open()
            
            raise
    
    def reset(self):
        """Remet à zéro le circuit breaker."""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._fail_count = 0
            self._success_count = 0
            self._last_failure_time = None
            self._last_success_time = None
            self._last_reset_time = time.time()
            logger.info(f"Circuit {self.name} RESET")
    
    def open(self):
        """Force l'ouverture du circuit."""
        with self._lock:
            self._transition_to_open()
    
    def close(self):
        """Force la fermeture du circuit."""
        with self._lock:
            self._transition_to_closed()
    
    def __repr__(self) -> str:
        return f"CircuitBreaker(name={self.name}, state={self._state.value}, fails={self._fail_count})"
