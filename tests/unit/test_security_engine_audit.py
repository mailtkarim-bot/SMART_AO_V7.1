"""
SMART_AO V7 - Tests unitaires complets pour security_engine/audit.py
==================================================================
Tests complets pour toutes les classes et fonctions du module audit.
Cible: 90%+ couverture
"""

import pytest
import json
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock

from app.engines.security_engine.audit import (
    AuditAction,
    AuditLevel,
    AuditLog,
    CalculationAuditLog,
    AuditEvent,
    AuditQuery,
    AuditStats,
    AuditService,
    get_audit_service,
    log_audit_event,
    audit_action,
    log_calculation_audit,
)


# =============================================================================
# Tests pour les Enum
# =============================================================================

class TestAuditAction:
    """Tests pour AuditAction."""

    def test_all_values_exist(self):
        assert AuditAction.LOGIN.value == "LOGIN"
        assert AuditAction.LOGOUT.value == "LOGOUT"
        assert AuditAction.LOGIN_FAILED.value == "LOGIN_FAILED"
        assert AuditAction.MISSION_CREATED.value == "MISSION_CREATED"
        assert AuditAction.MISSION_UPDATED.value == "MISSION_UPDATED"
        assert AuditAction.MISSION_DELETED.value == "MISSION_DELETED"
        assert AuditAction.MISSION_STATUS_CHANGED.value == "MISSION_STATUS_CHANGED"
        assert AuditAction.DOCUMENT_UPLOADED.value == "DOCUMENT_UPLOADED"
        assert AuditAction.DOCUMENT_DOWNLOADED.value == "DOCUMENT_DOWNLOADED"
        assert AuditAction.DOCUMENT_DELETED.value == "DOCUMENT_DELETED"
        assert AuditAction.DOCUMENT_SCANNED.value == "DOCUMENT_SCANNED"
        assert AuditAction.AGENT_EXECUTED.value == "AGENT_EXECUTED"
        assert AuditAction.AGENT_FAILED.value == "AGENT_FAILED"
        assert AuditAction.CONFIG_UPDATED.value == "CONFIG_UPDATED"
        assert AuditAction.USER_CREATED.value == "USER_CREATED"
        assert AuditAction.USER_UPDATED.value == "USER_UPDATED"
        assert AuditAction.USER_DELETED.value == "USER_DELETED"
        assert AuditAction.RBAC_CHANGED.value == "RBAC_CHANGED"
        assert AuditAction.PERMISSION_GRANTED.value == "PERMISSION_GRANTED"
        assert AuditAction.PERMISSION_REVOKED.value == "PERMISSION_REVOKED"
        assert AuditAction.SYSTEM_STARTED.value == "SYSTEM_STARTED"
        assert AuditAction.SYSTEM_SHUTDOWN.value == "SYSTEM_SHUTDOWN"
        assert AuditAction.BACKUP_CREATED.value == "BACKUP_CREATED"


class TestAuditLevel:
    """Tests pour AuditLevel."""

    def test_all_values_exist(self):
        assert AuditLevel.DEBUG.value == "DEBUG"
        assert AuditLevel.INFO.value == "INFO"
        assert AuditLevel.WARNING.value == "WARNING"
        assert AuditLevel.ERROR.value == "ERROR"
        assert AuditLevel.CRITICAL.value == "CRITICAL"


# =============================================================================
# Tests pour les modeles SQLAlchemy
# =============================================================================

class TestAuditLog:
    """Tests pour AuditLog."""

    def test_table_name(self):
        assert AuditLog.__tablename__ == "audit_logs"

    def test_all_columns_exist(self):
        for col in ['id', 'event_id', 'timestamp', 'user_id', 'username', 'role',
                    'action', 'level', 'resource_type', 'resource_id', 'details',
                    'ip_address', 'user_agent', 'hash', 'is_modified']:
            assert hasattr(AuditLog, col)

    def test_has_indexes(self):
        assert hasattr(AuditLog, '__table_args__')


