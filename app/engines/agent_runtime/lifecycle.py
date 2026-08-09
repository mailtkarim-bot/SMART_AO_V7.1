"""SMART_AO V7.1 - Agent Lifecycle Management
Gestion du cycle de vie des agents : registration, health check, metrics.
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class AgentStatus:
    agent_id: str
    status: str  # active, inactive, error
    last_seen: datetime
    metrics: Dict[str, Any] = field(default_factory=dict)

class AgentLifecycleManager:
    """Gère le cycle de vie des 36 agents SMART_AO."""
    
    def __init__(self):
        self.agents: Dict[str, AgentStatus] = {}
    
    def register_agent(self, agent_id: str, capabilities: List[str]) -> bool:
        """Enregistrer un nouvel agent."""
        self.agents[agent_id] = AgentStatus(
            agent_id=agent_id,
            status="active",
            last_seen=datetime.utcnow(),
            metrics={"capabilities": capabilities, "calls": 0}
        )
        logger.info(f"Agent enregistré: {agent_id}")
        return True
    
    def heartbeat(self, agent_id: str) -> None:
        """Mettre à jour le last_seen d'un agent."""
        if agent_id in self.agents:
            self.agents[agent_id].last_seen = datetime.utcnow()
    
    def get_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Obtenir le statut d'un agent."""
        if agent_id not in self.agents:
            return None
        status = self.agents[agent_id]
        return {
            "agent_id": status.agent_id,
            "status": status.status,
            "last_seen": status.last_seen.isoformat(),
            "metrics": status.metrics
        }
    
    def list_agents(self, status_filter: str = None) -> List[Dict[str, Any]]:
        """Lister tous les agents avec filtrage optionnel."""
        result = []
        for agent_id, status in self.agents.items():
            if status_filter and status.status != status_filter:
                continue
            result.append(self.get_status(agent_id))
        return result
    
    def unregister_agent(self, agent_id: str) -> bool:
        """Désenregistrer un agent."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"Agent désenregistré: {agent_id}")
            return True
        return False

# Instance globale
lifecycle_manager = AgentLifecycleManager()
