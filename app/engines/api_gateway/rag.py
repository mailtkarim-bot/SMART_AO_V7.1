"""
SMART_AO V7 - rag.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 07/08/2026
Build: 9 - Phase: 5 - RAG Implementation

ADR-046: RAG hybrid BGE-M3 Qdrant on_disk RRF + FTS btp_french
"""

"""
SMART_AO V7 - RAG API Gateway
================================
API REST pour le Knowledge Engine RAG Hybrid
Intègre avec Qdrant, BGE-M3, et le système de chunks
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import uuid
import hashlib
import logging

from app.core.security import get_current_user
from app.core.config import settings
from app.engines.knowledge_engine.rag_hybrid import (
    get_rag_engine, rag_search_for_agent, DocumentChunk, RAGResponse
)
from app.engines.api_gateway.vault_core import get_vault_core

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/rag", tags=["rag", "knowledge-engine", "semantic-search"])


# =============================================================================
# RAG API ENDPOINTS
# =============================================================================

@router.post("/index", summary="Index Document in RAG", response_model=Dict[str, Any])
async def index_document(
    file: UploadFile = File(..., description="Document file to index"),
    document_type: Optional[str] = Form(None, description="Type of document (DCE, CCAP, DPGF, etc.)"),
    metadata: Optional[str] = Form(None, description="JSON metadata"),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Indexer un document dans le système RAG pour recherche sémantique.
    
    Process:
    1. Valider et lire le fichier
    2. Extraire le texte
    3. Découper en chunks
    4. Générer les embeddings (BGE-M3)
    5. Indexer dans Qdrant
    
    Args:
        file: Fichier à indexer (PDF, DOCX, etc.)
        document_type: Type de document
        metadata: Métadonnées supplémentaires (JSON)
        current_user: Utilisateur authentifié
    
    Returns:
        Dict: Résultats de l'indexation
    """
    user_id = current_user.get("user_id", "unknown")
    
    try:
        # Lire le contenu du fichier
        content = await file.read()
        
        if len(content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Fichier vide"
            )
        
        # Limite de taille
        max_size = getattr(settings, "UPLOAD_MAX_SIZE_MB", 50) * 1024 * 1024
        if len(content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Fichier trop volumineux: {len(content)} octets (max {max_size} octets)"
            )
        
        # Extraire le texte en fonction du type
        file_extension = Path(file.filename).suffix.lower()
        text_content = _extract_text_from_bytes(content, file_extension, file.filename)
        
        if not text_content or len(text_content.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Impossible d'extraire le texte du fichier"
            )
        
        # Générer un ID de document unique
        document_id = f"rag_{uuid.uuid4().hex[:16]}"
        content_hash = hashlib.sha256(content).hexdigest()
        
        # Parser les métadonnées
        extra_metadata = {}
        if metadata:
            try:
                import json
                extra_metadata = json.loads(metadata)
            except Exception as e:
                logger.warning(f"Métadonnées invalides: {e}")
        
        # Ajouter les métadonnées de base
        extra_metadata.update({
            "upload_time": datetime.now().isoformat(),
            "hash": content_hash,
            "file_name": file.filename,
            "file_size": len(content),
            "file_type": file.content_type,
            "user_id": user_id,
            "document_type": document_type or "UNKNOWN"
        })
        
        # Indexer dans le RAG
        rag_engine = await get_rag_engine()
        indexed_chunks = await rag_engine.index_document(
            document_id=document_id,
            content=text_content,
            metadata=extra_metadata)
        
        # Sauvegarder aussi dans le Vault Core pour persistance
        try:
            vault_core = get_vault_core()
            import io
            file_obj = io.BytesIO(content)
            await vault_core.upload_document(
                file=file_obj,
                file_name=file.filename,
                file_size=len(content),
                document_type=document_type,
                metadata=extra_metadata
            )
        except Exception as e:
            logger.warning(f"Échec de la sauvegarde dans Vault Core: {e}")
        
        logger.info(f"Document RAG indexé: {document_id} ({len(indexed_chunks)} chunks)")
        
        return {
            "success": True,
            "document_id": document_id,
            "file_name": file.filename,
            "file_size": len(content),
            "content_hash": content_hash,
            "chunks_indexed": len(indexed_chunks),
            "chunks": indexed_chunks,
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur d'indexation RAG: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur d'indexation RAG: {str(e)}"
        )


