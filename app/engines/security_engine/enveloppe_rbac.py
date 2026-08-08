"""
SMART_AO V7 - enveloppe_rbac.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 07/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - RBAC pour les Enveloppes
Source: RAPPORT_V102 §136 + ARCHITECTURE_V7_ENGINE.md

Règles RBAC strictes pour les 3 enveloppes:
- CANDIDATURE : Accessible par salarié et admin (lecture seule pour salarié)
- TECHNIQUE : Accessible par salarié et admin (lecture seule pour salarié)
- FINANCIERE : **UNIQUEMENT admin** (lecture/écriture)

Principe : Le salarié ne voit pas les euros. L'admin voit TOUT.
"""

import logging
from enum import Enum
from typing import Optional, Dict, Any
from functools import wraps

from app.core.config import settings

logger = logging.getLogger(__name__)


# =============================================================================
# ROLES
# =============================================================================

class UserRole(str, Enum):
    """Rôles utilisateur dans SMART_AO."""
    SALARIE = "SALARIE"      # Opérateur guidé
    ADMIN = "ADMIN"          # Contrôle total
    SUPER_ADMIN = "SUPER_ADMIN"  # Accès complet + configuration


# =============================================================================
# PERMISSIONS
# =============================================================================

class EnveloppePermission(str, Enum):
    """Permissions sur les enveloppes."""
    READ = "READ"
    WRITE = "WRITE"
    DELETE = "DELETE"
    EXPORT = "EXPORT"
    DECRYPT = "DECRYPT"  # Pour déchiffrer les enveloppes FINANCIERE


# =============================================================================
# RBAC RULES
# =============================================================================

# Matrice de permissions : enveloppe -> role -> permissions
RBAC_MATRIX: Dict[str, Dict[UserRole, list]] = {
    "CANDIDATURE": {
        UserRole.SALARIE: [EnveloppePermission.READ],
        UserRole.ADMIN: [EnveloppePermission.READ, EnveloppePermission.WRITE, EnveloppePermission.EXPORT],
        UserRole.SUPER_ADMIN: [EnveloppePermission.READ, EnveloppePermission.WRITE, EnveloppePermission.DELETE, EnveloppePermission.EXPORT],
    },
    "TECHNIQUE": {
        UserRole.SALARIE: [EnveloppePermission.READ],
        UserRole.ADMIN: [EnveloppePermission.READ, EnveloppePermission.WRITE, EnveloppePermission.EXPORT],
        UserRole.SUPER_ADMIN: [EnveloppePermission.READ, EnveloppePermission.WRITE, EnveloppePermission.DELETE, EnveloppePermission.EXPORT],
    },
    "FINANCIERE": {
        UserRole.SALARIE: [],  # AUCUNE PERMISSION - Admin only
        UserRole.ADMIN: [EnveloppePermission.READ, EnveloppePermission.WRITE, EnveloppePermission.EXPORT, EnveloppePermission.DECRYPT],
        UserRole.SUPER_ADMIN: [EnveloppePermission.READ, EnveloppePermission.WRITE, EnveloppePermission.DELETE, EnveloppePermission.EXPORT, EnveloppePermission.DECRYPT],
    },
}


# =============================================================================
# ENVELOPPE RBAC ENGINE
# =============================================================================

