"""
SMART_AO V7 - types.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Math Engine Types
"""
from decimal import Decimal, getcontext
from typing import Optional, Union, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

getcontext().prec = 28

class Currency(str, Enum):
    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"

class PenaltyType(str, Enum):
    CCAG_10PCT = "CCAG_10PCT"
    CCAG_5PCT = "CCAG_5PCT"
    CCMI = "CCMI"
    PAB_20PCT = "PAB_20PCT"
    PAB_30PCT = "PAB_30PCT"

@dataclass
class Amount:
    value: Decimal
    currency: Currency = Currency.EUR
    
    def __post_init__(self):
        if isinstance(self.value, (int, float, str)):
            self.value = Decimal(str(self.value))

@dataclass
class Penalty:
    penalty_type: PenaltyType
    amount: Amount
    description: str
    reference: str

@dataclass
class SolverResult:
    solver_name: str
    input_data: Dict[str, Any]
    output: Amount
    penalties: List = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
