"""
SMART_AO V7 - documents.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import uuid
import hashlib
import shutil
import logging
import os

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.auth import get_current_user, TokenData
from app.core.database import get_db
from app.schemas.document import DocumentUploadResponse, DocumentListResponse, UploadStatusResponse
from app.engines.security_engine.clamav import scan_content, ScanResult
from app.engines.api_gateway.vault_core import get_vault_core
from sqlalchemy import func, or_, select, desc

# Tracker des uploads en cours (pour démo - en prod: utiliser Redis ou base de données)
upload_tracker = {}

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


# Configuration upload (fallback sur les settings)
MAX_UPLOAD_SIZE_MB = getattr(settings, "UPLOAD_MAX_SIZE_MB", 50) or 50
ALLOWED_EXTENSIONS = getattr(settings, "UPLOAD_ALLOWED_EXTENSIONS", ".pdf,.docx,.xlsx,.txt,.json") or ".pdf,.docx,.xlsx,.txt,.json"
ALLOWED_EXTENSIONS_SET = {ext.strip().lower() for ext in ALLOWED_EXTENSIONS.split(",")}
UPLOAD_DIR = Path(getattr(settings, "UPLOAD_DIR", "./uploads") or "./uploads")


def _get_extension(filename: Optional[str]) -> str:
    """Extraire l'extension d'un nom de fichier."""
    if not filename:
        return ""
    return Path(filename).suffix.lower()


def _sanitize_filename(filename: Optional[str]) -> str:
    """Nettoyer et sécuriser le nom de fichier original."""
    if not filename:
        return "unknown"
    # Garder uniquement le nom de base et limiter la longueur
    safe = Path(filename).name
    safe = safe[:255]
    return safe


@router.post("/upload", response_model=DocumentUploadResponse, summary="Upload Document")
async def upload_document(
    file: UploadFile = File(...),
    mission_id: Optional[str] = Form(None),
    document_type: Optional[str] = Form(None),
    current_user: TokenData = Depends(get_current_user),
):
    '''Uploader un document pour analyse avec validation de sécurité complète.'''
    
    # Générer un ID d'upload pour le suivi
    upload_id = uuid.uuid4().hex
    
    # Initialiser le tracker
    upload_tracker[upload_id] = {
        "status": "UPLOADING",
        "progress": 0.0,
        "bytes_received": 0,
        "bytes_total": 0,
        "file_name": file.filename,
        "document_type": document_type,
        "started_at": datetime.now(),
        "error": None
    }
    
    try:
        # Validation : extension
        ext = _get_extension(file.filename)
        if ext not in ALLOWED_EXTENSIONS_SET:
            upload_tracker[upload_id]["error"] = f"Extension non autorisée: {ext}"
            upload_tracker[upload_id]["status"] = "FAILED"
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Extension non autorisée: {ext}. Autorisées: {', '.join(sorted(ALLOWED_EXTENSIONS_SET))}"
            )
        
        upload_tracker[upload_id]["progress"] = 10.0
        
        # Validation : taille (lecture complète en mémoire pour vérification)
        content = await file.read()
        max_size_bytes = MAX_UPLOAD_SIZE_MB * 1024 * 1024
        
        upload_tracker[upload_id]["bytes_total"] = len(content)
        upload_tracker[upload_id]["bytes_received"] = len(content)
        upload_tracker[upload_id]["progress"] = 30.0
        
        if len(content) > max_size_bytes:
            upload_tracker[upload_id]["error"] = f"Fichier trop volumineux: {len(content)} octets"
            upload_tracker[upload_id]["status"] = "FAILED"
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Fichier trop volumineux: {len(content)} octets (max {MAX_UPLOAD_SIZE_MB} MB)"
            )
        
        # Validation : contenu non vide
        if len(content) == 0:
            upload_tracker[upload_id]["error"] = "Fichier vide"
            upload_tracker[upload_id]["status"] = "FAILED"
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Fichier vide"
            )
        
        upload_tracker[upload_id]["progress"] = 40.0
        
        # 🔒 SCAN ANTIVIRUS (ClamAV) - CRITIQUE POUR LA SÉCURITÉ
        upload_tracker[upload_id]["status"] = "SCANNING"
        upload_tracker[upload_id]["scan_status"] = "IN_PROGRESS"
        
        scan_result: ScanResult = await scan_content(content, file.filename)
        
        upload_tracker[upload_id]["progress"] = 60.0
        upload_tracker[upload_id]["scan_status"] = "CLEAN" if scan_result.is_clean else "INFECTED"
        
        if scan_result.is_infected:
            upload_tracker[upload_id]["error"] = f"Malware détecté: {scan_result.virus_name}"
            upload_tracker[upload_id]["status"] = "FAILED"
            logger.warning(f"Malware détecté: {scan_result.virus_name} dans {file.filename}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Malware détecté: {scan_result.virus_name or 'virus non identifié'}"
            )
        if scan_result.is_error:
            upload_tracker[upload_id]["error"] = f"Erreur de scan: {scan_result.message}"
            upload_tracker[upload_id]["status"] = "FAILED"
            logger.error(f"Erreur de scan antivirus: {scan_result.message}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur de scan antivirus: {scan_result.message}"
            )
        
        upload_tracker[upload_id]["progress"] = 70.0
        upload_tracker[upload_id]["status"] = "PROCESSING"
        
        # Stockage sécurisé : UUID + dossier unique documents
        user_id = current_user.user_id or "unknown"
        safe_name = _sanitize_filename(file.filename)
        file_uuid = uuid.uuid4().hex
        storage_name = f"{file_uuid}{ext}"
        documents_dir = UPLOAD_DIR / "documents"
        documents_dir.mkdir(parents=True, exist_ok=True)
        
        dest_path = documents_dir / storage_name
        with open(dest_path, "wb") as f:
            f.write(content)
        
        content_hash = hashlib.sha256(content).hexdigest()
        
        upload_tracker[upload_id]["progress"] = 85.0
        
        # 📁 INDEXATION DANS QDRANT (Recherche sémantique)
        upload_tracker[upload_id]["indexing_status"] = "IN_PROGRESS"
        try:
            vault_core = get_vault_core()
            document_id = f"doc_{file_uuid}"
            
            # Indexer le document dans Qdrant
            await vault_core.index_document(
                document_id=document_id,
                file_path=str(dest_path),
                file_name=safe_name,
                content_type=file.content_type or "application/octet-stream",
                size=len(content),
                user_id=user_id,
                mission_id=mission_id,
                document_type=document_type or "UNKNOWN",
                metadata={
                    "upload_time": datetime.now().isoformat(),
                    "hash": content_hash,
                    "extension": ext,
                    "original_filename": file.filename,
                }
            )
            upload_tracker[upload_id]["indexing_status"] = "COMPLETED"
            logger.info(f"Document indexé dans Qdrant: {document_id}")
        except Exception as e:
            upload_tracker[upload_id]["indexing_status"] = "FAILED"
            upload_tracker[upload_id]["error"] = f"Indexation échouée: {str(e)}"
            logger.warning(f"Échec de l'indexation Qdrant: {e}")
        
        upload_tracker[upload_id]["progress"] = 100.0
        upload_tracker[upload_id]["status"] = "COMPLETED"
        upload_tracker[upload_id]["completed_at"] = datetime.now()
        
        logger.info(
            f"Document uploadé et sécurisé: user={user_id}, "
            f"original={safe_name}, size={len(content)}, hash={content_hash[:16]}..."
        )
        
        return DocumentUploadResponse(
            document_id=file_uuid,
            file_name=safe_name,
            content_type=file.content_type or "application/octet-stream",
            size=len(content),
            mission_id=mission_id,
            document_type=document_type or "UNKNOWN",
            upload_time=datetime.now(),
            scan_status="CLEAN",
            scan_details={"virus_name": None, "scan_time": scan_result.scan_time}
        )
        
    except Exception as e:
        upload_tracker[upload_id]["status"] = "FAILED"
        upload_tracker[upload_id]["error"] = str(e)
        upload_tracker[upload_id]["completed_at"] = datetime.now()
        raise


@router.get("/upload/{upload_id}/status", response_model=UploadStatusResponse, summary="Upload Status")
async def get_upload_status(
    upload_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    '''Récupérer le statut d'un upload en cours.'''
    upload_info = upload_tracker.get(upload_id)
    
    if not upload_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Upload {upload_id} non trouvé"
        )
    
    return UploadStatusResponse(
        upload_id=upload_id,
        status=upload_info.get("status", "UNKNOWN"),
        progress=upload_info.get("progress", 0.0),
        bytes_received=upload_info.get("bytes_received", 0),
        bytes_total=upload_info.get("bytes_total", 0),
        file_name=upload_info.get("file_name"),
        document_type=upload_info.get("document_type"),
        error=upload_info.get("error"),
        scan_status=upload_info.get("scan_status"),
        indexing_status=upload_info.get("indexing_status"),
        started_at=upload_info.get("started_at"),
        completed_at=upload_info.get("completed_at")
    )


@router.get("", response_model=DocumentListResponse, summary="List Documents")
async def list_documents(
    mission_id: Optional[str] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    '''Lister tous les documents avec pagination.'''
    from app.models.vault_core import VaultDocument
    from sqlalchemy import select, desc, or_, and_
    
    # Construction de la requête (single-tenant pur : pas de filtre tenant)
    query = select(VaultDocument)
    
    # Filtre par mission_id si spécifié
    if mission_id:
        from sqlalchemy import String
        query = query.where(
            or_(
                VaultDocument.extra_metadata["mission_id"].cast(String) == mission_id,
                VaultDocument.document_id.startswith(f"{mission_id}_")
            )
        )
    
    # Compter le total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Appliquer limite et tri
    query = query.order_by(desc(VaultDocument.created_at)).limit(limit)
    
    # Exécuter la requête
    result = await db.execute(query)
    documents_models = result.scalars().all()
    
    # Convertir en DocumentResponse
    from app.schemas.document import DocumentResponse
    documents = []
    for doc_model in documents_models:
        document_type = doc_model.extra_metadata.get("document_type", "UNKNOWN") if doc_model.extra_metadata else "UNKNOWN"
        mission_id_from_metadata = doc_model.extra_metadata.get("mission_id") if doc_model.extra_metadata else None
        
        documents.append(DocumentResponse(
            id=doc_model.document_id,
            file_name=doc_model.file_name,
            content_type=doc_model.file_type or "application/octet-stream",
            size=doc_model.file_size or 0,
            mission_id=mission_id_from_metadata,
            document_type=document_type,
            upload_time=doc_model.created_at,
            status=doc_model.status,
        ))
    
    return DocumentListResponse(documents=documents, total=total)
