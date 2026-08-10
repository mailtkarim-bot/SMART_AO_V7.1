"""
SMART_AO V7 - ratios_financiers.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Ratios Financiers
Calcul des ratios financiers clés pour l'analyse BTP
"""
from decimal import Decimal, getcontext
from typing import Dict, Any
from app.engines.math_engine.types import Amount, SolverResult, Currency

getcontext().prec = 28

class Ratiosfinanciers:
    """
    Calcul des ratios financiers pour l'analyse de rentabilité
    
    Ratios calculés:
    - Rentabilité économique = Résultat net / Capitaux propres
    - Rentabilité financière = Résultat net / Capitaux investis
    - Endettement = Dettes / Capitaux propres
    - Autonomie financière = Capitaux propres / Total bilan
    """
    
    def solve(self, data: Dict[str, Any]) -> SolverResult:
        warnings = []
        metadata = {}
        
        try:
            resultat_net = Decimal(str(data.get('resultat_net', 0)))
            capitaux_propres = Decimal(str(data.get('capitaux_propres', 0)))
            dettes = Decimal(str(data.get('dettes', 0)))
            total_bilan = Decimal(str(data.get('total_bilan', 0)))
            capitaux_investis = Decimal(str(data.get('capitaux_investis', 0)))
            
            # Validation
            if capitaux_propres <= 0:
                warnings.append("Capitaux propres doit être supérieur à 0")
                capitaux_propres = Decimal('1')
            if capitaux_investis <= 0:
                capitaux_investis = capitaux_propres
            if total_bilan <= 0:
                total_bilan = capitaux_propres + dettes
            
            # Calcul des ratios
            rentabilite_economique = (resultat_net / capitaux_propres) * 100 if capitaux_propres > 0 else Decimal('0')
            rentabilite_financiere = (resultat_net / capitaux_investis) * 100 if capitaux_investis > 0 else Decimal('0')
            endettement = (dettes / capitaux_propres) * 100 if capitaux_propres > 0 else Decimal('0')
            autonomie = (capitaux_propres / total_bilan) * 100 if total_bilan > 0 else Decimal('0')
            
            # Score global (pondération)
            score = (rentabilite_economique * Decimal('0.4') + 
                    rentabilite_financiere * Decimal('0.3') + 
                    autonomie * Decimal('0.2') - 
                    endettement * Decimal('0.1'))
            
            # Avertissements
            if endettement > Decimal('100'):
                warnings.append("⚠️ Endettement élevé (> 100%)")
            if autonomie < Decimal('30'):
                warnings.append("⚠️ Autonomie financière faible (< 30%)")
            if rentabilite_economique < Decimal('5'):
                warnings.append("⚠️ Rentabilité économique insuffisante (< 5%)")
            
            metadata = {
                'resultat_net': float(resultat_net),
                'capitaux_propres': float(capitaux_propres),
                'dettes': float(dettes),
                'total_bilan': float(total_bilan),
                'capitaux_investis': float(capitaux_investis),
                'rentabilite_economique_pct': float(rentabilite_economique),
                'rentabilite_financiere_pct': float(rentabilite_financiere),
                'endettement_pct': float(endettement),
                'autonomie_pct': float(autonomie),
                'score_global': float(score),
                'calcul_score': f"({rentabilite_economique} * 0.4) + ({rentabilite_financiere} * 0.3) + ({autonomie} * 0.2) - ({endettement} * 0.1)",
                'status': 'calculated'
            }
            
            currency = data.get('currency', 'EUR')
            if isinstance(currency, str):
                currency = Currency[currency.upper()] if currency.upper() in Currency.__members__ else Currency.EUR
            
            return SolverResult(
                solver_name="Ratiosfinanciers",
                input_data=data,
                output=Amount(score, currency=currency),
                penalties=[],
                warnings=warnings,
                metadata=metadata
            )
            
        except Exception as e:
            warnings.append(f"Erreur de calcul: {str(e)}")
            currency = data.get('currency', 'EUR')
            if isinstance(currency, str):
                currency = Currency[currency.upper()] if currency.upper() in Currency.__members__ else Currency.EUR
            return SolverResult(
                solver_name="Ratiosfinanciers",
                input_data=data,
                output=Amount(Decimal('0'), currency=currency),
                penalties=[],
                warnings=warnings,
                metadata={'status': 'error', 'error': str(e)}
            )
