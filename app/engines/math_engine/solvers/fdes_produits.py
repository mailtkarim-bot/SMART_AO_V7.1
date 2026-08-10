"""
SMART_AO V7 - fdes_produits.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Fdes Produits
Calcul des frais de déblaiement et d'évacuation des produits de démolition
"""
from decimal import Decimal, getcontext
from typing import Dict, Any
from app.engines.math_engine.types import Amount, SolverResult, Currency

getcontext().prec = 28

class Fdesproduits:
    """
    Calcul des Frais de Déblaiement et d'Évacuation des produits (FDES)
    
    Formules:
    - FDES = Volume * Coefficient * Distance * Majorations
    - Coefficient selon nature des produits (béton, bois, métaux, etc.)
    - Majorations pour site urbain, accès difficile, etc.
    """
    
    # Coefficients moyens par type de matériau (€/tonne)
    COEFF_MATERIAUX = {
        'beton': Decimal('25.50'),
        'bois': Decimal('45.00'),
        'metaux': Decimal('85.00'),
        'platre': Decimal('35.00'),
        'melange': Decimal('38.00'),
    }
    
    # Majorations selon conditions de site
    MAJORATIONS = {
        'urbain': Decimal('1.25'),
        'peripherique': Decimal('1.10'),
        'rural': Decimal('1.00'),
        'acces_difficile': Decimal('1.40'),
    }
    
    # Coût transport par km (€/tonne/km)
    COUT_TRANSPORT = Decimal('0.15')
    
    def solve(self, data: Dict[str, Any]) -> SolverResult:
        warnings = []
        metadata = {}
        
        try:
            # Extraire les paramètres
            volume_tonnes = Decimal(str(data.get('volume_tonnes', 0)))
            type_materiaux = data.get('type_materiaux', 'melange')
            distance_km = Decimal(str(data.get('distance_km', 50)))
            conditions_site = data.get('conditions_site', 'peripherique')
            
            # Validation
            if volume_tonnes <= 0:
                warnings.append("Volume doit être supérieur à 0")
                volume_tonnes = Decimal('1')
            
            # Calcul coefficient matériau
            coeff = self.COEFF_MATERIAUX.get(type_materiaux.lower(), self.COEFF_MATERIAUX['melange'])
            
            # Calcul majoration
            majoration = self.MAJORATIONS.get(conditions_site.lower(), Decimal('1.00'))
            
            # Calcul coût de base
            cout_base = volume_tonnes * coeff * majoration
            
            # Calcul coût transport
            cout_transport = volume_tonnes * distance_km * self.COUT_TRANSPORT
            
            # Total FDES
            total = cout_base + cout_transport
            
            # Metadata avec détails
            metadata = {
                'volume_tonnes': float(volume_tonnes),
                'type_materiaux': type_materiaux,
                'distance_km': float(distance_km),
                'conditions_site': conditions_site,
                'coeff_materiaux': float(coeff),
                'majoration': float(majoration),
                'cout_base': float(cout_base),
                'cout_transport': float(cout_transport),
                'calcul': f"({volume_tonnes} * {coeff} * {majoration}) + ({volume_tonnes} * {distance_km} * 0.15)",
                'status': 'calculated'
            }
            
            currency = data.get('currency', 'EUR')
            if isinstance(currency, str):
                currency = Currency[currency.upper()] if currency.upper() in Currency.__members__ else Currency.EUR
            
            return SolverResult(
                solver_name="Fdesproduits",
                input_data=data,
                output=Amount(total, currency=currency),
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
                solver_name="Fdesproduits",
                input_data=data,
                output=Amount(Decimal('0'), currency=currency),
                penalties=[],
                warnings=warnings,
                metadata={'status': 'error', 'error': str(e)}
            )
