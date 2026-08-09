"""
SMART_AO V7 - memoire_booster.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

Optimisation Mémoire Technique - Gestion et optimisation de la mémoire technique
Source: ARCHITECTURE_V7_ENGINE.md §4.3
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import logging
import hashlib
import json

from app.core.database import get_db
from app.core.auth import get_current_user, TokenData

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/memoire-technique", tags=["Mémoire Technique Booster"])


class TechnicalMemoryType(str):
    """Types de mémoire technique."""
    DOCUMENT = "document"
    CALCUL = "calcul"
    NOTE = "note"
    PROCEDURE = "procedure"
    RETOUR_EXPERIENCE = "retour_experience"


class TechnicalMemoryItem(BaseModel):
    """Élément de mémoire technique."""
    memory_id: str
    mission_id: Optional[str] = None
    project_id: Optional[str] = None
    memory_type: TechnicalMemoryType
    title: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    created_by: str
    version: str = Field(default="1.0")
    content_hash: str


class MemorySearchRequest(BaseModel):
    """Requête de recherche dans la mémoire technique."""
    query: str
    mission_id: Optional[str] = None
    project_id: Optional[str] = None
    memory_type: Optional[TechnicalMemoryType] = None
    tags: Optional[List[str]] = None
    limit: int = Field(default=50, ge=1, le=1000)


class MemorySearchResult(BaseModel):
    """Résultat de recherche dans la mémoire technique."""
    memory_id: str
    title: str
    memory_type: TechnicalMemoryType
    mission_id: Optional[str] = None
    project_id: Optional[str] = None
    score: float = Field(ge=0.0, le=1.0)
    excerpt: str
    tags: List[str] = Field(default_factory=list)


class MemoryOptimizationRequest(BaseModel):
    """Requête d'optimisation de la mémoire technique."""
    mission_id: str
    optimize_for: List[str] = Field(
        default_factory=list,
        description="Liste des objectifs d'optimisation (ex: ['performance', 'cout', 'securite'])"
    )
    scope: Optional[str] = None


class MemoryOptimizationResult(BaseModel):
    """Résultat d'optimisation de la mémoire technique."""
    mission_id: str
    optimized_content: str
    improvements: List[Dict[str, Any]]
    metrics: Dict[str, Any]
    recommendations: List[str]
    generated_at: datetime


class MemoryUsageStats(BaseModel):
    """Statistiques d'utilisation de la mémoire technique."""
    total_items: int
    by_type: Dict[str, int]
    by_mission: Dict[str, int]
    by_tag: Dict[str, int]
    most_accessed: List[Dict[str, Any]]
    storage_size_mb: float


class MemoryCacheEntry(BaseModel):
    """Entrée de cache mémoire."""
    cache_key: str
    data: Dict[str, Any]
    expires_at: datetime
    created_at: datetime


