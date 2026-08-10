"""
SMART_AO V7 - test_integration.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
Tests d'intégration API-UI-MCP
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestAPIIntegration:
    """Tests d'intégration API."""
    
    def test_api_health_endpoint(self, override_auth_dependency):
        """Test que l'endpoint health fonctionne."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
        """Test que l'endpoint health fonctionne."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_api_missions_endpoint(self, override_auth_dependency):
        """Test que l'endpoint missions fonctionne."""
        response = client.get("/api/v1/missions")
        assert response.status_code == 200
        data = response.json()
        assert "missions" in data
        assert "total" in data
    
        """Test que l'endpoint missions fonctionne."""
        response = client.get("/api/v1/missions")
        assert response.status_code == 200
        data = response.json()
        assert "missions" in data
        assert "total" in data
    
    def test_api_agents_endpoint(self, override_auth_dependency):
        """Test que l'endpoint agents fonctionne."""
        response = client.get("/api/v1/agents")
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert "total" in data


        """Test que l'endpoint agents fonctionne."""
        response = client.get("/api/v1/agents")
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert "total" in data


class TestMCPToolsIntegration:
    """Tests d'intégration MCP Tools."""
    
    def test_mcp_tools_loaded(self):
        """Test que les outils MCP sont chargés."""
        from app.mcp.tools import mission_tools, agent_tools, document_tools
        
        mission_tools_list = mission_tools.get_tools()
        agent_tools_list = agent_tools.get_tools()
        document_tools_list = document_tools.get_tools()
        
        total = len(mission_tools_list) + len(agent_tools_list) + len(document_tools_list)
        assert total >= 10
    
        """Test que les outils MCP sont chargés."""
        from app.mcp.tools import mission_tools, agent_tools, document_tools
        
        mission_tools_list = mission_tools.get_tools()
        agent_tools_list = agent_tools.get_tools()
        document_tools_list = document_tools.get_tools()
        
        total = len(mission_tools_list) + len(agent_tools_list) + len(document_tools_list)
        assert total >= 10
    
    def test_mcp_server_initialization(self):
        """Test que le serveur MCP peut être initialisé."""
        from app.mcp.server import SMARTAOServer
        
        server = SMARTAOServer()
        assert server is not None


        """Test que le serveur MCP peut être initialisé."""
        from app.mcp.server import SMARTAOServer
        
        server = SMARTAOServer()
        assert server is not None


class TestUIIntegration:
    """Tests d'intégration UI."""
    
    def test_web_app_module_loaded(self):
        """Test que le module de l'app web se charge."""
        # Le module ne peut pas être testé directement car Streamlit
        # nécessite un contexte spécial, mais nous pouvons vérifier
        # que le fichier est syntaxiquement correct
        import ast
        import inspect
        
        # Lire le fichier app.py
        app_file = Path(project_root) / "app" / "web" / "app.py"
        with open(app_file, 'r') as f:
            source = f.read()
        
        # Parser le code
        try:
            ast.parse(source)
            assert True  # Le parsing a réussi
        except SyntaxError:
            assert False  # Le parsing a échoué
    
        """Test que le module de l'app web se charge."""
        # Le module ne peut pas être testé directement car Streamlit
        # nécessite un contexte spécial, mais nous pouvons vérifier
        # que le fichier est syntaxiquement correct
        import ast
        import inspect
        
        # Lire le fichier app.py
        app_file = Path(project_root) / "app" / "web" / "app.py"
        with open(app_file, 'r') as f:
            source = f.read()
        
        # Parser le code
        try:
            ast.parse(source)
            assert True  # Le parsing a réussi
        except SyntaxError:
            assert False  # Le parsing a échoué
    
    def test_web_pages_modules_loaded(self):
        """Test que les modules des pages web se chargent."""
        from app.web.pages import missions, agents, documents, analysis
        assert missions is not None
        assert agents is not None
        assert documents is not None
        assert analysis is not None


        """Test que les modules des pages web se chargent."""
        from app.web.pages import missions, agents, documents, analysis
        assert missions is not None
        assert agents is not None
        assert documents is not None
        assert analysis is not None


