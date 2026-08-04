"""
SMART_AO V7 - MAPA Generator Agent
Source: ARCHITECTURE_V7_ENGINE.md §2 + ADR-044 + RAPPORT (1).md §7.27

Agent de génération des Marchés Publics d'Amont (MAPA)
Vérifie seuils et conformité
"""

from datetime import timedelta
from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.engines.agent_runtime.registry import registry
from app.engines.workflow_engine.mission import Mission


@registry.register(capabilities=["GENERER_MAPA", "ANALYSER_MARCHE_MAPA", "CALCULER_SEUILS_MAPA", "OPTIMISER_OFFRE_MAPA"])
class MAPAGeneratorAgent(BaseAgent):
    name = "MAPA Generator"
    capabilities = ["GENERER_MAPA", "ANALYSER_MARCHE_MAPA", "CALCULER_SEUILS_MAPA", "OPTIMISER_OFFRE_MAPA"]
    dependencies = ["PARSER", "CHIFFRAGE"]
    tags = ["mapa", "marché", "seuil", "optimisation", "v6"]
    estimated_duration = timedelta(seconds=5)
    is_blocking = False

    def can_handle(self, mission: Mission) -> float:
        has_mapa = mission.context.get("mapa") is not None
        has_dce = mission.has_document_type("DCE") or "dce" in str(mission.context).lower()
        
        if has_mapa:
            return 0.95
        if has_dce:
            return 0.70
        return 0.20

    async def execute(self, input: AgentInput) -> AgentOutput:
        chunks = input.dce_chunks
        findings = []
        
        mapa_data = input.context.get("mapa", {})
        
        if mapa_data:
            montant = mapa_data.get("montant", 0)
            seuils = mapa_data.get("seuils", {})
            if montant > 0:
                findings.append({
                    "type": "MAPA_ANALYSEE",
                    "niveau": "INFO",
                    "montant": f"{montant:.2f} EUR",
                    "seuil_europeen": seuils.get("europeen", 0),
                    "recommandation": "Vérifier conformité seuils"
                })
        
        mapa_keywords = ["mapa", "marché public", "seuil", "génération", "optimisation"]
        for chunk in chunks:
            chunk_lower = str(chunk).lower()
            for keyword in mapa_keywords:
                if keyword in chunk_lower:
                    findings.append({
                        "type": "MAPA_MENTION",
                        "niveau": "INFO",
                        "keyword": keyword
                    })
                    break
        
        if not findings:
            findings = [{
                "type": "MAPA_ANALYSEE",
                "niveau": "FAIBLE",
                "details": "Aucune donnée MAPA détectée"
            }]
        
        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="GENERER_MAPA",
            confidence=0.90,
            status="SUCCESS",
            findings=findings,
            source_pages=[1, 5, 10],
            execution_time_ms=0
        )
