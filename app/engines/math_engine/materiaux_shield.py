"""
SMART_AO V7 - materiaux_shield.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Protection des Matériaux - Optimisation et protection contre les risques matériaux
Source: ARCHITECTURE_V7_ENGINE.md §3.4
"""

from typing import Dict, List, Optional, Any, Set, Tuple
from decimal import Decimal, getcontext
from dataclasses import dataclass, field
import logging

from app.engines.math_engine.decimal_ops import DecimalOps

getcontext().prec = 28
logger = logging.getLogger(__name__)


@dataclass
class Materiau:
    nom: str
    code: str
    categorie: str
    cout_unitaire: Decimal
    unite: str = "m3"
    impact_carbone: Decimal = Decimal("0")
    durabilite: int = 50
    resistance: str = "standard"
    disponibilite: str = "bonne"
    risques: List[str] = field(default_factory=list)


@dataclass
class MateriauRisque:
    risque_id: str
    materiau_code: str
    type_risque: str
    description: str
    niveau: str = "moyen"
    probabilite: float = 0.5
    impact_potentiel: Decimal = Decimal("0")
    mitigation: Optional[str] = None


@dataclass
class MateriauAlternative:
    materiau_original: str
    alternative: Materiau
    cout_relatif: float
    impact_carbone_relatif: float
    justification: str


@dataclass
class ShieldResult:
    mission_id: str
    materiaux_analyses: List[Materiau]
    risques_identifies: List[MateriauRisque]
    alternatives_proposees: List[MateriauAlternative]
    score_protection: float
    niveau_global: str
    recommandations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "materiaux_analyses": [{"nom": m.nom, "code": m.code, "categorie": m.categorie, "cout_unitaire": float(m.cout_unitaire), "unite": m.unite, "impact_carbone": float(m.impact_carbone), "risques": m.risques} for m in self.materiaux_analyses],
            "risques_identifies": [{"risque_id": r.risque_id, "materiau_code": r.materiau_code, "type_risque": r.type_risque, "niveau": r.niveau, "description": r.description, "mitigation": r.mitigation} for r in self.risques_identifies],
            "alternatives_proposees": [{"original": a.materiau_original, "alternative": a.alternative.nom, "cout_relatif": a.cout_relatif, "impact_carbone_relatif": a.impact_carbone_relatif, "justification": a.justification} for a in self.alternatives_proposees],
            "score_protection": self.score_protection,
            "niveau_global": self.niveau_global,
            "recommandations": self.recommandations
        }


