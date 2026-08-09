"""Streaming Engine - Streaming de réponses IA"""
import logging
from typing import AsyncGenerator, Dict, Any

logger = logging.getLogger(__name__)

class StreamingEngine:
    """Gère le streaming des réponses IA vers le frontend"""
    
    async def stream_analysis(
        self,
        mission_id: int,
        analysis_steps: list
    ) -> AsyncGenerator[Dict, None]:
        """Stream l'analyse étape par étape"""
        for i, step in enumerate(analysis_steps):
            yield {
                "step": i + 1,
                "total": len(analysis_steps),
                "current_step": step,
                "status": "processing"
            }
            
            # Simulation délai traitement
            import asyncio
            await asyncio.sleep(0.5)
            
            yield {
                "step": i + 1,
                "status": "completed",
                "result": f"Résultat de {step}"
            }
    
    async def stream_token_response(
        self,
        response_text: str,
        chunk_size: int = 10
    ) -> AsyncGenerator[str, None]:
        """Stream une réponse token par token"""
        for i in range(0, len(response_text), chunk_size):
            chunk = response_text[i:i+chunk_size]
            yield chunk
    
    async def stream_table_update(
        self,
        table_data: list,
        batch_size: int = 10
    ) -> AsyncGenerator[list, None]:
        """Stream les lignes d'un tableau par batches"""
        for i in range(0, len(table_data), batch_size):
            batch = table_data[i:i+batch_size]
            yield batch

# Instance globale
streaming_engine = StreamingEngine()