class TestCalculationAuditLog:
    """Tests pour CalculationAuditLog."""

    def test_table_name(self):
        assert CalculationAuditLog.__tablename__ == "calculation_audit_logs"

    def test_all_columns_exist(self):
        for col in ['id', 'calculation_id', 'timestamp', 'user_id', 'username', 'role',
                    'mission_id', 'calculation_type', 'input_hash', 'output_hash',
                    'input_data', 'output_data', 'solver_version', 'duration_ms',
                    'hash', 'is_modified']:
            assert hasattr(CalculationAuditLog, col)


# =============================================================================
# Tests pour les dataclasses
# =============================================================================

class TestAuditEvent:
    """Tests pour AuditEvent."""

    def test_creation_minimal(self):
        event = AuditEvent(action=AuditAction.LOGIN)
        assert event.action == AuditAction.LOGIN
        assert event.level == AuditLevel.INFO
        assert event.event_id is not None
        assert event.timestamp is not None
        assert event.user_id is None
        assert event.details == {}

    def test_creation_full(self):
        custom_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        event = AuditEvent(
            action=AuditAction.LOGIN,
            level=AuditLevel.WARNING,
            user_id="user123",
            username="john.doe",
            role="admin",
            resource_type="mission",
            resource_id="mission456",
            details={"status": "success"},
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            event_id="custom_event_id",
            timestamp=custom_time
        )
        assert event.action == AuditAction.LOGIN
        assert event.level == AuditLevel.WARNING
        assert event.user_id == "user123"
        assert event.username == "john.doe"
        assert event.event_id == "custom_event_id"
        assert event.timestamp == custom_time

    def test_to_dict(self):
        event = AuditEvent(
            action=AuditAction.LOGIN,
            user_id="user123",
            username="john.doe"
        )
        d = event.to_dict()
        assert "event_id" in d
        assert "timestamp" in d
        assert d["action"] == "LOGIN"
        assert d["user_id"] == "user123"

    def test_compute_hash(self):
        event = AuditEvent(
            action=AuditAction.LOGIN,
            user_id="user123",
            username="john.doe"
        )
        hash1 = event.compute_hash()
        hash2 = event.compute_hash()
        assert hash1 == hash2
        assert len(hash1) == 64

    def test_different_events_different_hashes(self):
        event1 = AuditEvent(action=AuditAction.LOGIN, user_id="user123")
        event2 = AuditEvent(action=AuditAction.LOGOUT, user_id="user123")
        assert event1.compute_hash() != event2.compute_hash()


class TestAuditQuery:
    """Tests pour AuditQuery."""

    def test_default_values(self):
        query = AuditQuery()
        assert query.user_id is None
        assert query.action is None
        assert query.limit == 100
        assert query.offset == 0

    def test_custom_values(self):
        start = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end = datetime(2024, 1, 2, tzinfo=timezone.utc)
        query = AuditQuery(
            user_id="user123",
            action=AuditAction.LOGIN,
            level=AuditLevel.ERROR,
            start_time=start,
            end_time=end,
            limit=50,
            offset=10
        )
        assert query.user_id == "user123"
        assert query.action == AuditAction.LOGIN
        assert query.limit == 50


class TestAuditStats:
    """Tests pour AuditStats."""

    def test_default_values(self):
        stats = AuditStats()
        assert stats.total_events == 0
        assert stats.events_by_action == {}
        assert stats.recent_events == []

    def test_custom_values(self):
        stats = AuditStats(
            total_events=100,
            events_by_action={"LOGIN": 50},
            events_by_level={"INFO": 100},
            events_by_user={"user1": 60}
        )
        assert stats.total_events == 100
        assert stats.events_by_action["LOGIN"] == 50


# =============================================================================
# Tests pour AuditService
# =============================================================================

