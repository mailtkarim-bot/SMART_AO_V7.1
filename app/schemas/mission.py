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
SMART_AO V7 - Mission Schemas
==============================
Pydantic V2 schemas for Mission endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class MissionStatus(str, Enum):
    """Status enum for missions."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MissionType(str, Enum):
    """Type enum for missions."""
    ANALYSIS = "analysis"
    GENERATION = "generation"
    VALIDATION = "validation"
    OPTIMIZATION = "optimization"


class MissionCreate(BaseModel):
    """Schema for creating a new mission."""
    
    name: str = Field(..., description="Name of the mission", min_length=1, max_length=200)
    mission_type: MissionType = Field(..., description="Type of mission")
    description: Optional[str] = Field(None, description="Description of the mission", max_length=1000)
    parameters: Optional[dict] = Field(None, description="Mission parameters")
    priority: int = Field(1, description="Priority level (1-10)", ge=1, le=10)
    agent_name: Optional[str] = Field(None, description="Agent to execute the mission")


class MissionResponse(BaseModel):
    """Schema for mission response."""
    
    id: str = Field(..., description="Unique mission identifier")
    name: str = Field(..., description="Name of the mission")
    mission_type: MissionType = Field(..., description="Type of mission")
    description: Optional[str] = Field(None, description="Description of the mission")
    status: MissionStatus = Field(..., description="Current status of the mission")
    priority: int = Field(..., description="Priority level")
    parameters: Optional[dict] = Field(None, description="Mission parameters")
    agent_name: Optional[str] = Field(None, description="Agent executing the mission")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    result: Optional[dict] = Field(None, description="Mission result")
    error: Optional[str] = Field(None, description="Error message if failed")


class MissionListResponse(BaseModel):
    """Schema for listing missions."""
    
    missions: List[MissionResponse] = Field(..., description="List of missions")
    total: int = Field(..., description="Total number of missions")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of missions per page")
    total_pages: int = Field(..., description="Total number of pages")

