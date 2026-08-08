"""
SMART_AO V7.1 - agent_formule_revision.py
==========================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 07/08/2026
Build: 9.5 - Phase: 5
"""


"""
SMART_AO V7.1 - Formule de Révision Agent
Source: RAPPORT (1).md §7.32

Agent d'extraction et de vérification algébrique des formules de révision de prix
présentes dans le CCAP (Cahier des Clauses Administratives Particulières).

Fonctionnalités:
- Extraction de la formule de révision du CCAP
- Vérification que la somme des coefficients vaut 1.00 ± tolérance
- Vérification que les indices INSEE cités existent dans le référentiel
- Vérification de la cohérence de la date de base
- ZERO € : retour qualitatif uniquement, données chiffrées dans financial_data
"""

import re
from datetime import timedelta
from typing import Any, Dict, List

from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.engines.agent_runtime.registry import registry
from app.engines.math_engine.formule_algebra_checker import FormuleAlgebraChecker
from app.engines.workflow_engine.mission import Mission


# Mots-clés de détection d'une formule de révision
REVISION_KEYWORDS = [
    "révision des prix",
    "revision des prix",
    "formule de révision",
    "formule de revision",
    "coefficient",
    "indice insee",
    "BT01",
    "BT02",
    "BT03",
    "TP01",
    "FM0B",
    "FM1E",
    "FM3A",
    "date de base",
]

# Pattern de détection d'indices INSEE
INDICE_INSEE_PATTERN = re.compile(r"\b(BT0[1-9]|BT10|TP01|FM0B|FM1E|FM3A)\b")