class EnveloppeRBAC:
    """
    Engine RBAC pour contrôler l'accès aux enveloppes.
    
    Implémente les règles:
    1. CANDIDATURE : Lecture pour tous, écriture pour admin
    2. TECHNIQUE : Lecture pour tous, écriture pour admin
    3. FINANCIERE : **UNIQUEMENT admin** (toutes opérations)
    
    Intègre avec:
    - Security Engine pour authentification
    - Audit pour logging
    """
    
    @staticmethod
    def get_user_role(user_id: str, context: Optional[Dict] = None) -> UserRole:
        """
        Récupère le rôle de l'utilisateur.
        
        En production: intégration avec le système d'authentification.
        Pour les tests: utilisation du contexte ou default ADMIN.
        """
        # Si le context contient le rôle
        if context and "user_role" in context:
            return UserRole(context["user_role"])
        
        # Si user_id est dans une liste d'admins (à configurer)
        admin_users = getattr(settings, "ADMIN_USERS", [])
        if user_id in admin_users:
            return UserRole.ADMIN
        
        # Par défaut: SALARIE (principe du moindre privilège)
        return UserRole.SALARIE
    
    @staticmethod
    def check_permission(
        user_id: str,
        enveloppe_type: str,
        permission: EnveloppePermission,
        context: Optional[Dict] = None
    ) -> bool:
        """
        Vérifie si l'utilisateur a la permission sur l'enveloppe.
        
        Args:
            user_id: ID de l'utilisateur
            enveloppe_type: "CANDIDATURE", "TECHNIQUE", ou "FINANCIERE"
            permission: Permission à vérifier
            context: Contexte supplémentaire (rôle, etc.)
            
        Returns:
            True si autorisé, False sinon
        """
        # Normaliser le type d'enveloppe
        enveloppe_type = enveloppe_type.upper()
        
        # Vérifier que l'enveloppe existe
        if enveloppe_type not in RBAC_MATRIX:
            logger.error(f"Type d'enveloppe invalide: {enveloppe_type}")
            return False
        
        # Récupérer le rôle de l'utilisateur
        user_role = EnveloppeRBAC.get_user_role(user_id, context)
        
        # Vérifier la permission dans la matrice
        permissions = RBAC_MATRIX.get(enveloppe_type, {}).get(user_role, [])
        
        is_allowed = permission.value in [p.value for p in permissions]
        
        # Log pour audit
        if not is_allowed:
            logger.warning(
                f"ACCES REFUSE: user={user_id} role={user_role.value} "
                f"enveloppe={enveloppe_type} permission={permission.value}"
            )
        else:
            logger.debug(
                f"ACCES AUTORISE: user={user_id} role={user_role.value} "
                f"enveloppe={enveloppe_type} permission={permission.value}"
            )
        
        return is_allowed
    
    @staticmethod
    def can_read_enveloppe(user_id: str, enveloppe_type: str, context: Optional[Dict] = None) -> bool:
        """Vérifie si l'utilisateur peut lire l'enveloppe."""
        return EnveloppeRBAC.check_permission(user_id, enveloppe_type, EnveloppePermission.READ, context)
    
    @staticmethod
    def can_write_enveloppe(user_id: str, enveloppe_type: str, context: Optional[Dict] = None) -> bool:
        """Vérifie si l'utilisateur peut écrire dans l'enveloppe."""
        return EnveloppeRBAC.check_permission(user_id, enveloppe_type, EnveloppePermission.WRITE, context)
    
    @staticmethod
    def can_export_enveloppe(user_id: str, enveloppe_type: str, context: Optional[Dict] = None) -> bool:
        """Vérifie si l'utilisateur peut exporter l'enveloppe."""
        return EnveloppeRBAC.check_permission(user_id, enveloppe_type, EnveloppePermission.EXPORT, context)
    
    @staticmethod
    def can_decrypt_enveloppe(user_id: str, enveloppe_type: str, context: Optional[Dict] = None) -> bool:
        """Vérifie si l'utilisateur peut déchiffrer l'enveloppe."""
        return EnveloppeRBAC.check_permission(user_id, enveloppe_type, EnveloppePermission.DECRYPT, context)
    
    @staticmethod
    def assert_read_access(user_id: str, enveloppe_type: str, context: Optional[Dict] = None):
        """Lève une exception si l'accès en lecture est refusé."""
        if not EnveloppeRBAC.can_read_enveloppe(user_id, enveloppe_type, context):
            raise PermissionError(
                f"Accès refusé: l'utilisateur {user_id} ne peut pas lire l'enveloppe {enveloppe_type}. "
                f"Seul l'admin peut accéder à l'enveloppe FINANCIERE."
            )
    
    @staticmethod
    def assert_write_access(user_id: str, enveloppe_type: str, context: Optional[Dict] = None):
        """Lève une exception si l'accès en écriture est refusé."""
        if not EnveloppeRBAC.can_write_enveloppe(user_id, enveloppe_type, context):
            raise PermissionError(
                f"Accès refusé: l'utilisateur {user_id} ne peut pas écrire dans l'enveloppe {enveloppe_type}. "
                f"Seul l'admin peut modifier l'enveloppe FINANCIERE."
            )
    
    @staticmethod
    def assert_decrypt_access(user_id: str, enveloppe_type: str, context: Optional[Dict] = None):
        """Lève une exception si l'accès de déchiffrement est refusé."""
        if not EnveloppeRBAC.can_decrypt_enveloppe(user_id, enveloppe_type, context):
            raise PermissionError(
                f"Accès refusé: l'utilisateur {user_id} ne peut pas déchiffrer l'enveloppe {enveloppe_type}. "
                f"Seul l'admin peut déchiffrer l'enveloppe FINANCIERE."
            )


