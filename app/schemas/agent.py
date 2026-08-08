"""
SMART_AO V7 - agent.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import timedelta


class AgentResponse(BaseModel):
    '''Schema de réponse pour un agent.'''
    name: str
    capabilities: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    estimated_duration: timedelta
    is_blocking: bool = False
    description: str = ""
    
    model_config = ConfigDict(from_attributes=True)


class AgentListResponse(BaseModel):
    '''Schema de réponse pour la liste des agents.'''
    agents: List[AgentResponse] = Field(default_factory=list)
    total: int = 0