class TestFullIntegration:
    """Tests d'intégration complète."""
    
    def test_api_and_mcp_work_together(self, override_auth_dependency):
        """Test que l'API et le MCP peuvent coexister."""
        # Test API
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        # Test MCP tools loaded
        from app.mcp.tools import mission_tools
        tools = mission_tools.get_tools()
        assert len(tools) > 0
        
        # Les deux systèmes fonctionnent
        assert True
    
        """Test que l'API et le MCP peuvent coexister."""
        # Test API
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        # Test MCP tools loaded
        from app.mcp.tools import mission_tools
        tools = mission_tools.get_tools()
        assert len(tools) > 0
        
        # Les deux systèmes fonctionnent
        assert True
    
    def test_api_endpoints_consistency(self, override_auth_dependency):
        """Test la cohérence des endpoints API."""
        # Tous les endpoints doivent retourner 200
        endpoints = [
            "/api/v1/health",
            "/api/v1/missions",
            "/api/v1/agents",
            "/api/v1/documents",
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200, f"Endpoint {endpoint} failed"
    
        """Test la cohérence des endpoints API."""
        # Tous les endpoints doivent retourner 200
        endpoints = [
            "/api/v1/health",
            "/api/v1/missions",
            "/api/v1/agents",
            "/api/v1/documents",
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200, f"Endpoint {endpoint} failed"
    
    def test_api_response_structure(self, override_auth_dependency):
        """Test la structure des réponses API."""
        # Health endpoint
        response = client.get("/api/v1/health")
        data = response.json()
        assert "status" in data
        assert "version" in data
        
        # Missions endpoint
        response = client.get("/api/v1/missions")
        data = response.json()
        assert "missions" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        assert "total_pages" in data
    
        """Test la structure des réponses API."""
        # Health endpoint
        response = client.get("/api/v1/health")
        data = response.json()
        assert "status" in data
        assert "version" in data
        
        # Missions endpoint
        response = client.get("/api/v1/missions")
        data = response.json()
        assert "missions" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        assert "total_pages" in data
    
    def test_mcp_tools_count(self):
        """Test le nombre total d'outils MCP."""
        from app.mcp.tools import mission_tools, agent_tools, document_tools
        
        total_tools = (
            len(mission_tools.get_tools()) +
            len(agent_tools.get_tools()) +
            len(document_tools.get_tools())
        )
        
        # Doit avoir au moins 10 outils
        assert total_tools >= 10
        # Doit avoir exactement 13 outils (5 + 4 + 4)
        assert total_tools == 13
    
        """Test le nombre total d'outils MCP."""
        from app.mcp.tools import mission_tools, agent_tools, document_tools
        
        total_tools = (
            len(mission_tools.get_tools()) +
            len(agent_tools.get_tools()) +
            len(document_tools.get_tools())
        )
        
        # Doit avoir au moins 10 outils
        assert total_tools >= 10
        # Doit avoir exactement 13 outils (5 + 4 + 4)
        assert total_tools == 13
    
    def test_data_flow_api_to_mcp(self, override_auth_dependency):
        """Test le flux de données API → MCP."""
        # L'API doit pouvoir retourner des données
        # que le MCP peut consommer
        
        # Récupérer les missions de l'API
        response = client.get("/api/v1/missions")
        assert response.status_code == 200
        api_data = response.json()
        
        # Le MCP doit avoir des outils pour gérer les missions
        from app.mcp.tools import mission_tools
        mcp_tools = mission_tools.get_tools()
        
        # Vérifier qu'il y a des outils MCP pour les missions
        mission_tool_names = [tool.name for tool in mcp_tools]
        assert "list_missions" in mission_tool_names
        assert "create_mission" in mission_tool_names
        assert "get_mission" in mission_tool_names

        """Test le flux de données API → MCP."""
        # L'API doit pouvoir retourner des données
        # que le MCP peut consommer
        
        # Récupérer les missions de l'API
        response = client.get("/api/v1/missions")
        assert response.status_code == 200
        api_data = response.json()
        
        # Le MCP doit avoir des outils pour gérer les missions
        from app.mcp.tools import mission_tools
        mcp_tools = mission_tools.get_tools()
        
        # Vérifier qu'il y a des outils MCP pour les missions
        mission_tool_names = [tool.name for tool in mcp_tools]
        assert "list_missions" in mission_tool_names
        assert "create_mission" in mission_tool_names
        assert "get_mission" in mission_tool_names
