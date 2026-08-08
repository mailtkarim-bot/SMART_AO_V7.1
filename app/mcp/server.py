"""
SMART_AO V7 - server.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 MCP Server
=====================
MCP Server pour SMART_AO V7 Engine OS.
Utilise MCP Server 2.0 API avec add_tool.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from app.mcp.tools import mission_tools, agent_tools, document_tools

logger = logging.getLogger(__name__)


class SMARTAOServer:
    '''MCP Server pour SMART_AO V7 Engine OS.'''
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        self.host = host
        self.port = port
        self.mcp_server: Optional[FastMCP] = None
    
    async def initialize(self) -> FastMCP:
        '''Initialiser le serveur MCP et registrer tous les outils.'''
        logger.info("Initializing SMART_AO V7 MCP Server...")
        
        # Créer le serveur MCP via FastMCP (API mcp>=1.0)
        server = FastMCP(
            name="SMART_AO V7 Engine OS",
            debug=True,
        )
        
        # Dictionnaire de mappings nom -> fonction
        tool_functions = {
            # Mission tools
            "create_mission": mission_tools._create_mission,
            "list_missions": mission_tools._list_missions,
            "get_mission": mission_tools._get_mission,
            "execute_workflow": mission_tools._execute_workflow,
            "get_workflow_status": mission_tools._get_workflow_status,
            # Agent tools
            "list_agents": agent_tools._list_agents,
            "get_agent": agent_tools._get_agent,
            "run_agent": agent_tools._run_agent,
            "get_agent_capabilities": agent_tools._get_agent_capabilities,
            # Document tools
            "upload_document": document_tools._upload_document,
            "list_documents": document_tools._list_documents,
            "get_document": document_tools._get_document,
            "delete_document": document_tools._delete_document,
        }
        
        # Charger tous les outils depuis les modules
        all_tools = [
            *mission_tools.get_tools(),
            *agent_tools.get_tools(),
            *document_tools.get_tools(),
        ]
        
        # Enregistrer chaque outil avec add_tool
        for tool in all_tools:
            try:
                tool_name = tool.name
                tool_func = tool_functions.get(tool_name)
                
                if tool_func:
                    server.add_tool(
                        fn=tool_func,
                        name=tool_name,
                        description=tool.description,
                    )
                    logger.info(f"Registered MCP tool: {tool_name}")
                else:
                    logger.warning(f"No function found for tool: {tool_name}")
            except Exception as e:
                logger.error(f"Failed to register tool {tool.name}: {e}")
        
        logger.info(f"Loaded {len(all_tools)} MCP tools")
        return server
    
    async def start(self) -> None:
        '''Démarrer le serveur MCP.'''
        logger.info(f"Starting MCP server on {self.host}:{self.port}")
        
        # Initialiser
        self.mcp_server = await self.initialize()
        
        # Démarrer le serveur en mode stdio
        logger.info("MCP Server started successfully")
        await self.mcp_server.run_stdio_async()
    
    async def stop(self) -> None:
        '''Arrêter le serveur MCP.'''
        logger.info("MCP Server stopped")


# Instance singleton
mcp_server = SMARTAOServer()


if __name__ == "__main__":
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    # Parsing des arguments
    host = sys.argv[1] if len(sys.argv) > 1 else "0.0.0.0"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
    
    server = SMARTAOServer(host=host, port=port)
    asyncio.run(server.start())
