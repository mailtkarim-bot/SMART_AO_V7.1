"""
SMART_AO V7 - seuil_eplusc.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Seuil E+C-
Calcul des seuils pour la réglementation Environnementale (E+C-)
"""
from decimal import Decimal, getcontext
from typing import Dict, Any
from app.engines.math_engine.types import Amount, SolverResult, Currency, Penalty, PenaltyType

getcontext().prec = 28

class Seuileplusc:
    """
    Calcul des seuils et conformité pour la réglementation E+C- (Énergie-Carbone)
    
    La réglementation E+C- fixée des seuils minimaux pour:
    - Besoin bioclimatique (Bbes)
    - Consommation d'énergie non renouvelable (Cepnr)
    - Impact carbone (Ic)
    
    Niveaux: E+C- (2020), RE2020
    """
    
    # Seuils RE2020 pour les bâtiments résidentiels (kWhEP/m²/an)
    SEUILS_RE2020 = {
        'maison': {
            'bbes_max': Decimal('650'),
            'cepnr_max': Decimal('100'),
            'ic_max': Decimal('600'),
        },
        'collectif': {
            'bbes_max': Decimal('750'),
            'cepnr_max': Decimal('120'),
            'ic_max': Decimal('550'),
        },
        'bureau': {
            'bbes_max': Decimal('800'),
            'cepnr_max': Decimal('130'),
            'ic_max': Decimal('700'),
        },
    }
    
    # Seuils E+C- (niveau E4C1 minimum)
    SEUILS_EPLUSC = {
        'maison': {
            'bbes_max': Decimal('600'),
            'cepnr_max': Decimal('50'),
            'ic_max': Decimal('800'),
        },
        'collectif': {
            'bbes_max': Decimal('700'),
            'cepnr_max': Decimal('65'),
            'ic_max': Decimal('750'),
        },
        'bureau': {
            'bbes_max': Decimal('750'),
            'cepnr_max': Decimal('80'),
            'ic_max': Decimal('850'),
        },
    }
    
    # Pénalités pour non-conformité
    PENALITES_NON_CONFORMITE = {
        'bbes': Decimal('5000'),  # €/m²
        'cepnr': Decimal('3000'),  # €/m²
        'ic': Decimal('2000'),  # €/m²
    }
    
    def solve(self, data: Dict[str, Any]) -> SolverResult:
        warnings = []
        penalties = []
        metadata = {}
        
        try:
            type_batiment = data.get('type_batiment', 'maison')
            surface = Decimal(str(data.get('surface_m2', 100)))
            bbes_actuel = Decimal(str(data.get('bbes', 0)))
            cepnr_actuel = Decimal(str(data.get('cepnr', 0)))
            ic_actuel = Decimal(str(data.get('ic', 0)))
            regulation = data.get('regulation', 'RE2020')
            
            # Validation
            if surface <= 0:
                warnings.append("Surface doit être supérieure à 0")
                surface = Decimal('100')
            
            # Sélection des seuils
            if regulation.upper() == 'E+C-' or regulation.upper() == 'EPLUSC':
                seuils = self.SEUILS_EPLUSC.get(type_batiment.lower(), self.SEUILS_EPLUSC['maison'])
            else:
                seuils = self.SEUILS_RE2020.get(type_batiment.lower(), self.SEUILS_RE2020['maison'])
            
            # Vérification conformité
            conforme = True
            
            if bbes_actuel > seuils['bbes_max']:
                warnings.append(f"⚠️ Bbes dépassé: {float(bbes_actuel)} > {float(seuils['bbes_max'])}")
                conforme = False
                penalties.append(Penalty(
                    penalty_type=PenaltyType.CCAG_10PCT,
                    amount=Amount(surface * self.PENALITES_NON_CONFORMITE['bbes'], currency=Currency.EUR),
                    description=f"Dépassement Bbes de {float(bbes_actuel - seuils['bbes_max']):.1f}",
                    reference=f"E+C-{regulation}-BBES"
                ))
            
            if cepnr_actuel > seuils['cepnr_max']:
                warnings.append(f"⚠️ Cepnr dépassé: {float(cepnr_actuel)} > {float(seuils['cepnr_max'])}")
                conforme = False
                penalties.append(Penalty(
                    penalty_type=PenaltyType.CCAG_5PCT,
                    amount=Amount(surface * self.PENALITES_NON_CONFORMITE['cepnr'], currency=Currency.EUR),
                    description=f"Dépassement Cepnr de {float(cepnr_actuel - seuils['cepnr_max']):.1f}",
                    reference=f"E+C-{regulation}-CEPNR"
                ))
            
            if ic_actuel > seuils['ic_max']:
                warnings.append(f"⚠️ Ic dépassé: {float(ic_actuel)} > {float(seuils['ic_max'])}")
                conforme = False
                penalties.append(Penalty(
                    penalty_type=PenaltyType.CCMI,
                    amount=Amount(surface * self.PENALITES_NON_CONFORMITE['ic'], currency=Currency.EUR),
                    description=f"Dépassement Ic de {float(ic_actuel - seuils['ic_max']):.1f}",
                    reference=f"E+C-{regulation}-IC"
                ))
            
            # Calcul score performance
            if conforme:
                score = Decimal('100')
                warnings.append("✅ Conforme à la réglementation")
            else:
                # Score dégradé proportionnellement aux dépassements
                penalty_bbes = max(Decimal('0'), (bbes_actuel - seuils['bbes_max']) / seuils['bbes_max'])
                penalty_cepnr = max(Decimal('0'), (cepnr_actuel - seuils['cepnr_max']) / seuils['cepnr_max'])
                penalty_ic = max(Decimal('0'), (ic_actuel - seuils['ic_max']) / seuils['ic_max'])
                score = Decimal('100') - (penalty_bbes * Decimal('40') + penalty_cepnr * Decimal('30') + penalty_ic * Decimal('30'))
            
            # Calcul coût pénalités total
            total_penalites = sum(p.amount.value for p in penalties)
            
            metadata = {
                'type_batiment': type_batiment,
                'surface_m2': float(surface),
                'regulation': regulation,
                'bbes_actuel': float(bbes_actuel),
                'cepnr_actuel': float(cepnr_actuel),
                'ic_actuel': float(ic_actuel),
                'seuils': {
                    'bbes_max': float(seuils['bbes_max']),
                    'cepnr_max': float(seuils['cepnr_max']),
                    'ic_max': float(seuils['ic_max']),
                },
                'conforme': conforme,
                'score_performance': float(score),
                'total_penalites': float(total_penalites),
                'calcul_score': f"100 - (penalités Bbes, Cepnr, Ic pondérées)",
                'status': 'calculated'
            }
            
            currency = data.get('currency', 'EUR')
            if isinstance(currency, str):
                currency = Currency[currency.upper()] if currency.upper() in Currency.__members__ else Currency.EUR
            
            return SolverResult(
                solver_name="Seuileplusc",
                input_data=data,
                output=Amount(score, currency=currency),
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
                solver_name="Seuileplusc",
                input_data=data,
                output=Amount(Decimal('0'), currency=currency),
                penalties=[],
                warnings=warnings,
                metadata={'status': 'error', 'error': str(e)}
            )
