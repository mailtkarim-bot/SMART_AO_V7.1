"""
SMART_AO V7 - models.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Event Bus Models
==============================
Modèles des 9 événements standardisés.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List
from datetime import datetime
from enum import Enum
import uuid
import json


class EventType(str, Enum):
    """Types d'événements."""
    DOCUMENT_UPLOADED = "DocumentUploaded"
    ENTITIES_EXTRACTED = "EntitiesExtracted"
    DOCUMENT_CHUNKED = "DocumentChunked"
    EMBEDDING_GENERATED = "EmbeddingGenerated"
    QDRANT_INDEXED = "QdrantIndexed"
    MISSION_CREATED = "MissionCreated"
    STEP_COMPLETED = "StepCompleted"
    WORKFLOW_COMPLETED = "WorkflowCompleted"
    AGENT_EXECUTED = "AgentExecuted"


@dataclass
class Event:
    """Événement de base."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = None
    timestamp: datetime = field(default_factory=datetime.now)
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "metadata": self.metadata,
        }
    
    def to_json(self) -> str:
        """Convertir en JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=False, default=str)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Créer depuis un dictionnaire."""
        event_type = EventType(data.get("event_type", ""))
        event = cls(
            event_id=data.get("event_id", str(uuid.uuid4())),
            event_type=event_type,
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            data=data.get("data", {}),
            metadata=data.get("metadata", {}),
        )
        # Resturer le type spécifique
        if event_type == EventType.DOCUMENT_UPLOADED:
            return DocumentUploaded.from_event(event)
        elif event_type == EventType.ENTITIES_EXTRACTED:
            return EntitiesExtracted.from_event(event)
        elif event_type == EventType.DOCUMENT_CHUNKED:
            return DocumentChunked.from_event(event)
        elif event_type == EventType.EMBEDDING_GENERATED:
            return EmbeddingGenerated.from_event(event)
        elif event_type == EventType.QDRANT_INDEXED:
            return QdrantIndexed.from_event(event)
        elif event_type == EventType.MISSION_CREATED:
            return MissionCreated.from_event(event)
        elif event_type == EventType.STEP_COMPLETED:
            return StepCompleted.from_event(event)
        elif event_type == EventType.WORKFLOW_COMPLETED:
            return WorkflowCompleted.from_event(event)
        elif event_type == EventType.AGENT_EXECUTED:
            return AgentExecuted.from_event(event)
        return event


# Événements spécifiques
@dataclass
class DocumentUploaded(Event):
    """Document téléchargé."""
    document_id: str = ""
    document_name: str = ""
    document_type: str = ""  # PDF, DOCX, etc.
    document_size: int = 0
    
    def __post_init__(self):
        if self.event_type is None:
            self.event_type = EventType.DOCUMENT_UPLOADED
        self.data["document_id"] = self.document_id
        self.data["document_name"] = self.document_name
        self.data["document_type"] = self.document_type
        self.data["document_size"] = self.document_size
    
    @classmethod
    def from_event(cls, event: Event) -> 'DocumentUploaded':
        return cls(
            event_id=event.event_id,
            timestamp=event.timestamp,
            data=event.data,
            metadata=event.metadata,
            document_id=event.data.get("document_id", ""),
            document_name=event.data.get("document_name", ""),
            document_type=event.data.get("document_type", ""),
            document_size=event.data.get("document_size", 0),
        )


@dataclass
class EntitiesExtracted(Event):
    """Entités extraites du document."""
    document_id: str = ""
    entities: List[Dict[str, Any]] = field(default_factory=list)
    extraction_method: str = ""
    
    def __post_init__(self):
        if self.event_type is None:
            self.event_type = EventType.ENTITIES_EXTRACTED
        self.data["document_id"] = self.document_id
        self.data["entities"] = self.entities
        self.data["extraction_method"] = self.extraction_method
    
    @classmethod
    def from_event(cls, event: Event) -> 'EntitiesExtracted':
        return cls(
            event_id=event.event_id,
            timestamp=event.timestamp,
            data=event.data,
            metadata=event.metadata,
            document_id=event.data.get("document_id", ""),
            entities=event.data.get("entities", []),
            extraction_method=event.data.get("extraction_method", ""),
        )


@dataclass
class DocumentChunked(Event):
    """Document découpé en chunks."""
    document_id: str = ""
    chunks: List[Dict[str, Any]] = field(default_factory=list)
    chunk_size: int = 512
    overlap: int = 50
    
    def __post_init__(self):
        if self.event_type is None:
            self.event_type = EventType.DOCUMENT_CHUNKED
        self.data["document_id"] = self.document_id
        self.data["chunks"] = self.chunks
        self.data["chunk_size"] = self.chunk_size
        self.data["overlap"] = self.overlap
    
    @classmethod
    def from_event(cls, event: Event) -> 'DocumentChunked':
        return cls(
            event_id=event.event_id,
            timestamp=event.timestamp,
            data=event.data,
            metadata=event.metadata,
            document_id=event.data.get("document_id", ""),
            chunks=event.data.get("chunks", []),
            chunk_size=event.data.get("chunk_size", 512),
            overlap=event.data.get("overlap", 50),
        )


@dataclass
class EmbeddingGenerated(Event):
    """Embeddings générés."""
    document_id: str = ""
    embedding_dim: int = 1024
    embeddings: List[List[float]] = field(default_factory=list)
    model_name: str = "BAAI/bge-m3"
    
    def __post_init__(self):
        if self.event_type is None:
            self.event_type = EventType.EMBEDDING_GENERATED
        self.data["document_id"] = self.document_id
        self.data["embedding_dim"] = self.embedding_dim
        self.data["embeddings"] = self.embeddings
        self.data["model_name"] = self.model_name
    
    @classmethod
    def from_event(cls, event: Event) -> 'EmbeddingGenerated':
        return cls(
            event_id=event.event_id,
            timestamp=event.timestamp,
            data=event.data,
            metadata=event.metadata,
            document_id=event.data.get("document_id", ""),
            embedding_dim=event.data.get("embedding_dim", 1024),
            embeddings=event.data.get("embeddings", []),
            model_name=event.data.get("model_name", "BAAI/bge-m3"),
        )


@dataclass
class QdrantIndexed(Event):
    """Document indexé dans Qdrant."""
    document_id: str = ""
    collection_name: str = "vault_documents"
    vector_id: str = ""
    
    def __post_init__(self):
        if self.event_type is None:
            self.event_type = EventType.QDRANT_INDEXED
        self.data["document_id"] = self.document_id
        self.data["collection_name"] = self.collection_name
        self.data["vector_id"] = self.vector_id
    
    @classmethod
    def from_event(cls, event: Event) -> 'QdrantIndexed':
        return cls(
            event_id=event.event_id,
            timestamp=event.timestamp,
            data=event.data,
            metadata=event.metadata,
            document_id=event.data.get("document_id", ""),
            collection_name=event.data.get("collection_name", "vault_documents"),
            vector_id=event.data.get("vector_id", ""),
        )


@dataclass
class MissionCreated(Event):
    """Mission créée."""
    mission_id: str = ""
    project_id: str = ""
    mission_type: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.event_type is None:
            self.event_type = EventType.MISSION_CREATED
        self.data["mission_id"] = self.mission_id
        self.data["project_id"] = self.project_id
        self.data["mission_type"] = self.mission_type
        self.data["context"] = self.context
    
    @classmethod
    def from_event(cls, event: Event) -> 'MissionCreated':
        return cls(
            event_id=event.event_id,
            timestamp=event.timestamp,
            data=event.data,
            metadata=event.metadata,
            mission_id=event.data.get("mission_id", ""),
            project_id=event.data.get("project_id", ""),
            mission_type=event.data.get("mission_type", ""),
            context=event.data.get("context", {}),
        )


@dataclass
class StepCompleted(Event):
    """Étape du workflow terminée."""
    mission_id: str = ""
    step_name: str = ""
    step_number: int = 0
    result: Dict[str, Any] = field(default_factory=dict)
    duration_ms: int = 0
    
    def __post_init__(self):
        if self.event_type is None:
            self.event_type = EventType.STEP_COMPLETED
        self.data["mission_id"] = self.mission_id
        self.data["step_name"] = self.step_name
        self.data["step_number"] = self.step_number
        self.data["result"] = self.result
        self.data["duration_ms"] = self.duration_ms
    
    @classmethod
    def from_event(cls, event: Event) -> 'StepCompleted':
        return cls(
            event_id=event.event_id,
            timestamp=event.timestamp,
            data=event.data,
            metadata=event.metadata,
            mission_id=event.data.get("mission_id", ""),
            step_name=event.data.get("step_name", ""),
            step_number=event.data.get("step_number", 0),
            result=event.data.get("result", {}),
            duration_ms=event.data.get("duration_ms", 0),
        )


@dataclass
class WorkflowCompleted(Event):
    """Workflow terminé."""
    mission_id: str = ""
    total_steps: int = 0
    completed_steps: int = 0
    total_duration_ms: int = 0
    status: str = "SUCCESS"
    
    def __post_init__(self):
        if self.event_type is None:
            self.event_type = EventType.WORKFLOW_COMPLETED
        self.data["mission_id"] = self.mission_id
        self.data["total_steps"] = self.total_steps
        self.data["completed_steps"] = self.completed_steps
        self.data["total_duration_ms"] = self.total_duration_ms
        self.data["status"] = self.status
    
    @classmethod
    def from_event(cls, event: Event) -> 'WorkflowCompleted':
        return cls(
            event_id=event.event_id,
            timestamp=event.timestamp,
            data=event.data,
            metadata=event.metadata,
            mission_id=event.data.get("mission_id", ""),
            total_steps=event.data.get("total_steps", 0),
            completed_steps=event.data.get("completed_steps", 0),
            total_duration_ms=event.data.get("total_duration_ms", 0),
            status=event.data.get("status", "SUCCESS"),
        )


@dataclass
class AgentExecuted(Event):
    """Agent exécuté."""
    mission_id: str = ""
    agent_name: str = ""
    input_data: Dict[str, Any] = field(default_factory=dict)
    output: Dict[str, Any] = field(default_factory=dict)
    duration_ms: int = 0
    
    def __post_init__(self):
        if self.event_type is None:
            self.event_type = EventType.AGENT_EXECUTED
        self.data["mission_id"] = self.mission_id
        self.data["agent_name"] = self.agent_name
        self.data["input_data"] = self.input_data
        self.data["output"] = self.output
        self.data["duration_ms"] = self.duration_ms
    
    @classmethod
    def from_event(cls, event: Event) -> 'AgentExecuted':
        return cls(
            event_id=event.event_id,
            timestamp=event.timestamp,
            data=event.data,
            metadata=event.metadata,
            mission_id=event.data.get("mission_id", ""),
            agent_name=event.data.get("agent_name", ""),
            input_data=event.data.get("input_data", {}),
            output=event.data.get("output", {}),
            duration_ms=event.data.get("duration_ms", 0),
        )
