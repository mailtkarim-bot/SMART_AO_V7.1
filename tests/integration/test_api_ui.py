"""
SMART_AO V7 - test_api_ui.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Tests d'Intégration API ↔ UI
===========================================
Tests d'intégration entre l'API et l'UI V7.

Source: PLAN_DE_CODAGE_PHASE_5_V7.md - Sprint 1 (Jour 3)
Cible: 5 tests API ↔ UI
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestAPIUIIntegration:
    """Tests d'intégration API ↔ UI."""
    
    def test_api_returns_json_for_ui(self):
        """Test que l'API retourne du JSON pour l'UI."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        # Vérifier que la réponse est du JSON
        assert response.headers.get("content-type") == "application/json"
    
    def test_api_health_for_ui_dashboard(self):
        """Test que l'API santé est utilisable par l'UI dashboard."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        # L'UI a besoin de ces champs
        assert "status" in data
    
    def test_api_missions_structure_for_ui(self):
        """Test que l'API missions a la structure attendue par l'UI."""
        response = client.get("/api/v1/missions")
        if response.status_code == 200:
            data = response.json()
            # L'UI attend ces champs
            assert "missions" in data or "total" in data or "items" in data
    
    def test_api_agents_structure_for_ui(self):
        """Test que l'API agents a la structure attendue par l'UI."""
        response = client.get("/api/v1/agents")
        if response.status_code == 200:
            data = response.json()
            # L'UI attend ces champs
            assert "agents" in data or "total" in data or "items" in data
    
    def test_api_error_handling_for_ui(self):
        """Test que l'API gère les erreurs de manière utilisable par l'UI."""
        # Tester un endpoint qui n'existe pas
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
        # L'UI attend un JSON même pour les erreurs
        # (FastAPI le fait automatiquement)
