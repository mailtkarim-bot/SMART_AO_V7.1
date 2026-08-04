"""
SMART_AO V7 - Event Bus - Découplage total
Source: ARCHITECTURE_V7_ENGINE.md §5 + ADR-043

Parser ne connait personne. Il publie DocumentAnalysé.
PAB, Certif, RSE écoutent sans que Parser le sache.

Tech: asyncio.Queue en mémoire + table Postgres events pour replay
PAS Kafka/Redis Streams (contrainte 16Go RAM Single-Tenant)
"""

from typing import Dict, List, Callable, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import asyncio
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class Event(BaseModel):
    """
    Event standardisé V7 - SSoT
    Voir ARCHITECTURE_V7_ENGINE.md §5 tableau events
    """
    type: str = Field(..., description="MissionCréée, DocumentAnalysé, EntitésExtraites, ClassificationTerminée, AgentDémarré, AgentTerminé, RisqueDétecté, AnalyseTerminée, MissionÉchouée")
    mission_id: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = Field(..., description="Nom engine/agent émetteur")
    id: Optional[str] = None

    class Config:
        extra = "allow"


class EventBus:
    """
    EventBus intra-VPS V7
    - publish() persiste PG + queue mémoire + notifie subscribers
    - subscribe decorator
    - replay(mission_id) pour debug
    - Mode memory pour tests
    """

    def __init__(self, mode: str = "production"):
        self.mode = mode  # production ou memory (tests)
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.queue: asyncio.Queue = asyncio.Queue()
        self._events_store: List[Event] = []  # En prod = Postgres table events, ici mémoire pour skeleton
        self._running = False
        logger.info(f"EventBus initialized mode={mode} - V7 OS")

    async def publish(self, event: Event):
        """
        Publie event:
        1. Persiste (PG en prod, mémoire ici)
        2. Queue mémoire
        3. Notifie subscribers directs async
        """
        # 1. Persistance
        await self._persist(event)

        # 2. Queue
        await self.queue.put(event)

        # 3. Notif subscribers
        handlers = self.subscribers.get(event.type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    asyncio.create_task(handler(event))
                else:
                    # Supporte aussi classes avec __call__ ou méthodes
                    asyncio.create_task(self._call_handler(handler, event))
            except Exception as e:
                logger.error(f"EventBus handler error {event.type}: {e}")

        logger.debug(f"Published {event.type} mission={event.mission_id} source={event.source}")

    async def _call_handler(self, handler: Any, event: Event):
        """Wrapper pour handlers qui sont des classes instanciées"""
        try:
            if hasattr(handler, "__call__"):
                result = handler(event)
                if asyncio.iscoroutine(result):
                    await result
            elif hasattr(handler, "handle"):
                result = handler.handle(event)
                if asyncio.iscoroutine(result):
                    await result
        except Exception as e:
            logger.error(f"Handler call failed {handler}: {e}")

    async def _persist(self, event: Event):
        """En prod: INSERT INTO events. Ici: mémoire"""
        self._events_store.append(event)
        # TODO prod: await db.execute("INSERT INTO events ...", event.dict())

    def subscribe(self, event_type: str):
        """
        Decorator
        Usage:
            @event_bus.subscribe("DocumentAnalysé")
            class PABAgent(BaseAgent): ...

            @event_bus.subscribe("DocumentAnalysé")
            async def on_doc(event): ...
        """
        def decorator(func_or_cls):
            self.subscribers[event_type].append(func_or_cls)
            logger.debug(f"Subscribed {func_or_cls} to {event_type}")
            return func_or_cls
        return decorator

    def subscribe_fn(self, event_type: str, handler: Callable):
        """Subscribe impératif pour tests"""
        self.subscribers[event_type].append(handler)

    async def replay(self, mission_id: str) -> List[Event]:
        """Rejouabilité debug - tous events d'une mission"""
        # En prod: SELECT * FROM events WHERE mission_id = ?
        return [e for e in self._events_store if e.mission_id == mission_id]

    async def get_all_events(self) -> List[Event]:
        return list(self._events_store)

    def clear(self):
        """Tests only"""
        self._events_store.clear()
        self.subscribers.clear()
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
            except:
                break


# Singleton global - comme registry
event_bus = EventBus(mode="production")

# Pour tests
def create_test_event_bus() -> EventBus:
    return EventBus(mode="memory")
