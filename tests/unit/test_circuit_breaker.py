"""
SMART_AO V7 - test_circuit_breaker.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Tests Circuit Breakers
====================================
Tests unitaires pour le module de résilience (circuit breakers).
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from app.core.resilience import (
    CircuitBreakerError,
    CircuitBreakerConfig,
    create_circuit_breaker,
    get_circuit_breaker,
    DB_BREAKER,
    LLM_BREAKER,
    QDRANT_BREAKER,
    MINIO_BREAKER,
    circuit_breaker,
    async_circuit_breaker,
    retry_on_failure,
    async_retry_on_failure,
    with_fallback,
    get_circuit_breaker_stats,
    reset_all_circuit_breakers
)
from app.core.circuit_breaker import CircuitState
import time


class TestCircuitBreakerConfig:
    """Tests de configuration des Circuit Breakers."""
    
    def test_default_config(self):
        """Test de la configuration par défaut."""
        assert CircuitBreakerConfig.DEFAULT['fail_max'] == 3
        assert CircuitBreakerConfig.DEFAULT['reset_timeout'] == 60
    
    def test_critical_config(self):
        """Test de la configuration critique."""
        assert CircuitBreakerConfig.CRITICAL['fail_max'] == 2
        assert CircuitBreakerConfig.CRITICAL['reset_timeout'] == 120
    
    def test_external_config(self):
        """Test de la configuration externe."""
        assert CircuitBreakerConfig.EXTERNAL['fail_max'] == 5
        assert CircuitBreakerConfig.EXTERNAL['reset_timeout'] == 30


class TestCircuitBreakerCreation:
    """Tests de création des Circuit Breakers."""
    
    def test_create_circuit_breaker_default(self):
        """Test de création avec config par défaut."""
        breaker = create_circuit_breaker("test_breaker")
        assert breaker is not None
        assert breaker.fail_max == 3
        assert breaker.reset_timeout == 60
    
    def test_create_circuit_breaker_critical(self):
        """Test de création avec config critique."""
        breaker = create_circuit_breaker("test_critical", "CRITICAL")
        assert breaker.fail_max == 2
        assert breaker.reset_timeout == 120
    
    def test_create_circuit_breaker_external(self):
        """Test de création avec config externe."""
        breaker = create_circuit_breaker("test_external", "EXTERNAL")
        assert breaker.fail_max == 5
        assert breaker.reset_timeout == 30


class TestCircuitBreakerSingleton:
    """Tests du pattern Singleton pour les Circuit Breakers."""
    
    def test_get_circuit_breaker_singleton(self):
        """Test que get_circuit_breaker retourne la même instance."""
        breaker1 = get_circuit_breaker("singleton_test")
        breaker2 = get_circuit_breaker("singleton_test")
        assert breaker1 is breaker2
    
    def test_get_circuit_breaker_different_config(self):
        """Test que des configs différentes créent des instances différentes."""
        breaker_default = get_circuit_breaker("config_test", "DEFAULT")
        breaker_critical = get_circuit_breaker("config_test", "CRITICAL")
        assert breaker_default is not breaker_critical


class TestPredefinedBreakers:
    """Tests des Circuit Breakers pré-définis."""
    
    def test_db_breaker_exists(self):
        """Test que DB_BREAKER existe."""
        assert DB_BREAKER is not None
        assert DB_BREAKER.fail_max == 2
    
    def test_llm_breaker_exists(self):
        """Test que LLM_BREAKER existe."""
        assert LLM_BREAKER is not None
        assert LLM_BREAKER.fail_max == 2
    
    def test_qdrant_breaker_exists(self):
        """Test que QDRANT_BREAKER existe."""
        assert QDRANT_BREAKER is not None
        assert QDRANT_BREAKER.fail_max == 2
    
    def test_minio_breaker_exists(self):
        """Test que MINIO_BREAKER existe."""
        assert MINIO_BREAKER is not None
        assert MINIO_BREAKER.fail_max == 2


class TestCircuitBreakerDecorator:
    """Tests du décorateur circuit_breaker."""
    
    def test_circuit_breaker_success(self):
        """Test que le décorateur laisse passer les appels réussis."""
        call_count = 0
        
        @circuit_breaker(breaker_name="test_decorator_success")
        def successful_function():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = successful_function()
        assert result == "success"
        assert call_count == 1
    
    def test_circuit_breaker_with_predefined_breaker(self):
        """Test avec un breaker pré-défini."""
        call_count = 0
        
        @circuit_breaker(breaker=DB_BREAKER)
        def db_function():
            nonlocal call_count
            call_count += 1
            return "db_result"
        
        result = db_function()
        assert result == "db_result"
        assert call_count == 1
    
    def test_circuit_breaker_failure(self):
        """Test que le décorateur compte les échecs."""
        @circuit_breaker(breaker_name="test_decorator_failure")
        def failing_function():
            raise ValueError("Test error")
        
        # Premier appel devrait échouer
        with pytest.raises(ValueError):
            failing_function()
        
        # Deuxième appel devrait aussi échouer (le breaker n'est pas encore ouvert)
        with pytest.raises(ValueError):
            failing_function()
    
    def test_circuit_breaker_trips(self):
        """Test que le circuit s'ouvre après trop d'échecs."""
        @circuit_breaker(breaker_name="test_trip", config_type="CRITICAL")
        def always_failing():
            raise ValueError("Always fails")
        
        # Faire échouer 2 fois (fail_max=2 pour CRITICAL)
        with pytest.raises(ValueError):
            always_failing()
        with pytest.raises(ValueError):
            always_failing()
        
        # La troisième tentative devrait déclencher CircuitBreakerError
        with pytest.raises(CircuitBreakerError):
            always_failing()


class TestRetryDecorator:
    """Tests du décorateur retry_on_failure."""
    
    def test_retry_success_first_attempt(self):
        """Test que la première tentative réussie ne retry pas."""
        call_count = 0
        
        @retry_on_failure(max_retries=3, delay=0.01)
        def successful_function():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = successful_function()
        assert result == "success"
        assert call_count == 1
    
    def test_retry_success_after_failures(self):
        """Test que le retry fonctionne après des échecs."""
        call_count = 0
        
        @retry_on_failure(max_retries=3, delay=0.01)
        def sometimes_failing():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Not yet")
            return "success"
        
        result = sometimes_failing()
        assert result == "success"
        assert call_count == 3
    
    def test_retry_exhausted(self):
        """Test que l'exception est levée après épuisement des retries."""
        call_count = 0
        
        @retry_on_failure(max_retries=2, delay=0.01)
        def always_failing():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError):
            always_failing()
        
        assert call_count == 3  # 1 initial + 2 retries


