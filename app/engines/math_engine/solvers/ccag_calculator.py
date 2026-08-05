"""
SMART_AO V7 - CCAG Calculator (10%/5%/CCMI)
"""
from decimal import Decimal, getcontext
from typing import Dict, Any, Optional
from dataclasses import dataclass
from app.engines.math_engine.types import Amount, Penalty, PenaltyType, SolverResult

getcontext().prec = 28

@dataclass
class CCAGConfig:
    montant_marche_ht: Amount
    delai_execution_jours: int

class CCAGCalculator:
    SEUIL_1000_EURO = Amount(value=Decimal('1000'), currency='EUR')
    
    def __init__(self, config: Optional[CCAGConfig] = None):
        self.config = config
    
    def solve(self, data: Dict[str, Any]) -> SolverResult:
        config = CCAGConfig(
            montant_marche_ht=Amount(
                value=Decimal(str(data.get('montant_marche_ht', 0))),
                currency=data.get('currency', 'EUR')
            ),
            delai_execution_jours=int(data.get('delai_execution_jours', 0)),
        )
        retard_jours = int(data.get('retard_jours', 0))
        
        montant = config.montant_marche_ht.value
        delai = Decimal(config.delai_execution_jours)
        
        penalite_10pct = (montant * Decimal('0.10')) * (Decimal(retard_jours) / delai) if delai > 0 else Decimal('0')
        penalite_5pct = (montant * Decimal('0.05')) * (Decimal(retard_jours) / delai) if delai > 0 else Decimal('0')
        total_penalite = Amount(value=penalite_10pct + penalite_5pct, currency=config.montant_marche_ht.currency)
        
        penalties = []
        if penalite_10pct > Decimal('0'):
            penalties.append(Penalty(PenaltyType.CCAG_10PCT, Amount(penalite_10pct, currency=config.montant_marche_ht.currency), "CCAG 10%", "RAPPORT §7.2"))
        if penalite_5pct > Decimal('0'):
            penalties.append(Penalty(PenaltyType.CCAG_5PCT, Amount(penalite_5pct, currency=config.montant_marche_ht.currency), "CCAG 5%", "RAPPORT §7.2"))
        
        return SolverResult("CCAGCalculator", data, total_penalite, penalties, [], {"seuil_1000e": total_penalite.value > self.SEUIL_1000_EURO.value})
