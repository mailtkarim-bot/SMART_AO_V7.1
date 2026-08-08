"""
SMART_AO V7 - agent_tresorerie.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Trésorerie Agent
Source: ARCHITECTURE_V7_ENGINE.md §2 + ADR-044 + RAPPORT (1).md §7.3

Agent de suivi de trésorerie et avance P0
P0: avance 2024 30%/10% + BFR S-curve
Gère les flux financiers du chantier
"""

from datetime import timedelta
from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.engines.agent_runtime.registry import registry
from app.engines.workflow_engine.mission import Mission


@registry.register(capabilities=["CALCULER_AVANCE", "SUIVRE_TRESORERIE", "GENERER_BFR_CURVE", "ANALYSER_FLUX_FINANCIERS"])
class TresorerieAgent(BaseAgent):
    name = "Tresorerie Guardian"
    capabilities = ["CALCULER_AVANCE", "SUIVRE_TRESORERIE", "GENERER_BFR_CURVE", "ANALYSER_FLUX_FINANCIERS"]
    dependencies = ["PARSER", "CHIFFRAGE"]
    tags = ["finance", "tresorerie", "bfr"]
    estimated_duration = timedelta(seconds=8)
    is_blocking = False

    def can_handle(self, mission: Mission) -> float:
        has_dce = mission.has_document_type("DCE") or "dce" in str(mission.context).lower()
        has_financial = mission.context.get("montant_marche") is not None
        has_planning = mission.context.get("planning") is not None
        
        if has_dce and has_financial and has_planning:
            return 0.98
        if has_financial:
            return 0.75
        return 0.25

    async def execute(self, input: AgentInput) -> AgentOutput:
        chunks = input.dce_chunks
        findings = []
        financial_data = {}
        
        montant_marche = input.context.get("montant_marche_ht", 0)
        avance_pourcentage = input.context.get("avance_pourcentage", 30)  # P0 2024: 30%
        duree_mois = input.context.get("duree_mois", 12)
        bfr_mois = input.context.get("bfr_mois", {})
        
        # Calcul avance - données financières pour Math Engine
        if montant_marche > 0 and avance_pourcentage > 0:
            avance_montant = montant_marche * (avance_pourcentage / 100)
            financial_data["avance"] = {
                "montant": avance_montant,
                "pourcentage": avance_pourcentage,
                "base_calcul": montant_marche
            }
            findings.append({
                "type": "AVANCE_CALCULEE",
                "niveau": "INFO",
                "pourcentage": f"{avance_pourcentage}%",
                "reference": "P0 2024",
                "recommandation": "Vérifier conditions de versement (montant exact dans financial_data)"
            })
        
        # Analyse BFR S-curve - données financières pour Math Engine
        if bfr_mois:
            total_bfr = sum(bfr_mois.values())
            bfr_ratio = (total_bfr / montant_marche * 100) if montant_marche > 0 else 0
            financial_data["bfr"] = {
                "total": total_bfr,
                "par_mois": bfr_mois,
                "ratio_pourcent": bfr_ratio
            }
            
            if total_bfr > montant_marche * 0.15:  # BFR > 15% du marché
                findings.append({
                    "type": "BFR_ELEVE",
                    "niveau": "CRITIQUE",
                    "ratio": f"{bfr_ratio:.1f}% du marché",
                    "recommandation": "Optimiser trésorerie ou demander avance complémentaire (détails dans financial_data)"
                })
            elif total_bfr > montant_marche * 0.10:
                findings.append({
                    "type": "BFR_MOYEN",
                    "niveau": "ELEVE",
                    "ratio": f"{bfr_ratio:.1f}% du marché",
                    "recommandation": "Surveiller flux de trésorerie (détails dans financial_data)"
                })
            else:
                findings.append({
                    "type": "BFR_NORME",
                    "niveau": "FAIBLE",
                    "ratio": f"{bfr_ratio:.1f}% du marché",
                    "details": "Besoin en fonds de roulement conforme aux attentes"
                })
        
        # Détection mots-clés trésorerie
        tresorerie_keywords = ["avance", "acompte", "situation", "paiement", "bfr", "trésorerie"]
        for chunk in chunks:
            chunk_lower = str(chunk).lower()
            for keyword in tresorerie_keywords:
                if keyword in chunk_lower:
                    findings.append({
                        "type": "TRESORERIE_MENTION",
                        "niveau": "INFO",
                        "keyword": keyword,
                        "recommandation": "Vérifier modalités de paiement"
                    })
                    break
        
        if not findings:
            findings = [{
                "type": "TRESORERIE_OK",
                "niveau": "FAIBLE",
                "details": "Aucun problème de trésorerie détecté"
            }]
        
        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="CALCULER_AVANCE",
            confidence=0.94,
            status="SUCCESS",
            findings=findings,
            financial_data=financial_data if financial_data else None,
            source_pages=[8, 15, 30],
            execution_time_ms=0
        )
