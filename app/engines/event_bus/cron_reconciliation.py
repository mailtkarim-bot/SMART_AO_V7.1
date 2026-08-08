"""
SMART_AO V7 - cron_reconciliation.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 07/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - Cron Reconciliation EventBus
==========================================
Source: ARCHITECTURE_V7_ENGINE.md ADR-061

Tâche périodique qui :
1. Détecte les événements bloqués en statut RUNNING depuis plus de N secondes.
2. Les déplace dans la DLQ.
3. Retente les événements de la DLQ (jusqu'à max_retries).

Exécution typique : toutes les heures via cron/systemd timer.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any

from app.engines.event_bus.models import Event
from app.engines.event_bus.bus import EventBus, get_event_bus
from app.engines.event_bus.dlq import DeadLetterQueue, get_dlq

logger = logging.getLogger(__name__)


class CronReconciler:
    """
    Reconciliateur périodique pour le bus d'événements.
    """

    def __init__(
        self,
        event_bus: Optional[EventBus] = None,
        dlq: Optional[DeadLetterQueue] = None,
        stuck_timeout_seconds: float = 300.0,
    ):
        self.event_bus = event_bus or get_event_bus()
        self.dlq = dlq or get_dlq(self.event_bus)
        self.stuck_timeout_seconds = stuck_timeout_seconds

    def _is_stuck(self, event: Event) -> bool:
        """Un événement est bloqué s'il est marqué RUNNING et dépassé le timeout."""
        status = event.data.get("status") if event.data else None
        if status != "RUNNING":
            return False
        age = datetime.now(timezone.utc) - event.timestamp
        return age.total_seconds() > self.stuck_timeout_seconds

    def reconcile_stuck_events(self) -> List[Event]:
        """
        Scanne l'historique du bus, détecte les événements bloqués et les envoie
        en DLQ.
        """
        moved: List[Event] = []
        # On récupère l'historique complet en mémoire
        history = self.event_bus.get_history(limit=10000)
        for event in history:
            if self._is_stuck(event):
                self.dlq.send_to_dlq(
                    event,
                    error=f"Stuck in RUNNING for >{self.stuck_timeout_seconds}s",
                    metadata={"detected_by": "cron_reconciliation", "source": "event_bus_history"},
                )
                moved.append(event)
        if moved:
            logger.warning(f"CronReconciler: {len(moved)} événements bloqués déplacés en DLQ")
        return moved

    def retry_dlq(self) -> Dict[str, int]:
        """Retente les événements de la DLQ."""
        return self.dlq.retry_all()

    def run_once(self) -> Dict[str, Any]:
        """
        Exécite un cycle complet de reconciliation.
        Retourne un résumé des actions.
        """
        stuck = self.reconcile_stuck_events()
        retry_result = self.retry_dlq()
        return {
            "stuck_detected": len(stuck),
            "stuck_event_ids": [e.event_id for e in stuck],
            "dlq_retry_success": retry_result["success"],
            "dlq_retry_failed": retry_result["failed"],
            "dlq_remaining": retry_result["remaining"],
        }

    async def run_async_once(self) -> Dict[str, Any]:
        """Version asynchrone (le travail est synchrone en mémoire)."""
        return self.run_once()


def reconcile_now(
    event_bus: Optional[EventBus] = None,
    dlq: Optional[DeadLetterQueue] = None,
    stuck_timeout_seconds: float = 300.0,
) -> Dict[str, Any]:
    """Helper pour exécuter une reconciliation immédiatement."""
    reconciler = CronReconciler(event_bus, dlq, stuck_timeout_seconds)
    return reconciler.run_once()
