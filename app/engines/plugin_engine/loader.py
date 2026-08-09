"""
SMART_AO V7 - loader.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Plugin Loader - Chargement dynamique des plugins
Source: ARCHITECTURE_V7_ENGINE.md §3.4
"""

from typing import Dict, List, Optional, Any, Callable, Type, Set
import importlib
import logging
import sys
from pathlib import Path
from datetime import datetime
import inspect

from app.engines.plugin_engine.manifest import PluginManifest, PluginManifestManager, PluginRegistration

logger = logging.getLogger(__name__)


class PluginLoadError(Exception):
    """Exception pour les erreurs de chargement de plugin."""
    pass


class PluginValidationError(Exception):
    """Exception pour les erreurs de validation de plugin."""
    pass


class Plugin:
    """Représente un plugin chargé."""
    
    def __init__(
        self,
        plugin_id: str,
        module: Any,
        manifest: PluginManifest,
        registration: PluginRegistration
    ):
        self.plugin_id = plugin_id
        self.module = module
        self.manifest = manifest
        self.registration = registration
        self._commands: Dict[str, Callable] = {}
        self._hooks: Dict[str, List[Callable]] = {}
        self._loaded = False
        self._load_time = None
    
    def load(self) -> None:
        """Charge le plugin."""
        if self._loaded:
            return
        
        logger.info(f"Chargement du plugin: {self.plugin_id}")
        
        # Charger les commandes
        self._load_commands()
        
        # Charger les hooks
        self._load_hooks()
        
        self._loaded = True
        self._load_time = datetime.utcnow()
        
        logger.info(f"Plugin charge: {self.plugin_id}")
    
    def _load_commands(self) -> None:
        """Charge les commandes du plugin."""
        for route in self.manifest.routes:
            if 'command' in route and route['command'] in dir(self.module):
                cmd_name = route.get('name', route['command'])
                self._commands[cmd_name] = getattr(self.module, route['command'])
                logger.debug(f"Commande chargee: {cmd_name} (plugin: {self.plugin_id})")
    
    def _load_hooks(self) -> None:
        """Charge les hooks du plugin."""
        for hook in self.manifest.hooks:
            if hook['name'] in dir(self.module):
                hook_func = getattr(self.module, hook['name'])
                if hook['event'] not in self._hooks:
                    self._hooks[hook['event']] = []
                self._hooks[hook['event']].append(hook_func)
                logger.debug(f"Hook charge: {hook['name']} pour evenement {hook['event']}")
    
    def get_command(self, command_name: str) -> Optional[Callable]:
        """Récupère une commande par nom."""
        return self._commands.get(command_name)
    
    def get_hooks(self, event_name: str) -> List[Callable]:
        """Récupère les hooks pour un événement."""
        return self._hooks.get(event_name, [])
    
    def has_hooks(self, event_name: str) -> bool:
        """Vérifie si le plugin a des hooks pour un événement."""
        return event_name in self._hooks and len(self._hooks[event_name]) > 0
    
    @property
    def is_loaded(self) -> bool:
        """Vérifie si le plugin est chargé."""
        return self._loaded
    
    @property
    def load_time(self) -> Optional[datetime]:
        """Retourne l'heure de chargement."""
        return self._load_time


