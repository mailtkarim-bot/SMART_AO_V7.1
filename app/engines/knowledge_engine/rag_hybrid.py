"""
SMART_AO V7 - Knowledge Engine RAG Hybrid
========================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 07/08/2026
Build: 9 - Phase: 5 - RAG Implementation

ADR-046: RAG hybrid BGE-M3 Qdrant on_disk RRF + FTS btp_french
"""

import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import numpy as np

from app.core.config import settings

logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class RAGConfig:
    EMBEDDING_MODEL: str = "BAAI/bge-m3"
    EMBEDDING_DIM: int = 1024
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "vault_documents"
    RRF_K: int = 60
    TOP_K_DENSE: int = 10
    TOP_K_SPARSE: int = 10
    TOP_K_FINAL: int = 5
    CACHE_ENABLED: bool = True
    CACHE_MAX_SIZE: int = 1000

config = RAGConfig()


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class DocumentChunk:
    chunk_id: str
    document_id: str
    content: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    page: Optional[int] = None

@dataclass  
class SearchResult:
    chunk_id: str
    document_id: str
    content: str
    score: float
    metadata: Dict[str, Any]
    source: str
    page: Optional[int] = None

@dataclass
class RAGResponse:
    query: str
    results: List[SearchResult]
    top_k: int
    processing_time_ms: float
    sources_used: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# QDRANT MANAGER
# =============================================================================

class QdrantCollectionManager:
    def __init__(self):
        self._client = None
        self._collection_created = False
    
    async def get_client(self):
        if self._client is None:
            try:
                from qdrant_client import QdrantClient
                from qdrant_client.http import models
                self._client = QdrantClient(
                    host=config.QDRANT_HOST,
                    port=config.QDRANT_PORT,
                    timeout=30.0
                )
                await self._ensure_collection_exists()
            except ImportError:
                logger.warning("Qdrant not installed. Fallback mode.")
                self._client = None
        return self._client
    
    async def _ensure_collection_exists(self):
        if self._collection_created:
            return
        try:
            from qdrant_client.http import models
            collections = await self._client.get_collections()
            if config.QDRANT_COLLECTION not in [c.name for c in collections.collections]:
                await self._client.create_collection(
                    collection_name=config.QDRANT_COLLECTION,
                    vectors_config=models.VectorParams(
                        size=config.EMBEDDING_DIM,
                        distance=models.Distance.COSINE
                    ),
                    sparse_vectors_config={"sparse": models.SparseVectorParams()},
                    on_disk_payload=True
                )
            self._collection_created = True
        except Exception as e:
            logger.error(f"Qdrant error: {e}")
            self._client = None
    
    async def index_chunk(self, chunk: DocumentChunk) -> bool:
        try:
            client = await self.get_client()
            if not client:
                return False
            point = {
                "id": chunk.chunk_id,
                "vector": chunk.embedding or [0.0]*config.EMBEDDING_DIM,
                "sparse": {},
                "payload": {
                    "document_id": chunk.document_id,
                    "content": chunk.content,
                    "page": chunk.page,
                    "metadata": chunk.metadata
                }
            }
            await client.upsert(
                collection_name=config.QDRANT_COLLECTION,
                points=[point],
                wait=True
            )
            return True
        except Exception as e:
            logger.error(f"Indexing error: {e}")
            return False
    
    async def search_hybrid(self, query: str, query_embedding: Optional[List[float]],
                            top_k: int = config.TOP_K_FINAL) -> List[SearchResult]:
        """Recherche hybride dense + sparse sans filtre tenant (single-tenant pur)."""
        try:
            client = await self.get_client()
            if not client:
                return []
            
            results = []
            
            # Dense search
            if query_embedding:
                dense_res = await client.search(
                    collection_name=config.QDRANT_COLLECTION,
                    query_vector=query_embedding,
                    limit=config.TOP_K_DENSE,
                )
                for r in dense_res:
                    p = r.payload
                    results.append(SearchResult(
                        chunk_id=str(r.id),
                        document_id=p.get("document_id", ""),
                        content=p.get("content", ""),
                        score=r.score,
                        metadata=p.get("metadata", {}),
                        source="dense",
                        page=p.get("page")
                    ))
            
            # Sparse/FTS search
            sparse_res = await client.search(
                collection_name=config.QDRANT_COLLECTION,
                query=query,
                limit=config.TOP_K_SPARSE,
            )
            for r in sparse_res:
                p = r.payload
                results.append(SearchResult(
                    chunk_id=str(r.id),
                    document_id=p.get("document_id", ""),
                    content=p.get("content", ""),
                    score=r.score,
                    metadata=p.get("metadata", {}),
                    source="sparse",
                    page=p.get("page")
                ))
            
            # RRF fusion
            return self._rrf_fusion(results)[:top_k]
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def _rrf_fusion(self, results: List[SearchResult], k: int = 60) -> List[SearchResult]:
        from collections import defaultdict
        chunk_scores = defaultdict(float)
        chunk_data = {}
        for rank, r in enumerate(results, 1):
            cid = r.chunk_id
            if cid not in chunk_data:
                chunk_data[cid] = r
            chunk_scores[cid] += 1.0 / (k + rank)
        return [chunk_data[cid] for cid, _ in sorted(chunk_scores.items(), key=lambda x: x[1], reverse=True)]


