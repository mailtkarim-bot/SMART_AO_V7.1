"""WebSocket Handler - Gestion des connexions WebSocket"""
import logging
from typing import Dict, Set, Any
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class WebSocketHandler:
    """Gère les connexions WebSocket pour l'UI"""
    
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}
        self.user_subscriptions: Dict[int, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accepte une connexion"""
        await websocket.accept()
        self.connections[client_id] = websocket
        logger.info(f"WS connecté: {client_id}")
    
    def disconnect(self, client_id: str):
        """Ferme une connexion"""
        if client_id in self.connections:
            del self.connections[client_id]
        logger.info(f"WS déconnecté: {client_id}")
    
    async def send_message(self, client_id: str, message: dict):
        """Envoie un message à un client"""
        if client_id in self.connections:
            try:
                await self.connections[client_id].send_json(message)
            except Exception as e:
                logger.error(f"Échec envoi WS: {str(e)}")
                self.disconnect(client_id)
    
    async def broadcast(self, message: dict, exclude: str = None):
        """Diffuse à tous les clients"""
        disconnected = []
        for client_id, ws in self.connections.items():
            if client_id == exclude:
                continue
            try:
                await ws.send_json(message)
            except:
                disconnected.append(client_id)
        
        for client_id in disconnected:
            self.disconnect(client_id)
    
    def subscribe_user(self, user_id: int, client_id: str):
        """Abonne un client aux updates d'un utilisateur"""
        if user_id not in self.user_subscriptions:
            self.user_subscriptions[user_id] = set()
        self.user_subscriptions[user_id].add(client_id)
    
    async def notify_user(self, user_id: int, message: dict):
        """Notifie tous les clients d'un utilisateur"""
        if user_id in self.user_subscriptions:
            for client_id in self.user_subscriptions[user_id]:
                await self.send_message(client_id, message)

# Instance globale
ws_handler = WebSocketHandler()