class TestAuditService:
    """Tests pour AuditService."""

    def test_init(self):
        service = AuditService()
        assert service.events == []
        assert service.calculation_events == []
        assert service._initialized is False

    def test_singleton(self):
        import app.engines.security_engine.audit as audit_module
        audit_module._audit_service = None
        service1 = get_audit_service()
        service2 = get_audit_service()
        assert service1 is service2

    def test_initialize_method_exists(self):
        """Test que la methode initialize existe."""
        service = AuditService()
        assert hasattr(service, 'initialize')
        assert callable(service.initialize)

    def test_create_event_from_dict_valid(self):
        service = AuditService()
        data = {
            "action": "LOGIN",
            "level": "INFO",
            "user_id": "user_001",
            "username": "john.doe",
            "role": "PATRON",
            "resource_type": "mission",
            "resource_id": "mission_001",
            "details": {"status": "success"},
            "ip_address": "192.168.1.1",
            "user_agent": "Mozilla/5.0",
            "event_id": "event_001",
            "timestamp": "2024-01-01T12:00:00+00:00"
        }
        event = service._create_event_from_dict(data)
        assert isinstance(event, AuditEvent)
        assert event.action == AuditAction.LOGIN
        assert event.user_id == "user_001"
        assert event.event_id == "event_001"

    def test_create_event_from_dict_invalid_action(self):
        service = AuditService()
        data = {"action": "INVALID", "level": "INFO"}
        event = service._create_event_from_dict(data)
        assert event.action == AuditAction.LOGIN

    def test_create_event_from_dict_invalid_level(self):
        service = AuditService()
        data = {"action": "LOGIN", "level": "INVALID"}
        event = service._create_event_from_dict(data)
        assert event.level == AuditLevel.INFO

    @pytest.mark.asyncio
    async def test_log_event_in_memory(self):
        service = AuditService()
        event = AuditEvent(action=AuditAction.LOGIN, user_id="user_001")
        event_id = await service.log_event(event)
        assert len(service.events) == 1
        assert service.events[0] is event

    @pytest.mark.asyncio
    async def test_log_event_with_db(self):
        service = AuditService()
        mock_db = AsyncMock()
        event = AuditEvent(action=AuditAction.LOGIN, user_id="user_001")
        await service.log_event(event, mock_db)
        assert mock_db.add.called
        assert mock_db.commit.called

    @pytest.mark.asyncio
    async def test_log_event_db_error(self):
        service = AuditService()
        mock_db = AsyncMock()
        mock_db.add.side_effect = Exception("DB Error")
        event = AuditEvent(action=AuditAction.LOGIN, user_id="user_001")
        await service.log_event(event, mock_db)
        # L'evenement doit quand meme etre en memoire
        assert len(service.events) == 1

    @pytest.mark.asyncio
    async def test_log_action_basic(self):
        service = AuditService()
        event_id = await service.log_action(
            action=AuditAction.LOGIN,
            user={"user_id": "user_001"},
            resource={"type": "mission", "id": "mission_001"}
        )
        assert len(service.events) == 1
        assert service.events[0].action == AuditAction.LOGIN

    @pytest.mark.asyncio
    async def test_query_events_no_filter(self):
        service = AuditService()
        await service.log_action(action=AuditAction.LOGIN, user={"user_id": "user_001"})
        await service.log_action(action=AuditAction.LOGOUT, user={"user_id": "user_001"})
        query = AuditQuery(limit=10)
        results = await service.query_events(query)
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_query_events_filter_by_action(self):
        service = AuditService()
        await service.log_action(action=AuditAction.LOGIN, user={"user_id": "user_001"})
        await service.log_action(action=AuditAction.LOGOUT, user={"user_id": "user_001"})
        query = AuditQuery(action=AuditAction.LOGIN, limit=10)
        results = await service.query_events(query)
        assert len(results) == 1
        assert results[0]["action"] == "LOGIN"

    @pytest.mark.asyncio
    async def test_query_events_filter_by_user_id(self):
        service = AuditService()
        await service.log_action(action=AuditAction.LOGIN, user={"user_id": "user_001"})
        await service.log_action(action=AuditAction.LOGIN, user={"user_id": "user_002"})
        query = AuditQuery(user_id="user_001", limit=10)
        results = await service.query_events(query)
        assert len(results) == 1
        assert results[0]["user_id"] == "user_001"

    @pytest.mark.asyncio
    async def test_query_events_filter_by_resource_type(self):
        service = AuditService()
        await service.log_action(
            action=AuditAction.DOCUMENT_UPLOADED,
            user={"user_id": "user_001"},
            resource={"type": "document", "id": "doc_001"}
        )
        query = AuditQuery(resource_type="document", limit=10)
        results = await service.query_events(query)
        assert len(results) == 1
        assert results[0]["resource_type"] == "document"

    @pytest.mark.asyncio
    async def test_query_events_filter_by_level(self):
        service = AuditService()
        await service.log_action(
            action=AuditAction.LOGIN,
            user={"user_id": "user_001"},
            level=AuditLevel.INFO
        )
        await service.log_action(
            action=AuditAction.LOGIN_FAILED,
            user={"user_id": "user_002"},
            level=AuditLevel.WARNING
        )
        query = AuditQuery(level=AuditLevel.INFO, limit=10)
        results = await service.query_events(query)
        assert len(results) == 1
        assert results[0]["level"] == "INFO"

    @pytest.mark.asyncio
    async def test_query_events_pagination(self):
        service = AuditService()
        for i in range(5):
            await service.log_action(action=AuditAction.LOGIN, user={"user_id": f"user_{i:03d}"})
        query = AuditQuery(limit=2, offset=0)
        results = await service.query_events(query)
        assert len(results) == 2
        query = AuditQuery(limit=2, offset=4)
        results = await service.query_events(query)
        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_query_events_empty(self):
        service = AuditService()
        query = AuditQuery(action=AuditAction.LOGOUT, limit=10)
        results = await service.query_events(query)
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_query_events_with_db(self):
        service = AuditService()
        mock_db = AsyncMock()
        mock_audit_log = MagicMock()
        mock_audit_log.event_id = "event_001"
        mock_audit_log.timestamp = datetime(2024, 1, 1, tzinfo=timezone.utc)
        mock_audit_log.action = "LOGIN"
        mock_audit_log.level = "INFO"
        mock_audit_log.user_id = "user_001"
        mock_audit_log.username = None
        mock_audit_log.role = None
        mock_audit_log.resource_type = None
        mock_audit_log.resource_id = None
        mock_audit_log.details = None
        mock_audit_log.ip_address = None
        mock_audit_log.user_agent = None
        mock_audit_log.hash = "abc123"
        mock_audit_log.is_modified = False
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_audit_log]
        mock_db.execute.return_value = mock_result
        query = AuditQuery(limit=10)
        results = await service.query_events(query, mock_db)
        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_query_events_db_error(self):
        service = AuditService()
        mock_db = AsyncMock()
        mock_db.execute.side_effect = Exception("DB Error")
        query = AuditQuery(limit=10)
        results = await service.query_events(query, mock_db)
        assert results == []

    @pytest.mark.asyncio
    async def test_get_stats_basic(self):
        service = AuditService()
        await service.log_action(
            action=AuditAction.LOGIN,
            user={"user_id": "user_001"},
            level=AuditLevel.INFO
        )
        await service.log_action(
            action=AuditAction.LOGIN,
            user={"user_id": "user_002"},
            level=AuditLevel.INFO
        )
        await service.log_action(
            action=AuditAction.LOGOUT,
            user={"user_id": "user_001"},
            level=AuditLevel.WARNING
        )
        stats = await service.get_stats(days=30)
        assert stats.total_events == 3
        assert stats.events_by_action["LOGIN"] == 2
        assert stats.events_by_action["LOGOUT"] == 1
        assert stats.events_by_level["INFO"] == 2
        assert stats.events_by_level["WARNING"] == 1
        assert stats.events_by_user["user_001"] == 2
        assert stats.events_by_user["user_002"] == 1

    @pytest.mark.asyncio
    async def test_get_stats_empty(self):
        service = AuditService()
        stats = await service.get_stats(days=30)
        assert stats.total_events == 0

    @pytest.mark.asyncio
    async def test_export_events_json(self):
        service = AuditService()
        await service.log_action(
            action=AuditAction.LOGIN,
            user={"user_id": "user_001"}
        )
        query = AuditQuery(limit=10)
        result = await service.export_events(query, format="json")
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert len(parsed) == 1

    @pytest.mark.asyncio
    async def test_export_events_csv(self):
        service = AuditService()
        await service.log_action(
            action=AuditAction.LOGIN,
            user={"user_id": "user_001"}
        )
        query = AuditQuery(limit=10)
        result = await service.export_events(query, format="csv")
        assert isinstance(result, bytes)
        csv_text = result.decode('utf-8')
        assert "event_id" in csv_text

    @pytest.mark.asyncio
    async def test_export_events_invalid_format(self):
        service = AuditService()
        query = AuditQuery(limit=10)
        with pytest.raises(ValueError):
            await service.export_events(query, format="xml")

    @pytest.mark.asyncio
    async def test_export_events_empty(self):
        service = AuditService()
        query = AuditQuery(limit=10)
        result_json = await service.export_events(query, format="json")
        assert result_json == "[]"
        result_csv = await service.export_events(query, format="csv")
        assert b"event_id" in result_csv


