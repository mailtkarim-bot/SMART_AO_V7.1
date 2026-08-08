"""
SMART_AO V7 - registry.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


from typing import Dict, List, Optional, Any, Type
from pathlib import Path
import importlib
import logging

from .base_plugin import BasePlugin, PluginHook

logger = logging.getLogger(__name__)


class PluginRegistry:
    '''Registre des plugins SMART_AO V7.'''
    
    def __init__(self):
        self._plugins: Dict[str, BasePlugin] = {}
        self._hooks: Dict[PluginHook, List[BasePlugin]] = {
            hook: [] for hook in PluginHook
        }
    
    def register(self, plugin: BasePlugin) -> None:
        '''Enregistrer un plugin.'''
        if plugin.name in self._plugins:
            logger.warning(f"Plugin {plugin.name} already registered, overwriting")
        self._plugins[plugin.name] = plugin
        
        for hook in plugin.hooks:
            if hook not in self._hooks:
                self._hooks[hook] = []
            self._hooks[hook].append(plugin)
        
        logger.info(f"Plugin {plugin.name} v{plugin.version} registered")
    
    def unregister(self, plugin_name: str) -> bool:
        '''Désenregistrer un plugin.'''
        if plugin_name not in self._plugins:
            return False
        del self._plugins[plugin_name]
        logger.info(f"Plugin {plugin_name} unregistered")
        return True
    
    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        '''Récupérer un plugin par nom.'''
        return self._plugins.get(plugin_name)
    
    def list_plugins(self) -> List[BasePlugin]:
        '''Lister tous les plugins.'''
        return list(self._plugins.values())
    
    def discover_plugins(self, directory: str = "app/plugins") -> int:
        '''Découvrir et charger automatiquement les plugins.'''
        plugins_dir = Path(directory)
        count = 0
        
        if not plugins_dir.exists():
            logger.warning(f"Plugins directory {directory} not found")
            return 0
        
        for plugin_file in plugins_dir.glob("*_plugin.py"):
            if plugin_file.name.startswith("_"):
                continue
            
            module_name = f"{directory}.{plugin_file.stem}".replace("/", ".")
            try:
                module = importlib.import_module(module_name)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type) 
                        and issubclass(attr, BasePlugin) 
                        and attr != BasePlugin
                    ):
                        plugin_instance = attr()
                        self.register(plugin_instance)
                        count += 1
            except Exception as e:
                logger.error(f"Failed to load plugin {plugin_file}: {e}")
        
        logger.info(f"Discovered and loaded {count} plugins")
        return count
    
    def trigger_hook(
        self, 
        hook: PluginHook, 
        context: Dict[str, Any], 
        result: Any = None,
        error: Exception = None
    ) -> Any:
        '''Déclencher un hook pour tous les plugins enregistrés.'''
        plugins = self._hooks.get(hook, [])
        
        for plugin in plugins:
            try:
                if hook == PluginHook.PRE_EXECUTE:
                    context = plugin.on_pre_execute(context)
                elif hook == PluginHook.POST_EXECUTE:
                    result = plugin.on_post_execute(context, result)
                elif hook == PluginHook.ON_ERROR:
                    error = plugin.on_error(context, error)
            except Exception as e:
                logger.error(f"Plugin {plugin.name} hook {hook} failed: {e}")
        
        return result or context


# Instance singleton
plugin_registry = PluginRegistry()


def get_plugin_registry() -> PluginRegistry:
    return plugin_registry
