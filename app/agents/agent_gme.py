"""
SMART_AO V7 - agent_gme.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - GME Agent (Gestion des Means d'Oeuvre)
Source: ARCHITECTURE_V7_ENGINE.md §2 + ADR-044 + RAPPORT (1).md §7.4

Agent d'analyse des means d'oeuvre et main d'oeuvre
Évalue les coûts MO et leur optimisation
"""

from datetime import timedelta
from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.engines.agent_runtime.registry import registry
from app.engines.workflow_engine.mission import Mission


@registry.register(capabilities=["ANALYSER_MO", "CALCULER_COUT_MO", "OPTIMISER_MEANS_OEUVRE", "DETECTER_SOUS_EFFECTIF"])
class GMEAgent(BaseAgent):
    name = "GME Analyzer"
    capabilities = ["ANALYSER_MO", "CALCULER_COUT_MO", "OPTIMISER_MEANS_OEUVRE", "DETECTER_SOUS_EFFECTIF"]
    dependencies = ["PARSER", "CHIFFRAGE"]
    tags = ["technique", "main_oeuvre", "moyens"]
    estimated_duration = timedelta(seconds=6)
    is_blocking = False

    def can_handle(self, mission: Mission) -> float:
        has_dce = mission.has_document_type("DCE") or "dce" in str(mission.context).lower()
        has_gme = mission.context.get("means_oeuvre") is not None
        has_mo = mission.context.get("main_oeuvre") is not None
        
        if has_dce and (has_gme or has_mo):
            return 0.95
        if has_dce:
            return 0.60
        return 0.20

    async def execute(self, input: AgentInput) -> AgentOutput:
        chunks = input.dce_chunks
        findings = []
        financial_data = {}
        
        cout_mo_heure = input.context.get("cout_mo_heure", 0)
        heures_prevues = input.context.get("heures_prevues", 0)
        heures_reelles = input.context.get("heures_reelles", 0)
        effectif = input.context.get("effectif", {})
        
        # Stocker données financières
        if cout_mo_heure > 0 and heures_prevues > 0:
            cout_total = cout_mo_heure * heures_prevues
            financial_data["cout_mo"] = {
                "cout_heure": cout_mo_heure,
                "heures_prevues": heures_prevues,
                "cout_total": cout_total
            }
        
        # Analyse sous-effectif
        if effectif and heures_reelles > 0:
            for poste, data in effectif.items():
                prevu = data.get("prevus", 0)
                reel = data.get("reels", 0)
                if reel < prevu * 0.8:  # -20%
                    findings.append({
                        "type": "SOUS_EFFECTIF",
                        "niveau": "CRITIQUE",
                        "poste": poste,
                        "prevus": prevu,
                        "reels": reel,
                        "ecart": f"-{((prevu - reel) / prevu * 100):.1f}%",
                        "recommandation": "Recruter ou sous-traiter en urgence"
                    })
                elif reel < prevu * 0.9:  # -10%
                    findings.append({
                        "type": "EFFECTIF_INSUFFISANT",
                        "niveau": "ELEVE",
                        "poste": poste,
                        "prevus": prevu,
                        "reels": reel,
                        "ecart": f"-{((prevu - reel) / prevu * 100):.1f}%",
                        "recommandation": "Planning à ajuster"
                    })
        
        # Analyse coût MO (qualitatif UNIQUEMENT)
        if cout_mo_heure > 0 and heures_prevues > 0:
            findings.append({
                "type": "COUT_MO_CALCULE",
                "niveau": "INFO",
                "details": f"Coût MO calculé sur {heures_prevues} heures (voir financial_data)",
                "recommandation": "Comparer avec marché"
            })
        
        # Détection de mots-clés MO/GME
        mo_keywords = ["main d'oeuvre", "means d'oeuvre", "heures", "opérateurs", "compagnons"]
        for chunk in chunks:
            chunk_lower = str(chunk).lower()
            for keyword in mo_keywords:
                if keyword in chunk_lower:
                    findings.append({
                        "type": "MO_MENTION",
                        "niveau": "INFO",
                        "keyword": keyword,
                        "recommandation": "Vérifier détail des effectifs"
                    })
                    break
        
        if not findings:
            findings = [{
                "type": "MO_ANALYSEE",
                "niveau": "FAIBLE",
                "details": "Aucune anomalie MO/GME détectée"
            }]
        
        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="ANALYSER_MO",
            confidence=0.88,
            status="SUCCESS",
            findings=findings,
            financial_data=financial_data if financial_data else None,
            source_pages=[10, 18, 22],
            execution_time_ms=0
        )
