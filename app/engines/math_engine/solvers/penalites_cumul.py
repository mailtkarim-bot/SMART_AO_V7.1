"""
SMART_AO V7 - penalites_cumul.py (solvers wrapper)
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - Pénalités Cumulées (Solver Wrapper)
==================================================
Wrapper autour du calculateur CCAG/CCMI canonique pour l'interface SolverResult.

Règles appliquées:
- Pénalité de retard : 1/1000 du montant HT par jour de retard.
- Plafond CCAG : 10% avant 2024, 5% à compter du 1er avril 2024.
- Seuil d'application : 1 000 €.
"""
from decimal import Decimal, getcontext
from datetime import date
from typing import Dict, Any, List

from app.engines.math_engine.types import Amount, Penalty, PenaltyType, SolverResult
from app.engines.math_engine.penalites_cumul import (
    CCAGCalculator,
    CCMICalculator,
    SEUIL_MINIMAL_PENALITE_EUR,
)

getcontext().prec = 28


class PenalitesCumulSolver:
    """Solver exposant le calculateur de pénalités via l'interface SolverResult."""

    def solve(self, data: Dict[str, Any]) -> SolverResult:
        montant = Decimal(str(data.get('montant_marche', 0)))
        currency = data.get('currency', 'EUR')
        retards = data.get('retards', [])
        taux = [Decimal(str(t)) for t in data.get('taux', [0.001, 0.001])]
        date_contrat_str = data.get('date_contrat')
        date_contrat = date.fromisoformat(date_contrat_str) if date_contrat_str else None

        total_penalite = Decimal('0')
        penalties: List[Penalty] = []
        warnings: List[str] = []

        for i, retard in enumerate(retards):
            retard = int(retard)
            if retard <= 0:
                continue

            # Le premier élément est traité comme CCAG, les suivants comme CCMI
            # (comportement conservé pour compatibilité d'interface).
            if i == 0:
                result = CCAGCalculator.calculer(float(montant), retard, date_contrat)
                penalty_type = PenaltyType.CCAG_10PCT if result.details.get("plafond_pourcentage") == 0.10 else PenaltyType.CCAG_5PCT
            else:
                result = CCMICalculator.calculer(retard, float(montant))
                penalty_type = PenaltyType.CCMI

            montant_penalite = Decimal(str(result.montant))
            total_penalite += montant_penalite
            penalties.append(Penalty(
                penalty_type=penalty_type,
                amount=Amount(montant_penalite, currency=currency),
                description=f"{result.reference} — {retard} jours de retard",
                reference=result.reference
            ))

        if total_penalite > 0 and total_penalite < Decimal(str(SEUIL_MINIMAL_PENALITE_EUR)):
            warnings.append(
                f"Montant total des pénalités ({total_penalite} EUR) inférieur au seuil légal de {SEUIL_MINIMAL_PENALITE_EUR} EUR"
            )

        return SolverResult(
            solver_name="PenalitesCumulSolver",
            input_data=data,
            output=Amount(total_penalite, currency=currency),
            penalties=penalties,
            warnings=warnings,
            metadata={"count": len(penalties), "seuil_minimal": SEUIL_MINIMAL_PENALITE_EUR}
        )
