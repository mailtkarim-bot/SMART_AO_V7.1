"""
SMART_AO V7 - materiaux_shield.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Matériaux Shield
"""
from decimal import Decimal, getcontext
from typing import Dict, Any
from app.engines.math_engine.types import Amount, Penalty, PenaltyType, SolverResult

getcontext().prec = 28

class MateriauxShieldSolver:
    def solve(self, data: Dict[str, Any]) -> SolverResult:
        currency = data.get('currency', 'EUR')
        cout_prev = Decimal(str(data.get('cout_previsionnel', 0)))
        cout_reel = Decimal(str(data.get('cout_reel', 0)))
        seuil = Decimal(str(data.get('seuil_protection', 0.10)))
        
        if cout_prev == Decimal('0'):
            variation = Decimal('0')
        else:
            variation = (cout_reel - cout_prev) / cout_prev
        
        bouclier = Decimal('0')
        penalties = []
        warnings = []
        
        if variation > seuil:
            diff = cout_reel - cout_prev
            bouclier = diff - (cout_prev * seuil)
            penalties.append(Penalty(PenaltyType.CCAG_10PCT, Amount(bouclier, currency=currency), f"Bouclier activé (variation: {variation*100}%)", "RAPPORT §7.25"))
            
            if variation > seuil * Decimal('2'):
                warnings.append(f"Variation élevée: {variation*100}% - Risque important")
        
        return SolverResult("MateriauxShieldSolver", data, Amount(bouclier, currency=currency), penalties, warnings, {"variation": str(variation), "seuil_depasse": variation > seuil})
