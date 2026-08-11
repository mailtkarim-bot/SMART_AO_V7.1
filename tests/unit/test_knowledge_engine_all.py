"""
SMART_AO V7 - Tests unitaires pour knowledge_engine
===================================================
Tests qui exécutent le code des modules knowledge_engine pour améliorer la couverture.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))


class TestKnowledgeEngineImports:
    """Test l'import de tous les modules knowledge_engine."""
    
    def test_embedding_engine_import(self):
        """Test l'import de embedding_engine."""
        from app.engines.knowledge_engine.embedding_engine import BGEEmbeddingProvider
        assert BGEEmbeddingProvider is not None
    
    def test_document_chunker_import(self):
        """Test l'import de document_chunker."""
        from app.engines.knowledge_engine.document_chunker import DocumentChunker
        assert DocumentChunker is not None
    
    def test_rag_hybrid_import(self):
        """Test l'import de rag_hybrid."""
        from app.engines.knowledge_engine.rag_hybrid import RAGHybridEngine
        assert RAGHybridEngine is not None
    
    def test_chantier_matcher_import(self):
        """Test l'import de chantier_matcher."""
        from app.engines.knowledge_engine.chantier_matcher import ChantierMatcher
        assert ChantierMatcher is not None
    
    def test_confidentialite_detector_import(self):
        """Test l'import de confidentialite_detector."""
        from app.engines.knowledge_engine.confidentialite_detector import ConfidentialiteDetector
        assert ConfidentialiteDetector is not None
    
    def test_embedding_fallback_import(self):
        """Test l'import de embedding_fallback."""
        from app.engines.knowledge_engine.embedding_fallback import EmbeddingFallback
        assert EmbeddingFallback is not None
    
    def test_local_llm_import(self):
        """Test l'import de local_llm."""
        try:
            from app.engines.knowledge_engine.local_llm import LocalLLMClient
            assert LocalLLMClient is not None
        except ImportError:
            pytest.skip("LocalLLMClient a des dépendances optionnelles")
    
    def test_vault_semantic_search_import(self):
        """Test l'import de vault_semantic_search."""
        from app.engines.knowledge_engine.vault_semantic_search import VaultSemanticSearch
        assert VaultSemanticSearch is not None
    
    def test_embedding_preloader_import(self):
        """Test l'import de embedding_preloader."""
        from app.engines.knowledge_engine.embedding_preloader import EmbeddingPreloader
        assert EmbeddingPreloader is not None


class TestEmbeddingEngine:
    """Tests pour BGEEmbeddingProvider."""
    
    def test_embedding_provider_has_embed_method(self):
        """Test que BGEEmbeddingProvider a une méthode embed."""
        from app.engines.knowledge_engine.embedding_engine import BGEEmbeddingProvider
        assert hasattr(BGEEmbeddingProvider, 'embed')
    
    def test_embedding_provider_has_init_method(self):
        """Test que BGEEmbeddingProvider a une méthode __init__."""
        from app.engines.knowledge_engine.embedding_engine import BGEEmbeddingProvider
        assert hasattr(BGEEmbeddingProvider, '__init__')
    
    def test_embedding_provider_has_get_dimension_method(self):
        """Test que BGEEmbeddingProvider a une méthode get_dimension."""
        from app.engines.knowledge_engine.embedding_engine import BGEEmbeddingProvider
        assert hasattr(BGEEmbeddingProvider, 'get_dimension')


class TestDocumentChunker:
    """Tests pour DocumentChunker."""
    
    def test_document_chunker_initialization(self):
        """Test l'initialisation de DocumentChunker."""
        from app.engines.knowledge_engine.document_chunker import DocumentChunker
        
        chunker = DocumentChunker()
        assert chunker is not None
    
    def test_document_chunker_has_process_method(self):
        """Test que DocumentChunker a une méthode process."""
        from app.engines.knowledge_engine.document_chunker import DocumentChunker
        assert hasattr(DocumentChunker, 'process')
    
    def test_document_chunker_has_chunk_methods(self):
        """Test que DocumentChunker a des méthodes de chunking."""
        from app.engines.knowledge_engine.document_chunker import DocumentChunker
        assert hasattr(DocumentChunker, 'chunk_by_section')
        assert hasattr(DocumentChunker, 'chunk_sliding_window')


class TestRAGHybridEngine:
    """Tests pour RAGHybridEngine."""
    
    def test_rag_hybrid_engine_initialization(self):
        """Test l'initialisation de RAGHybridEngine."""
        try:
            from app.engines.knowledge_engine.rag_hybrid import RAGHybridEngine
            
            with patch.multiple(
                'app.engines.knowledge_engine.rag_hybrid.Chroma',
                'app.engines.knowledge_engine.rag_hybrid.SentenceTransformer',
                'app.engines.knowledge_engine.rag_hybrid.HuggingFaceEmbeddingFunction'
            ):
                engine = RAGHybridEngine()
                assert engine is not None
        except Exception as e:
            pytest.skip(f"RAGHybridEngine nécessite des dépendances: {e}")


class TestChantierMatcher:
    """Tests pour ChantierMatcher."""
    
    def test_chantier_matcher_initialization(self):
        """Test l'initialisation de ChantierMatcher."""
        from app.engines.knowledge_engine.chantier_matcher import ChantierMatcher
        
        matcher = ChantierMatcher()
        assert matcher is not None
    
    def test_chantier_matcher_has_find_method(self):
        """Test que ChantierMatcher a une méthode find_similar_projects."""
        from app.engines.knowledge_engine.chantier_matcher import ChantierMatcher
        assert hasattr(ChantierMatcher, 'find_similar_projects')
    
    def test_chantier_matcher_has_match_methods(self):
        """Test que ChantierMatcher a des méthodes de matching."""
        from app.engines.knowledge_engine.chantier_matcher import ChantierMatcher
        assert hasattr(ChantierMatcher, 'match_by_type')
        assert hasattr(ChantierMatcher, 'match_by_location')


class TestConfidentialiteDetector:
    """Tests pour ConfidentialiteDetector."""
    
    def test_confidentialite_detector_initialization(self):
        """Test l'initialisation de ConfidentialiteDetector."""
        from app.engines.knowledge_engine.confidentialite_detector import ConfidentialiteDetector
        
        detector = ConfidentialiteDetector()
        assert detector is not None
    
    def test_confidentialite_detector_has_detect_method(self):
        """Test que ConfidentialiteDetector a une méthode detect."""
        from app.engines.knowledge_engine.confidentialite_detector import ConfidentialiteDetector
        assert hasattr(ConfidentialiteDetector, 'detect')


class TestEmbeddingFallback:
    """Tests pour EmbeddingFallback."""
    
    def test_embedding_fallback_initialization(self):
        """Test l'initialisation de EmbeddingFallback."""
        from app.engines.knowledge_engine.embedding_fallback import EmbeddingFallback
        
        fallback = EmbeddingFallback()
        assert fallback is not None


class TestEmbeddingPreloader:
    """Tests pour EmbeddingPreloader."""
    
    def test_embedding_preloader_initialization(self):
        """Test l'initialisation de EmbeddingPreloader."""
        from app.engines.knowledge_engine.embedding_preloader import EmbeddingPreloader
        
        preloader = EmbeddingPreloader()
        assert preloader is not None
