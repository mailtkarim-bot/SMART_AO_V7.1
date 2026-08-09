"""Document Chunker - Découpage intelligent de documents pour RAG"""
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class DocumentChunker:
    """Découpe les documents en chunks optimisés pour l'embedding"""
    
    def __init__(self, chunk_size: int = 512, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_by_section(self, text: str, metadata: Dict[str, Any]) -> List[Dict]:
        """Découpage par sections sémantiques"""
        chunks = []
        sections = text.split('\n\n')
        
        current_chunk = ""
        for section in sections:
            if len(current_chunk) + len(section) > self.chunk_size:
                chunks.append({
                    "content": current_chunk.strip(),
                    "metadata": metadata.copy(),
                    "type": "section"
                })
                current_chunk = section
            else:
                current_chunk += "\n\n" + section
        
        if current_chunk.strip():
            chunks.append({
                "content": current_chunk.strip(),
                "metadata": metadata,
                "type": "section"
            })
        
        return chunks
    
    def chunk_sliding_window(self, text: str, metadata: Dict[str, Any]) -> List[Dict]:
        """Découpage par fenêtre glissante"""
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), self.chunk_size - self.overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = " ".join(chunk_words)
            
            chunks.append({
                "content": chunk_text,
                "metadata": {**metadata, "position": i},
                "type": "sliding_window"
            })
        
        return chunks
    
    def process(self, document: Dict[str, Any]) -> List[Dict]:
        """Traite un document complet"""
        text = document.get("content", "")
        metadata = document.get("metadata", {})
        
        # Combinaison des stratégies
        section_chunks = self.chunk_by_section(text, metadata)
        
        if len(section_chunks) < 3:
            # Si trop peu de sections, utiliser sliding window
            return self.chunk_sliding_window(text, metadata)
        
        return section_chunks

# Instance globale
chunker = DocumentChunker()
