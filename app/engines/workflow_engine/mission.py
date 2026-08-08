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
SMART_AO V7 - Mission - Tour de contrôle Workflow Engine
Source: ARCHITECTURE_V7_ENGINE.md §4 + ADR-041 + ADR-053

Mission = technique éphémère (analyse DCE)
Project = métier 15 statuts (DEPOSE, GAGNE...) - Voir RAPPORT §Q
Mapping: Mission DONE + Go => Project ANALYSE_TERMINEE
"""

from enum import Enum
from typing import List, Dict, Optional, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict
import uuid


class MissionStatus(str, Enum):
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


class StepStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    DONE = "DONE"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class MissionStep(BaseModel):
    """
    Une étape du workflow 6 steps canoniques V7
    [PARSER, EXTRACTION, CLASSIFICATION, AGENTS, COMPILATION, RAPPORT]
    """
    name: str = Field(..., description="PARSER, EXTRACTION, CLASSIFICATION, AGENTS, COMPILATION, RAPPORT")
    status: StepStatus = StepStatus.PENDING
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 2
    timeout_seconds: int = 300
    output_ref: Optional[str] = None  # Ref vers output stocké MinIO/PG
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @property
    def duration_ms(self) -> Optional[int]:
        if self.started_at and self.ended_at:
            return int((self.ended_at - self.started_at).total_seconds() * 1000)
        return None
    
    @property
    def step_name(self) -> str:
        """Alias pour name pour compatibilité avec les tests."""
        return self.name

    def to_dict(self):
        return {
            "name": self.name,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "duration_ms": self.duration_ms,
            "retry": self.retry_count,
            "error": self.error,
        }


class Mission(BaseModel):
    """
    Mission #254 - Tour de contrôle
    Persistée en PG table missions + mission_steps pour rejouabilité
    """
    id: str = Field(default_factory=lambda: f"mission_{uuid.uuid4().hex[:6]}")
    type: str = Field(default="ANALYSE_DCE", description="ANALYSE_DCE, BATCH, REPLAY")
    status: MissionStatus = MissionStatus.PENDING
    documents: List[str] = Field(default_factory=list, description="17 PDF IDs ex: 412 pages")
    workflow: List[MissionStep] = Field(default_factory=list)
    current_step_idx: int = 0
    context: Dict[str, Any] = Field(default_factory=dict, description="Vault, SIRET, estimation_interne, needed_capabilities")
    priority: str = Field(default="NORMALE", pattern="^(BASSE|NORMALE|HAUTE|URGENTE)$")
    created_by: str = Field(default="system", description="user_id patron")
    project_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def __init__(self, **data):
        # Auto-crée workflow 6 steps canoniques V7 si non fourni
        if "workflow" not in data or not data["workflow"]:
            data["workflow"] = [
                MissionStep(name="PARSER", timeout_seconds=600),
                MissionStep(name="EXTRACTION", timeout_seconds=300),
                MissionStep(name="CLASSIFICATION", timeout_seconds=120),
                MissionStep(name="AGENTS", timeout_seconds=900),
                MissionStep(name="COMPILATION", timeout_seconds=300),
                MissionStep(name="RAPPORT", timeout_seconds=300),
            ]
        super().__init__(**data)

    @property
    def current_step(self) -> Optional[MissionStep]:
        if 0 <= self.current_step_idx < len(self.workflow):
            return self.workflow[self.current_step_idx]
        return None

    @property
    def is_finished(self) -> bool:
        return self.status in [MissionStatus.DONE, MissionStatus.FAILED]

    def has_document_type(self, doc_type: str) -> bool:
        """Helper can_handle() - ex: mission.has_document_type('DPGF')"""
        docs_str = str(self.documents + [self.context.get("type_marche", "")]).lower()
        return doc_type.lower() in docs_str

    def get_step(self, name: str) -> Optional[MissionStep]:
        for s in self.workflow:
            if s.name == name:
                return s
        return None

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "status": self.status,
            "documents": self.documents,
            "workflow": [s.to_dict() for s in self.workflow],
            "current_step_idx": self.current_step_idx,
            "priority": self.priority,
            "project_id": self.project_id,
            "created_at": self.created_at.isoformat(),
        }

    model_config = ConfigDict(use_enum_values=True)


# Pour tests et API
class MissionCreate(BaseModel):
    documents: List[str]
    project_id: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    priority: str = "NORMALE"
