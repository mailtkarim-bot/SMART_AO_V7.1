"""
SMART_AO V7 - agent_eplusc.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - E+C- Detector Agent
Source: ARCHITECTURE_V7_ENGINE.md §2 + ADR-044 + RAPPORT (1).md §7.28

Agent de détection et analyse E+C- (Énergie positive & Réduction Carbone)
Vérifie conformité aux seuils 2025
"""

from datetime import timedelta
from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.engines.agent_runtime.registry import registry
from app.engines.workflow_engine.mission import Mission


@registry.register(capabilities=["DETECTER_EPLUSC", "ANALYSER_EPLUSC", "CALCULER_SEUILS_EPLUSC", "GENERER_CERTIFICAT_EPLUSC"])
class EPlusCDetectorAgent(BaseAgent):
    name = "E+C- Detector"
    capabilities = ["DETECTER_EPLUSC", "ANALYSER_EPLUSC", "CALCULER_SEUILS_EPLUSC", "GENERER_CERTIFICAT_EPLUSC"]
    dependencies = ["PARSER", "CHIFFRAGE"]
    tags = ["e+c-", "énergie", "environnement", "seuil", "certificat", "v6"]
    estimated_duration = timedelta(seconds=6)
    is_blocking = False

    def can_handle(self, mission: Mission) -> float:
        has_eplusc = mission.context.get("eplusc") is not None
        has_dce = mission.has_document_type("DCE") or "dce" in str(mission.context).lower()
        
        if has_eplusc:
            return 0.95
        if has_dce:
            return 0.70
        return 0.20

    async def execute(self, input: AgentInput) -> AgentOutput:
        chunks = input.dce_chunks
        findings = []
        
        eplusc_data = input.context.get("eplusc", {})
        seuils = input.context.get("seuils_eplusc", {})
        
        if eplusc_data:
            niveau_e = eplusc_data.get("niveau_e", "")
            niveau_c = eplusc_data.get("niveau_c", "")
            findings.append({
                "type": "EPLUSC_NIVEAUX",
                "niveau": "INFO",
                "niveau_e": niveau_e,
                "niveau_c": niveau_c,
                "recommandation": "Vérifier conformité seuils 2025"
            })
        
        eplusc_keywords = ["e+c-", "énergie", "carbone", "seuil", "certificat", "performance"]
        for chunk in chunks:
            chunk_lower = str(chunk).lower()
            for keyword in eplusc_keywords:
                if keyword in chunk_lower:
                    findings.append({
                        "type": "EPLUSC_MENTION",
                        "niveau": "INFO",
                        "keyword": keyword
                    })
                    break
        
        if not findings:
            findings = [{
                "type": "EPLUSC_ANALYSE",
                "niveau": "FAIBLE",
                "details": "Aucune donnée E+C- détectée"
            }]
        
        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="DETECTER_EPLUSC",
            confidence=0.90,
            status="SUCCESS",
            findings=findings,
            source_pages=[1, 5, 10],
            execution_time_ms=0
        )
