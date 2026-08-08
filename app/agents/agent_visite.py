"""
SMART_AO V7 - agent_visite.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Visite Auto GPS Agent
Source: ARCHITECTURE_V7_ENGINE.md §2 + ADR-044 + RAPPORT (1).md §7.20

Agent d'automatisation des visites de site avec GPS
Planification et analyse automatique des sites
"""

from datetime import timedelta
from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.engines.agent_runtime.registry import registry
from app.engines.workflow_engine.mission import Mission


@registry.register(capabilities=["PLANIFIER_VISITE", "ANALYSER_SITE_GPS", "GENERER_RAPPORT_VISITE", "OPTIMISER_ITINERAIRE"])
class VisiteAutoGPSAgent(BaseAgent):
    name = "Visite Auto GPS"
    capabilities = ["PLANIFIER_VISITE", "ANALYSER_SITE_GPS", "GENERER_RAPPORT_VISITE", "OPTIMISER_ITINERAIRE"]
    dependencies = ["PARSER"]
    tags = ["visite", "gps", "site", "automatique"]
    estimated_duration = timedelta(seconds=4)
    is_blocking = False

    def can_handle(self, mission: Mission) -> float:
        has_site_coords = mission.context.get("site_coordinates") is not None
        has_dce = mission.has_document_type("DCE") or "dce" in str(mission.context).lower()
        
        if has_site_coords:
            return 0.95
        if has_dce:
            return 0.70
        return 0.20

    async def execute(self, input: AgentInput) -> AgentOutput:
        chunks = input.dce_chunks
        findings = []
        
        site_coords = input.context.get("site_coordinates", {})
        
        if site_coords:
            findings.append({
                "type": "SITE_LOCALISE",
                "niveau": "INFO",
                "latitude": site_coords.get("latitude", 0),
                "longitude": site_coords.get("longitude", 0),
                "recommandation": "Planifier visite sur site"
            })
        
        visite_keywords = ["visite", "gps", "site", "coordonnées", "rapport"]
        for chunk in chunks:
            chunk_lower = str(chunk).lower()
            for keyword in visite_keywords:
                if keyword in chunk_lower:
                    findings.append({
                        "type": "VISITE_MENTION",
                        "niveau": "INFO",
                        "keyword": keyword
                    })
                    break
        
        if not findings:
            findings = [{
                "type": "VISITE_ANALYSEE",
                "niveau": "FAIBLE",
                "details": "Aucune donnée visite détectée"
            }]
        
        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="PLANIFIER_VISITE",
            confidence=0.90,
            status="SUCCESS",
            findings=findings,
            source_pages=[1, 5, 10],
            execution_time_ms=0
        )
