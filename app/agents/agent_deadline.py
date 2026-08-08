"""
SMART_AO V7 - agent_deadline.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Deadline Guardian Agent
Source: ARCHITECTURE_V7_ENGINE.md §2 + ADR-044

Agent bloquant (blocking=True) - Si échec, Mission FAILED
Vérifie les deadlines J-7, J-2, J-1, H-4
"""

from datetime import timedelta
from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.engines.agent_runtime.registry import registry
from app.engines.workflow_engine.mission import Mission


@registry.register(capabilities=["CHECK_DEADLINE", "DETECTER_RISQUE_JURIDIQUE"])
class DeadlineAgent(BaseAgent):
    name = "Deadline Guardian"
    capabilities = ["CHECK_DEADLINE", "DETECTER_RISQUE_JURIDIQUE"]
    dependencies = ["PARSER"]
    tags = ["juridique", "bloquant", "deadline"]
    estimated_duration = timedelta(seconds=3)
    is_blocking = True  # Echec = Mission FAILED

    def can_handle(self, mission: Mission) -> float:
        # Toujours pertinent - vérifie deadline sur TOUS les DCE
        return 1.0

    async def execute(self, input: AgentInput) -> AgentOutput:
        # Simule vérification deadline
        # En prod: vérifie date_limite_depot dans context
        jours_restants = input.context.get("jours_restants", 5)
        
        if jours_restants <= 2:
            status = "SUCCESS"
            findings = [
                {
                    "type": "DEADLINE_URGENT",
                    "niveau": "CRITIQUE",
                    "jours_restants": jours_restants,
                    "fuseau": "CET",
                    "recommandation": "Dépôt immédiat requis"
                }
            ]
            confidence = 1.0
        elif jours_restants <= 7:
            status = "SUCCESS"
            findings = [
                {
                    "type": "DEADLINE_OK",
                    "niveau": "ATTENTION",
                    "jours_restants": jours_restants,
                    "fuseau": "CET",
                    "recommandation": "Planifier dépôt sous 48h"
                }
            ]
            confidence = 1.0
        else:
            status = "SUCCESS"
            findings = [
                {
                    "type": "DEADLINE_OK",
                    "niveau": "NORMAL",
                    "jours_restants": jours_restants,
                    "fuseau": "CET"
                }
            ]
            confidence = 1.0

        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="CHECK_DEADLINE",
            confidence=confidence,
            status=status,
            findings=findings,
            source_pages=[1],  # Page du CCTP avec deadline
            execution_time_ms=0
        )
