"""
SMART_AO V7.1 - penibilite_solver.py
=====================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9.5 - Phase: 5
"""

"""
SMART_AO V7.1 - Pénibilité RH Solver
=====================================
Calcul déterministe du surcoût intérim lié aux contraintes de pénibilité RH.

Formule:
    surcout = nb_manquants × taux_horaire × coeff_majoration × heures × duree_semaines

Source: RAPPORT (1).md §7.29
"""

import json
import os
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, Optional
from dataclasses import dataclass

from app.engines.math_engine.types import Amount, SolverResult


# Chemin vers le référentiel des taux intérim BTP
REFERENTIEL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "data", "referentiels", "taux_interim_btp.json"
)


@dataclass
class PenibiliteInput:
    """Entrées du solveur de pénibilité RH."""
    nb_manquants: int
    metier: str
    duree_semaines: int
    heures_par_semaine: int = 35
    region: str = "default"
    contrainte: str = "penibilite_standard"  # ou "penibilite_elevee"
    taux_horaire_override: Optional[Decimal] = None
    coeff_majoration_override: Optional[Decimal] = None


@dataclass
class PenibiliteResult:
    """Résultat du calcul de pénibilité RH."""
    surcout_estime: Decimal
    taux_horaire: Decimal
    coeff_majoration: Decimal
    nb_manquants: int
    duree_semaines: int
    heures_par_semaine: int
    detail_calcul: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "surcout_estime": float(self.surcout_estime.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            "taux_horaire": float(self.taux_horaire.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            "coeff_majoration": float(self.coeff_majoration.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            "nb_manquants": self.nb_manquants,
            "duree_semaines": self.duree_semaines,
            "heures_par_semaine": self.heures_par_semaine,
            "detail_calcul": self.detail_calcul,
        }


class PenibiliteSolver:
    """
    Solveur de surcoût intérim lié à la pénibilité RH.

    Charge le référentiel `taux_interim_btp.json` et applique la formule:
        surcout = nb_manquants × taux_horaire × coeff_majoration × heures × duree_semaines
    """

    def __init__(self, referentiel_path: Optional[str] = None):
        self.referentiel_path = referentiel_path or REFERENTIEL_PATH
        self.referentiel = self._load_referentiel()

    def _load_referentiel(self) -> Dict[str, Any]:
        """Charge le référentiel JSON des taux intérim BTP."""
        try:
            with open(self.referentiel_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"taux": {}, "coeff_majoration": {}}

    def _get_taux_horaire(self, metier: str, region: str) -> Decimal:
        """Récupère le taux horaire pour un métier et une région."""
        metier_clean = metier.lower().strip()
        taux_metier = self.referentiel.get("taux", {}).get(metier_clean, {})
        if not taux_metier:
            return Decimal("22.00")  # Taux par défaut sécurisé

        regions = taux_metier.get("regions", {})
        taux_region = regions.get(region, regions.get("default", taux_metier.get("base", 22.00)))
        return Decimal(str(taux_region))

    def _get_coeff_majoration(self, contrainte: str) -> Decimal:
        """Récupère le coefficient de majoration selon le type de contrainte."""
        coeffs = self.referentiel.get("coeff_majoration", {})
        return Decimal(str(coeffs.get(contrainte, coeffs.get("penibilite_standard", 1.35))))

    def solve(self, data: Dict[str, Any]) -> SolverResult:
        """
        Calcule le surcoût intérim.

        Args:
            data: dict avec les clés nb_manquants, metier, duree_semaines,
                  heures_par_semaine (optionnel), region (optionnel),
                  contrainte (optionnel), currency (optionnel).

        Returns:
            SolverResult avec le surcoût estimé.
        """
        nb_manquants = int(data.get("nb_manquants", 0))
        metier = data.get("metier", "manoeuvre")
        duree_semaines = int(data.get("duree_semaines", 0))
        heures_par_semaine = int(data.get("heures_par_semaine", 35))
        region = data.get("region", "default")
        contrainte = data.get("contrainte", "penibilite_standard")
        currency = data.get("currency", "EUR")

        taux_horaire = Decimal(str(data.get("taux_horaire"))) if data.get("taux_horaire") else self._get_taux_horaire(metier, region)
        coeff_majoration = Decimal(str(data.get("coeff_majoration"))) if data.get("coeff_majoration") else self._get_coeff_majoration(contrainte)

        nb_manquants_dec = Decimal(str(nb_manquants))
        heures_dec = Decimal(str(heures_par_semaine))
        duree_dec = Decimal(str(duree_semaines))

        surcout = nb_manquants_dec * taux_horaire * coeff_majoration * heures_dec * duree_dec
        surcout = surcout.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        detail = {
            "formule": "nb_manquants × taux_horaire × coeff_majoration × heures_par_semaine × duree_semaines",
            "nb_manquants": nb_manquants,
            "taux_horaire": float(taux_horaire),
            "coeff_majoration": float(coeff_majoration),
            "heures_par_semaine": heures_par_semaine,
            "duree_semaines": duree_semaines,
            "metier": metier,
            "region": region,
            "contrainte": contrainte,
        }

        return SolverResult(
            solver_name="PenibiliteSolver",
            input_data=data,
            output=Amount(surcout, currency=currency),
            penalties=[],
            warnings=[],
            metadata={"detail_calcul": detail},
        )

    def calculer(
        self,
        nb_manquants: int,
        metier: str,
        duree_semaines: int,
        heures_par_semaine: int = 35,
        region: str = "default",
        contrainte: str = "penibilite_standard",
    ) -> PenibiliteResult:
        """API directe du solveur."""
        result = self.solve({
            "nb_manquants": nb_manquants,
            "metier": metier,
            "duree_semaines": duree_semaines,
            "heures_par_semaine": heures_par_semaine,
            "region": region,
            "contrainte": contrainte,
        })

        detail = result.metadata.get("detail_calcul", {})
        return PenibiliteResult(
            surcout_estime=result.output.value,
            taux_horaire=Decimal(str(detail.get("taux_horaire", 0))),
            coeff_majoration=Decimal(str(detail.get("coeff_majoration", 0))),
            nb_manquants=nb_manquants,
            duree_semaines=duree_semaines,
            heures_par_semaine=heures_par_semaine,
            detail_calcul=detail,
        )


# Singleton
penibilite_solver = PenibiliteSolver()


def get_penibilite_solver() -> PenibiliteSolver:
    """Retourne le singleton PenibiliteSolver."""
    return penibilite_solver


def calculer_surcout_penibilite(
    nb_manquants: int,
    metier: str,
    duree_semaines: int,
    heures_par_semaine: int = 35,
    region: str = "default",
    contrainte: str = "penibilite_standard",
) -> float:
    """Fonction utilitaire rapide."""
    result = penibilite_solver.calculer(
        nb_manquants, metier, duree_semaines, heures_par_semaine, region, contrainte
    )
    return float(result.surcout_estime)
