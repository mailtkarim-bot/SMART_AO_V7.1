"""
SMART_AO V7 - enveloppe_separator.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 07/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - Enveloppe Separator Engine
Source: ARCHITECTURE_V7_ENGINE.md §4 + ADR-044 + RAPPORT_V102 §130

CERVEAU (transverse) : M5 RAG (BGE-M3 + Qdrant) + M4 GARAGE MATH (BTP ENGINE)
OUTPUT : 3 ENVELOPPES ZIP (Candidature | Technique | Financière)

Responsabilités:
- Classification des documents dans les 3 enveloppes canoniques
- Génération des ZIP avec manifest.json
- Chiffrement des enveloppes FINANCIERE (RGPD/AI Act)
- Intégration avec le Vault (12 docs core A01-A12)
- Respect des règles de séparation Admin/Salarié

Principe : Le salarié ne voit pas les euros. L'admin voit TOUT.
Sécurité : L'enveloppe FINANCIERE est chiffrée + RBAC admin-only.
"""

import asyncio
import json
import logging
import os
import shutil
import zipfile
from base64 import urlsafe_b64encode
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.core.config import settings

logger = logging.getLogger(__name__)


# =============================================================================
# SECURITY - CHIFREMENT RGPD/AI ACT
# =============================================================================

class EnvelopeEncryption:
    """
    Gestion du chiffrement des enveloppes pour conformité RGPD/AI Act.
    
    Seul l'enveloppe FINANCIERE est chiffrée (contient des données sensibles).
    
    Méthode: Fernet (AES-128-CBC) avec clé dérivée de STORAGE_ENCRYPTION_KEY
    """
    
    _fernet: Optional[Fernet] = None
    
    @classmethod
    def get_fernet(cls) -> Optional[Fernet]:
        """Récupère ou crée l'instance Fernet."""
        if cls._fernet is None:
            try:
                # Récupérer la clé depuis les settings
                encryption_key = settings.STORAGE_ENCRYPTION_KEY
                
                if not encryption_key:
                    logger.warning("STORAGE_ENCRYPTION_KEY non configuré. Le chiffrement est désactivé.")
                    return None
                
                # Si la clé est en base64, la décoder
                try:
                    import base64
                    encryption_key = base64.urlsafe_b64decode(encryption_key)
                except Exception:
                    # La clé est peut-être déjà en bytes
                    if isinstance(encryption_key, str):
                        encryption_key = encryption_key.encode()
                
                # Vérifier la longueur (Fernet nécessite 32 bytes)
                if len(encryption_key) != 32:
                    # Dériver une clé de 32 bytes depuis la clé fournie
                    kdf = PBKDF2HMAC(
                        algorithm=hashes.SHA256(),
                        length=32,
                        salt=b'smart_ao_v7_salt_',
                        iterations=100000,
                    )
                    encryption_key = kdf.derive(encryption_key)
                
                cls._fernet = Fernet(urlsafe_b64encode(encryption_key))
                logger.info("Chiffrement Fernet initialisé pour les enveloppes FINANCIERE")
                
            except Exception as e:
                logger.error(f"Échec de l'initialisation du chiffrement: {e}")
                cls._fernet = None
        
        return cls._fernet
    
    @classmethod
    def encrypt_file(cls, file_path: Path, output_path: Optional[Path] = None) -> Optional[Path]:
        """Chiffre un fichier avec Fernet."""
        fernet = cls.get_fernet()
        if fernet is None:
            logger.warning("Chiffrement non disponible, fichier non chiffré")
            return file_path
        
        try:
            output_path = output_path or file_path
            encrypted_data = fernet.encrypt(file_path.read_bytes())
            output_path.write_bytes(encrypted_data)
            return output_path
        except Exception as e:
            logger.error(f"Échec du chiffrement de {file_path}: {e}")
            return None
    
    @classmethod
    def decrypt_file(cls, file_path: Path, output_path: Optional[Path] = None) -> Optional[Path]:
        """Déchiffre un fichier avec Fernet."""
        fernet = cls.get_fernet()
        if fernet is None:
            logger.warning("Chiffrement non disponible, fichier non déchiffré")
            return file_path
        
        try:
            output_path = output_path or file_path
            decrypted_data = fernet.decrypt(file_path.read_bytes())
            output_path.write_bytes(decrypted_data)
            return output_path
        except Exception as e:
            logger.error(f"Échec du déchiffrement de {file_path}: {e}")
            return None
    
    @classmethod
    def is_encryption_enabled(cls) -> bool:
        """Vérifie si le chiffrement est activé."""
        return settings.STORAGE_ENCRYPTION_ENABLED and cls.get_fernet() is not None


