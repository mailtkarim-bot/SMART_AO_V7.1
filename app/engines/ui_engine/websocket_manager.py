"""
SMART_AO V7 - websocket_manager.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

WebSocket Manager - Gestion des connexions WebSocket en temps réel
Source: ARCHITECTURE_V7_ENGINE.md §3.4
"""

from typing import Dict, List, Optional, Any, Callable, Set, Tuple
import json
import logging
import asyncio
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import uuid

logger = logging.getLogger(__name__)


class WebSocketStatus(Enum):
    """Statuts des connexions WebSocket."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    ERROR = "error"
    AUTHENTICATED = "authenticated"


class MessageType(Enum):
    """Types de messages WebSocket."""
    TEXT = "text"
    BINARY = "binary"
    JSON = "json"
    PING = "ping"
    PONG = "pong"
    ERROR = "error"
    EVENT = "event"
    COMMAND = "command"
    NOTIFICATION = "notification"


@dataclass
class WebSocketClient:
    """Représente un client WebSocket connecté."""
    client_id: str
    websocket: Any
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    connected_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    statu: str = WebSocketStatus.CONNECTED.value
    metadata: Dict[str, Any] = field(default_factory=dict)
    subscribed_channels: Set[str] = field(default_factory=set)
    permissions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire."""
        return {
            "client_id": self.client_id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "statu": self.statu,
            "connected_at": self.connected_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "metadata": self.metadata,
            "subscribed_channels": list(self.subscribed_channels),
            "permissions": self.permissions
        }
    
    def is_authenticated(self) -> bool:
        """Vérifie si le client est authentifié."""
        return self.statu == WebSocketStatus.AUTHENTICATED.value
    
    def update_activity(self) -> None:
        """Met à jour l'horodatage de la dernière activité."""
        self.last_activity = datetime.utcnow()


@dataclass
class WebSocketMessage:
    """Représente un message WebSocket."""
    message_id: str
    client_id: str
    type: str
    data: Any
    timestamp: datetime = field(default_factory=datetime.utcnow)
    channel: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire."""
        return {
            "message_id": self.message_id,
            "client_id": self.client_id,
            "type": self.type,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "channel": self.channel
        }
    
    def to_json(self) -> str:
        """Convertir en JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=False)


