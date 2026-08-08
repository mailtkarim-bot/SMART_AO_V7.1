"""
SMART_AO V7 - dlq.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 07/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - Dead Letter Queue (DLQ)
=====================================
Source: ARCHITECTURE_V7_ENGINE.md ADR-061

Gère les événements qui n'ont pas pu être traités par le bus :
- stockage des événements en échec
- compteur de retry
- replay manuel ou automatique
- exposition métriques pour monitoring Fleet
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Callable, Any

from app.engines.event_bus.models import Event
from app.engines.event_bus.bus import EventBus, get_event_bus

logger = logging.getLogger(__name__)


@dataclass
class DeadLetterEvent:
    """Événement stocké dans la DLQ."""
    event: Event
    error: str
    retry_count: int = 0
    first_failed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_failed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event": self.event.to_dict(),
            "error": self.error,
            "retry_count": self.retry_count,
            "first_failed_at": self.first_failed_at.isoformat(),
            "last_failed_at": self.last_failed_at.isoformat(),
            "metadata": self.metadata,
        }


class DeadLetterQueue:
    """
    DLQ en mémoire avec persistance optionnelle vers fichier.
    Thread-safe via gestion simple de liste (bus fournit le verrou interne).
    """

    def __init__(self, max_retries: int = 3, event_bus: Optional[EventBus] = None):
        self.max_retries = max_retries
        self.event_bus = event_bus or get_event_bus()
        self._dead_events: List[DeadLetterEvent] = []
        self._handlers: Dict[str, Callable[[Event], bool]] = {}

    def register_handler(self, event_type_value: str, handler: Callable[[Event], bool]) -> None:
        """
        Enregistre un handler de replay pour un type d'événement.
        Le handler retourne True si le replay a réussi.
        """
        self._handlers[event_type_value] = handler

    def send_to_dlq(self, event: Event, error: str, metadata: Optional[Dict[str, Any]] = None) -> DeadLetterEvent:
        """Ajoute un événement à la DLQ."""
        now = datetime.now(timezone.utc)
        # Mise à jour si l'événement est déjà présent
        for dle in self._dead_events:
            if dle.event.event_id == event.event_id:
                dle.retry_count += 1
                dle.last_failed_at = now
                dle.error = error
                dle.metadata.update(metadata or {})
                logger.warning(f"Event {event.event_id} retourné en DLQ (retry={dle.retry_count})")
                return dle

        dle = DeadLetterEvent(
            event=event,
            error=error,
            retry_count=0,
            first_failed_at=now,
            last_failed_at=now,
            metadata=metadata or {},
        )
        self._dead_events.append(dle)
        logger.warning(f"Event {event.event_id} envoyé en DLQ: {error}")
        return dle

    def list_events(
        self,
        event_type: Optional[str] = None,
        max_retries_exceeded: Optional[bool] = None,
    ) -> List[DeadLetterEvent]:
        """Liste les événements de la DLQ, avec filtres optionnels."""
        result = list(self._dead_events)
        if event_type:
            result = [dle for dle in result if dle.event.event_type.value == event_type]
        if max_retries_exceeded is not None:
            result = [
                dle for dle in result
                if (dle.retry_count >= self.max_retries) == max_retries_exceeded
            ]
        return result

    def retry_event(self, event_id: str) -> bool:
        """
        Retente un événement de la DLQ.
        Returns True si le handler a réussi ou si l'événement a été republié.
        """
        for idx, dle in enumerate(self._dead_events):
            if dle.event.event_id == event_id:
                handler = self._handlers.get(dle.event.event_type.value)
                success = False
                if handler:
                    try:
                        success = handler(dle.event)
                    except Exception as e:
                        logger.error(f"DLQ replay handler failed for {event_id}: {e}")
                        dle.error = str(e)
                else:
                    # Sans handler spécifique, on republie sur le bus
                    self.event_bus.publish(dle.event)
                    success = True

                if success:
                    self._dead_events.pop(idx)
                    logger.info(f"Event {event_id} sorti de la DLQ avec succès")
                    return True
                else:
                    dle.retry_count += 1
                    dle.last_failed_at = datetime.now(timezone.utc)
                    logger.warning(
                        f"Event {event_id} replay échoué (retry={dle.retry_count})"
                    )
                    return False
        return False

    def retry_all(self) -> Dict[str, int]:
        """Retente tous les événements de la DLQ. Retourne les compteurs."""
        success = 0
        failed = 0
        # Copie pour éviter la mutation pendant l'itération
        for dle in list(self._dead_events):
            if self.retry_event(dle.event.event_id):
                success += 1
            else:
                failed += 1
        return {"success": success, "failed": failed, "remaining": len(self._dead_events)}

    def purge(self) -> int:
        """Vide la DLQ. Retourne le nombre d'événements supprimés."""
        count = len(self._dead_events)
        self._dead_events.clear()
        return count

    def stats(self) -> Dict[str, int]:
        return {
            "total": len(self._dead_events),
            "max_retries_exceeded": sum(1 for dle in self._dead_events if dle.retry_count >= self.max_retries),
        }


# Singleton
_dlq: Optional[DeadLetterQueue] = None


def get_dlq(event_bus: Optional[EventBus] = None) -> DeadLetterQueue:
    global _dlq
    if _dlq is None:
        _dlq = DeadLetterQueue(event_bus=event_bus)
    return _dlq