class MemoryBooster:
    """Optimisateur de mémoire technique."""
    
    def __init__(self):
        self.cache = {}
        self.memory_index = []
    
    def store_technical_memory(
        self,
        mission_id: Optional[str],
        project_id: Optional[str],
        memory_type: TechnicalMemoryType,
        title: str,
        content: str,
        metadata: Dict[str, Any],
        tags: List[str],
        created_by: str
    ) -> TechnicalMemoryItem:
        """Stocke un élément de mémoire technique."""
        memory_id = f"MEM-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        item = TechnicalMemoryItem(
            memory_id=memory_id,
            mission_id=mission_id,
            project_id=project_id,
            memory_type=memory_type,
            title=title,
            content=content,
            metadata=metadata,
            tags=tags,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by=created_by,
            version="1.0",
            content_hash=content_hash
        )
        
        # Ajouter à l'index
        self.memory_index.append({
            "memory_id": memory_id,
            "title": title,
            "content": content[:500],  # Indexation partielle
            "tags": tags,
            "mission_id": mission_id,
            "project_id": project_id,
            "memory_type": memory_type.value,
            "created_at": datetime.utcnow()
        })
        
        return item
    
    def search_technical_memory(
        self,
        query: str,
        mission_id: Optional[str] = None,
        project_id: Optional[str] = None,
        memory_type: Optional[TechnicalMemoryType] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50
    ) -> List[MemorySearchResult]:
        """Recherche dans la mémoire technique."""
        query_lower = query.lower()
        results = []
        
        for entry in self.memory_index:
            score = 0.0
            
            # Score basé sur la correspondance du titre
            if query_lower in entry["title"].lower():
                score += 0.4
            
            # Score basé sur la correspondance du contenu
            if query_lower in entry["content"].lower():
                score += 0.3
            
            # Score basé sur les tags
            if tags:
                matching_tags = [t for t in tags if t in entry["tags"]]
                score += 0.1 * len(matching_tags)
            
            # Score basé sur mission_id
            if mission_id and entry["mission_id"] == mission_id:
                score += 0.2
            
            # Score basé sur project_id
            if project_id and entry["project_id"] == project_id:
                score += 0.2
            
            # Score basé sur memory_type
            if memory_type and entry["memory_type"] == memory_type.value:
                score += 0.1
            
            if score > 0:
                results.append(MemorySearchResult(
                    memory_id=entry["memory_id"],
                    title=entry["title"],
                    memory_type=TechnicalMemoryType(entry["memory_type"]),
                    mission_id=entry["mission_id"],
                    project_id=entry["project_id"],
                    score=score,
                    excerpt=entry["content"][:200],
                    tags=entry["tags"]
                ))
        
        # Trier par score décroissant
        results.sort(key=lambda x: x.score, reverse=True)
        
        return results[:limit]
    
    def optimize_memory(
        self,
        mission_id: str,
        optimize_for: List[str],
        scope: Optional[str] = None
    ) -> MemoryOptimizationResult:
        """Optimise la mémoire technique pour une mission."""
        # En production: récupère les éléments de mémoire liés à la mission
        related_memories = [
            entry for entry in self.memory_index 
            if entry["mission_id"] == mission_id
        ]
        
        if not related_memories:
            return MemoryOptimizationResult(
                mission_id=mission_id,
                optimized_content="",
                improvements=[],
                metrics={},
                recommendations=["Aucune mémoire technique trouvée pour cette mission"],
                generated_at=datetime.utcnow()
            )
        
        # Construire le contenu optimisé
        optimized_content_parts = []
        improvements = []
        
        for memory in related_memories[:5]:  # Limiter à 5 mémoires
            optimized_content_parts.append(f"# {memory['title']}\n\n{memory['content'][:500]}\n")
            
            # Ajouter des améliorations spécifiques
            if "performance" in optimize_for:
                improvements.append({
                    "type": "performance",
                    "description": f"Optimisation des informations de performance pour {memory['title']}",
                    "estimated_gain": "10-15%"
                })
            
            if "cout" in optimize_for:
                improvements.append({
                    "type": "cout",
                    "description": f"Analyse des coûts dans {memory['title']}",
                    "estimated_savings": "5-10%"
                })
        
        optimized_content = "\n\n".join(optimized_content_parts)
        
        # Calculer les métriques
        metrics = {
            "total_memories_optimized": len(related_memories),
            "content_length": len(optimized_content),
            "improvement_areas": optimize_for,
            "confidence_score": 0.95
        }
        
        # Générer des recommandations
        recommendations = [
            f"Mémoire technique optimisée pour {mission_id}",
            f"Priorité donnée à: {', '.join(optimize_for)}"
        ]
        
        if len(related_memories) > 10:
            recommendations.append("Considérer l'archivage des anciennes versions de mémoire technique")
        
        return MemoryOptimizationResult(
            mission_id=mission_id,
            optimized_content=optimized_content,
            improvements=improvements,
            metrics=metrics,
            recommendations=recommendations,
            generated_at=datetime.utcnow()
        )
    
    def cache_memory_data(self, key: str, data: Dict[str, Any], ttl_seconds: int = 3600) -> MemoryCacheEntry:
        """Met des données en cache."""
        cache_key = f"CACHE-{hashlib.md5(key.encode()).hexdigest()}"
        entry = MemoryCacheEntry(
            cache_key=cache_key,
            data=data,
            expires_at=datetime.utcnow() + timedelta(seconds=ttl_seconds),
            created_at=datetime.utcnow()
        )
        
        self.cache[cache_key] = entry
        return entry
    
    def get_cached_data(self, key: str) -> Optional[MemoryCacheEntry]:
        """Récupère des données depuis le cache."""
        cache_key = f"CACHE-{hashlib.md5(key.encode()).hexdigest()}"
        entry = self.cache.get(cache_key)
        
        if entry and entry.expires_at > datetime.utcnow():
            return entry
        
        return None


