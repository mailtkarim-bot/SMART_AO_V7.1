"""
SMART_AO V7 - jurisprudence_contentieux.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Jurisprudence Contentieux
Calcul des provisions pour contentieux basé sur la jurisprudence
"""
from decimal import Decimal, getcontext
from typing import Dict, Any
from app.engines.math_engine.types import Amount, SolverResult, Currency, Penalty, PenaltyType

getcontext().prec = 28

class Jurisprudencecontentieux:
    """
    Calcul des provisions pour contentieux basé sur l'historique et la jurisprudence
    
    Formules:
    - Risque contentieux = Montant AO * Taux de risque * Coefficient jurisprudence
    - Taux de risque selon type de marché (0.02 à 0.15)
    - Coefficient basé sur l'historique des contentieux de l'entreprise
    """
    
    # Taux de risque par type de marché
    TAUX_RISQUE = {
        'travaux': Decimal('0.05'),
        'conception_realisation': Decimal('0.08'),
        'public': Decimal('0.10'),
        'prive': Decimal('0.03'),
        'mixte': Decimal('0.06'),
    }
    
    # Coefficient jurisprudence (0.8 à 1.5)
    COEFF_JURISPRUDENCE = {
        'faible': Decimal('0.8'),
        'moyen': Decimal('1.0'),
        'eleve': Decimal('1.2'),
        'tres_eleve': Decimal('1.5'),
    }
    
    def solve(self, data: Dict[str, Any]) -> SolverResult:
        warnings = []
        penalties = []
        metadata = {}
        
        try:
            montant_ao = Decimal(str(data.get('montant_ao', 0)))
            type_marche = data.get('type_marche', 'travaux')
            niveau_jurisprudence = data.get('niveau_jurisprudence', 'moyen')
            historique_contentieux = data.get('historique_contentieux', 0)
            
            # Validation
            if montant_ao <= 0:
                warnings.append("Montant AO doit être supérieur à 0")
                montant_ao = Decimal('100000')
            
            # Calcul taux de risque
            taux = self.TAUX_RISQUE.get(type_marche.lower(), self.TAUX_RISQUE['travaux'])
            
            # Calcul coefficient jurisprudence
            coeff = self.COEFF_JURISPRUDENCE.get(niveau_jurisprudence.lower(), self.COEFF_JURISPRUDENCE['moyen'])
            
            # Ajustement basé sur historique
            if historique_contentieux > 5:
                coeff *= Decimal('1.3')
                warnings.append(f"Historique contentieux élevé ({historique_contentieux}) - majoration appliquée")
            elif historique_contentieux == 0:
                coeff *= Decimal('0.9')
            
            # Calcul provision
            provision = montant_ao * taux * coeff
            
            # Déterminer type de pénalité
            if provision > montant_ao * Decimal('0.10'):
                penalty_type = PenaltyType.CCAG_10PCT
            elif provision > montant_ao * Decimal('0.05'):
                penalty_type = PenaltyType.CCAG_5PCT
            else:
                penalty_type = PenaltyType.CCMI
            
            penalties.append(Penalty(
                penalty_type=penalty_type,
                amount=Amount(provision * Decimal('0.1'), currency=Currency.EUR),
                description=f"Provision contentieux basée sur jurisprudence {niveau_jurisprudence}",
                reference=f"JUR-{type_marche}-{niveau_jurisprudence}"
            ))
            
            metadata = {
                'montant_ao': float(montant_ao),
                'type_marche': type_marche,
                'niveau_jurisprudence': niveau_jurisprudence,
                'taux_risque': float(taux),
                'coeff_jurisprudence': float(coeff),
                'provision_calculee': float(provision),
                'historique_contentieux': historique_contentieux,
                'calcul': f"{montant_ao} * {taux} * {coeff}",
                'status': 'calculated'
            }
            
            currency = data.get('currency', 'EUR')
            if isinstance(currency, str):
                currency = Currency[currency.upper()] if currency.upper() in Currency.__members__ else Currency.EUR
            
            return SolverResult(
                solver_name="Jurisprudencecontentieux",
                input_data=data,
                output=Amount(provision, currency=currency),
                penalties=penalties,
                warnings=warnings,
                metadata=metadata
            )
            
        except Exception as e:
            warnings.append(f"Erreur de calcul: {str(e)}")
            currency = data.get('currency', 'EUR')
            if isinstance(currency, str):
                currency = Currency[currency.upper()] if currency.upper() in Currency.__members__ else Currency.EUR
            return SolverResult(
                solver_name="Jurisprudencecontentieux",
                input_data=data,
                output=Amount(Decimal('0'), currency=currency),
                penalties=[],
                warnings=warnings,
                metadata={'status': 'error', 'error': str(e)}
            )
