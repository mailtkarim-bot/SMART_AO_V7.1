"""Docling Worker - OCR et extraction avancée de documents"""
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class DoclingWorker:
    """Worker pour l'OCR et l'extraction de documents complexes"""
    
    def __init__(self, use_gpu: bool = False):
        self.use_gpu = use_gpu
        self.model = None
    
    def _load_model(self):
        """Charge le modèle OCR si nécessaire"""
        if self.model is None:
            try:
                # PyMuPDF comme fallback toujours disponible
                import fitz
                self.model = "pymupdf"
                logger.info("Modèle OCR chargé: PyMuPDF")
            except ImportError:
                logger.warning("PyMuPDF non disponible")
                self.model = "fallback"
    
    async def process_document(self, file_path: str) -> Dict[str, Any]:
        """Traite un document avec OCR si nécessaire"""
        self._load_model()
        
        result = {
            "file_path": file_path,
            "text": "",
            "pages": [],
            "tables": [],
            "images": [],
            "metadata": {}
        }
        
        try:
            if self.model == "pymupdf":
                return await self._process_with_pymupdf(file_path, result)
            else:
                return await self._process_fallback(file_path, result)
        except Exception as e:
            logger.error(f"Échec traitement document {file_path}: {str(e)}")
            result["error"] = str(e)
            return result
    
    async def _process_with_pymupdf(self, file_path: str, result: Dict) -> Dict:
        """Extraction avec PyMuPDF"""
        import fitz
        
        doc = fitz.open(file_path)
        full_text = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            full_text.append(text)
            
            # Extraction tables
            tables = page.find_tables()
            for table in tables:
                result["tables"].append({
                    "page": page_num,
                    "data": table.extract()
                })
            
            result["pages"].append({
                "number": page_num,
                "text": text,
                "width": page.rect.width,
                "height": page.rect.height
            })
        
        doc.close()
        result["text"] = "\n".join(full_text)
        result["metadata"]["page_count"] = len(full_text)
        
        return result
    
    async def _process_fallback(self, file_path: str, result: Dict) -> Dict:
        """Fallback simple lecture texte"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                result["text"] = f.read()
            result["metadata"]["method"] = "simple_read"
        except UnicodeDecodeError:
            result["text"] = ""
            result["error"] = "Impossible de lire le fichier (binaire ou encodage inconnu)"
        
        return result
    
    async def extract_tables(self, file_path: str) -> List[Dict]:
        """Extrait spécifiquement les tableaux d'un document"""
        result = await self.process_document(file_path)
        return result.get("tables", [])

# Instance globale
docling_worker = DoclingWorker()
