"""
SMART_AO V7 - filesystem.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - Filesystem Security
===================================
Validation et sécurité des fichiers uploadés
Source: ARCHITECTURE_V7_ENGINE.md §4.2
"""

import os
from pathlib import Path
from typing import Optional, Tuple, BinaryIO
from fastapi import UploadFile

from app.core.config import settings

# Essayer d'importer magic, sinon utiliser fallback
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False


# =============================================================================
# VALIDATION DES FICHIERS
# =============================================================================

def get_file_extension(file_name: str) -> str:
    """
    Extraire l'extension d'un fichier
    
    Args:
        file_name: Nom du fichier
    
    Returns:
        str: Extension (ex: .pdf, .docx)
    """
    return os.path.splitext(file_name)[1].lower()


def validate_file_extension(file_name: str) -> Tuple[bool, str]:
    """
    Valider l'extension d'un fichier
    
    Args:
        file_name: Nom du fichier
    
    Returns:
        Tuple[bool, str]: (valide, message)
    """
    allowed_extensions = [ext.lower() for ext in settings.UPLOAD_ALLOWED_EXTENSIONS.split(",")]
    file_extension = get_file_extension(file_name)
    
    if file_extension not in allowed_extensions:
        return False, f"Extension '{file_extension}' non autorisée. Extensions autorisées: {', '.join(allowed_extensions)}"
    
    return True, "Extension valide"


def validate_file_size(file_size: int) -> Tuple[bool, str]:
    """
    Valider la taille d'un fichier
    
    Args:
        file_size: Taille en octets
    
    Returns:
        Tuple[bool, str]: (valide, message)
    """
    max_size = settings.UPLOAD_MAX_SIZE_MB * 1024 * 1024
    
    if file_size > max_size:
        return False, f"Fichier trop volumineux: {file_size / (1024*1024):.2f}MB. Maximum: {settings.UPLOAD_MAX_SIZE_MB}MB"
    
    return True, "Taille valide"


def validate_file_type(file_content: bytes, file_name: str) -> Tuple[bool, str]:
    """
    Valider le type MIME d'un fichier
    
    Args:
        file_content: Contenu binaire du fichier
        file_name: Nom du fichier
    
    Returns:
        Tuple[bool, str]: (valide, message)
    """
    try:
        # Utiliser python-magic pour détecter le type MIME réel (si disponible)
        if not HAS_MAGIC:
            # Si magic n'est pas installé, on fait confiance à l'extension
            return True, "Vérification du type MIME désactivée (magic non installé)"
        
        mime = magic.from_buffer(file_content, mime=True)
        
        # Mapper les extensions aux types MIME attendus
        allowed_mimes = {
            '.pdf': ['application/pdf'],
            '.docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
            '.doc': ['application/msword'],
            '.xlsx': ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],
            '.xls': ['application/vnd.ms-excel'],
            '.txt': ['text/plain'],
            '.json': ['application/json']
        }
        
        file_extension = get_file_extension(file_name)
        expected_mimes = allowed_mimes.get(file_extension, [])
        
        if expected_mimes and mime not in expected_mimes:
            return False, f"Type MIME invalide: {mime}. Attendu: {', '.join(expected_mimes)}"
        
        return True, f"Type MIME valide: {mime}"
    
    except Exception as e:
        return False, f"Erreur lors de la vérification du type MIME: {e}"


def validate_file_content(file_content: bytes, file_name: str) -> Tuple[bool, str]:
    """
    Valider le contenu d'un fichier (détection de contenu malveillant)
    
    Args:
        file_content: Contenu binaire du fichier
        file_name: Nom du fichier
    
    Returns:
        Tuple[bool, str]: (valide, message)
    """
    # Détection de patterns suspects dans le contenu texte
    suspicious_patterns = [
        b'<?php', b'<?=', b'<% ', b'<%=', b'{{ ', b'{{{',
        b'<script', b'javascript:', b'onerror=', b'onload=',
        b'eval(', b'exec(', b'system(', b'os.system',
        b'subprocess.', b'__import__', b'base64_decode'
    ]
    
    try:
        # Convertir en texte si possible
        try:
            text_content = file_content.decode('utf-8', errors='ignore')
        except:
            text_content = ""
        
        for pattern in suspicious_patterns:
            if pattern in file_content or pattern.decode('utf-8', errors='ignore') in text_content:
                return False, f"Contenu suspect détecté: pattern {pattern}"
    
    except Exception as e:
        return False, f"Erreur lors de la vérification du contenu: {e}"
    
    return True, "Contenu valide"


# =============================================================================
# VALIDATION COMPLÈTE
# =============================================================================

async def validate_upload_file(
    file: UploadFile,
    document_type: Optional[str] = None
) -> Tuple[bool, str, Optional[dict]]:
    """
    Valider complètement un fichier uploadé
    
    Args:
        file: Fichier FastAPI UploadFile
        document_type: Type de document déclaré
    
    Returns:
        Tuple[bool, str, Optional[dict]]: (valide, message, métadonnées)
    """
    # Lire le contenu
    file_content = await file.read()
    file.seek(0)
    
    file_size = len(file_content)
    file_name = file.filename
    
    # 1. Valider l'extension
    ext_valid, ext_msg = validate_file_extension(file_name)
    if not ext_valid:
        return False, ext_msg, None
    
    # 2. Valider la taille
    size_valid, size_msg = validate_file_size(file_size)
    if not size_valid:
        return False, size_msg, None
    
    # 3. Valider le type MIME
    type_valid, type_msg = validate_file_type(file_content, file_name)
    if not type_valid:
        return False, type_msg, None
    
    # 4. Valider le contenu
    content_valid, content_msg = validate_file_content(file_content, file_name)
    if not content_valid:
        return False, content_msg, None
    
    # Si tout est valide, retourner les métadonnées
    metadata = {
        "file_name": file_name,
        "file_size": file_size,
        "file_extension": get_file_extension(file_name),
        "content_type": file.content_type,
        "content_hash": None  # Sera calculé lors de l'upload
    }
    
    return True, "Fichier valide", metadata


def validate_file(file_content: bytes, file_name: str) -> Tuple[bool, str]:
    """
    Fonction de validation complète pour les fichiers (sans async)
    
    Args:
        file_content: Contenu binaire
        file_name: Nom du fichier
    
    Returns:
        Tuple[bool, str]: (valide, message)
    """
    file_size = len(file_content)
    
    # 1. Extension
    ext_valid, ext_msg = validate_file_extension(file_name)
    if not ext_valid:
        return False, ext_msg
    
    # 2. Taille
    size_valid, size_msg = validate_file_size(file_size)
    if not size_valid:
        return False, size_msg
    
    # 3. Type MIME
    type_valid, type_msg = validate_file_type(file_content, file_name)
    if not type_valid:
        return False, type_msg
    
    # 4. Contenu
    content_valid, content_msg = validate_file_content(file_content, file_name)
    if not content_valid:
        return False, content_msg
    
    return True, "Fichier valide"