# =============================================================================
# CONSTANTES - TYPES DE DOCUMENTS PAR ENVELOPPE
# =============================================================================

class EnveloppeType(str, Enum):
    """Les 3 enveloppes canoniques du BTP français."""
    CANDIDATURE = "CANDIDATURE"
    TECHNIQUE = "TECHNIQUE"
    FINANCIERE = "FINANCIERE"


class VaultDocumentType(str, Enum):
    """
    Les 12 documents core du Vault (A01-A12) - SSoT pour les documents juridiques.
    Source: RAPPORT_V102 §142-162
    
    Règles:
    - A01-A06 (juridiques) : bloquants
    - A07-A10 (qualification/technique) : bloquants pour marchés publics > 100k€
    - A11-A12 (candidature) : générés par l'outil, stockés pour versionnage
    """
    # Juridiques - bloquants (A01-A06)
    A01_KBIS = "A01_KBIS"
    A02_ATTESTATION_FISCALE = "A02_ATTESTATION_FISCALE"
    A03_ATTESTATION_SOCIALE_URSSAF = "A03_ATTESTATION_SOCIALE_URSSAF"
    A04_ASSURANCE_RC_PRO = "A04_ASSURANCE_RC_PRO"
    A05_ASSURANCE_DECENNALE = "A05_ASSURANCE_DECENNALE"
    A06_RIB = "A06_RIB"
    
    # Qualification/Technique - bloquants > 100k€ (A07-A10)
    A07_CERTIFICAT_QUALIBAT = "A07_CERTIFICAT_QUALIBAT"
    A08_REFERENCES_5_ANS = "A08_REFERENCES_5_ANS"
    A09_DECLARATION_MOYENS_HUMAINS = "A09_DECLARATION_MOYENS_HUMAINS"
    A10_DECLARATION_MOYENS_MATERIELS = "A10_DECLARATION_MOYENS_MATERIELS"
    
    # Candidature - générés par l'outil (A11-A12)
    A11_DC1 = "A11_DC1"
    A12_DC2_DUME = "A12_DC2_DUME"


class DCEPieceType(str, Enum):
    """
    Types de pièces DCE (Dossier de Consultation des Entreprises).
    Classés par enveloppe cible.
    Source: RAPPORT_V102 §181-225 + Analyse DCE réels
    """
    # ENVELOPPE CANDIDATURE
    RC = "RC"
    CCAP = "CCAP"
    DC1 = "DC1"
    DC2 = "DC2"
    DC4 = "DC4"
    ATTESTATION = "ATTESTATION"
    ASSURANCE = "ASSURANCE"
    
    # ENVELOPPE TECHNIQUE
    CCTP = "CCTP"
    DPGF = "DPGF"
    BPU = "BPU"
    PLANS = "PLANS"
    BIM = "BIM"
    DIAGNOSTICS = "DIAGNOSTICS"
    RAPPORT_GEO = "RAPPORT_GEO"
    DOE = "DOE"
    PAQ = "PAQ"
    MEMOIRE_TECHNIQUE = "MEMOTECH"
    PPSPS = "PPSPS"
    ORGANIGRAMME = "ORGANIGRAMME"
    REFERENCES = "REFERENCES"
    
    # ENVELOPPE FINANCIERE
    CHIFFRAGE = "CHIFFRAGE"
    DEVIS = "DEVIS"
    TRESORERIE = "TRESORERIE"
    BFR = "BFR"
    BILAN = "BILAN"
    PREVISIONNEL = "PREVISIONNEL"
    AE = "AE"
    BT01 = "BT01"
    BT02 = "BT02"
    CAPACITE_FINANCIERE = "CAPACITE_FINANCIERE"
    PENALETE = "PENALETE"
    GARANTIE = "GARANTIE"


