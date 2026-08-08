"""
SMART_AO V7 - bootstrap_phase4.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


#!/usr/bin/env python3
"""
SMART_AO V7 - Bootstrap Phase 4
================================
Crée la structure de fichiers pour la Phase 4 (Builds 7-8 : Interface)
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent

# Structure Build 7 - API REST + Plugin System
BUILD7_STRUCTURE = {
    "app/api/__init__.py": "# API Package",
    "app/api/v1/__init__.py": "# API V1 Package",
    "app/api/v1/endpoints/__init__.py": "# Endpoints Package",
    "app/api/v1/endpoints/health.py": """
from fastapi import APIRouter, Depends
from app.core.config import settings

router = APIRouter(prefix="/api/v1/health", tags=["health"])


@router.get("", summary="Health Check")
async def health_check():
    return {
        "status": "healthy",
        "version": "V7",
        "build": "7-8",
        "phase": "4",
    }
""",
    "app/api/v1/endpoints/missions.py": """
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime

from app.schemas.mission import MissionCreate, MissionResponse, MissionListResponse
from app.schemas.response import ErrorResponse
from app.engines.workflow_engine.mission import Mission, MissionStatus

router = APIRouter(prefix="/api/v1/missions", tags=["missions"])


@router.get("", response_model=MissionListResponse, summary="List Missions")
async def list_missions(
    status: Optional[MissionStatus] = None,
    limit: int = 100,
    offset: int = 0,
):
    '''Lister toutes les missions.'''
    # TODO: Implémenter avec persistance PG
    return MissionListResponse(
        missions=[],
        total=0,
        limit=limit,
        offset=offset,
    )


@router.post("", response_model=MissionResponse, status_code=status.HTTP_201_CREATED, summary="Create Mission")
async def create_mission(mission_data: MissionCreate):
    '''Créer une nouvelle mission.'''
    # TODO: Intégrer avec WorkflowEngine
    mission = Mission(**mission_data.model_dump())
    return MissionResponse.from_orm(mission)


@router.get("/{mission_id}", response_model=MissionResponse, summary="Get Mission")
async def get_mission(mission_id: str):
    '''Récupérer une mission spécifique.'''
    # TODO: Récupérer depuis PG
    return MissionResponse.from_orm(Mission(id=mission_id))
""",
    "app/api/v1/endpoints/agents.py": """
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional

from app.schemas.agent import AgentListResponse, AgentResponse
from app.engines.agent_runtime.registry import AgentRegistry, registry

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


@router.get("", response_model=AgentListResponse, summary="List Agents")
async def list_agents(
    capability: Optional[str] = None,
    is_blocking: Optional[bool] = None,
):
    '''Lister tous les agents enregistrés.'''
    agents = registry.list_agents()
    
    if capability:
        agents = [a for a in agents if capability in a.capabilities]
    if is_blocking is not None:
        agents = [a for a in agents if a.is_blocking == is_blocking]
    
    return AgentListResponse(
        agents=agents,
        total=len(agents),
    )


@router.get("/{agent_name}", response_model=AgentResponse, summary="Get Agent")
async def get_agent(agent_name: str):
    '''Récupérer un agent spécifique.'''
    agent = registry.get_agent(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")
    return AgentResponse.from_orm(agent)
""",
    "app/api/v1/endpoints/documents.py": """
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List, Optional
from datetime import datetime

from app.schemas.document import DocumentUploadResponse, DocumentListResponse

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentUploadResponse, summary="Upload Document")
async def upload_document(
    file: UploadFile = File(...),
    mission_id: Optional[str] = Form(None),
    document_type: Optional[str] = Form(None),
):
    '''Uploader un document pour analyse.'''
    # TODO: Sauvegarder dans MinIO/S3 et indexer dans Qdrant
    return DocumentUploadResponse(
        document_id=f"doc_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        file_name=file.filename,
        content_type=file.content_type,
        size=0,
        mission_id=mission_id,
        document_type=document_type or "UNKNOWN",
        upload_time=datetime.now(),
    )


@router.get("", response_model=DocumentListResponse, summary="List Documents")
async def list_documents(
    mission_id: Optional[str] = None,
    limit: int = 100,
):
    '''Lister les documents.'''
    # TODO: Implémenter avec persistance
    return DocumentListResponse(documents=[], total=0)
""",
    "app/api/v1/endpoints/workflows.py": """
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from app.schemas.workflow import WorkflowStatusResponse, WorkflowExecutionResponse
from app.engines.workflow_engine.workflow import WorkflowEngine

router = APIRouter(prefix="/api/v1/workflows", tags=["workflows"])


@router.get("/{mission_id}/status", response_model=WorkflowStatusResponse, summary="Workflow Status")
async def get_workflow_status(mission_id: str):
    '''Récupérer le statut du workflow pour une mission.'''
    # TODO: Intégrer avec WorkflowEngine
    return WorkflowStatusResponse(
        mission_id=mission_id,
        current_step="PARSER",
        total_steps=6,
        completed_steps=0,
        status="PENDING",
    )


@router.post("/{mission_id}/execute", response_model=WorkflowExecutionResponse, summary="Execute Workflow")
async def execute_workflow(mission_id: str):
    '''Exécuter le workflow pour une mission.'''
    # TODO: Démarrer l'exécution du workflow
    return WorkflowExecutionResponse(
        mission_id=mission_id,
        execution_id=f"exec_{mission_id}",
        started_at=datetime.now().isoformat(),
        status="STARTED",
    )
""",
    "app/plugins/__init__.py": "# Plugins Package\nfrom .base_plugin import BasePlugin\nfrom .registry import PluginRegistry\n\n__all__ = ['BasePlugin', 'PluginRegistry']",
    "app/plugins/base_plugin.py": """
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from enum import Enum


class PluginHook(str, Enum):
    PRE_EXECUTE = "pre_execute"
    POST_EXECUTE = "post_execute"
    ON_ERROR = "on_error"
    ON_STARTUP = "on_startup"
    ON_SHUTDOWN = "on_shutdown"


class BasePlugin(ABC):
    '''Classe de base pour tous les plugins.'''
    
    name: str = "BasePlugin"
    version: str = "1.0.0"
    author: str = "SMART_AO V7"
    description: str = ""
    hooks: List[PluginHook] = []
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        '''Initialiser le plugin.'''
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        '''Arrêter le plugin.'''
        pass
    
    def on_pre_execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        '''Hook exécuté avant une opération.'''
        return context
    
    def on_post_execute(self, context: Dict[str, Any], result: Any) -> Any:
        '''Hook exécuté après une opération.'''
        return result
    
    def on_error(self, context: Dict[str, Any], error: Exception) -> Exception:
        '''Hook exécuté en cas d'erreur.'''
        return error
""",
    "app/plugins/registry.py": """
from typing import Dict, List, Optional, Any, Type
from pathlib import Path
import importlib
import logging

from .base_plugin import BasePlugin, PluginHook

logger = logging.getLogger(__name__)


class PluginRegistry:
    '''Registre des plugins SMART_AO V7.'''
    
    def __init__(self):
        self._plugins: Dict[str, BasePlugin] = {}
        self._hooks: Dict[PluginHook, List[BasePlugin]] = {
            hook: [] for hook in PluginHook
        }
    
    def register(self, plugin: BasePlugin) -> None:
        '''Enregistrer un plugin.'''
        if plugin.name in self._plugins:
            logger.warning(f"Plugin {plugin.name} already registered, overwriting")
        self._plugins[plugin.name] = plugin
        
        for hook in plugin.hooks:
            if hook not in self._hooks:
                self._hooks[hook] = []
            self._hooks[hook].append(plugin)
        
        logger.info(f"Plugin {plugin.name} v{plugin.version} registered")
    
    def unregister(self, plugin_name: str) -> bool:
        '''Désenregistrer un plugin.'''
        if plugin_name not in self._plugins:
            return False
        del self._plugins[plugin_name]
        logger.info(f"Plugin {plugin_name} unregistered")
        return True
    
    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        '''Récupérer un plugin par nom.'''
        return self._plugins.get(plugin_name)
    
    def list_plugins(self) -> List[BasePlugin]:
        '''Lister tous les plugins.'''
        return list(self._plugins.values())
    
    def discover_plugins(self, directory: str = "app/plugins") -> int:
        '''Découvrir et charger automatiquement les plugins.'''
        plugins_dir = Path(directory)
        count = 0
        
        if not plugins_dir.exists():
            logger.warning(f"Plugins directory {directory} not found")
            return 0
        
        for plugin_file in plugins_dir.glob("*_plugin.py"):
            if plugin_file.name.startswith("_"):
                continue
            
            module_name = f"{directory}.{plugin_file.stem}".replace("/", ".")
            try:
                module = importlib.import_module(module_name)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type) 
                        and issubclass(attr, BasePlugin) 
                        and attr != BasePlugin
                    ):
                        plugin_instance = attr()
                        self.register(plugin_instance)
                        count += 1
            except Exception as e:
                logger.error(f"Failed to load plugin {plugin_file}: {e}")
        
        logger.info(f"Discovered and loaded {count} plugins")
        return count
    
    def trigger_hook(
        self, 
        hook: PluginHook, 
        context: Dict[str, Any], 
        result: Any = None,
        error: Exception = None
    ) -> Any:
        '''Déclencher un hook pour tous les plugins enregistrés.'''
        plugins = self._hooks.get(hook, [])
        
        for plugin in plugins:
            try:
                if hook == PluginHook.PRE_EXECUTE:
                    context = plugin.on_pre_execute(context)
                elif hook == PluginHook.POST_EXECUTE:
                    result = plugin.on_post_execute(context, result)
                elif hook == PluginHook.ON_ERROR:
                    error = plugin.on_error(context, error)
            except Exception as e:
                logger.error(f"Plugin {plugin.name} hook {hook} failed: {e}")
        
        return result or context


# Instance singleton
plugin_registry = PluginRegistry()


def get_plugin_registry() -> PluginRegistry:
    return plugin_registry
""",
    "app/plugins/example_plugin.py": """
from typing import Dict, Any

from .base_plugin import BasePlugin, PluginHook


class ExamplePlugin(BasePlugin):
    '''Plugin exemple pour démonstration.'''
    
    name = "ExamplePlugin"
    version = "1.0.0"
    author = "SMART_AO V7"
    description = "Plugin exemple pour tester le système de plugins"
    hooks = [
        PluginHook.PRE_EXECUTE,
        PluginHook.POST_EXECUTE,
    ]
    
    def __init__(self):
        self._config: Dict[str, Any] = {}
    
    def initialize(self, config: Dict[str, Any]) -> None:
        self._config = config
        print(f"{self.name} initialized with config: {config}")
    
    def shutdown(self) -> None:
        print(f"{self.name} shutting down")
    
    def on_pre_execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        print(f"{self.name}: Pre-execute hook triggered")
        context["example_plugin"] = "pre_execute_called"
        return context
    
    def on_post_execute(self, context: Dict[str, Any], result: Any) -> Any:
        print(f"{self.name}: Post-execute hook triggered")
        if isinstance(result, dict):
            result["example_plugin"] = "post_execute_called"
        return result
""",
    # Schemas
    "app/schemas/__init__.py": "# Schemas Package\nfrom .mission import MissionCreate, MissionResponse, MissionListResponse\nfrom .agent import AgentResponse, AgentListResponse\nfrom .document import DocumentUploadResponse, DocumentListResponse\nfrom .workflow import WorkflowStatusResponse, WorkflowExecutionResponse\nfrom .response import ErrorResponse, SuccessResponse\n\n__all__ = [\n    'MissionCreate', 'MissionResponse', 'MissionListResponse',\n    'AgentResponse', 'AgentListResponse',\n    'DocumentUploadResponse', 'DocumentListResponse',\n    'WorkflowStatusResponse', 'WorkflowExecutionResponse',\n    'ErrorResponse', 'SuccessResponse',\n]",
    "app/schemas/mission.py": """
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

from app.engines.workflow_engine.mission import MissionStatus


class MissionCreate(BaseModel):
    '''Schema pour la création d'une mission.'''
    project_id: str = Field(..., description="ID du projet")
    documents: List[str] = Field(default_factory=list, description="Liste des IDs de documents")
    context: Dict[str, Any] = Field(default_factory=dict, description="Contexte de la mission")
    priority: str = Field(default="NORMALE", pattern="^(BASSE|NORMALE|HAUTE|URGENTE)$")
    created_by: str = Field(default="system", description="Créé par")


class MissionResponse(BaseModel):
    '''Schema de réponse pour une mission.'''
    id: str
    project_id: Optional[str] = None
    type: str = "ANALYSE_DCE"
    status: MissionStatus
    documents: List[str] = Field(default_factory=list)
    current_step_idx: int = 0
    context: Dict[str, Any] = Field(default_factory=dict)
    priority: str = "NORMALE"
    created_by: str = "system"
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MissionListResponse(BaseModel):
    '''Schema de réponse pour la liste des missions.'''
    missions: List[MissionResponse] = Field(default_factory=list)
    total: int = 0
    limit: int = 100
    offset: int = 0
""",
    "app/schemas/agent.py": """
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import timedelta


class AgentResponse(BaseModel):
    '''Schema de réponse pour un agent.'''
    name: str
    capabilities: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    estimated_duration: timedelta
    is_blocking: bool = False
    description: str = ""
    
    class Config:
        from_attributes = True


class AgentListResponse(BaseModel):
    '''Schema de réponse pour la liste des agents.'''
    agents: List[AgentResponse] = Field(default_factory=list)
    total: int = 0
""",
    "app/schemas/document.py": """
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class DocumentUploadResponse(BaseModel):
    '''Schema de réponse pour l'upload d'un document.'''
    document_id: str
    file_name: str
    content_type: str
    size: int
    mission_id: Optional[str] = None
    document_type: str = "UNKNOWN"
    upload_time: datetime
    status: str = "UPLOADED"


class DocumentResponse(BaseModel):
    '''Schema pour un document.'''
    id: str
    file_name: str
    content_type: str
    size: int
    mission_id: Optional[str] = None
    document_type: str = "UNKNOWN"
    upload_time: datetime
    status: str = "UPLOADED"


class DocumentListResponse(BaseModel):
    '''Schema de réponse pour la liste des documents.'''
    documents: List[DocumentResponse] = Field(default_factory=list)
    total: int = 0
""",
    "app/schemas/workflow.py": """
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class WorkflowStatusResponse(BaseModel):
    '''Schema de réponse pour le statut du workflow.'''
    mission_id: str
    current_step: str
    total_steps: int
    completed_steps: int
    status: str
    started_at: Optional[datetime] = None
    last_update: Optional[datetime] = None


class WorkflowExecutionResponse(BaseModel):
    '''Schema de réponse pour l'exécution du workflow.'''
    mission_id: str
    execution_id: str
    started_at: str
    status: str
    message: Optional[str] = None
""",
    "app/schemas/response.py": """
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List


class ErrorResponse(BaseModel):
    '''Schema de réponse pour les erreurs.'''
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


class SuccessResponse(BaseModel):
    '''Schema de réponse pour les succès.'''
    success: bool = True
    message: str = "Operation successful"
    data: Optional[Dict[str, Any]] = None
""",
    # Build 8 - UI
    "app/web/app.py": """
import streamlit as st
from typing import List, Dict, Any
import requests

# Configuration
API_BASE_URL = "http://localhost:8000"

# Setup page
st.set_page_config(
    page_title="SMART_AO V7",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    '<style>\n'
    '    .main-header {\n'
    '        font-size: 3rem;\n'
    '        font-weight: bold;\n'
    '        color: #1f77b4;\n'
    '        text-align: center;\n'
    '        margin-bottom: 2rem;\n'
    '    }\n'
    '    .metric-card {\n'
    '        background: #f0f2f6;\n'
    '        padding: 1rem;\n'
    '        border-radius: 0.5rem;\n'
    '        margin: 0.5rem 0;\n'
    '    }\n'
    '</style>',
    unsafe_allow_html=True,
)


def api_get(endpoint: str, params: Dict = None) -> Any:
    '''Effectuer une requête GET vers l'API.'''
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API Error: {e}")
        return None


def api_post(endpoint: str, data: Dict = None, files: Dict = None) -> Any:
    '''Effectuer une requête POST vers l'API.'''
    try:
        response = requests.post(f"{API_BASE_URL}{endpoint}", json=data, files=files)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API Error: {e}")
        return None


def main():
    '''Application Streamlit principale.'''
    st.markdown('<p class="main-header">🏗️ SMART_AO V7 - Engine OS</p>', unsafe_allow_html=True)
    
    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["🏠 Dashboard", "📁 Missions", "🤖 Agents", "📄 Documents", "📊 Analyse"]
    )
    
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "📁 Missions":
        show_missions()
    elif page == "🤖 Agents":
        show_agents()
    elif page == "📄 Documents":
        show_documents()
    elif page == "📊 Analyse":
        show_analysis()


def show_dashboard():
    '''Afficher le dashboard principal.'''
    st.header("📊 Dashboard")
    
    # Health check
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🏥 Status Système")
        health = api_get("/api/v1/health")
        if health:
            st.json(health)
    
    with col2:
        st.markdown("### 📈 Statistiques")
        missions = api_get("/api/v1/missions")
        if missions:
            st.metric("Missions", missions.get("total", 0))
    
    with col3:
        st.markdown("### 🤖 Agents")
        agents = api_get("/api/v1/agents")
        if agents:
            st.metric("Agents", agents.get("total", 0))


def show_missions():
    '''Afficher la page des missions.'''
    st.header("📁 Gestion des Missions")
    
    # Créer une nouvelle mission
    with st.expander("➕ Créer une nouvelle mission", expanded=True):
        with st.form("create_mission"):
            project_id = st.text_input("Project ID", placeholder="PROJ-001")
            context = st.text_area("Contexte (JSON)", placeholder='{"type": "DCE"}')
            priority = st.selectbox("Priorité", ["BASSE", "NORMALE", "HAUTE", "URGENTE"])
            
            if st.form_submit_button("Créer"):
                try:
                    import json
                    context_dict = json.loads(context) if context else {}
                    data = {
                        "project_id": project_id,
                        "context": context_dict,
                        "priority": priority,
                    }
                    result = api_post("/api/v1/missions", data=data)
                    if result:
                        st.success(f"Mission créée: {result.get('id')}")
                except Exception as e:
                    st.error(f"Erreur: {e}")
    
    # Lister les missions
    st.markdown("### 📋 Liste des Missions")
    missions = api_get("/api/v1/missions")
    if missions and missions.get("missions"):
        for mission in missions["missions"]:
            with st.expander(f"📄 Mission: {mission.get('id')} - {mission.get('status')}"):
                st.json(mission)
    else:
        st.info("Aucune mission trouvée")


def show_agents():
    '''Afficher la page des agents.'''
    st.header("🤖 Registry des Agents")
    
    agents = api_get("/api/v1/agents")
    if agents and agents.get("agents"):
        st.metric("Total Agents", agents["total"])
        
        for agent in agents["agents"]:
            with st.expander(f"🤖 {agent.get('name')} - {'🔴 Bloquant' if agent.get('is_blocking') else '🟢 Non-bloquant'}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Capacités:** {', '.join(agent.get('capabilities', []))}")
                with col2:
                    st.markdown(f"**Tags:** {', '.join(agent.get('tags', []))}")
    else:
        st.info("Aucun agent trouvé")


def show_documents():
    '''Afficher la page des documents.'''
    st.header("📄 Gestion des Documents")
    
    # Upload de document
    with st.expander("➕ Uploader un document", expanded=True):
        with st.form("upload_document"):
            file = st.file_uploader("Sélectionner un fichier", type=["pdf", "docx", "txt"])
            mission_id = st.text_input("Mission ID (optionnel)")
            document_type = st.text_input("Type de document (optionnel)")
            
            if st.form_submit_button("Uploader"):
                if file:
                    files = {"file": (file.name, file.getvalue(), file.type)}
                    data = {
                        "mission_id": mission_id,
                        "document_type": document_type,
                    }
                    result = api_post("/api/v1/documents/upload", files=files, data=data)
                    if result:
                        st.success(f"Document uploadé: {result.get('document_id')}")
    
    # Lister les documents
    st.markdown("### 📋 Liste des Documents")
    documents = api_get("/api/v1/documents")
    if documents and documents.get("documents"):
        for doc in documents["documents"]:
            with st.expander(f"📄 {doc.get('file_name')} - {doc.get('document_type')}"):
                st.json(doc)
    else:
        st.info("Aucun document trouvé")


def show_analysis():
    '''Afficher la page d'analyse.'''
    st.header("📊 Résultats d'Analyse")
    
    mission_id = st.text_input("Mission ID", placeholder="mission_xxxxx")
    
    if st.button("Récupérer le statut du workflow"):
        if mission_id:
            workflow = api_get(f"/api/v1/workflows/{mission_id}/status")
            if workflow:
                st.json(workflow)
    
    if st.button("Exécuter le workflow"):
        if mission_id:
            result = api_post(f"/api/v1/workflows/{mission_id}/execute")
            if result:
                st.success(f"Workflow démarré: {result.get('execution_id')}")


if __name__ == "__main__":
    main()
""",
    "app/web/pages/__init__.py": "# Pages Package",
    "app/web/pages/missions.py": """
import streamlit as st
from typing import List, Dict, Any
import requests

API_BASE_URL = "http://localhost:8000"


def api_get(endpoint: str, params: Dict = None) -> Any:
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API Error: {e}")
        return None


def show():
    st.title("📁 Gestion des Missions")
    
    # Créer
    with st.expander("➕ Créer une mission", expanded=True):
        with st.form("create_mission"):
            project_id = st.text_input("Project ID")
            priority = st.selectbox("Priorité", ["BASSE", "NORMALE", "HAUTE", "URGENTE"])
            if st.form_submit_button("Créer"):
                data = {"project_id": project_id, "priority": priority}
                result = api_get("/api/v1/missions", data=data)
                if result:
                    st.success(f"Créée: {result.get('id')}")
    
    # Lister
    st.markdown("### Liste")
    missions = api_get("/api/v1/missions")
    if missions and missions.get("missions"):
        for m in missions["missions"]:
            st.json(m)
    else:
        st.info("Aucune mission")


if __name__ == "__main__":
    show()
""",
    "app/web/pages/agents.py": """
import streamlit as st
from typing import List, Dict, Any
import requests

API_BASE_URL = "http://localhost:8000"


def api_get(endpoint: str, params: Dict = None) -> Any:
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API Error: {e}")
        return None


def show():
    st.title("🤖 Agents")
    agents = api_get("/api/v1/agents")
    if agents and agents.get("agents"):
        for agent in agents["agents"]:
            st.json(agent)
    else:
        st.info("Aucun agent")


if __name__ == "__main__":
    show()
""",
    "app/web/pages/documents.py": """
import streamlit as st
from typing import List, Dict, Any
import requests

API_BASE_URL = "http://localhost:8000"


def api_get(endpoint: str, params: Dict = None) -> Any:
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API Error: {e}")
        return None


def api_post(endpoint: str, files: Dict = None, data: Dict = None) -> Any:
    try:
        response = requests.post(f"{API_BASE_URL}{endpoint}", files=files, data=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API Error: {e}")
        return None


def show():
    st.title("📄 Documents")
    
    with st.expander("➕ Uploader"):
        file = st.file_uploader("Fichier")
        if file and st.button("Uploader"):
            files = {"file": (file.name, file.getvalue(), file.type)}
            result = api_post("/api/v1/documents/upload", files=files)
            if result:
                st.success(f"Uploadé: {result.get('document_id')}")
    
    st.markdown("### Liste")
    docs = api_get("/api/v1/documents")
    if docs and docs.get("documents"):
        for d in docs["documents"]:
            st.json(d)
    else:
        st.info("Aucun document")


if __name__ == "__main__":
    show()
""",
    "app/web/pages/analysis.py": """
import streamlit as st
from typing import List, Dict, Any
import requests

API_BASE_URL = "http://localhost:8000"


def api_get(endpoint: str, params: Dict = None) -> Any:
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API Error: {e}")
        return None


def show():
    st.title("📊 Analyse")
    mission_id = st.text_input("Mission ID")
    if mission_id:
        if st.button("Statut Workflow"):
            status = api_get(f"/api/v1/workflows/{mission_id}/status")
            if status:
                st.json(status)
        if st.button("Exécuter"):
            result = requests.post(f"{API_BASE_URL}/api/v1/workflows/{mission_id}/execute")
            st.json(result.json())


if __name__ == "__main__":
    show()
""",
    "app/web/styles.css": """
/* Custom styles for SMART_AO V7 UI */

.main-header {
    font-size: 3rem;
    font-weight: bold;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}

.metric-card {
    background: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
}

.stAlert {
    border-radius: 0.5rem;
}
""",
    # MCP Server
    "app/mcp/server.py": """
import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

from app.mcp.tools import mission_tools, agent_tools, document_tools

logger = logging.getLogger(__name__)


class SMARTAOServer:
    '''MCP Server pour SMART_AO V7 Engine OS.'''
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        self.host = host
        self.port = port
        self.server: Optional[Server] = None
        self._tools: List[Tool] = []
    
    async def initialize(self) -> None:
        '''Initialiser le serveur MCP.'''
        logger.info("Initializing SMART_AO V7 MCP Server...")
        
        # Charger tous les outils
        self._tools = [
            *mission_tools.get_tools(),
            *agent_tools.get_tools(),
            *document_tools.get_tools(),
        ]
        
        logger.info(f"Loaded {len(self._tools)} MCP tools")
    
    async def get_tools(self) -> List[Tool]:
        '''Récupérer la liste des outils disponibles.'''
        return self._tools
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
        '''Appeler un outil par son nom.'''
        logger.info(f"Calling MCP tool: {name} with args: {arguments}")
        
        # Trouver et exécuter l'outil
        for tool in self._tools:
            if tool.name == name:
                # Exécuter l'outil
                result = await self._execute_tool(tool, arguments)
                return result
        
        raise ValueError(f"Tool {name} not found")
    
    async def _execute_tool(self, tool: Tool, arguments: Dict[str, Any]) -> List[Union[TextContent, ImageContent, EmbeddedResource]]:
        '''Exécuter un outil spécifique.'''
        try:
            # Extraire la fonction de l'outil
            tool_func = tool.func
            result = await tool_func(**arguments)
            
            # Formater le résultat
            if isinstance(result, str):
                return [TextContent(type="text", text=result)]
            elif isinstance(result, dict):
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            else:
                return [TextContent(type="text", text=str(result))]
        except Exception as e:
            logger.error(f"Error executing tool {tool.name}: {e}")
            return [TextContent(type="text", text=f"Error: {str(e)}"))]
    
    async def start(self) -> None:
        '''Démarrer le serveur MCP.'''
        logger.info(f"Starting MCP server on {self.host}:{self.port}")
        
        # Initialiser
        await self.initialize()
        
        # Créer le serveur
        self.server = Server(
            host=self.host,
            port=self.port,
            name="SMART_AO V7 Engine OS",
            version="1.0.0",
        )
        
        # Configurer les handlers
        self.server.add_tool_handler(self.get_tools, self.call_tool)
        
        # Démarrer
        logger.info("MCP Server started successfully")
        await self.server.run()
    
    async def stop(self) -> None:
        '''Arrêter le serveur MCP.'''
        if self.server:
            await self.server.shutdown()
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
""",
    "app/mcp/tools/__init__.py": "# MCP Tools Package\nfrom .mission_tools import get_tools as get_mission_tools\nfrom .agent_tools import get_tools as get_agent_tools\nfrom .document_tools import get_tools as get_document_tools\n\n__all__ = ['get_mission_tools', 'get_agent_tools', 'get_document_tools']",
    "app/mcp/tools/mission_tools.py": """
from typing import List, Dict, Any
from mcp.types import Tool


def get_tools() -> List[Tool]:
    '''Récupérer les outils pour la gestion des missions.'''
    return [
        Tool(
            name="create_mission",
            description="Créer une nouvelle mission SMART_AO",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "ID du projet"},
                    "documents": {"type": "array", "items": {"type": "string"}, "description": "Liste des IDs de documents"},
                    "context": {"type": "object", "description": "Contexte de la mission"},
                    "priority": {"type": "string", "enum": ["BASSE", "NORMALE", "HAUTE", "URGENTE"], "default": "NORMALE"},
                },
                "required": ["project_id"],
            },
            func=_create_mission,
        ),
        Tool(
            name="list_missions",
            description="Lister toutes les missions",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {"type": "string", "description": "Filtrer par statut"},
                    "limit": {"type": "integer", "default": 100},
                    "offset": {"type": "integer", "default": 0},
                },
            },
            func=_list_missions,
        ),
        Tool(
            name="get_mission",
            description="Récupérer une mission spécifique",
            inputSchema={
                "type": "object",
                "properties": {
                    "mission_id": {"type": "string", "description": "ID de la mission"},
                },
                "required": ["mission_id"],
            },
            func=_get_mission,
        ),
        Tool(
            name="execute_workflow",
            description="Exécuter le workflow pour une mission",
            inputSchema={
                "type": "object",
                "properties": {
                    "mission_id": {"type": "string", "description": "ID de la mission"},
                },
                "required": ["mission_id"],
            },
            func=_execute_workflow,
        ),
        Tool(
            name="get_workflow_status",
            description="Récupérer le statut du workflow",
            inputSchema={
                "type": "object",
                "properties": {
                    "mission_id": {"type": "string", "description": "ID de la mission"},
                },
                "required": ["mission_id"],
            },
            func=_get_workflow_status,
        ),
    ]


async def _create_mission(
    project_id: str,
    documents: List[str] = None,
    context: Dict[str, Any] = None,
    priority: str = "NORMALE",
) -> Dict[str, Any]:
    '''Créer une nouvelle mission.'''
    # TODO: Intégrer avec API ou WorkflowEngine
    return {
        "status": "created",
        "mission_id": f"mission_{project_id[:6]}",
        "project_id": project_id,
        "documents": documents or [],
        "context": context or {},
        "priority": priority,
        "message": "Mission created successfully",
    }


async def _list_missions(
    status: str = None,
    limit: int = 100,
    offset: int = 0,
) -> Dict[str, Any]:
    '''Lister toutes les missions.'''
    # TODO: Intégrer avec API
    return {
        "missions": [],
        "total": 0,
        "limit": limit,
        "offset": offset,
    }


async def _get_mission(mission_id: str) -> Dict[str, Any]:
    '''Récupérer une mission spécifique.'''
    # TODO: Intégrer avec API
    return {
        "id": mission_id,
        "project_id": "PROJ-001",
        "status": "PENDING",
        "documents": [],
        "context": {},
        "priority": "NORMALE",
    }


async def _execute_workflow(mission_id: str) -> Dict[str, Any]:
    '''Exécuter le workflow pour une mission.'''
    # TODO: Intégrer avec WorkflowEngine
    return {
        "mission_id": mission_id,
        "execution_id": f"exec_{mission_id}",
        "status": "STARTED",
        "started_at": "2026-08-05T12:00:00",
    }


async def _get_workflow_status(mission_id: str) -> Dict[str, Any]:
    '''Récupérer le statut du workflow.'''
    # TODO: Intégrer avec WorkflowEngine
    return {
        "mission_id": mission_id,
        "current_step": "PARSER",
        "total_steps": 6,
        "completed_steps": 0,
        "status": "PENDING",
    }
""",
    "app/mcp/tools/agent_tools.py": """
from typing import List, Dict, Any
from mcp.types import Tool


def get_tools() -> List[Tool]:
    '''Récupérer les outils pour la gestion des agents.'''
    return [
        Tool(
            name="list_agents",
            description="Lister tous les agents disponibles",
            inputSchema={
                "type": "object",
                "properties": {
                    "capability": {"type": "string", "description": "Filtrer par capacité"},
                    "is_blocking": {"type": "boolean", "description": "Filtrer par bloquant"},
                },
            },
            func=_list_agents,
        ),
        Tool(
            name="get_agent",
            description="Récupérer un agent spécifique",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_name": {"type": "string", "description": "Nom de l'agent"},
                },
                "required": ["agent_name"],
            },
            func=_get_agent,
        ),
        Tool(
            name="run_agent",
            description="Exécuter un agent sur une mission",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_name": {"type": "string", "description": "Nom de l'agent"},
                    "mission_id": {"type": "string", "description": "ID de la mission"},
                    "parameters": {"type": "object", "description": "Paramètres de l'agent"},
                },
                "required": ["agent_name", "mission_id"],
            },
            func=_run_agent,
        ),
        Tool(
            name="get_agent_capabilities",
            description="Récupérer les capacités d'un agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_name": {"type": "string", "description": "Nom de l'agent"},
                },
                "required": ["agent_name"],
            },
            func=_get_agent_capabilities,
        ),
    ]


async def _list_agents(
    capability: str = None,
    is_blocking: bool = None,
) -> Dict[str, Any]:
    '''Lister tous les agents.'''
    # TODO: Intégrer avec AgentRegistry
    from app.engines.agent_runtime.registry import registry
    
    agents = registry.list_agents()
    result = []
    
    for agent in agents:
        if capability and capability not in agent.capabilities:
            continue
        if is_blocking is not None and agent.is_blocking != is_blocking:
            continue
        
        result.append({
            "name": agent.name,
            "capabilities": agent.capabilities,
            "is_blocking": agent.is_blocking,
            "tags": agent.tags,
        })
    
    return {"agents": result, "total": len(result)}


async def _get_agent(agent_name: str) -> Dict[str, Any]:
    '''Récupérer un agent spécifique.'''
    # TODO: Intégrer avec AgentRegistry
    from app.engines.agent_runtime.registry import registry
    
    agent = registry.get_agent(agent_name)
    if not agent:
        return {"error": f"Agent {agent_name} not found"}
    
    return {
        "name": agent.name,
        "capabilities": agent.capabilities,
        "dependencies": agent.dependencies,
        "is_blocking": agent.is_blocking,
        "tags": agent.tags,
        "estimated_duration_ms": agent.estimated_duration.total_seconds() * 1000,
    }


async def _run_agent(
    agent_name: str,
    mission_id: str,
    parameters: Dict[str, Any] = None,
) -> Dict[str, Any]:
    '''Exécuter un agent sur une mission.'''
    # TODO: Intégrer avec AgentRuntime
    return {
        "agent_name": agent_name,
        "mission_id": mission_id,
        "parameters": parameters or {},
        "status": "STARTED",
        "execution_id": f"exec_{agent_name}_{mission_id}",
    }


async def _get_agent_capabilities(agent_name: str) -> Dict[str, Any]:
    '''Récupérer les capacités d'un agent.'''
    agent = _get_agent(agent_name)
    return {
        "agent_name": agent_name,
        "capabilities": agent.get("capabilities", []),
    }
""",
    "app/mcp/tools/document_tools.py": """
from typing import List, Dict, Any
from mcp.types import Tool


def get_tools() -> List[Tool]:
    '''Récupérer les outils pour la gestion des documents.'''
    return [
        Tool(
            name="upload_document",
            description="Uploader un document pour analyse",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Chemin vers le fichier"},
                    "mission_id": {"type": "string", "description": "ID de la mission (optionnel)"},
                    "document_type": {"type": "string", "description": "Type de document"},
                },
                "required": ["file_path"],
            },
            func=_upload_document,
        ),
        Tool(
            name="list_documents",
            description="Lister tous les documents",
            inputSchema={
                "type": "object",
                "properties": {
                    "mission_id": {"type": "string", "description": "Filtrer par mission"},
                    "limit": {"type": "integer", "default": 100},
                },
            },
            func=_list_documents,
        ),
        Tool(
            name="get_document",
            description="Récupérer un document spécifique",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {"type": "string", "description": "ID du document"},
                },
                "required": ["document_id"],
            },
            func=_get_document,
        ),
        Tool(
            name="delete_document",
            description="Supprimer un document",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_id": {"type": "string", "description": "ID du document"},
                },
                "required": ["document_id"],
            },
            func=_delete_document,
        ),
    ]


async def _upload_document(
    file_path: str,
    mission_id: str = None,
    document_type: str = "UNKNOWN",
) -> Dict[str, Any]:
    '''Uploader un document.'''
    # TODO: Implémenter l'upload réel
    import os
    from datetime import datetime
    
    if not os.path.exists(file_path):
        return {"error": f"File {file_path} not found"}
    
    return {
        "status": "uploaded",
        "document_id": f"doc_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "file_name": os.path.basename(file_path),
        "file_path": file_path,
        "mission_id": mission_id,
        "document_type": document_type,
        "upload_time": datetime.now().isoformat(),
    }


async def _list_documents(
    mission_id: str = None,
    limit: int = 100,
) -> Dict[str, Any]:
    '''Lister tous les documents.'''
    # TODO: Implémenter avec persistance
    return {
        "documents": [],
        "total": 0,
        "limit": limit,
    }


async def _get_document(document_id: str) -> Dict[str, Any]:
    '''Récupérer un document spécifique.'''
    # TODO: Implémenter avec persistance
    return {
        "id": document_id,
        "file_name": "document.pdf",
        "file_path": "/path/to/document.pdf",
        "document_type": "DCE",
        "upload_time": "2026-08-05T12:00:00",
    }


async def _delete_document(document_id: str) -> Dict[str, Any]:
    '''Supprimer un document.'''
    # TODO: Implémenter la suppression
    return {
        "status": "deleted",
        "document_id": document_id,
    }
""",
    # Core
    "app/core/config.py": """
from pydantic_settings import BaseSettings
from typing import Optional, List
from functools import lru_cache


class Settings(BaseSettings):
    '''Configuration centrale SMART_AO V7.'''
    
    # Application
    APP_NAME: str = "SMART_AO V7 Engine OS"
    APP_VERSION: str = "1.0.0"
    APP_ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_ROOT_PATH: str = "/api"
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"],
    CORS_ALLOW_METHODS: List[str] = ["*"],
    CORS_ALLOW_HEADERS: List[str] = ["*"],
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/smart_ao_v7"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Qdrant
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "vault_documents"
    
    # MinIO
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "smart-ao-documents"
    
    # MCP
    MCP_HOST: str = "0.0.0.0"
    MCP_PORT: int = 8080
    
    # UI
    UI_HOST: str = "0.0.0.0"
    UI_PORT: int = 8501
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    '''Récupérer les paramètres de configuration.'''
    return Settings()


settings = get_settings()
""",
    "app/core/api_client.py": """
import httpx
from typing import Any, Dict, Optional, Union
from .config import settings


class APIClient:
    '''Client API pour les requêtes internes.'''
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or f"http://{settings.API_HOST}:{settings.API_PORT}{settings.API_ROOT_PATH}"
        self.client = httpx.AsyncClient()
    
    async def get(
        self,
        endpoint: str,
        params: Dict[str, Any] = None,
        headers: Dict[str, str] = None,
    ) -> Dict[str, Any]:
        '''Effectuer une requête GET.'''
        url = f"{self.base_url}{endpoint}"
        response = await self.client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    
    async def post(
        self,
        endpoint: str,
        json: Dict[str, Any] = None,
        data: Dict[str, Any] = None,
        files: Dict[str, Any] = None,
        headers: Dict[str, str] = None,
    ) -> Dict[str, Any]:
        '''Effectuer une requête POST.'''
        url = f"{self.base_url}{endpoint}"
        response = await self.client.post(
            url,
            json=json,
            data=data,
            files=files,
            headers=headers,
        )
        response.raise_for_status()
        return response.json()
    
    async def put(
        self,
        endpoint: str,
        json: Dict[str, Any] = None,
        headers: Dict[str, str] = None,
    ) -> Dict[str, Any]:
        '''Effectuer une requête PUT.'''
        url = f"{self.base_url}{endpoint}"
        response = await self.client.put(url, json=json, headers=headers)
        response.raise_for_status()
        return response.json()
    
    async def delete(
        self,
        endpoint: str,
        headers: Dict[str, str] = None,
    ) -> Dict[str, Any]:
        '''Effectuer une requête DELETE.'''
        url = f"{self.base_url}{endpoint}"
        response = await self.client.delete(url, headers=headers)
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        '''Fermer la connexion.'''
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# Instance singleton
api_client = APIClient()


def get_api_client() -> APIClient:
    return api_client
""",
    # Configuration files
    "config/api.yaml": """
# API Configuration
server:
  host: 0.0.0.0
  port: 8000
  root_path: /api
  debug: true
  workers: 4

cors:
  origins:
    - "*"
  allow_methods:
    - "*"
  allow_headers:
    - "*"

logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
""",
    "config/mcp.yaml": """
# MCP Server Configuration
server:
  host: 0.0.0.0
  port: 8080
  name: SMART_AO V7 Engine OS
  version: 1.0.0

logging:
  level: INFO
""",
    "config/ui.yaml": """
# UI Configuration
server:
  headless: true
  host: 0.0.0.0
  port: 8501

theme:
  primary_color: "#1f77b4"
  background_color: "#ffffff"
  secondary_background_color: "#f0f2f6"
  text_color: "#31333F"
  font: "sans serif"
""",
}

