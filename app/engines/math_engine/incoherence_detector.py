"""
SMART_AO V7 - incoherence_detector.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Détection d'Incohérences CCTP/DPGF - Solveur de détection et résolution
Source: ARCHITECTURE_V7_ENGINE.md §3.4
"""

from typing import Dict, List, Optional, Any, Set
from decimal import Decimal, getcontext
from dataclasses import dataclass, field
import logging
import re

from app.engines.math_engine.decimal_ops import DecimalOps

# Configuration de la précision pour Decimal
getcontext().prec = 28

logger = logging.getLogger(__name__)


@dataclass
class Incoherence:
    """Représente une incohérence détectée."""
    incoherence_id: str
    type_incoherence: str
    description: str
    emplacement: str
    niveau: str = "avertissement"
    valeur_cctp: Optional[Any] = None
    valeur_dpgf: Optional[Any] = None
    ecart: Optional[Decimal] = None
    solution_proposee: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "incoherence_id": self.incoherence_id,
            "type": self.type_incoherence,
            "niveau": self.niveau,
            "description": self.description,
            "emplacement": self.emplacement,
            "valeur_cctp": str(self.valeur_cctp) if self.valeur_cctp else None,
            "valeur_dpgf": str(self.valeur_dpgf) if self.valeur_dpgf else None,
            "ecart": float(self.ecart) if self.ecart else None,
            "solution_proposee": self.solution_proposee
        }


@dataclass
class IncoherenceReport:
    """Rapport complet des incohérences détectées."""
    mission_id: str
    total_incoherences: int
    score_coherence: float
    est_coherent: bool
    incoherences: List[Incoherence] = field(default_factory=list)
    incoherences_par_type: Dict[str, int] = field(default_factory=dict)
    incoherences_par_niveau: Dict[str, int] = field(default_factory=dict)
    recommandations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "total_incoherences": self.total_incoherences,
            "incoherences": [i.to_dict() for i in self.incoherences],
            "incoherences_par_type": self.incoherences_par_type,
            "incoherences_par_niveau": self.incoherences_par_niveau,
            "score_coherence": self.score_coherence,
            "est_coherent": self.est_coherent,
            "recommandations": self.recommandations
        }


