"""
SMART_AO V7.1 - zan_solver.py
==============================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9.5 - Phase: 5
"""

"""
SMART_AO V7.1 - ZAN & Trackterres Solver
=========================================
Calcul déterministe du coût d'évacuation des terres selon la loi ZAN,
avec transport vers l'ISDI la plus proche et traçabilité Trackterres.

Formule:
    cout_total = volume × (tri + transport × distance + exutoire)

Source: RAPPORT (1).md §7.31
"""

import json
import math
import os
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, Optional
from dataclasses import dataclass

from app.engines.math_engine.types import Amount, SolverResult


REFERENTIEL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "data", "referentiels", "isdi_geolocalisees.json"
)


@dataclass
class ZANResult:
    """Résultat du calcul ZAN."""
    cout_total: Decimal
    volume: Decimal
    distance_km: Decimal
    cout_m3: Decimal
    isdi_id: Optional[str]
    trackterres_obligatoire: bool
    detail_calcul: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cout_total": float(self.cout_total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            "volume": float(self.volume.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            "distance_km": float(self.distance_km.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            "cout_m3": float(self.cout_m3.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            "isdi_id": self.isdi_id,
            "trackterres_obligatoire": self.trackterres_obligatoire,
            "detail_calcul": self.detail_calcul,
        }


class ZANSolver:
    """
    Solveur de coût ZAN & Trackterres.

    Charge le référentiel `isdi_geolocalisees.json` et calcule le coût
    d'évacuation des terres vers l'ISDI la plus proche.
    """

    def __init__(self, referentiel_path: Optional[str] = None):
        self.referentiel_path = referentiel_path or REFERENTIEL_PATH
        self.referentiel = self._load_referentiel()

    def _load_referentiel(self) -> Dict[str, Any]:
        try:
            with open(self.referentiel_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"isdi": [], "trackterres": {"obligatoire": True, "cout_tracking_m3": 1.2}}

    def _haversine(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calcule la distance en km entre deux points GPS."""
        R = 6371.0
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def _find_nearest_isdi(self, lat: float, lon: float, type_terre: str) -> Optional[Dict[str, Any]]:
        """Trouve l'ISDI la plus proche acceptant le type de terre."""
        isdis = self.referentiel.get("isdi", [])
        eligible = [
            isdi for isdi in isdis
            if type_terre.lower() in [t.lower() for t in isdi.get("types_acceptes", [])]
        ]
        if not eligible:
            eligible = isdis

        nearest = None
        min_distance = float("inf")
        for isdi in eligible:
            distance = self._haversine(lat, lon, isdi["lat"], isdi["lon"])
            if distance < min_distance:
                min_distance = distance
                nearest = isdi
                nearest["distance_km"] = distance

        return nearest

    def solve(self, data: Dict[str, Any]) -> SolverResult:
        """
        Calcule le coût d'évacuation ZAN.

        Args:
            data: dict avec volume, lat, lon, type_terre, dept,
                  distance_km (optionnel), currency (optionnel).

        Returns:
            SolverResult avec le coût total.
        """
        volume = Decimal(str(data.get("volume", 0)))
        lat = data.get("lat")
        lon = data.get("lon")
        type_terre = data.get("type_terre", "terre")
        distance_override = data.get("distance_km")
        currency = data.get("currency", "EUR")

        isdi = None
        distance_km = Decimal("0")
        tarif_exutoire = Decimal("15.00")

        if distance_override is not None:
            distance_km = Decimal(str(distance_override))
            tarif_exutoire = Decimal("15.00")
        elif lat is not None and lon is not None:
            isdi = self._find_nearest_isdi(float(lat), float(lon), type_terre)
            if isdi:
                distance_km = Decimal(str(isdi.get("distance_km", 0)))
                tarif_exutoire = Decimal(str(isdi.get("tarif_m3", 15.0)))

        cout_transport_km = Decimal(str(self.referentiel.get("unite_transport_eur_km", 0.85)))
        trackterres = self.referentiel.get("trackterres", {})
        trackterres_obligatoire = trackterres.get("obligatoire", True)
        cout_tracking_m3 = Decimal(str(trackterres.get("cout_tracking_m3", 1.2)))

        # Formule: volume × (tri + transport × distance + exutoire + tracking)
        cout_tri_m3 = Decimal("5.00")  # Coût de tri / chargement estimé
        cout_m3 = cout_tri_m3 + (cout_transport_km * distance_km) + tarif_exutoire + cout_tracking_m3
        cout_total = volume * cout_m3
        cout_total = cout_total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        detail = {
            "formule": "volume × (tri + transport × distance + exutoire + tracking)",
            "volume": float(volume),
            "distance_km": float(distance_km),
            "cout_tri_m3": float(cout_tri_m3),
            "cout_transport_km": float(cout_transport_km),
            "tarif_exutoire_m3": float(tarif_exutoire),
            "cout_tracking_m3": float(cout_tracking_m3),
            "cout_m3": float(cout_m3.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            "type_terre": type_terre,
            "isdi_id": isdi.get("id") if isdi else None,
            "trackterres_obligatoire": trackterres_obligatoire,
        }

        return SolverResult(
            solver_name="ZANSolver",
            input_data=data,
            output=Amount(cout_total, currency=currency),
            penalties=[],
            warnings=[],
            metadata={"detail_calcul": detail},
        )

    def calculer(
        self,
        volume: float,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        type_terre: str = "terre",
        distance_km: Optional[float] = None,
    ) -> ZANResult:
        """API directe du solveur."""
        data = {
            "volume": volume,
            "type_terre": type_terre,
        }
        if lat is not None and lon is not None:
            data["lat"] = lat
            data["lon"] = lon
        if distance_km is not None:
            data["distance_km"] = distance_km

        result = self.solve(data)
        detail = result.metadata.get("detail_calcul", {})
        return ZANResult(
            cout_total=result.output.value,
            volume=Decimal(str(volume)),
            distance_km=Decimal(str(detail.get("distance_km", 0))),
            cout_m3=Decimal(str(detail.get("cout_m3", 0))),
            isdi_id=detail.get("isdi_id"),
            trackterres_obligatoire=detail.get("trackterres_obligatoire", True),
            detail_calcul=detail,
        )


# Singleton
zan_solver = ZANSolver()


def get_zan_solver() -> ZANSolver:
    """Retourne le singleton ZANSolver."""
    return zan_solver


def calculer_cout_zan(
    volume: float,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    type_terre: str = "terre",
    distance_km: Optional[float] = None,
) -> Dict[str, Any]:
    """Fonction utilitaire rapide."""
    result = zan_solver.calculer(volume, lat, lon, type_terre, distance_km)
    return result.to_dict()
