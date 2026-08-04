"""
SMART_AO V7 - RSE Booster Agent
Source: ARCHITECTURE_V7_ENGINE.md §2 + ADR-044 + RAPPORT (1).md §7.15

Agent d'optimisation RSE (Responsabilité Sociétale des Entreprises)
Bonus 15% sur les offres avec bon score RSE
"""

from datetime import timedelta
from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.engines.agent_runtime.registry import registry
from app.engines.workflow_engine.mission import Mission


@registry.register(capabilities=["ANALYSER_RSE", "CALCULER_SCORE_RSE", "OPTIMISER_RSE", "GENERER_BONUS_RSE"])
class RSEBoosterAgent(BaseAgent):
    name = "RSE Booster"
    capabilities = ["ANALYSER_RSE", "CALCULER_SCORE_RSE", "OPTIMISER_RSE", "GENERER_BONUS_RSE"]
    dependencies = ["PARSER"]
    tags = ["rse", "bonus", "15%", "environnement"]
    estimated_duration = timedelta(seconds=6)
    is_blocking = False

    def can_handle(self, mission: Mission) -> float:
        has_rse = mission.context.get("rse") is not None
        has_dce = mission.has_document_type("DCE") or "dce" in str(mission.context).lower()
        
        if has_rse:
            return 0.95
        if has_dce:
            return 0.70
        return 0.20

    async def execute(self, input: AgentInput) -> AgentOutput:
        chunks = input.dce_chunks
        findings = []
        
        rse_data = input.context.get("rse", {})
        
        if rse_data:
            score = rse_data.get("score", 0)
            if score >= 80:
                bonus = 0.15
                findings.append({
                    "type": "RSE_EXCELLENT",
                    "niveau": "NORMAL",
                    "score": score,
                    "bonus": f"{bonus * 100}%",
                    "recommandation": "Bonus applicable sur l'offre"
                })
            elif score >= 50:
                findings.append({
                    "type": "RSE_BON",
                    "niveau": "MOYEN",
                    "score": score,
                    "recommandation": "Améliorer pour atteindre bonus 15%"
                })
            else:
                findings.append({
                    "type": "RSE_INSUFFISANT",
                    "niveau": "ELEVE",
                    "score": score,
                    "recommandation": "Priorité: améliorer score RSE"
                })
        
        rse_keywords = ["rse", "environnement", "bonus", "développement durable", "15%"]
        for chunk in chunks:
            chunk_lower = str(chunk).lower()
            for keyword in rse_keywords:
                if keyword in chunk_lower:
                    findings.append({
                        "type": "RSE_MENTION",
                        "niveau": "INFO",
                        "keyword": keyword
                    })
                    break
        
        if not findings:
            findings = [{
                "type": "RSE_ANALYSEE",
                "niveau": "FAIBLE",
                "details": "Aucune donnée RSE détectée"
            }]
        
        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="ANALYSER_RSE",
            confidence=0.90,
            status="SUCCESS",
            findings=findings,
            source_pages=[1, 5, 10],
            execution_time_ms=0
        )
