"""
SMART_AO V7.1 - vigilance_solver.py
====================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9.5 - Phase: 5
"""

"""
SMART_AO V7.1 - Vigilance URSSAF Solver
========================================
Calcul déterministe de l'exposition solidaire et du blocage dépôt
lorsqu'une attestation URSSAF est expirée ou qu'un sous-traitant est en liquidation.

Source: RAPPORT (1).md §7.30
"""

from datetime import datetime, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, Optional
from dataclasses import dataclass

from app.engines.math_engine.types import Amount, SolverResult


# Seuil légal de validité d'une attestation URSSAF : 6 mois
VALIDITE_URSSAF_JOURS = 180


@dataclass
class VigilanceResult:
    """Résultat du calcul de vigilance URSSAF."""
    blocage_depot: bool
    attestation_valide: bool
    exposition_solidaire: Decimal
    motif_blocage: str
    detail_calcul: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "blocage_depot": self.blocage_depot,
            "attestation_valide": self.attestation_valide,
            "exposition_solidaire": float(self.exposition_solidaire.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            "motif_blocage": self.motif_blocage,
            "detail_calcul": self.detail_calcul,
        }


class VigilanceSolver:
    """
    Solveur de vigilance URSSAF et délit de marchandage.

    Règles:
    - Attestation URSSAF doit dater de moins de 6 mois.
    - Si expirée > 6 mois → blocage dépôt + exposition solidaire = montant sous-traité.
    - Si sous-traitant en liquidation → blocage dépôt + exposition = 100% du montant.
    """

    def solve(self, data: Dict[str, Any]) -> SolverResult:
        """
        Calcule l'exposition solidaire et le blocage dépôt.

        Args:
            data: dict avec date_attestation (ISO), montant_sous_traite,
                  statut_juridique (optionnel), currency (optionnel).

        Returns:
            SolverResult avec exposition_solidaire et blocage_depot.
        """
        date_attestation_str = data.get("date_attestation")
        montant_sous_traite = Decimal(str(data.get("montant_sous_traite", 0)))
        statut_juridique = data.get("statut_juridique", "actif")
        currency = data.get("currency", "EUR")

        attestation_valide = False
        motif_blocage = ""

        if statut_juridique.lower() in ["liquidation", "radiation", "cessation"]:
            blocage_depot = True
            motif_blocage = "Sous-traitant en liquidation / radié — DC4 bloqué"
        elif date_attestation_str:
            try:
                date_attestation = datetime.fromisoformat(date_attestation_str.replace("Z", "+00:00"))
                if date_attestation.tzinfo is None:
                    date_attestation = date_attestation.replace(tzinfo=timezone.utc)

                age_jours = (datetime.now(timezone.utc) - date_attestation).days
                attestation_valide = age_jours <= VALIDITE_URSSAF_JOURS

                if attestation_valide:
                    blocage_depot = False
                    motif_blocage = "Attestation URSSAF valide"
                else:
                    blocage_depot = True
                    motif_blocage = f"Attestation URSSAF expirée depuis {age_jours - VALIDITE_URSSAF_JOURS} jours — DC4 bloqué"
            except (ValueError, TypeError):
                blocage_depot = True
                motif_blocage = "Date d'attestation URSSAF invalide — DC4 bloqué"
        else:
            blocage_depot = True
            motif_blocage = "Attestation URSSAF manquante — DC4 bloqué"

        exposition = montant_sous_traite if blocage_depot else Decimal("0")
        exposition = exposition.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        detail = {
            "formule_exposition": "exposition = montant_sous_traite si blocage, sinon 0",
            "date_attestation": date_attestation_str,
            "montant_sous_traite": float(montant_sous_traite),
            "statut_juridique": statut_juridique,
            "validite_jours": VALIDITE_URSSAF_JOURS,
            "attestation_valide": attestation_valide,
            "blocage_depot": blocage_depot,
            "motif_blocage": motif_blocage,
        }

        warnings = []
        if blocage_depot:
            warnings.append(motif_blocage)

        return SolverResult(
            solver_name="VigilanceSolver",
            input_data=data,
            output=Amount(exposition, currency=currency),
            penalties=[],
            warnings=warnings,
            metadata={"detail_calcul": detail},
        )

    def calculer(
        self,
        date_attestation: Optional[str],
        montant_sous_traite: float,
        statut_juridique: str = "actif",
    ) -> VigilanceResult:
        """API directe du solveur."""
        result = self.solve({
            "date_attestation": date_attestation,
            "montant_sous_traite": montant_sous_traite,
            "statut_juridique": statut_juridique,
        })

        detail = result.metadata.get("detail_calcul", {})
        return VigilanceResult(
            blocage_depot=detail.get("blocage_depot", True),
            attestation_valide=detail.get("attestation_valide", False),
            exposition_solidaire=result.output.value,
            motif_blocage=detail.get("motif_blocage", ""),
            detail_calcul=detail,
        )


# Singleton
vigilance_solver = VigilanceSolver()


def get_vigilance_solver() -> VigilanceSolver:
    """Retourne le singleton VigilanceSolver."""
    return vigilance_solver


def calculer_exposition_urssaf(
    date_attestation: Optional[str],
    montant_sous_traite: float,
    statut_juridique: str = "actif",
) -> Dict[str, Any]:
    """Fonction utilitaire rapide."""
    result = vigilance_solver.calculer(date_attestation, montant_sous_traite, statut_juridique)
    return result.to_dict()
