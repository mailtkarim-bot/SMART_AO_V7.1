"""
SMART_AO V7 - classification_step.py
====================================
Étape 3 : Classification et catégorisation des données extraites.
Organise les informations par thématique et priorité.
"""
import logging
from typing import Dict, Any, List

from app.engines.workflow_engine.steps.base_step import BaseStep

logger = logging.getLogger(__name__)


class ClassificationStep(BaseStep):
    """Étape de classification des données extraites."""

    name = "classification_step"
    version = "1.0.0"
    description = "Classification des données par thématique, criticité et priorité"

    async def execute(self, mission_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classe les données extraites selon leur nature et criticité.
        
        Args:
            mission_id: ID de la mission en cours
            context: Contexte contenant les données extraites
            
        Returns:
            Dict avec les données classifiées et hiérarchisées
        """
        logger.info(f"[{self.name}] Démarrage de la classification pour la mission {mission_id}")
        
        try:
            extracted_data = context.get("extracted_data", {})
            if not extracted_data:
                raise ValueError("Aucune donnée extraite à classifier")

            # Classification par criticité
            classified = {
                "critique": [],
                "majeur": [],
                "mineur": [],
                "information": []
            }

            # Traitement des deadlines
            for deadline in extracted_data.get("deadlines", []):
                niveau = self._evaluer_criticite_deadline(deadline)
                classified[niveau].append({
                    "type": "deadline",
                    "data": deadline,
                    "niveau": niveau
                })

            # Traitement des pénalités
            for penalite in extracted_data.get("penalites", []):
                niveau = self._evaluer_criticite_penalite(penalite)
                classified[niveau].append({
                    "type": "penalite",
                    "data": penalite,
                    "niveau": niveau
                })

            # Traitement des clauses PAB
            for pab in extracted_data.get("pab_clauses", []):
                # PAB est toujours critique
                classified["critique"].append({
                    "type": "pab",
                    "data": pab,
                    "niveau": "critique"
                })

            result = {
                "status": "success",
                "classified_data": classified,
                "summary": {
                    "critique_count": len(classified["critique"]),
                    "majeur_count": len(classified["majeur"]),
                    "mineur_count": len(classified["mineur"]),
                    "information_count": len(classified["information"])
                },
                "next_step": "agents_step"
            }

            logger.info(f"[{self.name}] Classification terminée : {result['summary']}")
            return result

        except Exception as e:
            logger.error(f"[{self.name}] Erreur critique lors de la classification : {str(e)}")
            return {
                "status": "error",
                "error_code": "CLASSIFICATION_FAILED",
                "error_message": str(e),
                "next_step": None
            }

    def _evaluer_criticite_deadline(self, deadline: Dict) -> str:
        """Évalue la criticité d'une deadline."""
        jours_restants = deadline.get("jours_restants", 999)
        
        if jours_restants <= 3:
            return "critique"
        elif jours_restants <= 7:
            return "majeur"
        elif jours_restants <= 14:
            return "mineur"
        else:
            return "information"

    def _evaluer_criticite_penalite(self, penalite: Dict) -> str:
        """Évalue la criticité d'une pénalité."""
        montant = penalite.get("montant_estime", 0)
        frequence = penalite.get("frequence", "ponctuelle")
        
        if montant > 10000 or frequence == "quotidienne":
            return "critique"
        elif montant > 5000 or frequence == "hebdomadaire":
            return "majeur"
        elif montant > 1000:
            return "mineur"
        else:
            return "information"

    async def rollback(self, mission_id: str, context: Dict[str, Any]) -> bool:
        """Nettoie les données classifiées en cas d'échec global."""
        logger.warning(f"[{self.name}] Rollback demandé pour mission {mission_id}")
        return True