class TestFallbackDecorator:
    """Tests du décorateur with_fallback."""
    
    def test_fallback_with_value(self):
        """Test du fallback avec une valeur par défaut."""
        @with_fallback(fallback_value="default")
        def failing_function():
            raise ValueError("Error")
        
        result = failing_function()
        assert result == "default"
    
    def test_fallback_with_function(self):
        """Test du fallback avec une fonction."""
        @with_fallback(fallback_func=lambda e: f"fallback:{str(e)}")
        def failing_function():
            raise ValueError("test_error")
        
        result = failing_function()
        assert result == "fallback:test_error"
    
    def test_fallback_no_error(self):
        """Test que le fallback ne s'applique pas si pas d'erreur."""
        @with_fallback(fallback_value="default")
        def successful_function():
            return "success"
        
        result = successful_function()
        assert result == "success"


class TestCircuitBreakerStats:
    """Tests des statistiques des Circuit Breakers."""
    
    def test_get_stats(self):
        """Test de la récupération des statistiques."""
        from app.core.resilience import get_circuit_breaker_stats, DB_BREAKER
        
        # Les breakers pré-défini sont déjà créés
        stats = get_circuit_breaker_stats()
        # Vérifier que DB_BREAKER existe dans les stats
        assert any("db_access:CRITICAL" in key for key in stats.keys())
        
        # Trouver le bon breaker dans les stats
        db_stats = next((v for k, v in stats.items() if "db_access" in k), None)
        assert db_stats is not None
        # Vérifier que le breaker est en état closed
        assert db_stats['state'] == 'closed'
        # Le success_count est 0 en état CLOSED (seul HALF_OPEN compte les succès)
        # C'est le comportement correct du pattern Circuit Breaker
    
    def test_reset_breakers(self):
        """Test du reset de tous les breakers."""
        # Utiliser un breaker pré-défini
        from app.core.resilience import DB_BREAKER
        
        @circuit_breaker(breaker=DB_BREAKER)
        def failing_function():
            raise ValueError("Error")
        
        # Faire échouer
        with pytest.raises(ValueError):
            failing_function()
        
        # Vérifier que le breaker a des échecs
        stats_before = get_circuit_breaker_stats()
        db_stats_before = next((v for k, v in stats_before.items() if "db_access" in k), None)
        assert db_stats_before is not None
        assert db_stats_before['fail_count'] >= 1
        
        # Reset
        reset_all_circuit_breakers()
        
        # Vérifier que les stats sont remises à zéro
        stats_after = get_circuit_breaker_stats()
        db_stats_after = next((v for k, v in stats_after.items() if "db_access" in k), None)
        assert db_stats_after is not None
        assert db_stats_after['fail_count'] == 0


class TestAsyncDecorators:
    """Tests des décorateurs async."""
    
    @pytest.mark.asyncio
    async def test_async_circuit_breaker(self):
        """Test du décorateur async_circuit_breaker."""
        call_count = 0
        
        # Corriger: async_circuit_breaker retourne un coroutine, il faut l'appeler
        @async_circuit_breaker(breaker_name="async_test")
        async def async_function():
            nonlocal call_count
            call_count += 1
            return "async_success"
        
        # Appeler directement sans await dans le décorateur
        result = await async_function()
        assert result == "async_success"
        assert call_count == 1
    
    @pytest.mark.asyncio
    async def test_async_retry(self):
        """Test du décorateur async_retry_on_failure."""
        call_count = 0
        
        @async_retry_on_failure(max_retries=2, delay=0.01)
        async def async_sometimes_failing():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Not yet")
            return "async_success"
        
        result = await async_sometimes_failing()
        assert result == "async_success"
        assert call_count == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
