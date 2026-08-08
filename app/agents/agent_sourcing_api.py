"""
SMART_AO V7.1 - agent_sourcing_api.py
======================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 07/08/2026
Build: 9.5 - Phase: 5
"""


"""
SMART_AO V7.1 - Sourcing API Agent
Source: RAPPORT (1).md §7.33 + ADR-044

Assemble le DUME JSON natif et simule le push API vers Profil Acheteur / PLACE.
ZERO € garanti - retourne uniquement du qualitatif dans findings.
Les données techniques du push API (DUME, empreinte SHA-256, horodatage)
sont transmises via financial_data pour traçabilité.
"""

from datetime import timedelta
from typing import List, Dict, Any

from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.engines.agent_runtime.registry import registry
from app.engines.math_engine.sourcing_api_solver import SourcingAPISolver
from app.engines.workflow_engine.mission import Mission


@registry.register(capabilities=["ASSEMBLER_DUME", "PUSH_API_PLACE"])
class SourcingAPIAgent(BaseAgent):
    name = "Sourcing API Assembler"
    capabilities = ["ASSEMBLER_DUME", "PUSH_API_PLACE"]
    dependencies = ["PARSER", "EXTRACTION"]
    tags = ["admin_only", "depose"]
    estimated_duration = timedelta(seconds=10)
    is_blocking = False

    def __init__(self):
        self._solver = SourcingAPISolver()

    def can_handle(self, mission: Mission) -> float:
        """
        Score pertinence 0.0-1.0 pour l'assemblage DUME / push API.
        Pertinent lorsque la mission contient les pièces constitutives
        du dossier de candidature (DC1, DC2, DUME, SIRET, pièces jointes).
        """
        ctx = mission.context or {}

        has_siret = bool(ctx.get("siret") or ctx.get("soumissionnaire", {}).get("siret"))
        has_dc1 = bool(ctx.get("dc1") or ctx.get("documents", {}).get("dc1"))
        has_dc2 = bool(ctx.get("dc2") or ctx.get("documents", {}).get("dc2"))
        has_dume = bool(ctx.get("dume") or ctx.get("documents", {}).get("dume"))
        has_pieces = bool(ctx.get("pieces_jointes") or ctx.get("documents", {}).get("pieces_jointes"))
        is_admin = ctx.get("is_admin", False) or ctx.get("role") == "admin"

        signals = [has_siret, has_dc1, has_dc2, has_dume, has_pieces]
        signal_count = sum(1 for s in signals if s)

        if signal_count >= 4 and is_admin:
            return 1.0
        if signal_count >= 3:
            return 0.85
        if signal_count >= 2:
            return 0.55
        if signal_count >= 1:
            return 0.25
        return 0.0

    async def execute(self, input: AgentInput) -> AgentOutput:
        """
        Assemble le DUME JSON natif et simule le push API.
        ZERO €: aucun montant, aucune marge, aucun BFR dans findings.
        """
        ctx = input.context or {}

        # Extraction des données de candidature depuis le contexte enrichi
        siret = (
            ctx.get("siret")
            or ctx.get("soumissionnaire", {}).get("siret")
            or ""
        )
        plateforme = ctx.get("plateforme", "PLACE")
        dc1 = ctx.get("dc1") or ctx.get("documents", {}).get("dc1") or {}
        dc2 = ctx.get("dc2") or ctx.get("documents", {}).get("dc2") or {}
        dume_input = ctx.get("dume") or ctx.get("documents", {}).get("dume") or {}
        pieces_jointes = (
            ctx.get("pieces_jointes")
            or ctx.get("documents", {}).get("pieces_jointes")
            or []
        )

        # Appel au solveur d'assemblage DUME / push API
        solver_result = self._solver.assembler(
            siret=siret,
            plateforme=plateforme,
            dc1=dc1,
            dc2=dc2,
            dume=dume_input,
            pieces_jointes=pieces_jointes,
        )

        # Findings qualitatifs uniquement - ZÉRO €
        findings: List[Dict[str, Any]] = [
            {
                "type": "DUME_ASSEMBLE",
                "niveau": "INFO",
                "details": "Document Unique de Marché Européen assemblé au format JSON natif",
                "plateforme": solver_result.plateforme,
                "statut_envoi": solver_result.statut_envoi,
            },
            {
                "type": "EMPREINTE_SHA256",
                "niveau": "INFO",
                "details": "Empreinte cryptographique générée pour preuve d'intégrité",
                "empreinte": solver_result.empreinte_sha256,
            },
            {
                "type": "HORODATAGE_API",
                "niveau": "INFO",
                "details": "Horodatage UTC apposé avant simulation de push API",
                "horodatage": solver_result.horodatage,
            },
        ]

        if not siret:
            findings.append({
                "type": "SIRET_MANQUANT",
                "niveau": "AVERTISSEMENT",
                "details": "Identifiant SIRET du soumissionnaire absent - DUME incomplet",
                "recommandation": "Compléter le SIRET avant envoi réel",
            })

        if not pieces_jointes:
            findings.append({
                "type": "PIECES_JOINTES_VIDES",
                "niveau": "AVERTISSEMENT",
                "details": "Aucune pièce jointe rattachée au DUME",
                "recommandation": "Vérifier les pièces complémentaires obligatoires",
            })

        # Données techniques / traçabilité dans financial_data (accès RBAC)
        financial_data = {
            "capability": "ASSEMBLER_DUME",
            "dume_json": solver_result.dume_json,
            "horodatage": solver_result.horodatage,
            "empreinte_sha256": solver_result.empreinte_sha256,
            "plateforme": solver_result.plateforme,
            "statut_envoi": solver_result.statut_envoi,
            "detail_calcul": solver_result.detail_calcul,
        }

        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="ASSEMBLER_DUME",
            confidence=0.95 if siret and pieces_jointes else 0.72,
            status="SUCCESS",
            findings=findings,
            financial_data=financial_data,
            source_pages=[],
            execution_time_ms=0,
        )
