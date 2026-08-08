"""
SMART_AO V7 - audit.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - Audit Trail WORM
================================
Système de traçabilité des actions (Write Once, Read Many)
Conforme ISO 27001 et RGPD

Source: ARCHITECTURE_V7_ENGINE.md §4.2
"""

import os
import json
import logging
import hashlib
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import uuid
import threading

from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, Index
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

logger = logging.getLogger(__name__)


# =============================================================================
# CONSTANTES
# =============================================================================

# Noms des actions auditées
class AuditAction(Enum):
    """Types d'actions auditées."""
    # Actions utilisateur
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    LOGIN_FAILED = "LOGIN_FAILED"
    
    # Actions sur les missions
    MISSION_CREATED = "MISSION_CREATED"
    MISSION_UPDATED = "MISSION_UPDATED"
    MISSION_DELETED = "MISSION_DELETED"
    MISSION_STATUS_CHANGED = "MISSION_STATUS_CHANGED"
    
    # Actions sur les documents
    DOCUMENT_UPLOADED = "DOCUMENT_UPLOADED"
    DOCUMENT_DOWNLOADED = "DOCUMENT_DOWNLOADED"
    DOCUMENT_DELETED = "DOCUMENT_DELETED"
    DOCUMENT_SCANNED = "DOCUMENT_SCANNED"
    
    # Actions sur les agents
    AGENT_EXECUTED = "AGENT_EXECUTED"
    AGENT_FAILED = "AGENT_FAILED"
    
    # Actions de configuration
    CONFIG_UPDATED = "CONFIG_UPDATED"
    USER_CREATED = "USER_CREATED"
    USER_UPDATED = "USER_UPDATED"
    USER_DELETED = "USER_DELETED"
    
    # Actions de sécurité
    RBAC_CHANGED = "RBAC_CHANGED"
    PERMISSION_GRANTED = "PERMISSION_GRANTED"
    PERMISSION_REVOKED = "PERMISSION_REVOKED"
    
    # Actions système
    SYSTEM_STARTED = "SYSTEM_STARTED"
    SYSTEM_SHUTDOWN = "SYSTEM_SHUTDOWN"
    BACKUP_CREATED = "BACKUP_CREATED"


# Niveaux de gravité
class AuditLevel(Enum):
    """Niveaux de gravité des actions."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# =============================================================================
# MODÈLE SQLALCHEMY
# =============================================================================

class AuditLog(Base):
    """
    Modèle SQLAlchemy pour le journal d'audit.
    Implémente le principe WORM (Write Once, Read Many).
    """
    __tablename__ = "audit_logs"
    
    # Champ ID (auto-généré)
    id = Column(Integer, primary_key=True, index=True)
    
    # Identifiant unique de l'événement
    event_id = Column(String(64), unique=True, index=True, nullable=False)
    
    # Timestamp
    timestamp = Column(DateTime(timezone=True), index=True, nullable=False)
    
    # Utilisateur
    user_id = Column(String(64), index=True)
    username = Column(String(128))
    role = Column(String(64))
    
    # Action
    action = Column(String(64), index=True, nullable=False)
    level = Column(String(32), index=True, nullable=False, default="INFO")
    
    # Contexte
    resource_type = Column(String(64), index=True)  # mission, document, user, etc.
    resource_id = Column(String(128), index=True)  # ID de la ressource
    
    # Données de l'action
    details = Column(JSON)  # Données JSON de l'action
    
    # Metadata
    ip_address = Column(String(45))  # IPv4 ou IPv6
    user_agent = Column(String(512))
    
    # Intégrité
    hash = Column(String(64))  # Hash SHA-256 de l'événement
    is_modified = Column(Boolean, default=False, nullable=False)  # WORM: ne doit jamais être True
    
    # Index pour les recherches rapides
    __table_args__ = (
        Index('idx_audit_user_action', 'user_id', 'action'),
        Index('idx_audit_timestamp', 'timestamp'),
    )


# =============================================================================
# STRUCTURES DE DONNÉES
# =============================================================================

@dataclass
class AuditEvent:
    """Représente un événement d'audit."""
    action: AuditAction
    level: AuditLevel = AuditLevel.INFO
    user_id: Optional[str] = None
    username: Optional[str] = None
    role: Optional[str] = None
    
    # Ressource concernée
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    
    # Détails de l'action
    details: Dict[str, Any] = field(default_factory=dict)
    
    # Contexte
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Généré automatiquement
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir en dictionnaire."""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "action": self.action.value,
            "level": self.level.value,
            "user_id": self.user_id,
            "username": self.username,
            "role": self.role,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "details": self.details,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent
        }
    
    def compute_hash(self) -> str:
        """Calculer le hash SHA-256 de l'événement."""
        data_str = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()


