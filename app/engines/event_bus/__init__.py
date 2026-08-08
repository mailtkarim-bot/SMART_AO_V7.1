"""
SMART_AO V7 - __init__.py
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
Bus d'événements pour la communication inter-engines.

9 Events standardisés:
- DocumentUploaded
- EntitiesExtracted
- DocumentChunked
- EmbeddingGenerated
- QdrantIndexed
- MissionCreated
- StepCompleted
- WorkflowCompleted
- AgentExecuted
"""

from app.engines.event_bus.bus import EventBus
from app.engines.event_bus.models import (
    Event,
    EventType,
    DocumentUploaded,
    EntitiesExtracted,
    DocumentChunked,
    EmbeddingGenerated,
    QdrantIndexed,
    MissionCreated,
    StepCompleted,
    WorkflowCompleted,
    AgentExecuted,
)
from app.engines.event_bus.replay import EventReplay
from app.engines.event_bus.dlq import DeadLetterQueue, get_dlq
from app.engines.event_bus.cron_reconciliation import CronReconciler, reconcile_now

__all__ = [
    'EventBus',
    'Event',
    'EventType',
    'DocumentUploaded',
    'EntitiesExtracted',
    'DocumentChunked',
    'EmbeddingGenerated',
    'QdrantIndexed',
    'MissionCreated',
    'StepCompleted',
    'WorkflowCompleted',
    'AgentExecuted',
    'EventReplay',
    'DeadLetterQueue',
    'get_dlq',
    'CronReconciler',
    'reconcile_now',
]
