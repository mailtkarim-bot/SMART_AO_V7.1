"""
SMART_AO V7 - missions.py
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
