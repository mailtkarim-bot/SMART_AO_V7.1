"""
SMART_AO V7 - user_settings.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 09/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - User Settings Model
===============================
PostgreSQL User settings model for deadline configurations and preferences
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class UserSettings(Base):
    """
    User settings model for storing individual preferences and configurations
    
    Attributes:
        id: Unique identifier
        user_id: Reference to user
        deadline_config: Deadline escalation configuration
        preferences: General user preferences
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    deadline_config = Column(JSON, default={}, nullable=True)
    preferences = Column(JSON, default={}, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), 
                       onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationship
    user = relationship("User", backref="settings")
    
    def __repr__(self):
        return f"<UserSettings(id={self.id}, user_id={self.user_id})>"
