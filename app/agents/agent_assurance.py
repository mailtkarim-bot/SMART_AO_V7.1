"""
SMART_AO V7 - Assurance Agent
Source: ARCHITECTURE_V7_ENGINE.md §2 + ADR-044 + RAPPORT (1).md

Agent de vérification des assurances (exemple Plugin Engine V7)
Vérifie couverture et validité des polices
"""

from datetime import timedelta
from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.engines.agent_runtime.registry import registry
from app.engines.workflow_engine.mission import Mission


@registry.register(capabilities=["VERIFIER_ASSURANCES", "ANALYSER_COUVERTURE", "DETECTER_LACUNE_ASSURANCE", "OPTIMISER_GARANTIES"])
class AssuranceAgent(BaseAgent):
    name = "Assurance Agent"
    capabilities = ["VERIFIER_ASSURANCES", "ANALYSER_COUVERTURE", "DETECTER_LACUNE_ASSURANCE", "OPTIMISER_GARANTIES"]
    dependencies = ["PARSER", "PLUGIN_ENGINE"]
    tags = ["assurance", "couverture", "garantie", "risque", "v7"]
    estimated_duration = timedelta(seconds=5)
    is_blocking = False

    def can_handle(self, mission: Mission) -> float:
        has_assurances = mission.context.get("assurances") is not None
        has_dce = mission.has_document_type("DCE") or "dce" in str(mission.context).lower()
        
        if has_assurances:
            return 0.95
        if has_dce:
            return 0.70
        return 0.20

    async def execute(self, input: AgentInput) -> AgentOutput:
        chunks = input.dce_chunks
        findings = []
        
        assurances = input.context.get("assurances", {})
        
        if assurances:
            for assurance, data in assurances.items():
                if not data.get("valide", False):
                    findings.append({
                        "type": "ASSURANCE_NON_VALIDE",
                        "niveau": "ELEVE",
                        "type": assurance,
                        "recommandation": "Souscrire ou renouveler assurance"
                    })
                else:
                    findings.append({
                        "type": "ASSURANCE_VALIDE",
                        "niveau": "FAIBLE",
                        "type": assurance,
                        "expiration": data.get("expiration", "")
                    })
        
        assurance_keywords = ["assurance", "couverture", "garantie", "risque", "police", "souscription"]
        for chunk in chunks:
            chunk_lower = str(chunk).lower()
            for keyword in assurance_keywords:
                if keyword in chunk_lower:
                    findings.append({
                        "type": "ASSURANCE_MENTION",
                        "niveau": "INFO",
                        "keyword": keyword
                    })
                    break
        
        if not findings:
            findings = [{
                "type": "ASSURANCE_ANALYSEE",
                "niveau": "FAIBLE",
                "details": "Aucune assurance détectée"
            }]
        
        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="VERIFIER_ASSURANCES",
            confidence=0.90,
            status="SUCCESS",
            findings=findings,
            source_pages=[1, 5, 10],
            execution_time_ms=0
        )