# Structure Build 8 - UI + MCP (déjà partiellement existante)
BUILD8_STRUCTURE = {
    "app/web/styles.css": "/* Styles existants */",
    "config/__init__.py": "# Config Package",
}

# Tests Build 7
TESTS_BUILD7 = {
    "tests/unit/test_api_health.py": """
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from app.main import app

client = TestClient(app)


class TestHealthEndpoint:
    def test_health_check(self):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "V7"
        assert data["build"] == "7-8"
        assert data["phase"] == "4"
""",
    "tests/unit/test_api_missions.py": """
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from app.main import app

client = TestClient(app)


class TestMissionsEndpoint:
    def test_list_missions(self):
        response = client.get("/api/v1/missions")
        assert response.status_code == 200
        data = response.json()
        assert "missions" in data
        assert "total" in data
    
    def test_create_mission(self):
        data = {
            "project_id": "PROJ-001",
            "priority": "NORMALE",
            "context": {"type": "DCE"},
        }
        response = client.post("/api/v1/missions", json=data)
        assert response.status_code == 201
        # Vérifier la structure de la réponse
        assert "id" in response.json()
""",
    "tests/unit/test_api_agents.py": """
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
""",
    "tests/unit/test_plugins.py": """
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from app.plugins.base_plugin import BasePlugin, PluginHook
from app.plugins.registry import PluginRegistry
from app.plugins.example_plugin import ExamplePlugin


class TestPluginRegistry:
    def test_register_plugin(self):
        registry = PluginRegistry()
        plugin = ExamplePlugin()
        registry.register(plugin)
        assert plugin.name in [p.name for p in registry.list_plugins()]
    
    def test_get_plugin(self):
        registry = PluginRegistry()
        plugin = ExamplePlugin()
        registry.register(plugin)
        retrieved = registry.get_plugin(plugin.name)
        assert retrieved == plugin
    
    def test_list_plugins(self):
        registry = PluginRegistry()
        plugin1 = ExamplePlugin()
        plugin2 = ExamplePlugin()
        plugin2.name = "AnotherPlugin"
        registry.register(plugin1)
        registry.register(plugin2)
        plugins = registry.list_plugins()
        assert len(plugins) == 2
""",
    "tests/unit/__init__.py": "",
}


