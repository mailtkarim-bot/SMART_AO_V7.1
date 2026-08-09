"""
SMART_AO V7 - isolation.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Plugin Isolation - Gestion de l'isolation et de la sécurité des plugins
Source: ARCHITECTURE_V7_ENGINE.md §3.4
"""

from typing import Dict, List, Optional, Any, Callable, Set, Union
import logging
import sys
import traceback
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
import threading

logger = logging.getLogger(__name__)


class PluginIsolationError(Exception):
    """Exception pour les erreurs d'isolation de plugin."""
    pass


class SecurityViolationError(Exception):
    """Exception pour les violations de sécurité."""
    pass


class PluginSecurityLevel(Enum):
    """Niveaux de sécurité pour les plugins."""
    SANDBOX = "sandbox"          # Exécution en sandbox complet
    RESTRICTED = "restricted"    # Restrictions sur les opérations dangereuses
    TRUSTED = "trusted"        # Plugin de confiance
    SYSTEM = "system"          # Plugin système (plein accès)


class ResourceAccess(Enum):
    """Types d'accès aux ressources."""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    DELETE = "delete"
    NETWORK = "network"
    FILE_SYSTEM = "filesystem"
    PROCESS = "process"
    ENVIRONMENT = "environment"


@dataclass
class PluginPermissions:
    """Permissions d'un plugin."""
    plugin_id: str
    security_level: str = PluginSecurityLevel.SANDBOX.value
    allowed_resources: Set[str] = field(default_factory=set)
    denied_resources: Set[str] = field(default_factory=set)
    allowed_modules: Set[str] = field(default_factory=set)
    denied_modules: Set[str] = field(default_factory=set)
    max_execution_time: float = 5.0
    max_memory_mb: int = 100
    
    def can_access(self, resource: str, access_type: str) -> bool:
        """Vérifie si le plugin peut accéder à une ressource."""
        resource_key = f"{resource}:{access_type}"
        
        if resource_key in self.denied_resources:
            return False
        
        if self.security_level == PluginSecurityLevel.SYSTEM.value:
            return True
        
        if self.security_level == PluginSecurityLevel.TRUSTED.value:
            return resource_key not in self.denied_resources
        
        return resource_key in self.allowed_resources
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire."""
        return {
            "plugin_id": self.plugin_id,
            "security_level": self.security_level,
            "allowed_resources": list(self.allowed_resources),
            "denied_resources": list(self.denied_resources),
            "allowed_modules": list(self.allowed_modules),
            "denied_modules": list(self.denied_modules),
            "max_execution_time": self.max_execution_time,
            "max_memory_mb": self.max_memory_mb
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PluginPermissions":
        """Créer à partir d'un dictionnaire."""
        return cls(
            plugin_id=data.get("plugin_id", ""),
            security_level=data.get("security_level", PluginSecurityLevel.SANDBOX.value),
            allowed_resources=set(data.get("allowed_resources", [])),
            denied_resources=set(data.get("denied_resources", [])),
            allowed_modules=set(data.get("allowed_modules", [])),
            denied_modules=set(data.get("denied_modules", [])),
            max_execution_time=data.get("max_execution_time", 5.0),
            max_memory_mb=data.get("max_memory_mb", 100)
        )


@dataclass
class PluginSandbox:
    """Environnement d'exécution isolé pour un plugin."""
    plugin_id: str
    permissions: PluginPermissions
    original_sys_modules: Dict[str, Any] = field(default_factory=dict)
    original_sys_path: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.original_sys_modules = dict(sys.modules)
        self.original_sys_path = list(sys.path)
    
    @contextmanager
    def isolate(self):
        """Contexte d'isolation pour le plugin."""
        try:
            # Sauvegarder l'état actuel
            saved_modules = dict(sys.modules)
            saved_path = list(sys.path)
            
            # Appliquer les restrictions
            self._apply_restrictions()
            
            yield self
            
        except SecurityViolationError:
            logger.error(f"Violation de securite dans plugin {self.plugin_id}")
            raise
        except Exception as e:
            logger.error(f"Erreur dans plugin {self.plugin_id}: {e}")
            raise PluginIsolationError(f"Erreur d'execution: {e}")
        finally:
            # Restaurer l'état
            self._restore_state()
    
    def _apply_restrictions(self) -> None:
        """Applique les restrictions de sécurité."""
        # Limiter les modules accessibles
        if self.permissions.denied_modules:
            for module_name in self.permissions.denied_modules:
                if module_name in sys.modules:
                    # Masquer le module
                    sys.modules[module_name] = None
        
        # Limiter sys.path
        if self.permissions.security_level in [
            PluginSecurityLevel.SANDBOX.value,
            PluginSecurityLevel.RESTRICTED.value
        ]:
            # Garder seulement les chemins sûr
            safe_paths = [
                p for p in sys.path
                if any(
                    safe in p.lower()
                    for safe in ['site-packages', 'python', 'lib']
                )
            ]
            sys.path = safe_paths
    
    def _restore_state(self) -> None:
        """Restaure l'état du système."""
        # Restaurer sys.modules
        for module_name in sys.modules:
            if module_name not in self.original_sys_modules:
                del sys.modules[module_name]
        
        for module_name, module in self.original_sys_modules.items():
            if module_name not in sys.modules:
                sys.modules[module_name] = module
        
        # Restaurer sys.path
        sys.path = self.original_sys_path
    
    def check_resource_access(self, resource: str, access_type: str) -> bool:
        """Vérifie l'accès à une ressource."""
        if not self.permissions.can_access(resource, access_type):
            logger.warning(
                f"Acces refuse: plugin {self.plugin_id} tentait d'acceder "
                f"a {resource} ({access_type})"
            )
            return False
        return True


