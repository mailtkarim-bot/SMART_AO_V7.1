"""
SMART_AO V7 - analysis.py
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
