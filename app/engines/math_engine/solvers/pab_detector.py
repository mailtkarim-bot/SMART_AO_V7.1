"""
SMART_AO V7 - PAB Detector (-20%/-30%)
"""
from decimal import Decimal, getcontext
from datetime import date
from typing import Dict, Any, Optional
from dataclasses import dataclass
from app.engines.math_engine.types import Amount, Penalty, PenaltyType, SolverResult

getcontext().prec = 28

@dataclass
class PABConfig:
    montant_marche_ht: Amount
    date_previsionnelle: date
    date_reelle: Optional[date] = None

class PABDetector:
    JOURS_SEUIL_30PCT = 30
    
    def solve(self, data: Dict[str, Any]) -> SolverResult:
        montant = Amount(value=Decimal(str(data.get('montant_marche_ht', 0))), currency=data.get('currency', 'EUR'))
        
        date_prev = data.get('date_previsionnelle')
        date_reelle = data.get('date_reelle')
        
        if isinstance(date_prev, str):
            date_prev = date.fromisoformat(date_prev)
        if isinstance(date_reelle, str):
            date_reelle = date.fromisoformat(date_reelle)
        
        retard_jours = (date_reelle - date_prev).days if date_prev and date_reelle else 0
        
        penalite_montant = Decimal('0')
        penalty_type = PenaltyType.PAB_20PCT
        
        if retard_jours > 0:
            if retard_jours <= self.JOURS_SEUIL_30PCT:
                penalite_montant = montant.value * Decimal('0.20')
                penalty_type = PenaltyType.PAB_20PCT
            else:
                penalite_montant = montant.value * Decimal('0.30')
                penalty_type = PenaltyType.PAB_30PCT
        
        penalties = [Penalty(penalty_type, Amount(penalite_montant, currency=montant.currency), f"PAB {penalty_type.value}", "RAPPORT §7.19")] if penalite_montant > Decimal('0') else []
        warnings = [f"Retard de {retard_jours} jours"] if retard_jours > 0 else []
        
        return SolverResult("PABDetector", data, Amount(penalite_montant, currency=montant.currency), penalties, warnings, {"retard_jours": retard_jours, "penalty_type": penalty_type.value})
