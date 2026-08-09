"""
SMART_AO V7 - Plugin Engine __init__.py
========================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Plugin Engine - Moteur de plugins pour SMART_AO V7
Source: ARCHITECTURE_V7_ENGINE.md §3.4
"""

from app.engines.plugin_engine.manifest import *
from app.engines.plugin_engine.loader import *
from app.engines.plugin_engine.isolation import *

__all__ = [
    # Modules
    'manifest', 'loader', 'isolation',
    # Classes principales
    'PluginManifest', 'PluginManifestManager', 'PluginRegistration',
    'PluginLoader', 'Plugin', 'PluginSandbox', 'PluginIsolator',
    'PluginPermissions', 'PluginDependency', 'PluginMetadata',
    # Instances singleton
    'manager', 'loader', 'isolator',
    # Exceptions
    'PluginLoadError', 'PluginValidationError', 'PluginIsolationError',
    'SecurityViolationError',
    # Fonctions API
    'create_manifest', 'get_manifest', 'get_all_manifests', 'validate_manifest',
    'check_dependencies', 'load_plugin', 'unload_plugin', 'reload_plugin',
    'call_command', 'call_hooks', 'get_all_plugins_info', 'get_loaded_plugins',
    'get_failed_plugins', 'create_sandbox', 'get_permissions', 'update_permissions',
    'check_module_access', 'check_resource_access', 'destroy_sandbox', 'sandboxed'
]

# Exporter les instances singleton
def __getattr__(name):
    if name == 'manager':
        from app.engines.plugin_engine.manifest import manager
        return manager
    elif name == 'loader':
        from app.engines.plugin_engine.loader import loader
        return loader
    elif name == 'isolator':
        from app.engines.plugin_engine.isolation import isolator
        return isolator
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def init_plugin_engine():
    """Initialise le moteur de plugins."""
    from app.engines.plugin_engine.manifest import manager
    from app.engines.plugin_engine.loader import loader
    from app.engines.plugin_engine.isolation import isolator
    return True


# Initialiser automatiquement
init_plugin_engine()

