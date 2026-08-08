"""
SMART_AO V7 - test_api_workflows.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
Tests unitaires pour les endpoints Workflows API V1
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from app.main import app

client = TestClient(app)


class TestWorkflowsEndpoint:
    """Tests pour l'endpoint /api/v1/workflows."""
    
    def test_get_workflow_status(self):
        """Test la récupération du statut du workflow."""
        mission_id = "test_mission_001"
        response = client.get(f"/api/v1/workflows/{mission_id}/status")
        assert response.status_code == 200
        data = response.json()
        assert "mission_id" in data
        assert data["mission_id"] == mission_id
        assert "current_step" in data
        assert "total_steps" in data
        assert "completed_steps" in data
        assert "status" in data
    
    def test_get_workflow_status_missing_mission(self):
        """Test le statut avec une mission inexistante."""
        response = client.get("/api/v1/workflows/missing_mission/status")
        assert response.status_code == 200
        # Devrait retourner un statut par défaut
        data = response.json()
        assert "mission_id" in data
    
    def test_execute_workflow(self):
        """Test l'exécution d'un workflow."""
        mission_id = "test_mission_001"
        response = client.post(f"/api/v1/workflows/{mission_id}/execute")
        assert response.status_code == 200
        data = response.json()
        assert "mission_id" in data
        assert data["mission_id"] == mission_id
        assert "execution_id" in data
        assert "started_at" in data
        assert "status" in data
        assert data["status"] == "STARTED"
    
    def test_execute_workflow_missing_mission(self):
        """Test l'exécution avec une mission inexistante."""
        response = client.post("/api/v1/workflows/missing_mission/execute")
        assert response.status_code == 200
        data = response.json()
        assert "mission_id" in data


class TestWorkflowIntegration:
    """Tests d'intégration workflow."""
    
    def test_workflow_status_structure(self):
        """Test la structure complète du statut workflow."""
        mission_id = "integration_test_001"
        response = client.get(f"/api/v1/workflows/{mission_id}/status")
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier tous les champs requis
        required_fields = ["mission_id", "current_step", "total_steps", "completed_steps", "status"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
    
    def test_workflow_execution_structure(self):
        """Test la structure complète de l'exécution workflow."""
        mission_id = "integration_test_001"
        response = client.post(f"/api/v1/workflows/{mission_id}/execute")
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier tous les champs requis
        required_fields = ["mission_id", "execution_id", "started_at", "status"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
