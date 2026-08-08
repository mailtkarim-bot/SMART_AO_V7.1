"""
SMART_AO V7.1 - agent_zan_trackterres.py
=======================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 07/08/2026
Build: 9.5 - Phase: 5
"""


"""
SMART_AO V7.1 - ZAN & Trackterres Agent
Source: ARCHITECTURE_V7_ENGINE.md §2 + ADR-044 + RAPPORT (1).md §7.31

Agent de détection de l'évacuation des terres et calcul du coût ZAN
via le ZANSolver. Les montants sont isolés dans financial_data ; les
findings restent qualitatifs (ZERO € garanti).
"""

from datetime import timedelta
from typing import Any, Dict, List

from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.engines.agent_runtime.registry import registry
from app.engines.math_engine.zan_solver import ZANSolver, get_zan_solver
from app.engines.workflow_engine.mission import Mission


@registry.register(capabilities=["DETECTER_ZAN", "CALCULER_COUT_EVACUATION"])
class ZANTrackterresAgent(BaseAgent):
    name = "ZAN Trackterres Detector"
    capabilities = ["DETECTER_ZAN", "CALCULER_COUT_EVACUATION"]
    tags = ["environnement", "risque"]
    estimated_duration = timedelta(seconds=10)
    is_blocking = False

    # Mots-clés utilisés pour détecter un enjeu d'évacuation de terres.
    _TERRES_KEYWORDS = [
        "terre",
        "terres",
        "déblai",
        "deblai",
        "remblai",
        "excavation",
        "evacuation",
        "évacuation",
        "zan",
        "trackterres",
        "isdi",
        "sous-produits",
        "inertes",
    ]

    def __init__(self, solver: ZANSolver = None):
        self.solver = solver or get_zan_solver()

    def can_handle(self, mission: Mission) -> float:
        context = mission.context if hasattr(mission, "context") else {}
        context_str = str(context).lower()

        has_dce = False
        if hasattr(mission, "has_document_type"):
            has_dce = mission.has_document_type("DCE")
        has_dce = has_dce or "dce" in context_str

        keyword_hits = sum(1 for kw in self._TERRES_KEYWORDS if kw in context_str)
        has_geoloc = (
            context.get("lat") is not None and context.get("lon") is not None
        ) or context.get("distance_km") is not None
        has_volume = context.get("volume_terres") is not None or context.get("volume") is not None

        if has_dce and keyword_hits >= 2 and (has_geoloc or has_volume):
            return 0.95
        if has_dce and keyword_hits >= 2:
            return 0.80
        if keyword_hits >= 1:
            return 0.45
        return 0.10

    async def execute(self, input: AgentInput) -> AgentOutput:
        chunks = input.dce_chunks or []
        context = input.context or {}
        findings: List[Dict[str, Any]] = []
        warnings: List[str] = []

        # Détection qualitative dans les chunks RAG
        mentions = set()
        source_pages: List[int] = []
        for chunk in chunks:
            text = str(chunk.get("text", chunk)).lower()
            page = chunk.get("page")
            if page is not None:
                try:
                    source_pages.append(int(page))
                except (ValueError, TypeError):
                    pass
            for keyword in self._TERRES_KEYWORDS:
                if keyword in text:
                    mentions.add(keyword)

        source_pages = sorted(set(source_pages)) or [1]

        if mentions:
            findings.append({
                "type": "MENTIONS_EVACUATION_TERRES_DETECTEES",
                "niveau": "INFO",
                "mots_cles": sorted(mentions),
                "recommandation": "Analyser le volume, le type de terre et la géolocalisation pour évaluer l'obligation ZAN.",
            })

        # Extraction des paramètres de calcul
        volume = context.get("volume_terres") or context.get("volume") or 0
        lat = context.get("lat")
        lon = context.get("lon")
        type_terre = context.get("type_terre", "terre")
        distance_km = context.get("distance_km")

        # Appel au solveur uniquement si un volume est disponible
        financial_data: Dict[str, Any] = {}
        if volume:
            try:
                result = self.solver.calculer(
                    volume=float(volume),
                    lat=float(lat) if lat is not None else None,
                    lon=float(lon) if lon is not None else None,
                    type_terre=str(type_terre),
                    distance_km=float(distance_km) if distance_km is not None else None,
                )
                financial_data = result.to_dict()

                isdi_id = result.isdi_id
                findings.append({
                    "type": "COUT_EVACUATION_ZAN_CALCULE",
                    "niveau": "RISQUE" if result.trackterres_obligatoire else "INFO",
                    "volume_terres": float(result.volume),
                    "type_terre": str(type_terre),
                    "distance_km": float(result.distance_km),
                    "isdi_identifie": isdi_id is not None,
                    "isdi_id": isdi_id,
                    "trackterres_obligatoire": result.trackterres_obligatoire,
                    "recommandation": (
                        "Le détail du calcul ZAN est disponible dans financial_data. "
                        "Vérifier l'ISDI et la traçabilité Trackterres dans l'offre."
                    ),
                })
            except Exception as exc:
                warnings.append(f"Erreur lors du calcul ZAN : {exc}")
                findings.append({
                    "type": "CALCUL_ZAN_ECHOUE",
                    "niveau": "AVERTISSEMENT",
                    "detail": "Impossible de calculer le coût d'évacuation avec les données fournies.",
                    "recommandation": "Vérifier volume, coordonnées GPS et distance fournis.",
                })
        else:
            findings.append({
                "type": "VOLUME_TERRES_NON_FOURNI",
                "niveau": "INFO",
                "recommandation": (
                    "Aucun volume de terres détecté dans le contexte. "
                    "Fournir volume_terres ou volume pour activer le calcul ZAN."
                ),
            })

        status = "SUCCESS" if not warnings else "PARTIAL"
        confidence = 0.90 if financial_data else 0.65

        return AgentOutput(
            agent_name=self.name,
            mission_id=input.mission_id,
            capability="DETECTER_ZAN",
            confidence=confidence,
            status=status,
            findings=findings,
            financial_data=financial_data if financial_data else None,
            warnings=warnings,
            source_pages=source_pages,
            execution_time_ms=0,
        )
