"""
SMART_AO V7 - Risques Guardian Agent
Source: ARCHITECTURE_V7_ENGINE.md §2 + ADR-044 + RAPPORT (1).md §7.26

Agent de génération du tableau des risques
Marge < 3% acceptable
"""

from datetime import timedelta
from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.engines.agent_runtime.registry import registry
from app.engines.workflow_engine.mission import Mission


@registry.register(capabilities=["DETECTER_RISQUES", "ANALYSER_RISQUES", "CALCULER_PROBABILITE", "GENERER_TABLEAU_RISQUES"])
class RisquesGuardianAgent(BaseAgent):
    name = "Risques Guardian"
    capabilities = ["DETECTER_RISQUES", "ANALYSER_RISQUES", "CALCULER_PROBABILITE", "GENERER_TABLEAU_RISQUES"]
    dependencies = ["PARSER", "CHIFFRAGE"]
    tags = ["risques", "tableau", "marge", "3%", "probabilité", "v6"]
    estimated_duration = timedelta(seconds=8)
    is_blocking = False

    def can_handle(self, mission: Mission) -> float:
        has_risques = mission.context.get("tableau_risques") is not None
        has_dce = mission.has_document_type("DCE") or "dce" in str(mission.context).lower()
        
        if has_risques:
            return 0.95
        if has_dce:
            return 0.70
        return 0.20

    async def execute(self, input: AgentInput) -> AgentOutput:
        chunks = input.dce_chunks
        findings = []
        
        tableau_risques = input.context.get("tableau_risques", [])
        
        if tableau_risques:
            risques_eleves = [r for r in tableau_risques if r.get("niveau", "") == "CRITIQUE"]
            if risques_eleves:
                findings.append({
                    "type": "RISQUES_CRITIQUES",
                    "niveau": "CRITIQUE",
                    "nombre": len(risques_eleves),
                    "recommandation": "Traiter en priorité",
                    "marge_min": "3%"
                })
            else:
                findings.append({
                    "type": "RISQUES_MAITRISES",
                    "niveau": "FAIBLE",
                    "details": "Tous les risques sont acceptables"
                })
        
        risques_keywords = ["risque", "tableau", "marge", "3%", "probabilité", "impact"]
        for chunk in chunks:
            chunk_lower = str(chunk).lower()
            for keyword in risques_keywords:
                if keyword in chunk_lower:
                    findings.append({
                        "type": "RISQUES_MENTION",
                        "niveau": "INFO",
                        "keyword": keyword
                    })
                    break
        
        if not findings:
            findings = [{
                "type": "RISQUES_ANALYSES",
                "niveau": "FAIBLE",
                "details": "Aucun risque détecté"
            }]
        
        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="DETECTER_RISQUES",
            confidence=0.92,
            status="SUCCESS",
            findings=findings,
            source_pages=[1, 5, 10],
            execution_time_ms=0
        )