# Mapping des types de documents vers les enveloppes
ENVELOPPE_CANDIDATURE_TYPES: Set[str] = {
    VaultDocumentType.A01_KBIS.value,
    VaultDocumentType.A02_ATTESTATION_FISCALE.value,
    VaultDocumentType.A03_ATTESTATION_SOCIALE_URSSAF.value,
    VaultDocumentType.A04_ASSURANCE_RC_PRO.value,
    VaultDocumentType.A05_ASSURANCE_DECENNALE.value,
    VaultDocumentType.A06_RIB.value,
    VaultDocumentType.A07_CERTIFICAT_QUALIBAT.value,
    VaultDocumentType.A08_REFERENCES_5_ANS.value,
    VaultDocumentType.A09_DECLARATION_MOYENS_HUMAINS.value,
    VaultDocumentType.A10_DECLARATION_MOYENS_MATERIELS.value,
    VaultDocumentType.A11_DC1.value,
    VaultDocumentType.A12_DC2_DUME.value,
    DCEPieceType.RC.value,
    DCEPieceType.CCAP.value,
    DCEPieceType.DC1.value,
    DCEPieceType.DC2.value,
    DCEPieceType.DC4.value,
    DCEPieceType.ATTESTATION.value,
    DCEPieceType.ASSURANCE.value,
}

ENVELOPPE_TECHNIQUE_TYPES: Set[str] = {
    DCEPieceType.CCTP.value,
    DCEPieceType.DPGF.value,
    DCEPieceType.BPU.value,
    DCEPieceType.PLANS.value,
    DCEPieceType.BIM.value,
    DCEPieceType.DIAGNOSTICS.value,
    DCEPieceType.RAPPORT_GEO.value,
    DCEPieceType.DOE.value,
    DCEPieceType.PAQ.value,
    DCEPieceType.MEMOIRE_TECHNIQUE.value,
    DCEPieceType.PPSPS.value,
    DCEPieceType.ORGANIGRAMME.value,
    DCEPieceType.REFERENCES.value,
}

ENVELOPPE_FINANCIERE_TYPES: Set[str] = {
    DCEPieceType.CHIFFRAGE.value,
    DCEPieceType.DEVIS.value,
    DCEPieceType.TRESORERIE.value,
    DCEPieceType.BFR.value,
    DCEPieceType.BILAN.value,
    DCEPieceType.PREVISIONNEL.value,
    DCEPieceType.AE.value,
    DCEPieceType.BT01.value,
    DCEPieceType.BT02.value,
    DCEPieceType.CAPACITE_FINANCIERE.value,
    DCEPieceType.PENALETE.value,
    DCEPieceType.GARANTIE.value,
}


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class DocumentMetadata:
    """Métadonnées d'un document pour classification et traçabilité."""
    document_id: str
    file_path: str
    document_type: str
    file_name: str
    page_count: Optional[int] = None
    file_size_bytes: int = 0
    checksum: Optional[str] = None
    extracted_at: Optional[datetime] = None
    vault_code: Optional[str] = None
    is_blocking: bool = False
    is_vault: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "document_id": self.document_id,
            "file_path": self.file_path,
            "document_type": self.document_type,
            "file_name": self.file_name,
            "page_count": self.page_count,
            "file_size_bytes": self.file_size_bytes,
            "checksum": self.checksum,
            "extracted_at": self.extracted_at.isoformat() if self.extracted_at else None,
            "vault_code": self.vault_code,
            "is_blocking": self.is_blocking,
            "is_vault": self.is_vault,
        }


@dataclass
class EnveloppeContent:
    """Contenu d'une enveloppe avant ZIP."""
    enveloppe_type: EnveloppeType
    documents: List[DocumentMetadata] = field(default_factory=list)
    manifest: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        return {
            "enveloppe_type": self.enveloppe_type.value,
            "document_count": len(self.documents),
            "total_size_bytes": sum(d.file_size_bytes for d in self.documents),
            "documents": [d.to_dict() for d in self.documents],
            "manifest": self.manifest,
        }


