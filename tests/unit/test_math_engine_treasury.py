"""
SMART_AO V7 - Tests unitaires pour treasury.py
===============================================
Tests complets pour les classes AvanceCalculator, BFRCalculator, FluxTresorerieCalculator
"""

import pytest
from datetime import date, timedelta
from app.engines.math_engine.treasury import (
    FluxType, AvanceType, TypeAcheteur,
    FluxTresorerie, AvanceCalculee, BFRResult, TreasuryAnalysis,
    AvanceCalculator, BFRCalculator, FluxTresorerieCalculator
)


# =============================================================================
# TESTS POUR ENUMS
# =============================================================================

class TestFluxType:
    def test_enum_values(self):
        assert FluxType.ENCAISSEMENT == "encaissement"
        assert FluxType.DECAISSEMENT == "decaisement"


class TestAvanceType:
    def test_enum_values(self):
        assert AvanceType.AVANCE_2024 == "avance_2024"
        assert AvanceType.ACONTE == "acompte"
        assert AvanceType.SITUATION == "situation"


class TestTypeAcheteur:
    def test_enum_values(self):
        assert TypeAcheteur.ETAT == "etat"
        assert TypeAcheteur.COLLECTIVITE == "collectivite"
        assert TypeAcheteur.AUTRE == "autre"


# =============================================================================
# TESTS POUR DATACLASSES
# =============================================================================

class TestFluxTresorerie:
    def test_creation(self):
        flux = FluxTresorerie(
            date=date(2026, 8, 10),
            montant=10000.0,
            type=FluxType.ENCAISSEMENT,
            libelle="Paiement client",
            echeance=30
        )
        assert flux.date == date(2026, 8, 10)
        assert flux.montant == 10000.0
        assert flux.type == FluxType.ENCAISSEMENT
        assert flux.libelle == "Paiement client"
        assert flux.echeance == 30

    def test_default_echeance(self):
        flux = FluxTresorerie(
            date=date(2026, 8, 10),
            montant=5000.0,
            type=FluxType.DECAISSEMENT,
            libelle="Paiement fournisseur"
        )
        assert flux.echeance is None


class TestAvanceCalculee:
    def test_creation(self):
        avance = AvanceCalculee(
            type=AvanceType.AVANCE_2024,
            montant=30000.0,
            pourcentage=30.0,
            base_calcul=100000.0,
            date_versement=date(2026, 8, 15),
            conditions=["Condition 1", "Condition 2"]
        )
        assert avance.type == AvanceType.AVANCE_2024
        assert avance.montant == 30000.0
        assert avance.pourcentage == 30.0
        assert avance.base_calcul == 100000.0
        assert avance.date_versement == date(2026, 8, 15)
        assert avance.conditions == ["Condition 1", "Condition 2"]

    def test_default_values(self):
        avance = AvanceCalculee(
            type=AvanceType.ACONTE,
            montant=15000.0,
            pourcentage=15.0,
            base_calcul=100000.0
        )
        assert avance.date_versement is None
        assert avance.conditions is None


class TestBFRResult:
    def test_creation(self):
        bfr = BFRResult(
            bfr_total=50000.0,
            bfr_par_mois={"01": 10000.0, "02": 20000.0},
            bfr_cumul={"01": 10000.0, "02": 30000.0},
            pic_bfr=30000.0,
            mois_pic="02",
            besoins_financement=20000.0
        )
        assert bfr.bfr_total == 50000.0
        assert bfr.bfr_par_mois == {"01": 10000.0, "02": 20000.0}
        assert bfr.bfr_cumul == {"01": 10000.0, "02": 30000.0}
        assert bfr.pic_bfr == 30000.0
        assert bfr.mois_pic == "02"
        assert bfr.besoins_financement == 20000.0


class TestTreasuryAnalysis:
    def test_creation(self):
        avance = AvanceCalculee(
            type=AvanceType.AVANCE_2024,
            montant=30000.0,
            pourcentage=30.0,
            base_calcul=100000.0
        )
        bfr = BFRResult(
            bfr_total=50000.0,
            bfr_par_mois={"01": 10000.0},
            bfr_cumul={"01": 10000.0},
            pic_bfr=10000.0,
            mois_pic="01",
            besoins_financement=10000.0
        )
        analysis = TreasuryAnalysis(
            avance=avance,
            bfr=bfr,
            flux_tresorerie=[],
            solde_tresorerie={"01": 50000.0},
            solde_minimal=0.0,
            mois_critique="01",
            recommandations=["Augmenter la trésorerie"]
        )
        assert analysis.avance == avance
        assert analysis.bfr == bfr
        assert analysis.flux_tresorerie == []
        assert analysis.solde_tresorerie == {"01": 50000.0}
        assert analysis.solde_minimal == 0.0
        assert analysis.mois_critique == "01"
        assert analysis.recommandations == ["Augmenter la trésorerie"]


