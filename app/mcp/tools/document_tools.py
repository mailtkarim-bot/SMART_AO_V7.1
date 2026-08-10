"""
SMART_AO V7 - document_tools.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


from typing import List, Dict, Any
from mcp.types import Tool
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
import uuid
import os
import hashlib
from datetime import datetime

# Session database globale (à initialiser)
_db_session: AsyncSession = None

def set_db_session(session: AsyncSession):
    global _db_session
    _db_session = session

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
    '''Uploader un document dans le vault.'''
    from app.models.vault_core import VaultDocument
    import shutil
    from pathlib import Path
    
    if not os.path.exists(file_path):
        return {"error": f"File {file_path} not found"}
    
    try:
        # Lire le fichier et calculer hash
        with open(file_path, 'rb') as f:
            content = f.read()
        content_hash = hashlib.sha256(content).hexdigest()
        file_size = len(content)
        
        # Créer un storage path
        storage_dir = Path("/tmp/smart_ao_documents")
        storage_dir.mkdir(parents=True, exist_ok=True)
        storage_path = storage_dir / f"{uuid.uuid4().hex}_{os.path.basename(file_path)}"
        
        # Copier le fichier
        shutil.copy2(file_path, storage_path)
        
        # Créer le document en DB
        doc = VaultDocument(
            document_id=f"doc_{uuid.uuid4().hex[:12]}",
            file_name=os.path.basename(file_path),
            file_path=str(storage_path),
            file_type=get_file_type(file_path),
            file_size=file_size,
            content_hash=content_hash,
            extra_metadata={
                "mission_id": mission_id,
                "document_type": document_type,
                "uploaded_by": "mcp_tool",
            },
            status="uploaded",
        )
        
        if _db_session:
            _db_session.add(doc)
            await _db_session.commit()
            await _db_session.refresh(doc)
        
        return {
            "status": "uploaded",
            "document_id": doc.document_id,
            "file_name": doc.file_name,
            "file_path": doc.file_path,
            "file_size": doc.file_size,
            "file_type": doc.file_type,
            "content_hash": doc.content_hash,
            "mission_id": mission_id,
            "document_type": document_type,
            "upload_time": doc.created_at.isoformat(),
            "db_id": doc.id,
        }
    except Exception as e:
        return {"error": f"Upload failed: {str(e)}"}

def get_file_type(file_path: str) -> str:
    """Déterminer le type MIME à partir de l'extension."""
    extensions = {
        '.pdf': 'application/pdf',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.xls': 'application/vnd.ms-excel',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.txt': 'text/plain',
    }
    ext = os.path.splitext(file_path)[1].lower()
    return extensions.get(ext, 'application/octet-stream')


async def _list_documents(
    mission_id: str = None,
    limit: int = 100,
) -> Dict[str, Any]:
    '''Lister tous les documents depuis la base.'''
    from app.models.vault_core import VaultDocument
    from sqlalchemy import or_, and_
    
    try:
        query = select(VaultDocument)
        
        if mission_id:
            query = query.where(
                VaultDocument.extra_metadata["mission_id"].as_string() == mission_id
            )
        
        if _db_session:
            result = await _db_session.execute(query.limit(limit))
            documents = result.scalars().all()
        else:
            documents = []
        
        doc_list = [
            {
                "id": doc.id,
                "document_id": doc.document_id,
                "file_name": doc.file_name,
                "file_path": doc.file_path,
                "file_type": doc.file_type,
                "file_size": doc.file_size,
                "status": doc.status,
                "mission_id": doc.extra_metadata.get("mission_id"),
                "document_type": doc.extra_metadata.get("document_type"),
                "upload_time": doc.created_at.isoformat() if doc.created_at else None,
            }
            for doc in documents
        ]
        
        return {
            "documents": doc_list,
            "total": len(doc_list),
            "limit": limit,
        }
    except Exception as e:
        return {"error": f"List failed: {str(e)}", "documents": [], "total": 0, "limit": limit}


async def _get_document(document_id: str) -> Dict[str, Any]:
    '''Récupérer un document spécifique depuis la base.'''
    from app.models.vault_core import VaultDocument
    from sqlalchemy import or_
    
    try:
        query = select(VaultDocument).where(
            or_(
                VaultDocument.document_id == document_id,
                VaultDocument.id == int(document_id) if document_id.isdigit() else False
            )
        )
        
        if _db_session:
            result = await _db_session.execute(query)
            doc = result.scalar_one_or_none()
        else:
            doc = None
        
        if not doc:
            return {"error": f"Document {document_id} not found"}
        
        return {
            "id": doc.id,
            "document_id": doc.document_id,
            "file_name": doc.file_name,
            "file_path": doc.file_path,
            "file_type": doc.file_type,
            "file_size": doc.file_size,
            "content_hash": doc.content_hash,
            "status": doc.status,
            "mission_id": doc.extra_metadata.get("mission_id"),
            "document_type": doc.extra_metadata.get("document_type"),
            "upload_time": doc.created_at.isoformat() if doc.created_at else None,
            "processed_at": doc.processed_at.isoformat() if doc.processed_at else None,
        }
    except Exception as e:
        return {"error": f"Get document failed: {str(e)}"}


async def _delete_document(document_id: str) -> Dict[str, Any]:
    '''Supprimer un document de la base et du stockage.'''
    from app.models.vault_core import VaultDocument
    from sqlalchemy import or_
    
    try:
        query = select(VaultDocument).where(
            or_(
                VaultDocument.document_id == document_id,
                VaultDocument.id == int(document_id) if document_id.isdigit() else False
            )
        )
        
        if _db_session:
            result = await _db_session.execute(query)
            doc = result.scalar_one_or_none()
            
            if not doc:
                return {"error": f"Document {document_id} not found", "status": "not_found"}
            
            # Supprimer le fichier du stockage
            try:
                if os.path.exists(doc.file_path):
                    os.remove(doc.file_path)
            except Exception as e:
                pass  # Log mais ne pas bloquer la suppression DB
            
            # Supprimer de la base
            await _db_session.delete(doc)
            await _db_session.commit()
            
            return {
                "status": "deleted",
                "document_id": document_id,
                "file_path": doc.file_path,
                "file_name": doc.file_name,
            }
        else:
            return {"error": "No database session", "status": "error"}
    except Exception as e:
        return {"error": f"Delete failed: {str(e)}", "status": "error", "document_id": document_id}
