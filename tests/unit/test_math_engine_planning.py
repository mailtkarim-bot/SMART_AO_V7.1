"""
SMART_AO V7 - Tests unitaires pour planning.py
==============================================
Tests complets pour Tache, Ressource, Planning, PlanningOptimisation
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from app.engines.math_engine.planning import Tache, Ressource, Planning, PlanningOptimisation


# =============================================================================
# TESTS POUR Tache
# =============================================================================

class TestTache:
    def test_creation_simple(self):
        tache = Tache(
            tache_id="T001",
            nom="Fondations",
            duree_jours=10
        )
        assert tache.tache_id == "T001"
        assert tache.nom == "Fondations"
        assert tache.duree_jours == 10
        assert tache.dependencies == []
        assert tache.date_debut is None
        assert tache.date_fin is None
        assert tache.ressources == []
        assert tache.cout == Decimal("0")
        assert tache.est_critique is False

    def test_creation_with_all_fields(self):
        date_debut = date(2026, 8, 10)
        date_fin = date(2026, 8, 20)
        tache = Tache(
            tache_id="T001",
            nom="Fondations",
            duree_jours=10,
            dependencies=["T002"],
            date_debut=date_debut,
            date_fin=date_fin,
            ressources=["R001", "R002"],
            cout=Decimal("50000.00"),
            est_critique=True
        )
        assert tache.dependencies == ["T002"]
        assert tache.date_debut == date_debut
        assert tache.date_fin == date_fin
        assert tache.ressources == ["R001", "R002"]
        assert tache.cout == Decimal("50000.00")
        assert tache.est_critique is True

    def test_creation_with_empty_dependencies(self):
        tache = Tache(
            tache_id="T001",
            nom="Test",
            duree_jours=5,
            dependencies=[]
        )
        assert tache.dependencies == []


# =============================================================================
# TESTS POUR Ressource
# =============================================================================

class TestRessource:
    def test_creation_simple(self):
        ressource = Ressource(
            ressource_id="R001",
            nom="Ouvrier qualifié"
        )
        assert ressource.ressource_id == "R001"
        assert ressource.nom == "Ouvrier qualifié"
        assert ressource.type == "humaine"
        assert ressource.cout_journalier == Decimal("0")
        assert ressource.disponibilite == []
        assert ressource.capacite == 1

    def test_creation_with_all_fields(self):
        disponibilite = [date(2026, 8, 10), date(2026, 8, 11)]
        ressource = Ressource(
            ressource_id="R001",
            nom="Grue",
            type="materiel",
            cout_journalier=Decimal("500.00"),
            disponibilite=disponibilite,
            capacite=3
        )
        assert ressource.type == "materiel"
        assert ressource.cout_journalier == Decimal("500.00")
        assert ressource.disponibilite == disponibilite
        assert ressource.capacite == 3

    def test_creation_type_sous_traitant(self):
        ressource = Ressource(
            ressource_id="R002",
            nom="Sous-traitant",
            type="sous_traitant",
            cout_journalier=Decimal("1000.00")
        )
        assert ressource.type == "sous_traitant"


# =============================================================================
# TESTS POUR Planning
# =============================================================================

class TestPlanning:
    def test_creation_simple(self):
        date_debut = date(2026, 8, 10)
        planning = Planning(
            planning_id="P001",
            mission_id="M001",
            nom="Planning Chantier A",
            date_debut=date_debut
        )
        assert planning.planning_id == "P001"
        assert planning.mission_id == "M001"
        assert planning.nom == "Planning Chantier A"
        assert planning.date_debut == date_debut
        assert planning.date_fin is None
        assert planning.taches == []
        assert planning.ressources == []
        assert planning.duree_totale is None
        assert planning.cout_total is None
        assert planning.chemin_critique == []

    def test_creation_with_taches_and_ressources(self):
        date_debut = date(2026, 8, 10)
        date_fin = date(2026, 9, 10)
        
        taches = [
            Tache(tache_id="T001", nom="Tache 1", duree_jours=10),
            Tache(tache_id="T002", nom="Tache 2", duree_jours=5)
        ]
        
        ressources = [
            Ressource(ressource_id="R001", nom="Ressource 1", cout_journalier=Decimal("200.00")),
            Ressource(ressource_id="R002", nom="Ressource 2", cout_journalier=Decimal("300.00"))
        ]
        
        planning = Planning(
            planning_id="P001",
            mission_id="M001",
            nom="Planning Complet",
            date_debut=date_debut,
            date_fin=date_fin,
            taches=taches,
            ressources=ressources,
            duree_totale=15,
            cout_total=Decimal("7500.00"),
            chemin_critique=["T001"]
        )
        
        assert planning.taches == taches
        assert planning.ressources == ressources
        assert planning.duree_totale == 15
        assert planning.cout_total == Decimal("7500.00")
        assert planning.chemin_critique == ["T001"]

    def test_to_dict_simple(self):
        date_debut = date(2026, 8, 10)
        planning = Planning(
            planning_id="P001",
            mission_id="M001",
            nom="Test",
            date_debut=date_debut
        )
        result = planning.to_dict()
        
        assert result["planning_id"] == "P001"
        assert result["mission_id"] == "M001"
        assert result["nom"] == "Test"
        assert result["date_debut"] == "2026-08-10"
        assert result["date_fin"] is None
        assert result["duree_totale"] is None
        assert result["cout_total"] is None
        assert result["taches"] == []
        assert result["ressources"] == []

    def test_to_dict_with_all_fields(self):
        date_debut = date(2026, 8, 10)
        date_fin = date(2026, 8, 20)
        
        tache = Tache(
            tache_id="T001",
            nom="Tache Test",
            duree_jours=5,
            dependencies=["T002"],
            date_debut=date_debut,
            date_fin=date_fin,
            est_critique=True
        )
        
        ressource = Ressource(
            ressource_id="R001",
            nom="Ressource Test",
            type="humaine",
            cout_journalier=Decimal("200.00")
        )
        
        planning = Planning(
            planning_id="P001",
            mission_id="M001",
            nom="Test Complet",
            date_debut=date_debut,
            date_fin=date_fin,
            taches=[tache],
            ressources=[ressource],
            duree_totale=10,
            cout_total=Decimal("2000.00"),
            chemin_critique=["T001"]
        )
        
        result = planning.to_dict()
        
        assert result["date_fin"] == "2026-08-20"
        assert result["duree_totale"] == 10
        assert result["cout_total"] == 2000.0
        assert len(result["taches"]) == 1
        assert result["taches"][0]["tache_id"] == "T001"
        assert result["taches"][0]["nom"] == "Tache Test"
        assert result["taches"][0]["duree_jours"] == 5
        assert result["taches"][0]["dependencies"] == ["T002"]
        assert result["taches"][0]["date_debut"] == "2026-08-10"
        assert result["taches"][0]["date_fin"] == "2026-08-20"
        assert result["taches"][0]["est_critique"] is True
        
        assert len(result["ressources"]) == 1
        assert result["ressources"][0]["ressource_id"] == "R001"
        assert result["ressources"][0]["nom"] == "Ressource Test"
        assert result["ressources"][0]["type"] == "humaine"
        assert result["ressources"][0]["cout_journalier"] == 200.0


# =============================================================================
# TESTS POUR PlanningOptimisation
# =============================================================================

class TestPlanningOptimisation:
    def test_creation(self):
        planning_original = Planning(
            planning_id="P001",
            mission_id="M001",
            nom="Original",
            date_debut=date(2026, 8, 10)
        )
        
        planning_optimise = Planning(
            planning_id="P002",
            mission_id="M001",
            nom="Optimisé",
            date_debut=date(2026, 8, 10)
        )
        
        optimisation = PlanningOptimisation(
            planning_original=planning_original,
            planning_optimise=planning_optimise,
            duree_gagnee=5,
            cout_economise=Decimal("10000.00")
        )
        
        assert optimisation.planning_original == planning_original
        assert optimisation.planning_optimise == planning_optimise
        assert optimisation.duree_gagnee == 5
        assert optimisation.cout_economise == Decimal("10000.00")