@dataclass
class SeparationResult:
    """Résultat de la séparation des documents en enveloppes."""
    mission_id: str
    enveloppes: Dict[EnveloppeType, EnveloppeContent] = field(default_factory=dict)
    unclassified: List[DocumentMetadata] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    separation_time_ms: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            "mission_id": self.mission_id,
            "enveloppes": {k.value: v.to_dict() for k, v in self.enveloppes.items()},
            "unclassified_count": len(self.unclassified),
            "warnings": self.warnings,
            "errors": self.errors,
            "separation_time_ms": self.separation_time_ms,
        }


# =============================================================================
# ENVELOPPE SEPARATOR ENGINE
# =============================================================================

class EnveloppeSeparator:
    """
    Engine de séparation des documents en 3 enveloppes canoniques.
    
    Intègre avec:
    - Knowledge Engine (RAG) pour classification intelligente
    - Vault pour les documents core (A01-A12)
    - Workflow Engine pour déclenchement automatique
    
    Règles:
    1. Les documents Vault (A01-A12) vont automatiquement dans CANDIDATURE
    2. Les pièces DCE sont classées selon leur type
    3. Les documents générés (chiffrage, etc.) vont dans FINANCIERE
    4. En cas de doute, utilisation du RAG pour classification
    """
    
    def __init__(self, mission_id: str, storage_path: Optional[str] = None):
        self.mission_id = mission_id
        self.storage_path = Path(storage_path or settings.STORAGE_DATA_DIRECTORY) / "enveloppes" / mission_id
        self._rag_engine: Optional[any] = None
        
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"EnveloppeSeparator initialized for mission {mission_id}")
    
    async def lazy_load_rag(self):
        """Charge le RAG Engine à la demande."""
        if self._rag_engine is None:
            try:
                from app.engines.knowledge_engine.rag_hybrid import RAGHybridEngine
                self._rag_engine = RAGHybridEngine()
                logger.info("RAG Engine loaded for document classification")
            except ImportError as e:
                logger.warning(f"RAG Engine not available: {e}")
                self._rag_engine = None
    
    def _classify_document(self, doc_metadata: DocumentMetadata) -> EnveloppeType:
        """Classifie un document dans l'une des 3 enveloppes."""
        doc_type = doc_metadata.document_type.upper()
        
        if doc_metadata.is_vault or doc_type.startswith("A"):
            return EnveloppeType.CANDIDATURE
        
        if doc_type in ENVELOPPE_CANDIDATURE_TYPES:
            return EnveloppeType.CANDIDATURE
        elif doc_type in ENVELOPPE_TECHNIQUE_TYPES:
            return EnveloppeType.TECHNIQUE
        elif doc_type in ENVELOPPE_FINANCIERE_TYPES:
            return EnveloppeType.FINANCIERE
        
        file_name_upper = doc_metadata.file_name.upper()
        
        if any(keyword in file_name_upper for keyword in ['RC', 'CCAP', 'DC1', 'DC2', 'DC4', 'ATTEST', 'ASSUR', 'KBIS', 'RIB']):
            return EnveloppeType.CANDIDATURE
        elif any(keyword in file_name_upper for keyword in ['CCTP', 'DPGF', 'BPU', 'PLAN', 'BIM', 'DIAG', 'GEO', 'DOE', 'PAQ', 'MEMOTECH', 'PPSPS']):
            return EnveloppeType.TECHNIQUE
        elif any(keyword in file_name_upper for keyword in ['CHIFFRAGE', 'DEVIS', 'TRESOR', 'BFR', 'BILAN', 'PREVIS', 'AE', 'BT01', 'BT02']):
            return EnveloppeType.FINANCIERE
        
        if file_name_upper.endswith(('.PDF', '.DOCX', '.XLSX')):
            return EnveloppeType.TECHNIQUE
        
        return EnveloppeType.CANDIDATURE
    
    async def classify_with_rag(self, doc_metadata: DocumentMetadata) -> EnveloppeType:
        """Utilise le RAG pour classer un document ambigu."""
        await self.lazy_load_rag()
        
        if self._rag_engine is None:
            logger.warning(f"RAG not available, fallback to rule-based classification for {doc_metadata.document_id}")
            return self._classify_document(doc_metadata)
        
        try:
            file_path = Path(doc_metadata.file_path)
            if file_path.exists():
                content = file_path.read_text(encoding='utf-8', errors='ignore')[:1000]
            else:
                content = doc_metadata.file_name
            
            query = f"""Classifie ce document dans l'une des 3 enveloppes : CANDIDATURE, TECHNIQUE, FINANCIERE.
            Contenu: {content}
            Nom: {doc_metadata.file_name}
            Reponds UNIQUEMENT avec: CANDIDATURE, TECHNIQUE ou FINANCIERE"""
            
            rag_response = await self._rag_engine.search(query, top_k=1)
            
            if rag_response.results:
                result_content = rag_response.results[0].content.lower()
                if 'candidature' in result_content:
                    return EnveloppeType.CANDIDATURE
                elif 'technique' in result_content:
                    return EnveloppeType.TECHNIQUE
                elif 'financiere' in result_content or 'financier' in result_content:
                    return EnveloppeType.FINANCIERE
            
            logger.warning(f"RAG classification ambiguous for {doc_metadata.document_id}, fallback to rules")
            return self._classify_document(doc_metadata)
            
        except Exception as e:
            logger.error(f"RAG classification failed for {doc_metadata.document_id}: {e}")
            return self._classify_document(doc_metadata)
    
    def separate_documents(self, documents: List[DocumentMetadata]) -> SeparationResult:
        """Sépare une liste de documents en 3 enveloppes."""
        import time
        start_time = time.time()
        
        result = SeparationResult(mission_id=self.mission_id)
        result.enveloppes = {
            EnveloppeType.CANDIDATURE: EnveloppeContent(enveloppe_type=EnveloppeType.CANDIDATURE),
            EnveloppeType.TECHNIQUE: EnveloppeContent(enveloppe_type=EnveloppeType.TECHNIQUE),
            EnveloppeType.FINANCIERE: EnveloppeContent(enveloppe_type=EnveloppeType.FINANCIERE),
        }
        
        for doc in documents:
            try:
                enveloppe = self._classify_document(doc)
                
                if enveloppe == EnveloppeType.CANDIDATURE and not doc.is_vault:
                    file_name_upper = doc.file_name.upper()
                    if any(keyword in file_name_upper for keyword in ['CCTP', 'DPGF', 'BPU', 'PLAN', 'CHIFFRAGE', 'DEVIS']):
                        import asyncio
                        enveloppe = asyncio.run(self.classify_with_rag(doc))
                
                result.enveloppes[enveloppe].documents.append(doc)
                
            except Exception as e:
                logger.error(f"Failed to classify document {doc.document_id}: {e}")
                result.unclassified.append(doc)
                result.errors.append(f"Document {doc.document_id} ({doc.file_name}): {str(e)}")
        
        for enveloppe_type, content in result.enveloppes.items():
            content.manifest = self._generate_manifest(content)
        
        result.warnings = self._validate_separation(result)
        result.separation_time_ms = (time.time() - start_time) * 1000
        
        logger.info(f"Separation completed for mission {self.mission_id}: "
                   f"CANDIDATURE={len(result.enveloppes[EnveloppeType.CANDIDATURE].documents)}, "
                   f"TECHNIQUE={len(result.enveloppes[EnveloppeType.TECHNIQUE].documents)}, "
                   f"FINANCIERE={len(result.enveloppes[EnveloppeType.FINANCIERE].documents)}")
        
        return result
    
    def _generate_manifest(self, content: EnveloppeContent) -> Dict:
        """Genere un manifest.json pour une enveloppe."""
        import hashlib
        
        manifest = {
            "metadata": {
                "enveloppe_type": content.enveloppe_type.value,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "document_count": len(content.documents),
                "total_size_bytes": sum(d.file_size_bytes for d in content.documents),
                "total_pages": sum(d.page_count or 0 for d in content.documents),
            },
            "documents": [
                {
                    "id": doc.document_id,
                    "file_name": doc.file_name,
                    "type": doc.document_type,
                    "vault_code": doc.vault_code,
                    "is_blocking": doc.is_blocking,
                    "page_count": doc.page_count,
                    "size_bytes": doc.file_size_bytes,
                }
                for doc in content.documents
            ],
            "classification": {
                "method": "rule_based_with_rag_fallback",
                "rules_version": "V7.1",
            },
            "integrity": {
                "checksum": hashlib.sha256(
                    "".join(f"{d.document_id}:{d.file_size_bytes}" for d in content.documents).encode()
                ).hexdigest()[:16]
            }
        }
        
        if content.enveloppe_type == EnveloppeType.CANDIDATURE:
            manifest["requirements"] = {
                "mandatory_for_submission": True,
                "contains_blocking_documents": any(d.is_blocking for d in content.documents),
                "vault_documents_present": any(d.is_vault for d in content.documents),
            }
        elif content.enveloppe_type == EnveloppeType.TECHNIQUE:
            manifest["requirements"] = {
                "mandatory_for_technical_analysis": True,
                "contains_plans": any(d.document_type == DCEPieceType.PLANS.value for d in content.documents),
                "contains_bim": any(d.document_type == DCEPieceType.BIM.value for d in content.documents),
            }
        elif content.enveloppe_type == EnveloppeType.FINANCIERE:
            manifest["requirements"] = {
                "contains_sensitive_data": True,
                "admin_only": True,
                "contains_exact_values": True,
            }
        
        return manifest
    
    def _validate_separation(self, result: SeparationResult) -> List[str]:
        """Valide la coherence de la separation."""
        warnings = []
        
        vault_docs = [d for d in result.enveloppes[EnveloppeType.CANDIDATURE].documents if d.is_vault]
        if len(vault_docs) < 12:
            warnings.append(f"Vault incomplet: {len(vault_docs)}/12 documents core presents")
        
        for doc in vault_docs:
            if doc.vault_code in ['A01', 'A02', 'A03'] and doc.extracted_at:
                age_days = (datetime.now(timezone.utc) - doc.extracted_at).days
                if age_days > 180:
                    warnings.append(f"Document bloquant expire: {doc.file_name} ({doc.vault_code}) - {age_days} jours")
            elif doc.vault_code in ['A04', 'A05', 'A07'] and doc.extracted_at:
                age_days = (datetime.now(timezone.utc) - doc.extracted_at).days
                if age_days > 365:
                    warnings.append(f"Document bloquant expire: {doc.file_name} ({doc.vault_code}) - {age_days} jours")
        
        return warnings
    
    async def generate_zips(self, separation_result: SeparationResult, output_dir: Optional[Path] = None) -> Dict[EnveloppeType, Path]:
        """Genere les 3 fichiers ZIP a partir du resultat de separation.
        
        Sécurité:
        - L'enveloppe FINANCIERE est chiffrée (RGPD/AI Act)
        - Les enveloppes CANDIDATURE et TECHNIQUE ne sont pas chiffrées
        - Une clé STORAGE_ENCRYPTION_KEY est requise dans .env
        """
        output_dir = Path(output_dir or self.storage_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        manifests_dir = output_dir / "manifests"
        manifests_dir.mkdir(exist_ok=True)
        
        zip_paths = {}
        encryption_enabled = EnvelopeEncryption.is_encryption_enabled()
        
        if encryption_enabled:
            logger.info("Chiffrement activé pour les enveloppes FINANCIERE (RGPD/AI Act)")
        else:
            logger.warning("Chiffrement désactivé: STORAGE_ENCRYPTION_KEY non configuré ou chiffrement désactivé")
        
        for enveloppe_type, content in separation_result.enveloppes.items():
            if not content.documents:
                logger.warning(f"Skipping empty enveloppe: {enveloppe_type.value}")
                continue
            
            zip_path = output_dir / f"enveloppe_{enveloppe_type.value.lower()}_{self.mission_id}.zip"
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for doc in content.documents:
                    file_path = Path(doc.file_path)
                    if file_path.exists():
                        arcname = f"{enveloppe_type.value}/{doc.file_name}"
                        
                        # Chiffrer les fichiers de l'enveloppe FINANCIERE
                        if enveloppe_type == EnveloppeType.FINANCIERE and encryption_enabled:
                            try:
                                # Créer une version chiffrée temporaire
                                temp_encrypted = file_path.with_suffix('.enc')
                                EnvelopeEncryption.encrypt_file(file_path, temp_encrypted)
                                
                                if temp_encrypted.exists():
                                    # Ajouter le fichier chiffré au ZIP
                                    zipf.write(temp_encrypted, arcname + '.enc')
                                    # Nettoyer
                                    temp_encrypted.unlink(missing_ok=True)
                                    logger.debug(f"Fichier chiffré ajouté: {doc.file_name}")
                                else:
                                    logger.warning(f"Échec du chiffrement de {doc.file_name}, ajouté non chiffré")
                                    zipf.write(file_path, arcname)
                            except Exception as e:
                                logger.error(f"Erreur de chiffrement {doc.file_name}: {e}, ajouté non chiffré")
                                zipf.write(file_path, arcname)
                        else:
                            # Pas de chiffrement pour CANDIDATURE et TECHNIQUE
                            zipf.write(file_path, arcname)
                    else:
                        logger.warning(f"File not found: {doc.file_path}")
                
                manifest_content = json.dumps(content.manifest, indent=2, ensure_ascii=False)
                zipf.writestr(f"{enveloppe_type.value}/manifest.json", manifest_content)
            
            manifest_path = manifests_dir / f"{enveloppe_type.value.lower()}_manifest_{self.mission_id}.json"
            manifest_path.write_text(manifest_content, encoding='utf-8')
            zip_paths[enveloppe_type] = zip_path
            
            # Ajouter un marqueur de chiffrement dans le manifest si activé
            if enveloppe_type == EnveloppeType.FINANCIERE and encryption_enabled:
                content.manifest["security"] = {
                    "encrypted": True,
                    "algorithm": "Fernet (AES-128-CBC)",
                    "compliance": ["RGPD", "AI Act"],
                    "admin_only": True,
                    "access_control": "RBAC required",
                }
            else:
                content.manifest["security"] = {
                    "encrypted": False,
                    "compliance": ["RGPD"],
                }
            
            logger.info(f"Generated ZIP: {zip_path} ({len(content.documents)} documents)" + 
                       (" [ENCRYPTED]" if enveloppe_type == EnveloppeType.FINANCIERE and encryption_enabled else ""))
        
        return zip_paths
    
    async def run(self, documents: List[DocumentMetadata]) -> Tuple[SeparationResult, Dict[EnveloppeType, Path]]:
        """Execute la separation complete et genere les ZIP.
        
        Audit logging:
        - Log toutes les actions de séparation pour conformité RGPD/AI Act
        - Journalisation WORM (Write Once Read Many) via EventBus
        """
        import time
        start_time = time.time()
        
        # Log d'audit: Début de la séparation
        audit_logs = []
        audit_logs.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "SEPARATION_STARTED",
            "mission_id": self.mission_id,
            "document_count": len(documents),
            "user": "system",  # À remplir avec le vrai user
        })
        
        # Étape 1: Séparation des documents
        separation_result = self.separate_documents(documents)
        
        # Log d'audit: Classification terminée
        audit_logs.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "CLASSIFICATION_COMPLETED",
            "mission_id": self.mission_id,
            "candidature_count": len(separation_result.enveloppes[EnveloppeType.CANDIDATURE].documents),
            "technique_count": len(separation_result.enveloppes[EnveloppeType.TECHNIQUE].documents),
            "financiere_count": len(separation_result.enveloppes[EnveloppeType.FINANCIERE].documents),
            "unclassified_count": len(separation_result.unclassified),
        })
        
        # Étape 2: Génération des ZIP
        zip_paths = await self.generate_zips(separation_result)
        
        # Log d'audit: Génération des ZIP terminée
        for enveloppe_type, zip_path in zip_paths.items():
            audit_logs.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": "ZIP_GENERATED",
                "mission_id": self.mission_id,
                "enveloppe_type": enveloppe_type.value,
                "zip_path": str(zip_path),
                "encrypted": enveloppe_type == EnveloppeType.FINANCIERE and EnvelopeEncryption.is_encryption_enabled(),
            })
        
        # Log d'audit: Séparation terminée
        total_time = (time.time() - start_time) * 1000
        audit_logs.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "SEPARATION_COMPLETED",
            "mission_id": self.mission_id,
            "total_time_ms": total_time,
            "status": "SUCCESS" if not separation_result.errors else "PARTIAL",
            "warnings_count": len(separation_result.warnings),
            "errors_count": len(separation_result.errors),
        })
        
        # Publier les logs d'audit sur l'EventBus (si disponible)
        try:
            from app.engines.event_bus.bus import EventBus, Event
            from app.core.config import settings
            event_bus = EventBus()
            for log_entry in audit_logs:
                event_bus.publish(Event(
                    "AuditSeparation",
                    mission_id=self.mission_id,
                    payload=log_entry,
                    source="EnveloppeSeparator"
                ))
        except Exception as e:
            logger.debug(f"EventBus non disponible pour l'audit: {e}")
        
        # Log dans le logger standard
        for log_entry in audit_logs:
            logger.info(f"AUDIT: {log_entry['action']} - mission={self.mission_id} - {log_entry.get('enveloppe_type', '')}")
        
        # Gestion des erreurs
        if separation_result.errors:
            logger.error(f"Errors during separation: {separation_result.errors}")
            raise RuntimeError(f"Separation failed with {len(separation_result.errors)} errors")
        
        for warning in separation_result.warnings:
            logger.warning(f"Separation warning: {warning}")
        
        logger.info(f"Enveloppe separation completed for mission {self.mission_id} in {total_time:.2f}ms")
        
        return separation_result, zip_paths
    
    async def get_enveloppe_path(self, enveloppe_type: EnveloppeType) -> Optional[Path]:
        """Recupere le chemin du ZIP d'une enveloppe generee."""
        zip_path = self.storage_path / f"enveloppe_{enveloppe_type.value.lower()}_{self.mission_id}.zip"
        return zip_path if zip_path.exists() else None
    
    def cleanup(self) -> bool:
        """Nettoie les fichiers generes pour cette mission."""
        try:
            if self.storage_path.exists():
                shutil.rmtree(self.storage_path)
                return True
            return True
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return False


