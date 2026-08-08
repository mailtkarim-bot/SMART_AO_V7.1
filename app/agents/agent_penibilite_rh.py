"""
SMART_AO V7.1 - agent_penibilite_rh.py
=======================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 07/08/2026
Build: 9.5 - Phase: 5
"""

"""
SMART_AO V7.1 - Pénibilité RH Agent
Source: RAPPORT (1).md §7.29

Détecte les contraintes de pénibilité RH dans le CCTP, croise le Vault A04,
et calcule le surcoût intérim via PenibiliteSolver.

ZERO € garanti - findings strictement qualitatifs.
Les résultats chiffrés sont isolés dans financial_data pour le Math Engine.
"""

from datetime import timedelta
from typing import List

from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.engines.math_engine.penibilite_solver import PenibiliteSolver, get_penibilite_solver
from app.engines.workflow_engine.mission import Mission
from app.engines.agent_runtime.registry import registry


@registry.register(capabilities=["DETECTER_PENIBILITE_RH", "CALCULER_SURCOUT_INTERIM"])
class PenibiliteRHAgent(BaseAgent):
    name = "Penibilite RH Detector"
    capabilities = ["DETECTER_PENIBILITE_RH", "CALCULER_SURCOUT_INTERIM"]
    dependencies = ["PARSER", "VAULT_A04"]
    tags = ["rh", "risque"]
    estimated_duration = timedelta(seconds=10)
    is_blocking = False

    def __init__(self, solver: PenibiliteSolver = None):
        self.solver = solver or get_penibilite_solver()

    def can_handle(self, mission: Mission) -> float:
        """
        Score de pertinence 0.0-1.0 basé sur la présence de signaux
        de pénibilité RH dans la mission (CCTP, Vault A04).
        """
        text_context = str(mission.context).lower()
        text_docs = str(mission.documents).lower() if hasattr(mission, "documents") else ""

        keywords = [
            "penibilite",
            "interim",
            "manutention",
            "hauteur",
            "travail nocturne",
            "exposition",
            "substances",
            "vibrations",
            "bruit",
            "travail en equipe",
            "postes penibles",
            "renfort",
            "interimaire",
            "turnover",
            "absentéisme",
        ]

        keyword_hits = sum(1 for kw in keywords if kw in text_context or kw in text_docs)
        has_cctp = mission.has_document_type("CCTP") if hasattr(mission, "has_document_type") else "cctp" in text_docs
        has_a04 = "a04" in text_context or "rh" in text_context

        if has_cctp and has_a04 and keyword_hits >= 3:
            return 0.95
        if has_cctp and keyword_hits >= 2:
            return 0.78
        if has_a04 and keyword_hits >= 1:
            return 0.55
        if keyword_hits >= 1:
            return 0.30
        return 0.05

    async def execute(self, input: AgentInput) -> AgentOutput:
        """
        Détecte les contraintes de pénibilité RH et isole les calculs
        financiers dans financial_data (accès RBAC patron).
        """
        chunks = input.dce_chunks
        context = input.context or {}
        vault_a04 = context.get("vault_a04", context.get("A04", {})) or {}

        findings: List[dict] = []
        financial_data = {}
        source_pages = []

        # Mots-clés de pénibilité recherchés dans les chunks CCTP
        penibilite_keywords = [
            "penibilite", "penible", "postes penibles", "contraintes de pénibilité",
            "travail en hauteur", "manutention manuelle", "travail nocturne",
            "exposition aux agents chimiques", "vibrations", "bruit",
            "travail en equipe", "renfort interimaire", "turnover",
        ]

        detected_keywords = []
        for chunk in chunks:
            text = str(chunk.get("text", "")).lower()
            page = chunk.get("page", 0)
            for kw in penibilite_keywords:
                if kw in text and kw not in detected_keywords:
                    detected_keywords.append(kw)
                    if page and page not in source_pages:
                        source_pages.append(page)

        # Croisement avec Vault A04
        effectifs_prevus = vault_a04.get("effectifs_prevus", {})
        postes_critiques = vault_a04.get("postes_critiques", [])
        metier_cle = vault_a04.get("metier_cle", "manoeuvre")
        duree_semaines = vault_a04.get("duree_semaines", context.get("duree_semaines", 1))
        nb_manquants = vault_a04.get("nb_manquants", context.get("nb_manquants", 0))

        if detected_keywords:
            findings.append({
                "type": "PENIBILITE_DETECTEE",
                "niveau": "MOYEN" if len(detected_keywords) <= 3 else "ELEVE",
                "contraintes_detectees": detected_keywords,
                "cause": "presence de clauses ou exigences de penibilite dans le CCTP",
                "recommandation": "croiser avec plan de prevention et effectifs prevus (details dans financial_data)",
            })

        if postes_critiques:
            findings.append({
                "type": "POSTES_CRITIQUES_VAULT_A04",
                "niveau": "INFO",
                "postes": postes_critiques,
                "cause": "postes identifies comme critiques dans le Vault A04",
                "recommandation": "verifier l'adéquation entre postes critiques et taux d'interim",
            })

        # Calcul financier isolé dans financial_data (jamais dans findings)
        if nb_manquants > 0 and metier_cle and duree_semaines > 0:
            solver_result = self.solver.solve({
                "nb_manquants": nb_manquants,
                "metier": metier_cle,
                "duree_semaines": duree_semaines,
                "heures_par_semaine": vault_a04.get("heures_par_semaine", 35),
                "region": vault_a04.get("region", "default"),
                "contrainte": vault_a04.get("contrainte", "penibilite_standard"),
                "currency": vault_a04.get("currency", "EUR"),
            })

            financial_data["penibilite_rh"] = {
                "solver": solver_result.solver_name,
                "nb_manquants": nb_manquants,
                "metier": metier_cle,
                "duree_semaines": duree_semaines,
                "detail_calcul": solver_result.metadata.get("detail_calcul", {}),
                "output": {
                    "value": float(solver_result.output.value),
                    "currency": solver_result.output.currency,
                },
            }

            findings.append({
                "type": "SURCOUT_INTERIM_CALCULE",
                "niveau": "INFO",
                "cause": "manquants d'effectifs identifies sur postes penibles",
                "recommandation": "consulter financial_data pour le calcul detaille du surcout",
                "variables_utilisees": {
                    "nb_manquants": nb_manquants,
                    "metier": metier_cle,
                    "duree_semaines": duree_semaines,
                },
            })
        else:
            findings.append({
                "type": "PENIBILITE_A_ANALYSER",
                "niveau": "INFO",
                "cause": "donnees RH insuffisantes pour calculer le surcout intérim",
                "recommandation": "saisir nb_manquants, metier_cle et duree_semaines dans le Vault A04",
            })

        if not findings:
            findings = [{
                "type": "PENIBILITE_AUCUN_SIGNAL",
                "niveau": "FAIBLE",
                "cause": "aucune contrainte de penibilite detectee",
            }]

        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="DETECTER_PENIBILITE_RH",
            confidence=0.85 if detected_keywords else 0.60,
            status="SUCCESS",
            findings=findings,
            financial_data=financial_data if financial_data else None,
            source_pages=sorted(source_pages),
            execution_time_ms=0,
        )
