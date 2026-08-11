"""
SMART_AO V7.1 - test_math_engine_vigilance_solver.py
======================================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 11/08/2026
Build: 9.5 - Phase: 5
"""

"""
Tests unitaires complets pour VigilanceSolver.
Couvre tous les cas métiers URSSAF/DC4 pour le BTP.
Cible: >95% couverture du module vigilance_solver.py
"""

import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from unittest.mock import patch

from app.engines.math_engine.vigilance_solver import (
    VigilanceSolver,
    VigilanceResult,
    vigilance_solver,
    get_vigilance_solver,
    calculer_exposition_urssaf,
    VALIDITE_URSSAF_JOURS,
)
from app.engines.math_engine.types import SolverResult, Amount, Currency


class TestVigilanceSolverInit:
    """Tests d'initialisation du solver."""

    def test_singleton_instance(self):
        """Vérifie que vigilance_solver est bien un singleton."""
        solver1 = get_vigilance_solver()
        solver2 = get_vigilance_solver()
        assert solver1 is solver2
        assert isinstance(solver1, VigilanceSolver)

    def test_vigilance_solver_module_level(self):
        """Vérifie l'instance au niveau module."""
        assert isinstance(vigilance_solver, VigilanceSolver)

    def test_solver_creation(self):
        """Vérifie la création d'une nouvelle instance."""
        solver = VigilanceSolver()
        assert isinstance(solver, VigilanceSolver)


class TestVigilanceResultDataclass:
    """Tests du dataclass VigilanceResult."""

    def test_vigilance_result_creation(self):
        """Vérifie la création d'un VigilanceResult."""
        result = VigilanceResult(
            blocage_depot=True,
            attestation_valide=False,
            exposition_solidaire=Decimal("100000.00"),
            motif_blocage="Test",
            detail_calcul={"key": "value"},
        )
        assert result.blocage_depot is True
        assert result.attestation_valide is False
        assert result.exposition_solidaire == Decimal("100000.00")
        assert result.motif_blocage == "Test"
        assert result.detail_calcul == {"key": "value"}

    def test_vigilance_result_to_dict(self):
        """Vérifie la sécurisation to_dict."""
        result = VigilanceResult(
            blocage_depot=True,
            attestation_valide=False,
            exposition_solidaire=Decimal("100000.00"),
            motif_blocage="Test blocage",
            detail_calcul={"formule": "test"},
        )
        d = result.to_dict()
        assert d["blocage_depot"] is True
        assert d["attestation_valide"] is False
        assert d["exposition_solidaire"] == 100000.00
        assert d["motif_blocage"] == "Test blocage"
        assert d["detail_calcul"] == {"formule": "test"}

    def test_vigilance_result_to_dict_rounding(self):
        """Vérifie l'arrondi dans to_dict."""
        result = VigilanceResult(
            blocage_depot=True,
            attestation_valide=False,
            exposition_solidaire=Decimal("12345.678"),
            motif_blocage="",
            detail_calcul={},
        )
        d = result.to_dict()
        assert d["exposition_solidaire"] == 12345.68


