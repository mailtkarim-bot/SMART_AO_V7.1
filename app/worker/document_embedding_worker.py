"""
SMART_AO V7 - document_embedding_worker.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - Document Embedding Worker
=======================================
Worker asynchrone pour la génération d'embeddings de documents
Utilise Qdrant pour l'indexation et la recherche vectorielle

Source: ARCHITECTURE_V7_ENGINE.md §4.4
"""

import asyncio
import logging
import os
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import hashlib

# Imports conditionnels
try:
    from qdrant_client import QdrantClient, models
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    logging.warning("Qdrant client not available. Embedding worker will use fallback.")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    logging.warning("NumPy not available. Some embedding features will be limited.")

logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class EmbeddingConfig:
    """Configuration pour le worker d'embedding."""
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    collection_name: str = "vault_documents"
    
    # Configuration des embeddings
    model_name: str = "bge-m3"  # ou "sentence-transformers/all-mpnet-base-v2"
    dimension: int = 1024  # Dimension des embeddings
    batch_size: int = 32
    
    # Configuration de stockage
    temp_directory: str = "/tmp/embeddings"
    cache_enabled: bool = True
    
    # Seuil de similarité
    similarity_threshold: float = 0.7


# Configuration par défaut
config = EmbeddingConfig()


# =============================================================================
# STRUCTURES DE DONNÉES
# =============================================================================

