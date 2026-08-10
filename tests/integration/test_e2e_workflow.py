"""
SMART_AO V7 - test_e2e_workflow.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Tests End-to-End Workflow
========================================
Tests end-to-end pour le workflow complet V7.

Source: PLAN_DE_CODAGE_PHASE_5_V7.md - Sprint 2 (Jour 4)
Cible: 8 tests End-to-End
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient
from app.main import app
from app.engines.workflow_engine.mission import Mission, MissionStatus
from app.engines.workflow_engine.workflow import Workflow
from app.engines.agent_runtime.registry import AgentRegistry, registry
from app.engines.event_bus.bus import EventBus

client = TestClient(app)


class TestE2EWorkflow:
    """Tests end-to-end pour le workflow V7."""
    
    def test_e2e_health_check(self):
        """Test end-to-end: vérification de santé."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_e2e_missions_list(self, override_auth_dependency):
        """Test end-to-end: liste des missions."""
        response = client.get("/api/v1/missions")
        assert response.status_code == 200
    
    def test_e2e_agents_list(self, override_auth_dependency):
        """Test end-to-end: liste des agents."""
        response = client.get("/api/v1/agents")
        assert response.status_code == 200
    
    def test_e2e_documents_endpoint(self, override_auth_dependency):
        """Test end-to-end: endpoint documents."""
        response = client.get("/api/v1/documents")
        assert response.status_code in [200, 404]
    
    def test_e2e_workflows_endpoint(self, override_auth_dependency):
        """Test end-to-end: endpoint workflows."""
        response = client.get("/api/v1/workflows")
        assert response.status_code in [200, 404]
    
    def test_e2e_full_system_integration(self):
        """Test end-to-end: intégration complète du système."""
        # Vérifier que tous les composants principaux sont accessibles
        assert registry is not None
        assert isinstance(registry, AgentRegistry)
        
        # Créer un event bus
        event_bus = EventBus()
        assert event_bus is not None
        
        # Créer une mission
        mission = Mission(
            documents=["test.pdf"],
            context={"test": "e2e"},
            created_by="e2e_test"
        )
        assert mission is not None
        assert mission.id is not None
        
        # Créer un workflow
        workflow = Workflow(mission)
        assert workflow is not None
        assert len(workflow.steps) == 6
    
    def test_e2e_error_handling(self):
        """Test end-to-end: gestion des erreurs."""
        # Tester un endpoint qui n'existe pas
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    def test_e2e_system_ready(self, override_auth_dependency):
        """Test end-to-end: système prêt pour production."""
        # Vérifier que le système répond correctement
        health_response = client.get("/api/v1/health")
        assert health_response.status_code == 200
        
        # Vérifier que l'API est fonctionnelle
        missions_response = client.get("/api/v1/missions")
        assert missions_response.status_code == 200
        
        # Vérifier que le registry est accessible
        agents_response = client.get("/api/v1/agents")
        assert agents_response.status_code == 200
