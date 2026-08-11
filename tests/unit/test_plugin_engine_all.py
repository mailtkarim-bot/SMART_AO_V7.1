"""
SMART_AO V7 - Tests unitaires pour plugin_engine
================================================
Tests qui exécutent le code des modules plugin_engine pour améliorer la couverture.
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))


class TestPluginEngineImports:
    """Test l'import des modules plugin_engine."""
    
    def test_loader_import(self):
        """Test l'import de PluginLoader."""
        from app.engines.plugin_engine.loader import PluginLoader
        assert PluginLoader is not None
    
    def test_manifest_import(self):
        """Test l'import de PluginManifest."""
        from app.engines.plugin_engine.manifest import PluginManifest
        assert PluginManifest is not None


class TestPluginLoader:
    """Tests pour PluginLoader."""
    
    def test_plugin_loader_initialization(self):
        """Test l'initialisation de PluginLoader."""
        from app.engines.plugin_engine.loader import PluginLoader
        
        loader = PluginLoader()
        assert loader is not None
    
    def test_plugin_loader_has_load_method(self):
        """Test que PluginLoader a une méthode load_plugin."""
        from app.engines.plugin_engine.loader import PluginLoader
        assert hasattr(PluginLoader, 'load_plugin')
    
    def test_plugin_loader_has_discover_method(self):
        """Test que PluginLoader a une méthode discover_and_load."""
        from app.engines.plugin_engine.loader import PluginLoader
        assert hasattr(PluginLoader, 'discover_and_load')
        assert hasattr(PluginLoader, 'load_plugin')


class TestPluginManifest:
    """Tests pour PluginManifest."""
    
    def test_plugin_manifest_is_dataclass(self):
        """Test que PluginManifest est un dataclass."""
        from app.engines.plugin_engine.manifest import PluginManifest
        import dataclasses
        assert dataclasses.is_dataclass(PluginManifest)
    
    def test_plugin_manifest_has_to_dict_method(self):
        """Test que PluginManifest a une méthode to_dict."""
        from app.engines.plugin_engine.manifest import PluginManifest
        assert hasattr(PluginManifest, 'to_dict')
    
    def test_plugin_manifest_has_from_dict_method(self):
        """Test que PluginManifest a une méthode from_dict."""
        from app.engines.plugin_engine.manifest import PluginManifest
        assert hasattr(PluginManifest, 'from_dict')