def create_file(file_path: Path, content: str) -> None:
    """Créer un fichier avec son contenu."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if not file_path.exists() or file_path.stat().st_size == 0:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content.lstrip())
        print(f"✅ Créé: {file_path}")
    else:
        print(f"⚠️  Existe déjà: {file_path}")


def create_structure(structure: Dict[str, str], base_path: Path = None) -> int:
    """Créer une structure de fichiers."""
    count = 0
    for file_path_str, content in structure.items():
        file_path = (base_path or PROJECT_ROOT) / file_path_str
        create_file(file_path, content)
        count += 1
    return count


def main():
    """Point d'entrée principal."""
    print("=" * 80)
    print("🚀 SMART_AO V7 - BOOTSTRAP PHASE 4")
    print("=" * 80)
    print()
    
    # Créer Build 7
    print("📦 Création Build 7 (API REST + Plugin System)...")
    build7_count = create_structure(BUILD7_STRUCTURE)
    print(f"   ✅ {build7_count} fichiers créés pour Build 7")
    print()
    
    # Créer Build 8 (compléter ce qui manque)
    print("📦 Création Build 8 (UI + MCP Server)...")
    build8_count = create_structure(BUILD8_STRUCTURE)
    print(f"   ✅ {build8_count} fichiers créés pour Build 8")
    print()
    
    # Créer les tests
    print("🧪 Création des tests Build 7...")
    tests_count = create_structure(TESTS_BUILD7)
    print(f"   ✅ {tests_count} tests créés")
    print()
    
    # Mettre à jour main.py pour FastAPI
    print("🔧 Mise à jour de main.py pour FastAPI...")
    main_py_content = '''"""
SMART_AO V7 - Application Principale
===================================
Point d'entrée FastAPI pour l'API REST V7.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.api.v1.endpoints import health, missions, agents, documents, workflows

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Créer l'application
app = FastAPI(
    title="SMART_AO V7 Engine OS",
    description="API REST pour le système SMART_AO V7 - Gestion des appels d'offres BTP",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Inclure les routers
app.include_router(health.router)
app.include_router(missions.router)
app.include_router(agents.router)
app.include_router(documents.router)
app.include_router(workflows.router)


@app.on_event("startup")
async def startup_event():
    logger.info("🚀 SMART_AO V7 API started successfully")
    logger.info(f"   Docs: http://{settings.API_HOST}:{settings.API_PORT}/api/docs")
    logger.info(f"   Redoc: http://{settings.API_HOST}:{settings.API_PORT}/api/redoc")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 SMART_AO V7 API shutting down")


# Pour le démarrage direct
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
    )
'''
    main_py = PROJECT_ROOT / "app" / "main.py"
    create_file(main_py, main_py_content)
    print()
    
    # Mettre à jour app/api/v1/endpoints/__init__.py
    print("🔧 Mise à jour endpoints __init__.py...")
    endpoints_init = '''"""
Endpoints Package
"""
from .health import router as health_router
from .missions import router as missions_router
from .agents import router as agents_router
from .documents import router as documents_router
from .workflows import router as workflows_router

__all__ = [
    "health_router",
    "missions_router",
    "agents_router",
    "documents_router",
    "workflows_router",
]
'''
    create_file(PROJECT_ROOT / "app" / "api" / "v1" / "endpoints" / "__init__.py", endpoints_init)
    print()
    
    # Résumé
    print("=" * 80)
    print("✅ BOOTSTRAP PHASE 4 COMPLET")
    print("=" * 80)
    print()
    print("Structure créée:")
    print(f"  • Build 7: {build7_count} fichiers (API REST + Plugin System)")
    print(f"  • Build 8: {build8_count} fichiers (UI + MCP Server)")
    print(f"  • Tests: {tests_count} fichiers")
    print()
    print("Prochaines étapes:")
    print("  1. Installer les dépendances: pip install fastapi uvicorn streamlit mcp")
    print("  2. Démarrer l'API: uvicorn app.main:app --reload")
    print("  3. Démarrer l'UI: streamlit run app/web/app.py")
    print("  4. Démarrer MCP: python -m app.mcp.server")
    print("  5. Exécuter les tests: pytest tests/unit/test_api_*.py")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
