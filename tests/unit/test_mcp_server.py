"""
SMART_AO V7 - test_mcp_server.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
Tests d'intégration pour le MCP Server
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from app.mcp.tools import mission_tools, agent_tools, document_tools


class TestMCPTools:
    def test_all_tools_loaded(self):
        """Test que tous les outils MCP sont chargés."""
        mission_tools_list = mission_tools.get_tools()
        agent_tools_list = agent_tools.get_tools()
        document_tools_list = document_tools.get_tools()
        
        assert len(mission_tools_list) > 0
        assert len(agent_tools_list) > 0
        assert len(document_tools_list) > 0
        
        total_tools = len(mission_tools_list) + len(agent_tools_list) + len(document_tools_list)
        assert total_tools >= 10
    
    def test_mission_tools_structure(self):
        """Test la structure des outils missions."""
        tools = mission_tools.get_tools()
        
        for tool in tools:
            assert hasattr(tool, 'name')
            assert hasattr(tool, 'description')
            # MCP 2.0 Tool n'a pas func, mais a input_schema
            assert hasattr(tool, 'input_schema') or hasattr(tool, 'inputSchema')
    
    def test_agent_tools_structure(self):
        """Test la structure des outils agents."""
        tools = agent_tools.get_tools()
        
        for tool in tools:
            assert hasattr(tool, 'name')
            assert hasattr(tool, 'description')
            assert hasattr(tool, 'input_schema') or hasattr(tool, 'inputSchema')
    
    def test_document_tools_structure(self):
        """Test la structure des outils documents."""
        tools = document_tools.get_tools()
        
        for tool in tools:
            assert hasattr(tool, 'name')
            assert hasattr(tool, 'description')
            assert hasattr(tool, 'input_schema') or hasattr(tool, 'inputSchema')


class TestMCPServerInitialization:
    def test_server_creation(self):
        """Test la création du serveur MCP."""
        from app.mcp.server import SMARTAOServer
        
        server = SMARTAOServer()
        assert server is not None
        assert server.host == "0.0.0.0"
        assert server.port == 8080
        assert server.mcp_server is None
    
    def test_server_with_custom_host_port(self):
        """Test le serveur MCP avec host/port personnalisés."""
        from app.mcp.server import SMARTAOServer
        
        server = SMARTAOServer(host="127.0.0.1", port=9090)
        assert server.host == "127.0.0.1"
        assert server.port == 9090


class TestMCPToolFunctions:
    """Tests pour les fonctions des outils MCP."""
    
    def test_mission_tool_functions_exist(self):
        """Test que les fonctions des outils missions existent."""
        from app.mcp.tools import mission_tools
        
        # Vérifier que les fonctions internes existent
        assert hasattr(mission_tools, '_create_mission')
        assert hasattr(mission_tools, '_list_missions')
        assert hasattr(mission_tools, '_get_mission')
        assert hasattr(mission_tools, '_execute_workflow')
        assert hasattr(mission_tools, '_get_workflow_status')
    
    def test_agent_tool_functions_exist(self):
        """Test que les fonctions des outils agents existent."""
        from app.mcp.tools import agent_tools
        
        assert hasattr(agent_tools, '_list_agents')
        assert hasattr(agent_tools, '_get_agent')
        assert hasattr(agent_tools, '_run_agent')
        assert hasattr(agent_tools, '_get_agent_capabilities')
    
    def test_document_tool_functions_exist(self):
        """Test que les fonctions des outils documents existent."""
        from app.mcp.tools import document_tools
        
        assert hasattr(document_tools, '_upload_document')
        assert hasattr(document_tools, '_list_documents')
        assert hasattr(document_tools, '_get_document')
        assert hasattr(document_tools, '_delete_document')
    
    @pytest.mark.asyncio
    async def test_mission_tool_function_calls(self):
        """Test l'exécution des fonctions des outils missions."""
        from app.mcp.tools import mission_tools
        
        # Tester _list_missions
        result = await mission_tools._list_missions()
        assert isinstance(result, dict)
        assert "missions" in result
        assert "total" in result
    
    @pytest.mark.asyncio
    async def test_agent_tool_function_calls(self):
        """Test l'exécution des fonctions des outils agents."""
        from app.mcp.tools import agent_tools
        
        # Tester _list_agents
        result = await agent_tools._list_agents()
        assert isinstance(result, dict)
        assert "agents" in result
        assert "total" in result
    
    @pytest.mark.asyncio
    async def test_document_tool_function_calls(self):
        """Test l'exécution des fonctions des outils documents."""
        from app.mcp.tools import document_tools
        
        # Tester _list_documents
        result = await document_tools._list_documents()
        assert isinstance(result, dict)
        assert "documents" in result
        assert "total" in result
