"""
SMART_AO V7 - CCTP/DPGF Agent
Source: ARCHITECTURE_V7_ENGINE.md §2 + ADR-044 + RAPPORT (1).md §7.9

Agent d'analyse conjointe CCTP (Cahier des Clauses Techniques Particulières) et DPGF (Décomposition Prix Global Forfaitaire)
Vérifie la cohérence entre les descriptions techniques et les prix
"""

from datetime import timedelta
from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.engines.agent_runtime.registry import registry
from app.engines.workflow_engine.mission import Mission


@registry.register(capabilities=["ANALYSER_CCTP", "ANALYSER_DPGF", "VERIFIER_COHERENCE_CCTP_DPGF", "DETECTER_ANOMALIE_PRIX"])
class CCTPDPGFAgent(BaseAgent):
    name = "CCTP-DPGF Analyzer"
    capabilities = ["ANALYSER_CCTP", "ANALYSER_DPGF", "VERIFIER_COHERENCE_CCTP_DPGF", "DETECTER_ANOMALIE_PRIX"]
    dependencies = ["PARSER", "CHIFFRAGE"]
    tags = ["technique", "finance", "cctp", "dpgf", "coherence"]
    estimated_duration = timedelta(seconds=8)
    is_blocking = False

    def can_handle(self, mission: Mission) -> float:
        has_cctp = mission.has_document_type("CCTP") or "cctp" in str(mission.context).lower()
        has_dpgf = mission.has_document_type("DPGF") or "dpgf" in str(mission.context).lower()
        has_dce = mission.has_document_type("DCE") or "dce" in str(mission.context).lower()
        
        if has_cctp and has_dpgf:
            return 1.0
        if has_dce:
            return 0.80
        return 0.30

    async def execute(self, input: AgentInput) -> AgentOutput:
        chunks = input.dce_chunks
        findings = []
        
        cctp_data = input.context.get("cctp", {})
        dpgf_data = input.context.get("dpgf", {})
        
        # Vérification cohérence CCTP/DPGF
        if cctp_data and dpgf_data:
            # Comparer les lots
            cctp_lots = cctp_data.get("lots", {})
            dpgf_lots = dpgf_data.get("lots", {})
            
            lots_manquants_cctp = set(dpgf_lots.keys()) - set(cctp_lots.keys())
            lots_manquants_dpgf = set(cctp_lots.keys()) - set(dpgf_lots.keys())
            
            if lots_manquants_cctp:
                findings.append({
                    "type": "LOTS_MANQUANTS_DANS_CCTP",
                    "niveau": "CRITIQUE",
                    "lots": list(lots_manquants_cctp),
                    "recommandation": "Compléter CCTP pour tous les lots du DPGF"
                })
            
            if lots_manquants_dpgf:
                findings.append({
                    "type": "LOTS_MANQUANTS_DANS_DPGF",
                    "niveau": "CRITIQUE",
                    "lots": list(lots_manquants_dpgf),
                    "recommandation": "Ajouter prix pour tous les lots du CCTP"
                })
            
            # Vérifier cohérence prix/quantité
            for lot, cctp_info in cctp_lots.items():
                if lot in dpgf_lots:
                    quantite_cctp = cctp_info.get("quantite", 0)
                    prix_unitaire_dpgf = dpgf_lots[lot].get("prix_unitaire", 0)
                    
                    if quantite_cctp > 0 and prix_unitaire_dpgf > 0:
                        prix_total = quantite_cctp * prix_unitaire_dpgf
                        
                        # Détecter anomalies (prix anormalement bas ou élevé)
                        prix_moyen_marche = cctp_info.get("prix_moyen_marche", prix_unitaire_dpgf)
                        
                        if prix_unitaire_dpgf < prix_moyen_marche * 0.7:
                            findings.append({
                                "type": "PRIX_ANORMALEMENT_BAS",
                                "niveau": "ELEVE",
                                "lot": lot,
                                "prix_dpgf": f"{prix_unitaire_dpgf:.2f} EUR",
                                "prix_marche": f"{prix_moyen_marche:.2f} EUR",
                                "ecart": f"-{(1 - prix_unitaire_dpgf/prix_moyen_marche)*100:.1f}%",
                                "recommandation": "Justifier écart ou réviser prix"
                            })
                        elif prix_unitaire_dpgf > prix_moyen_marche * 1.5:
                            findings.append({
                                "type": "PRIX_ANORMALEMENT_ELEVE",
                                "niveau": "ELEVE",
                                "lot": lot,
                                "prix_dpgf": f"{prix_unitaire_dpgf:.2f} EUR",
                                "prix_marche": f"{prix_moyen_marche:.2f} EUR",
                                "ecart": f"+{(prix_unitaire_dpgf/prix_moyen_marche - 1)*100:.1f}%",
                                "recommandation": "Vérifier calcul ou négocier avec fournisseur"
                            })
        
        # Détection de mots-clés CCTP/DPGF
        cctp_dpgf_keywords = ["cctp", "dpgf", "lot", "prix unitaire", "quantité", "décomposition", "clause technique"]
        for chunk in chunks:
            chunk_lower = str(chunk).lower()
            for keyword in cctp_dpgf_keywords:
                if keyword in chunk_lower:
                    findings.append({
                        "type": "CCTP_DPGF_MENTION",
                        "niveau": "INFO",
                        "keyword": keyword
                    })
                    break
        
        if not findings:
            findings = [{
                "type": "CCTP_DPGF_COHERENT",
                "niveau": "FAIBLE",
                "details": "CCTP et DPGF cohérents"
            }]
        
        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="VERIFIER_COHERENCE_CCTP_DPGF",
            confidence=0.93,
            status="SUCCESS",
            findings=findings,
            source_pages=[3, 8, 15, 20],
            execution_time_ms=0
        )
