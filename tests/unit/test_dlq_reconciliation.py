"""
SMART_AO V7.1 - test_dlq_reconciliation.py
============================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 07/08/2026
Build: 9.5 - Phase: 5
"""

"""
SMART_AO V7.1 - Test DLQ + Cron Reconciliation (ADR-061)
Source: ARCHITECTURE_V7_ENGINE.md ADR-061
"""
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from app.engines.event_bus.bus import create_test_event_bus
from app.engines.event_bus.models import Event, EventType
from app.engines.event_bus.dlq import DeadLetterQueue
from app.engines.event_bus.cron_reconciliation import CronReconciler


def test_dlq_send_and_retry():
    bus = create_test_event_bus()
    dlq = DeadLetterQueue(event_bus=bus)

    event = Event(event_type=EventType.AGENT_EXECUTED, data={"agent": "test"})
    dlq.send_to_dlq(event, error="timeout simulé")
    assert len(dlq.list_events()) == 1

    # Handler qui réussit au retry
    success_ids = []

    def handler(evt):
        success_ids.append(evt.event_id)
        return True

    dlq.register_handler(EventType.AGENT_EXECUTED.value, handler)
    assert dlq.retry_event(event.event_id) is True
    assert len(dlq.list_events()) == 0
    print("✅ Event DLQ retenté avec succès")


def test_dlq_max_retries():
    bus = create_test_event_bus()
    dlq = DeadLetterQueue(event_bus=bus, max_retries=2)

    event = Event(event_type=EventType.STEP_COMPLETED, data={"step": "test"})
    dlq.send_to_dlq(event, error="échec permanent")

    def handler(evt):
        return False

    dlq.register_handler(EventType.STEP_COMPLETED.value, handler)
    dlq.retry_event(event.event_id)
    dlq.retry_event(event.event_id)
    dlq.retry_event(event.event_id)
    dead = dlq.list_events(max_retries_exceeded=True)
    assert len(dead) == 1
    assert dead[0].retry_count >= 2
    print("✅ Max retries détecté")


def test_cron_reconcile_stuck_event():
    bus = create_test_event_bus()
    dlq = DeadLetterQueue(event_bus=bus)

    # Event marqué RUNNING il y a 10 minutes
    stuck_ts = datetime.now(timezone.utc) - timedelta(seconds=600)
    event = Event(
        event_type=EventType.STEP_COMPLETED,
        data={"status": "RUNNING", "step": "AGENTS"},
        timestamp=stuck_ts,
    )
    bus.publish(event)

    reconciler = CronReconciler(event_bus=bus, dlq=dlq, stuck_timeout_seconds=300)
    # On appelle uniquement la détection des événements bloqués
    stuck = reconciler.reconcile_stuck_events()
    assert len(stuck) == 1
    assert len(dlq.list_events(event_type=EventType.STEP_COMPLETED.value)) == 1
    print("✅ Event bloqué détecté et déplacé en DLQ")


if __name__ == "__main__":
    test_dlq_send_and_retry()
    test_dlq_max_retries()
    test_cron_reconcile_stuck_event()
    print("✅ TESTS PASSED: DLQ + Cron Reconciliation")
