"""
SMART_AO V7 - bus.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Event Bus
=======================
Bus d'événements asynchrone avec publish/subscribe/replay.
"""

import asyncio
from typing import Callable, Any, Dict, List, Optional, Union
from collections import defaultdict
import logging
import threading

from app.engines.event_bus.models import (
    Event, EventType, MissionCreated, StepCompleted, WorkflowCompleted,
    AgentExecuted, DocumentUploaded, EntitiesExtracted, DocumentChunked,
)
# Alias pour éviter conflit avec LegacyEvent
BaseEvent = Event

logger = logging.getLogger(__name__)


# Wrapper pour compatibilité descendante avec l'ancien format Event(type=...)
# @deprecated - À migrer vers les événements spécifiques
class LegacyEvent:
    """Wrapper pour compatibilité avec l'ancien format Event(type=...)."""
    
    def __init__(self, type: str, mission_id: str = None, payload: dict = None, source: str = None, **kwargs):
        # Mapper les anciens types vers les nouveaux EventType
        type_mapping = {
            "MissionCréée": EventType.MISSION_CREATED,
            "MissionÉchouée": EventType.WORKFLOW_COMPLETED,
            "DocumentAnalysé": EventType.DOCUMENT_UPLOADED,
            "EntitésExtraites": EventType.ENTITIES_EXTRACTED,
            "ClassificationTerminée": EventType.DOCUMENT_CHUNKED,
            "AgentDémarré": EventType.AGENT_EXECUTED,
            "AgentTerminé": EventType.AGENT_EXECUTED,
            "CompilationTerminée": EventType.WORKFLOW_COMPLETED,
            "AnalyseTerminée": EventType.WORKFLOW_COMPLETED,
        }
        
        event_type = type_mapping.get(type, EventType.WORKFLOW_COMPLETED)
        
        # Pour éviter les problèmes de compatibilité avec les champs des événements spécifiques,
        # créer un BaseEvent générique avec toutes les données dans payload et metadata
        # La migration vers les événements spécifiques se fera progressivement
        self._event = BaseEvent(
            event_type=event_type,
            data=payload or {},
            metadata={"source": source, "legacy_type": type, "mission_id": mission_id}
        )
    
    # Déléguer toutes les méthodes à l'événement interne
    def __getattr__(self, name):
        return getattr(self._event, name)


class EventBus:
    """Bus d'événements asynchrone."""
    
    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable[[Event], None]]] = defaultdict(list)
        self._event_history: List[Event] = []
        self._lock = threading.Lock()
        self._async_lock = asyncio.Lock()
        self._max_history = 10000
    
    def subscribe(self, event_type: EventType, callback: Callable[[Event], None]) -> None:
        """S'abonner à un type d'événement."""
        with self._lock:
            self._subscribers[event_type].append(callback)
        logger.debug(f"Subscribed to {event_type.value}")
    
    def unsubscribe(self, event_type: EventType, callback: Callable[[Event], None]) -> None:
        """Se désabonner d'un type d'événement."""
        with self._lock:
            if callback in self._subscribers[event_type]:
                self._subscribers[event_type].remove(callback)
        logger.debug(f"Unsubscribed from {event_type.value}")
    
    def publish(self, event: Event) -> None:
        """Publier un événement (synchrone)."""
        with self._lock:
            # Sauvegarder dans l'historique
            if len(self._event_history) >= self._max_history:
                self._event_history.pop(0)
            self._event_history.append(event)
            
            # Notifier les abonnés
            for callback in self._subscribers.get(event.event_type, []):
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Error in callback for {event.event_type.value}: {e}")
    
    async def publish_async(self, event: Event) -> None:
        """Publier un événement (asynchrone)."""
        async with self._async_lock:
            with self._lock:
                if len(self._event_history) >= self._max_history:
                    self._event_history.pop(0)
                self._event_history.append(event)
            
            # Notifier les abonnés de manière asynchrone
            tasks = []
            for callback in self._subscribers.get(event.event_type, []):
                try:
                    # Si le callback est une coroutine
                    if asyncio.iscoroutinefunction(callback):
                        tasks.append(asyncio.create_task(callback(event)))
                    else:
                        # Exécuter dans un thread pour ne pas bloquer
                        loop = asyncio.get_event_loop()
                        tasks.append(loop.run_in_executor(None, callback, event))
                except Exception as e:
                    logger.error(f"Error in async callback for {event.event_type.value}: {e}")
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    def get_history(self, event_type: Optional[EventType] = None, limit: int = 100) -> List[Event]:
        """Récupérer l'historique des événements."""
        with self._lock:
            if event_type is None:
                return list(reversed(self._event_history[-limit:]))
            else:
                return [e for e in reversed(self._event_history[-limit:]) if e.event_type == event_type]
    
    async def replay(self, mission_id: str, limit: int = 100) -> List[Event]:
        """Rejouer les événements pour une mission (alias pour get_history filtré)."""
        with self._lock:
            return [e for e in reversed(self._event_history[-limit:]) 
                   if e.metadata.get("mission_id") == mission_id]
    
    def clear_history(self) -> None:
        """Effacer l'historique."""
        with self._lock:
            self._event_history.clear()
    
    def clear_subscribers(self) -> None:
        """Effacer tous les abonnés."""
        with self._lock:
            self._subscribers.clear()


# Instance singleton
event_bus = EventBus()


def get_event_bus() -> EventBus:
    """Récupérer l'instance singleton du EventBus."""
    return event_bus


def create_test_event_bus() -> EventBus:
    """Créer une nouvelle instance EventBus pour les tests (isolation)."""
    return EventBus()


# Pour compatibilité descendante : exporter LegacyEvent comme Event
# NOTE: Cela permet à workflow.py d'utiliser Event(type=...) sans casser
# À long terme, migrer workflow.py vers les événements spécifiques
Event = LegacyEvent  # type: ignore[no-redef]


# Décorateur pour simplifier la publication
def publish_event(event_type: EventType, **kwargs) -> Event:
    """Créer et publier un événement."""
    event_class = {
        EventType.DOCUMENT_UPLOADED: Event,
        EventType.ENTITIES_EXTRACTED: Event,
        EventType.DOCUMENT_CHUNKED: Event,
        EventType.EMBEDDING_GENERATED: Event,
        EventType.QDRANT_INDEXED: Event,
        EventType.MISSION_CREATED: Event,
        EventType.STEP_COMPLETED: Event,
        EventType.WORKFLOW_COMPLETED: Event,
        EventType.AGENT_EXECUTED: Event,
    }.get(event_type, Event)
    
    event = event_class(**kwargs)
    event_bus.publish(event)
    return event
