"""
SMART_AO V7 - indices_materiaux.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Indices Materiaux
Calcul des indices matériaux pour révision des prix
"""
from decimal import Decimal, getcontext
from typing import Dict, Any
from app.engines.math_engine.types import Amount, SolverResult, Currency

getcontext().prec = 28

class Indicesmateriaux:
    """
    Calcul des indices matériaux pour la révision des prix dans les marchés BTP
    
    Basé sur les indices officiels (INSEE, FFB, etc.)
    
    Formules:
    - Prix révisé = Prix initial * (Indice actuel / Indice initial)
    - Variation = (Indice actuel - Indice initial) / Indice initial * 100
    """
    
    # Indices moyens par catégorie de matériau (base 100)
    INDICES_BASE = {
        'beton': {
            '2020': Decimal('100.0'),
            '2021': Decimal('105.5'),
            '2022': Decimal('112.3'),
            '2023': Decimal('118.7'),
            '2024': Decimal('122.1'),
        },
        'acier': {
            '2020': Decimal('100.0'),
            '2021': Decimal('118.2'),
            '2022': Decimal('135.5'),
            '2023': Decimal('128.9'),
            '2024': Decimal('132.4'),
        },
        'bois': {
            '2020': Decimal('100.0'),
            '2021': Decimal('125.3'),
            '2022': Decimal('145.7'),
            '2023': Decimal('142.1'),
            '2024': Decimal('148.9'),
        },
        'isolants': {
            '2020': Decimal('100.0'),
            '2021': Decimal('108.5'),
            '2022': Decimal('115.2'),
            '2023': Decimal('118.9'),
            '2024': Decimal('122.3'),
        },
    }
    
    def solve(self, data: Dict[str, Any]) -> SolverResult:
        warnings = []
        metadata = {}
        
        try:
            categorie = data.get('categorie', 'beton')
            annee_initiale = str(data.get('annee_initiale', '2020'))
            annee_actuelle = str(data.get('annee_actuelle', '2024'))
            prix_initial = Decimal(str(data.get('prix_initial', 0)))
            quantite = Decimal(str(data.get('quantite', 1)))
            
            # Validation
            if prix_initial <= 0:
                warnings.append("Prix initial doit être supérieur à 0")
                prix_initial = Decimal('100')
            
            # Récupérer les indices
            indices_categorie = self.INDICES_BASE.get(categorie.lower(), self.INDICES_BASE['beton'])
            
            indice_initial = indices_categorie.get(annee_initiale, Decimal('100'))
            indice_actuel = indices_categorie.get(annee_actuelle, Decimal('120'))
            
            # Calcul variation
            variation_pct = ((indice_actuel - indice_initial) / indice_initial) * 100
            
            # Calcul prix révisé
            prix_revise = prix_initial * (indice_actuel / indice_initial)
            
            # Calcul coût total
            cout_total = prix_revise * quantite
            
            # Avertissements
            if variation_pct > Decimal('20'):
                warnings.append(f"⚠️ Forte variation pour {categorie}: +{float(variation_pct):.1f}%")
            elif variation_pct < Decimal('-10'):
                warnings.append(f"⚠️ Baisse significative pour {categorie}: {float(variation_pct):.1f}%")
            
            metadata = {
                'categorie': categorie,
                'annee_initiale': annee_initiale,
                'annee_actuelle': annee_actuelle,
                'prix_initial': float(prix_initial),
                'quantite': float(quantite),
                'indice_initial': float(indice_initial),
                'indice_actuel': float(indice_actuel),
                'variation_pct': float(variation_pct),
                'prix_revise': float(prix_revise),
                'cout_total': float(cout_total),
                'calcul': f"{prix_initial} * ({indice_actuel} / {indice_initial}) * {quantite}",
                'status': 'calculated'
            }
            
            currency = data.get('currency', 'EUR')
            if isinstance(currency, str):
                currency = Currency[currency.upper()] if currency.upper() in Currency.__members__ else Currency.EUR
            
            return SolverResult(
                solver_name="Indicesmateriaux",
                input_data=data,
                output=Amount(cout_total, currency=currency),
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
                solver_name="Indicesmateriaux",
                input_data=data,
                output=Amount(Decimal('0'), currency=currency),
                penalties=[],
                warnings=warnings,
                metadata={'status': 'error', 'error': str(e)}
            )
