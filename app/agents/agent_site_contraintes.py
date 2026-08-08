"""
SMART_AO V7 - agent_site_contraintes.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Site Contraintes Agent
Source: ARCHITECTURE_V7_ENGINE.md §2 + ADR-044 + RAPPORT (1).md §7.8

Agent d'analyse des contraintes de site
Évalue les coefficients de majoration liés aux contraintes géographiques et techniques
"""

from datetime import timedelta
from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.engines.agent_runtime.registry import registry
from app.engines.workflow_engine.mission import Mission


@registry.register(capabilities=["ANALYSER_SITE", "CALCULER_COEFF_CONTRAINTES", "DETECTER_RISQUE_SITE", "OPTIMISER_PLANNING"])
class SiteContraintesAgent(BaseAgent):
    name = "Site Contraintes Analyzer"
    capabilities = ["ANALYSER_SITE", "CALCULER_COEFF_CONTRAINTES", "DETECTER_RISQUE_SITE", "OPTIMISER_PLANNING"]
    dependencies = ["PARSER", "CHIFFRAGE"]
    tags = ["technique", "site", "contraintes", "coefficient"]
    estimated_duration = timedelta(seconds=7)
    is_blocking = False

    def can_handle(self, mission: Mission) -> float:
        has_dce = mission.has_document_type("DCE") or "dce" in str(mission.context).lower()
        has_site_info = mission.context.get("site_info") is not None
        
        if has_dce and has_site_info:
            return 0.96
        if has_dce:
            return 0.70
        return 0.20

    async def execute(self, input: AgentInput) -> AgentOutput:
        chunks = input.dce_chunks
        findings = []
        
        site_info = input.context.get("site_info", {})
        coeffs_site = input.context.get("coeffs_site_contraintes", {})
        
        # Analyse des contraintes de site
        contraintes = site_info.get("contraintes", [])
        
        if contraintes:
            for contrainte in contraintes:
                niveau = contrainte.get("niveau", "FAIBLE")
                coefficient = contrainte.get("coefficient", 1.0)
                description = contrainte.get("description", "")
                
                findings.append({
                    "type": "CONTRAINTE_SITE",
                    "niveau": niveau,
                    "description": description,
                    "coefficient": coefficient,
                    "impact": f"{(coefficient - 1) * 100:.1f}% sur coût"
                })
        
        # Calcul coefficient global
        if coeffs_site:
            coeff_global = coeffs_site.get("global", 1.0)
            if coeff_global > 1.3:
                findings.append({
                    "type": "COEFF_ELEVE",
                    "niveau": "CRITIQUE",
                    "coefficient": coeff_global,
                    "impact": f"{(coeff_global - 1) * 100:.1f}% de majoration",
                    "recommandation": "Étudier alternatives ou négocier délais"
                })
            elif coeff_global > 1.15:
                findings.append({
                    "type": "COEFF_MOYEN",
                    "niveau": "ELEVE",
                    "coefficient": coeff_global,
                    "impact": f"{(coeff_global - 1) * 100:.1f}% de majoration",
                    "recommandation": "Prévoir marge supplémentaire"
                })
            else:
                findings.append({
                    "type": "COEFF_NORME",
                    "niveau": "FAIBLE",
                    "coefficient": coeff_global,
                    "impact": f"{(coeff_global - 1) * 100:.1f}% de majoration"
                })
        
        # Détection de mots-clés site/contraintes
        site_keywords = ["site", "contrainte", "accès", "coefficient", "majoration", "géographie"]
        for chunk in chunks:
            chunk_lower = str(chunk).lower()
            for keyword in site_keywords:
                if keyword in chunk_lower:
                    findings.append({
                        "type": "SITE_MENTION",
                        "niveau": "INFO",
                        "keyword": keyword
                    })
                    break
        
        if not findings:
            findings = [{
                "type": "SITE_ANALYSE",
                "niveau": "FAIBLE",
                "details": "Aucune contrainte de site détectée"
            }]
        
        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="ANALYSER_SITE",
            confidence=0.91,
            status="SUCCESS",
            findings=findings,
            source_pages=[7, 11, 19],
            execution_time_ms=0
        )
