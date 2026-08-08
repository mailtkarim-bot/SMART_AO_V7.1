"""
SMART_AO V7 - test_plugins.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from app.plugins.base_plugin import BasePlugin, PluginHook
from app.plugins.registry import PluginRegistry
from app.plugins.example_plugin import ExamplePlugin


class TestPluginRegistry:
    def test_register_plugin(self):
        registry = PluginRegistry()
        plugin = ExamplePlugin()
        registry.register(plugin)
        assert plugin.name in [p.name for p in registry.list_plugins()]
    
    def test_get_plugin(self):
        registry = PluginRegistry()
        plugin = ExamplePlugin()
        registry.register(plugin)
        retrieved = registry.get_plugin(plugin.name)
        assert retrieved == plugin
    
    def test_list_plugins(self):
        registry = PluginRegistry()
        plugin1 = ExamplePlugin()
        plugin2 = ExamplePlugin()
        plugin2.name = "AnotherPlugin"
        registry.register(plugin1)
        registry.register(plugin2)
        plugins = registry.list_plugins()
        assert len(plugins) == 2


class TestPluginBase:
    """Tests pour la classe BasePlugin."""
    
    def test_base_plugin_defaults(self):
        """Test les valeurs par défaut du plugin de base."""
        # BasePlugin est abstrait, on utilise ExamplePlugin qui en hérite
        from app.plugins.example_plugin import ExamplePlugin
        plugin = ExamplePlugin()
        assert plugin.name == "ExamplePlugin"
        assert plugin.version == "1.0.0"
        assert plugin.author == "SMART_AO V7"
    
    def test_base_plugin_abstract_methods(self):
        """Test que BasePlugin a les méthodes abstraites."""
        from app.plugins.base_plugin import BasePlugin
        assert hasattr(BasePlugin, 'initialize')
        assert hasattr(BasePlugin, 'shutdown')


class TestPluginRegistryExtended:
    """Tests étendus pour PluginRegistry."""
    
    def test_get_plugin_not_found(self):
        """Test la récupération d'un plugin inexistant."""
        registry = PluginRegistry()
        plugin = registry.get_plugin("NonExistentPlugin")
        assert plugin is None
    
    def test_unregister_plugin(self):
        """Test le désenregistrement d'un plugin."""
        registry = PluginRegistry()
        plugin1 = ExamplePlugin()
        plugin2 = ExamplePlugin()
        plugin2.name = "AnotherPlugin"
        
        registry.register(plugin1)
        registry.register(plugin2)
        assert len(registry.list_plugins()) == 2
        
        registry.unregister(plugin1.name)
        plugins = registry.list_plugins()
        plugin_names = [p.name for p in plugins]
        assert plugin1.name not in plugin_names
        assert len(plugins) == 1
    
    def test_list_plugins_filtered(self):
        """Test le listage des plugins avec filtrage manuel."""
        registry = PluginRegistry()
        plugin1 = ExamplePlugin()
        plugin1.capabilities = ["test", "demo"]
        plugin2 = ExamplePlugin()
        plugin2.name = "AnotherPlugin"
        plugin2.capabilities = ["prod", "demo"]
        
        registry.register(plugin1)
        registry.register(plugin2)
        
        # Filtrer manuellement par capacité
        all_plugins = registry.list_plugins()
        demo_plugins = [p for p in all_plugins if "demo" in p.capabilities]
        assert len(demo_plugins) == 2


class TestExamplePlugin:
    """Tests pour le plugin exemple."""
    
    def test_example_plugin_creation(self):
        """Test la création du plugin exemple."""
        plugin = ExamplePlugin()
        assert plugin.name == "ExamplePlugin"
        assert plugin.version == "1.0.0"
        assert plugin.description == "Plugin exemple pour tester le système de plugins"
    
    def test_example_plugin_hooks_callable(self):
        """Test que les hooks du plugin exemple sont appelables."""
        plugin = ExamplePlugin()
        assert callable(plugin.on_pre_execute)
        assert callable(plugin.on_post_execute)
        # on_error n'est pas implémenté dans ExamplePlugin
        # assert callable(plugin.on_error)
