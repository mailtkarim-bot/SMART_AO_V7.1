"""
SMART_AO V7 - Math Engine __init__.py
======================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Math Engine - Moteur de calcul et d'analyse mathématique pour SMART_AO V7
Source: ARCHITECTURE_V7_ENGINE.md §3.4
"""

from app.engines.math_engine.decimal_ops import DecimalOps, getcontext
from app.engines.math_engine.types import *
from app.engines.math_engine.chiffrage_pulp import *
from app.engines.math_engine.margin import *
from app.engines.math_engine.treasury import *
from app.engines.math_engine.worst_case import *
from app.engines.math_engine.zan_solver import *
from app.engines.math_engine.sous_chiffrage import *
from app.engines.math_engine.formule_algebra_checker import *
from app.engines.math_engine.sourcing_api_solver import *
from app.engines.math_engine.pab_detector import *
from app.engines.math_engine.penibilite_solver import *
from app.engines.math_engine.planning import *
from app.engines.math_engine.resources import *
from app.engines.math_engine.rep_cost import *
from app.engines.math_engine.materiaux_shield import *
from app.engines.math_engine.incoherence_solver import *
from app.engines.math_engine.eplusc_calculator import *
from app.engines.math_engine.risques_generator import *
from app.engines.math_engine.site_coeff import *

__all__ = [
    # Modules
    'decimal_ops', 'types', 'chiffrage_pulp', 'margin', 'treasury',
    'worst_case', 'zan_solver', 'sous_chiffrage', 'formule_algebra_checker',
    'sourcing_api_solver', 'pab_detector', 'penibilite_solver', 'planning',
    'resources', 'rep_cost', 'materiaux_shield', 'incoherence_solver',
    'eplusc_calculator', 'risques_generator', 'site_coeff',
    # Classes principales
    'DecimalOps', 'PlanningSolver', 'ResourcesSolver', 'RepCostSolver',
    'MateriauxShield', 'IncoherenceSolver', 'EPlusCCalculator',
    'RisquesGenerator', 'SiteCoeffCalculator',
    # Fonctions utilitaires
    'solver', 'generator', 'calculator'
]

# Exporter les instances singleton
def __getattr__(name):
    if name == 'solver':
        from app.engines.math_engine.planning import solver
        return solver
    elif name == 'generator':
        from app.engines.math_engine.risques_generator import generator
        return generator
    elif name == 'calculator':
        from app.engines.math_engine.site_coeff import calculator
        return calculator
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

# Configuration globale
def init_math_engine():
    """Initialise le moteur mathématique."""
    from decimal import getcontext
    getcontext().prec = 28
    return True

# Initialiser automatiquement
init_math_engine()

