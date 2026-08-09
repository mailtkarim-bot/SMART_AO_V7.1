"""WebSocket Manager - Notifications temps réel via WebSocket"""
from typing import Dict, Set, Any
import logging
import asyncio

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Gère les connexions WebSocket pour les notifications temps réel"""
    
    def __init__(self):
        self.active_connections: Dict[int, Set[Any]] = {}  # user_id -> set of connections
        self.mission_subscriptions: Dict[int, Set[int]] = {}  # mission_id -> set of user_ids
    
    async def connect(self, websocket: Any, user_id: int):
        """Accepte une nouvelle connexion WebSocket"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        
        logger.info(f"WebSocket connecté: user {user_id}")
    
    def disconnect(self, websocket: Any, user_id: int):
        """Ferme une connexion WebSocket"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        logger.info(f"WebSocket déconnecté: user {user_id}")
    
    async def send_personal_message(self, message: dict, user_id: int):
        """Envoie un message à un utilisateur spécifique"""
        if user_id not in self.active_connections:
            return
        
        disconnected = set()
        for connection in self.active_connections[user_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Échec envoi WebSocket: {str(e)}")
                disconnected.add(connection)
        
        # Nettoyer les connexions mortes
        for conn in disconnected:
            self.active_connections[user_id].discard(conn)
    
    async def broadcast_mission_update(self, mission_id: int, update: dict):
        """Diffuse une mise à jour de mission à tous les abonnés"""
        if mission_id not in self.mission_subscriptions:
            return
        
        message = {
            "type": "mission_update",
            "mission_id": mission_id,
            "data": update
        }
        
        for user_id in self.mission_subscriptions[mission_id]:
            await self.send_personal_message(message, user_id)
    
    def subscribe_mission(self, mission_id: int, user_id: int):
        """Abonne un utilisateur aux updates d'une mission"""
        if mission_id not in self.mission_subscriptions:
            self.mission_subscriptions[mission_id] = set()
        self.mission_subscriptions[mission_id].add(user_id)
    
    def unsubscribe_mission(self, mission_id: int, user_id: int):
        """Désabonne un utilisateur"""
        if mission_id in self.mission_subscriptions:
            self.mission_subscriptions[mission_id].discard(user_id)

# Instance globale
ws_manager = WebSocketManager()
