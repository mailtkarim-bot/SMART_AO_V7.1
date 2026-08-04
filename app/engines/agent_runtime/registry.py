"""
SMART_AO V7 - Agent Registry - Découverte par capacités
Source: ARCHITECTURE_V7_ENGINE.md §3 + ADR-042

L'orchestrateur ne connait plus aucun agent. Il connait des capacités.
registry.find_by_capability("DETECTER_PAB") -> [PABAgent, ...]

NOTE: Ce module doit être importé AVANT les agents pour éviter les circular imports.
"""

from typing import List, Dict, Type, Optional, Callable
import pkgutil
import importlib
import logging
from collections import defaultdict
import sys

# Import différé pour éviter circular import avec app.agents
# BaseAgent sera importé quand nécessaire

logger = logging.getLogger(__name__)


class AgentRegistry:
    """
    Singleton Registry - RH des agents
    Thread-safe pour boot single-tenant VPS
    """
    _instance: Optional["AgentRegistry"] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._agents_by_capability: Dict[str, List] = defaultdict(list)
        self._agents_by_name: Dict[str, object] = {}
        self._all_agents: List[object] = []
        self._initialized = True
        logger.info("AgentRegistry initialized - V7 OS Kernel")

    def register(self, capabilities: List[str]):
        """
        Decorator d'enregistrement
        Usage:
            @registry.register(capabilities=["DETECTER_PAB"])
            class PABAgent(BaseAgent): ...
        """
        def decorator(cls: Type):
            try:
                instance = cls()
                # Vérifier que c'est un BaseAgent (import différé)
                from app.agents.base_agent import BaseAgent
                if not isinstance(instance, BaseAgent):
                    raise TypeError(f"{cls.__name__} must inherit BaseAgent")

                # Index par capacité
                for cap in capabilities:
                    cap_upper = cap.upper()
                    # Dédup par nom
                    if instance not in self._agents_by_capability[cap_upper]:
                        self._agents_by_capability[cap_upper].append(instance)

                # Index par nom
                self._agents_by_name[instance.name] = instance

                # Liste globale dédupliquée
                if instance not in self._all_agents:
                    self._all_agents.append(instance)

                logger.info(f"Registered {instance.name} -> {capabilities}")
            except Exception as e:
                logger.error(f"Failed to register {cls.__name__}: {e}")
                raise
            return cls
        return decorator

    def find_by_capability(self, capability: str) -> List:
        """SSoT découverte - Orchestrateur appelle ça, pas de fichier"""
        return list(self._agents_by_capability.get(capability.upper(), []))

    def find_by_tags(self, tags: List[str]) -> List:
        """Intersection tags - ex: ['finance', 'bloquant']"""
        tags_set = set(t.lower() for t in tags)
        result = []
        for agent in self._all_agents:
            agent_tags = set(t.lower() for t in agent.tags)
            if tags_set.intersection(agent_tags):
                result.append(agent)
        return result

    def get_all(self) -> List:
        return list(self._all_agents)

    def get_by_name(self, name: str) -> Optional[object]:
        return self._agents_by_name.get(name)

    def clear(self):
        """Pour tests uniquement"""
        self._agents_by_capability.clear()
        self._agents_by_name.clear()
        self._all_agents.clear()
        logger.warning("Registry cleared - tests only")

    def auto_discover(self, package: str = "app.agents"):
        """
        Auto-discovery au boot V7
        Scan tous les modules app.agents.agent_*.py et importe
        Chaque fichier a @registry.register au top-level -> auto-enregistré
        """
        logger.info(f"Auto-discovering agents in {package}...")
        try:
            pkg = importlib.import_module(package)
            for _, modname, _ in pkgutil.iter_modules(pkg.__path__, package + "."):
                if "agent_" in modname or modname.endswith("_agent"):
                    try:
                        importlib.import_module(modname)
                        logger.debug(f"Discovered {modname}")
                    except Exception as e:
                        logger.warning(f"Failed to import {modname}: {e}")
        except ModuleNotFoundError:
            # En test, package n'existe pas encore - normal
            logger.warning(f"Package {package} not found, skipping auto-discover (test mode)")
        logger.info(f"Discovery done: {len(self._all_agents)} agents, {len(self._agents_by_capability)} capabilities")

    def stats(self) -> Dict:
        return {
            "total_agents": len(self._all_agents),
            "total_capabilities": len(self._agents_by_capability),
            "capabilities": {k: [a.name for a in v] for k, v in self._agents_by_capability.items()}
        }


# Singleton global - import partout
registry = AgentRegistry()
