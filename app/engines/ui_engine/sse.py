"""SSE Engine - Server-Sent Events pour streaming temps réel"""
import logging
from typing import AsyncGenerator, Dict, Any
import json

logger = logging.getLogger(__name__)

class SSEEngine:
    """Gère les Server-Sent Events pour le frontend"""
    
    def __init__(self):
        self.subscribers: Dict[int, list] = {}  # user_id -> list of queues
    
    async def stream_updates(self, user_id: int) -> AsyncGenerator[str, None]:
        """Stream les updates pour un utilisateur"""
        import asyncio
        
        queue = asyncio.Queue()
        if user_id not in self.subscribers:
            self.subscribers[user_id] = []
        self.subscribers[user_id].append(queue)
        
        try:
            while True:
                message = await queue.get()
                yield f"data: {json.dumps(message)}\n\n"
        except GeneratorExit:
            # Nettoyage
            if user_id in self.subscribers:
                self.subscribers[user_id].remove(queue)
    
    async def send_update(self, user_id: int, event_type: str, data: Dict):
        """Envoie une update à un utilisateur"""
        message = {
            "event": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if user_id in self.subscribers:
            for queue in self.subscribers[user_id]:
                await queue.put(message)
    
    async def broadcast_progress(
        self, 
        mission_id: int, 
        step: str, 
        progress: float,
        details: Optional[str] = None
    ):
        """Broadcast la progression d'une mission"""
        message = {
            "type": "progress",
            "mission_id": mission_id,
            "step": step,
            "progress": progress,
            "details": details
        }
        
        # À implémenter avec subscription par mission
        logger.info(f"Progress: {mission_id}/{step} = {progress*100:.1f}%")

from datetime import datetime
# Instance globale
sse_engine = SSEEngine()