class IncoherenceSolver:
    def __init__(self):
        self.decimal_ops = DecimalOps()
        self.tolerance_relative = Decimal("0.05")
        self.tolerance_absolue = Decimal("100")
    
    def detecter_incoherences(
        self,
        mission_id: str,
        cctp_data: Dict[str, Any],
        dpgf_data: Dict[str, Any]
    ) -> IncoherenceReport:
        incoherences = []
        incoherence_id = 0
        
        cctp_lots = self._extraire_lots(cctp_data)
        dpgf_lots = self._extraire_lots(dpgf_data)
        
        # Vérifier correspondance des lots
        incoherences.extend(self._verifier_lots_correspondants(mission_id, cctp_lots, dpgf_lots, incoherence_id))
        incoherence_id = len(incoherences)
        
        # Vérifier montants et quantités
        for lot_nom, cctp_lot in cctp_lots.items():
            if lot_nom in dpgf_lots:
                dpgf_lot = dpgf_lots[lot_nom]
                incoherences.extend(self._verifier_montants(mission_id, lot_nom, cctp_lot, dpgf_lot, incoherence_id))
                incoherence_id = len(incoherences)
                incoherences.extend(self._verifier_quantites(mission_id, lot_nom, cctp_lot, dpgf_lot, incoherence_id))
                incoherence_id = len(incoherences)
                incoherences.extend(self._verifier_unites(mission_id, lot_nom, cctp_lot, dpgf_lot, incoherence_id))
                incoherence_id = len(incoherences)
        
        # Vérifier global
        incoherences.extend(self._verifier_global(mission_id, cctp_data, dpgf_data, incoherence_id))
        
        # Statistiques
        total = len(incoherences)
        by_type = self._compter_par_type(incoherences)
        by_niveau = self._compter_par_niveau(incoherences)
        
        score_coherence = max(0.0, 1.0 - (total * 0.1))
        if by_niveau.get("critique", 0) > 0:
            score_coherence = max(0.0, score_coherence - 0.5)
        if by_niveau.get("erreur", 0) > 0:
            score_coherence = max(0.0, score_coherence - 0.3)
        
        est_coherent = score_coherence >= 0.95 and total == 0
        recommandations = self._generer_recommandations(incoherences, by_niveau, score_coherence)
        
        return IncoherenceReport(
            mission_id=mission_id,
            total_incoherences=total,
            incoherences=incoherences,
            incoherences_par_type=by_type,
            incoherences_par_niveau=by_niveau,
            score_coherence=round(score_coherence, 2),
            est_coherent=est_coherent,
            recommandations=recommandations
        )
    
    def _extraire_lots(self, data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        if "lots" in data:
            return data["lots"]
        return data if isinstance(data, dict) else {}
    
    def _extraire_montant(self, lot_data: Dict[str, Any]) -> Optional[Decimal]:
        for key in ["montant", "prix", "total", "montant_ht", "montant_total"]:
            if key in lot_data and lot_data[key] is not None:
                return Decimal(str(lot_data[key]))
        return None
    
    def _extraire_quantite(self, lot_data: Dict[str, Any]) -> Optional[Decimal]:
        for key in ["quantite", "qte", "quantity"]:
            if key in lot_data and lot_data[key] is not None:
                return Decimal(str(lot_data[key]))
        return None
    
    def _extraire_unite(self, lot_data: Dict[str, Any]) -> Optional[str]:
        for key in ["unite", "unit", "unite_mesure"]:
            if key in lot_data:
                return str(lot_data[key])
        return None
    
    def _extraire_montant_total(self, data: Dict[str, Any]) -> Optional[Decimal]:
        for key in ["montant_total", "total", "montant_ht", "prix_total"]:
            if key in data and data[key] is not None:
                return Decimal(str(data[key]))
        return None
    
    def _verifier_lots_correspondants(self, mission_id: str, cctp_lots: Dict, dpgf_lots: Dict, start_id: int) -> List[Incoherence]:
        incoherences = []
        for lot_nom in sorted(set(cctp_lots.keys()) - set(dpgf_lots.keys())):
            incoherences.append(Incoherence(
                incoherence_id=f"INC-{mission_id}-{start_id + len(incoherences):04d}",
                type_incoherence="lot_manquant",
                niveau="erreur",
                description=f"Lot '{lot_nom}' présent dans CCTP mais absent dans DPGF",
                emplacement="CCTP → DPGF",
                solution_proposee=f"Ajouter le lot '{lot_nom}' dans le DPGF"
            ))
        for lot_nom in sorted(set(dpgf_lots.keys()) - set(cctp_lots.keys())):
            incoherences.append(Incoherence(
                incoherence_id=f"INC-{mission_id}-{start_id + len(incoherences):04d}",
                type_incoherence="lot_supplementaire",
                niveau="erreur",
                description=f"Lot '{lot_nom}' présent dans DPGF mais absent dans CCTP",
                emplacement="DPGF → CCTP",
                solution_proposee=f"Vérifier si le lot '{lot_nom}' doit être dans le CCTP"
            ))
        return incoherences
    
    def _verifier_montants(self, mission_id: str, lot_nom: str, cctp_lot: Dict, dpgf_lot: Dict, start_id: int) -> List[Incoherence]:
        incoherences = []
        cctp_montant = self._extraire_montant(cctp_lot)
        dpgf_montant = self._extraire_montant(dpgf_lot)
        if cctp_montant is None or dpgf_montant is None:
            return incoherences
        ecart_absolu = abs(cctp_montant - dpgf_montant)
        ecart_relatif = ecart_absolu / max(cctp_montant, dpgf_montant, Decimal("1"))
        niveau = "erreur" if ecart_relatif > Decimal("0.10") or ecart_absolu > self.tolerance_absolue else "avertissement" if ecart_relatif > self.tolerance_relative else None
        if niveau:
            incoherences.append(Incoherence(
                incoherence_id=f"INC-{mission_id}-{start_id + len(incoherences):04d}",
                type_incoherence="montant",
                niveau=niveau,
                description=f"Écart de montant pour le lot '{lot_nom}': {float(ecart_absolu):.2f}€ ({float(ecart_relatif*100):.1f}%)",
                emplacement=f"Lot {lot_nom}",
                valeur_cctp=cctp_montant,
                valeur_dpgf=dpgf_montant,
                ecart=ecart_absolu,
                solution_proposee="Vérifier et aligner les montants CCTP/DPGF"
            ))
        return incoherences
    
    def _verifier_quantites(self, mission_id: str, lot_nom: str, cctp_lot: Dict, dpgf_lot: Dict, start_id: int) -> List[Incoherence]:
        incoherences = []
        cctp_qte = self._extraire_quantite(cctp_lot)
        dpgf_qte = self._extraire_quantite(dpgf_lot)
        if cctp_qte is not None and dpgf_qte is not None and cctp_qte != dpgf_qte:
            incoherences.append(Incoherence(
                incoherence_id=f"INC-{mission_id}-{start_id + len(incoherences):04d}",
                type_incoherence="quantite",
                niveau="avertissement",
                description=f"Différence de quantité pour le lot '{lot_nom}': CCTP={cctp_qte}, DPGF={dpgf_qte}",
                emplacement=f"Lot {lot_nom}",
                valeur_cctp=cctp_qte,
                valeur_dpgf=dpgf_qte,
                solution_proposee="Vérifier et aligner les quantités"
            ))
        return incoherences
    
    def _verifier_unites(self, mission_id: str, lot_nom: str, cctp_lot: Dict, dpgf_lot: Dict, start_id: int) -> List[Incoherence]:
        incoherences = []
        cctp_unite = self._extraire_unite(cctp_lot)
        dpgf_unite = self._extraire_unite(dpgf_lot)
        if cctp_unite and dpgf_unite and not self._unites_compatibles(cctp_unite, dpgf_unite):
            incoherences.append(Incoherence(
                incoherence_id=f"INC-{mission_id}-{start_id + len(incoherences):04d}",
                type_incoherence="unite",
                niveau="erreur",
                description=f"Unités différentes pour le lot '{lot_nom}': CCTP={cctp_unite}, DPGF={dpgf_unite}",
                emplacement=f"Lot {lot_nom}",
                solution_proposee="Standardiser les unités entre CCTP et DPGF"
            ))
        return incoherences
    
    def _verifier_global(self, mission_id: str, cctp_data: Dict, dpgf_data: Dict, start_id: int) -> List[Incoherence]:
        incoherences = []
        cctp_total = self._extraire_montant_total(cctp_data)
        dpgf_total = self._extraire_montant_total(dpgf_data)
        if cctp_total is not None and dpgf_total is not None:
            ecart = abs(cctp_total - dpgf_total)
            ecart_relatif = ecart / max(cctp_total, dpgf_total, Decimal("1"))
            if ecart_relatif > Decimal("0.05"):
                incoherences.append(Incoherence(
                    incoherence_id=f"INC-{mission_id}-{start_id + len(incoherences):04d}",
                    type_incoherence="montant_total",
                    niveau="critique" if ecart_relatif > Decimal("0.10") else "erreur",
                    description=f"Écart sur le montant total: CCTP={float(cctp_total):.2f}€ vs DPGF={float(dpgf_total):.2f}€ ({float(ecart_relatif*100):.1f}%)",
                    emplacement="Total global",
                    valeur_cctp=cctp_total,
                    valeur_dpgf=dpgf_total,
                    ecart=ecart,
                    solution_proposee="Recalculer et valider tous les montants"
                ))
        return incoherences
    
    def _unites_compatibles(self, unite1: str, unite2: str) -> bool:
        equivalences = {
            "m": ["m", "metre", "mètre"],
            "m2": ["m2", "m²", "m^2", "metre care", "metre carre"],
            "m3": ["m3", "m³", "m^3", "metre cube", "metre cubique"],
            "kg": ["kg", "kilogramme"],
            "t": ["t", "tonne"],
            "l": ["l", "litre"],
            "u": ["u", "unite", "unité", "unit"],
        }
        u1 = unite1.lower().replace(" ", "").replace("²", "2").replace("³", "3")
        u2 = unite2.lower().replace(" ", "").replace("²", "2").replace("³", "3")
        for variants in equivalences.values():
            if u1 in variants and u2 in variants:
                return True
        return u1 == u2
    
    def _compter_par_type(self, incoherences: List[Incoherence]) -> Dict[str, int]:
        counter = {}
        for inc in incoherences:
            counter[inc.type_incoherence] = counter.get(inc.type_incoherence, 0) + 1
        return counter
    
    def _compter_par_niveau(self, incoherences: List[Incoherence]) -> Dict[str, int]:
        counter = {}
        for inc in incoherences:
            counter[inc.niveau] = counter.get(inc.niveau, 0) + 1
        return counter
    
    def _generer_recommandations(self, incoherences: List[Incoherence], by_niveau: Dict[str, int], score: float) -> List[str]:
        recos = []
        if not incoherences:
            recos.append("✅ Aucune incohérence détectée - CCTP et DPGF sont cohérents")
            return recos
        if by_niveau.get("critique", 0) > 0:
            recos.append("🔴 Incohérences CRITIQUES détectées - Validation manuelle obligatoire")
        if by_niveau.get("erreur", 0) > 0:
            recos.append("⚠️ Incohérences majeures - Corrections nécessaires avant soumission")
        if by_niveau.get("montant", 0) > 0:
            recos.append("Vérifier l'alignement des montants entre CCTP et DPGF")
        if by_niveau.get("quantite", 0) > 0:
            recos.append("Vérifier les quantités et unités dans les deux documents")
        if by_niveau.get("unite", 0) > 0:
            recos.append("Standardiser les unités de mesure entre CCTP et DPGF")
        return recos


solveur_incoherences = IncoherenceSolver()


def detecter_incoherences_cctp_dpgf(mission_id: str, cctp: Dict[str, Any], dpgf: Dict[str, Any]) -> Dict[str, Any]:
    report = solveur_incoherences.detecter_incoherences(mission_id, cctp, dpgf)
    return report.to_dict()


def verifier_coherence_globale(mission_id: str, cctp: Dict[str, Any], dpgf: Dict[str, Any]) -> bool:
    report = solveur_incoherences.detecter_incoherences(mission_id, cctp, dpgf)
    return report.est_coherent

