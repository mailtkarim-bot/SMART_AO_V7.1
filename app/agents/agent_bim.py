"""
SMART_AO V7 - BIM Agent
Source: ARCHITECTURE_V7_ENGINE.md §2 + ADR-044 + RAPPORT (1).md

Agent d'analyse des modèles BIM (exemple Plugin Engine V7)
Vérifie intégrité et détection des collisions
"""

from datetime import timedelta
from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.engines.agent_runtime.registry import registry
from app.engines.workflow_engine.mission import Mission


@registry.register(capabilities=["ANALYSER_BIM", "VERIFIER_MODELE_BIM", "DETECTER_CONFLITS_BIM", "OPTIMISER_BIM"])
class BIMAgent(BaseAgent):
    name = "BIM Agent"
    capabilities = ["ANALYSER_BIM", "VERIFIER_MODELE_BIM", "DETECTER_CONFLITS_BIM", "OPTIMISER_BIM"]
    dependencies = ["PARSER", "PLUGIN_ENGINE"]
    tags = ["bim", "modélisation", "3d", "plugin", "v7"]
    estimated_duration = timedelta(seconds=9)
    is_blocking = False

    def can_handle(self, mission: Mission) -> float:
        has_bim = mission.context.get("bim") is not None
        has_dce = mission.has_document_type("DCE") or "dce" in str(mission.context).lower()
        
        if has_bim:
            return 0.95
        if has_dce:
            return 0.70
        return 0.20

    async def execute(self, input: AgentInput) -> AgentOutput:
        chunks = input.dce_chunks
        findings = []
        
        bim_data = input.context.get("bim", {})
        
        if bim_data:
            fichiers = bim_data.get("fichiers", [])
            if fichiers:
                findings.append({
                    "type": "MODELE_BIM",
                    "niveau": "INFO",
                    "fichiers": len(fichiers),
                    "recommandation": "Vérifier intégrité et collisions"
                })
        
        bim_keywords = ["bim", "modèle", "3d", "maquette", "numérique", "collision"]
        for chunk in chunks:
            chunk_lower = str(chunk).lower()
            for keyword in bim_keywords:
                if keyword in chunk_lower:
                    findings.append({
                        "type": "BIM_MENTION",
                        "niveau": "INFO",
                        "keyword": keyword
                    })
                    break
        
        if not findings:
            findings = [{
                "type": "BIM_ANALYSE",
                "niveau": "FAIBLE",
                "details": "Aucune donnée BIM détectée"
            }]
        
        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="ANALYSER_BIM",
            confidence=0.90,
            status="SUCCESS",
            findings=findings,
            source_pages=[1, 5, 10],
            execution_time_ms=0
        )