# =============================================================================
# EMBEDDING MANAGER
# =============================================================================

class EmbeddingManager:
    def __init__(self):
        self._model = None
    
    async def get_model(self):
        if self._model is None:
            try:
                from flag_embedding import FlagModel
                self._model = FlagModel(config.EMBEDDING_MODEL, use_fp16=True)
            except ImportError:
                logger.warning("flag_embedding not installed")
                self._model = None
        return self._model
    
    async def embed(self, text: str) -> Optional[List[float]]:
        try:
            model = await self.get_model()
            if not model:
                return None
            emb = model.encode(text)
            norm = np.linalg.norm(emb)
            return (emb / norm).tolist() if norm > 0 else None
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            return None


# =============================================================================
# CACHE
# =============================================================================

class EmbeddingCache:
    def __init__(self, max_size: int = 1000):
        self._cache: Dict[str, List[float]] = {}
        self._max_size = max_size
    
    def get(self, text: str) -> Optional[List[float]]:
        return self._cache.get(text)
    
    def set(self, text: str, emb: List[float]):
        if len(self._cache) >= self._max_size:
            self._cache.pop(next(iter(self._cache)))
        self._cache[text] = emb


# =============================================================================
# MAIN RAG ENGINE
# =============================================================================

class RAGHybridEngine:
    def __init__(self):
        self._qdrant = QdrantCollectionManager()
        self._embedding = EmbeddingManager()
        self._cache = EmbeddingCache(config.CACHE_MAX_SIZE)
    
    async def initialize(self):
        try:
            await self._qdrant.get_client()
        except Exception as e:
            logger.error(f"RAG init error: {e}")
    
    def _split_into_chunks(self, content: str, doc_id: str, 
                         metadata: Dict[str, Any]) -> List[DocumentChunk]:
        chunks = []
        char_chunk = 512 * 4
        lines = content.split('\n')
        current_chunk = []
        current_len = 0
        idx = 0
        
        for line in lines:
            line_len = len(line)
            if current_len + line_len > char_chunk and current_chunk:
                chunks.append(DocumentChunk(
                    chunk_id=f"{doc_id}_chunk_{idx}",
                    document_id=doc_id,
                    content='\n'.join(current_chunk),
                    metadata=metadata,
                    page=metadata.get("page")))
                current_chunk = current_chunk[-50:] + [line] if len(current_chunk) > 50 else [line]
                current_len = sum(len(l) for l in current_chunk)
                idx += 1
            else:
                current_chunk.append(line)
                current_len += line_len
        
        if current_chunk:
            chunks.append(DocumentChunk(
                chunk_id=f"{doc_id}_chunk_{idx}",
                document_id=doc_id,
                content='\n'.join(current_chunk),
                metadata=metadata,
                page=metadata.get("page")))
        return chunks
    
    async def index_document(self, document_id: str, content: str, 
                            metadata: Dict[str, Any]) -> List[str]:
        indexed = []
        chunks = self._split_into_chunks(content, document_id, metadata)
        
        for chunk in chunks:
            emb = await self._embedding.embed(chunk.content)
            if emb:
                self._cache.set(chunk.content, emb)
            chunk.embedding = emb
            if await self._qdrant.index_chunk(chunk):
                indexed.append(chunk.chunk_id)
        
        return indexed
    
    async def search(self, query: str, top_k: int = 5) -> RAGResponse:
        import time
        start = time.time()
        
        try:
            query_emb = self._cache.get(query)
            if not query_emb:
                query_emb = await self._embedding.embed(query)
                if query_emb:
                    self._cache.set(query, query_emb)
            
            results = await self._qdrant.search_hybrid(query, query_emb, top_k)
            
            return RAGResponse(
                query=query,
                results=results,
                top_k=top_k,
                processing_time_ms=(time.time()-start)*1000,
                sources_used=list(set(r.source for r in results))
            )
        except Exception as e:
            logger.error(f"RAG search error: {e}")
            return RAGResponse(query=query, results=[], top_k=top_k, 
                              processing_time_ms=0, sources_used=[])


# =============================================================================
# SINGLETON & UTILITIES
# =============================================================================

_rag_engine: Optional[RAGHybridEngine] = None

async def get_rag_engine() -> RAGHybridEngine:
    global _rag_engine
    if not _rag_engine:
        _rag_engine = RAGHybridEngine()
        await _rag_engine.initialize()
    return _rag_engine

async def rag_search_for_agent(query: str, context: Dict[str, Any], top_k: int = 3) -> List[Dict]:
    engine = await get_rag_engine()
    response = await engine.search(query, top_k)
    return [{
        "chunk_id": r.chunk_id, "document_id": r.document_id,
        "content": r.content, "score": r.score, "source": r.source,
        "page": r.page, "metadata": r.metadata
    } for r in response.results]
