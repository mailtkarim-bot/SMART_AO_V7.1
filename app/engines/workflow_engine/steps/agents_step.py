"""
SMART_AO V7 - agents_step.py
============================
Étape 4 : Orchestration des agents spécialisés sur les données classifiées.
Déclenche les agents pertinents selon la nature des données.
"""
import logging
from typing import Dict, Any, List

from app.engines.workflow_engine.steps.base_step import BaseStep
from app.engines.agent_runtime.registry import AgentRegistry

logger = logging.getLogger(__name__)


class AgentsStep(BaseStep):
    """Étape d'exécution des agents spécialisés."""

    name = "agents_step"
    version = "1.0.0"
    description = "Orchestration et exécution des agents spécialisés sur les données classifiées"

    async def execute(self, mission_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exécute les agents spécialisés sur les données classifiées.
        
        Args:
            mission_id: ID de la mission en cours
            context: Contexte contenant les données classifiées
            
        Returns:
            Dict avec les résultats des analyses des agents
        """
        logger.info(f"[{self.name}] Démarrage de l'exécution des agents pour la mission {mission_id}")
        
        try:
            classified_data = context.get("classified_data", {})
            if not classified_data:
                raise ValueError("Aucune donnée classifiée à analyser")

            registry = AgentRegistry()
            agents_results = {}

            # Sélection des agents à exécuter selon les données présentes
            agents_to_run = self._select_agents(classified_data)
            
            logger.info(f"Agents sélectionnés : {agents_to_run}")

            for agent_name in agents_to_run:
                try:
                    agent = registry.get_agent(agent_name)
                    if agent:
                        logger.debug(f"Exécution de l'agent : {agent_name}")
                        
                        # Préparation des données pour l'agent
                        agent_input = self._prepare_agent_input(agent_name, classified_data)
                        
                        # Exécution de l'agent (P0-4 FIX: utiliser execute() au lieu de analyze())
                        result = await agent.execute(agent_input)
                        
                        agents_results[agent_name] = {
                            "status": "success",
                            "result": result
                        }
                    else:
                        logger.warning(f"Agent {agent_name} non trouvé dans le registry")
                        agents_results[agent_name] = {
                            "status": "error",
                            "error": "Agent not found"
                        }
                        
                except Exception as e:
                    logger.error(f"Erreur lors de l'exécution de l'agent {agent_name}: {str(e)}")
                    agents_results[agent_name] = {
                        "status": "error",
                        "error": str(e)
                    }

            result = {
                "status": "success",
                "agents_executed": len(agents_to_run),
                "agents_results": agents_results,
                "next_step": "compilation_step"
            }

            logger.info(f"[{self.name}] Exécution des agents terminée : {len(agents_results)} résultats")
            return result

        except Exception as e:
            logger.error(f"[{self.name}] Erreur critique lors de l'exécution des agents : {str(e)}")
            return {
                "status": "error",
                "error_code": "AGENTS_EXECUTION_FAILED",
                "error_message": str(e),
                "next_step": None
            }

    def _select_agents(self, classified_data: Dict) -> List[str]:
        """Sélectionne les agents pertinents selon les données classifiées."""
        agents = []
        
        # Toujours exécuter l'agent de synthèse
        agents.append("agent_synthese")
        
        # Agents conditionnels selon les données présentes
        if classified_data.get("critique", []):
            agents.extend(["agent_risque", "agent_deadline"])
        
        if any(d.get("type") == "pab" for items in classified_data.values() 
               for d in items if isinstance(d, dict)):
            agents.append("agent_pab")
        
        if any(d.get("type") == "penalite" for items in classified_data.values() 
               for d in items if isinstance(d, dict)):
            agents.append("agent_penalites")
        
        # Ajout d'agents complémentaires
        agents.extend(["agent_variantes", "agent_memoire"])
        
        return list(set(agents))  # Supprime les doublons

    def _prepare_agent_input(self, agent_name: str, classified_data: Dict) -> Dict:
        """Prépare les données d'entrée pour un agent spécifique."""
        # Implementation simplifiée - à adapter selon chaque agent
        return {
            "classified_data": classified_data,
            "agent_target": agent_name
        }

    async def rollback(self, mission_id: str, context: Dict[str, Any]) -> bool:
        """Nettoie les résultats des agents en cas d'échec global."""
        logger.warning(f"[{self.name}] Rollback demandé pour mission {mission_id}")
        return True
