"""
SMART_AO V7 - test_api_missions.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from app.main import app

client = TestClient(app)


class TestMissionsEndpoint:
    def test_list_missions(self, override_auth_dependency):
        response = client.get("/api/v1/missions")
        assert response.status_code == 200
        data = response.json()
        assert "missions" in data
        assert "total" in data
    
    def test_create_mission(self, override_auth_dependency):
        data = {
            "name": "Test Mission",
            "mission_type": "analysis",
            "description": "Test mission for API",
            "priority": 1,
        }
        response = client.post("/api/v1/missions", json=data)
        assert response.status_code == 201
        # Vérifier la structure de la réponse
        assert "id" in response.json()
        assert "name" in response.json()