# =============================================================================
# Tests pour les fonctions utilitaires
# =============================================================================

class TestGetAuditService:
    """Tests pour get_audit_service."""

    def test_returns_instance(self):
        import app.engines.security_engine.audit as audit_module
        audit_module._audit_service = None
        service = get_audit_service()
        assert isinstance(service, AuditService)


class TestLogAuditEvent:
    """Tests pour log_audit_event."""

    @pytest.mark.asyncio
    async def test_basic(self):
        import app.engines.security_engine.audit as audit_module
        audit_module._audit_service = None
        event_id = await log_audit_event(
            action=AuditAction.LOGIN,
            user={"user_id": "user_001"}
        )
        assert isinstance(event_id, str)


class TestAuditActionDecorator:
    """Tests pour audit_action."""

    @pytest.mark.asyncio
    async def test_basic(self):
        import app.engines.security_engine.audit as audit_module
        audit_module._audit_service = None

        @audit_action(AuditAction.LOGIN, resource_type="mission")
        async def test_function(current_user, resource_id="mission_001"):
            return {"status": "success"}

        class MockUser:
            user_id = "user_001"
            username = "john"
            role = "ADMIN"

        result = await test_function(MockUser(), resource_id="mission_001")
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_without_user(self):
        import app.engines.security_engine.audit as audit_module
        audit_module._audit_service = None

        @audit_action(AuditAction.SYSTEM_STARTED)
        async def test_function():
            return {"status": "success"}

        result = await test_function()
        assert result["status"] == "success"