class MateriauxShield:
    def __init__(self):
        self.base_materiaux = {
            "BETON_C25": Materiau(nom="Béton C25/30", code="BETON_C25", categorie="beton", cout_unitaire=Decimal("120"), unite="m3", impact_carbone=Decimal("250"), durabilite=100, resistance="elevee", disponibilite="bonne"),
            "ACIER_S235": Materiau(nom="Acier S235", code="ACIER_S235", categorie="acier", cout_unitaire=Decimal("800"), unite="kg", impact_carbone=Decimal("1.8"), durabilite=50, resistance="elevee", disponibilite="moyenne", risques=["penurie", "cout_volatil"]),
            "BOIS_LAM": Materiau(nom="Bois lamellé-collé", code="BOIS_LAM", categorie="bois", cout_unitaire=Decimal("600"), unite="m3", impact_carbone=Decimal("50"), durabilite=80, resistance="standard", disponibilite="bonne", risques=["disponibilite_regionale"]),
            "LAINE_MINERALE": Materiau(nom="Laine minérale", code="LAINE_MINERALE", categorie="isolation", cout_unitaire=Decimal("15"), unite="m2", impact_carbone=Decimal("1.5"), durabilite=40, resistance="standard", disponibilite="bonne")
        }
        self.base_risques = [
            MateriauRisque(risque_id="RISQUE_ACIER_PENURIE_2026", materiau_code="ACIER_S235", type_risque="penurie", niveau="eleve", description="Risque de pénurie d'acier en 2026-2027", probabilite=0.7, impact_potentiel=Decimal("50000"), mitigation="Contrats longs termes avec fournisseurs"),
            MateriauRisque(risque_id="RISQUE_ACIER_COUT_2026", materiau_code="ACIER_S235", type_risque="cout_volatil", niveau="eleve", description="Volatilité des prix de l'acier (+20% possible)", probabilite=0.6, impact_potentiel=Decimal("30000"), mitigation="Achats groupés"),
            MateriauRisque(risque_id="RISQUE_BETON_REGLEMENTAIRE", materiau_code="BETON_C25", type_risque="reglementaire", niveau="moyen", description="Évolution possible des normes RE2020", probabilite=0.4, impact_potentiel=Decimal("10000"), mitigation="Veille réglementaire")
        ]
        self.base_alternatives = [
            MateriauAlternative(materiau_original="ACIER_S235", alternative=Materiau(nom="Bois CLT", code="BOIS_CLT", categorie="bois", cout_unitaire=Decimal("700"), unite="m3", impact_carbone=Decimal("40"), durabilite=80, resistance="elevee", disponibilite="bonne"), cout_relatif=-0.15, impact_carbone_relatif=-0.90, justification="Alternative bas-carbone"),
            MateriauAlternative(materiau_original="BETON_C25", alternative=Materiau(nom="Béton bas carbone", code="BETON_BAS_C", categorie="beton", cout_unitaire=Decimal("150"), unite="m3", impact_carbone=Decimal("120"), durabilite=100, resistance="elevee", disponibilite="moyenne"), cout_relatif=+0.25, impact_carbone_relatif=-0.52, justification="Réduction 52% carbone")
        ]
    
    def analyser_materiaux(self, mission_id: str, materiaux_projet: List[Dict[str, Any]]) -> ShieldResult:
        materiaux_analyses = []
        risques_identifies = []
        alternatives_proposees = []
        
        for mat_data in materiaux_projet:
            code = mat_data.get("code", "")
            if code in self.base_materiaux:
                mat_base = self.base_materiaux[code]
                mat_analyse = Materiau(nom=mat_base.nom, code=mat_base.code, categorie=mat_base.categorie, cout_unitaire=mat_base.cout_unitaire, unite=mat_base.unite, impact_carbone=mat_base.impact_carbone, durabilite=mat_base.durabilite, resistance=mat_base.resistance, disponibilite=mat_base.disponibilite, risques=mat_base.risques.copy())
                materiaux_analyses.append(mat_analyse)
                for risque in self.base_risques:
                    if risque.materiau_code == code:
                        risques_identifies.append(risque)
                for alt in self.base_alternatives:
                    if alt.materiau_original == code:
                        alternatives_proposees.append(alt)
        
        score = 1.0
        for risque in risques_identifies:
            penalite = {"critique": 0.4, "eleve": 0.25, "moyen": 0.15, "faible": 0.05}.get(risque.niveau, 0.1)
            score -= penalite * risque.probabilite
        for mat in materiaux_analyses:
            if mat.disponibilite in ["faible", "moyenne"]:
                score -= 0.05
            if "penurie" in mat.risques or "cout_volatil" in mat.risques:
                score -= 0.1
        if alternatives_proposees:
            score += 0.05
        score = max(0.0, min(1.0, score))
        
        niveau_global = "excellent" if score >= 0.9 else "bon" if score >= 0.7 else "moyen" if score >= 0.5 else "faible"
        recommandations = self._generer_recommandations(risques_identifies, alternatives_proposees, score)
        
        return ShieldResult(mission_id=mission_id, materiaux_analyses=materiaux_analyses, risques_identifies=risques_identifies, alternatives_proposees=alternatives_proposees, score_protection=round(score, 2), niveau_global=niveau_global, recommandations=recommandations)
    
    def calculer_cout_carbone_total(self, materiaux: List[Dict[str, Any]]) -> Tuple[Decimal, Decimal]:
        cout_total = Decimal("0")
        impact_total = Decimal("0")
        for mat_data in materiaux:
            code = mat_data.get("code", "")
            quantite = Decimal(str(mat_data.get("quantite", 0)))
            if code in self.base_materiaux:
                mat = self.base_materiaux[code]
                cout_total += mat.cout_unitaire * quantite
                impact_total += mat.impact_carbone * quantite
        return cout_total, impact_total
    
    def _generer_recommandations(self, risques: List[MateriauRisque], alternatives: List[MateriauAlternative], score: float) -> List[str]:
        recos = []
        if not risques and score >= 0.9:
            recos.append("✅ Choix de matériaux optimaux - aucun risque majeur identifié")
            return recos
        for risque in sorted(risques, key=lambda x: {"critique": 0, "eleve": 1, "moyen": 2, "faible": 3}.get(x.niveau, 4)):
            if risque.niveau in ["critique", "eleve"]:
                recos.append(f"🔴 {risque.type_risque.upper()} pour {risque.materiau_code}: {risque.description}")
                if risque.mitigation:
                    recos.append(f"   → Mitigation: {risque.mitigation}")
        if alternatives:
            recos.append("✨ Alternatives disponibles:")
            for alt in alternatives[:3]:
                cout_sign = "+" if alt.cout_relatif > 0 else ""
                carbone_sign = "+" if alt.impact_carbone_relatif > 0 else ""
                recos.append(f"   - {alt.materiau_original} → {alt.alternative.nom}: Coût {cout_sign}{alt.cout_relatif*100:.0f}%, Carbone {carbone_sign}{alt.impact_carbone_relatif*100:.0f}%")
        if score < 0.5:
            recos.append("🔴 Score de protection faible - audit complet recommandé")
        elif score < 0.7:
            recos.append("⚠️ Score de protection moyen - améliorations nécessaires")
        return recos


shield = MateriauxShield()


def analyser_protection_materiaux(mission_id: str, materiaux: List[Dict[str, Any]]) -> Dict[str, Any]:
    result = shield.analyser_materiaux(mission_id, materiaux)
    return result.to_dict()


def calculer_cout_carbone(materiaux: List[Dict[str, Any]]) -> Dict[str, Any]:
    cout, carbone = shield.calculer_cout_carbone_total(materiaux)
    return {"cout_total": float(cout), "carbone_total": float(carbone)}


