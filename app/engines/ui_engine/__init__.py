"""
SMART_AO V7 - UI Engine __init__.py
===================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

UI Engine - Moteur d'interface utilisateur pour SMART_AO V7
Source: ARCHITECTURE_V7_ENGINE.md §3.4
"""

from app.engines.ui_engine.websocket_manager import *

try:
    from app.engines.ui_engine.sse import sse_engine
    from app.engines.ui_engine.streaming import streaming_engine
    from app.engines.ui_engine.websocket_handler import ws_handler
except ImportError:
    sse_engine = None
    streaming_engine = None
    ws_handler = None

__all__ = [
    # Modules
    'websocket_manager',
    # Classes principales
    'WebSocketManager', 'WebSocketClient', 'WebSocketMessage', 'Channel',
    # Instances singleton
    'manager',
    # Fonctions API
    'on_connect', 'on_disconnect', 'on_message', 'send_message', 'broadcast',
    'create_channel', 'subscribe', 'unsubscribe', 'register_message_handler',
    'register_event_handler', 'emit_event', 'get_client_info', 'get_all_clients_info',
    'get_channel_info',
    # Compatibilité
    'sse_engine', 'streaming_engine', 'ws_handler'
]

# Exporter les instances singleton
def __getattr__(name):
    if name == 'manager':
        from app.engines.ui_engine.websocket_manager import manager
        return manager
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def init_ui_engine():
    """Initialise le moteur d'UI."""
    from app.engines.ui_engine.websocket_manager import manager
    return True


# Initialiser automatiquement
init_ui_engine()
