"""
SMART_AO V7 - document.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


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
    scan_status: str = "PENDING"
    scan_details: Optional[dict] = None


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


class UploadStatusResponse(BaseModel):
    '''Schema pour le statut d'un upload.'''
    upload_id: str
    status: str = "UPLOADING"  # UPLOADING, SCANNING, PROCESSING, COMPLETED, FAILED
    progress: float = 0.0  # 0.0 à 100.0
    bytes_received: int = 0
    bytes_total: int = 0
    file_name: Optional[str] = None
    document_type: Optional[str] = None
    error: Optional[str] = None
    scan_status: Optional[str] = None
    indexing_status: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
