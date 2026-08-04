"""
SMART_AO V7 - BaseAgent - Contrat unique opposable
Source: ARCHITECTURE_V7_ENGINE.md §2 + ENGINEERING-HANDBOOK V7 ADR-044

Règles opposables:
- Tous agents héritent BaseAgent dans app/agents/agent_*.py
- AgentOutput.findings = ZERO € garanti (regex check test_agent_no_euro.py)
- estimated_duration utilisé par WorkflowEngine pour timeout
- dependencies = capabilities, pas noms de fichiers
- can_handle() 0.0-1.0 pour pertinence
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from datetime import timedelta
from pydantic import BaseModel, Field, field_validator
import re

# Regex ZERO € - bloquant si trouvé dans findings
EURO_REGEX = re.compile(r"\d+\s*€|\bEUR\b|\bmarge\b|\bcoeff_vente\b|\bBFR\b", re.IGNORECASE)


class AgentInput(BaseModel):
    """
    Input standardisé pour tous les agents V7
    Fourni par WorkflowEngine + Knowledge Engine + Document Engine
    """
    mission_id: str = Field(..., description="ID Mission_XXX")
    dce_chunks: List[Dict[str, Any]] = Field(default_factory=list, description="Chunks RAG BGE-M3")
    parsed_docs: Dict[str, Any] = Field(default_factory=dict, description="Output Document Engine {pages, type_marche, chunks}")
    context: Dict[str, Any] = Field(default_factory=dict, description="Vault A01-A12, estimation_interne, projet, etc.")
    previous_outputs: Dict[str, "AgentOutput"] = Field(default_factory=dict, description="Outputs agents dépendants {capability: AgentOutput}")

    class Config:
        extra = "allow"  # Permet contexte riche


class AgentOutput(BaseModel):
    """
    Output standardisé V7 - ZERO € garanti par type
    INTERDIT: tout champ €, marge, coeff, BFR
    """
    agent_name: str
    mission_id: str
    capability: str = Field(..., description="Capabilité principale traitée")
    confidence: float = Field(ge=0.0, le=1.0, description="Confiance IA 0-1")
    status: str = Field(..., pattern="^(SUCCESS|PARTIAL|FAILED|SKIPPED)$")
    findings: List[Dict[str, Any]] = Field(default_factory=list, description="JSON quali ZERO €")
    warnings: List[str] = Field(default_factory=list)
    execution_time_ms: int = Field(default=0)
    source_pages: List[int] = Field(default_factory=list, description="Traçabilité pages sources")

    @field_validator("findings")
    @classmethod
    def check_zero_euro(cls, v):
        """Garde-fou ZERO € - bloque si € détecté dans findings"""
        payload_str = str(v)
        if EURO_REGEX.search(payload_str):
            # On log mais ne bloque pas en prod, test bloquant fera échouer
            # Pour V7 strict, on lève
            raise ValueError(f"ZERO € violation: findings contient €/marge/BFR interdit: {payload_str[:200]}")
        return v


class BaseAgent(ABC):
    """
    Contrat unique V7 - Tous les agents, du Deadline au Contentieux
    Même structure, 5min pour un junior
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Ex: 'PAB Detector' - affiché UI"""
        ...

    @property
    @abstractmethod
    def capabilities(self) -> List[str]:
        """Ex: ['DETECTER_PAB', 'CALCULER_ECART_MARCHE'] - SSoT"""
        ...

    @property
    def dependencies(self) -> List[str]:
        """Capabilities requises - ex: ['PARSER', 'CHIFFRAGE']"""
        return []

    @property
    def tags(self) -> List[str]:
        """Ex: ['finance', 'risque', 'bloquant', 'admin_only']"""
        return []

    @property
    def estimated_duration(self) -> timedelta:
        """Utilisé par WorkflowEngine pour timeout = *2 et semaphore"""
        return timedelta(seconds=12)

    @property
    def is_blocking(self) -> bool:
        """Si True, échec = Mission FAILED (ex: Deadline Guardian)"""
        return False

    def can_handle(self, mission: "Mission") -> float:
        """
        Score pertinence 0.0-1.0
        0.0 = pas pertinent, 1.0 = critique
        A surcharger par agent

        Ex PAB:
          has_dpgf + estimation_interne => 0.92
          sinon 0.15
        """
        return 0.5

    def score_capabilities(self, mission: Any) -> float:
        """Helper scoring par défaut - base sur presence docs"""
        return 0.5

    @abstractmethod
    async def execute(self, input: AgentInput) -> AgentOutput:
        """
        ZERO € garanti:
        - Ne retourne JAMAIS montant €, marge, coeff, BFR
        - Retourne uniquement quali + source_pages
        - Math Engine fera chiffrage après
        """
        ...

    def __repr__(self):
        return f"<{self.name} capabilities={self.capabilities} blocking={self.is_blocking}>"
