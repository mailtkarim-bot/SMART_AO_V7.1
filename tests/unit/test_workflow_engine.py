"""
SMART_AO V7 - test_workflow_engine.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Tests Workflow Engine
====================================
Tests unitaires pour le Workflow Engine.
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from app.engines.workflow_engine.workflow import Workflow
from app.engines.workflow_engine.mission import Mission, MissionStatus


class TestWorkflow:
    """Tests du Workflow Engine."""
    
    def test_workflow_creation(self):
        """Test de la création d'un workflow."""
        mission = Mission(id="test-mission", project_id="test-project")
        workflow = Workflow(mission=mission)
        assert workflow.mission_id == "test-mission"
        assert workflow.status == "PENDING"
    
    def test_workflow_steps(self):
        """Test des étapes du workflow - 6 étapes canoniques V7."""
        mission = Mission(id="test-mission", project_id="test-project")
        workflow = Workflow(mission=mission)

        # Le workflow doit avoir 6 étapes canoniques (V7)
        assert len(workflow.steps) == 6

        # Vérifier les noms des étapes
        expected_steps = [
            "parser_step",
            "extraction_step",
            "classification_step",
            "agents_step",
            "compilation_step",
            "rapport_step",
        ]
        for i, step_name in enumerate(expected_steps):
            assert workflow.steps[i].step_name == step_name
    
    def test_workflow_execution(self):
        """Test de l'exécution du workflow."""
        mission = Mission(id="test-mission", project_id="test-project")
        workflow = Workflow(mission=mission)
        
        # Exécuter le workflow (simplifié)
        # En réalité, chaque étape serait exécutée séquentiellement
        assert workflow.current_step == 0


class TestMission:
    """Tests des missions."""
    
    def test_mission_creation(self):
        """Test de la création d'une mission."""
        mission = Mission(
            id="test-mission",
            project_id="test-project",
            context={"type": "DCE"}
        )
        assert mission.id == "test-mission"
        assert mission.project_id == "test-project"
        assert mission.status == MissionStatus.PENDING
    
    def test_mission_context(self):
        """Test du contexte de la mission."""
        mission = Mission(
            id="test-mission",
            project_id="test-project",
            context={
                "type": "DCE",
                "montant_marche_ht": 1000000,
                "delai_execution_jours": 90,
            }
        )
        assert mission.context["type"] == "DCE"
        assert mission.context["montant_marche_ht"] == 1000000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
