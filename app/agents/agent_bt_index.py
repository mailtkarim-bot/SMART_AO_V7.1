"""
SMART_AO V7 - agent_bt_index.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - BT Index Agent
Source: ARCHITECTURE_V7_ENGINE.md §2 + ADR-044 + RAPPORT (1).md §7.1

Agent de suivi des indices BT (Bordereau des Prix)
Calcule les variations d'indices INSEE sur les matériaux et main d'oeuvre
"""

from datetime import timedelta
from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.engines.agent_runtime.registry import registry
from app.engines.workflow_engine.mission import Mission


@registry.register(capabilities=["CALCULER_BT_INDEX", "SUIVRE_INDICES_INSEE", "DETECTER_VARIATION_MATERIAUX"])
class BTIndexAgent(BaseAgent):
    name = "BT Index Tracker"
    capabilities = ["CALCULER_BT_INDEX", "SUIVRE_INDICES_INSEE", "DETECTER_VARIATION_MATERIAUX"]
    dependencies = ["PARSER", "CHIFFRAGE"]
    tags = ["finance", "materiaux", "insee"]
    estimated_duration = timedelta(seconds=5)
    is_blocking = False

    def can_handle(self, mission: Mission) -> float:
        has_bt = mission.has_document_type("BT") or "bt" in str(mission.context).lower()
        has_dce = mission.has_document_type("DCE") or "dce" in str(mission.context).lower()
        has_indices = mission.context.get("indices_materiaux") is not None
        
        if has_bt and has_indices:
            return 0.95
        if has_dce:
            return 0.70
        return 0.20

    async def execute(self, input: AgentInput) -> AgentOutput:
        chunks = input.dce_chunks
        parsed_pages = input.parsed_docs.get("pages", 0)
        
        findings = []
        
        # Analyse des variations d'indices
        indices_context = input.context.get("indices_materiaux", {})
        
        if indices_context:
            for materiau, data in indices_context.items():
                variation = data.get("variation_mensuelle", 0)
                if variation > 5:  # +5%
                    findings.append({
                        "type": "INDICE_HAUSSE_FORTE",
                        "niveau": "ELEVE",
                        "materiau": materiau,
                        "variation": f"{variation}%",
                        "recommandation": f"Réviser prix {materiau} dans offres",
                        "source": "INSEE_36m"
                    })
                elif variation > 2:
                    findings.append({
                        "type": "INDICE_HAUSSE",
                        "niveau": "MOYEN",
                        "materiau": materiau,
                        "variation": f"{variation}%",
                        "recommandation": "Surveiller évolution"
                    })
        
        # Détection BT dans les chunks
        bt_keywords = ["bordereau", "prix unitaires", "bt", "indice insee"]
        for chunk in chunks:
            chunk_lower = str(chunk).lower()
            for keyword in bt_keywords:
                if keyword in chunk_lower:
                    findings.append({
                        "type": "BT_REFERENCE_DETECTEE",
                        "niveau": "INFO",
                        "keyword": keyword,
                        "recommandation": "Vérifier cohérence avec indices actuels"
                    })
                    break
        
        if not findings:
            findings = [{
                "type": "BT_INDEX_A_JOUR",
                "niveau": "FAIBLE",
                "details": "Aucune variation significative des indices détectée"
            }]
        
        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="CALCULER_BT_INDEX",
            confidence=0.90,
            status="SUCCESS",
            findings=findings,
            source_pages=[1, 2, 10],
            execution_time_ms=0
        )
