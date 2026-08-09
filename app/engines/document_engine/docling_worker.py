"""SMART_AO V7.1 - Docling Worker
Worker d'extraction documentaire avec Docling (IBM).
Fallback sur PyMuPDF si Docling indisponible.
"""
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class DoclingWorker:
    """Extraction intelligente de documents DCE."""
    
    def __init__(self, use_docling: bool = True):
        self.use_docling = use_docling
        self.docling_available = False
        
        # Tentative d'import de docling
        try:
            if self.use_docling:
                from docling.document_converter import DocumentConverter
                self.converter = DocumentConverter()
                self.docling_available = True
                logger.info("Docling initialisé avec succès")
        except ImportError:
            logger.warning("Docling non disponible, fallback sur PyMuPDF")
    
    def extract(self, file_path: str) -> Dict[str, Any]:
        """Extraire le contenu d'un document."""
        path = Path(file_path)
        
        if not path.exists():
            return {"success": False, "error": "File not found"}
        
        try:
            if self.docling_available and self.use_docling:
                return self._extract_with_docling(path)
            else:
                return self._extract_with_pymupdf(path)
        except Exception as e:
            logger.error(f"Erreur extraction: {e}")
            return {"success": False, "error": str(e)}
    
    def _extract_with_docling(self, path: Path) -> Dict[str, Any]:
        """Extraction avec Docling (meilleure qualité)."""
        from docling.document_converter import DocumentConverter
        converter = DocumentConverter()
        result = converter.convert(str(path))
        
        return {
            "success": True,
            "content": result.document.export_to_text(),
            "metadata": {
                "pages": len(result.pages),
                "source": "docling"
            }
        }
    
    def _extract_with_pymupdf(self, path: Path) -> Dict[str, Any]:
        """Fallback avec PyMuPDF."""
        import fitz
        
        doc = fitz.open(path)
        text_content = []
        
        for page in doc:
            text_content.append(page.get_text())
        
        doc.close()
        
        return {
            "success": True,
            "content": "\n".join(text_content),
            "metadata": {
                "pages": len(doc),
                "source": "pymupdf"
            }
        }
    
    def batch_extract(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """Extraire plusieurs documents en lot."""
        results = []
        for path in file_paths:
            results.append(self.extract(path))
        return results

# Instance globale
docling_worker = DoclingWorker()
