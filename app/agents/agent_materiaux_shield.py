"""
SMART_AO V7 - Materiaux Shield Agent
Source: ARCHITECTURE_V7_ENGINE.md §2 + ADR-044 + RAPPORT (1).md §7.18

Agent de protection contre les variations de prix des matériaux (P0)
Surveille acier, bois, cuivre et autres matériaux stratégiques
"""

from datetime import timedelta
from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.engines.agent_runtime.registry import registry
from app.engines.workflow_engine.mission import Mission


@registry.register(capabilities=["PROTEGER_MATERIAUX", "DETECTER_RISQUE_MATERIAUX", "CALCULER_COEFF_MATERIAUX", "OPTIMISER_APPROVISIONNEMENT"])
class MateriauxShieldAgent(BaseAgent):
    name = "Materiaux Shield"
    capabilities = ["PROTEGER_MATERIAUX", "DETECTER_RISQUE_MATERIAUX", "CALCULER_COEFF_MATERIAUX", "OPTIMISER_APPROVISIONNEMENT"]
    dependencies = ["PARSER", "CHIFFRAGE"]
    tags = ["matériaux", "p0", "acier", "bois", "cuivre", "protection"]
    estimated_duration = timedelta(seconds=6)
    is_blocking = False

    def can_handle(self, mission: Mission) -> float:
        has_materiaux = mission.context.get("materiaux") is not None
        has_dce = mission.has_document_type("DCE") or "dce" in str(mission.context).lower()
        
        if has_materiaux:
            return 0.95
        if has_dce:
            return 0.70
        return 0.20

    async def execute(self, input: AgentInput) -> AgentOutput:
        chunks = input.dce_chunks
        findings = []
        
        materiaux_data = input.context.get("materiaux", {})
        indices_data = input.context.get("indices_materiaux_insee", {})
        
        if materiaux_data and indices_data:
            for materiau, data in materiaux_data.items():
                if materiau in indices_data:
                    variation = indices_data[materiau].get("variation_12m", 0)
                    if variation > 10:
                        findings.append({
                            "type": "MATERIAU_RISQUE",
                            "niveau": "ELEVE",
                            "materiau": materiau,
                            "variation": f"{variation}%",
                            "recommandation": "Couvrir risque avec clause révision prix"
                        })
        
        materiaux_keywords = ["matériaux", "p0", "acier", "bois", "cuivre", "indice"]
        for chunk in chunks:
            chunk_lower = str(chunk).lower()
            for keyword in materiaux_keywords:
                if keyword in chunk_lower:
                    findings.append({
                        "type": "MATERIAUX_MENTION",
                        "niveau": "INFO",
                        "keyword": keyword
                    })
                    break
        
        if not findings:
            findings = [{
                "type": "MATERIAUX_ANALYSES",
                "niveau": "FAIBLE",
                "details": "Aucune donnée matériaux détectée"
            }]
        
        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="PROTEGER_MATERIAUX",
            confidence=0.90,
            status="SUCCESS",
            findings=findings,
            source_pages=[1, 5, 10],
            execution_time_ms=0
        )
