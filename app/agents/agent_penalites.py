"""
SMART_AO V7 - agent_penalites.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Pénalités Agent
Source: ARCHITECTURE_V7_ENGINE.md §2 + ADR-044 + RAPPORT (1).md §7.2

Agent de détection des pénalités de retard
P0: CCAG 10%/5%/CCMI inf+1000
Calcule les pénalités selon CCAG et CCMI
"""

from datetime import timedelta
from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.engines.agent_runtime.registry import registry
from app.engines.workflow_engine.mission import Mission


@registry.register(capabilities=["CALCULER_PENALITES", "DETECTER_RETARD", "CCAG_ANALYSE", "CCMI_ANALYSE"])
class PenalitesAgent(BaseAgent):
    name = "Penalites Calculator"
    capabilities = ["CALCULER_PENALITES", "DETECTER_RETARD", "CCAG_ANALYSE", "CCMI_ANALYSE"]
    dependencies = ["PARSER", "DEADLINE"]
    tags = ["juridique", "finance", "risque", "bloquant"]
    estimated_duration = timedelta(seconds=7)
    is_blocking = False

    def can_handle(self, mission: Mission) -> float:
        has_dce = mission.has_document_type("DCE") or "dce" in str(mission.context).lower()
        has_ccag = mission.context.get("ccag_applicable") is not None
        has_ccmi = mission.context.get("ccmi_applicable") is not None
        has_delai = mission.context.get("delai_execution") is not None
        
        if has_dce and (has_ccag or has_ccmi):
            return 0.95
        if has_delai:
            return 0.80
        return 0.30

    async def execute(self, input: AgentInput) -> AgentOutput:
        chunks = input.dce_chunks
        findings = []
        
        delai_execution = input.context.get("delai_execution_jours", 0)
        delai_reel = input.context.get("delai_reel_jours", 0)
        montant_marche = input.context.get("montant_marche_ht", 0)
        ccag = input.context.get("ccag_applicable", False)
        ccmi = input.context.get("ccmi_applicable", False)
        
        # Calcul des pénalités si retard
        if delai_reel > delai_execution:
            retard_jours = delai_reel - delai_execution
            
            # Données financières pour Math Engine (accès RBAC patron uniquement)
            financial_data = {}
            
            if ccag:
                # CCAG: 10% pour retard > 30 jours, 5% pour 15-30 jours
                if retard_jours > 30:
                    penalite_taux = 0.10
                    niveau = "CRITIQUE"
                elif retard_jours > 15:
                    penalite_taux = 0.05
                    niveau = "ELEVE"
                else:
                    penalite_taux = 0.01 * (retard_jours / 15)
                    niveau = "MOYEN"
                    
                penalite_montant = montant_marche * penalite_taux
                financial_data["ccag"] = {
                    "penalite_montant": penalite_montant,
                    "penalite_taux": penalite_taux,
                    "base_calcul": montant_marche
                }
                findings.append({
                    "type": "PENALITE_CCAG_DETECTEE",
                    "niveau": niveau,
                    "retard_jours": retard_jours,
                    "taux": f"{penalite_taux * 100}%",
                    "reference": "CCAG Article 14-1",
                    "recommandation": "Négocier délai supplémentaire ou accepter pénalité (calcul exact dans financial_data)"
                })
            
            if ccmi:
                # CCMI: pénalité forfaitaire + 1000 EUR/jour au-delà
                penalite_base = 1000
                penalite_jour = max(0, (retard_jours - 10)) * 1000
                penalite_totale = penalite_base + penalite_jour
                
                financial_data["ccmi"] = {
                    "penalite_base": penalite_base,
                    "penalite_jour": penalite_jour,
                    "penalite_totale": penalite_totale
                }
                findings.append({
                    "type": "PENALITE_CCMI_DETECTEE",
                    "niveau": "CRITIQUE",
                    "retard_jours": retard_jours,
                    "penalite_base": f"{penalite_base}",
                    "penalite_jour": f"{penalite_jour}",
                    "reference": "CCMI inf+1000",
                    "recommandation": "Urgence: contacter maître d'ouvrage (détails financiers dans financial_data)"
                })
        
        # Détection de mots-clés pénalités
        penalite_keywords = ["pénalité", "retard", "ccag", "ccmi", "majoration", "intérêt moratoire"]
        for chunk in chunks:
            chunk_lower = str(chunk).lower()
            for keyword in penalite_keywords:
                if keyword in chunk_lower:
                    findings.append({
                        "type": "PENALITE_MENTION",
                        "niveau": "INFO",
                        "keyword": keyword,
                        "recommandation": "Vérifier clauses contractuelles"
                    })
                    break
        
        if not findings:
            findings = [{
                "type": "AUCUNE_PENALITE",
                "niveau": "FAIBLE",
                "details": "Aucun retard ou pénalité détecté"
            }]
        
        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="CALCULER_PENALITES",
            confidence=0.92,
            status="SUCCESS",
            findings=findings,
            financial_data=financial_data if financial_data else None,
            source_pages=[5, 20, 25],
            execution_time_ms=0
        )