# =============================================================================
# TESTS POUR AvanceCalculator
# =============================================================================

class TestAvanceCalculator:
    def test_pourcentage_avance_2024_etat(self):
        """Test pourcentage pour État - doit être 30%"""
        pct = AvanceCalculator._pourcentage_avance_2024(
            TypeAcheteur.ETAT, 1000000.0, None
        )
        assert pct == 30.0

    def test_pourcentage_avance_2024_collectivite_sup_seuil(self):
        """Test pourcentage pour collectivité > 60M€ - doit être 10%"""
        pct = AvanceCalculator._pourcentage_avance_2024(
            TypeAcheteur.COLLECTIVITE, 70000000.0, None
        )
        assert pct == 10.0

    def test_pourcentage_avance_2024_collectivite_inf_seuil(self):
        """Test pourcentage pour collectivité <= 60M€ - doit être 0%"""
        pct = AvanceCalculator._pourcentage_avance_2024(
            TypeAcheteur.COLLECTIVITE, 50000000.0, None
        )
        assert pct == 0.0

    def test_pourcentage_avance_2024_autre(self):
        """Test pourcentage pour autre acheteur - doit être 0%"""
        pct = AvanceCalculator._pourcentage_avance_2024(
            TypeAcheteur.AUTRE, 1000000.0, None
        )
        assert pct == 0.0

    def test_pourcentage_override(self):
        """Test pourcentage avec override"""
        pct = AvanceCalculator._pourcentage_avance_2024(
            TypeAcheteur.ETAT, 1000000.0, 25.0
        )
        assert pct == 25.0

    def test_calculer_avance_2024_etat(self):
        """Test calcul avance État"""
        result = AvanceCalculator.calculer(
            montant_marche_ht=1000000.0,
            avance_type=AvanceType.AVANCE_2024,
            type_acheteur=TypeAcheteur.ETAT,
            date_debut=date(2026, 8, 10),
            delai_versement_jours=30
        )
        assert result.montant == 300000.0
        assert result.pourcentage == 30.0
        assert result.base_calcul == 1000000.0
        assert result.date_versement == date(2026, 9, 9)
        assert result.type == AvanceType.AVANCE_2024
        assert len(result.conditions) > 0

    def test_calculer_avance_personnalisee(self):
        """Test calcul avance avec pourcentage personnalisé"""
        result = AvanceCalculator.calculer(
            montant_marche_ht=200000.0,
            avance_type=AvanceType.ACONTE,
            pourcentage=20.0
        )
        assert result.montant == 40000.0
        assert result.pourcentage == 20.0

    def test_calculer_avance_collectivite_sup_seuil(self):
        """Test calcul avance collectivité > 60M€"""
        result = AvanceCalculator.calculer(
            montant_marche_ht=70000000.0,
            avance_type=AvanceType.AVANCE_2024,
            type_acheteur=TypeAcheteur.COLLECTIVITE
        )
        assert result.montant == 7000000.0
        assert result.pourcentage == 10.0

    def test_calculer_avance_sans_date(self):
        """Test calcul avance sans date de début"""
        result = AvanceCalculator.calculer(
            montant_marche_ht=100000.0,
            avance_type=AvanceType.AVANCE_2024,
            type_acheteur=TypeAcheteur.ETAT
        )
        assert result.date_versement is None


# =============================================================================
# TESTS POUR BFRCalculator
# =============================================================================

