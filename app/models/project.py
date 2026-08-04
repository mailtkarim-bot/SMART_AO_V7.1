"""
SMART_AO V7 - Project Model
===========================
PostgreSQL Project model for construction projects
Source: ARCHITECTURE_V7_ENGINE.md §4.2
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, Text, DateTime, Integer, Float, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class Project(Base):
    """
    Project model representing a construction project
    
    Attributes:
        id: Unique identifier
        project_id: Human-readable project ID
        name: Project name
        description: Project description
        location: Project location
        budget: Total budget
        status: Project status
        start_date: Project start date
        end_date: Project end date
        created_at: Creation timestamp
        updated_at: Last update timestamp
        metadata: Additional project metadata
    """
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(512), nullable=True)
    budget = Column(Float, nullable=True)
    status = Column(String(64), default="active", nullable=False)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    extra_metadata = Column(JSON, default={}, nullable=True)
    
    # Relationships
    missions = relationship("Mission", backref="project", foreign_keys="[Mission.project_id]")
    
    def __repr__(self):
        return f"<Project(id={self.id}, project_id={self.project_id}, name={self.name})>"
    
    @property
    def total_missions(self) -> int:
        """Count total missions for this project"""
        return len(self.missions) if self.missions else 0

