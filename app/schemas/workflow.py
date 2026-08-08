"""
SMART_AO V7 - workflow.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class WorkflowStatusResponse(BaseModel):
    '''Schema de réponse pour le statut du workflow.'''
    mission_id: str
    current_step: str
    total_steps: int
    completed_steps: int
    status: str
    started_at: Optional[datetime] = None
    last_update: Optional[datetime] = None


class WorkflowExecutionResponse(BaseModel):
    '''Schema de réponse pour l'exécution du workflow.'''
    mission_id: str
    execution_id: str
    started_at: str
    status: str
    message: Optional[str] = None