booster = MemoryBooster()


@router.post("/store", response_model=TechnicalMemoryItem, status_code=status.HTTP_201_CREATED)
async def store_technical_memory(
    mission_id: Optional[str] = None,
    project_id: Optional[str] = None,
    memory_type: TechnicalMemoryType = TechnicalMemoryType.DOCUMENT,
    title: str = "Nouvelle mémoire technique",
    content: str = "",
    metadata: Optional[Dict[str, Any]] = None,
    tags: Optional[List[str]] = None,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Stocke un élément de mémoire technique.
    """
    logger.info(f"Stockage mémoire technique: {title} par {current_user.user_id}")
    
    item = booster.store_technical_memory(
        mission_id=mission_id,
        project_id=project_id,
        memory_type=memory_type,
        title=title,
        content=content,
        metadata=metadata or {},
        tags=tags or [],
        created_by=current_user.user_id
    )
    
    return item


@router.get("/search", response_model=List[MemorySearchResult])
async def search_technical_memory(
    query: str,
    mission_id: Optional[str] = None,
    project_id: Optional[str] = None,
    memory_type: Optional[TechnicalMemoryType] = None,
    tags: Optional[List[str]] = None,
    limit: int = 50,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Recherche dans la mémoire technique.
    """
    logger.info(f"Recherche mémoire technique: {query} par {current_user.user_id}")
    
    results = booster.search_technical_memory(
        query=query,
        mission_id=mission_id,
        project_id=project_id,
        memory_type=memory_type,
        tags=tags,
        limit=limit
    )
    
    return results


@router.get("/missions/{mission_id}", response_model=List[TechnicalMemoryItem])
async def get_mission_memories(
    mission_id: str,
    memory_type: Optional[TechnicalMemoryType] = None,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère tous les éléments de mémoire technique pour une mission.
    """
    logger.info(f"Mémoires techniques pour mission {mission_id} par {current_user.user_id}")
    
    # En production: requête SQL
    return []


@router.post("/optimize", response_model=MemoryOptimizationResult)
async def optimize_technical_memory(
    request: MemoryOptimizationRequest,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Optimise la mémoire technique pour une mission.
    """
    logger.info(f"Optimisation mémoire technique pour mission {request.mission_id} par {current_user.user_id}")
    
    result = booster.optimize_memory(
        mission_id=request.mission_id,
        optimize_for=request.optimize_for,
        scope=request.scope
    )
    
    return result


@router.get("/stats", response_model=MemoryUsageStats)
async def get_memory_stats(
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère les statistiques d'utilisation de la mémoire technique.
    """
    logger.info(f"Statistiques mémoire technique par {current_user.user_id}")
    
    # Calculer les statistiques depuis l'index
    total_items = len(booster.memory_index)
    
    by_type = {}
    for entry in booster.memory_index:
        mem_type = entry["memory_type"]
        by_type[mem_type] = by_type.get(mem_type, 0) + 1
    
    by_mission = {}
    for entry in booster.memory_index:
        if entry["mission_id"]:
            by_mission[entry["mission_id"]] = by_mission.get(entry["mission_id"], 0) + 1
    
    by_tag = {}
    for entry in booster.memory_index:
        for tag in entry["tags"]:
            by_tag[tag] = by_tag.get(tag, 0) + 1
    
    # Calculer la taille de stockage estimée
    storage_size = sum(len(json.dumps(entry)) for entry in booster.memory_index) / (1024 * 1024)
    
    return MemoryUsageStats(
        total_items=total_items,
        by_type=by_type,
        by_mission=by_mission,
        by_tag=by_tag,
        most_accessed=[],  # En production: basé sur les accès réels
        storage_size_mb=round(storage_size, 2)
    )


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "memoire_booster",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

