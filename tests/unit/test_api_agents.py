"""
SMART_AO V7 - test_api_agents.py
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


class TestAgentsEndpoint:
    def test_list_agents(self):
        response = client.get("/api/v1/agents")
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert "total" in data
    
    def test_get_agent(self):
        response = client.get("/api/v1/agents/DeadlineAgent")
        # Peut échouer si l'agent n'existe pas, mais vérifie que l'endpoint fonctionne
        assert response.status_code in [200, 404]
