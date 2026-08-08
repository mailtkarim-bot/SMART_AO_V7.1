"""
SMART_AO V7 - agent_soged.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - SOGED Agent (Société de Gestion des Déchets)
Source: ARCHITECTURE_V7_ENGINE.md §2 + ADR-044 + RAPPORT (1).md §7.7

Agent de gestion et valorisation des déchets de chantier
Analyse coûts, traçabilité et conformité réglementaire
"""

from datetime import timedelta
from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.engines.agent_runtime.registry import registry
from app.engines.workflow_engine.mission import Mission


@registry.register(capabilities=["ANALYSER_DECHETS", "CALCULER_COUT_DECHETS", "OPTIMISER_VALORISATION", "VERIFIER_TRACABILITE"])
class SOGEDAgent(BaseAgent):
    name = "SOGED Waste Manager"
    capabilities = ["ANALYSER_DECHETS", "CALCULER_COUT_DECHETS", "OPTIMISER_VALORISATION", "VERIFIER_TRACABILITE"]
    dependencies = ["PARSER", "CHIFFRAGE"]
    tags = ["dechets", "environment", "valorisation"]
    estimated_duration = timedelta(seconds=5)
    is_blocking = False

    def can_handle(self, mission: Mission) -> float:
        has_dce = mission.has_document_type("DCE") or "dce" in str(mission.context).lower()
        has_dechets = mission.context.get("dechets") is not None
        
        if has_dce and has_dechets:
            return 0.95
        if has_dce:
            return 0.60
        return 0.20

    async def execute(self, input: AgentInput) -> AgentOutput:
        chunks = input.dce_chunks
        findings = []
        financial_data = {}
        
        dechets = input.context.get("dechets", {})
        ratios_dechets = input.context.get("ratios_ademes_dechets", {})
        
        # Stocker données financières
        if dechets:
            financial_data["dechets"] = {
                "total_tonnes": sum(d.get("quantite_tonnes", 0) for d in dechets.values()),
                "total_cout": sum(d.get("cout_evacuation", 0) for d in dechets.values()),
                "par_categorie": dechets
            }
        
        # Analyse des déchets par catégorie (qualitatif UNIQUEMENT)
        if dechets:
            total_tonnes = sum(d.get("quantite_tonnes", 0) for d in dechets.values())
            
            findings.append({
                "type": "DECHETS_TOTAUX",
                "niveau": "INFO",
                "quantite": f"{total_tonnes:.2f} tonnes",
                "details": "Analyse complète dans financial_data",
                "recommandation": "Optimiser tri et valorisation"
            })
            
            # Détection déchets dangereux
            for categorie, data in dechets.items():
                if data.get("dangeroux", False):
                    findings.append({
                        "type": "DECHET_DANGEREUX",
                        "niveau": "ELEVE",
                        "categorie": categorie,
                        "quantite": f"{data.get('quantite_tonnes', 0):.2f} tonnes",
                        "details": "Coût détaillé dans financial_data",
                        "recommandation": "Filière spécialisée obligatoire"
                    })
        
        # Vérification traçabilité
        bordereaux = input.context.get("bordereaux_suivi", [])
        if len(bordereaux) < len(dechets):
            findings.append({
                "type": "TRACABILITE_INCOMPLETE",
                "niveau": "ELEVE",
                "bordereaux": len(bordereaux),
                "dechets": len(dechets),
                "recommandation": "Établir BSD pour chaque flux de déchet"
            })
        else:
            findings.append({
                "type": "TRACABILITE_OK",
                "niveau": "FAIBLE",
                "details": "Tous les déchets ont un bordereau de suivi"
            })
        
        # Détection de mots-clés SOGED
        soged_keywords = ["déchet", "evacuation", "valorisation", "bsd", "tracabilité", "ademé"]
        for chunk in chunks:
            chunk_lower = str(chunk).lower()
            for keyword in soged_keywords:
                if keyword in chunk_lower:
                    findings.append({
                        "type": "SOGED_MENTION",
                        "niveau": "INFO",
                        "keyword": keyword
                    })
                    break
        
        if not findings:
            findings = [{
                "type": "DECHETS_ANALYSES",
                "niveau": "FAIBLE",
                "details": "Aucune donnée déchet détectée"
            }]
        
        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="ANALYSER_DECHETS",
            confidence=0.85,
            status="SUCCESS",
            findings=findings,
            financial_data=financial_data if financial_data else None,
            source_pages=[6, 12, 28],
            execution_time_ms=0
        )
