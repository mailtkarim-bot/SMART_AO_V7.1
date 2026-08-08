"""
SMART_AO V7.1 - agent_vigilance_urssaf.py
==========================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 07/08/2026
Build: 9.5 - Phase: 5
"""


"""
SMART_AO V7.1 - Vigilance URSSAF Agent
Source: ARCHITECTURE_V7_ENGINE.md §2 + ADR-044 + RAPPORT (1).md §7.30

Agent de vérification des attestations URSSAF des sous-traitants.
Détecte les risques de solidarité et bloque le DC4 en cas d'attestation
expirée ou de sous-traitant en difficulté juridique.

ZERO € garanti:
- Les findings sont strictement qualitatifs (statut, motif, recommandation).
- Tout montant ou calcul financier est confiné dans financial_data.
"""

from datetime import timedelta
from typing import Any, Dict, List

from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.engines.agent_runtime.registry import registry
from app.engines.math_engine.vigilance_solver import get_vigilance_solver
from app.engines.workflow_engine.mission import Mission


@registry.register(capabilities=["VERIFIER_URSSAF", "BLOQUER_DC4"])
class VigilanceUrssafAgent(BaseAgent):
    name = "Vigilance URSSAF"
    capabilities = ["VERIFIER_URSSAF", "BLOQUER_DC4"]
    dependencies = ["PARSER"]
    tags = ["juridique", "bloquant"]
    estimated_duration = timedelta(seconds=6)
    is_blocking = True

    def can_handle(self, mission: Mission) -> float:
        """
        Score de pertinence 0.0-1.0 basé sur le contexte de la mission.
        """
        ctx = mission.context if hasattr(mission, "context") else {}
        has_sous_traitants = bool(ctx.get("sous_traitants")) or "sous-traitant" in str(ctx).lower()
        has_dc4 = mission.has_document_type("DC4") if hasattr(mission, "has_document_type") else "dc4" in str(ctx).lower()
        has_urssaf_mention = "urssaf" in str(ctx).lower() or "attestation" in str(ctx).lower()

        if has_sous_traitants and has_dc4:
            return 1.0
        if has_sous_traitants and has_urssaf_mention:
            return 0.92
        if has_sous_traitants:
            return 0.75
        if has_urssaf_mention:
            return 0.45
        return 0.10

    async def execute(self, input: AgentInput) -> AgentOutput:
        """
        Vérifie les attestations URSSAF des sous-traitants et calcule
        l'exposition solidaire via VigilanceSolver.

        Les résultats chiffrés sont isolés dans financial_data.
        Les findings restent qualitatifs (ZERO €).
        """
        solver = get_vigilance_solver()
        findings: List[Dict[str, Any]] = []
        financial_data: Dict[str, Any] = {"sous_traitants": []}
        source_pages: List[int] = []
        global_blocage = False
        global_confidence = 0.85

        # Récupération de la liste des sous-traitants depuis le contexte enrichi
        sous_traitants = input.context.get("sous_traitants", [])
        if not sous_traitants and input.context.get("sous_traitant"):
            sous_traitants = [input.context.get("sous_traitant")]

        # Fallback: recherche dans parsed_docs si le contexte n'a pas structuré les sous-traitants
        if not sous_traitants and isinstance(input.parsed_docs, dict):
            parsed_sous_traitants = input.parsed_docs.get("sous_traitants", [])
            if parsed_sous_traitants:
                sous_traitants = parsed_sous_traitants

        if not sous_traitants:
            findings.append({
                "type": "URSSAF_AUCUN_SOUS_TRAITANT",
                "niveau": "INFO",
                "details": "Aucun sous-traitant déclaré dans le contexte mission",
                "recommandation": "Vérifier le DC4 et les actes de sous-traitance si applicable"
            })
            global_confidence = 0.60

        for idx, st in enumerate(sous_traitants):
            if isinstance(st, dict):
                nom = st.get("nom", st.get("raison_sociale", f"Sous-traitant {idx + 1}"))
                date_attestation = st.get("date_attestation_urssaf") or st.get("date_attestation")
                montant_sous_traite = float(st.get("montant_sous_traite", 0) or 0)
                statut_juridique = st.get("statut_juridique", "actif")
                page = st.get("page", 0)
            else:
                nom = str(st)
                date_attestation = None
                montant_sous_traite = 0.0
                statut_juridique = "actif"
                page = 0

            if page and page not in source_pages:
                source_pages.append(page)

            result = solver.calculer(
                date_attestation=date_attestation,
                montant_sous_traite=montant_sous_traite,
                statut_juridique=statut_juridique,
            )

            result_dict = result.to_dict()
            financial_data["sous_traitants"].append({
                "nom": nom,
                "date_attestation": date_attestation,
                "montant_sous_traite": montant_sous_traite,
                "statut_juridique": statut_juridique,
                "resultat": result_dict,
            })

            if result.blocage_depot:
                global_blocage = True
                findings.append({
                    "type": "URSSAF_BLOCAGE_DC4",
                    "niveau": "CRITIQUE",
                    "sous_traitant": nom,
                    "motif": result.motif_blocage,
                    "statut_juridique": statut_juridique,
                    "recommandation": "Obtenir une attestation URSSAF valide ou substituer le sous-traitant avant dépôt"
                })
            else:
                findings.append({
                    "type": "URSSAF_ATTESTATION_VALIDE",
                    "niveau": "FAIBLE",
                    "sous_traitant": nom,
                    "motif": result.motif_blocage,
                    "recommandation": "Attestation conforme — conserver la trace dans le dossier"
                })

        financial_data["blocage_depot"] = global_blocage
        financial_data["capability"] = "VERIFIER_URSSAF"

        if not findings:
            findings.append({
                "type": "URSSAF_AUCUN_RISQUE",
                "niveau": "FAIBLE",
                "details": "Aucun risque URSSAF détecté",
                "recommandation": "Pas d'action requise"
            })

        if not source_pages:
            source_pages = [1]

        status = "SUCCESS"
        if global_blocage:
            status = "PARTIAL"

        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="VERIFIER_URSSAF",
            confidence=global_confidence,
            status=status,
            findings=findings,
            financial_data=financial_data,
            source_pages=source_pages,
            execution_time_ms=0,
        )
