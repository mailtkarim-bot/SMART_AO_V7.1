"""
SMART_AO V7 - base_step.py
=========================
Classe de base pour toutes les étapes du workflow.
"""
import logging
from typing import Dict, Any
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseStep(ABC):
    """
    Classe de base abstraite pour toutes les étapes du workflow.
    
    Chaque étape du workflow doit implémenter la méthode execute().
    """
    
    name: str = ""
    version: str = "1.0.0"
    description: str = ""
    
    @abstractmethod
    async def execute(self, mission_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exécute l'étape du workflow.
        
        Args:
            mission_id: ID de la mission en cours
            context: Contexte contenant les données nécessaires
            
        Returns:
            Dict avec les résultats de l'exécution et le next_step
        """
        pass
    
    async def rollback(self, mission_id: str, context: Dict[str, Any]) -> bool:
        """
        Nettoie les résultats en cas d'échec global.
        
        Args:
            mission_id: ID de la mission en cours
            context: Contexte contenant les données nécessaires
            
        Returns:
            bool: True si le rollback a réussi, False sinon
        """
        logger.warning(f"[{self.name}] Rollback demandé pour mission {mission_id}")
        return True
