"""
SMART_AO V7 - example_plugin.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


from typing import Dict, Any

from .base_plugin import BasePlugin, PluginHook


class ExamplePlugin(BasePlugin):
    '''Plugin exemple pour démonstration.'''
    
    name = "ExamplePlugin"
    version = "1.0.0"
    author = "SMART_AO V7"
    description = "Plugin exemple pour tester le système de plugins"
    hooks = [
        PluginHook.PRE_EXECUTE,
        PluginHook.POST_EXECUTE,
    ]
    
    def __init__(self):
        self._config: Dict[str, Any] = {}
    
    def initialize(self, config: Dict[str, Any]) -> None:
        self._config = config
        print(f"{self.name} initialized with config: {config}")
    
    def shutdown(self) -> None:
        print(f"{self.name} shutting down")
    
    def on_pre_execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        print(f"{self.name}: Pre-execute hook triggered")
        context["example_plugin"] = "pre_execute_called"
        return context
    
    def on_post_execute(self, context: Dict[str, Any], result: Any) -> Any:
        print(f"{self.name}: Post-execute hook triggered")
        if isinstance(result, dict):
            result["example_plugin"] = "post_execute_called"
        return result