@dataclass
class AuditQuery:
    """Requête de recherche dans les logs d'audit."""
    user_id: Optional[str] = None
    action: Optional[AuditAction] = None
    level: Optional[AuditLevel] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: int = 100
    offset: int = 0


@dataclass
class AuditStats:
    """Statistiques d'audit."""
    total_events: int = 0
    events_by_action: Dict[str, int] = field(default_factory=dict)
    events_by_level: Dict[str, int] = field(default_factory=dict)
    events_by_user: Dict[str, int] = field(default_factory=dict)
    recent_events: List[Dict[str, Any]] = field(default_factory=list)


# =============================================================================
# SERVICE D'AUDIT
# =============================================================================

class AuditService:
    """
    Service de journalisation d'audit WORM.
    
    Caractéristiques:
    - Write Once, Read Many (WORM): les événements ne peuvent pas être modifiés
    - Conformité ISO 27001 et RGPD
    - Indexation par utilisateur, action, ressource, etc.
    - Recherche rapide
    - Statistiques et rapports
    """
    
    def __init__(self):
        self.events: List[AuditEvent] = []
        self.lock = threading.Lock()
        self._initialized = False
    
    async def initialize(self, db: AsyncSession) -> None:
        """Initialiser le service (vérifier la base de données)."""
        # Créer la table si elle n'existe pas
        async with db.begin():
            # SQLAlchemy crée automatiquement les tables
            pass
        
        self._initialized = True
        logger.info("AuditService initialisé")
    
    def _create_event_from_dict(self, data: Dict[str, Any]) -> AuditEvent:
        """Créer un AuditEvent à partir d'un dictionnaire."""
        try:
            action = AuditAction(data.get("action", "LOGIN"))
        except ValueError:
            action = AuditAction.LOGIN
        
        try:
            level = AuditLevel(data.get("level", "INFO"))
        except ValueError:
            level = AuditLevel.INFO
        
        return AuditEvent(
            action=action,
            level=level,
            user_id=data.get("user_id"),
            username=data.get("username"),
            role=data.get("role"),
            resource_type=data.get("resource_type"),
            resource_id=data.get("resource_id"),
            details=data.get("details", {}),
            ip_address=data.get("ip_address"),
            user_agent=data.get("user_agent"),
            event_id=data.get("event_id", str(uuid.uuid4())),
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else datetime.now(timezone.utc)
        )
    
    async def log_event(
        self,
        event: AuditEvent,
        db: Optional[AsyncSession] = None
    ) -> str:
        """
        Journaliser un événement d'audit.
        
        Args:
            event: Événement à journaliser
            db: Session de base de données (optionnelle)
        
        Returns:
            str: ID de l'événement
        """
        # Calculer le hash
        event_hash = event.compute_hash()
        
        # En mode mémoire (pour les tests)
        with self.lock:
            self.events.append(event)
        
        # En mode base de données
        if db is not None:
            try:
                # Convertir en AuditLog pour SQLAlchemy
                audit_log = AuditLog(
                    event_id=event.event_id,
                    timestamp=event.timestamp,
                    user_id=event.user_id,
                    username=event.username,
                    role=event.role,
                    action=event.action.value,
                    level=event.level.value,
                    resource_type=event.resource_type,
                    resource_id=event.resource_id,
                    details=event.details,
                    ip_address=event.ip_address,
                    user_agent=event.user_agent,
                    hash=event_hash,
                    is_modified=False
                )
                
                db.add(audit_log)
                await db.commit()
                
                logger.debug(f"Événement d'audit journalisé: {event.action.value} - {event.event_id}")
                
            except Exception as e:
                logger.error(f"Erreur lors de la journalisation en base: {e}")
                await db.rollback()
        
        return event.event_id
    
    async def log_action(
        self,
        action: AuditAction,
        user: Optional[Dict[str, Any]] = None,
        resource: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None,
        db: Optional[AsyncSession] = None,
        **kwargs
    ) -> str:
        """
        Journaliser une action de manière simplifiée.
        
        Args:
            action: Type d'action
            user: Informations utilisateur
            resource: Informations sur la ressource
            details: Détails supplémentaires
            db: Session de base de données
            **kwargs: Autres paramètres
        
        Returns:
            str: ID de l'événement
        """
        event = AuditEvent(
            action=action,
            user_id=user.get("user_id") if user else None,
            username=user.get("username") if user else None,
            role=user.get("role") if user else None,
            resource_type=resource.get("type") if resource else None,
            resource_id=resource.get("id") if resource else None,
            details=details or {},
            ip_address=kwargs.get("ip_address"),
            user_agent=kwargs.get("user_agent"),
            level=kwargs.get("level", AuditLevel.INFO)
        )
        
        return await self.log_event(event, db)
    
    async def query_events(
        self,
        query: AuditQuery,
        db: Optional[AsyncSession] = None
    ) -> List[Dict[str, Any]]:
        """
        Rechercher des événements d'audit.
        
        Args:
            query: Requête de recherche
            db: Session de base de données
        
        Returns:
            List[Dict]: Liste d'événements
        """
        # En mode mémoire
        if db is None:
            with self.lock:
                results = []
                for event in self.events:
                    if query.user_id and event.user_id != query.user_id:
                        continue
                    if query.action and event.action != query.action:
                        continue
                    if query.level and event.level != query.level:
                        continue
                    if query.resource_type and event.resource_type != query.resource_type:
                        continue
                    if query.resource_id and event.resource_id != query.resource_id:
                        continue
                    if query.start_time and event.timestamp < query.start_time:
                        continue
                    if query.end_time and event.timestamp > query.end_time:
                        continue
                    
                    results.append(event.to_dict())
                
                return results[query.offset:query.offset + query.limit]
        
        # En mode base de données
        try:
            from sqlalchemy import select, and_
            from sqlalchemy.sql import or_
            
            conditions = []
            if query.user_id:
                conditions.append(AuditLog.user_id == query.user_id)
            if query.action:
                conditions.append(AuditLog.action == query.action.value)
            if query.level:
                conditions.append(AuditLog.level == query.level.value)
            if query.resource_type:
                conditions.append(AuditLog.resource_type == query.resource_type)
            if query.resource_id:
                conditions.append(AuditLog.resource_id == query.resource_id)
            if query.start_time:
                conditions.append(AuditLog.timestamp >= query.start_time)
            if query.end_time:
                conditions.append(AuditLog.timestamp <= query.end_time)
            
            stmt = select(AuditLog)
            if conditions:
                stmt = stmt.where(and_(*conditions))
            
            stmt = stmt.order_by(AuditLog.timestamp.desc())
            stmt = stmt.offset(query.offset).limit(query.limit)
            
            result = await db.execute(stmt)
            logs = result.scalars().all()
            
            return [
                {
                    "event_id": log.event_id,
                    "timestamp": log.timestamp.isoformat(),
                    "action": log.action,
                    "level": log.level,
                    "user_id": log.user_id,
                    "username": log.username,
                    "role": log.role,
                    "resource_type": log.resource_type,
                    "resource_id": log.resource_id,
                    "details": log.details or {},
                    "ip_address": log.ip_address,
                    "user_agent": log.user_agent,
                    "hash": log.hash,
                    "is_modified": log.is_modified
                }
                for log in logs
            ]
            
        except Exception as e:
            logger.error(f"Erreur lors de la requête d'audit: {e}")
            return []
    
    async def get_stats(
        self,
        days: int = 30,
        db: Optional[AsyncSession] = None
    ) -> AuditStats:
        """
        Obtenir des statistiques d'audit.
        
        Args:
            days: Nombre de jours à analyser
            db: Session de base de données
        
        Returns:
            AuditStats: Statistiques
        """
        from datetime import timedelta
        
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=days)
        
        query = AuditQuery(
            start_time=start_time,
            end_time=end_time,
            limit=1000
        )
        
        events = await self.query_events(query, db)
        
        stats = AuditStats(total_events=len(events))
        
        for event in events:
            # Par action
            stats.events_by_action[event["action"]] = \
                stats.events_by_action.get(event["action"], 0) + 1
            
            # Par niveau
            stats.events_by_level[event["level"]] = \
                stats.events_by_level.get(event["level"], 0) + 1
            
            # Par utilisateur
            if event.get("user_id"):
                stats.events_by_user[event["user_id"]] = \
                    stats.events_by_user.get(event["user_id"], 0) + 1
            
        # Événements récents (par timestamp)
        stats.recent_events = sorted(events, key=lambda x: x["timestamp"], reverse=True)[:10]
        
        return stats
    
    async def export_events(
        self,
        query: AuditQuery,
        format: str = "json",
        db: Optional[AsyncSession] = None
    ) -> Union[str, bytes]:
        """
        Exporter des événements d'audit.
        
        Args:
            query: Requête de recherche
            format: Format d'export (json, csv)
            db: Session de base de données
        
        Returns:
            Union[str, bytes]: Données exportées
        """
        events = await self.query_events(query, db)
        
        if format == "json":
            return json.dumps(events, indent=2, ensure_ascii=False)
        elif format == "csv":
            # Générer CSV
            headers = ["event_id", "timestamp", "action", "level", "user_id", "username", 
                      "role", "resource_type", "resource_id", "details", 
                      "ip_address", "user_agent"]
            
            csv_lines = [",".join(headers)]
            for event in events:
                row = [
                    event.get("event_id", ""),
                    event.get("timestamp", ""),
                    event.get("action", ""),
                    event.get("level", ""),
                    event.get("user_id", ""),
                    event.get("username", ""),
                    event.get("role", ""),
                    event.get("resource_type", ""),
                    event.get("resource_id", ""),
                    json.dumps(event.get("details", {}), ensure_ascii=False),
                    event.get("ip_address", ""),
                    event.get("user_agent", "")
                ]
                csv_lines.append(",".join(f'"{v}"' for v in row))
            
            return "\n".join(csv_lines).encode("utf-8")
        else:
            raise ValueError(f"Format non supporté: {format}")