# =============================================================================
# DECORATORS
# =============================================================================

def require_enveloppe_read(enveloppe_type: str):
    """Decorator pour vérifier l'accès en lecture à une enveloppe."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extraire user_id et context des arguments
            user_id = kwargs.get('user_id') or kwargs.get('current_user')
            context = kwargs.get('context')
            
            if not user_id:
                raise ValueError("user_id requis pour la vérification RBAC")
            
            EnveloppeRBAC.assert_read_access(user_id, enveloppe_type, context)
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_enveloppe_write(enveloppe_type: str):
    """Decorator pour vérifier l'accès en écriture à une enveloppe."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user_id = kwargs.get('user_id') or kwargs.get('current_user')
            context = kwargs.get('context')
            
            if not user_id:
                raise ValueError("user_id requis pour la vérification RBAC")
            
            EnveloppeRBAC.assert_write_access(user_id, enveloppe_type, context)
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_enveloppe_admin(enveloppe_type: str):
    """Decorator pour vérifier que l'utilisateur est admin (pour FINANCIERE)."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user_id = kwargs.get('user_id') or kwargs.get('current_user')
            context = kwargs.get('context')
            
            if not user_id:
                raise ValueError("user_id requis pour la vérification RBAC")
            
            # Pour FINANCIERE, vérifier que l'utilisateur est au moins ADMIN
            user_role = EnveloppeRBAC.get_user_role(user_id, context)
            if user_role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
                raise PermissionError(
                    f"Accès admin requis pour l'enveloppe {enveloppe_type}. "
                    f"Votre rôle: {user_role.value}"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_financiere_warning(user_role: UserRole) -> str:
    """Retourne un message d'avertissement pour l'enveloppe FINANCIERE."""
    if user_role == UserRole.SALARIE:
        return (
            "⚠️  ENVELOPPE FINANCIERE - ACCES RESTREINT "
            "Votre rôle (SALARIE) ne peut pas accéder à cette enveloppe. "
            "Seul l'admin peut voir les données financières."
        )
    return ""


def is_financiere_admin_only(user_role: UserRole) -> bool:
    """Vérifie si l'enveloppe FINANCIERE est admin-only pour ce rôle."""
    return user_role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]


# =============================================================================
# EXPORT
# =============================================================================

__all__ = [
    'UserRole',
    'EnveloppePermission',
    'RBAC_MATRIX',
    'EnveloppeRBAC',
    'require_enveloppe_read',
    'require_enveloppe_write',
    'require_enveloppe_admin',
    'get_financiere_warning',
    'is_financiere_admin_only',
]