@dataclass
class Channel:
    """Représente un canal de communication WebSocket."""
    channel_id: str
    nom: str
    description: str = ""
    clients: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    permissions: List[str] = field(default_factory=list)
    
    def add_client(self, client_id: str) -> None:
        """Ajoute un client au canal."""
        self.clients.add(client_id)
    
    def remove_client(self, client_id: str) -> None:
        """Retire un client du canal."""
        self.clients.discard(client_id)
    
    def has_client(self, client_id: str) -> bool:
        """Vérifie si un client est abonné."""
        return client_id in self.clients
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire."""
        return {
            "channel_id": self.channel_id,
            "nom": self.nom,
            "description": self.description,
            "nb_clients": len(self.clients),
            "metadata": self.metadata,
            "permissions": self.permissions
        }


class WebSocketManager:
    """
    Gestionnaire des connexions WebSocket.
    
    Gère les connexions, les canaux, les messages et les événements
    en temps réel pour l'interface utilisateur de SMART_AO V7.
    """
    
    def __init__(self):
        self.clients: Dict[str, WebSocketClient] = {}
        self.channels: Dict[str, Channel] = {}
        self.message_handlers: Dict[str, List[Callable]] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
        self._message_counter = 0
    
    def generate_client_id(self) -> str:
        """Génère un ID unique pour un client."""
        return f"ws_client_{uuid.uuid4().hex[:8]}"
    
    def generate_message_id(self) -> str:
        """Génère un ID unique pour un message."""
        self._message_counter += 1
        return f"msg_{self._message_counter:08d}_{datetime.utcnow().strftime('%H%M%S%f')}"
    
    async def on_connect(
        self,
        websocket: Any,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Gère une nouvelle connexion WebSocket.
        
        Args:
            websocket: Objet WebSocket
            user_id: ID de l'utilisateur (optionnel)
            metadata: Métadonnées supplémentaires
            
        Returns:
            client_id
        """
        client_id = self.generate_client_id()
        
        client = WebSocketClient(
            client_id=client_id,
            websocket=websocket,
            user_id=user_id,
            metadata=metadata or {}
        )
        
        self.clients[client_id] = client
        logger.info(f"Client connecte: {client_id} (user: {user_id})")
        
        return client_id
    
    async def on_disconnect(self, client_id: str) -> bool:
        """
        Gère la déconnexion d'un client.
        
        Args:
            client_id: ID du client
            
        Returns:
            True si le client a été déconnecté
        """
        client = self.clients.get(client_id)
        if client:
            # Retirer du client de tous les canaux
            for channel_id in list(client.subscribed_channels):
                self.unsubscribe(client_id, channel_id)
            
            # Fermer la connexion
            try:
                await client.websocket.close()
            except Exception as e:
                logger.error(f"Erreur de fermeture WebSocket: {e}")
            
            del self.clients[client_id]
            client.statu = WebSocketStatus.DISCONNECTED.value
            logger.info(f"Client deconnecte: {client_id}")
            return True
        return False
    
    async def on_message(
        self,
        client_id: str,
        message_data: Any,
        message_type: str = MessageType.TEXT.value
    ) -> Optional[WebSocketMessage]:
        """
        Gère un message reçu.
        
        Args:
            client_id: ID du client
            message_data: Données du message
            message_type: Type du message
            
        Returns:
            Message traité ou None
        """
        client = self.clients.get(client_id)
        if not client:
            logger.error(f"Client non trouve: {client_id}")
            return None
        
        client.update_activity()
        
        # Créer le message
        message_id = self.generate_message_id()
        message = WebSocketMessage(
            message_id=message_id,
            client_id=client_id,
            type=message_type,
            data=message_data
        )
        
        logger.debug(f"Message recu de {client_id}: {message_type}")
        
        # Traiter selon le type
        if message_type == MessageType.JSON.value:
            await self._handle_json_message(message)
        elif message_type == MessageType.COMMAND.value:
            await self._handle_command_message(message)
        elif message_type == MessageType.EVENT.value:
            await self._handle_event_message(message)
        else:
            # Message standard, appeler les handlers
            await self._dispatch_message(message)
        
        return message
    
    async def _handle_json_message(self, message: WebSocketMessage) -> None:
        """Traite un message JSON."""
        data = message.data
        
        if isinstance(data, dict):
            # Vérifier si c'est une commande
            if "command" in data:
                message.type = MessageType.COMMAND.value
                await self._handle_command_message(message)
            # Vérifier si c'est un événement
            elif "event" in data:
                message.type = MessageType.EVENT.value
                await self._handle_event_message(message)
            else:
                # Message standard
                await self._dispatch_message(message)
    
    async def _handle_command_message(self, message: WebSocketMessage) -> None:
        """Traite un message de commande."""
        data = message.data
        command = data.get("command", "")
        args = data.get("args", [])
        kwargs = data.get("kwargs", {})
        
        logger.info(f"Commande recue: {command} (client: {message.client_id})")
        
        # Appeler les handlers de commande
        if command in self.message_handlers:
            for handler in self.message_handlers[command]:
                try:
                    result = await handler(message, *args, **kwargs)
                    # Envoyer la réponse
                    await self.send_message(
                        message.client_id,
                        {
                            "type": "response",
                            "command": command,
                            "result": result,
                            "message_id": message.message_id
                        }
                    )
                except Exception as e:
                    logger.error(f"Erreur dans handler de commande {command}: {e}")
                    await self.send_error(
                        message.client_id,
                        f"Erreur dans commande {command}: {e}",
                        message.message_id
                    )
    
    async def _handle_event_message(self, message: WebSocketMessage) -> None:
        """Traite un message d'événement."""
        data = message.data
        event = data.get("event", "")
        payload = data.get("payload", {})
        
        logger.info(f"Evenement recu: {event} (client: {message.client_id})")
        
        # Appeler les handlers d'événement
        if event in self.event_handlers:
            for handler in self.event_handlers[event]:
                try:
                    await handler(message, payload)
                except Exception as e:
                    logger.error(f"Erreur dans handler d'evenement {event}: {e}")
    
    async def _dispatch_message(self, message: WebSocketMessage) -> None:
        """Distribue un message aux handlers."""
        handlers = self.message_handlers.get(message.type, [])
        
        for handler in handlers:
            try:
                await handler(message)
            except Exception as e:
                logger.error(f"Erreur dans handler de message: {e}")
    
    async def send_message(
        self,
        client_id: str,
        data: Any,
        message_type: str = MessageType.JSON.value,
        channel: Optional[str] = None
    ) -> bool:
        """
        Envoie un message à un client.
        
        Args:
            client_id: ID du client
            data: Données à envoyer
            message_type: Type de message
            channel: Canal (optionnel)
            
        Returns:
            True si le message a été envoyé
        """
        client = self.clients.get(client_id)
        if not client:
            logger.error(f"Client non trouve: {client_id}")
            return False
        
        try:
            message = WebSocketMessage(
                message_id=self.generate_message_id(),
                client_id=client_id,
                type=message_type,
                data=data,
                channel=channel
            )
            
            # Envoyer selon le type
            if message_type == MessageType.JSON.value:
                await client.websocket.send_json(data)
            elif message_type == MessageType.TEXT.value:
                await client.websocket.send_text(str(data))
            else:
                await client.websocket.send_text(json.dumps(data, ensure_ascii=False))
            
            client.update_activity()
            logger.debug(f"Message envoye a {client_id}")
            return True
        except Exception as e:
            logger.error(f"Erreur d'envoi de message: {e}")
            return False
    
    async def broadcast(
        self,
        data: Any,
        message_type: str = MessageType.JSON.value,
        channel: Optional[str] = None,
        exclude_clients: Optional[List[str]] = None
    ) -> int:
        """
        Diffuse un message à tous les clients.
        
        Args:
            data: Données à diffuser
            message_type: Type de message
            channel: Canal (optionnel)
            exclude_clients: Clients à exclure
            
        Returns:
            Nombre de clients ayant reçu le message
        """
        if channel:
            # Diffusion sur un canal spécifique
            channel_obj = self.channels.get(channel)
            if not channel_obj:
                return 0
            
            clients_to_send = [
                cid for cid in channel_obj.clients
                if cid in self.clients and cid not in (exclude_clients or [])
            ]
        else:
            # Diffusion à tous les clients
            clients_to_send = [
                cid for cid in self.clients
                if cid not in (exclude_clients or [])
            ]
        
        success_count = 0
        for client_id in clients_to_send:
            if await self.send_message(client_id, data, message_type, channel):
                success_count += 1
        
        logger.info(f"Broadcast vers {len(clients_to_send)} clients ({success_count} succes)")
        return success_count
    
    async def send_error(
        self,
        client_id: str,
        error_message: str,
        reference_id: Optional[str] = None
    ) -> bool:
        """
        Envoie un message d'erreur à un client.
        
        Args:
            client_id: ID du client
            error_message: Message d'erreur
            reference_id: ID de référence (optionnel)
            
        Returns:
            True si le message a été envoyé
        """
        error_data = {
            "type": MessageType.ERROR.value,
            "error": error_message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if reference_id:
            error_data["reference_id"] = reference_id
        
        return await self.send_message(client_id, error_data)
    
    def create_channel(
        self,
        channel_id: str,
        nom: str,
        description: str = "",
        permissions: Optional[List[str]] = None
    ) -> Channel:
        """
        Crée un nouveau canal.
        
        Args:
            channel_id: ID du canal
            nom: Nom du canal
            description: Description
            permissions: Permissions
            
        Returns:
            Canal créé
        """
        channel = Channel(
            channel_id=channel_id,
            nom=nom,
            description=description,
            permissions=permissions or []
        )
        
        self.channels[channel_id] = channel
        logger.info(f"Canal cree: {channel_id}")
        return channel
    
    def subscribe(self, client_id: str, channel_id: str) -> bool:
        """
        Abonne un client à un canal.
        
        Args:
            client_id: ID du client
            channel_id: ID du canal
            
        Returns:
            True si l'abonnement a réussi
        """
        client = self.clients.get(client_id)
        channel = self.channels.get(channel_id)
        
        if not client or not channel:
            return False
        
        client.subscribed_channels.add(channel_id)
        channel.add_client(client_id)
        logger.info(f"Client {client_id} abonne a canal {channel_id}")
        return True
    
    def unsubscribe(self, client_id: str, channel_id: str) -> bool:
        """
        Désabonne un client d'un canal.
        
        Args:
            client_id: ID du client
            channel_id: ID du canal
            
        Returns:
            True si le désabonnement a réussi
        """
        client = self.clients.get(client_id)
        channel = self.channels.get(channel_id)
        
        if not client or not channel:
            return False
        
        client.subscribed_channels.discard(channel_id)
        channel.remove_client(client_id)
        logger.info(f"Client {client_id} desabonne de canal {channel_id}")
        return True
    
    def register_message_handler(
        self,
        message_type: str,
        handler: Callable
    ) -> None:
        """
        Enregistre un handler de message.
        
        Args:
            message_type: Type de message
            handler: Fonction de traitement
        """
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        
        self.message_handlers[message_type].append(handler)
        logger.info(f"Handler registre pour type: {message_type}")
    
    def register_event_handler(
        self,
        event_name: str,
        handler: Callable
    ) -> None:
        """
        Enregistre un handler d'événement.
        
        Args:
            event_name: Nom de l'événement
            handler: Fonction de traitement
        """
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []
        
        self.event_handlers[event_name].append(handler)
        logger.info(f"Handler registre pour evenement: {event_name}")
    
    def get_client(self, client_id: str) -> Optional[WebSocketClient]:
        """Récupère un client par ID."""
        return self.clients.get(client_id)
    
    def get_clients(self) -> Dict[str, WebSocketClient]:
        """Récupère tous les clients."""
        return self.clients.copy()
    
    def get_channel(self, channel_id: str) -> Optional[Channel]:
        """Récupère un canal par ID."""
        return self.channels.get(channel_id)
    
    def get_channels(self) -> Dict[str, Channel]:
        """Récupère tous les canaux."""
        return self.channels.copy()
    
    def get_subscribed_channels(self, client_id: str) -> List[str]:
        """Récupère les canaux abonnés par un client."""
        client = self.clients.get(client_id)
        return list(client.subscribed_channels) if client else []
    
    def remove_inactive_clients(self, timeout_seconds: int = 3600) -> int:
        """
        Supprime les clients inactifs.
        
        Args:
            timeout_seconds: Délai d'inactivité en secondes
            
        Returns:
            Nombre de clients supprimés
        """
        now = datetime.utcnow()
        removed = 0
        
        inactive_clients = [
            client_id for client_id, client in self.clients.items()
            if (now - client.last_activity).total_seconds() > timeout_seconds
        ]
        
        for client_id in inactive_clients:
            # Déconnecter le client
            asyncio.create_task(self.on_disconnect(client_id))
            removed += 1
        
        if removed > 0:
            logger.info(f"{removed} clients inactifs supprimes")
        
        return removed
    
    async def emit_event(
        self,
        event_name: str,
        payload: Dict[str, Any],
        to_client: Optional[str] = None,
        to_channel: Optional[str] = None
    ) -> int:
        """
        Émet un événement.
        
        Args:
            event_name: Nom de l'événement
            payload: Données de l'événement
            to_client: Client spécifique (optionnel)
            to_channel: Canal spécifique (optionnel)
            
        Returns:
            Nombre de destinations ayant reçu l'événement
        """
        event_data = {
            "type": MessageType.EVENT.value,
            "event": event_name,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if to_client:
            # Envoyer à un client spécifique
            if await self.send_message(to_client, event_data):
                return 1
            return 0
        
        if to_channel:
            # Envoyer à un canal
            return await self.broadcast(event_data, channel=to_channel)
        
        # Diffusion à tous
        return await self.broadcast(event_data)


# Instance singleton
manager = WebSocketManager()


async def on_connect(websocket: Any, user_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> str:
    """Gere une nouvelle connexion."""
    return await manager.on_connect(websocket, user_id, metadata)


async def on_disconnect(client_id: str) -> bool:
    """Gere une deconnexion."""
    return await manager.on_disconnect(client_id)


async def on_message(client_id: str, message_data: Any, message_type: str = MessageType.TEXT.value) -> Optional[Dict[str, Any]]:
    """Gere un message recu."""
    message = await manager.on_message(client_id, message_data, message_type)
    return message.to_dict() if message else None


async def send_message(client_id: str, data: Any, message_type: str = MessageType.JSON.value) -> bool:
    """Envoie un message."""
    return await manager.send_message(client_id, data, message_type)


async def broadcast(data: Any, message_type: str = MessageType.JSON.value, channel: Optional[str] = None) -> int:
    """Diffuse un message."""
    return await manager.broadcast(data, message_type, channel)


def create_channel(channel_id: str, nom: str, description: str = "") -> Dict[str, Any]:
    """Cree un canal."""
    channel = manager.create_channel(channel_id, nom, description)
    return channel.to_dict()


def subscribe(client_id: str, channel_id: str) -> bool:
    """Abonne un client a un canal."""
    return manager.subscribe(client_id, channel_id)


def unsubscribe(client_id: str, channel_id: str) -> bool:
    """Desabonne un client d'un canal."""
    return manager.unsubscribe(client_id, channel_id)


def register_message_handler(message_type: str, handler: Callable) -> None:
    """Enregistre un handler de message."""
    manager.register_message_handler(message_type, handler)


def register_event_handler(event_name: str, handler: Callable) -> None:
    """Enregistre un handler d'evenement."""
    manager.register_event_handler(event_name, handler)


async def emit_event(event_name: str, payload: Dict[str, Any], to_client: Optional[str] = None, to_channel: Optional[str] = None) -> int:
    """Emet un evenement."""
    return await manager.emit_event(event_name, payload, to_client, to_channel)


def get_client_info(client_id: str) -> Optional[Dict[str, Any]]:
    """Recupere les infos d'un client."""
    client = manager.get_client(client_id)
    return client.to_dict() if client else None


def get_all_clients_info() -> Dict[str, Dict[str, Any]]:
    """Recupere les infos de tous les clients."""
    return {cid: client.to_dict() for cid, client in manager.get_clients().items()}


def get_channel_info(channel_id: str) -> Optional[Dict[str, Any]]:
    """Recupere les infos d'un canal."""
    channel = manager.get_channel(channel_id)
    return channel.to_dict() if channel else None

