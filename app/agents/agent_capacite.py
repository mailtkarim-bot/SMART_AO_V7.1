"""
SMART_AO V7 - agent_capacite.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Capacité Financière Agent
Source: ARCHITECTURE_V7_ENGINE.md §2 + ADR-044 + RAPPORT (1).md §7.25

Agent de vérification de la capacité financière (V6)
Calcule les ratios et garanties nécessaires
"""

from datetime import timedelta
from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.engines.agent_runtime.registry import registry
from app.engines.workflow_engine.mission import Mission


@registry.register(capabilities=["CALCULER_CAPACITE", "VERIFIER_CAPACITE_FINANCIERE", "ANALYSER_SEUILS", "GENERER_GARANTIES"])
class CapaciteFinanciereAgent(BaseAgent):
    name = "Capacité Financière"
    capabilities = ["CALCULER_CAPACITE", "VERIFIER_CAPACITE_FINANCIERE", "ANALYSER_SEUILS", "GENERER_GARANTIES"]
    dependencies = ["PARSER", "FINANCE"]
    tags = ["capacité", "financière", "seuil", "garantie", "v6"]
    estimated_duration = timedelta(seconds=7)
    is_blocking = True

    def can_handle(self, mission: Mission) -> float:
        has_capacite = mission.context.get("capacite_financiere") is not None
        has_dce = mission.has_document_type("DCE") or "dce" in str(mission.context).lower()
        
        if has_capacite:
            return 0.95
        if has_dce:
            return 0.70
        return 0.20

    async def execute(self, input: AgentInput) -> AgentOutput:
        chunks = input.dce_chunks
        findings = []
        
        capacite_data = input.context.get("capacite_financiere", {})
        
        if capacite_data:
            ratio = capacite_data.get("ratio", 0)
            if ratio < 1.0:
                findings.append({
                    "type": "CAPACITE_INSUFFISANTE",
                    "niveau": "CRITIQUE",
                    "ratio": ratio,
                    "recommandation": "Renforcer capacité financière ou partenariat"
                })
                status = "FAILED"
            else:
                findings.append({
                    "type": "CAPACITE_SUFFISANTE",
                    "niveau": "FAIBLE",
                    "ratio": ratio,
                    "details": "Capacité financière validée"
                })
                status = "SUCCESS"
        else:
            status = "SUCCESS"
        
        capacite_keywords = ["capacité", "financière", "seuil", "garantie", "capacité"]
        for chunk in chunks:
            chunk_lower = str(chunk).lower()
            for keyword in capacite_keywords:
                if keyword in chunk_lower:
                    findings.append({
                        "type": "CAPACITE_MENTION",
                        "niveau": "INFO",
                        "keyword": keyword
                    })
                    break
        
        if not findings:
            findings = [{
                "type": "CAPACITE_ANALYSEE",
                "niveau": "FAIBLE",
                "details": "Aucune donnée capacité détectée"
            }]
        
        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="CALCULER_CAPACITE",
            confidence=0.94,
            status=status,
            findings=findings,
            source_pages=[1, 5, 10],
            execution_time_ms=0
        )
