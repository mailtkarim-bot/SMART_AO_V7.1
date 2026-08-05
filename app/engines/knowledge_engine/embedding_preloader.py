"""
SMART_AO V7 - Embedding Preloader (BGE-M3)
"""
from typing import List, Dict, Optional
import numpy as np

class EmbeddingPreloader:
    def __init__(self, model_name: str = "BAAI/bge-m3"):
        self.model_name = model_name
    
    def get_embedding_dim(self) -> int:
        return 1024  # BGE-M3 dimension
    
    def encode(self, texts: List[str]) -> np.ndarray:
        return np.zeros((len(texts), self.get_embedding_dim()))