@router.post("/index-batch", summary="Index Multiple Documents", response_model=Dict[str, Any])
async def index_documents_batch(
    documents: List[Dict[str, Any]],
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Indexer plusieurs documents en une seule requête.
    
    Args:
        documents: Liste de documents à indexer
        current_user: Utilisateur authentifié
    
    Returns:
        Dict: Résumé de l'indexation batch
    """
    user_id = current_user.get("user_id", "unknown")
    
    rag_engine = await get_rag_engine()
    
    indexed = []
    failed = []
    
    for doc in documents:
        try:
            document_id = f"rag_{uuid.uuid4().hex[:16]}"
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            
            metadata.update({
                "upload_time": datetime.now().isoformat(),
                "user_id": user_id,
                "file_name": doc.get("file_name", "unknown")
            })
            
            chunks = await rag_engine.index_document(
                document_id=document_id,
                content=content,
                metadata=metadata)
            
            indexed.append({
                "document_id": document_id,
                "file_name": doc.get("file_name"),
                "chunks": len(chunks)
            })
        except Exception as e:
            failed.append({
                "file_name": doc.get("file_name", "unknown"),
                "error": str(e)
            })
    
    return {
        "success": len(failed) == 0,
        "indexed": indexed,
        "failed": failed,
        "total": len(documents),
        "success_count": len(indexed),
        "failure_count": len(failed)
    }


@router.get("/search", summary="Search in RAG", response_model=Dict[str, Any])
async def search_rag(
    query: str,
    top_k: int = 5,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Rechercher dans les documents indexés via RAG Hybrid.
    
    Args:
        query: Requête de recherche
        top_k: Nombre de résultats à retourner
        current_user: Utilisateur authentifié
    
    Returns:
        Dict: Résultats de la recherche
    """
    try:
        rag_engine = await get_rag_engine()
        response: RAGResponse = await rag_engine.search(
            query=query,
            top_k=top_k
        )
        
        results = []
        for r in response.results:
            results.append({
                "chunk_id": r.chunk_id,
                "document_id": r.document_id,
                "content": r.content,
                "score": r.score,
                "source": r.source,
                "page": r.page,
                "metadata": r.metadata
            })
        
        return {
            "success": True,
            "query": query,
            "results": results,
            "top_k": top_k,
            "processing_time_ms": response.processing_time_ms,
            "sources_used": response.sources_used,
            "total_results": len(results)
        }
    
    except Exception as e:
        logger.error(f"Erreur de recherche RAG: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur de recherche RAG: {str(e)}"
        )


@router.post("/search", summary="Search with POST", response_model=Dict[str, Any])
async def search_rag_post(
    query_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Rechercher avec une requête complexe (POST).
    
    Args:
        query_data: Dict contenant 'query' et optionnellement 'top_k', 'filters'
        current_user: Utilisateur authentifié
    
    Returns:
        Dict: Résultats de la recherche
    """
    query = query_data.get("query", "")
    top_k = query_data.get("top_k", 5)
    
    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La requête ne peut pas être vide"
        )
    
    try:
        rag_engine = await get_rag_engine()
        response: RAGResponse = await rag_engine.search(
            query=query,
            top_k=top_k
        )
        
        results = []
        for r in response.results:
            results.append({
                "chunk_id": r.chunk_id,
                "document_id": r.document_id,
                "content": r.content,
                "score": r.score,
                "source": r.source,
                "page": r.page,
                "metadata": r.metadata
            })
        
        return {
            "success": True,
            "query": query,
            "results": results,
            "top_k": top_k,
            "processing_time_ms": response.processing_time_ms,
            "sources_used": response.sources_used
        }
    
    except Exception as e:
        logger.error(f"Erreur de recherche RAG: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur de recherche RAG: {str(e)}"
        )


@router.delete("/{document_id}", summary="Delete Document from RAG", response_model=Dict[str, Any])
async def delete_document_rag(
    document_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Supprimer un document de l'index RAG et de Qdrant.
    
    Args:
        document_id: ID du document à supprimer
        current_user: Utilisateur authentifié
    
    Returns:
        Dict: Confirmation de la suppression
    """
    try:
        rag_engine = await get_rag_engine()
        
        # Supprimer de Qdrant
        client = await rag_engine._qdrant.get_client()
        if client:
            from qdrant_client.http import models
            # Supprimer tous les chunks de ce document
            chunk_prefix = f"{document_id}_chunk_"
            # Récupérer tous les points avec ce préfixe
            points = await client.scroll(
                collection_name=rag_engine._qdrant.config.QDRANT_COLLECTION,
                limit=1000,
                with_payload=True,
                with_vectors=False
            )
            
            chunk_ids = [
                str(p.id) for p in points[0] 
                if str(p.id).startswith(chunk_prefix)
            ]
            
            if chunk_ids:
                await client.delete(
                    collection_name=rag_engine._qdrant.config.QDRANT_COLLECTION,
                    points_selector=models.PointIdsList(points=chunk_ids)
                )
        
        logger.info(f"Document RAG supprimé: {document_id}")
        
        return {
            "success": True,
            "document_id": document_id,
            "message": "Document supprimé de l'index RAG"
        }
    
    except Exception as e:
        logger.error(f"Erreur de suppression RAG: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur de suppression RAG: {str(e)}"
        )


@router.get("/status", summary="Get RAG Status", response_model=Dict[str, Any])
async def get_rag_status(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Obtenir l'état du système RAG.
    
    Returns:
        Dict: État du système RAG
    """
    try:
        rag_engine = await get_rag_engine()
        
        qdrant_status = "unknown"
        collection_status = "unknown"
        
        try:
            client = await rag_engine._qdrant.get_client()
            if client:
                collections = await client.get_collections()
                collection_names = [c.name for c in collections.collections]
                if rag_engine._qdrant.config.QDRANT_COLLECTION in collection_names:
                    collection_status = "ready"
                else:
                    collection_status = "not_created"
                qdrant_status = "connected"
        except Exception as e:
            qdrant_status = f"error: {str(e)}"
        
        embedding_status = "unknown"
        try:
            model = await rag_engine._embedding.get_model()
            if model:
                embedding_status = f"loaded: {rag_engine._qdrant.config.EMBEDDING_MODEL}"
            else:
                embedding_status = "not_loaded"
        except Exception as e:
            embedding_status = f"error: {str(e)}"
        
        return {
            "status": "operational" if qdrant_status == "connected" else "degraded",
            "qdrant": {
                "status": qdrant_status,
                "collection": collection_status,
                "host": rag_engine._qdrant.config.QDRANT_HOST,
                "port": rag_engine._qdrant.config.QDRANT_PORT
            },
            "embedding": {
                "status": embedding_status,
                "model": rag_engine._qdrant.config.EMBEDDING_MODEL,
                "dimensions": rag_engine._qdrant.config.EMBEDDING_DIM
            },
            "cache": {
                "enabled": rag_engine._cache._max_size > 0,
                "max_size": rag_engine._cache._max_size,
                "current_size": len(rag_engine._cache._cache)
            }
        }
    
    except Exception as e:
        logger.error(f"Erreur de statuts RAG: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def _extract_text_from_bytes(content: bytes, file_extension: str, filename: str) -> str:
    """Extraire le texte d'un fichier en bytes selon son extension."""
    try:
        if file_extension == ".pdf":
            try:
                import fitz
                doc = fitz.open(stream=content)
                return "".join([page.get_text() for page in doc])
            except ImportError:
                pass
        
        elif file_extension in [".docx", ".doc"]:
            try:
                from docx import Document
                import io
                doc = Document(io.BytesIO(content))
                return "\n".join([p.text for p in doc.paragraphs])
            except ImportError:
                pass
        
        elif file_extension in [".xlsx", ".xls"]:
            try:
                import pandas as pd
                import io
                df = pd.read_excel(io.BytesIO(content))
                return df.to_string()
            except ImportError:
                pass
        
        elif file_extension in [".txt", ".json", ".csv"]:
            return content.decode('utf-8', errors='ignore')
        
        # Fallback
        return content.decode('utf-8', errors='ignore')
    
    except Exception as e:
        logger.error(f"Erreur d'extraction de texte de {filename}: {e}")
        return ""

