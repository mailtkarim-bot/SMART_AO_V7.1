"""
SMART_AO V7 - documents.py
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
