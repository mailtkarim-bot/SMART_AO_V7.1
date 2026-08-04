"""
SMART_AO V7 - Event Model
=========================
Event Bus persistence models
Source: ARCHITECTURE_V7_ENGINE.md §4.4
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import Column, String, Text, DateTime, Integer, JSON
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SQLEnum

from app.core.database import Base


# =============================================================================
# EVENT ENUMS
# =============================================================================

class EventType(str, Enum):
    """Types of events in the system"""
    MISSION_CREATED = "MISSION_CREATED"
    MISSION_STARTED = "MISSION_STARTED"
    MISSION_COMPLETED = "MISSION_COMPLETED"
    MISSION_FAILED = "MISSION_FAILED"
    STEP_STARTED = "STEP_STARTED"
    STEP_COMPLETED = "STEP_COMPLETED"
    STEP_FAILED = "STEP_FAILED"
    DOCUMENT_UPLOADED = "DOCUMENT_UPLOADED"
    DOCUMENT_PROCESSED = "DOCUMENT_PROCESSED"
    AGENT_REGISTERED = "AGENT_REGISTERED"
    AGENT_EXECUTED = "AGENT_EXECUTED"
    SYSTEM_ERROR = "SYSTEM_ERROR"


# =============================================================================
# EVENT MODEL
# =============================================================================

class Event(Base):
    """
    Generic event model for the EventBus
    
    Attributes:
        id: Unique identifier
        event_type: Type of event
        event_data: Event payload
        source: Source of the event
        mission_id: Related mission ID
        step_id: Related step ID
        created_at: Event timestamp
    """
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(SQLEnum(EventType), nullable=False, index=True)
    event_data = Column(JSON, default={}, nullable=True)
    source = Column(String(128), nullable=True)
    mission_id = Column(Integer, nullable=True)
    step_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Event(id={self.id}, event_type={self.event_type}, source={self.source})>"


# =============================================================================
# MISSION EVENT MODEL (Specific to missions)
# =============================================================================

class MissionEvent(Base):
    """
    Mission-specific event model
    
    Attributes:
        id: Unique identifier
        mission_id: Related mission ID
        step_id: Related step ID
        event_type: Type of event
        data: Event data
        created_at: Event timestamp
    """
    __tablename__ = "mission_events"
    
    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(Integer, index=True, nullable=True)
    step_id = Column(Integer, nullable=True)
    event_type = Column(String(128), nullable=False)
    data = Column(JSON, default={}, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    mission = relationship("Mission", back_populates="events")
    
    def __repr__(self):
        return f"<MissionEvent(id={self.id}, event_type={self.event_type}, mission_id={self.mission_id})>"

