"""
SMART_AO V7 - test_engines_event_bus.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Tests d'Intégration Event Bus
============================================
Tests d'intégration pour l'Event Bus V7.
Valide les interactions entre EventBus, les publishers et les subscribers.

Source: PLAN_DE_CODAGE_PHASE_5_V7.md - Sprint 1 (Jour 2)
Cible: 2 tests EventBus
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from app.engines.event_bus.bus import EventBus
from app.engines.event_bus.models import Event, EventType, MissionCreated, WorkflowCompleted
from unittest.mock import Mock, AsyncMock, MagicMock, call
from datetime import datetime, timezone
import asyncio


# Fixtures
@pytest.fixture
def event_bus():
    """Crée un EventBus pour les tests."""
    return EventBus()


# Tests EventBus (2 tests)
class TestEventBusIntegration:
    """Tests d'intégration pour EventBus."""
    
    def test_event_bus_publish_and_subscribe(self, event_bus: EventBus):
        """Test que EventBus peut publier et recevoir des événements."""
        # Créer un événement avec le bon modèle
        event = MissionCreated(
            mission_id="MISSION_001",
            project_id="PROJ_001",
            mission_type="ANALYSE_DCE",
            context={"docs": ["DCE_001.pdf"]}
        )
        
        # Créer un subscriber
        received_events = []
        
        def test_subscriber(event: Event):
            received_events.append(event)
        
        # S'abonner au type d'événement
        event_bus.subscribe(EventType.MISSION_CREATED, test_subscriber)
        
        # Publier l'événement (méthode synchrone)
        event_bus.publish(event)
        
        # Vérifier que l'événement a été reçu
        assert len(received_events) == 1
        assert received_events[0].event_type == EventType.MISSION_CREATED
        assert received_events[0].mission_id == "MISSION_001"
    
    def test_event_bus_multiple_subscribers(self, event_bus: EventBus):
        """Test que EventBus gère plusieurs subscribers pour un même événement."""
        # Créer un événement
        event = WorkflowCompleted(
            mission_id="MISSION_002",
            total_steps=6,
            completed_steps=6,
            total_duration_ms=5000,
            status="SUCCESS"
        )
        
        # Créer plusieurs subscribers
        subscriber_calls = []
        
        def subscriber_1(event: Event):
            subscriber_calls.append(("subscriber_1", event.mission_id))
        
        def subscriber_2(event: Event):
            subscriber_calls.append(("subscriber_2", event.mission_id))
        
        # S'abonner
        event_bus.subscribe(EventType.WORKFLOW_COMPLETED, subscriber_1)
        event_bus.subscribe(EventType.WORKFLOW_COMPLETED, subscriber_2)
        
        # Publier l'événement
        event_bus.publish(event)
        
        # Vérifier que les deux subscribers ont été appelés
        assert len(subscriber_calls) == 2
        assert ("subscriber_1", "MISSION_002") in subscriber_calls
        assert ("subscriber_2", "MISSION_002") in subscriber_calls
