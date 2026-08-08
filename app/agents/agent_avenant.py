"""
SMART_AO V7 - agent_avenant.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Avenant Tracker Agent
Source: ARCHITECTURE_V7_ENGINE.md §2 + ADR-044 + RAPPORT (1).md §7.22

Agent de suivi des avenants et modifications de contrat
Gère les évolutions post-gagné
"""

from datetime import timedelta
from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.engines.agent_runtime.registry import registry
from app.engines.workflow_engine.mission import Mission


@registry.register(capabilities=["SUIVRE_AVENANTS", "ANALYSER_IMPACT_AVENANT", "GENERER_ALERTE_AVENANT", "DETECTER_OPPORTUNITE_AVENANT"])
class AvenantTrackerAgent(BaseAgent):
    name = "Avenant Tracker"
    capabilities = ["SUIVRE_AVENANTS", "ANALYSER_IMPACT_AVENANT", "GENERER_ALERTE_AVENANT", "DETECTER_OPPORTUNITE_AVENANT"]
    dependencies = ["PARSER", "POST_GAGNE"]
    tags = ["avenant", "modification", "contrat", "suivi"]
    estimated_duration = timedelta(seconds=6)
    is_blocking = False

    def can_handle(self, mission: Mission) -> float:
        has_avenants = mission.context.get("avenants") is not None
        has_dce = mission.has_document_type("DCE") or "dce" in str(mission.context).lower()
        
        if has_avenants:
            return 0.95
        if has_dce:
            return 0.70
        return 0.20

    async def execute(self, input: AgentInput) -> AgentOutput:
        chunks = input.dce_chunks
        findings = []
        financial_data = {}
        
        avenants = input.context.get("avenants", [])
        
        if avenants:
            for idx, avenant in enumerate(avenants):
                impact_financier = avenant.get("impact_financier", 0)
                
                # Stocker les données financières
                if impact_financier != 0:
                    financial_data[f"avenant_{idx}"] = {
                        "description": avenant.get("description", ""),
                        "impact_financier": impact_financier,
                        "type": "AUGMENTATION" if impact_financier > 0 else "REDUCTION"
                    }
                
                # Findings qualitatifs UNIQUEMENT
                if impact_financier > 0:
                    findings.append({
                        "type": "AVENANT_AUGMENTATION",
                        "niveau": "ELEVE",
                        "description": avenant.get("description", ""),
                        "details": "Impact financier positif detecte (voir financial_data)",
                        "recommandation": "Evaluer impact sur resultats"
                    })
                elif impact_financier < 0:
                    findings.append({
                        "type": "AVENANT_REDUCTION",
                        "niveau": "INFO",
                        "description": avenant.get("description", ""),
                        "details": "Impact financier negatif detecte (voir financial_data)",
                        "recommandation": "Opportunite a saisir"
                    })
        
        avenant_keywords = ["avenant", "modification", "contrat", "supplément", "réduction"]
        for chunk in chunks:
            chunk_lower = str(chunk).lower()
            for keyword in avenant_keywords:
                if keyword in chunk_lower:
                    findings.append({
                        "type": "AVENANT_MENTION",
                        "niveau": "INFO",
                        "keyword": keyword
                    })
                    break
        
        if not findings:
            findings = [{
                "type": "AVENANT_ANALYSE",
                "niveau": "FAIBLE",
                "details": "Aucun avenant détecté"
            }]
        
        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="SUIVRE_AVENANTS",
            confidence=0.90,
            status="SUCCESS",
            findings=findings,
            financial_data=financial_data if financial_data else None,
            source_pages=[1, 5, 10],
            execution_time_ms=0
        )