def create_document_metadata(
    document_id: str,
    file_path: str,
    document_type: str,
    file_name: Optional[str] = None,
    is_vault: bool = False,
    vault_code: Optional[str] = None,
    is_blocking: bool = False,
    page_count: Optional[int] = None,
) -> DocumentMetadata:
    """Factory pour creer des DocumentMetadata."""
    actual_file_name = file_name or Path(file_path).name
    file_size = Path(file_path).stat().st_size if Path(file_path).exists() else 0
    
    if is_vault or (vault_code and vault_code.startswith('A')):
        is_vault = True
        if vault_code in ['A01', 'A02', 'A03', 'A04', 'A05', 'A06']:
            is_blocking = True
    
    return DocumentMetadata(
        document_id=document_id,
        file_path=file_path,
        document_type=document_type,
        file_name=actual_file_name,
        page_count=page_count,
        file_size_bytes=file_size,
        is_vault=is_vault,
        vault_code=vault_code,
        is_blocking=is_blocking,
    )


def get_enveloppe_separator(mission_id: str) -> EnveloppeSeparator:
    """Factory pour obtenir un EnveloppeSeparator."""
    return EnveloppeSeparator(mission_id)


__all__ = [
    'EnveloppeType',
    'VaultDocumentType',
    'DCEPieceType',
    'ENVELOPPE_CANDIDATURE_TYPES',
    'ENVELOPPE_TECHNIQUE_TYPES',
    'ENVELOPPE_FINANCIERE_TYPES',
    'DocumentMetadata',
    'EnveloppeContent',
    'SeparationResult',
    'EnveloppeSeparator',
    'EnvelopeEncryption',
    'create_document_metadata',
    'get_enveloppe_separator',
]