@dataclass
class DocumentChunk:
    """Représente un chunk de document pour embedding."""
    document_id: str
    chunk_id: str
    text: str
    page: int
    position: int
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire."""
        return {
            "document_id": self.document_id,
            "chunk_id": self.chunk_id,
            "text": self.text,
            "page": self.page,
            "position": self.position,
            **self.metadata
        }


@dataclass
class EmbeddingResult:
    """Résultat d'un embedding."""
    chunk: DocumentChunk
    embedding: Optional[List[float]] = None
    generated_at: datetime = datetime.now(timezone.utc)
    model: str = ""
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire."""
        result = {
            "chunk": self.chunk.to_dict(),
            "generated_at": self.generated_at.isoformat(),
            "model": self.model,
            "error": self.error
        }
        
        if self.embedding is not None:
            result["embedding"] = self.embedding
        
        return result


@dataclass
class QdrantRecord:
    """Record pour Qdrant."""
    id: str
    vector: List[float]
    payload: Dict[str, Any]


# =============================================================================
# SERVICE D'EMBEDDING
# =============================================================================

class EmbeddingService:
    """
    Service de génération d'embeddings pour les documents.
    
    Fonctionnalités:
    - Génération d'embeddings avec différents modèles
    - Indexation dans Qdrant
    - Recherche vectorielle
    - Gestion du cache
    """
    
    def __init__(self, config: EmbeddingConfig = None):
        self.config = config or EmbeddingConfig()
        self.qdrant_client: Optional[Any] = None
        
        if QDRANT_AVAILABLE:
            try:
                self.qdrant_client = QdrantClient(
                    host=self.config.qdrant_host,
                    port=self.config.qdrant_port
                )
                logger.info(f"Connexion à Qdrant: {self.config.qdrant_host}:{self.config.qdrant_port}")
            except Exception as e:
                logger.error(f"Erreur de connexion à Qdrant: {e}")
        
        # Créer le répertoire temporaire
        os.makedirs(self.config.temp_directory, exist_ok=True)
    
    def _generate_chunk_id(self, document_id: str, page: int, position: int) -> str:
        """Générer un ID unique pour un chunk."""
        return hashlib.sha256(f"{document_id}_{page}_{position}".encode()).hexdigest()
    
    def _generate_embedding_id(self, chunk_id: str) -> str:
        """Générer un ID unique pour un embedding."""
        return hashlib.sha256(f"{chunk_id}_{self.config.model_name}".encode()).hexdigest()
    
    def generate_mock_embedding(self, text: str, dimension: int = 1024) -> List[float]:
        """
        Générer un embedding mock (pour les tests sans modèle IA).
        
        Args:
            text: Texte à embedder
            dimension: Dimension de l'embedding
        
        Returns:
            List[float]: Embedding mock
        """
        # Simple hash-based embedding for testing
        hash_obj = hashlib.sha256(text.encode())
        hash_int = int(hash_obj.hexdigest(), 16)
        
        # Créer un embedding basé sur le hash
        if NUMPY_AVAILABLE:
            np.random.seed(hash_int % (2**32))
            return np.random.randn(dimension).tolist()
        else:
            # Sans NumPy, créer un embedding simple
            base = hash_int / (2**256)
            return [(base * (i + 1)) % 2 - 1 for i in range(dimension)]
    
    def generate_embedding(self, text: str) -> Tuple[List[float], str]:
        """
        Générer un embedding pour un texte.
        
        Args:
            text: Texte à embedder
        
        Returns:
            Tuple[List[float], str]: (embedding, model_name)
        """
        # Pour l'instant, on utilise l'embedding mock
        # En production, cela serait remplacé par un appel à l'API BGE-M3
        embedding = self.generate_mock_embedding(text, self.config.dimension)
        return embedding, self.config.model_name
    
    def generate_embeddings(self, chunks: List[DocumentChunk]) -> List[EmbeddingResult]:
        """
        Générer des embeddings pour une liste de chunks.
        
        Args:
            chunks: Liste de chunks de document
        
        Returns:
            List[EmbeddingResult]: Liste de résultats d'embedding
        """
        results = []
        
        for chunk in chunks:
            try:
                embedding, model = self.generate_embedding(chunk.text)
                result = EmbeddingResult(
                    chunk=chunk,
                    embedding=embedding,
                    model=model
                )
                results.append(result)
                logger.debug(f"Embedding généré pour chunk {chunk.chunk_id}")
            except Exception as e:
                logger.error(f"Erreur lors de la génération de l'embedding pour {chunk.chunk_id}: {e}")
                result = EmbeddingResult(
                    chunk=chunk,
                    error=str(e),
                    model=self.config.model_name
                )
                results.append(result)
        
        return results
    
    async def index_in_qdrant(self, embeddings: List[EmbeddingResult]) -> int:
        """
        Indexer les embeddings dans Qdrant.
        
        Args:
            embeddings: Liste de résultats d'embedding
        
        Returns:
            int: Nombre d'embeddings indexés
        """
        if not QDRANT_AVAILABLE or not self.qdrant_client:
            logger.warning("Qdrant non disponible. Indexation sautée.")
            return 0
        
        try:
            # Vérifier que la collection existe
            try:
                self.qdrant_client.get_collection(self.config.collection_name)
            except:
                # Créer la collection si elle n'existe pas
                self.qdrant_client.create_collection(
                    collection_name=self.config.collection_name,
                    vectors_config=models.VectorParams(
                        size=self.config.dimension,
                        distance=models.Distance.COSINE
                    )
                )
                logger.info(f"Collection {self.config.collection_name} créée")
            
            # Préparer les records Qdrant
            records = []
            for embedding in embeddings:
                if embedding.embedding is None:
                    continue
                
                payload = {
                    "document_id": embedding.chunk.document_id,
                    "chunk_id": embedding.chunk.chunk_id,
                    "text": embedding.chunk.text[:500],  # Limiter la taille
                    "page": embedding.chunk.page,
                    "position": embedding.chunk.position,
                    "generated_at": embedding.generated_at.isoformat(),
                    "model": embedding.model,
                    **embedding.chunk.metadata
                }
                
                record = QdrantRecord(
                    id=embedding.chunk.chunk_id,
                    vector=embedding.embedding,
                    payload=payload
                )
                records.append(record)
            
            # Upsert dans Qdrant
            if records:
                self.qdrant_client.upsert(
                    collection_name=self.config.collection_name,
                    points=models.Batch(
                        ids=[r.id for r in records],
                        vectors=[r.vector for r in records],
                        payloads=[r.payload for r in records]
                    )
                )
                logger.info(f"{len(records)} embeddings indexés dans Qdrant")
                return len(records)
            else:
                return 0
                
        except Exception as e:
            logger.error(f"Erreur lors de l'indexation dans Qdrant: {e}")
            return 0
    
    def search_similar(self, query_text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Rechercher des documents similaires dans Qdrant.
        
        Args:
            query_text: Texte de la requête
            limit: Nombre maximum de résultats
        
        Returns:
            List[Dict[str, Any]]: Liste de résultats
        """
        if not QDRANT_AVAILABLE or not self.qdrant_client:
            logger.warning("Qdrant non disponible. Recherche non disponible.")
            return []
        
        try:
            # Générer l'embedding de la requête
            query_embedding, _ = self.generate_embedding(query_text)
            
            # Rechercher dans Qdrant
            search_result = self.qdrant_client.search(
                collection_name=self.config.collection_name,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=self.config.similarity_threshold
            )
            
            # Formater les résultats
            results = []
            for scored_point in search_result:
                results.append({
                    "id": scored_point.id,
                    "score": scored_point.score,
                    "payload": scored_point.payload
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche: {e}")
            return []


# =============================================================================
# WORKER PRINCIPAL
# =============================================================================

class DocumentEmbeddingWorker:
    """
    Worker asynchrone pour le traitement des embeddings de documents.
    
    Responsabilités:
    - Réception des documents à traiter
    - Découpage en chunks
    - Génération des embeddings
    - Indexation dans Qdrant
    - Gestion des erreurs
    """
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.processing: bool = False
        self.queue: asyncio.Queue = asyncio.Queue()
        self.results: Dict[str, List[EmbeddingResult]] = {}
        
    def split_text_into_chunks(self, text: str, max_length: int = 512) -> List[str]:
        """
        Diviser un texte en chunks de taille maximale.
        
        Args:
            text: Texte à diviser
            max_length: Taille maximale d'un chunk
        
        Returns:
            List[str]: Liste de chunks
        """
        chunks = []
        
        # Division simple par phrases ou paragraphes
        paragraphs = text.split("\n\n")
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) + 2 <= max_length:
                current_chunk += ("\n\n" if current_chunk else "") + para
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = para
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def create_chunks_from_document(
        self,
        document_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[DocumentChunk]:
        """
        Créer des chunks à partir d'un document.
        
        Args:
            document_id: ID du document
            text: Texte du document
            metadata: Métadonnées du document
        
        Returns:
            List[DocumentChunk]: Liste de chunks
        """
        chunks_text = self.split_text_into_chunks(text)
        
        chunks = []
        for i, chunk_text in enumerate(chunks_text):
            chunk_id = self.embedding_service._generate_chunk_id(
                document_id, i, i
            )
            chunk = DocumentChunk(
                document_id=document_id,
                chunk_id=chunk_id,
                text=chunk_text,
                page=metadata.get("page", 1) if metadata else 1,
                position=i,
                metadata=metadata or {}
            )
            chunks.append(chunk)
        
        return chunks
    
    async def process_document(
        self,
        document_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[EmbeddingResult]:
        """
        Traiter un document complet (découpage + embedding + indexation).
        
        Args:
            document_id: ID du document
            text: Texte du document
            metadata: Métadonnées du document
        
        Returns:
            List[EmbeddingResult]: Résultats de l'embedding
        """
        # Créer les chunks
        chunks = self.create_chunks_from_document(document_id, text, metadata)
        logger.info(f"Document {document_id}: {len(chunks)} chunks créés")
        
        # Générer les embeddings
        embeddings = self.embedding_service.generate_embeddings(chunks)
        logger.info(f"Document {document_id}: {len(embeddings)} embeddings générés")
        
        # Indexer dans Qdrant
        indexed_count = await self.embedding_service.index_in_qdrant(embeddings)
        logger.info(f"Document {document_id}: {indexed_count} embeddings indexés")
        
        return embeddings
    
    async def process_batch(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Traiter un batch de documents.
        
        Args:
            documents: Liste de documents à traiter
        
        Returns:
            Dict[str, Any]: Résumé du traitement
        """
        total_chunks = 0
        total_indexed = 0
        errors = []
        results = {}
        
        for doc in documents:
            document_id = doc.get("id", "unknown")
            text = doc.get("text", "")
            metadata = doc.get("metadata", {})
            
            try:
                embeddings = await self.process_document(document_id, text, metadata)
                results[document_id] = [e.to_dict() for e in embeddings]
                total_chunks += len(embeddings)
                total_indexed += sum(1 for e in embeddings if e.embedding is not None)
            except Exception as e:
                logger.error(f"Erreur lors du traitement du document {document_id}: {e}")
                errors.append({"document_id": document_id, "error": str(e)})
        
        return {
            "total_documents": len(documents),
            "total_chunks": total_chunks,
            "total_indexed": total_indexed,
            "errors": errors,
            "results": results
        }
    
    async def start(self) -> None:
        """Démarrer le worker."""
        self.processing = True
        logger.info("DocumentEmbeddingWorker démarré")
        
        while self.processing:
            try:
                # Attendre une tâche
                task = await self.queue.get()
                
                # Traiter la tâche
                document_id = task.get("document_id")
                text = task.get("text")
                metadata = task.get("metadata")
                
                if document_id and text:
                    embeddings = await self.process_document(document_id, text, metadata)
                    self.results[document_id] = embeddings
                
                # Marquer la tâche comme terminée
                self.queue.task_done()
                
            except Exception as e:
                logger.error(f"Erreur dans le worker: {e}")
            
            await asyncio.sleep(0.1)  # Éviter la boucle serrée
    
    async def stop(self) -> None:
        """Arrêter le worker."""
        self.processing = False
        logger.info("DocumentEmbeddingWorker arrêté")


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

# Instance globale du worker
worker: Optional[DocumentEmbeddingWorker] = None


async def get_embedding_worker() -> DocumentEmbeddingWorker:
    """
    Récupérer l'instance globale du worker.
    """
    global worker
    if worker is None:
        worker = DocumentEmbeddingWorker()
    return worker


async def process_document_async(
    document_id: str,
    text: str,
    metadata: Optional[Dict[str, Any]] = None
) -> List[EmbeddingResult]:
    """
    Traiter un document de manière asynchrone.
    
    Args:
        document_id: ID du document
        text: Texte du document
        metadata: Métadonnées du document
    
    Returns:
        List[EmbeddingResult]: Résultats de l'embedding
    """
    worker = await get_embedding_worker()
    return await worker.process_document(document_id, text, metadata)


async def search_similar_documents(
    query_text: str,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Rechercher des documents similaires.
    
    Args:
        query_text: Texte de la requête
        limit: Nombre maximum de résultats
    
    Returns:
        List[Dict[str, Any]]: Résultats de la recherche
    """
    service = EmbeddingService()
    return service.search_similar(query_text, limit)


if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Tester le worker
        worker = DocumentEmbeddingWorker()
        
        # Exemple de document
        document_id = "test_doc_001"
        text = """
        Ce document traite de la construction de bâtiments en Béton Armé.
        Les spécifications techniques incluent des normes strictes pour la qualité du béton.
        Le chantier doit être terminé dans un délai de 12 mois.
        """
        metadata = {
            "type": "DCE",
            "date": "2026-08-06",
            "author": "SMART_AO"
        }
        
        # Traiter le document
        results = await worker.process_document(document_id, text, metadata)
        
        print(f"Document traité: {document_id}")
        print(f"Nombre de chunks: {len(results)}")
        for result in results:
            print(f"  Chunk {result.chunk.chunk_id}: {len(result.chunk.text)} caractères")
            if result.embedding:
                print(f"    Embedding: {len(result.embedding)} dimensions")
            if result.error:
                print(f"    Erreur: {result.error}")
        
        # Tester la recherche
        if QDRANT_AVAILABLE:
            similar = await search_similar_documents("construction béton", limit=3)
            print(f"\nRecherche similaire: {len(similar)} résultats")
            for doc in similar:
                print(f"  Score: {doc['score']:.4f}, ID: {doc['id']}")
    
    asyncio.run(main())

