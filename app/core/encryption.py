"""
SMART_AO V7 - encryption.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 07/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Encryption Module
===============================
Chiffrement des données sensibles pour la conformité RGPD
Utilise AES-256-GCM pour le chiffrement symétrique
"""

import base64
import hashlib
from typing import Optional, Union, bytes, str
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.core.config import settings


# =============================================================================
# CONFIGURATION
# =============================================================================

class EncryptionConfig:
    """Configuration du chiffrement AES-256-GCM."""
    
    # Taille de la clé (256 bits = 32 octets pour AES-256)
    KEY_SIZE: int = 32
    
    # Taille du sel (16 octets recommandé pour PBKDF2)
    SALT_SIZE: int = 16
    
    # Nombre d'itérations PBKDF2 (OWASP recommande minimum 600,000)
    ITERATIONS: int = 600000
    
    # Algorithme de hachage pour PBKDF2
    HASH_ALGORITHM = hashes.SHA256()
    
    # Longueur du nonce pour AES-GCM (12 octets recommandé)
    NONCE_SIZE: int = 12


config = EncryptionConfig()


# =============================================================================
# CLÉ DE CHIFFREMENT
# =============================================================================

class EncryptionKeyManager:
    """Gestionnaire de clé de chiffrement."""
    
    _key: Optional[bytes] = None
    
    @classmethod
    def get_key(cls) -> bytes:
        """Récupérer ou générer la clé de chiffrement."""
        if cls._key is None:
            # Vérifier si la clé est fournie dans les settings
            if settings.STORAGE_ENCRYPTION_KEY:
                # Dériver une clé de 32 octets à partir de la clé fournie
                cls._key = cls._derive_key(settings.STORAGE_ENCRYPTION_KEY)
            else:
                # En développement/test : générer une clé temporaire
                # ⚠️ NE PAS UTILISER EN PRODUCTION
                import secrets
                cls._key = secrets.token_bytes(config.KEY_SIZE)
        
        return cls._key
    
    @classmethod
    def _derive_key(cls, password: str) -> bytes:
        """Dériver une clé à partir d'un mot de passe."""
        # Générer un sel fixe déterministe à partir de l'environnement
        # (en production, utiliser un sel stocké dans un fichier sécurisé)
        salt = hashlib.sha256(settings.JWT_SECRET_KEY.encode()).digest()[:config.SALT_SIZE] if settings.JWT_SECRET_KEY else b"default_salt_123456"
        
        kdf = PBKDF2HMAC(
            algorithm=config.HASH_ALGORITHM,
            length=config.KEY_SIZE,
            salt=salt,
            iterations=config.ITERATIONS,
            backend=default_backend()
        )
        return kdf.derive(password.encode())
    
    @classmethod
    def rotate_key(cls):
        """Changer la clé de chiffrement (pour rotation des clés)."""
        cls._key = None


# =============================================================================
# FONCTIONS DE CHIFFREMENT
# =============================================================================

def encrypt_data(plaintext: Union[str, bytes]) -> str:
    """
    Chiffrer des données avec AES-256-GCM.
    
    Args:
        plaintext: Données à chiffrer (str ou bytes)
        
    Returns:
        str: Données chiffrées encodées en base64 (format: nonce:ciphertext:tag)
    """
    if not settings.STORAGE_ENCRYPTION_ENABLED:
        # Si le chiffrement est désactivé, retourner les données en clair
        if isinstance(plaintext, str):
            return plaintext
        return base64.b64encode(plaintext).decode('utf-8')
    
    key = EncryptionKeyManager.get_key()
    aesgcm = AESGCM(key)
    
    # Convertir en bytes si nécessaire
    if isinstance(plaintext, str):
        plaintext_bytes = plaintext.encode('utf-8')
    else:
        plaintext_bytes = plaintext
    
    # Générer un nonce aléatoire
    nonce = secrets.token_bytes(config.NONCE_SIZE)
    
    # Chiffrer
    ciphertext = aesgcm.encrypt(nonce, plaintext_bytes, None)
    
    # Combiner nonce + ciphertext (le tag est inclus dans ciphertext pour GCM)
    combined = nonce + ciphertext
    
    # Encoder en base64 pour stockage
    return base64.b64encode(combined).decode('utf-8')


def decrypt_data(encrypted_data: str) -> Union[str, bytes]:
    """
    Déchiffrer des données chiffrées avec AES-256-GCM.
    
    Args:
        encrypted_data: Données chiffrées encodées en base64
        
    Returns:
        Union[str, bytes]: Données déchiffrées (str si possible, bytes sinon)
    
    Raises:
        ValueError: Si le déchiffrement échoue
    """
    if not settings.STORAGE_ENCRYPTION_ENABLED:
        # Si le chiffrement est désactivé, retourner les données en clair
        try:
            return base64.b64decode(encrypted_data).decode('utf-8')
        except (UnicodeDecodeError, base64.binascii.Error):
            return encrypted_data
    
    key = EncryptionKeyManager.get_key()
    aesgcm = AESGCM(key)
    
    # Décoder de base64
    try:
        combined = base64.b64decode(encrypted_data)
    except (base64.binascii.Error, UnicodeDecodeError) as e:
        raise ValueError(f"Données chiffrées invalides: {e}")
    
    # Extraire nonce et ciphertext
    nonce = combined[:config.NONCE_SIZE]
    ciphertext = combined[config.NONCE_SIZE:]
    
    # Déchiffrer
    try:
        plaintext_bytes = aesgcm.decrypt(nonce, ciphertext, None)
        
        # Essayer de décoder en UTF-8
        try:
            return plaintext_bytes.decode('utf-8')
        except UnicodeDecodeError:
            return plaintext_bytes
    except Exception as e:
        raise ValueError(f"Échec du déchiffrement: {e}")


# =============================================================================
# UTILITAIRES POUR LES CHAMPS SENSIBLES
# =============================================================================

def encrypt_field(value: Optional[Union[str, bytes, int, float]]) -> Optional[str]:
    """
    Chiffrer un champ sensible.
    
    Args:
        value: Valeur à chiffrer
        
    Returns:
        Optional[str]: Valeur chiffrée ou None
    """
    if value is None:
        return None
    
    return encrypt_data(str(value))


def decrypt_field(encrypted_value: Optional[str]) -> Optional[Union[str, int, float]]:
    """
    Déchiffrer un champ sensible.
    
    Args:
        encrypted_value: Valeur chiffrée
        
    Returns:
        Optional[Union[str, int, float]]: Valeur déchiffrée ou None
    """
    if encrypted_value is None:
        return None
    
    decrypted = decrypt_data(encrypted_value)
    
    # Essayer de convertir en int ou float
    if isinstance(decrypted, str):
        try:
            return int(decrypted)
        except ValueError:
            try:
                return float(decrypted)
            except ValueError:
                return decrypted
    
    return decrypted


# =============================================================================
# IMPORT POUR SECRETS
# =============================================================================

try:
    import secrets
except ImportError:
    # Fallback pour les anciennes versions de Python
    import os
    secrets = os