class TestLogCalculationAudit:
    """Tests pour log_calculation_audit."""

    @pytest.mark.asyncio
    async def test_basic(self):
        import app.engines.security_engine.audit as audit_module
        audit_module._audit_service = None
        calc_id = await log_calculation_audit(
            calculation_type="marge",
            input_data={"montant": 1000},
            output_data={"result": 1200}
        )
        assert isinstance(calc_id, str)

    @pytest.mark.asyncio
    async def test_computes_hashes(self):
        import app.engines.security_engine.audit as audit_module
        audit_module._audit_service = None
        await log_calculation_audit(
            calculation_type="marge",
            input_data={"montant": 1000},
            output_data={"result": 1200}
        )
        service = get_audit_service()
        event = service.calculation_events[0]
        assert "input_hash" in event
        assert "output_hash" in event
        assert len(event["input_hash"]) == 64

    @pytest.mark.asyncio
    async def test_with_db(self):
        import app.engines.security_engine.audit as audit_module
        audit_module._audit_service = None
        mock_db = AsyncMock()
        await log_calculation_audit(
            calculation_type="marge",
            input_data={"montant": 1000},
            output_data={"result": 1200},
            db=mock_db
        )
        assert mock_db.add.called
        assert mock_db.commit.called

    @pytest.mark.asyncio
    async def test_db_error(self):
        import app.engines.security_engine.audit as audit_module
        audit_module._audit_service = None
        mock_db = AsyncMock()
        mock_db.add.side_effect = Exception("DB Error")
        await log_calculation_audit(
            calculation_type="marge",
            input_data={"montant": 1000},
            output_data={"result": 1200},
            db=mock_db
        )
        service = get_audit_service()
        # Doit quand meme avoir en memoire
        assert len(service.calculation_events) == 1
