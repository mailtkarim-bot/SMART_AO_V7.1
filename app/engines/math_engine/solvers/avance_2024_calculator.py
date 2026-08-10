"""
SMART_AO V7 - avance_2024_calculator.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Avance 2024 Calculator
Calcul des avances et acomptes selon la réglementation 2024
"""
from decimal import Decimal, getcontext
from typing import Dict, Any
from app.engines.math_engine.types import Amount, SolverResult, Currency

getcontext().prec = 28

class Avance2024Calculator:
    """
    Calcul des avances et acomptes pour les marchés publics 2024
    
    Selon le CCAG 2024:
    - Avance forfaitaire: 5% du montant HT pour les marchés de travaux
    - Acomptes mensuels: jusqu'à 95% de l'avancement
    - Solde: 5% à la réception
    """
    
    # Taux selon type de marché
    TAUX_AVANCE = {
        'travaux': Decimal('0.05'),
        'fournitures': Decimal('0.10'),
        'services': Decimal('0.15'),
        'mixte': Decimal('0.08'),
    }
    
    # Plafonds
    PLAFOND_AVANCE = Decimal('500000')  # €
    
    def solve(self, data: Dict[str, Any]) -> SolverResult:
        warnings = []
        metadata = {}
        
        try:
            montant_ht = Decimal(str(data.get('montant_ht', 0)))
            type_marche = data.get('type_marche', 'travaux')
            avancement_pct = Decimal(str(data.get('avancement_pct', 0)))
            
            # Validation
            if montant_ht <= 0:
                warnings.append("Montant HT doit être supérieur à 0")
                montant_ht = Decimal('100000')
            
            if avancement_pct > Decimal('100'):
                avancement_pct = Decimal('100')
                warnings.append("Avancement limité à 100%")
            
            # Calcul taux d'avance
            taux = self.TAUX_AVANCE.get(type_marche.lower(), self.TAUX_AVANCE['travaux'])
            
            # Calcul avance forfaitaire
            avance_forfaitaire = montant_ht * taux
            
            # Plafond
            if avance_forfaitaire > self.PLAFOND_AVANCE:
                avance_forfaitaire = self.PLAFOND_AVANCE
                warnings.append(f"Avance plafonnée à {float(self.PLAFOND_AVANCE):,.2f} €")
            
            # Calcul acompte mensuel
            acompte_mensuel = montant_ht * (avancement_pct / Decimal('100')) * Decimal('0.95')
            
            # Calcul solde
            solde = montant_ht - avance_forfaitaire - acompte_mensuel
            
            # Total versé
            total_verse = avance_forfaitaire + acompte_mensuel
            
            metadata = {
                'montant_ht': float(montant_ht),
                'type_marche': type_marche,
                'taux_avance': float(taux),
                'avancement_pct': float(avancement_pct),
                'avance_forfaitaire': float(avance_forfaitaire),
                'acompte_mensuel': float(acompte_mensuel),
                'solde': float(solde),
                'total_verse': float(total_verse),
                'plafond_atteint': avance_forfaitaire == self.PLAFOND_AVANCE,
                'calcul': f"Avance: {montant_ht} * {taux}, Acompte: {montant_ht} * ({avancement_pct}/100) * 0.95",
                'status': 'calculated'
            }
            
            # Avertissements
            if solde < 0:
                warnings.append("⚠️ Le solde est négatif - vérifiez l'avancement")
            
            currency = data.get('currency', 'EUR')
            if isinstance(currency, str):
                currency = Currency[currency.upper()] if currency.upper() in Currency.__members__ else Currency.EUR
            
            return SolverResult(
                solver_name="Avance2024Calculator",
                input_data=data,
                output=Amount(total_verse, currency=currency),
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
                solver_name="Avance2024Calculator",
                input_data=data,
                output=Amount(Decimal('0'), currency=currency),
                penalties=[],
                warnings=warnings,
                metadata={'status': 'error', 'error': str(e)}
            )
