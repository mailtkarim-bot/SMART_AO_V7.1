"""
SMART_AO V7 - Pénalités Cumulées
"""
from decimal import Decimal, getcontext
from typing import List, Dict, Any
from app.engines.math_engine.types import Amount, Penalty, PenaltyType, SolverResult

getcontext().prec = 28

class PenalitesCumulSolver:
    def solve(self, data: Dict[str, Any]) -> SolverResult:
        montant = Amount(value=Decimal(str(data.get('montant_marche', 0))), currency=data.get('currency', 'EUR'))
        retards = data.get('retards', [])
        taux = [Decimal(str(t)) for t in data.get('taux', [0.10, 0.05])]
        
        total_penalite = Decimal('0')
        penalties = []
        
        for i, (retard, taux_val) in enumerate(zip(retards, taux)):
            if retard > 0:
                penalite = montant.value * taux_val * Decimal(retard)
                total_penalite += penalite
                penalty_type = PenaltyType.CCAG_10PCT if i == 0 else PenaltyType.CCAG_5PCT
                penalties.append(Penalty(penalty_type, Amount(penalite, currency=montant.currency), f"Pénalité {taux_val*100}% pour {retard} jours", "RAPPORT §7.2"))
        
        return SolverResult("PenalitesCumulSolver", data, Amount(total_penalite, currency=montant.currency), penalties, [], {"count": len([r for r in retards if r > 0])})
