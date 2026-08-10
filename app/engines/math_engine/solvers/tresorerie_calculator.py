"""
SMART_AO V7 - tresorerie_calculator.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Tresorerie Calculator
Calcul de trésorerie et BFR (Besoin en Fonds de Roulement)
"""
from decimal import Decimal, getcontext
from typing import Dict, Any
from app.engines.math_engine.types import Amount, SolverResult, Currency

getcontext().prec = 28

class Tresoreriecalculator:
    """
    Calcul de trésorerie et BFR pour les chantiers BTP
    
    Formules:
    - BFR = (Stocks + Créances clients) - Dettes fournisseurs
    - Trésorerie nette = Trésorerie disponible - BFR
    - Ratio de liquidité = Trésorerie / Passif courant
    """
    
    def solve(self, data: Dict[str, Any]) -> SolverResult:
        warnings = []
        metadata = {}
        
        try:
            # Extraire les données financières
            stocks = Decimal(str(data.get('stocks', 0)))
            creances_clients = Decimal(str(data.get('creances_clients', 0)))
            dettes_fournisseurs = Decimal(str(data.get('dettes_fournisseurs', 0)))
            tresorerie_dispo = Decimal(str(data.get('tresorerie_disponible', 0)))
            passif_courant = Decimal(str(data.get('passif_courant', 0)))
            
            # Validation
            if passif_courant <= 0:
                warnings.append("Passif courant doit être supérieur à 0")
                passif_courant = Decimal('1')
            
            # Calcul BFR
            bfr = (stocks + creances_clients) - dettes_fournisseurs
            
            # Calcul trésorerie nette
            tresorerie_nette = tresorerie_dispo - bfr
            
            # Ratio de liquidité
            ratio_liquidite = tresorerie_dispo / passif_courant if passif_courant > 0 else Decimal('0')
            
            # Solvabilité à court terme
            if ratio_liquidite < Decimal('0.5'):
                warnings.append("⚠️ Ratio de liquidité critique (< 0.5)")
            elif ratio_liquidite < Decimal('1.0'):
                warnings.append("⚠️ Ratio de liquidité faible (< 1.0)")
            
            metadata = {
                'stocks': float(stocks),
                'creances_clients': float(creances_clients),
                'dettes_fournisseurs': float(dettes_fournisseurs),
                'tresorerie_disponible': float(tresorerie_dispo),
                'passif_courant': float(passif_courant),
                'bfr': float(bfr),
                'tresorerie_nette': float(tresorerie_nette),
                'ratio_liquidite': float(ratio_liquidite),
                'calcul_bfr': f"({stocks} + {creances_clients}) - {dettes_fournisseurs}",
                'calcul_tresorerie_nette': f"{tresorerie_dispo} - {bfr}",
                'calcul_ratio': f"{tresorerie_dispo} / {passif_courant}",
                'status': 'calculated'
            }
            
            currency = data.get('currency', 'EUR')
            if isinstance(currency, str):
                currency = Currency[currency.upper()] if currency.upper() in Currency.__members__ else Currency.EUR
            
            return SolverResult(
                solver_name="Tresoreriecalculator",
                input_data=data,
                output=Amount(tresorerie_nette, currency=currency),
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
                solver_name="Tresoreriecalculator",
                input_data=data,
                output=Amount(Decimal('0'), currency=currency),
                penalties=[],
                warnings=warnings,
                metadata={'status': 'error', 'error': str(e)}
            )
