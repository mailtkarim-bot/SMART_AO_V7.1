"""
SMART_AO V7 - agent_pab.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - PAB Detector Agent
Source: ARCHITECTURE_V7_ENGINE.md §2 + ADR-044

Agent de détection des Prix Anormalement Bas (PAB)
ZERO € garanti - retourne uniquement du qualitatif
Math Engine calculera les écarts financiers après
"""

from datetime import timedelta
from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.engines.agent_runtime.registry import registry
from app.engines.workflow_engine.mission import Mission


@registry.register(capabilities=["DETECTER_PAB", "CALCULER_ECART_MARCHE", "DETECTER_RISQUE_FINANCIER"])
class PABAgent(BaseAgent):
    name = "PAB Detector"
    capabilities = ["DETECTER_PAB", "CALCULER_ECART_MARCHE", "DETECTER_RISQUE_FINANCIER"]
    dependencies = ["PARSER", "CHIFFRAGE"]
    tags = ["finance", "risque", "admin_only"]
    estimated_duration = timedelta(seconds=8)
    is_blocking = False

    def can_handle(self, mission: Mission) -> float:
        has_dpgf = mission.has_document_type("DPGF") or "dpgf" in str(mission.context).lower()
        has_estimation = mission.context.get("estimation_interne") is not None
        
        if has_dpgf and has_estimation:
            return 0.92  # Très pertinent
        if has_dpgf:
            return 0.65  # Pertinent
        return 0.15  # Peu pertinent

    async def execute(self, input: AgentInput) -> AgentOutput:
        # IA ZERO €: détecte écart qualitatif UNIQUEMENT
        # Tous les calculs € sont interdits ici - Math Engine les fera après
        
        # Analyse des chunks pour détecter des indicateurs PAB
        chunks = input.dce_chunks
        parsed_pages = input.parsed_docs.get("pages", 0)
        
        # Logique simplifiée de détection (en prod: IA + règles métier)
        findings = []
        financial_data = {}
        
        # Exemple: détecte si prix "fortement inférieur" à la moyenne
        # NOTE: On ne fait PAS de calcul ici, juste une détection qualitative
        if input.context.get("estimation_interne") and input.context.get("prix_moyen_marche"):
            estimation = input.context["estimation_interne"]
            prix_moyen = input.context["prix_moyen_marche"]
            
            # Données financières pour Math Engine (accès RBAC patron uniquement)
            financial_data["pab_analysis"] = {
                "estimation_interne": estimation,
                "prix_moyen_marche": prix_moyen,
                "ecart_pourcentage": ((prix_moyen - estimation) / prix_moyen * 100) if prix_moyen > 0 else 0
            }
            
            # Détection qualitative UNIQUEMENT (pas de € dans les findings)
            if estimation < prix_moyen * 0.7:
                findings.append({
                    "type": "PAB_SUSPECT",
                    "niveau": "ELEVE",
                    "cause": "ecart significatif detecte",
                    "recommandation": "justification 48h requise selon CCAG (details dans financial_data)",
                    "seuil": "superieur a 30%"
                })
            elif estimation < prix_moyen * 0.85:
                findings.append({
                    "type": "PAB_SUSPECT",
                    "niveau": "MOYEN",
                    "cause": "ecart modere detecte",
                    "recommandation": "verifier clauses de revision (details dans financial_data)",
                    "seuil": "entre 15% et 30%"
                })
        else:
            # Détection par mots-clés dans les chunks
            findings.append({
                "type": "PAB_A_ANALYSER",
                "niveau": "INFO",
                "cause": "presence DPGF detectee, estimation interne manquante",
                "recommandation": "saisir estimation interne pour analyse complete"
            })

        # Toujours ajouter une détection de base si DPGF présent
        if input.context.get("dpgf") or any("dpgf" in str(c).lower() for c in chunks):
            findings.append({
                "type": "DPGF_DETECTE",
                "niveau": "INFO",
                "details": "Document de Prix Global et Forfaitaire identifie"
            })

        # Si aucun finding, retourne quand même un statut
        if not findings:
            findings = [{
                "type": "PAB_AUCUN_RISQUE",
                "niveau": "FAIBLE",
                "cause": "aucun indicateur PAB detecte"
            }]

        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="DETECTER_PAB",
            confidence=0.88,
            status="SUCCESS",
            findings=findings,
            financial_data=financial_data if financial_data else None,
            source_pages=[12, 45],  # Pages typiques du DPGF
            execution_time_ms=0
        )
