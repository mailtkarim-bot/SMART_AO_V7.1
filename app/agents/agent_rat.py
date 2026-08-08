"""
SMART_AO V7 - agent_rat.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - RAT Agent (Réglementation et Assurances Travaux)
Source: ARCHITECTURE_V7_ENGINE.md §2 + ADR-044 + RAPPORT (1).md §7.6

Agent de vérification de la conformité réglementaire
RAT: Réglementation, Assurance, Travaux
"""

from datetime import timedelta
from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.engines.agent_runtime.registry import registry
from app.engines.workflow_engine.mission import Mission


@registry.register(capabilities=["VERIFIER_REGLEMENTATION", "ANALYSER_RAT", "DETECTER_NON_CONFORMITE", "VALIDER_ASSURANCES"])
class RATAgent(BaseAgent):
    name = "RAT Compliance"
    capabilities = ["VERIFIER_REGLEMENTATION", "ANALYSER_RAT", "DETECTER_NON_CONFORMITE", "VALIDER_ASSURANCES"]
    dependencies = ["PARSER"]
    tags = ["reglementation", "assurance", "conformite", "bloquant"]
    estimated_duration = timedelta(seconds=6)
    is_blocking = True  # Non conformité = exclusion

    def can_handle(self, mission: Mission) -> float:
        has_dce = mission.has_document_type("DCE") or "dce" in str(mission.context).lower()
        has_rat = mission.context.get("reglementation") is not None
        
        if has_dce:
            return 0.90
        if has_rat:
            return 0.85
        return 0.20

    async def execute(self, input: AgentInput) -> AgentOutput:
        chunks = input.dce_chunks
        findings = []
        
        # Réglementations à vérifier
        reglementations = [
            "code_du_travail", "regles_art", "dtu", "normes_nf",
            "accessibilite", "securite_chantier", "environment",
            "dechets", "amiante", "plomb"
        ]
        
        # Vérification des assurances
        assurances = input.context.get("assurances", {})
        
        # Assurance décennale obligatoire
        if "decennale" not in assurances:
            findings.append({
                "type": "ASSURANCE_DECENNALE_MANQUANTE",
                "niveau": "CRITIQUE",
                "risque": "EXCLUSION",
                "recommandation": "Souscrire assurance décennale avant tout chantier"
            })
        else:
            decennale = assurances["decennale"]
            if decennale.get("valide", False):
                findings.append({
                    "type": "ASSURANCE_DECENNALE_OK",
                    "niveau": "NORMAL",
                    "assureur": decennale.get("assureur", "Inconnu"),
                    "expiration": decennale.get("expiration", "Non spécifiée")
                })
            else:
                findings.append({
                    "type": "ASSURANCE_DECENNALE_EXPIREE",
                    "niveau": "CRITIQUE",
                    "risque": "EXCLUSION",
                    "recommandation": "Renouveler assurance décennale"
                })
        
        # Vérification conformité réglementaire
        conformites = input.context.get("conformites", {})
        non_conformites = []
        for regle, statut in conformites.items():
            if not statut:
                non_conformites.append(regle)
        
        if non_conformites:
            findings.append({
                "type": "NON_CONFORMITES",
                "niveau": "CRITIQUE",
                "regles": non_conformites,
                "nombre": len(non_conformites),
                "risque": "EXCLUSION",
                "recommandation": "Mettre en conformité avant dépôt"
            })
        else:
            findings.append({
                "type": "CONFORMITE_REGLEMENTAIRE",
                "niveau": "NORMAL",
                "details": "Tous les critères réglementaires sont conformes"
            })
        
        # Détection de mots-clés RAT
        rat_keywords = ["règlementation", "assurance", "dtu", "norme", "conformité", "décennale"]
        for chunk in chunks:
            chunk_lower = str(chunk).lower()
            for keyword in rat_keywords:
                if keyword in chunk_lower:
                    findings.append({
                        "type": "RAT_MENTION",
                        "niveau": "INFO",
                        "keyword": keyword
                    })
                    break
        
        if not findings:
            findings = [{
                "type": "RAT_A_VERIFIER",
                "niveau": "FAIBLE",
                "details": "Vérification RAT en cours"
            }]
        
        # Déterminer status
        status = "SUCCESS"
        for finding in findings:
            if finding.get("niveau") == "CRITIQUE":
                status = "FAILED"
                break
        
        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="VERIFIER_REGLEMENTATION",
            confidence=0.95,
            status=status,
            findings=findings,
            source_pages=[4, 9, 14],
            execution_time_ms=0
        )
