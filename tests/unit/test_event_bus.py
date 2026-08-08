"""
SMART_AO V7 - test_event_bus.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Tests Event Bus
==============================
Tests unitaires pour le Event Bus.
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from app.engines.event_bus import EventBus, Event, EventType
from app.engines.event_bus.models import (
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


class TestEvent:
    """Tests de l'événement de base."""
    
    def test_event_creation(self):
        """Test de la création d'un événement."""
        event = Event(event_type=EventType.DOCUMENT_UPLOADED)
        assert event.event_id is not None
        assert event.event_type == EventType.DOCUMENT_UPLOADED
        assert event.timestamp is not None
    
    def test_event_to_dict(self):
        """Test de la conversion en dictionnaire."""
        event = Event(
            event_type=EventType.DOCUMENT_UPLOADED,
            data={"test": "value"},
            metadata={"source": "test"}
        )
        d = event.to_dict()
        assert "event_id" in d
        assert "event_type" in d
        assert d["event_type"] == "DocumentUploaded"
    
    def test_event_to_json(self):
        """Test de la conversion en JSON."""
        event = Event(event_type=EventType.DOCUMENT_UPLOADED)
        json_str = event.to_json()
        assert "DocumentUploaded" in json_str


class TestEventBus:
    """Tests du EventBus."""
    
    def test_subscribe_and_publish(self):
        """Test de l'abonnement et de la publication."""
        bus = EventBus()
        received_events = []
        
        def callback(event: Event):
            received_events.append(event)
        
        bus.subscribe(EventType.DOCUMENT_UPLOADED, callback)
        
        event = Event(event_type=EventType.DOCUMENT_UPLOADED)
        bus.publish(event)
        
        assert len(received_events) == 1
        assert received_events[0].event_type == EventType.DOCUMENT_UPLOADED
    
    def test_multiple_subscribers(self):
        """Test de plusieurs abonnés."""
        bus = EventBus()
        received1 = []
        received2 = []
        
        def callback1(event: Event):
            received1.append(event)
        
        def callback2(event: Event):
            received2.append(event)
        
        bus.subscribe(EventType.DOCUMENT_UPLOADED, callback1)
        bus.subscribe(EventType.DOCUMENT_UPLOADED, callback2)
        
        event = Event(event_type=EventType.DOCUMENT_UPLOADED)
        bus.publish(event)
        
        assert len(received1) == 1
        assert len(received2) == 1
    
    def test_unsubscribe(self):
        """Test du désabonnement."""
        bus = EventBus()
        received = []
        
        def callback(event: Event):
            received.append(event)
        
        bus.subscribe(EventType.DOCUMENT_UPLOADED, callback)
        bus.unsubscribe(EventType.DOCUMENT_UPLOADED, callback)
        
        event = Event(event_type=EventType.DOCUMENT_UPLOADED)
        bus.publish(event)
        
        assert len(received) == 0
    
    def test_history(self):
        """Test de l'historique."""
        bus = EventBus()
        
        for i in range(5):
            event = Event(event_type=EventType.DOCUMENT_UPLOADED, data={"index": i})
            bus.publish(event)
        
        history = bus.get_history(limit=5)
        assert len(history) == 5
    
    def test_clear_history(self):
        """Test de l'effacement de l'historique."""
        bus = EventBus()
        
        event = Event(event_type=EventType.DOCUMENT_UPLOADED)
        bus.publish(event)
        
        bus.clear_history()
        history = bus.get_history()
        assert len(history) == 0


class TestSpecificEvents:
    """Tests des événements spécifiques."""
    
    def test_document_uploaded(self):
        """Test de DocumentUploaded."""
        event = DocumentUploaded(
            document_id="doc_001",
            document_name="test.pdf",
            document_type="PDF",
            document_size=1024
        )
        assert event.event_type == EventType.DOCUMENT_UPLOADED
        assert event.document_id == "doc_001"
    
    def test_entities_extracted(self):
        """Test de EntitiesExtracted."""
        event = EntitiesExtracted(
            document_id="doc_001",
            entities=[{"type": "CCAG", "value": "10%"}],
            extraction_method="NLP"
        )
        assert event.event_type == EventType.ENTITIES_EXTRACTED
        assert len(event.entities) == 1
    
    def test_step_completed(self):
        """Test de StepCompleted."""
        event = StepCompleted(
            mission_id="mission_001",
            step_name="parser_step",
            step_number=1,
            duration_ms=100
        )
        assert event.event_type == EventType.STEP_COMPLETED
        assert event.step_name == "parser_step"
    
    def test_workflow_completed(self):
        """Test de WorkflowCompleted."""
        event = WorkflowCompleted(
            mission_id="mission_001",
            total_steps=6,
            completed_steps=6,
            status="SUCCESS"
        )
        assert event.event_type == EventType.WORKFLOW_COMPLETED
        assert event.status == "SUCCESS"
    
    def test_agent_executed(self):
        """Test de AgentExecuted."""
        event = AgentExecuted(
            mission_id="mission_001",
            agent_name="DeadlineAgent",
            duration_ms=50
        )
        assert event.event_type == EventType.AGENT_EXECUTED
        assert event.agent_name == "DeadlineAgent"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
