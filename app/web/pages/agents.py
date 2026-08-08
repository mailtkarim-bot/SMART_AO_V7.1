"""
SMART_AO V7 - agents.py
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
    st.title("🤖 Agents")
    agents = api_get("/api/v1/agents")
    if agents and agents.get("agents"):
        for agent in agents["agents"]:
            st.json(agent)
    else:
        st.info("Aucun agent")


if __name__ == "__main__":
    show()
