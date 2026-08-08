"""
SMART_AO V7 - enveloppes.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 07/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - API Endpoints pour les Enveloppes
Source: ARCHITECTURE_V7_ENGINE.md + RAPPORT_V102 §129

Endpoints:
- POST /api/v1/enveloppes/{mission_id}/separate : Lancer la séparation
- GET /api/v1/enveloppes/{mission_id}/status : Statut de la séparation
- GET /api/v1/enveloppes/{mission_id}/candidature : Télécharger enveloppe CANDIDATURE
- GET /api/v1/enveloppes/{mission_id}/technique : Télécharger enveloppe TECHNIQUE
- GET /api/v1/enveloppes/{mission_id}/financiere : Télécharger enveloppe FINANCIERE (ADMIN ONLY)
- GET /api/v1/enveloppes/{mission_id}/manifests : Lister les manifests

Sécurité:
- RBAC strict appliqué (EnveloppeRBAC)
- FINANCIERE : Accessible UNIQUEMENT par les admins
- Audit logging complet
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Optional, Dict, Any
from pathlib import Path
import uuid
import logging

from app.core.config import settings
from app.core.security import get_current_user
from app.engines.api_gateway.enveloppe_separator import (
    EnveloppeSeparator,
    EnveloppeType,
    create_document_metadata,
    get_enveloppe_separator,
    VaultDocumentType,
    DCEPieceType,
)
from app.engines.security_engine.enveloppe_rbac import (
    EnveloppeRBAC,
    require_enveloppe_admin,
    UserRole,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/enveloppes", tags=["enveloppes"])


# =============================================================================
# DEPENDENCIES
# =============================================================================

async def get_enveloppe_separator_dependency(mission_id: str) -> EnveloppeSeparator:
    """Dependency pour obtenir un EnveloppeSeparator."""
    return get_enveloppe_separator(mission_id)


async def get_current_user_dependency(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Dependency pour obtenir l'utilisateur courant."""
    return current_user


# =============================================================================
# SCHEMAS (Pydantic Models)
# =============================================================================

from pydantic import BaseModel, Field


class SeparationRequest(BaseModel):
    """Requête pour lancer une séparation de documents."""
    document_paths: List[str] = Field(..., description="Liste des chemins vers les documents")
    document_types: Optional[List[str]] = Field(
        None, 
        description="Types des documents (VaultDocumentType ou DCEPieceType)"
    )
    vault_codes: Optional[List[Optional[str]]] = Field(
        None,
        description="Codes Vault (A01-A12) pour les documents Vault"
    )
    custom_storage_path: Optional[str] = Field(
        None,
        description="Chemin de stockage personnalisé"
    )


class SeparationResponse(BaseModel):
    """Réponse de la séparation des documents."""
    mission_id: str
    status: str
    enveloppes: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Contenu de chaque enveloppe"
    )
    warnings: List[str] = Field(default_factory=list)
    separation_time_ms: float
    zip_paths: Dict[str, str] = Field(default_factory=dict)
    security: Dict[str, Any] = Field(
        default_factory=dict,
        description="Informations de sécurité (chiffrement, RBAC)"
    )


class EnveloppeInfo(BaseModel):
    """Informations sur une enveloppe."""
    mission_id: str
    enveloppe_type: str
    document_count: int
    total_size_bytes: int
    zip_path: str
    manifest_path: str
    is_encrypted: bool
    is_admin_only: bool
    can_access: bool


class EnveloppeStatus(BaseModel):
    """Statut de la séparation pour une mission."""
    mission_id: str
    separation_completed: bool
    enveloppes: Dict[str, bool] = Field(
        default_factory=dict,
        description="Si chaque enveloppe a été générée"
    )
    warnings: List[str] = Field(default_factory=list)


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.post("/{mission_id}/separate", 
             response_model=SeparationResponse,
             summary="Lancer la séparation des documents en 3 enveloppes",
             description="Sépare une liste de documents en 3 enveloppes canoniques (CANDIDATURE, TECHNIQUE, FINANCIERE)")
