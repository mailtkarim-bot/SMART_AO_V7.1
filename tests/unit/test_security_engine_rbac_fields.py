"""
SMART_AO V7 - Tests unitaires complets pour rbac_fields.py
==========================================================
Tests complets pour normalize_field_name, FIELDS_STRIP, et is_sensitive_field.
Cible: 100% couverture
"""

import pytest

from app.engines.security_engine.rbac_fields import (
    normalize_field_name,
    FIELDS_STRIP,
    FIELDS_STRIP_V6,
    is_sensitive_field,
)


class TestNormalizeFieldName:
    """Tests pour la fonction normalize_field_name."""

    def test_basic_camel_case(self):
        assert normalize_field_name("priceUnitaire") == "price_unitaire"
        assert normalize_field_name("montantHT") == "montant_ht"

    def test_all_uppercase(self):
        assert normalize_field_name("HTTPResponseCode") == "http_response_code"
        assert normalize_field_name("PRIX") == "prix"

    def test_with_dashes(self):
        assert normalize_field_name("prix-unitaire") == "prix_unitaire"

    def test_with_spaces(self):
        assert normalize_field_name("Prix Unitaire") == "prix_unitaire"

    def test_with_dots(self):
        assert normalize_field_name("price.unitaire") == "price_unitaire"

    def test_mixed_formatters(self):
        assert normalize_field_name("get-HTTP.response-code") == "get_http_response_code"

    def test_already_snake_case(self):
        assert normalize_field_name("prix_unitaire") == "prix_unitaire"

    def test_lowercase(self):
        assert normalize_field_name("prix") == "prix"

    def test_uppercase(self):
        assert normalize_field_name("PRIX") == "prix"

    def test_with_numbers(self):
        assert normalize_field_name("field123") == "field123"
        assert normalize_field_name("field123ABC") == "field123_abc"

    def test_consecutive_uppercase(self):
        assert normalize_field_name("getHTTPResponse") == "get_http_response"

    def test_leading_underscore(self):
        assert normalize_field_name("_privateField") == "private_field"

    def test_trailing_underscore(self):
        assert normalize_field_name("field_") == "field"

    def test_multiple_separators(self):
        assert normalize_field_name("field--name") == "field_name"
        assert normalize_field_name("field..name") == "field_name"

    def test_empty_string(self):
        assert normalize_field_name("") == ""

    def test_single_character(self):
        assert normalize_field_name("a") == "a"
        assert normalize_field_name("A") == "a"

    def test_french_accents(self):
        assert normalize_field_name("coûtDirect") == "coût_direct"


class TestFieldsStrip:
    """Tests pour la constante FIELDS_STRIP."""

    def test_is_frozenset(self):
        assert isinstance(FIELDS_STRIP, frozenset)

    def test_not_empty(self):
        assert len(FIELDS_STRIP) > 0

    def test_contains_financial_fields(self):
        financial_fields = ["marge", "coefficient", "tresorerie", "prix", "cout", "montant", "penalite"]
        for field in financial_fields:
            assert field in FIELDS_STRIP

    def test_contains_v71_fields(self):
        v71_fields = ["penibilite", "urssaf", "zan", "formule_revision", "api_key"]
        for field in v71_fields:
            assert field in FIELDS_STRIP

    def test_fields_are_lowercase(self):
        for field in FIELDS_STRIP:
            assert field == field.lower()


class TestFieldsStripV6:
    """Tests pour FIELDS_STRIP_V6."""

    def test_is_same_as_fields_strip(self):
        assert FIELDS_STRIP_V6 is FIELDS_STRIP


class TestIsSensitiveField:
    """Tests pour la fonction is_sensitive_field."""

    def test_sensitive_fields(self):
        sensitive_fields = ["marge", "Marge", "coefficient", "prix", "montant_ht"]
        for field in sensitive_fields:
            assert is_sensitive_field(field) is True

    def test_non_sensitive_fields(self):
        non_sensitive_fields = ["nom", "prenom", "description", "statut"]
        for field in non_sensitive_fields:
            assert is_sensitive_field(field) is False

    def test_case_insensitive(self):
        assert is_sensitive_field("Marge") is True
        assert is_sensitive_field("MARGE") is True

    def test_with_normalized_names(self):
        # is_sensitive_field fait field_name.lower() in FIELDS_STRIP
        # Donc elle ne normalise pas, elle convertit juste en lowercase
        # "priceUnitaire".lower() = "priceunitaire" qui n'est pas dans FIELDS_STRIP
        # Mais "prix_unitaire" est dans FIELDS_STRIP
        assert is_sensitive_field("prix_unitaire") is True
        assert is_sensitive_field("prix unitaires") is False  # "prix unitaires" n'est pas dans FIELDS_STRIP
        assert is_sensitive_field("PRIX_UNITAIRE") is True

    def test_empty_string(self):
        assert is_sensitive_field("") is False

    def test_partial_matches(self):
        assert is_sensitive_field("marginal") is False
        assert is_sensitive_field("couture") is False

    def test_with_whitespace(self):
        # "prix unitaires".lower() = "prix unitaires" qui n'est pas dans FIELDS_STRIP
        # Seuls les champs exactement dans FIELDS_STRIP (en lowercase) sont détectés
        assert is_sensitive_field("prix unitaires") is False

    def test_with_hyphens(self):
        # "prix-unitaire".lower() = "prix-unitaire" qui n'est pas dans FIELDS_STRIP
        assert is_sensitive_field("prix-unitaire") is False

    def test_with_underscores(self):
        assert is_sensitive_field("prix_unitaire") is True


class TestIntegration:
    """Tests dintegration."""

    def test_normalize_then_check(self):
        # Après normalisation, les champs doivent être détectés
        test_cases = [
            ("priceUnitaire", False),  # normalisé en "price_unitaire" qui n'est pas dans FIELDS_STRIP
            ("prixUnitaire", True),  # normalisé en "prix_unitaire" qui est dans FIELDS_STRIP
            ("montantHT", True),  # normalisé en "montant_ht" qui est dans FIELDS_STRIP
            ("nomProjet", False),  # normalisé en "nom_projet" qui n'est pas dans FIELDS_STRIP
        ]
        for field_name, expected_sensitive in test_cases:
            normalized = normalize_field_name(field_name)
            is_sensitive = is_sensitive_field(normalized)
            assert is_sensitive == expected_sensitive

    def test_all_sensitive_fields_normalizable(self):
        for field in FIELDS_STRIP:
            normalized = normalize_field_name(field)
            assert is_sensitive_field(normalized) is True


class TestEdgeCases:
    """Tests pour les cas limites."""

    def test_very_long_field_name(self):
        long_name = "a" * 1000
        normalized = normalize_field_name(long_name)
        assert len(normalized) == 1000

    def test_field_with_many_separators(self):
        field = "field--name..with__multiple___separators"
        normalized = normalize_field_name(field)
        assert normalized == "field_name_with_multiple_separators"

    def test_field_with_mixed_case_and_numbers(self):
        field = "getHTTP2ResponseCode"
        normalized = normalize_field_name(field)
        assert normalized == "get_http2_response_code"
