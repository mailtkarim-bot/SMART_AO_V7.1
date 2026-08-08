"""
SMART_AO V7 - mission.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Mission Model
==========================
PostgreSQL Mission model with steps tracking
Source: ARCHITECTURE_V7_ENGINE.md §4.1
"""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from sqlalchemy import Column, String, Text, DateTime, Integer, Float, JSON, UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SQLEnum

from app.core.database import Base


# =============================================================================
# ENUMS
# SSoT: Alignés sur app/engines/workflow_engine/mission.py
# =============================================================================

class MissionStatus(str, Enum):
    """Status of a mission - SSoT V7 Workflow Engine"""
    PENDING = "PENDING"
    CREATED = "CREATED"
    PARSING = "PARSING"
    EXTRACTING = "EXTRACTING"
    CLASSIFYING = "CLASSIFYING"
    AGENT_RUNNING = "AGENT_RUNNING"
    COMPILING = "COMPILING"
    REPORTING = "REPORTING"
    DONE = "DONE"
    FAILED = "FAILED"


class MissionStepStatus(str, Enum):
    """Status of a mission step - SSoT V7 Workflow Engine"""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    DONE = "DONE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


# =============================================================================
# MISSION MODEL
# =============================================================================

class Mission(Base):
    """
    Mission model representing a complete workflow execution
    
    Attributes:
        id: Unique identifier
        mission_id: Human-readable mission ID
        name: Mission name
        description: Mission description
        status: Current status
        created_at: Creation timestamp
        updated_at: Last update timestamp
        completed_at: Completion timestamp
        total_steps: Total number of steps
        completed_steps: Number of completed steps
        error_message: Error message if failed
        metadata: Additional mission metadata
        project_id: Reference to project
    """
    __tablename__ = "missions"
    
    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(MissionStatus), default=MissionStatus.CREATED, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    total_steps = Column(Integer, default=0, nullable=False)
    completed_steps = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    extra_metadata = Column(JSON, default={}, nullable=True)
    project_id = Column(String(64), ForeignKey("projects.project_id"), nullable=True)
    
    # Relationships
    steps = relationship("MissionStep", back_populates="mission", cascade="all, delete-orphan")
    events = relationship("MissionEvent", back_populates="mission", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Mission(id={self.id}, mission_id={self.mission_id}, status={self.status})>"
    
    @property
    def progress(self) -> float:
        """Calculate mission progress percentage"""
        if self.total_steps == 0:
            return 0.0
        return (self.completed_steps / self.total_steps) * 100
    
    @property
    def is_complete(self) -> bool:
        """Check if mission is complete"""
        return self.status == MissionStatus.DONE
    
    @property
    def is_failed(self) -> bool:
        """Check if mission failed"""
        return self.status == MissionStatus.FAILED


# =============================================================================
# MISSION STEP MODEL
# =============================================================================

class MissionStep(Base):
    """
    Mission step model representing a single step in a mission
    
    Steps:
        1. parser_step: Document parsing
        2. extraction_step: Data extraction
        3. classification_step: Document classification
        4. agents_step: Agent execution
        5. compilation_step: Result compilation
        6. rapport_step: Report generation
    """
    __tablename__ = "mission_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(Integer, ForeignKey("missions.id"), index=True, nullable=False)
    step_name = Column(String(64), nullable=False)
    step_order = Column(Integer, nullable=False)
    status = Column(SQLEnum(MissionStepStatus), default=MissionStepStatus.PENDING, nullable=False)
    input_data = Column(JSON, default={}, nullable=True)
    output_data = Column(JSON, default={}, nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    agent_name = Column(String(128), nullable=True)
    execution_time_ms = Column(Float, nullable=True)
    
    # Relationships
    mission = relationship("Mission", back_populates="steps")
    
    __table_args__ = (
        # Composite unique constraint: one step per order per mission
        UniqueConstraint("mission_id", "step_order", name="uq_mission_step"),
    )
    
    def __repr__(self):
        return f"<MissionStep(id={self.id}, mission_id={self.mission_id}, step_name={self.step_name}, status={self.status})>"