class PluginIsolator:
    """
    Gestionnaire de l'isolation des plugins.
    
    Fournit un environnement d'exécution sécurisé pour les plugins,
    avec contrôle des accès aux ressources et protection contre les
    opérations dangereuses.
    """
    
    # Ressources sensibles par défaut
    DANGEROUS_RESOURCES = {
        ResourceAccess.FILE_SYSTEM.value: [ResourceAccess.WRITE.value, ResourceAccess.DELETE.value],
        ResourceAccess.PROCESS.value: [ResourceAccess.EXECUTE.value, ResourceAccess.DELETE.value],
        ResourceAccess.NETWORK.value: [ResourceAccess.WRITE.value],
        ResourceAccess.ENVIRONMENT.value: [ResourceAccess.WRITE.value, ResourceAccess.DELETE.value]
    }
    
    # Modules dangereux par défaut
    DANGEROUS_MODULES = [
        "os",
        "sys",
        "subprocess",
        "shutil",
        "socket",
        "http",
        "urllib",
        "requests",
        "pickle",
        "marshal",
        "importlib",
        "builtins",
        "__builtin__",
        "ctypes",
        "multiprocessing"
    ]
    
    def __init__(self):
        self.sandboxes: Dict[str, PluginSandbox] = {}
        self.permissions: Dict[str, PluginPermissions] = {}
        self._lock = threading.Lock()
    
    def create_sandbox(
        self,
        plugin_id: str,
        security_level: str = PluginSecurityLevel.SANDBOX.value,
        additional_permissions: Optional[Dict[str, Any]] = None
    ) -> PluginSandbox:
        """Crée un sandbox pour un plugin."""
        permissions = PluginPermissions(
            plugin_id=plugin_id,
            security_level=security_level,
            **{k: v for k, v in (additional_permissions or {}).items() 
               if k in ['allowed_resources', 'denied_resources', 'allowed_modules', 
                        'denied_modules', 'max_execution_time', 'max_memory_mb']}
        )
        
        # Appliquer les restrictions par défaut pour le niveau de sécurité
        self._apply_default_restrictions(permissions)
        
        sandbox = PluginSandbox(plugin_id=plugin_id, permissions=permissions)
        
        with self._lock:
            self.sandboxes[plugin_id] = sandbox
            self.permissions[plugin_id] = permissions
        
        logger.info(f"Sandbox cree pour plugin {plugin_id} (niveau: {security_level})")
        return sandbox
    
    def _apply_default_restrictions(self, permissions: PluginPermissions) -> None:
        """Applique les restrictions par défaut selon le niveau de sécurité."""
        if permissions.security_level == PluginSecurityLevel.SANDBOX.value:
            # Sandbox: tout est refusé par défaut
            permissions.denied_resources.update({
                f"{res}:{access}"
                for res, accesses in self.DANGEROUS_RESOURCES.items()
                for access in accesses
            })
            permissions.denied_modules.update(self.DANGEROUS_MODULES)
        
        elif permissions.security_level == PluginSecurityLevel.RESTRICTED.value:
            # Restreint: certaines opérations dangereuses refusées
            permissions.denied_resources.update({
                f"{ResourceAccess.FILE_SYSTEM.value}:{ResourceAccess.DELETE.value}",
                f"{ResourceAccess.PROCESS.value}:{ResourceAccess.EXECUTE.value}",
                f"{ResourceAccess.PROCESS.value}:{ResourceAccess.DELETE.value}"
            })
            permissions.denied_modules.update([
                "subprocess",
                "shutil",
                "socket",
                "ctypes"
            ])
        
        # Ajouter les autorisations de base
        permissions.allowed_resources.update({
            f"{ResourceAccess.FILE_SYSTEM.value}:{ResourceAccess.READ.value}",
            f"{ResourceAccess.ENVIRONMENT.value}:{ResourceAccess.READ.value}"
        })
    
    def get_sandbox(self, plugin_id: str) -> Optional[PluginSandbox]:
        """Récupère un sandbox par ID de plugin."""
        return self.sandboxes.get(plugin_id)
    
    def get_permissions(self, plugin_id: str) -> Optional[PluginPermissions]:
        """Récupère les permissions d'un plugin."""
        return self.permissions.get(plugin_id)
    
    def update_permissions(
        self,
        plugin_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Met à jour les permissions d'un plugin."""
        with self._lock:
            permissions = self.permissions.get(plugin_id)
            if not permissions:
                return False
            
            for key, value in updates.items():
                if hasattr(permissions, key):
                    setattr(permissions, key, value)
            
            logger.info(f"Permissions mises a jour pour plugin {plugin_id}")
            return True
    
    @contextmanager
    def execute_in_sandbox(
        self,
        plugin_id: str,
        timeout: Optional[float] = None
    ):
        """
        Exécute du code dans un sandbox.
        
        Args:
            plugin_id: ID du plugin
            timeout: Timeout en secondes (None pour pas de timeout)
            
        Yields:
            PluginSandbox
        """
        sandbox = self.get_sandbox(plugin_id)
        if not sandbox:
            raise PluginIsolationError(f"Sandbox non trouve pour plugin {plugin_id}")
        
        # Appliquer le timeout si spécifié
        if timeout is None:
            timeout = sandbox.permissions.max_execution_time
        
        # Utiliser le contexte d'isolation
        with sandbox.isolate():
            yield sandbox
    
    def wrap_function(
        self,
        plugin_id: str,
        func: Callable
    ) -> Callable:
        """
        Enveloppe une fonction pour qu'elle s'exécute dans un sandbox.
        
        Args:
            plugin_id: ID du plugin
            func: Fonction à envelopper
            
        Returns:
            Fonction enveloppée
        """
        sandbox = self.get_sandbox(plugin_id)
        if not sandbox:
            return func
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self.execute_in_sandbox(plugin_id):
                return func(*args, **kwargs)
        
        return wrapper
    
    def wrap_all_plugin_functions(
        self,
        plugin_id: str,
        module: Any
    ) -> Any:
        """
        Enveloppe toutes les fonctions d'un module plugin.
        
        Args:
            plugin_id: ID du plugin
            module: Module à envelopper
            
        Returns:
            Module avec les fonctions enveloppées
        """
        sandbox = self.get_sandbox(plugin_id)
        if not sandbox:
            return module
        
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if callable(attr):
                setattr(module, attr_name, self.wrap_function(plugin_id, attr))
        
        return module
    
    def check_module_access(self, plugin_id: str, module_name: str) -> bool:
        """Vérifie si un plugin peut accéder à un module."""
        permissions = self.get_permissions(plugin_id)
        if not permissions:
            return False
        
        if module_name in permissions.denied_modules:
            return False
        
        if module_name in permissions.allowed_modules:
            return True
        
        if permissions.security_level == PluginSecurityLevel.SYSTEM.value:
            return True
        
        if permissions.security_level == PluginSecurityLevel.TRUSTED.value:
            return module_name not in permissions.denied_modules
        
        # Par défaut, refus pour les plugins non-trusted
        return module_name not in self.DANGEROUS_MODULES
    
    def check_resource_access(
        self,
        plugin_id: str,
        resource: str,
        access_type: str
    ) -> bool:
        """Vérifie si un plugin peut accéder à une ressource."""
        sandbox = self.get_sandbox(plugin_id)
        if not sandbox:
            return False
        return sandbox.check_resource_access(resource, access_type)
    
    def destroy_sandbox(self, plugin_id: str) -> bool:
        """Détruit un sandbox."""
        with self._lock:
            if plugin_id in self.sandboxes:
                del self.sandboxes[plugin_id]
                if plugin_id in self.permissions:
                    del self.permissions[plugin_id]
                logger.info(f"Sandbox detruit pour plugin {plugin_id}")
                return True
            return False


isolator = PluginIsolator()


def create_sandbox(
    plugin_id: str,
    security_level: str = PluginSecurityLevel.SANDBOX.value,
    additional_permissions: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Cree un sandbox pour un plugin."""
    sandbox = isolator.create_sandbox(plugin_id, security_level, additional_permissions)
    return {
        "plugin_id": plugin_id,
        "security_level": security_level,
        "permissions": sandbox.permissions.to_dict()
    }


def get_permissions(plugin_id: str) -> Optional[Dict[str, Any]]:
    """Recupere les permissions d'un plugin."""
    permissions = isolator.get_permissions(plugin_id)
    return permissions.to_dict() if permissions else None


def update_permissions(plugin_id: str, updates: Dict[str, Any]) -> bool:
    """Met a jour les permissions d'un plugin."""
    return isolator.update_permissions(plugin_id, updates)


def check_module_access(plugin_id: str, module_name: str) -> bool:
    """Verifie l'acces a un module."""
    return isolator.check_module_access(plugin_id, module_name)


def check_resource_access(plugin_id: str, resource: str, access_type: str) -> bool:
    """Verifie l'acces a une ressource."""
    return isolator.check_resource_access(plugin_id, resource, access_type)


def destroy_sandbox(plugin_id: str) -> bool:
    """Detruit un sandbox."""
    return isolator.destroy_sandbox(plugin_id)


# Decorateur pour envelopper les fonctions de plugin
def sandboxed(plugin_id: str):
    """Decorateur pour executer une fonction dans un sandbox."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            with isolator.execute_in_sandbox(plugin_id):
                return func(*args, **kwargs)
        return wrapper
    return decorator