@registry.register(capabilities=["CHECKER_FORMULE_REVISION", "DETECTER_ERREUR_CCAP"])
class FormuleRevisionAgent(BaseAgent):
    """
    Agent de vérification des formules de révision du CCAP.

    Capabilités:
    - CHECKER_FORMULE_REVISION: vérifie la cohérence algébrique de la formule
    - DETECTER_ERREUR_CCAP: détecte les erreurs dans les clauses du CCAP

    Contraintes:
    - ZERO € : retour qualitatif uniquement
    - Données financières / calculatoires dans financial_data
    """

    name = "Formule de Révision Checker"
    capabilities = ["CHECKER_FORMULE_REVISION", "DETECTER_ERREUR_CCAP"]
    dependencies = ["PARSER", "EXTRACTION"]
    tags = ["finance", "risque"]
    estimated_duration = timedelta(seconds=6)
    is_blocking = False

    def can_handle(self, mission: Mission) -> float:
        """Évaluer la pertinence pour cette mission."""
        has_ccap = mission.has_document_type("CCAP") or "ccap" in str(mission.context).lower()
        context_text = str(mission.context).lower()
        has_revision = any(kw.lower() in context_text for kw in REVISION_KEYWORDS)
        has_formulaire = "formule" in context_text and "revision" in context_text

        if has_ccap and has_revision:
            return 1.0
        if has_ccap and has_formulaire:
            return 0.95
        if has_revision:
            return 0.80
        if has_ccap:
            return 0.50
        return 0.10

    async def execute(self, input: AgentInput) -> AgentOutput:
        """Exécuter la vérification de la formule de révision."""
        chunks = input.dce_chunks
        findings: List[Dict[str, Any]] = []
        financial_data: Dict[str, Any] = {}
        source_pages: List[int] = []

        # 1. Récupération des données de formule depuis le contexte
        ccap_data = input.context.get("ccap", {})
        formule_texte = ccap_data.get("formule_revision", "")
        coefficients = ccap_data.get("coefficients", [])
        date_base = ccap_data.get("date_base_revision")

        # 2. Recherche dans les chunks si non fourni dans le contexte
        if not formule_texte and not coefficients:
            extracted = self._extract_from_chunks(chunks)
            formule_texte = extracted.get("formule", "")
            coefficients = extracted.get("coefficients", [])
            date_base = extracted.get("date_base", date_base)
            source_pages = extracted.get("pages", [])

        # 3. Exécution du checker algébrique
        checker = FormuleAlgebraChecker()
        if coefficients or formule_texte:
            solver_result = checker.solve(
                {
                    "coefficients": coefficients,
                    "formule": formule_texte,
                    "date_base": date_base,
                }
            )
            detail = solver_result.metadata.get("detail_calcul", {})

            # Données financières / calculatoires dans financial_data (RBAC patron)
            financial_data["formule_revision_analysis"] = {
                "formule": formule_texte,
                "coefficients": coefficients,
                "somme_coefficients": detail.get("somme_coefficients"),
                "tolerance": detail.get("tolerance"),
                "erreur_somme": detail.get("erreur_somme"),
                "indices_detectes": detail.get("indices_detectes", []),
                "indice_inexistant": detail.get("indice_inexistant"),
                "date_base": date_base,
                "date_base_valide": detail.get("date_base_valide"),
                "impact_estime_pct": detail.get("impact_estime_pct"),
                "warnings_solver": solver_result.warnings,
            }

            # Findings qualitatifs ZERO €
            if detail.get("erreur_somme"):
                findings.append(
                    {
                        "type": "ERREUR_SOMME_COEFFICIENTS",
                        "niveau": "CRITIQUE",
                        "details": "La somme des coefficients de la formule de révision s'écarte de 1,00 au-delà de la tolérance autorisée.",
                        "reference": "CCAP - Formule de révision des prix",
                        "recommandation": "Vérifier la cohérence algébrique de la formule avec le Maître d'Ouvrage.",
                    }
                )

            if detail.get("indice_inexistant"):
                findings.append(
                    {
                        "type": "INDICE_INSEE_INEXISTANT",
                        "niveau": "CRITIQUE",
                        "indice": detail.get("indice_inexistant"),
                        "details": "Un indice INSEE cité dans la formule n'existe pas dans le référentiel officiel.",
                        "reference": "Référentiel INSEE des indices de révision",
                        "recommandation": "Demander la correction du code indice ou sa justification réglementaire.",
                    }
                )

            if not detail.get("date_base_valide"):
                findings.append(
                    {
                        "type": "DATE_BASE_INVALIDE",
                        "niveau": "ELEVE",
                        "details": "La date de base de la formule de révision est manquante ou hors plage autorisée.",
                        "reference": "CCAP - Date de base de révision",
                        "recommandation": "Préciser une date de base cohérente avec la période de consultation.",
                    }
                )

            if not detail.get("erreur_somme") and not detail.get("indice_inexistant") and detail.get("date_base_valide"):
                findings.append(
                    {
                        "type": "FORMULE_REVISION_CONFORME",
                        "niveau": "FAIBLE",
                        "details": "La formule de révision respecte les contraintes algébriques et le référentiel INSEE.",
                        "reference": "CCAP - Formule de révision des prix",
                        "recommandation": "Aucune action requise sur la structure de la formule.",
                    }
                )
        else:
            findings.append(
                {
                    "type": "FORMULE_REVISION_NON_TROUVEE",
                    "niveau": "INFO",
                    "details": "Aucune formule de révision n'a été extraite du CCAP.",
                    "reference": "CCAP - Formule de révision des prix",
                    "recommandation": "Vérifier la présence du CCAP et la qualité de l'extraction.",
                }
            )

        # 4. Détection d'indices INSEE dans les chunks pour traçabilité
        indices_pages = self._detect_indices_pages(chunks)
        if indices_pages and not source_pages:
            source_pages = sorted(indices_pages)[:20]

        if not source_pages:
            source_pages = list(range(1, min(len(chunks) + 1, 10)))

        status = "SUCCESS"
        confidence = 0.90
        if findings and any(f["niveau"] == "CRITIQUE" for f in findings):
            status = "PARTIAL"
            confidence = 0.75

        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="CHECKER_FORMULE_REVISION",
            confidence=confidence,
            status=status,
            findings=findings,
            financial_data=financial_data if financial_data else None,
            source_pages=source_pages,
            execution_time_ms=0,
        )

    def _extract_from_chunks(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extraire une formule de révision, ses coefficients et date de base des chunks."""
        result: Dict[str, Any] = {"formule": "", "coefficients": [], "date_base": None, "pages": []}
        if not chunks:
            return result

        for idx, chunk in enumerate(chunks):
            text = str(chunk)
            text_lower = text.lower()

            # Détection de la formule textuelle
            if any(kw in text_lower for kw in REVISION_KEYWORDS):
                result["pages"].append(idx + 1)

                if not result["formule"]:
                    # Recherche d'une ligne contenant "P =" ou similaire
                    match = re.search(
                        r"P\s*=\s*P0\s*\[?[^\n]{10,300}\]?",
                        text,
                        re.IGNORECASE | re.DOTALL,
                    )
                    if match:
                        result["formule"] = re.sub(r"\s+", " ", match.group(0)).strip()

                # Extraction de coefficients sous forme de nombres décimaux
                if not result["coefficients"]:
                    coeffs = re.findall(r"\b0\.\d{2,4}\b", text)
                    if coeffs:
                        result["coefficients"] = [float(c) for c in coeffs]

                # Extraction d'une date de base (ISO ou mois/année)
                if not result["date_base"]:
                    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", text)
                    if date_match:
                        result["date_base"] = date_match.group(1)

        result["pages"] = sorted(set(result["pages"]))
        return result

    def _detect_indices_pages(self, chunks: List[Dict[str, Any]]) -> List[int]:
        """Retourne les pages contenant des indices INSEE."""
        pages = []
        for idx, chunk in enumerate(chunks):
            if INDICE_INSEE_PATTERN.search(str(chunk)):
                pages.append(idx + 1)
        return sorted(set(pages))
