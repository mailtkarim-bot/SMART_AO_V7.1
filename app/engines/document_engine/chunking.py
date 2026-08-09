"""
SMART_AO V7 - chunking.py
=========================
Découpage intelligent des documents en chunks pour le RAG.
Préserve le contexte sémantique et les références croisées.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class DocumentChunker:
    """Chunker intelligent pour documents BTP."""

    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size  # tokens approximatifs
        self.overlap = overlap  # chevauchement entre chunks
        self.chunking_stats = {
            "documents_chunked": 0,
            "total_chunks": 0,
            "average_chunks_per_doc": 0
        }

    async def chunk_document(self, text_content: str, doc_type: str = "", 
                              filename: str = "") -> List[Dict[str, Any]]:
        """
        Découpe un document en chunks sémantiques.
        
        Args:
            text_content: Contenu textuel du document
            doc_type: Type de document (CCAP, CCTP, etc.)
            filename: Nom du fichier
            
        Returns:
            Liste de chunks avec métadonnées
        """
        logger.debug(f"Chunking du document : {filename[:50] if filename else 'inconnu'}")
        
        if not text_content or len(text_content) < 100:
            return []

        # Nettoyage préalable
        cleaned_text = self._clean_text(text_content)
        
        # Stratégie de chunking selon le type de document
        if doc_type in ["CCAP", "CCTP"]:
            chunks = self._chunk_by_sections(cleaned_text, doc_type, filename)
        elif doc_type in ["BPU", "DPGF", "DQE"]:
            chunks = self._chunk_financial_tables(cleaned_text, doc_type, filename)
        else:
            chunks = self._chunk_sliding_window(cleaned_text, doc_type, filename)

        # Mise à jour des stats
        self.chunking_stats["documents_chunked"] += 1
        self.chunking_stats["total_chunks"] += len(chunks)
        self.chunking_stats["average_chunks_per_doc"] = (
            self.chunking_stats["total_chunks"] / 
            self.chunking_stats["documents_chunked"]
        )

        logger.debug(f"Document découpé en {len(chunks)} chunks")
        return chunks

    def _clean_text(self, text: str) -> str:
        """Nettoie le texte avant chunking."""
        # Suppression des espaces multiples
        import re
        text = re.sub(r'\s+', ' ', text)
        # Suppression des caractères spéciaux non utiles
        text = text.replace('\x00', '')
        return text.strip()

    def _chunk_by_sections(self, text: str, doc_type: str, filename: str) -> List[Dict]:
        """Chunking par sections logiques (titres, articles)."""
        chunks = []
        
        # Détection des sections par motifs typiques
        section_patterns = [
            r'(Article\s*\d+[^.\n]*[.\n])',
            r'(Chapitre\s+\w+[^.\n]*[.\n])',
            r'(Section\s+\d+[^.\n]*[.\n])',
            r'(\d+\.\s+[A-Z][^.\n]*[.\n])'
        ]
        
        sections = self._split_by_patterns(text, section_patterns)
        
        for idx, section in enumerate(sections):
            if len(section.strip()) > 200:  # Ignore sections trop courtes
                chunks.append({
                    "chunk_id": f"{filename}_{idx}" if filename else f"chunk_{idx}",
                    "content": section.strip(),
                    "chunk_type": "section",
                    "doc_type": doc_type,
                    "position": idx,
                    "total_sections": len(sections),
                    "created_at": datetime.utcnow().isoformat()
                })
        
        return chunks if chunks else self._chunk_sliding_window(text, doc_type, filename)

    def _chunk_financial_tables(self, text: str, doc_type: str, filename: str) -> List[Dict]:
        """Chunking spécialisé pour tableaux financiers (BPU, DPGF, DQE)."""
        chunks = []
        
        lines = text.split('\n')
        current_table = []
        
        for line in lines:
            # Détection de ligne de tableau (présence de chiffres et devises)
            if any(char.isdigit() for char in line) and len(line) > 20:
                current_table.append(line)
            else:
                if current_table and len(current_table) >= 3:
                    table_text = '\n'.join(current_table)
                    chunks.append({
                        "chunk_id": f"{filename}_table_{len(chunks)}" if filename else f"table_{len(chunks)}",
                        "content": table_text,
                        "chunk_type": "financial_table",
                        "doc_type": doc_type,
                        "position": len(chunks),
                        "created_at": datetime.utcnow().isoformat()
                    })
                current_table = []
        
        return chunks

    def _chunk_sliding_window(self, text: str, doc_type: str, filename: str) -> List[Dict]:
        """Chunking par fenêtre glissante avec overlap."""
        chunks = []
        
        words = text.split()
        total_words = len(words)
        
        if total_words == 0:
            return chunks
        
        step_size = self.chunk_size - self.overlap
        position = 0
        
        while position < total_words:
            end_position = min(position + self.chunk_size, total_words)
            chunk_words = words[position:end_position]
            
            if len(chunk_words) > 20:  # Ignore chunks trop courts
                chunks.append({
                    "chunk_id": f"{filename}_{position}" if filename else f"chunk_{position}",
                    "content": ' '.join(chunk_words),
                    "chunk_type": "sliding_window",
                    "doc_type": doc_type,
                    "position": len(chunks),
                    "word_count": len(chunk_words),
                    "created_at": datetime.utcnow().isoformat()
                })
            
            position += step_size
            
            if end_position >= total_words:
                break
        
        return chunks

    def _split_by_patterns(self, text: str, patterns: List[str]) -> List[str]:
        """Split le texte selon des regex patterns."""
        import re
        
        combined_pattern = '|'.join(f'({p})' for p in patterns)
        matches = list(re.finditer(combined_pattern, text, re.IGNORECASE))
        
        if not matches:
            return [text]  # Retourne le texte entier si aucun pattern trouvé
        
        sections = []
        last_end = 0
        
        for match in matches:
            if match.start() > last_end:
                sections.append(text[last_end:match.start()])
            sections.append(match.group(0))
            last_end = match.end()
        
        if last_end < len(text):
            sections.append(text[last_end:])
        
        return sections

    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de chunking."""
        return self.chunking_stats.copy()
