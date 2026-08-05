"""
SMART_AO V7 - Decimal Operations (28 precision)
"""
from decimal import Decimal, getcontext
from typing import Union, List

getcontext().prec = 28

class DecimalOps:
    @staticmethod
    def to_decimal(value: Union[int, float, str, Decimal]) -> Decimal:
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))
    
    @staticmethod
    def percentage(value: Union[int, float, str, Decimal], percent: Union[int, float, str, Decimal]) -> Decimal:
        return (DecimalOps.to_decimal(value) * DecimalOps.to_decimal(percent)) / Decimal('100')
    
    @staticmethod
    def sum(values: List) -> Decimal:
        return sum(DecimalOps.to_decimal(v) for v in values)
    
    @staticmethod
    def round(value: Union[int, float, str, Decimal], places: int = 2) -> Decimal:
        value_d = DecimalOps.to_decimal(value)
        factor = Decimal('10') ** -places
        return (value_d + factor / Decimal('2')).quantize(factor)
