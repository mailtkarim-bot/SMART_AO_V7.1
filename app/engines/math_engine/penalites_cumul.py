"""
SMART_AO V7 - penalites_cumul.py
===================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - Pénalités Cumul Calculator
==========================================
Calcul déterministe des pénalités CCAG et CCMI.

Règles appliquées (source CCAG Travaux et réforme 2024):
- Pénalité de retard : 1/1000 du montant du marché HT par jour de retard.
- Plafond CCAG : 10% du montant HT pour les marchés signés avant 2024.
- Plafond CCAG (réforme 2024) : 5% du montant HT pour les marchés signés à
  compter du 1er avril 2024.
- Seuil d'application : aucune pénalité si le montant total calculé est
  strictement inférieur à 1 000 €.

Séparation complète IA/Déterministe - ZERO LLM.
Source: ARCHITECTURE_V7_ENGINE.md §4.3 + ADR-046
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import date
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================

class PenaliteType(str, Enum):
    """Type de pénalité"""
    CCAG = "ccag"
    CCMI = "ccmi"
    CONTRAT = "contrat"


class NiveauPenalite(str, Enum):
    """Niveau de gravité de la pénalité"""
    FAIBLE = "FAIBLE"
    MOYEN = "MOYEN"
    ELEVE = "ELEVE"
    CRITIQUE = "CRITIQUE"


# =============================================================================
# CONSTANTES MÉTIERS
# =============================================================================

SEUIL_MINIMAL_PENALITE_EUR = 1000.0  # Seuil légal d'application
TAUX_JOURNALIER_CCAG = 1 / 1000       # 1‰ par jour de retard
PLAFOND_CCAG_AVANT_2024 = 0.10        # 10%
PLAFOND_CCAG_APRES_2024 = 0.05        # 5%
DATE_REFORME_CCAG_2024 = date(2024, 4, 1)


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class PenaliteResult:
    """Résultat du calcul de pénalité"""
    type: PenaliteType
    montant: float
    taux: Optional[float] = None
    base_calcul: float = 0.0
    retard_jours: int = 0
    niveau: NiveauPenalite = NiveauPenalite.FAIBLE
    reference: str = ""
    details: Optional[Dict[str, Any]] = None


@dataclass
class PenaltiesSummary:
    """Résumé des pénalités calculées"""
    penalites: Dict[str, PenaliteResult]
    total_penalites: float
    total_retard_jours: int
    risque_global: NiveauPenalite


# =============================================================================
# CALCULATEUR DE PÉNALITÉS CCAG
# =============================================================================

class CCAGCalculator:
    """
    Calculateur de pénalités selon CCAG Travaux (article 14-1).

    Règles appliquées:
    - 1/1000 du montant HT par jour de retard.
    - Plafond à 10% du montant HT avant le 1er avril 2024.
    - Plafond à 5% du montant HT à compter du 1er avril 2024.
    - Aucune pénalité si le montant total calculé est < 1 000 €.
    """

    @staticmethod
    def _determiner_plafond(date_contrat: Optional[date]) -> float:
        """Choisir le plafond applicable selon la date du contrat."""
        if date_contrat is None:
            # Par défaut : règles les plus récentes (post-2024).
            return PLAFOND_CCAG_APRES_2024
        if date_contrat >= DATE_REFORME_CCAG_2024:
            return PLAFOND_CCAG_APRES_2024
        return PLAFOND_CCAG_AVANT_2024

    @staticmethod
    def calculer(
        montant_marche_ht: float,
        retard_jours: int,
        date_contrat: Optional[date] = None
    ) -> PenaliteResult:
        """
        Calculer la pénalité CCAG.

        Args:
            montant_marche_ht: Montant du marché HT (EUR).
            retard_jours: Nombre de jours de retard (>= 0).
            date_contrat: Date de signature du contrat (optionnelle).

        Returns:
            PenaliteResult: Résultat du calcul.
        """
        retard_jours = max(0, int(retard_jours))

        if retard_jours == 0 or montant_marche_ht <= 0:
            return PenaliteResult(
                type=PenaliteType.CCAG,
                montant=0.0,
                taux=0.0,
                base_calcul=montant_marche_ht,
                retard_jours=retard_jours,
                niveau=NiveauPenalite.FAIBLE,
                reference="CCAG Article 14-1",
                details={"message": "Aucun retard détecté ou montant nul"}
            )

        plafond = CCAGCalculator._determiner_plafond(date_contrat)
        penalite_brute = montant_marche_ht * TAUX_JOURNALIER_CCAG * retard_jours
        penalite_plafonnee = min(penalite_brute, montant_marche_ht * plafond)

        # Seuil minimal légal : aucune pénalité si < 1 000 €
        if penalite_plafonnee < SEUIL_MINIMAL_PENALITE_EUR:
            return PenaliteResult(
                type=PenaliteType.CCAG,
                montant=0.0,
                taux=0.0,
                base_calcul=montant_marche_ht,
                retard_jours=retard_jours,
                niveau=NiveauPenalite.FAIBLE,
                reference="CCAG Article 14-1",
                details={
                    "message": f"Montant calculé ({penalite_plafonnee:.2f} EUR) inférieur au seuil de {SEUIL_MINIMAL_PENALITE_EUR} EUR",
                    "penalite_theorique": penalite_plafonnee,
                    "seuil_minimal": SEUIL_MINIMAL_PENALITE_EUR,
                    "plafond_applicable": plafond,
                }
            )

        ratio = penalite_plafonnee / montant_marche_ht
        if ratio >= plafond * 0.8:
            niveau = NiveauPenalite.CRITIQUE
        elif ratio >= plafond * 0.5:
            niveau = NiveauPenalite.ELEVE
        else:
            niveau = NiveauPenalite.MOYEN

        return PenaliteResult(
            type=PenaliteType.CCAG,
            montant=round(penalite_plafonnee, 2),
            taux=TAUX_JOURNALIER_CCAG,
            base_calcul=montant_marche_ht,
            retard_jours=retard_jours,
            niveau=niveau,
            reference="CCAG Article 14-1",
            details={
                "penalite_brute": round(penalite_brute, 2),
                "penalite_plafonnee": round(penalite_plafonnee, 2),
                "plafond": round(montant_marche_ht * plafond, 2),
                "taux_journalier": TAUX_JOURNALIER_CCAG,
                "plafond_pourcentage": plafond,
                "seuil_minimal": SEUIL_MINIMAL_PENALITE_EUR,
                "date_contrat": date_contrat.isoformat() if date_contrat else None,
            }
        )


# =============================================================================
# CALCULATEUR DE PÉNALITÉS CCMI
# =============================================================================

class CCMICalculator:
    """
    Calculateur de pénalités selon CCMI.

    Règles CCMI (CCH art. L.231-8 / R.231-14):
    - Pénalité minimale légale: 1/3000ᵉ du prix du marché par jour de retard
    - Plafond: 5% du montant du marché (sauf clause contraire)
    """

    @staticmethod
    def calculer(
        retard_jours: int,
        montant_marche_ht: Optional[float] = None
    ) -> PenaliteResult:
        """
        Calculer la pénalité CCMI selon la formule légale (1/3000ᵉ par jour).

        Args:
            retard_jours: Nombre de jours de retard.
            montant_marche_ht: Montant du marché HT (requis pour CCMI).

        Returns:
            PenaliteResult: Résultat du calcul.

        Raises:
            ValueError: Si montant_marche_ht est absent ou nul.
        """
        if not montant_marche_ht or montant_marche_ht <= 0:
            raise ValueError("CCMI: montant_marche_ht requis pour le calcul (1/3000ᵉ du prix)")
        
        retard_jours = max(0, int(retard_jours))
        
        # Formule légale CCMI: 1/3000ᵉ du prix du marché par jour de retard
        from decimal import Decimal, ROUND_HALF_UP
        montant_decimal = Decimal(str(montant_marche_ht))
        penalite_journaliere = (montant_decimal / Decimal(3000)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        penalite_totale = (penalite_journaliere * Decimal(retard_jours)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Plafond légal: 5% du montant du marché
        plafond = (montant_decimal * Decimal('0.05')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        if penalite_totale > plafond:
            penalite_totale = plafond
        
        if retard_jours > 30:
            niveau = NiveauPenalite.CRITIQUE
        elif retard_jours > 20:
            niveau = NiveauPenalite.ELEVE
        elif retard_jours > 10:
            niveau = NiveauPenalite.MOYEN
        else:
            niveau = NiveauPenalite.FAIBLE

        return PenaliteResult(
            type=PenaliteType.CCMI,
            montant=float(penalite_totale),
            base_calcul=montant_marche_ht,
            retard_jours=retard_jours,
            niveau=niveau,
            reference="CCH art. L.231-8 / R.231-14 (1/3000ᵉ par jour, plafonné 5%)",
            details={
                "formule": "1/3000ᵉ du prix du marché par jour de retard",
                "penalite_journaliere": float(penalite_journaliere),
                "plafond_5pct": float(plafond),
                "base_legale": "Code de la Construction et de l'Habitation"
            }
        )


# =============================================================================
# CALCULATEUR DE PÉNALITÉS CONTRAT (PERSONNALISÉES)
# =============================================================================

class ContratPenalitesCalculator:
    """
    Calculateur de pénalités selon les clauses contractuelles personnalisées.

    Attention: une clause contractuelle ne peut pas déroger aux plafonds
    légaux CCAG sans être expressément justifiée.
    """

    @staticmethod
    def calculer(
        montant_marche_ht: float,
        retard_jours: int,
        clause_contrat: Dict[str, Any]
    ) -> PenaliteResult:
        """
        Calculer la pénalité selon une clause contractuelle personnalisée.

        Args:
            montant_marche_ht: Montant du marché HT (EUR).
            retard_jours: Nombre de jours de retard.
            clause_contrat: Clause contractuelle définissant les pénalités.

        Returns:
            PenaliteResult: Résultat du calcul.

        Raises:
            ValueError: Si la clause est invalide.
        """
        taux = clause_contrat.get("taux", 0.01)  # 1% par défaut
        plafond = clause_contrat.get("plafond", None)
        seuil_jours = clause_contrat.get("seuil_jours", 0)
        forfaitaire = clause_contrat.get("forfaitaire", None)
        retard_jours = max(0, int(retard_jours))

        if forfaitaire is not None:
            penalite_montant = float(forfaitaire)
        else:
            penalite_montant = montant_marche_ht * taux * max(0, retard_jours - seuil_jours)

        if plafond is not None:
            penalite_montant = min(penalite_montant, float(plafond))

        if penalite_montant > montant_marche_ht * 0.1:
            niveau = NiveauPenalite.CRITIQUE
        elif penalite_montant > montant_marche_ht * 0.05:
            niveau = NiveauPenalite.ELEVE
        elif penalite_montant > 0:
            niveau = NiveauPenalite.MOYEN
        else:
            niveau = NiveauPenalite.FAIBLE

        return PenaliteResult(
            type=PenaliteType.CONTRAT,
            montant=round(penalite_montant, 2),
            taux=taux,
            base_calcul=montant_marche_ht,
            retard_jours=retard_jours,
            niveau=niveau,
            reference=clause_contrat.get("reference", "Clause contractuelle"),
            details={
                "clause": clause_contrat,
                "taux": taux,
                "plafond": plafond,
                "seuil_jours": seuil_jours
            }
        )


# =============================================================================
# CALCULATEUR PRINCIPAL
# =============================================================================

class PenalitesCalculator:
    """
    Calculateur principal de pénalités.

    Combine CCAG, CCMI et clauses contractuelles.
    """

    def __init__(self):
        self.ccag = CCAGCalculator()
        self.ccmi = CCMICalculator()
        self.contrat = ContratPenalitesCalculator()

    def calculer_toutes(
        self,
        montant_marche_ht: float,
        delai_execution_jours: int,
        delai_reel_jours: int,
        ccag_applicable: bool = True,
        ccmi_applicable: bool = False,
        clause_contrat: Optional[Dict[str, Any]] = None,
        date_contrat: Optional[date] = None
    ) -> PenaltiesSummary:
        """
        Calculer toutes les pénalités applicables.

        Args:
            montant_marche_ht: Montant du marché HT (EUR).
            delai_execution_jours: Délai d'exécution prévu (jours).
            delai_reel_jours: Délai réel (jours).
            ccag_applicable: Si CCAG s'applique.
            ccmi_applicable: Si CCMI s'applique.
            clause_contrat: Clause contractuelle personnalisée (optionnelle).
            date_contrat: Date de signature du contrat (optionnelle).

        Returns:
            PenaltiesSummary: Résumé des pénalités calculées.
        """
        penalites: Dict[str, PenaliteResult] = {}
        total_penalites = 0.0
        total_retard_jours = max(0, delai_reel_jours - delai_execution_jours)

        if ccag_applicable:
            penalite_ccag = self.ccag.calculer(
                montant_marche_ht, total_retard_jours, date_contrat
            )
            penalites["ccag"] = penalite_ccag
            total_penalites += penalite_ccag.montant

        if ccmi_applicable:
            penalite_ccmi = self.ccmi.calculer(total_retard_jours, montant_marche_ht)
            penalites["ccmi"] = penalite_ccmi
            total_penalites += penalite_ccmi.montant

        if clause_contrat:
            penalite_contrat = self.contrat.calculer(
                montant_marche_ht, total_retard_jours, clause_contrat
            )
            penalites["contrat"] = penalite_contrat
            total_penalites += penalite_contrat.montant

        if total_penalites > montant_marche_ht * 0.10:
            risque_global = NiveauPenalite.CRITIQUE
        elif total_penalites > montant_marche_ht * 0.05:
            risque_global = NiveauPenalite.ELEVE
        elif total_penalites > 0:
            risque_global = NiveauPenalite.MOYEN
        else:
            risque_global = NiveauPenalite.FAIBLE

        return PenaltiesSummary(
            penalites=penalites,
            total_penalites=round(total_penalites, 2),
            total_retard_jours=total_retard_jours,
            risque_global=risque_global
        )


# =============================================================================
# UTILITIES
# =============================================================================

def calculer_penalite_ccag(
    montant_marche_ht: float,
    retard_jours: int,
    date_contrat: Optional[date] = None
) -> float:
    """
    Fonction utilitaire pour calculer une pénalité CCAG simple.

    Args:
        montant_marche_ht: Montant du marché HT.
        retard_jours: Nombre de jours de retard.
        date_contrat: Date de signature du contrat (optionnelle).

    Returns:
        float: Montant de la pénalité.
    """
    calculator = CCAGCalculator()
    result = calculator.calculer(montant_marche_ht, retard_jours, date_contrat)
    return result.montant


def calculer_penalite_ccmi(retard_jours: int) -> float:
    """
    Fonction utilitaire pour calculer une pénalité CCMI simple.

    Args:
        retard_jours: Nombre de jours de retard.

    Returns:
        float: Montant de la pénalité.
    """
    calculator = CCMICalculator()
    result = calculator.calculer(retard_jours)
    return result.montant


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

penalites_calculator = PenalitesCalculator()


def get_penalites_calculator() -> PenalitesCalculator:
    """Get the singleton PenalitesCalculator instance"""
    return penalites_calculator
