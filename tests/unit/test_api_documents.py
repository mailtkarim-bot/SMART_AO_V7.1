"""
SMART_AO V7 - test_api_documents.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
Tests unitaires pour les endpoints Documents API V1
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from app.main import app

client = TestClient(app)


class TestDocumentsEndpoint:
    """Tests pour l'endpoint /api/v1/documents."""
    
    def test_list_documents_empty(self):
        """Test la liste des documents vide."""
        response = client.get("/api/v1/documents")
        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert "total" in data
        assert data["total"] == 0
    
    def test_list_documents_with_mission_id(self):
        """Test la liste des documents filtrée par mission_id."""
        response = client.get("/api/v1/documents", params={"mission_id": "test_mission"})
        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert "total" in data
    
    def test_list_documents_with_limit(self):
        """Test la liste des documents avec limite."""
        response = client.get("/api/v1/documents", params={"limit": 50})
        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert "total" in data


class TestDocumentsUploadEndpoint:
    """Tests pour l'endpoint POST /api/v1/documents/upload."""
    
    def test_upload_document_no_file(self):
        """Test l'upload sans fichier."""
        response = client.post("/api/v1/documents/upload", data={"mission_id": "test"})
        # Doit retourner 422 (Validation Error) ou 400
        assert response.status_code in [400, 422]
    
    def test_upload_document_with_file(self):
        """Test l'upload avec un fichier valide."""
        # Créer un fichier test
        test_content = b"Test document content"
        files = {"file": ("test.txt", test_content, "text/plain")}
        
        response = client.post(
            "/api/v1/documents/upload",
            files=files,
            data={"mission_id": "test_mission_001", "document_type": "TEST"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "document_id" in data
        assert "file_name" in data
        assert data["file_name"] == "test.txt"
        assert "document_type" in data