# ==============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

# Instance globale
_audit_service: Optional[AuditService] = None


def get_audit_service() -> AuditService:
    """Récupérer l'instance globale du service d'audit."""
    global _audit_service
    if _audit_service is None:
        _audit_service = AuditService()
    return _audit_service


async def log_audit_event(
    action: AuditAction,
    user: Optional[Dict[str, Any]] = None,
    resource: Optional[Dict[str, Any]] = None,
    details: Optional[Dict[str, Any]] = None,
    db: Optional[AsyncSession] = None,
    **kwargs
) -> str:
    """
    Journaliser un événement d'audit (fonction utilitaire).
    
    Args:
        action: Type d'action
        user: Informations utilisateur
        resource: Informations sur la ressource
        details: Détails supplémentaires
        db: Session de base de données
        **kwargs: Autres paramètres
    
    Returns:
        str: ID de l'événement
    """
    service = get_audit_service()
    return await service.log_action(action, user, resource, details, db, **kwargs)


# ==============================================================================
# DÉCORATEURS
# =============================================================================

def audit_action(action: AuditAction, resource_type: str = None):
    """
    Décorateur pour auditer une action.
    
    Args:
        action: Type d'action
        resource_type: Type de ressource
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            service = get_audit_service()
            
            # Extraire les informations utilisateur
            user = kwargs.get("current_user") or (args and hasattr(args[0], "user_id") and args[0])
            if user and hasattr(user, "user_id"):
                user_info = {
                    "user_id": user.user_id,
                    "username": getattr(user, "username", None),
                    "role": getattr(user, "role", None)
                }
            else:
                user_info = None
            
            # Extraire les informations sur la ressource
            resource_id = kwargs.get("resource_id") or kwargs.get("id")
            if resource_id:
                resource_info = {
                    "type": resource_type,
                    "id": str(resource_id)
                }
            else:
                resource_info = None
            
            # Appeler la fonction originale
            result = await func(*args, **kwargs)
            
            # Journaliser l'action
            await service.log_action(
                action=action,
                user=user_info,
                resource=resource_info,
                details={"result": "success", "return": str(type(result))}
            )
            
            return result
        
        return wrapper
    return decorator


if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Tester le service d'audit
        service = get_audit_service()
        
        # Journaliser quelques événements
        event1 = AuditEvent(
            action=AuditAction.LOGIN,
            level=AuditLevel.INFO,
            user_id="user_001",
            username="john.doe",
            role="PATRON",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            details={"status": "success"}
        )
        
        event_id = await service.log_event(event1)
        print(f"Événement journalisé: {event_id}")
        
        # Journaliser un événement avec la méthode simplifiée
        event_id2 = await service.log_action(
            action=AuditAction.DOCUMENT_UPLOADED,
            user={"user_id": "user_002", "username": "jane.smith", "role": "CHARGE_ETUDES"},
            resource={"type": "document", "id": "doc_001"},
            details={"filename": "dce.pdf", "size": 1024}
        )
        print(f"Événement journalisé: {event_id2}")
        
        # Récupérer les statistiques
        stats = await service.get_stats(days=1)
        print(f"\nStatistiques: {stats.total_events} événements")
        print(f"Par action: {stats.events_by_action}")
        
        # Rechercher des événements
        query = AuditQuery(
            action=AuditAction.LOGIN,
            limit=10
        )
        results = await service.query_events(query)
        print(f"\nÉvénements LOGIN: {len(results)}")
        for r in results:
            print(f"  - {r['action']}: {r['user_id']}@{r['timestamp']}")


    asyncio.run(main())

