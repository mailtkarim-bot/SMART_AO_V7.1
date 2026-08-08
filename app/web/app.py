"""
SMART_AO V7 - app.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


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
    """
    <style>
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
    </style>
    """,
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