class TestSolveMethod:
    """Tests de la méthode solve principale."""

    def test_solve_attestation_valide_recente(self):
        """Attestation URSSAF valide (moins de 6 mois)."""
        # Date dans le futur proche
        future_date = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        data = {
            "date_attestation": future_date,
            "montant_sous_traite": 100000.00,
            "statut_juridique": "actif",
        }
        solver = VigilanceSolver()
        result = solver.solve(data)

        assert isinstance(result, SolverResult)
        assert result.solver_name == "VigilanceSolver"
        assert result.output.value == Decimal("0")
        assert result.output.currency == Currency.EUR
        assert len(result.warnings) == 0
        assert result.metadata["detail_calcul"]["attestation_valide"] is True
        assert result.metadata["detail_calcul"]["blocage_depot"] is False

    def test_solve_attestation_valide_today(self):
        """Attestation valide avec date du jour."""
        today = datetime.now(timezone.utc).isoformat()
        data = {
            "date_attestation": today,
            "montant_sous_traite": 50000.00,
            "statut_juridique": "actif",
        }
        solver = VigilanceSolver()
        result = solver.solve(data)

        assert result.metadata["detail_calcul"]["attestation_valide"] is True
        assert result.metadata["detail_calcul"]["blocage_depot"] is False
        assert result.output.value == Decimal("0")

    def test_solve_attestation_expiree_6_jours(self):
        """Attestation expirée de 6 jours (6 mois + 6 jours)."""
        expired_date = (datetime.now(timezone.utc) - timedelta(days=VALIDITE_URSSAF_JOURS + 6)).isoformat()
        data = {
            "date_attestation": expired_date,
            "montant_sous_traite": 100000.00,
            "statut_juridique": "actif",
        }
        solver = VigilanceSolver()
        result = solver.solve(data)

        assert result.metadata["detail_calcul"]["attestation_valide"] is False
        assert result.metadata["detail_calcul"]["blocage_depot"] is True
        assert result.output.value == Decimal("100000.00")
        assert "expirée" in result.metadata["detail_calcul"]["motif_blocage"]
        assert len(result.warnings) == 1

    def test_solve_attestation_expiree_exactement_6_mois(self):
        """Attestation expirée exactement à 6 mois."""
        exact_date = (datetime.now(timezone.utc) - timedelta(days=VALIDITE_URSSAF_JOURS)).isoformat()
        data = {
            "date_attestation": exact_date,
            "montant_sous_traite": 100000.00,
            "statut_juridique": "actif",
        }
        solver = VigilanceSolver()
        result = solver.solve(data)

        # À exactement 180 jours, c'est encore valide (<= 180)
        assert result.metadata["detail_calcul"]["attestation_valide"] is True
        assert result.metadata["detail_calcul"]["blocage_depot"] is False
        assert result.output.value == Decimal("0")

    def test_solve_attestation_expiree_1_jour(self):
        """Attestation expirée de 1 jour (181 jours)."""
        expired_date = (datetime.now(timezone.utc) - timedelta(days=VALIDITE_URSSAF_JOURS + 1)).isoformat()
        data = {
            "date_attestation": expired_date,
            "montant_sous_traite": 75000.50,
            "statut_juridique": "actif",
        }
        solver = VigilanceSolver()
        result = solver.solve(data)

        assert result.metadata["detail_calcul"]["attestation_valide"] is False
        assert result.metadata["detail_calcul"]["blocage_depot"] is True
        assert result.output.value == Decimal("75000.50")
        assert "1 jours" in result.metadata["detail_calcul"]["motif_blocage"] or "1 jour" in result.metadata["detail_calcul"]["motif_blocage"]

    def test_solve_sous_traitant_liquidation(self):
        """Sous-traitant en liquidation → blocage immédiat."""
        data = {
            "date_attestation": datetime.now(timezone.utc).isoformat(),
            "montant_sous_traite": 200000.00,
            "statut_juridique": "liquidation",
        }
        solver = VigilanceSolver()
        result = solver.solve(data)

        assert result.metadata["detail_calcul"]["attestation_valide"] is False
        assert result.metadata["detail_calcul"]["blocage_depot"] is True
        assert result.output.value == Decimal("200000.00")
        assert "liquidation" in result.metadata["detail_calcul"]["motif_blocage"].lower()
        assert "DC4 bloqué" in result.metadata["detail_calcul"]["motif_blocage"]

    def test_solve_sous_traitant_radiation(self):
        """Sous-traitant radié → blocage immédiat."""
        data = {
            "date_attestation": datetime.now(timezone.utc).isoformat(),
            "montant_sous_traite": 150000.00,
            "statut_juridique": "radiation",
        }
        solver = VigilanceSolver()
        result = solver.solve(data)

        assert result.metadata["detail_calcul"]["blocage_depot"] is True
        assert result.output.value == Decimal("150000.00")
        assert "radiation" in result.metadata["detail_calcul"]["motif_blocage"].lower() or "radié" in result.metadata["detail_calcul"]["motif_blocage"].lower()

    def test_solve_sous_traitant_cessation(self):
        """Sous-traitant en cessation → blocage immédiat."""
        data = {
            "date_attestation": datetime.now(timezone.utc).isoformat(),
            "montant_sous_traite": 100000.00,
            "statut_juridique": "cessation",
        }
        solver = VigilanceSolver()
        result = solver.solve(data)

        assert result.metadata["detail_calcul"]["blocage_depot"] is True
        assert result.output.value == Decimal("100000.00")
        # Note: Le motif est générique pour liquidation/radiation/cessation
        assert "liquidation" in result.metadata["detail_calcul"]["motif_blocage"].lower() or "cessation" in result.metadata["detail_calcul"]["motif_blocage"].lower()

    def test_solve_attestation_manquante(self):
        """Attestation URSSAF manquante → blocage."""
        data = {
            "montant_sous_traite": 100000.00,
            "statut_juridique": "actif",
        }
        solver = VigilanceSolver()
        result = solver.solve(data)

        assert result.metadata["detail_calcul"]["attestation_valide"] is False
        assert result.metadata["detail_calcul"]["blocage_depot"] is True
        assert result.output.value == Decimal("100000.00")
        assert "manquante" in result.metadata["detail_calcul"]["motif_blocage"].lower()

    def test_solve_date_invalide(self):
        """Date d'attestation invalide → blocage."""
        data = {
            "date_attestation": "invalid-date",
            "montant_sous_traite": 100000.00,
            "statut_juridique": "actif",
        }
        solver = VigilanceSolver()
        result = solver.solve(data)

        assert result.metadata["detail_calcul"]["attestation_valide"] is False
        assert result.metadata["detail_calcul"]["blocage_depot"] is True
        assert result.output.value == Decimal("100000.00")
        assert "invalide" in result.metadata["detail_calcul"]["motif_blocage"].lower()

    def test_solve_date_none(self):
        """Date d'attestation None → blocage."""
        data = {
            "date_attestation": None,
            "montant_sous_traite": 100000.00,
            "statut_juridique": "actif",
        }
        solver = VigilanceSolver()
        result = solver.solve(data)

        assert result.metadata["detail_calcul"]["blocage_depot"] is True
        assert result.output.value == Decimal("100000.00")

    def test_solve_montant_zero(self):
        """Montant sous-traité à 0 → pas d'exposition."""
        future_date = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        data = {
            "date_attestation": future_date,
            "montant_sous_traite": 0,
            "statut_juridique": "actif",
        }
        solver = VigilanceSolver()
        result = solver.solve(data)

        assert result.output.value == Decimal("0")
        assert result.metadata["detail_calcul"]["blocage_depot"] is False

    def test_solve_montant_zero_mais_blocage(self):
        """Montant à 0 mais blocage pour autre raison → exposition à 0."""
        data = {
            "montant_sous_traite": 0,
            "statut_juridique": "liquidation",
        }
        solver = VigilanceSolver()
        result = solver.solve(data)

        assert result.output.value == Decimal("0")
        assert result.metadata["detail_calcul"]["blocage_depot"] is True

    def test_solve_statut_case_insensitive(self):
        """Statut juridique case insensitive."""
        future_date = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        data = {
            "date_attestation": future_date,
            "montant_sous_traite": 100000.00,
            "statut_juridique": "LIQUIDATION",
        }
        solver = VigilanceSolver()
        result = solver.solve(data)

        assert result.metadata["detail_calcul"]["blocage_depot"] is True
        assert result.output.value == Decimal("100000.00")

    def test_solve_currency_eur(self):
        """Vérifie la gestion de la devise EUR."""
        future_date = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        data = {
            "date_attestation": future_date,
            "montant_sous_traite": 100000.00,
            "statut_juridique": "actif",
            "currency": "EUR",
        }
        solver = VigilanceSolver()
        result = solver.solve(data)
        assert result.output.currency == Currency.EUR

    def test_solve_currency_usd(self):
        """Vérifie la gestion de la devise USD."""
        future_date = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        data = {
            "date_attestation": future_date,
            "montant_sous_traite": 100000.00,
            "statut_juridique": "actif",
            "currency": "USD",
        }
        solver = VigilanceSolver()
        result = solver.solve(data)
        assert result.output.currency == Currency.USD

    def test_solve_montant_string(self):
        """Montant sous forme de string."""
        future_date = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        data = {
            "date_attestation": future_date,
            "montant_sous_traite": "100000.00",
            "statut_juridique": "actif",
        }
        solver = VigilanceSolver()
        result = solver.solve(data)
        # Avec date valide, pas de blocage donc exposition = 0
        assert result.metadata["detail_calcul"]["montant_sous_traite"] == 100000.0
        assert result.output.value == Decimal("0")

    def test_solve_montant_int(self):
        """Montant sous forme d'entier."""
        future_date = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        data = {
            "date_attestation": future_date,
            "montant_sous_traite": 100000,
            "statut_juridique": "actif",
        }
        solver = VigilanceSolver()
        result = solver.solve(data)
        # Avec date valide, pas de blocage donc exposition = 0
        assert result.metadata["detail_calcul"]["montant_sous_traite"] == 100000.0
        assert result.output.value == Decimal("0")

    def test_solve_montant_negatif(self):
        """Montant négatif → géré comme Decimal négatif."""
        data = {
            "date_attestation": None,  # Pas de date → blocage
            "montant_sous_traite": -100000.00,
            "statut_juridique": "actif",
        }
        solver = VigilanceSolver()
        result = solver.solve(data)
        # Avec blocage, exposition = montant (même négatif)
        assert result.output.value == Decimal("-100000.00")
        assert result.metadata["detail_calcul"]["blocage_depot"] is True

    def test_solve_date_avec_z(self):
        """Date avec suffixe Z (UTC)."""
        # Utiliser une date fixe dans le futur avec Z (sans timezone déjà incluse)
        future_date = (datetime.now(timezone.utc) + timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ")
        data = {
            "date_attestation": future_date,
            "montant_sous_traite": 100000.00,
            "statut_juridique": "actif",
        }
        solver = VigilanceSolver()
        result = solver.solve(data)
        assert result.metadata["detail_calcul"]["attestation_valide"] is True
        assert result.metadata["detail_calcul"]["blocage_depot"] is False

    def test_solve_date_sans_timezone(self):
        """Date sans timezone → traitée comme UTC."""
        future_date = (datetime.now() + timedelta(days=30)).isoformat()
        data = {
            "date_attestation": future_date,
            "montant_sous_traite": 100000.00,
            "statut_juridique": "actif",
        }
        solver = VigilanceSolver()
        result = solver.solve(data)
        assert result.metadata["detail_calcul"]["attestation_valide"] is True

    def test_solve_detail_calcul_structure(self):
        """Vérifie la structure complète de detail_calcul."""
        future_date = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        data = {
            "date_attestation": future_date,
            "montant_sous_traite": 100000.00,
            "statut_juridique": "actif",
            "currency": "EUR",
        }
        solver = VigilanceSolver()
        result = solver.solve(data)

        detail = result.metadata["detail_calcul"]
        assert "formule_exposition" in detail
        assert "date_attestation" in detail
        assert "montant_sous_traite" in detail
        assert "statut_juridique" in detail
        assert "validite_jours" in detail
        assert "attestation_valide" in detail
        assert "blocage_depot" in detail
        assert "motif_blocage" in detail

    def test_solve_input_data_preserved(self):
        """Vérifie que input_data est préservé."""
        future_date = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        data = {
            "date_attestation": future_date,
            "montant_sous_traite": 100000.00,
            "statut_juridique": "actif",
            "custom_field": "custom_value",
        }
        solver = VigilanceSolver()
        result = solver.solve(data)
        assert result.input_data == data


class TestCalculerMethod:
    """Tests de la méthode calculer (API directe)."""

    def test_calculer_attestation_valide(self):
        """Calcul direct avec attestation valide."""
        future_date = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        solver = VigilanceSolver()
        result = solver.calculer(
            date_attestation=future_date,
            montant_sous_traite=100000.00,
            statut_juridique="actif",
        )

        assert isinstance(result, VigilanceResult)
        assert result.blocage_depot is False
        assert result.attestation_valide is True
        assert result.exposition_solidaire == Decimal("0")

    def test_calculer_attestation_expiree(self):
        """Calcul direct avec attestation expirée."""
        expired_date = (datetime.now(timezone.utc) - timedelta(days=VALIDITE_URSSAF_JOURS + 1)).isoformat()
        solver = VigilanceSolver()
        result = solver.calculer(
            date_attestation=expired_date,
            montant_sous_traite=100000.00,
            statut_juridique="actif",
        )

        assert result.blocage_depot is True
        assert result.attestation_valide is False
        assert result.exposition_solidaire == Decimal("100000.00")

    def test_calculer_liquidation(self):
        """Calcul direct avec sous-traitant en liquidation."""
        solver = VigilanceSolver()
        result = solver.calculer(
            date_attestation=None,
            montant_sous_traite=200000.00,
            statut_juridique="liquidation",
        )

        assert result.blocage_depot is True
        assert result.attestation_valide is False
        assert result.exposition_solidaire == Decimal("200000.00")

    def test_calculer_attestation_manquante(self):
        """Calcul direct sans attestation."""
        solver = VigilanceSolver()
        result = solver.calculer(
            date_attestation=None,
            montant_sous_traite=50000.00,
            statut_juridique="actif",
        )

        assert result.blocage_depot is True
        assert result.attestation_valide is False
        assert result.exposition_solidaire == Decimal("50000.00")

    def test_calculer_detail_calcul_complet(self):
        """Vérifie detail_calcul dans calculer."""
        future_date = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        solver = VigilanceSolver()
        result = solver.calculer(
            date_attestation=future_date,
            montant_sous_traite=100000.00,
            statut_juridique="actif",
        )

        assert isinstance(result.detail_calcul, dict)
        assert "attestation_valide" in result.detail_calcul
        assert "blocage_depot" in result.detail_calcul

    def test_calculer_to_dict(self):
        """Vérifie la conversion to_dict."""
        future_date = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        solver = VigilanceSolver()
        result = solver.calculer(
            date_attestation=future_date,
            montant_sous_traite=100000.00,
            statut_juridique="actif",
        )
        d = result.to_dict()
        assert isinstance(d, dict)
        assert "blocage_depot" in d
        assert "attestation_valide" in d
        assert "exposition_solidaire" in d
        assert "motif_blocage" in d
        assert "detail_calcul" in d


class TestCalculerExpositionUrssaf:
    """Tests de la fonction utilitaire calculer_exposition_urssaf."""

    def test_calculer_exposition_urssaf_valide(self):
        """Fonction utilitaire avec attestation valide."""
        future_date = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        result = calculer_exposition_urssaf(
            date_attestation=future_date,
            montant_sous_traite=100000.00,
            statut_juridique="actif",
        )

        assert isinstance(result, dict)
        assert result["blocage_depot"] is False
        assert result["attestation_valide"] is True
        assert result["exposition_solidaire"] == 0.0

    def test_calculer_exposition_urssaf_expiree(self):
        """Fonction utilitaire avec attestation expirée."""
        expired_date = (datetime.now(timezone.utc) - timedelta(days=VALIDITE_URSSAF_JOURS + 1)).isoformat()
        result = calculer_exposition_urssaf(
            date_attestation=expired_date,
            montant_sous_traite=100000.00,
            statut_juridique="actif",
        )

        assert result["blocage_depot"] is True
        assert result["attestation_valide"] is False
        assert result["exposition_solidaire"] == 100000.0

    def test_calculer_exposition_urssaf_liquidation(self):
        """Fonction utilitaire avec liquidation."""
        result = calculer_exposition_urssaf(
            date_attestation=None,
            montant_sous_traite=200000.00,
            statut_juridique="liquidation",
        )

        assert result["blocage_depot"] is True
        assert result["exposition_solidaire"] == 200000.0

    def test_calculer_exposition_urssaf_none_attestation(self):
        """Fonction utilitaire sans attestation."""
        result = calculer_exposition_urssaf(
            date_attestation=None,
            montant_sous_traite=50000.00,
            statut_juridique="actif",
        )

        assert result["blocage_depot"] is True
        assert result["exposition_solidaire"] == 50000.0

    def test_calculer_exposition_urssaf_structure(self):
        """Vérifie la structure complète du dictionnaire."""
        future_date = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        result = calculer_exposition_urssaf(
            date_attestation=future_date,
            montant_sous_traite=100000.00,
            statut_juridique="actif",
        )

        assert "blocage_depot" in result
        assert "attestation_valide" in result
        assert "exposition_solidaire" in result
        assert "motif_blocage" in result
        assert "detail_calcul" in result


class TestConstants:
    """Tests des constantes."""

    def test_validite_urssaf_jours(self):
        """Vérifie la constante VALIDITE_URSSAF_JOURS."""
        assert VALIDITE_URSSAF_JOURS == 180


class TestEdgeCases:
    """Tests des cas limites et edge cases."""

    def test_empty_data(self):
        """Données vides."""
        solver = VigilanceSolver()
        result = solver.solve({})
        assert result.metadata["detail_calcul"]["blocage_depot"] is True
        assert result.output.value == Decimal("0")

    def test_only_date_attestation(self):
        """Seulement la date d'attestation."""
        future_date = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        solver = VigilanceSolver()
        result = solver.solve({"date_attestation": future_date})
        assert result.metadata["detail_calcul"]["blocage_depot"] is False

    def test_very_large_montant(self):
        """Montant très élevé."""
        solver = VigilanceSolver()
        result = solver.solve({
            "date_attestation": None,  # Blocage
            "montant_sous_traite": "999999999999.99",
            "statut_juridique": "actif",
        })
        assert result.output.value == Decimal("999999999999.99")
        assert result.metadata["detail_calcul"]["blocage_depot"] is True

    def test_very_small_montant(self):
        """Montant très petit."""
        solver = VigilanceSolver()
        result = solver.solve({
            "date_attestation": None,  # Blocage
            "montant_sous_traite": "0.01",
            "statut_juridique": "actif",
        })
        assert result.output.value == Decimal("0.01")
        assert result.metadata["detail_calcul"]["blocage_depot"] is True

    def test_date_future_1_year(self):
        """Date dans le futur lointain."""
        future_date = (datetime.now(timezone.utc) + timedelta(days=365)).isoformat()
        solver = VigilanceSolver()
        result = solver.solve({
            "date_attestation": future_date,
            "montant_sous_traite": 100000.00,
            "statut_juridique": "actif",
        })
        assert result.metadata["detail_calcul"]["attestation_valide"] is True
        assert result.metadata["detail_calcul"]["blocage_depot"] is False

    def test_date_very_old(self):
        """Date très ancienne (10 ans)."""
        old_date = (datetime.now(timezone.utc) - timedelta(days=365 * 10)).isoformat()
        solver = VigilanceSolver()
        result = solver.solve({
            "date_attestation": old_date,
            "montant_sous_traite": 100000.00,
            "statut_juridique": "actif",
        })
        assert result.metadata["detail_calcul"]["attestation_valide"] is False
        assert result.metadata["detail_calcul"]["blocage_depot"] is True

    def test_statut_unknown(self):
        """Statut juridique inconnu → pas de blocage si date valide."""
        future_date = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        solver = VigilanceSolver()
        result = solver.solve({
            "date_attestation": future_date,
            "montant_sous_traite": 100000.00,
            "statut_juridique": "inconnu",
        })
        assert result.metadata["detail_calcul"]["attestation_valide"] is True
        assert result.metadata["detail_calcul"]["blocage_depot"] is False

    def test_date_empty_string(self):
        """Date vide."""
        solver = VigilanceSolver()
        result = solver.solve({
            "date_attestation": "",
            "montant_sous_traite": 100000.00,
            "statut_juridique": "actif",
        })
        assert result.metadata["detail_calcul"]["blocage_depot"] is True

    def test_montant_missing(self):
        """Montant manquant."""
        future_date = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        solver = VigilanceSolver()
        result = solver.solve({
            "date_attestation": future_date,
            "statut_juridique": "actif",
        })
        assert result.output.value == Decimal("0")


class TestWarnings:
    """Tests des warnings générés."""

    def test_no_warnings_when_no_blocage(self):
        """Pas de warnings quand pas de blocage."""
        future_date = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        solver = VigilanceSolver()
        result = solver.solve({
            "date_attestation": future_date,
            "montant_sous_traite": 100000.00,
            "statut_juridique": "actif",
        })
        assert len(result.warnings) == 0

    def test_warning_when_blocage(self):
        """Warning généré quand blocage."""
        expired_date = (datetime.now(timezone.utc) - timedelta(days=VALIDITE_URSSAF_JOURS + 1)).isoformat()
        solver = VigilanceSolver()
        result = solver.solve({
            "date_attestation": expired_date,
            "montant_sous_traite": 100000.00,
            "statut_juridique": "actif",
        })
        assert len(result.warnings) == 1
        assert "expirée" in result.warnings[0].lower()

    def test_multiple_warnings_not_possible(self):
        """Un seul warning possible (motif unique)."""
        expired_date = (datetime.now(timezone.utc) - timedelta(days=VALIDITE_URSSAF_JOURS + 1)).isoformat()
        solver = VigilanceSolver()
        result = solver.solve({
            "date_attestation": expired_date,
            "montant_sous_traite": 100000.00,
            "statut_juridique": "actif",
        })
        assert len(result.warnings) == 1


class TestMockedDatetime:
    """Tests avec datetime mocké pour des tests déterministes."""

    @patch('app.engines.math_engine.vigilance_solver.datetime')
    def test_solve_with_mocked_datetime_valide(self, mock_datetime):
        """Test avec datetime mocké - attestation valide."""
        fixed_now = datetime(2026, 8, 11, 12, 0, 0, tzinfo=timezone.utc)
        fixed_attestation = datetime(2026, 7, 11, 12, 0, 0, tzinfo=timezone.utc)  # 30 jours avant
        
        mock_datetime.now.return_value = fixed_now
        mock_datetime.fromisoformat = lambda x: fixed_attestation.replace(tzinfo=timezone.utc)
        
        solver = VigilanceSolver()
        result = solver.solve({
            "date_attestation": "2026-07-11T12:00:00+00:00",
            "montant_sous_traite": 100000.00,
            "statut_juridique": "actif",
        })

        assert result.metadata["detail_calcul"]["attestation_valide"] is True
        assert result.metadata["detail_calcul"]["blocage_depot"] is False

    @patch('app.engines.math_engine.vigilance_solver.datetime')
    def test_solve_with_mocked_datetime_expiree(self, mock_datetime):
        """Test avec datetime mocké - attestation expirée."""
        fixed_now = datetime(2026, 8, 11, 12, 0, 0, tzinfo=timezone.utc)
        fixed_attestation = datetime(2026, 1, 11, 12, 0, 0, tzinfo=timezone.utc)  # 6 mois + 1 jour avant
        
        mock_datetime.now.return_value = fixed_now
        mock_datetime.fromisoformat = lambda x: fixed_attestation
        
        solver = VigilanceSolver()
        result = solver.solve({
            "date_attestation": "2026-01-11T12:00:00+00:00",
            "montant_sous_traite": 100000.00,
            "statut_juridique": "actif",
        })

        assert result.metadata["detail_calcul"]["attestation_valide"] is False
        assert result.metadata["detail_calcul"]["blocage_depot"] is True

    @patch('app.engines.math_engine.vigilance_solver.datetime')
    def test_solve_with_mocked_datetime_exact_limit(self, mock_datetime):
        """Test avec datetime mocké - à la limite exacte."""
        fixed_now = datetime(2026, 8, 11, 12, 0, 0, tzinfo=timezone.utc)
        fixed_attestation = datetime(2026, 2, 12, 12, 0, 0, tzinfo=timezone.utc)  # Exactement 180 jours avant
        
        mock_datetime.now.return_value = fixed_now
        mock_datetime.fromisoformat = lambda x: fixed_attestation
        
        solver = VigilanceSolver()
        result = solver.solve({
            "date_attestation": "2026-02-12T12:00:00+00:00",
            "montant_sous_traite": 100000.00,
            "statut_juridique": "actif",
        })

        assert result.metadata["detail_calcul"]["attestation_valide"] is True
        assert result.metadata["detail_calcul"]["blocage_depot"] is False