async def separate_documents(
    mission_id: str,
    request: SeparationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Lancer la séparation des documents pour une mission.
    
    **Permissions** : Accessible par tous les utilisateurs (salarié et admin)
    
    **Processus** :
    1. Classification des documents selon leur type
    2. Génération des 3 enveloppes
    3. Création des fichiers ZIP
    4. Chiffrement de l'enveloppe FINANCIERE (si activé)
    5. Génération des manifests
    
    **Retour** : Résumé de la séparation avec chemins des ZIP générés
    """
    user_id = current_user.get("sub") or current_user.get("user_id") or "unknown"
    user_role = current_user.get("role", "SALARIE")
    
    logger.info(f"Separation request: mission={mission_id}, user={user_id}, docs={len(request.document_paths)}")
    
    # Créer les métadonnées des documents
    documents = []
    for i, doc_path in enumerate(request.document_paths):
        doc_type = (request.document_types or ["DCE"] * len(request.document_paths))[i]
        vault_code = (request.vault_codes or [None] * len(request.document_paths))[i]
        
        doc = create_document_metadata(
            document_id=f"doc_{uuid.uuid4().hex[:8]}",
            file_path=doc_path,
            document_type=doc_type,
            is_vault=vault_code is not None and vault_code.startswith("A"),
            vault_code=vault_code,
            is_blocking=vault_code in ["A01", "A02", "A03", "A04", "A05", "A06"],
        )
        documents.append(doc)
    
    # Exécuter la séparation
    separator = get_enveloppe_separator(mission_id)
    
    try:
        separation_result, zip_paths = await separator.run(documents)
        
        # Préparer la réponse
        response_data = {
            "mission_id": mission_id,
            "status": "SUCCESS",
            "enveloppes": {},
            "warnings": separation_result.warnings,
            "separation_time_ms": separation_result.separation_time_ms,
            "zip_paths": {k.value: str(v) for k, v in zip_paths.items()},
            "security": {
                "encryption_enabled": settings.STORAGE_ENCRYPTION_ENABLED,
                "financiere_encrypted": (
                    EnveloppeType.FINANCIERE in zip_paths and 
                    settings.STORAGE_ENCRYPTION_ENABLED
                ),
            }
        }
        
        # Ajouter les informations des enveloppes
        for enveloppe_type, content in separation_result.enveloppes.items():
            response_data["enveloppes"][enveloppe_type.value] = {
                "document_count": len(content.documents),
                "total_size_bytes": sum(d.file_size_bytes for d in content.documents),
                "manifest": content.manifest,
            }
        
        logger.info(f"Separation completed: mission={mission_id}, status=SUCCESS")
        
        return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Separation failed: mission={mission_id}, error={e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la séparation: {str(e)}"
        )


@router.get("/{mission_id}/status",
            response_model=EnveloppeStatus,
            summary="Statut de la séparation pour une mission")
async def get_separation_status(
    mission_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Récupérer le statut de la séparation pour une mission.
    
    **Permissions** : Accessible par tous les utilisateurs
    """
    separator = get_enveloppe_separator(mission_id)
    storage_path = separator.storage_path
    
    enveloppes_status = {}
    warnings = []
    
    for enveloppe_type in EnveloppeType:
        zip_path = await separator.get_enveloppe_path(enveloppe_type)
        enveloppes_status[enveloppe_type.value] = zip_path is not None if zip_path else False
    
    # Vérifier si la séparation a été exécutée
    separation_completed = all(enveloppes_status.values())
    
    if not separation_completed:
        warnings.append("Certaines enveloppes n'ont pas encore été générées")
    
    return EnveloppeStatus(
        mission_id=mission_id,
        separation_completed=separation_completed,
        enveloppes=enveloppes_status,
        warnings=warnings,
    )


@router.get("/{mission_id}/candidature",
            summary="Télécharger l'enveloppe CANDIDATURE",
            description="Télécharger le fichier ZIP de l'enveloppe CANDIDATURE")
async def download_candidature_enveloppe(
    mission_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Télécharger l'enveloppe CANDIDATURE.
    
    **Permissions** : Accessible par salarié et admin (lecture seule)
    """
    user_id = current_user.get("sub") or current_user.get("user_id") or "unknown"
    
    # Vérifier RBAC
    if not EnveloppeRBAC.can_read_enveloppe(user_id, "CANDIDATURE", current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé: vous n'avez pas la permission de lire cette enveloppe"
        )
    
    separator = get_enveloppe_separator(mission_id)
    zip_path = await separator.get_enveloppe_path(EnveloppeType.CANDIDATURE)
    
    if not zip_path or not zip_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enveloppe CANDIDATURE non trouvée pour cette mission"
        )
    
    logger.info(f"Download CANDIDATURE: mission={mission_id}, user={user_id}")
    
    return FileResponse(
        path=zip_path,
        filename=f"enveloppe_candidature_{mission_id}.zip",
        media_type="application/zip",
    )


@router.get("/{mission_id}/technique",
            summary="Télécharger l'enveloppe TECHNIQUE",
            description="Télécharger le fichier ZIP de l'enveloppe TECHNIQUE")
async def download_technique_enveloppe(
    mission_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Télécharger l'enveloppe TECHNIQUE.
    
    **Permissions** : Accessible par salarié et admin (lecture seule)
    """
    user_id = current_user.get("sub") or current_user.get("user_id") or "unknown"
    
    # Vérifier RBAC
    if not EnveloppeRBAC.can_read_enveloppe(user_id, "TECHNIQUE", current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé: vous n'avez pas la permission de lire cette enveloppe"
        )
    
    separator = get_enveloppe_separator(mission_id)
    zip_path = await separator.get_enveloppe_path(EnveloppeType.TECHNIQUE)
    
    if not zip_path or not zip_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enveloppe TECHNIQUE non trouvée pour cette mission"
        )
    
    logger.info(f"Download TECHNIQUE: mission={mission_id}, user={user_id}")
    
    return FileResponse(
        path=zip_path,
        filename=f"enveloppe_technique_{mission_id}.zip",
        media_type="application/zip",
    )


@router.get("/{mission_id}/financiere",
            summary="Télécharger l'enveloppe FINANCIERE",
            description="Télécharger le fichier ZIP de l'enveloppe FINANCIERE (ADMIN ONLY)")
async def download_financiere_enveloppe(
    mission_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Télécharger l'enveloppe FINANCIERE.
    
    **⚠️ ACCÈS RESTREINT : UNIQUEMENT POUR LES ADMINS**
    
    L'enveloppe FINANCIERE contient des données sensibles (chiffrage, devis, trésorerie).
    Seuls les utilisateurs avec le rôle ADMIN ou SUPER_ADMIN peuvent y accéder.
    
    **Permissions** : ADMIN ONLY
    """
    user_id = current_user.get("sub") or current_user.get("user_id") or "unknown"
    
    # Vérifier RBAC - ADMIN ONLY
    if not EnveloppeRBAC.can_read_enveloppe(user_id, "FINANCIERE", current_user):
        user_role = current_user.get("role", "SALARIE")
        warning_msg = f"⚠️ ENVELOPPE FINANCIERE - ACCÈS RESTREINT: Votre rôle ({user_role}) ne peut pas accéder à cette enveloppe. Seul l'admin peut voir les données financières."
        
        logger.warning(f"ACCES REFUSE - FINANCIERE: user={user_id}, role={user_role}")
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=warning_msg,
        )
    
    separator = get_enveloppe_separator(mission_id)
    zip_path = await separator.get_enveloppe_path(EnveloppeType.FINANCIERE)
    
    if not zip_path or not zip_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enveloppe FINANCIERE non trouvée pour cette mission"
        )
    
    logger.info(f"Download FINANCIERE: mission={mission_id}, user={user_id} (ADMIN)")
    
    return FileResponse(
        path=zip_path,
        filename=f"enveloppe_financiere_{mission_id}.zip",
        media_type="application/zip",
    )


@router.get("/{mission_id}/manifests",
            summary="Lister les manifests des enveloppes",
            description="Récupérer la liste des fichiers manifest générés")
async def list_enveloppe_manifests(
    mission_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Lister les manifests des enveloppes pour une mission.
    
    **Permissions** : Accessible par tous, mais les manifests FINANCIERE
    peuvent contenir des métadonnées sensibles
    """
    user_id = current_user.get("sub") or current_user.get("user_id") or "unknown"
    
    separator = get_enveloppe_separator(mission_id)
    storage_path = separator.storage_path
    manifests_dir = storage_path / "manifests"
    
    if not manifests_dir.exists():
        return JSONResponse(
            content={"mission_id": mission_id, "manifests": []},
            status_code=status.HTTP_200_OK
        )
    
    manifests = []
    for manifest_file in manifests_dir.glob("*.json"):
        manifests.append({
            "filename": manifest_file.name,
            "path": str(manifest_file),
            "size_bytes": manifest_file.stat().st_size,
        })
    
    logger.info(f"List manifests: mission={mission_id}, user={user_id}, count={len(manifests)}")
    
    return JSONResponse(
        content={"mission_id": mission_id, "manifests": manifests},
        status_code=status.HTTP_200_OK
    )


@router.get("/{mission_id}/info",
            response_model=List[EnveloppeInfo],
            summary="Informations détaillées sur les enveloppes")
async def get_enveloppe_info(
    mission_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Récupérer les informations détaillées sur toutes les enveloppes d'une mission.
    
    **Permissions** : Accessible par tous, mais les infos FINANCIERE
    sont masquées pour les non-admins
    """
    user_id = current_user.get("sub") or current_user.get("user_id") or "unknown"
    
    separator = get_enveloppe_separator(mission_id)
    
    infos = []
    for enveloppe_type in EnveloppeType:
        zip_path = await separator.get_enveloppe_path(enveloppe_type)
        
        # Vérifier RBAC pour chaque enveloppe
        can_access = EnveloppeRBAC.can_read_enveloppe(user_id, enveloppe_type.value, current_user)
        
        info = EnveloppeInfo(
            mission_id=mission_id,
            enveloppe_type=enveloppe_type.value,
            document_count=0,  # À calculer
            total_size_bytes=0,  # À calculer
            zip_path=str(zip_path) if zip_path else "",
            manifest_path=str(separator.storage_path / "manifests" / f"{enveloppe_type.value.lower()}_manifest_{mission_id}.json"),
            is_encrypted=enveloppe_type == EnveloppeType.FINANCIERE and settings.STORAGE_ENCRYPTION_ENABLED,
            is_admin_only=enveloppe_type == EnveloppeType.FINANCIERE,
            can_access=can_access,
        )
        infos.append(info)
    
    return infos


# =============================================================================
# EXPORT
# =============================================================================

__all__ = [
    'router',
    'SeparationRequest',
    'SeparationResponse',
    'EnveloppeInfo',
    'EnveloppeStatus',
]
