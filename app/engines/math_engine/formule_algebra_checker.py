"""
SMART_AO V7.1 - formule_algebra_checker.py
===========================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9.5 - Phase: 5
"""

"""
SMART_AO V7.1 - Syntax Checker Formules de Révision
=====================================================
Vérifie la cohérence algébrique des formules de révision de prix:
- Somme des coefficients = 1.00 ± tolérance
- Indices INSEE cités existent dans le référentiel
- Date de base cohérente

Source: RAPPORT (1).md §7.32
"""

import json
import os
import re
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from app.engines.math_engine.types import Amount, SolverResult


REFERENTIEL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "data", "referentiels", "indices_insee_valides.json"
)


@dataclass
class FormuleCheckResult:
    """Résultat de la vérification d'une formule de révision."""
    somme_coefficients: Decimal
    erreur: bool
    indice_inexistant: Optional[str]
    impact_estime_pct: Decimal
    date_base_valide: bool
    detail_calcul: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "somme_coefficients": float(self.somme_coefficients.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)),
            "erreur": self.erreur,
            "indice_inexistant": self.indice_inexistant,
            "impact_estime_pct": float(self.impact_estime_pct.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            "date_base_valide": self.date_base_valide,
            "detail_calcul": self.detail_calcul,
        }


class FormuleAlgebraChecker:
    """
    Vérificateur algébrique des formules de révision.

    Charge le référentiel `indices_insee_valides.json` et valide:
    - Σ coefficients = 1.00 ± tolérance
    - Chaque indice cité existe
    - Date de base dans la plage autorisée
    """

    def __init__(self, referentiel_path: Optional[str] = None):
        self.referentiel_path = referentiel_path or REFERENTIEL_PATH
        self.referentiel = self._load_referentiel()
        self.tolerance = Decimal(str(self.referentiel.get("regles_validation", {}).get("somme_coefficients_tolerance", 0.001)))

    def _load_referentiel(self) -> Dict[str, Any]:
        try:
            with open(self.referentiel_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"indices": {}, "regles_validation": {"somme_coefficients_tolerance": 0.001}}

    def _extract_indices(self, formule_texte: str) -> List[str]:
        """Extrait les codes indices INSEE d'une formule textuelle."""
        pattern = r"\b(BT\d{1,2}[a-z]?|TP\d{1,2}|FM\d[A-Z])\b"
        return list(set(re.findall(pattern, formule_texte)))

    def _validate_indices(self, indices: List[str]) -> Optional[str]:
        """Retourne le premier indice inexistant ou None."""
        valid_indices = self.referentiel.get("indices", {})
        for indice in indices:
            if indice not in valid_indices:
                return indice
        return None

    def _validate_date_base(self, date_base: Optional[str]) -> bool:
        """Vérifie que la date de base est dans la plage autorisée."""
        if not date_base:
            return False
        try:
            d = date.fromisoformat(date_base)
            regles = self.referentiel.get("regles_validation", {})
            date_min = date.fromisoformat(regles.get("date_base_min", "2020-01-01"))
            date_max = date.fromisoformat(regles.get("date_base_max", "2026-12-31"))
            return date_min <= d <= date_max
        except (ValueError, TypeError):
            return False

    def solve(self, data: Dict[str, Any]) -> SolverResult:
        """
        Vérifie une formule de révision.

        Args:
            data: dict avec coefficients (list), formule (texte optionnel),
                  date_base (optionnel), currency (optionnel).

        Returns:
            SolverResult avec la somme des coefficients et les erreurs détectées.
        """
        coefficients = data.get("coefficients", [])
        formule_texte = data.get("formule", "")
        date_base = data.get("date_base")
        currency = data.get("currency", "EUR")

        somme = Decimal("0")
        coeffs_dec = []
        for c in coefficients:
            d = Decimal(str(c))
            coeffs_dec.append(d)
            somme += d

        erreur_somme = abs(somme - Decimal("1")) > self.tolerance

        indices = self._extract_indices(formule_texte)
        indice_inexistant = self._validate_indices(indices)
        date_base_valide = self._validate_date_base(date_base)

        erreur = erreur_somme or indice_inexistant is not None or not date_base_valide

        # Estimation de l'impact: écart à 1.00 en pourcentage
        impact_estime = abs(somme - Decimal("1")) * Decimal("100")
        if indice_inexistant:
            impact_estime = max(impact_estime, Decimal("8.00"))

        impact_estime = impact_estime.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        somme = somme.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)

        detail = {
            "formule": formule_texte,
            "coefficients": [float(c) for c in coeffs_dec],
            "somme_coefficients": float(somme),
            "tolerance": float(self.tolerance),
            "erreur_somme": erreur_somme,
            "indices_detectes": indices,
            "indice_inexistant": indice_inexistant,
            "date_base": date_base,
            "date_base_valide": date_base_valide,
            "impact_estime_pct": float(impact_estime),
        }

        warnings = []
        if erreur_somme:
            warnings.append(f"Somme des coefficients = {somme} (attendu 1.000 ± {self.tolerance})")
        if indice_inexistant:
            warnings.append(f"Indice INSEE inexistant: {indice_inexistant}")
        if not date_base_valide:
            warnings.append("Date de base invalide ou manquante")

        return SolverResult(
            solver_name="FormuleAlgebraChecker",
            input_data=data,
            output=Amount(impact_estime, currency=currency),
            penalties=[],
            warnings=warnings,
            metadata={"detail_calcul": detail},
        )

    def verifier(
        self,
        coefficients: List[float],
        formule: str = "",
        date_base: Optional[str] = None,
    ) -> FormuleCheckResult:
        """API directe du checker."""
        result = self.solve({
            "coefficients": coefficients,
            "formule": formule,
            "date_base": date_base,
        })
        detail = result.metadata.get("detail_calcul", {})
        return FormuleCheckResult(
            somme_coefficients=Decimal(str(detail.get("somme_coefficients", 0))),
            erreur=detail.get("erreur_somme", False) or detail.get("indice_inexistant") is not None or not detail.get("date_base_valide", False),
            indice_inexistant=detail.get("indice_inexistant"),
            impact_estime_pct=result.output.value,
            date_base_valide=detail.get("date_base_valide", False),
            detail_calcul=detail,
        )


# Singleton
formule_checker = FormuleAlgebraChecker()


def get_formule_checker() -> FormuleAlgebraChecker:
    """Retourne le singleton FormuleAlgebraChecker."""
    return formule_checker


def verifier_formule_revision(
    coefficients: List[float],
    formule: str = "",
    date_base: Optional[str] = None,
) -> Dict[str, Any]:
    """Fonction utilitaire rapide."""
    result = formule_checker.verifier(coefficients, formule, date_base)
    return result.to_dict()
