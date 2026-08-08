"""
SMART_AO V7 - base_plugin.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from enum import Enum


class PluginHook(str, Enum):
    PRE_EXECUTE = "pre_execute"
    POST_EXECUTE = "post_execute"
    ON_ERROR = "on_error"
    ON_STARTUP = "on_startup"
    ON_SHUTDOWN = "on_shutdown"


class BasePlugin(ABC):
    '''Classe de base pour tous les plugins.'''
    
    name: str = "BasePlugin"
    version: str = "1.0.0"
    author: str = "SMART_AO V7"
    description: str = ""
    hooks: List[PluginHook] = []
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        '''Initialiser le plugin.'''
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        '''Arrêter le plugin.'''
        pass
    
    def on_pre_execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        '''Hook exécuté avant une opération.'''
        return context
    
    def on_post_execute(self, context: Dict[str, Any], result: Any) -> Any:
        '''Hook exécuté après une opération.'''
        return result
    
    def on_error(self, context: Dict[str, Any], error: Exception) -> Exception:
        '''Hook exécuté en cas d'erreur.'''
        return error
