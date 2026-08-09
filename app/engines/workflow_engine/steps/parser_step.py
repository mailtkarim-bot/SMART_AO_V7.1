"""
SMART_AO V7 - parser_step.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""

from typing import Dict, Any, List
from pathlib import Path
import logging
from datetime import datetime

from app.engines.workflow_engine.steps.base_step import BaseStep
from app.engines.document_engine.parser import DocumentParser
from app.models.mission import Mission
from app.schemas.workflow import StepResult, StepStatus

logger = logging.getLogger(__name__)


class ParserStep(BaseStep):
    """
    Étape 1: Parsing des documents DCE (CCTP, CCAP, BPU, etc.)
    
    Responsabilités:
    - Charger les fichiers PDF/uploadés
    - Extraire le texte brut avec métadonnées
    - Détecter la structure documentaire (sections, chapitres)
    - Valider la complétude des pièces administratives
    """
    
    step_name = "parser"
    step_order = 1
    required_capabilities = ["document_parsing", "pdf_extraction"]
    
    async def execute(self, mission: Mission, context: Dict[str, Any]) -> StepResult:
        """
        Exécute le parsing des documents du DCE
        
        Args:
            mission: La mission en cours de traitement
            context: Contexte d'exécution contenant les chemins de fichiers
            
        Returns:
            StepResult avec les documents parsés ou erreur détaillée
        """
        try:
            logger.info(f"[ParserStep] Démarrage parsing pour mission {mission.id}")
            
            # Récupérer les chemins des fichiers depuis le contexte
            files_path = context.get("files_path")
            if not files_path:
                return StepResult(
                    status=StepStatus.FAILED,
                    error="Aucun chemin de fichier fourni dans le contexte",
                    data={}
                )
            
            # Initialiser le parser de documents
            parser = DocumentParser()
            
            # Lister tous les fichiers PDF à parser
            pdf_files = list(Path(files_path).glob("*.pdf"))
            if not pdf_files:
                return StepResult(
                    status=StepStatus.FAILED,
                    error=f"Aucun fichier PDF trouvé dans {files_path}",
                    data={}
                )
            
            logger.info(f"[ParserStep] {len(pdf_files)} fichiers PDF à parser")
            
            # Parser chaque document
            parsed_documents = []
            for pdf_file in pdf_files:
                try:
                    logger.debug(f"[ParserStep] Parsing de {pdf_file.name}")
                    
                    # Extraire le contenu du PDF
                    parsed_content = await parser.extract_text(str(pdf_file))
                    
                    # Détecter le type de document (CCTP, CCAP, BPU, etc.)
                    doc_type = await parser.detect_document_type(parsed_content)
                    
                    # Extraire la structure (sections, chapitres)
                    structure = await parser.extract_structure(parsed_content)
                    
                    parsed_documents.append({
                        "filename": pdf_file.name,
                        "filepath": str(pdf_file),
                        "doc_type": doc_type,
                        "content": parsed_content,
                        "structure": structure,
                        "pages_count": len(parsed_content.get("pages", [])),
                        "parsed_at": datetime.utcnow().isoformat()
                    })
                    
                    logger.info(f"[ParserStep] {pdf_file.name} parsé avec succès ({doc_type})")
                    
                except Exception as e:
                    logger.error(f"[ParserStep] Erreur lors du parsing de {pdf_file.name}: {str(e)}")
                    parsed_documents.append({
                        "filename": pdf_file.name,
                        "error": str(e),
                        "status": "failed"
                    })
            
            # Vérifier la complétude des pièces administratives obligatoires
            completeness_check = self._check_administrative_completeness(parsed_documents)
            
            # Préparer le résultat
            result_data = {
                "parsed_documents": parsed_documents,
                "total_files": len(pdf_files),
                "successful_parses": len([d for d in parsed_documents if "error" not in d]),
                "failed_parses": len([d for d in parsed_documents if "error" in d]),
                "completeness": completeness_check,
                "next_step": "extraction"
            }
            
            return StepResult(
                status=StepStatus.COMPLETED,
                data=result_data,
                message=f"Parsing terminé: {result_data['successful_parses']}/{result_data['total_files']} fichiers traités"
            )
            
        except Exception as e:
            logger.exception(f"[ParserStep] Erreur critique: {str(e)}")
            return StepResult(
                status=StepStatus.FAILED,
                error=f"Échec critique du parsing: {str(e)}",
                data={}
            )
    
    def _check_administrative_completeness(self, parsed_documents: List[Dict]) -> Dict[str, Any]:
        """
        Vérifie la présence des pièces administratives obligatoires
        
        Returns:
            Dict avec état de complétude et pièces manquantes
        """
        required_docs = {
            "CCTP": False,
            "CCAP": False,
            "BPU": False,
            "DPGF": False,
            "RC": False  # Règlement de Consultation
        }
        
        doc_keywords = {
            "CCTP": ["cahier", "clauses", "techniques", "particulières"],
            "CCAP": ["cahier", "clauses", "administratives", "particulières"],
            "BPU": ["bordereau", "prix", "unitaires"],
            "DPGF": ["décomposition", "prix", "global", "forfaitaire"],
            "RC": ["règlement", "consultation", "avis", "appel"]
        }
        
        for doc in parsed_documents:
            if "error" in doc:
                continue
                
            content_lower = doc.get("content", "").lower()
            detected_type = doc.get("doc_type", "").upper()
            
            # Si le type est déjà détecté
            if detected_type in required_docs:
                required_docs[detected_type] = True
            else:
                # Sinon chercher par mots-clés
                for doc_type, keywords in doc_keywords.items():
                    if any(keyword in content_lower for keyword in keywords):
                        required_docs[doc_type] = True
        
        missing_docs = [doc_type for doc_type, present in required_docs.items() if not present]
        completeness_rate = ((len(required_docs) - len(missing_docs)) / len(required_docs)) * 100
        
        return {
            "required_documents": required_docs,
            "missing_documents": missing_docs,
            "completeness_rate": round(completeness_rate, 2),
            "is_complete": len(missing_docs) == 0,
            "warning": "DCE incomplet - certaines pièces obligatoires manquent" if missing_docs else None
        }

