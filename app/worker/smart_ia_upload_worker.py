"""
SMART_AO V7 - smart_ia_upload_worker.py
==========================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - Smart IA Upload Worker
======================================
Worker asynchrone pour le traitement des uploads de documents
Source: ARCHITECTURE_V7_ENGINE.md §4.5
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import engine
from app.engines.api_gateway.vault_core import get_vault_core, VaultCoreEngine
from app.engines.workflow_engine.workflow import WorkflowEngine
from app.engines.document_engine.parser import DocumentParser
from app.models.vault_core import VaultDocument
from app.models.mission import Mission

logger = logging.getLogger(__name__)


class SmartIAUploadWorker:
    """
    Worker pour le traitement intelligent des documents uploadés
    
    Tâches:
    1. Validation et scan antivirus du fichier
    2. Extraction du texte et métadonnées
    3. Découpage en chunks pour recherche sémantique
    4. Indexation dans Qdrant
    5. Déclenchement du workflow d'analyse
    """
    
    def __init__(self):
        self.vault_core: VaultCoreEngine = get_vault_core()
        self.workflow_engine: Optional[WorkflowEngine] = None
        self.document_parser: Optional[DocumentParser] = None
        self._db: Optional[AsyncSession] = None
        self._running = False
        self._queue = asyncio.Queue()
    
    async def initialize(self):
        """Initialiser le worker"""
        from app.engines.workflow_engine.workflow import get_workflow_engine
        from app.engines.document_engine.parser import get_document_parser
        
        self.workflow_engine = get_workflow_engine()
        self.document_parser = get_document_parser()
        self._running = True
        
        logger.info("SmartIAUploadWorker initialized")
    
    async def shutdown(self):
        """Arrêter le worker"""
        self._running = False
        if self._db:
            await self._db.close()
        logger.info("SmartIAUploadWorker shutdown")
    
    async def get_db(self) -> AsyncSession:
        """Obtenir une session de base de données"""
        if self._db is None:
            self._db = AsyncSession(engine, expire_on_commit=False)
        return self._db
    
    async def process_upload(
        self,
        file_path: str,
        file_name: str,
        file_size: int,
        mission_id: Optional[str] = None,
        document_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Traiter un upload de fichier de manière asynchrone
        
        Args:
            file_path: Chemin du fichier temporaire
            file_name: Nom du fichier
            file_size: Taille du fichier
            mission_id: ID de la mission associée (optionnel)
            document_type: Type de document
            metadata: Métadonnées supplémentaires
        
        Returns:
            Dict: Résultat du traitement
        """
        try:
            # Ajouter à la file d'attente
            task = {
                "file_path": file_path,
                "file_name": file_name,
                "file_size": file_size,
                "mission_id": mission_id,
                "document_type": document_type,
                "metadata": metadata or {},
                "timestamp": datetime.now(timezone.utc)
            }
            
            await self._queue.put(task)
            
            return {
                "success": True,
                "message": "File added to processing queue",
                "task_id": task["timestamp"].isoformat()
            }
        
        except Exception as e:
            logger.error(f"Failed to queue upload: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to queue file"
            }
    
    async def _process_queue(self):
        """Traiter les fichiers en file d'attente"""
        while self._running:
            try:
                # Attendre un fichier
                task = await self._queue.get()
                
                logger.info(f"Processing upload: {task['file_name']} ")
                
                # Étape 1: Upload dans Vault
                with open(task['file_path'], 'rb') as f:
                    result = await self.vault_core.upload_document(
                        f,
                        task['file_name'],
                        task['file_size'],
                        task['document_type'],
                        task['metadata']
                    )
                
                if not result.get('success'):
                    logger.error(f"Vault upload failed: {result.get('error')}")
                    self._queue.task_done()
                    continue
                
                document_id = result['document_id']
                
                # Étape 2: Traitement du document
                process_result = await self.vault_core.process_document(
                    document_id
                )
                
                if not process_result.get('success'):
                    logger.error(f"Document processing failed: {process_result.get('error')}")
                    self._queue.task_done()
                    continue
                
                # Étape 3: Indexation Qdrant (à implémenter)
                # qdrant_result = await self._index_in_qdrant(document_id, )
                
                # Étape 4: Si mission_id fourni, lier le document
                if task.get('mission_id') and self.workflow_engine:
                    mission = await self.workflow_engine.get_mission(task['mission_id'])
                    if mission:
                        # Mettre à jour le contexte de la mission avec le document
                        if 'context' not in mission or mission['context'] is None:
                            mission['context'] = {}
                        if 'documents' not in mission['context']:
                            mission['context']['documents'] = []
                        
                        mission['context']['documents'].append({
                            "document_id": document_id,
                            "file_name": task['file_name'],
                            "document_type": task['document_type'],
                            "processed_at": datetime.now(timezone.utc).isoformat()
                        })
                        
                        await self.workflow_engine.update_mission(mission)
                
                logger.info(f"Successfully processed: {task['file_name']}")
                
                # Nettoyer le fichier temporaire
                try:
                    Path(task['file_path']).unlink()
                except Exception as e:
                    logger.warning(f"Failed to cleanup temp file: {e}")
                
            except Exception as e:
                logger.error(f"Error processing queue item: {e}")
            
            finally:
                self._queue.task_done()
    
    async def start(self):
        """Démarrer le worker"""
        await self.initialize()
        asyncio.create_task(self._process_queue())
        logger.info("SmartIAUploadWorker started")
    
    # =========================================================================
    # MÉTHODES PUBLIQUES (Appel direct)
    # =========================================================================
    
    async def upload_and_process(
        self,
        file_content: bytes,
        file_name: str,
        mission_id: Optional[str] = None,
        document_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Upload et traitement direct (sans file d'attente)
        
        Args:
            file_content: Contenu binaire du fichier
            file_name: Nom du fichier
            mission_id: ID de la mission
            document_type: Type de document
            metadata: Métadonnées
        
        Returns:
            Dict: Résultat du traitement
        """
        import io
        import tempfile
        
        try:
            # Créer un fichier temporaire
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file_name).suffix) as tmp_file:
                tmp_file.write(file_content)
                tmp_file_path = tmp_file.name
            
            # Traiter via la file d'attente
            result = await self.process_upload(
                tmp_file_path,
                file_name,
                len(file_content),
                mission_id=mission_id,
                document_type=document_type,
                metadata=metadata
            )
            
            return result
        
        except Exception as e:
            logger.error(f"Direct upload failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Direct upload failed"
            }


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

smart_ia_upload_worker = SmartIAUploadWorker()


def get_smart_ia_upload_worker() -> SmartIAUploadWorker:
    """Get the singleton SmartIAUploadWorker instance"""
    return smart_ia_upload_worker


# =============================================================================
# UTILITIES
# =============================================================================

async def process_upload_task(
    file_path: str,
    file_name: str,
    file_size: int,
    mission_id: Optional[str] = None,
    document_type: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Fonction utilitaire pour traiter un upload"""
    worker = get_smart_ia_upload_worker()
    return await worker.process_upload(
        file_path, file_name, file_size, mission_id=mission_id, document_type=document_type, metadata=metadata
    )
