"""Embedding Fallback - Stratégies de repli pour les embeddings"""
from typing import List, Optional
import hashlib
import logging

logger = logging.getLogger(__name__)

class EmbeddingFallback:
    """Gère les fallbacks quand les modèles d'embedding principaux échouent"""
    
    def __init__(self):
        self.strategies = ["hash_based", "keyword_vector", "random_deterministic"]
    
    def generate_hash_embedding(self, text: str, dimensions: int = 1024) -> List[float]:
        """Génère un embedding basé sur le hash du texte (déterministe)"""
        # Hash SHA-256 comme seed
        hash_obj = hashlib.sha256(text.encode('utf-8'))
        hash_bytes = hash_obj.digest()
        
        # Conversion en vecteur de floats
        embedding = []
        for i in range(dimensions):
            byte_idx = i % len(hash_bytes)
            normalized = hash_bytes[byte_idx] / 255.0
            embedding.append(normalized)
        
        return embedding
    
    def generate_keyword_vector(self, text: str, keywords: List[str]) -> List[float]:
        """Génère un vecteur basé sur la présence de mots-clés"""
        text_lower = text.lower()
        vector = []
        
        for keyword in keywords:
            count = text_lower.count(keyword.lower())
            # Normalisation simple
            score = min(count / 10.0, 1.0)
            vector.append(score)
        
        return vector
    
    def get_fallback_embedding(
        self, 
        text: str, 
        dimensions: int = 1024,
        strategy: str = "hash_based"
    ) -> Optional[List[float]]:
        """Obtient un embedding de repli selon la stratégie"""
        try:
            if strategy == "hash_based":
                return self.generate_hash_embedding(text, dimensions)
            elif strategy == "keyword_vector":
                # Mots-clés BTP par défaut
                keywords_btp = [
                    "travaux", "chantier", "marché", "prix", "délai", 
                    "pénalité", "CCTP", "CCAP", "BPU", "DPGF"
                ]
                return self.generate_keyword_vector(text, keywords_btp)
            else:
                logger.warning(f"Stratégie inconnue: {strategy}")
                return None
        except Exception as e:
            logger.error(f"Échec fallback embedding: {str(e)}")
            return None

# Instance globale
fallback = EmbeddingFallback()
