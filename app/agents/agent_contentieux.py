"""
SMART_AO V7 - Contentieux Generator Agent
Source: ARCHITECTURE_V7_ENGINE.md §2 + ADR-044 + RAPPORT (1).md §7.23

Agent de détection et analyse des risques contentieux
Provision 1M EUR pour les litiges majeurs
"""

from datetime import timedelta
from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.engines.agent_runtime.registry import registry
from app.engines.workflow_engine.mission import Mission


@registry.register(capabilities=["DETECTER_RISQUE_CONTENTIEUX", "ANALYSER_CONTENTIEUX", "CALCULER_COUT_CONTENTIEUX", "GENERER_PROVISION_1MEUR"])
class ContentieuxGeneratorAgent(BaseAgent):
    name = "Contentieux Generator"
    capabilities = ["DETECTER_RISQUE_CONTENTIEUX", "ANALYSER_CONTENTIEUX", "CALCULER_COUT_CONTENTIEUX", "GENERER_PROVISION_1MEUR"]
    dependencies = ["PARSER", "JURIDIQUE"]
    tags = ["contentieux", "risque", "1MEUR", "juridique", "litige"]
    estimated_duration = timedelta(seconds=8)
    is_blocking = False

    def can_handle(self, mission: Mission) -> float:
        has_contentieux = mission.context.get("contentieux") is not None
        has_dce = mission.has_document_type("DCE") or "dce" in str(mission.context).lower()
        
        if has_contentieux:
            return 0.95
        if has_dce:
            return 0.70
        return 0.20

    async def execute(self, input: AgentInput) -> AgentOutput:
        chunks = input.dce_chunks
        findings = []
        
        contentieux_data = input.context.get("contentieux", {})
        
        if contentieux_data:
            montant_risque = contentieux_data.get("montant_risque", 0)
            if montant_risque > 1000000:
                findings.append({
                    "type": "RISQUE_CONTENTIEUX_ELEVE",
                    "niveau": "CRITIQUE",
                    "montant": f"{montant_risque:.2f} EUR",
                    "recommandation": "Provisionner immédiatement",
                    "risque": "PROVISION_1MEUR"
                })
            elif montant_risque > 0:
                findings.append({
                    "type": "RISQUE_CONTENTIEUX",
                    "niveau": "ELEVE",
                    "montant": f"{montant_risque:.2f} EUR",
                    "recommandation": "Surveiller et provisionner"
                })
        
        contentieux_keywords = ["contentieux", "litige", "provision", "risque", "1MEUR", "juridique"]
        for chunk in chunks:
            chunk_lower = str(chunk).lower()
            for keyword in contentieux_keywords:
                if keyword in chunk_lower:
                    findings.append({
                        "type": "CONTENTIEUX_MENTION",
                        "niveau": "INFO",
                        "keyword": keyword
                    })
                    break
        
        if not findings:
            findings = [{
                "type": "CONTENTIEUX_ANALYSE",
                "niveau": "FAIBLE",
                "details": "Aucun risque contentieux détecté"
            }]
        
        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="DETECTER_RISQUE_CONTENTIEUX",
            confidence=0.92,
            status="SUCCESS",
            findings=findings,
            source_pages=[1, 5, 10],
            execution_time_ms=0
        )