class TestBFRCalculator:
    def test_calculer_par_mois_simple(self):
        """Test calcul BFR par mois avec données simples"""
        planning = {
            "2026-08": {
                "facturation": 50000.0,
                "main_doeuvre": 20000.0,
                "sous_traitance": 10000.0
            }
        }
        couts_materiaux = {"2026-08": 15000.0}
        
        result = BFRCalculator.calculer_par_mois(
            planning, couts_materiaux, 60, 30
        )
        
        assert isinstance(result, BFRResult)
        assert "2026-08" in result.bfr_par_mois
        assert "2026-08" in result.bfr_cumul
        assert result.pic_bfr is not None
        assert result.mois_pic == "2026-08"

    def test_calculer_par_mois_multiple_mois(self):
        """Test calcul BFR par mois avec plusieurs mois"""
        planning = {
            "2026-01": {"facturation": 50000.0, "main_doeuvre": 20000.0},
            "2026-02": {"facturation": 30000.0, "main_doeuvre": 15000.0},
            "2026-03": {"facturation": 20000.0, "main_doeuvre": 10000.0}
        }
        couts_materiaux = {
            "2026-01": 10000.0,
            "2026-02": 8000.0,
            "2026-03": 5000.0
        }
        
        result = BFRCalculator.calculer_par_mois(
            planning, couts_materiaux, 60, 30
        )
        
        assert len(result.bfr_par_mois) == 3
        assert len(result.bfr_cumul) == 3
        assert result.pic_bfr == max(result.bfr_cumul.values())

    def test_calculer_par_mois_vide(self):
        """Test calcul BFR par mois avec planning vide"""
        result = BFRCalculator.calculer_par_mois({}, {}, 60, 30)
        
        assert result.bfr_par_mois == {}
        assert result.bfr_cumul == {}
        assert result.pic_bfr == 0.0
        assert result.besoins_financement == 0.0

    def test_calculer_simple(self):
        """Test calcul BFR simplifié"""
        bfr = BFRCalculator.calculer_simple(
            chiffre_affaires_annuel=1200000.0,
            cout_revient_annuel=800000.0,
            delai_paiement_clients=60,
            delai_paiement_fournisseurs=30,
            stock_moyen=50000.0
        )
        
        assert isinstance(bfr, float)
        assert bfr > 0
        # Vérification du calcul : (1200000 * 60/360) + 50000 - (800000 * 30/360)
        # = 200000 + 50000 - 66666.67 = 183333.33
        expected = round(1200000 * 60 / 360 + 50000 - 800000 * 30 / 360, 2)
        assert bfr == expected

    def test_calculer_simple_zero(self):
        """Test calcul BFR simplifié avec zéros"""
        bfr = BFRCalculator.calculer_simple(
            chiffre_affaires_annuel=0.0,
            cout_revient_annuel=0.0,
            stock_moyen=0.0
        )
        assert bfr == 0.0


# =============================================================================
# TESTS POUR FluxTresorerieCalculator
# =============================================================================

class TestFluxTresorerieCalculator:
    def test_generer_flux_simple(self):
        """Test génération de flux de trésorerie simple"""
        planning = {
            "M01": {"facturation": 50000.0},
            "M02": {"facturation": 30000.0}
        }
        
        avance = AvanceCalculee(
            type=AvanceType.AVANCE_2024,
            montant=30000.0,
            pourcentage=30.0,
            base_calcul=100000.0,
            date_versement=date(2026, 8, 15)
        )
        
        bfr_result = BFRResult(
            bfr_total=10000.0,
            bfr_par_mois={"M01": 5000.0, "M02": 5000.0},
            bfr_cumul={"M01": 5000.0, "M02": 10000.0},
            pic_bfr=10000.0,
            mois_pic="M02",
            besoins_financement=10000.0
        )
        
        flux = FluxTresorerieCalculator.generer_flux(
            planning=planning,
            avance=avance,
            bfr_result=bfr_result,
            date_debut=date(2026, 8, 1),
            duree_mois=2
        )
        
        assert len(flux) > 0
        assert isinstance(flux[0], FluxTresorerie)
        # Premier flux doit être l'avance
        assert flux[0].type == FluxType.ENCAISSEMENT
        assert flux[0].libelle == "Avance marché"

    def test_generer_flux_with_facturation(self):
        """Test génération de flux avec facturation"""
        planning = {
            "M01": {"facturation": 50000.0},
        }
        
        avance = AvanceCalculee(
            type=AvanceType.AVANCE_2024,
            montant=30000.0,
            pourcentage=30.0,
            base_calcul=100000.0,
            date_versement=date(2026, 8, 15)
        )
        
        bfr_result = BFRResult(
            bfr_total=5000.0,
            bfr_par_mois={"M01": 5000.0},
            bfr_cumul={"M01": 5000.0},
            pic_bfr=5000.0,
            mois_pic="M01",
            besoins_financement=5000.0
        )
        
        flux = FluxTresorerieCalculator.generer_flux(
            planning=planning,
            avance=avance,
            bfr_result=bfr_result,
            date_debut=date(2026, 8, 1),
            duree_mois=1
        )
        
        # Doit avoir au moins 2 flux : avance + facturation
        assert len(flux) >= 2
        # Vérifier qu'il y a un flux pour la facturation
        facturation_flux = [f for f in flux if "Facturation" in f.libelle]
        assert len(facturation_flux) >= 1
