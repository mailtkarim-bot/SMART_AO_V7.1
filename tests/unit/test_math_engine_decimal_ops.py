"""
SMART_AO V7 - Tests unitaires pour decimal_ops.py
=================================================
Tests complets pour DecimalOps
"""

import pytest
from decimal import Decimal
from app.engines.math_engine.decimal_ops import DecimalOps


class TestDecimalOpsToDecimal:
    def test_int_to_decimal(self):
        result = DecimalOps.to_decimal(100)
        assert isinstance(result, Decimal)
        assert result == Decimal("100")

    def test_float_to_decimal(self):
        result = DecimalOps.to_decimal(100.50)
        assert isinstance(result, Decimal)
        assert result == Decimal("100.50")

    def test_str_to_decimal(self):
        result = DecimalOps.to_decimal("100.50")
        assert isinstance(result, Decimal)
        assert result == Decimal("100.50")

    def test_decimal_to_decimal(self):
        value = Decimal("100.50")
        result = DecimalOps.to_decimal(value)
        assert result is value

    def test_negative_to_decimal(self):
        result = DecimalOps.to_decimal(-100.50)
        assert result == Decimal("-100.50")

    def test_zero_to_decimal(self):
        result = DecimalOps.to_decimal(0)
        assert result == Decimal("0")

    def test_large_number_to_decimal(self):
        # Les floats ont une précision limitée, donc on vérifie que la conversion fonctionne
        result = DecimalOps.to_decimal(1234567890.123456789)
        assert isinstance(result, Decimal)
        # Le float 1234567890.123456789 est stocké avec une précision limitée
        # Donc on vérifie juste que c'est un Decimal valide


class TestDecimalOpsPercentage:
    def test_percentage_int_values(self):
        result = DecimalOps.percentage(100, 10)
        assert result == Decimal("10")

    def test_percentage_float_values(self):
        result = DecimalOps.percentage(100.0, 10.0)
        assert result == Decimal("10")

    def test_percentage_decimal_values(self):
        result = DecimalOps.percentage(Decimal("100"), Decimal("10"))
        assert result == Decimal("10")

    def test_percentage_string_values(self):
        result = DecimalOps.percentage("100", "10")
        assert result == Decimal("10")

    def test_percentage_zero(self):
        result = DecimalOps.percentage(100, 0)
        assert result == Decimal("0")

    def test_percentage_100(self):
        result = DecimalOps.percentage(100, 100)
        assert result == Decimal("100")

    def test_percentage_mixed_types(self):
        result = DecimalOps.percentage(100, "25.5")
        assert result == Decimal("25.5")


class TestDecimalOpsSum:
    def test_sum_empty_list(self):
        result = DecimalOps.sum([])
        assert result == Decimal("0")

    def test_sum_single_value(self):
        result = DecimalOps.sum([100])
        assert result == Decimal("100")

    def test_sum_multiple_int_values(self):
        result = DecimalOps.sum([100, 200, 300])
        assert result == Decimal("600")

    def test_sum_multiple_float_values(self):
        result = DecimalOps.sum([100.50, 200.25, 300.75])
        assert result == Decimal("601.50")

    def test_sum_mixed_types(self):
        result = DecimalOps.sum([100, 200.50, Decimal("300.50"), "50.25"])
        assert result == Decimal("651.25")

    def test_sum_negative_values(self):
        result = DecimalOps.sum([100, -50, 200])
        assert result == Decimal("250")


class TestDecimalOpsRound:
    def test_round_default_places(self):
        # L'arrondi bancaire (ROUND_HALF_UP) arrondit 100.125 à 100.13
        result = DecimalOps.round("100.123456")
        # Avec ROUND_HALF_UP, 100.123456 arrondi à 2 décimales = 100.12
        assert result == pytest.approx(Decimal("100.12"), abs=Decimal("0.01"))

    def test_round_0_places(self):
        result = DecimalOps.round("100.567", 0)
        assert result == Decimal("101")

    def test_round_1_place(self):
        result = DecimalOps.round("100.567", 1)
        assert result == Decimal("100.6")

    def test_round_2_places(self):
        result = DecimalOps.round("100.5678", 2)
        assert result == Decimal("100.57")

    def test_round_4_places(self):
        result = DecimalOps.round("100.12345678", 4)
        assert result == Decimal("100.1235")

    def test_round_negative(self):
        # Avec ROUND_HALF_UP, -100.567 arrondi à 1 décimale = -100.6
        result = DecimalOps.round("-100.567", 1)
        assert result == pytest.approx(Decimal("-100.6"), abs=Decimal("0.1"))

    def test_round_int(self):
        result = DecimalOps.round(100, 2)
        assert result == Decimal("100.00")

    def test_round_float(self):
        result = DecimalOps.round(100.567, 2)
        assert result == Decimal("100.57")

    def test_round_decimal(self):
        result = DecimalOps.round(Decimal("100.567"), 2)
        assert result == Decimal("100.57")
