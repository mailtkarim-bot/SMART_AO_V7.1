"""
SMART_AO V7.1 - sourcing_api_solver.py
=======================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9.5 - Phase: 5
"""

"""
SMART_AO V7.1 - Sourcing & API Profil Acheteur Solver
======================================================
Assemble le DUME natif JSON et simule le push API vers Profil Acheteur / PLACE
avec horodatage cryptographique.

Aucun calcul d'euros dans ce solver (conforme RAPPORT §7.33).
Source: RAPPORT (1).md §7.33
"""

import hashlib
import json
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any, Optional
from dataclasses import dataclass

from app.engines.math_engine.types import Amount, SolverResult


@dataclass
class SourcingAPIResult:
    """Résultat de l'assemblage DUME / push API."""
    dume_json: Dict[str, Any]
    horodatage: str
    empreinte_sha256: str
    statut_envoi: str
    plateforme: str
    detail_calcul: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dume_json": self.dume_json,
            "horodatage": self.horodatage,
            "empreinte_sha256": self.empreinte_sha256,
            "statut_envoi": self.statut_envoi,
            "plateforme": self.plateforme,
            "detail_calcul": self.detail_calcul,
        }


class SourcingAPISolver:
    """
    Solveur d'assemblage DUME natif JSON et push API Profil Acheteur.

    Ce solver ne fait aucun calcul financier. Il génère un DUME JSON
    structuré, un horodatage UTC et une empreinte SHA-256 de preuve.
    """

    def solve(self, data: Dict[str, Any]) -> SolverResult:
        """
        Assemble le DUME JSON et simule le push API.

        Args:
            data: dict avec siret, dc1, dc2, dume, plateforme, pieces_jointes,
                  currency (optionnel, ignoré car pas de calcul €).

        Returns:
            SolverResult avec dume_json et horodatage dans metadata.
        """
        siret = data.get("siret", "")
        plateforme = data.get("plateforme", "PLACE")
        dc1 = data.get("dc1", {})
        dc2 = data.get("dc2", {})
        dume_input = data.get("dume", {})
        pieces_jointes = data.get("pieces_jointes", [])

        horodatage = datetime.now(timezone.utc).isoformat()

        dume_json = {
            "version": "DUME-JSON-1.0",
            "plateforme": plateforme,
            "horodatage": horodatage,
            "soumissionnaire": {
                "siret": siret,
                "dc1": dc1,
                "dc2": dc2,
            },
            "dume": dume_input,
            "pieces_jointes": pieces_jointes,
            "statut": "PRET_A_ENVOI",
        }

        # Empreinte cryptographique SHA-256 du DUME
        dume_str = json.dumps(dume_json, sort_keys=True, ensure_ascii=False)
        empreinte = hashlib.sha256(dume_str.encode("utf-8")).hexdigest()
        dume_json["empreinte_sha256"] = empreinte

        # Simulation du push API (en production: appel HTTP réel)
        statut_envoi = "SIMULATION_OK"

        detail = {
            "formule": "Aucun calcul € — assemblage DUME JSON + horodatage + SHA-256",
            "plateforme": plateforme,
            "siret": siret,
            "horodatage": horodatage,
            "empreinte_sha256": empreinte,
            "statut_envoi": statut_envoi,
            "nb_pieces_jointes": len(pieces_jointes),
        }

        return SolverResult(
            solver_name="SourcingAPISolver",
            input_data=data,
            output=Amount(Decimal("0"), currency=data.get("currency", "EUR")),
            penalties=[],
            warnings=[],
            metadata={
                "dume_json": dume_json,
                "horodatage": horodatage,
                "empreinte_sha256": empreinte,
                "statut_envoi": statut_envoi,
                "plateforme": plateforme,
                "detail_calcul": detail,
            },
        )

    def assembler(
        self,
        siret: str,
        plateforme: str = "PLACE",
        dc1: Optional[Dict[str, Any]] = None,
        dc2: Optional[Dict[str, Any]] = None,
        dume: Optional[Dict[str, Any]] = None,
        pieces_jointes: Optional[list] = None,
    ) -> SourcingAPIResult:
        """API directe du solveur."""
        result = self.solve({
            "siret": siret,
            "plateforme": plateforme,
            "dc1": dc1 or {},
            "dc2": dc2 or {},
            "dume": dume or {},
            "pieces_jointes": pieces_jointes or [],
        })

        meta = result.metadata
        return SourcingAPIResult(
            dume_json=meta.get("dume_json", {}),
            horodatage=meta.get("horodatage", ""),
            empreinte_sha256=meta.get("empreinte_sha256", ""),
            statut_envoi=meta.get("statut_envoi", ""),
            plateforme=meta.get("plateforme", ""),
            detail_calcul=meta.get("detail_calcul", {}),
        )


# Singleton
sourcing_api_solver = SourcingAPISolver()


def get_sourcing_api_solver() -> SourcingAPISolver:
    """Retourne le singleton SourcingAPISolver."""
    return sourcing_api_solver


def assembler_dume_api(
    siret: str,
    plateforme: str = "PLACE",
    dc1: Optional[Dict[str, Any]] = None,
    dc2: Optional[Dict[str, Any]] = None,
    dume: Optional[Dict[str, Any]] = None,
    pieces_jointes: Optional[list] = None,
) -> Dict[str, Any]:
    """Fonction utilitaire rapide."""
    result = sourcing_api_solver.assembler(siret, plateforme, dc1, dc2, dume, pieces_jointes)
    return result.to_dict()