class PluginLoader:
    """
    Chargeur dynamique de plugins.
    
    Gère le chargement, l'initialisation et la gestion du cycle de vie
    des plugins SMART_AO V7.
    """
    
    def __init__(self, plugins_dir: str = "plugins", auto_load: bool = True):
        self.plugins_dir = Path(plugins_dir)
        self.manifest_manager = PluginManifestManager(plugins_dir)
        self._plugins: Dict[str, Plugin] = {}
        self._loaded_plugins: Set[str] = set()
        self._failed_plugins: Dict[str, str] = {}
        
        if auto_load:
            self.discover_and_load()
    
    def discover_and_load(self) -> Dict[str, bool]:
        """
        Découvre et charge tous les plugins.
        
        Returns:
            Dictionnaire {plugin_id: succes}
        """
        results = {}
        
        for plugin_id, manifest in self.manifest_manager.get_all_manifests().items():
            try:
                plugin = self.load_plugin(plugin_id)
                if plugin:
                    results[plugin_id] = True
                else:
                    results[plugin_id] = False
            except Exception as e:
                logger.error(f"Erreur de chargement du plugin {plugin_id}: {e}")
                results[plugin_id] = False
                self._failed_plugins[plugin_id] = str(e)
        
        return results
    
    def load_plugin(self, plugin_id: str) -> Optional[Plugin]:
        """
        Charge un plugin par son ID.
        
        Args:
            plugin_id: ID du plugin à charger
            
        Returns:
            Plugin chargé ou None si échec
        """
        if plugin_id in self._plugins:
            return self._plugins[plugin_id]
        
        manifest = self.manifest_manager.get_manifest(plugin_id)
        if not manifest:
            logger.error(f"Manifeste non trouve pour plugin: {plugin_id}")
            return None
        
        registration = self.manifest_manager.get_registration(plugin_id)
        if not registration:
            logger.error(f"Enregistrement non trouve pour plugin: {plugin_id}")
            return None
        
        # Valider le manifeste
        is_valid, errors = self.manifest_manager.validate_manifest(manifest)
        if not is_valid:
            raise PluginValidationError(f"Manifeste invalide: {errors}")
        
        # Vérifier la compatibilité
        is_compatible, errors = self.manifest_manager.check_compatibility(manifest)
        if not is_compatible:
            raise PluginValidationError(f"Plugin non compatible: {errors}")
        
        # Charger le module
        try:
            module = self._load_module(plugin_id, registration.chemin, manifest.entry_point)
        except Exception as e:
            raise PluginLoadError(f"Echec du chargement du module: {e}")
        
        # Créer le plugin
        plugin = Plugin(plugin_id, module, manifest, registration)
        plugin.load()
        
        self._plugins[plugin_id] = plugin
        self._loaded_plugins.add(plugin_id)
        
        logger.info(f"Plugin charge avec succes: {plugin_id}")
        return plugin
    
    def _load_module(
        self,
        plugin_id: str,
        plugin_path: str,
        entry_point: str
    ) -> Any:
        """Charge un module Python."""
        # Ajouter le chemin du plugin au sys.path
        plugin_dir = Path(plugin_path)
        if str(plugin_dir) not in sys.path:
            sys.path.insert(0, str(plugin_dir))
        
        # Charger le module d'entrée
        try:
            module_path = plugin_dir / entry_point
            if not module_path.exists():
                raise ImportError(f"Module d'entree non trouve: {module_path}")
            
            # Extraire le nom du module (sans .py)
            module_name = entry_point.replace(".py", "").replace("/", ".")
            
            # Utiliser importlib pour charger le module
            spec = importlib.util.spec_from_file_location(
                f"{plugin_id}_module",
                str(module_path)
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[f"{plugin_id}_module"] = module
                spec.loader.exec_module(module)
                return module
            else:
                raise ImportError(f"Impossible de charger le module: {module_path}")
        except Exception as e:
            raise PluginLoadError(f"Erreur de chargement du module {entry_point}: {e}")
    
    def unload_plugin(self, plugin_id: str) -> bool:
        """Décharge un plugin."""
        if plugin_id not in self._plugins:
            return False
        
        plugin = self._plugins[plugin_id]
        
        # Nettoyer les hooks et commandes
        plugin._commands.clear()
        plugin._hooks.clear()
        plugin._loaded = False
        
        del self._plugins[plugin_id]
        self._loaded_plugins.discard(plugin_id)
        
        logger.info(f"Plugin decharge: {plugin_id}")
        return True
    
    def reload_plugin(self, plugin_id: str) -> Optional[Plugin]:
        """Recharge un plugin."""
        self.unload_plugin(plugin_id)
        return self.load_plugin(plugin_id)
    
    def get_plugin(self, plugin_id: str) -> Optional[Plugin]:
        """Récupère un plugin chargé."""
        return self._plugins.get(plugin_id)
    
    def get_all_plugins(self) -> Dict[str, Plugin]:
        """Récupère tous les plugins chargés."""
        return self._plugins.copy()
    
    def get_loaded_plugin_ids(self) -> List[str]:
        """Récupère la liste des IDs des plugins chargés."""
        return list(self._plugins.keys())
    
    def get_failed_plugin_ids(self) -> Dict[str, str]:
        """Récupère la liste des plugins échoués avec leurs erreurs."""
        return self._failed_plugins.copy()
    
    def call_command(
        self,
        plugin_id: str,
        command_name: str,
        *args,
        **kwargs
    ) -> Any:
        """Appelle une commande de plugin."""
        plugin = self.get_plugin(plugin_id)
        if not plugin:
            raise PluginLoadError(f"Plugin non charge: {plugin_id}")
        
        command = plugin.get_command(command_name)
        if not command:
            raise PluginLoadError(f"Commande non trouve: {command_name} (plugin: {plugin_id})")
        
        return command(*args, **kwargs)
    
    def call_hooks(
        self,
        event_name: str,
        *args,
        **kwargs
    ) -> List[Any]:
        """Appelle tous les hooks pour un événement."""
        results = []
        
        for plugin_id, plugin in self._plugins.items():
            if plugin.has_hooks(event_name):
                hooks = plugin.get_hooks(event_name)
                for hook in hooks:
                    try:
                        result = hook(*args, **kwargs)
                        results.append(result)
                        logger.debug(f"Hook execute: {event_name} (plugin: {plugin_id})")
                    except Exception as e:
                        logger.error(f"Erreur dans hook {event_name} (plugin: {plugin_id}): {e}")
        
        return results
    
    def get_plugins_with_command(self, command_name: str) -> List[str]:
        """Récupère les plugins ayant une commande spécifique."""
        return [
            plugin_id for plugin_id, plugin in self._plugins.items()
            if plugin.get_command(command_name) is not None
        ]
    
    def get_plugins_with_hook(self, event_name: str) -> List[str]:
        """Récupère les plugins ayant un hook pour un événement."""
        return [
            plugin_id for plugin_id, plugin in self._plugins.items()
            if plugin.has_hooks(event_name)
        ]
    
    def get_plugin_info(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les informations d'un plugin."""
        plugin = self.get_plugin(plugin_id)
        if not plugin:
            return None
        
        return {
            "plugin_id": plugin.plugin_id,
            "metadata": plugin.manifest.metadata.to_dict(),
            "entry_point": plugin.manifest.entry_point,
            "is_loaded": plugin.is_loaded,
            "load_time": plugin.load_time.isoformat() if plugin.load_time else None,
            "commands": list(plugin._commands.keys()),
            "hooks": {event: len(hooks) for event, hooks in plugin._hooks.items()}
        }
    
    def get_all_plugins_info(self) -> Dict[str, Dict[str, Any]]:
        """Récupère les informations de tous les plugins."""
        return {
            plugin_id: self.get_plugin_info(plugin_id)
            for plugin_id in self._plugins
        }


# Instance singleton
loader = PluginLoader()


def load_plugin(plugin_id: str) -> Optional[Dict[str, Any]]:
    """Charge un plugin et retourne ses infos."""
    plugin = loader.load_plugin(plugin_id)
    return loader.get_plugin_info(plugin_id) if plugin else None


def unload_plugin(plugin_id: str) -> bool:
    """Decharge un plugin."""
    return loader.unload_plugin(plugin_id)


def reload_plugin(plugin_id: str) -> Optional[Dict[str, Any]]:
    """Recharge un plugin."""
    plugin = loader.reload_plugin(plugin_id)
    return loader.get_plugin_info(plugin_id) if plugin else None


def call_command(plugin_id: str, command_name: str, *args, **kwargs) -> Any:
    """Appelle une commande de plugin."""
    return loader.call_command(plugin_id, command_name, *args, **kwargs)


def call_hooks(event_name: str, *args, **kwargs) -> List[Any]:
    """Appelle tous les hooks pour un evenement."""
    return loader.call_hooks(event_name, *args, **kwargs)


def get_all_plugins_info() -> Dict[str, Dict[str, Any]]:
    """Recupere les infos de tous les plugins."""
    return loader.get_all_plugins_info()


def get_loaded_plugins() -> List[str]:
    """Recupere la liste des plugins charges."""
    return loader.get_loaded_plugin_ids()


def get_failed_plugins() -> Dict[str, str]:
    """Recupere les plugins echoues."""
    return loader.get_failed_plugin_ids()


