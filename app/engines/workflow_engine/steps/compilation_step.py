"""
SMART_AO V7 - compilation_step.py
=================================
Étape 5 : Compilation et agrégation des résultats des agents.
Fusionne les analyses en un rapport cohérent.
"""
import logging
from typing import Dict, Any, List
from datetime import datetime

from app.engines.workflow_engine.steps.base_step import BaseStep

logger = logging.getLogger(__name__)


class CompilationStep(BaseStep):
    """Étape de compilation des résultats des agents."""

    name = "compilation_step"
    version = "1.0.0"
    description = "Compilation et agrégation des résultats des agents en un rapport unifié"

    async def execute(self, mission_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compile les résultats de tous les agents exécutés.
        
        Args:
            mission_id: ID de la mission en cours
            context: Contexte contenant les résultats des agents
            
        Returns:
            Dict avec le rapport compilé et structuré
        """
        logger.info(f"[{self.name}] Démarrage de la compilation pour la mission {mission_id}")
        
        try:
            agents_results = context.get("agents_results", {})
            if not agents_results:
                raise ValueError("Aucun résultat d'agent à compiler")

            # Agrégation des résultats
            compiled_report = {
                "mission_id": mission_id,
                "compiled_at": datetime.utcnow().isoformat(),
                "summary": self._generate_summary(agents_results),
                "analyses": {},
                "recommandations": [],
                "alertes": []
            }

            # Traitement de chaque résultat d'agent
            for agent_name, result_data in agents_results.items():
                if result_data.get("status") == "success":
                    analyse = result_data.get("result", {})
                    compiled_report["analyses"][agent_name] = analyse
                    
                    # Extraction des alertes critiques
                    alertes = self._extract_alertes(analyse, agent_name)
                    compiled_report["alertes"].extend(alertes)
                    
                    # Extraction des recommandations
                    recommandations = self._extract_recommandations(analyse, agent_name)
                    compiled_report["recommandations"].extend(recommandations)
                else:
                    logger.warning(f"Résultat de l'agent {agent_name} ignoré (échec)")

            # Tri des alertes par criticité
            compiled_report["alertes"] = sorted(
                compiled_report["alertes"],
                key=lambda x: x.get("niveau", "low"),
                reverse=True
            )

            result = {
                "status": "success",
                "compiled_report": compiled_report,
                "stats": {
                    "agents_successful": sum(1 for r in agents_results.values() if r.get("status") == "success"),
                    "agents_failed": sum(1 for r in agents_results.values() if r.get("status") != "success"),
                    "alertes_count": len(compiled_report["alertes"]),
                    "recommandations_count": len(compiled_report["recommandations"])
                },
                "next_step": "rapport_step"
            }

            logger.info(f"[{self.name}] Compilation terminée : {result['stats']}")
            return result

        except Exception as e:
            logger.error(f"[{self.name}] Erreur critique lors de la compilation : {str(e)}")
            return {
                "status": "error",
                "error_code": "COMPILATION_FAILED",
                "error_message": str(e),
                "next_step": None
            }

    def _generate_summary(self, agents_results: Dict) -> Dict[str, Any]:
        """Génère un résumé global des analyses."""
        total_agents = len(agents_results)
        successful_agents = sum(1 for r in agents_results.values() if r.get("status") == "success")
        
        return {
            "total_agents": total_agents,
            "successful_agents": successful_agents,
            "success_rate": (successful_agents / total_agents * 100) if total_agents > 0 else 0,
            "global_status": "OK" if successful_agents == total_agents else "PARTIAL"
        }

    def _extract_alertes(self, analyse: Dict, agent_name: str) -> List[Dict]:
        """Extrait les alertes depuis une analyse d'agent."""
        alertes = []
        
        # Recherche d'alertes dans la structure de résultat
        if isinstance(analyse, dict):
            for key, value in analyse.items():
                if "alerte" in key.lower() or "risk" in key.lower():
                    alertes.append({
                        "source_agent": agent_name,
                        "type": key,
                        "content": value,
                        "niveau": self._evaluer_niveau_alerte(value)
                    })
        
        return alertes

    def _extract_recommandations(self, analyse: Dict, agent_name: str) -> List[Dict]:
        """Extrait les recommandations depuis une analyse d'agent."""
        recommandations = []
        
        if isinstance(analyse, dict):
            for key, value in analyse.items():
                if "recommandation" in key.lower() or "conseil" in key.lower():
                    recommandations.append({
                        "source_agent": agent_name,
                        "type": key,
                        "content": value
                    })
        
        return recommandations

    def _evaluer_niveau_alerte(self, value: Any) -> str:
        """Évalue le niveau d'une alerte selon son contenu."""
        if isinstance(value, str):
            value_lower = value.lower()
            if any(word in value_lower for word in ["critique", "urgent", "grave"]):
                return "high"
            elif any(word in value_lower for word in ["important", "majeur"]):
                return "medium"
        return "low"

    async def rollback(self, mission_id: str, context: Dict[str, Any]) -> bool:
        """Nettoie le rapport compilé en cas d'échec global."""
        logger.warning(f"[{self.name}] Rollback demandé pour mission {mission_id}")
        return True
