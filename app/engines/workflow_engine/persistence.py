"""
SMART_AO V7 - persistence.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""

"""
SMART_AO V7 - Workflow Persistence
===================================
Persistance PostgreSQL pour les missions, étapes et événements.
Single-tenant pur : aucune colonne tenant_id.
Source: ARCHITECTURE_V7_ENGINE.md §4.1
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from dataclasses import dataclass, asdict, field
import logging

from sqlalchemy import select, update, delete, insert, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import engine, Base, async_session_maker
from app.models.mission import Mission as MissionModel, MissionStatus, MissionStep, MissionStepStatus
from app.models.events import MissionEvent
from app.models.project import Project

logger = logging.getLogger(__name__)


def _naive_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """Convertit un datetime timezone-aware en naive UTC pour SQLAlchemy."""
    if dt is None:
        return None
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


# =============================================================================
# DATA CLASSES (pour compatibilité avec l'existant)
# =============================================================================

@dataclass
class MissionRecord:
    """Enregistrement d'une mission en base."""
    mission_id: str
    project_id: Optional[str] = None
    mission_type: str = ""
    name: str = ""
    description: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    status: str = "CREATED"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    total_steps: int = 0
    completed_steps: int = 0
    error_message: Optional[str] = None
    extra_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MissionRecord':
        return cls(
            mission_id=data.get("mission_id", ""),
            project_id=data.get("project_id"),
            mission_type=data.get("mission_type", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            context=data.get("context", {}),
            status=data.get("status", "CREATED"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(timezone.utc),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.now(timezone.utc),
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            total_steps=data.get("total_steps", 0),
            completed_steps=data.get("completed_steps", 0),
            error_message=data.get("error_message"),
            extra_metadata=data.get("extra_metadata", {})
        )

    def to_model(self) -> MissionModel:
        """Convertir en modèle SQLAlchemy"""
        return MissionModel(
            mission_id=self.mission_id,
            name=self.name,
            description=self.description,
            status=MissionStatus(self.status),
            created_at=_naive_utc(self.created_at),
            updated_at=_naive_utc(self.updated_at),
            completed_at=_naive_utc(self.completed_at),
            total_steps=self.total_steps,
            completed_steps=self.completed_steps,
            error_message=self.error_message,
            extra_metadata=self.extra_metadata,
            project_id=self.project_id,
        )

    @classmethod
    def from_model(cls, model: MissionModel) -> 'MissionRecord':
        """Convertir depuis un modèle SQLAlchemy"""
        return cls(
            mission_id=model.mission_id,
            project_id=model.project_id,
            mission_type="",
            name=model.name,
            description=model.description or "",
            context={},
            status=model.status.value,
            created_at=model.created_at,
            updated_at=model.updated_at,
            completed_at=model.completed_at,
            total_steps=model.total_steps,
            completed_steps=model.completed_steps,
            error_message=model.error_message,
            extra_metadata=model.extra_metadata or {}
        )


@dataclass
class StepRecord:
    """Enregistrement d'une étape de mission."""
    step_id: str
    mission_id: str
    step_name: str = ""
    step_order: int = 0
    status: str = "PENDING"
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    agent_name: Optional[str] = None
    execution_time_ms: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StepRecord':
        return cls(
            step_id=data.get("step_id", ""),
            mission_id=data.get("mission_id", ""),
            step_name=data.get("step_name", ""),
            step_order=data.get("step_order", 0),
            status=data.get("status", "PENDING"),
            input_data=data.get("input_data", {}),
            output_data=data.get("output_data", {}),
            error_message=data.get("error_message"),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            agent_name=data.get("agent_name"),
            execution_time_ms=data.get("execution_time_ms", 0.0),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(timezone.utc)
        )

    def to_model(self, mission_id: int) -> Dict[str, Any]:
        """Convertir en dictionnaire pour insertion SQLAlchemy"""
        return {
            "mission_id": mission_id,
            "step_name": self.step_name,
            "step_order": self.step_order,
            "status": MissionStepStatus(self.status),
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error_message": self.error_message,
            "started_at": _naive_utc(self.started_at),
            "completed_at": _naive_utc(self.completed_at),
            "agent_name": self.agent_name,
            "execution_time_ms": self.execution_time_ms,
        }

    @classmethod
    def from_model(cls, model: MissionStep, mission_id: str) -> 'StepRecord':
        """Convertir depuis un modèle SQLAlchemy"""
        return cls(
            step_id=str(model.id),
            mission_id=mission_id,
            step_name=model.step_name,
            step_order=model.step_order,
            status=model.status.value,
            input_data=model.input_data or {},
            output_data=model.output_data or {},
            error_message=model.error_message,
            started_at=model.started_at,
            completed_at=model.completed_at,
            agent_name=model.agent_name,
            execution_time_ms=model.execution_time_ms or 0.0,
            created_at=model.created_at
        )


@dataclass
class EventRecord:
    """Enregistrement d'un événement."""
    event_id: str
    event_type: str = ""
    mission_id: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EventRecord':
        return cls(
            event_id=data.get("event_id", ""),
            event_type=data.get("event_type", ""),
            mission_id=data.get("mission_id"),
            data=data.get("data", {}),
            metadata=data.get("metadata", {}),
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else datetime.now(timezone.utc)
        )

    def to_model(self, mission_id: Optional[int] = None) -> Dict[str, Any]:
        """Convertir en dictionnaire pour insertion SQLAlchemy"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "mission_id": mission_id,
            "data": self.data,
            "metadata": self.metadata,
            "timestamp": _naive_utc(self.timestamp)
        }

    @classmethod
    def from_model(cls, model: MissionEvent, mission_id: Optional[str] = None) -> 'EventRecord':
        """Convertir depuis un modèle SQLAlchemy"""
        return cls(
            event_id=model.event_id,
            event_type=model.event_type,
            mission_id=mission_id,
            data=model.data or {},
            metadata=model.metadata or {},
            timestamp=model.timestamp
        )


# =============================================================================
# PERSISTENCE POSTGRESQL
# =============================================================================

class WorkflowPersistence:
    """
    Gestion de la persistance des workflows en PostgreSQL.
    Single-tenant pur : aucune isolation tenant en code métier.
    """

    def __init__(self, db: Optional[AsyncSession] = None):
        self._db = db
        self._missions: Dict[str, MissionRecord] = {}  # Cache en mémoire
        self._steps: Dict[str, List[StepRecord]] = {}  # Cache en mémoire
        self._events: List[EventRecord] = []  # Cache en mémoire

    async def get_db(self) -> AsyncSession:
        """Obtenir une nouvelle session de base de données"""
        return async_session_maker()

    async def close(self):
        """Fermer la connexion (no-op car les sessions sont jetables)"""
        pass

    # =========================================================================
    # MISSIONS
    # =========================================================================

    async def save_mission(self, mission: MissionRecord) -> bool:
        """Sauvegarder une mission en PostgreSQL."""
        try:
            async with async_session_maker() as db:
                # Vérifier si la mission existe déjà
                result = await db.execute(
                    select(MissionModel).where(MissionModel.mission_id == mission.mission_id)
                )
                existing = result.scalar_one_or_none()

                if existing:
                    # Mise à jour
                    existing.name = mission.name
                    existing.description = mission.description
                    existing.status = MissionStatus(mission.status)
                    existing.total_steps = mission.total_steps
                    existing.completed_steps = mission.completed_steps
                    existing.error_message = mission.error_message
                    existing.extra_metadata = mission.extra_metadata
                    existing.project_id = mission.project_id
                    existing.created_at = _naive_utc(mission.created_at)
                    existing.updated_at = _naive_utc(datetime.now(timezone.utc))
                    existing.completed_at = _naive_utc(mission.completed_at)
                else:
                    # Insertion
                    existing = mission.to_model()
                    db.add(existing)

                await db.commit()
                await db.refresh(existing)

                # Mettre à jour le cache
                self._missions[mission.mission_id] = mission

                logger.info(f"Mission saved to PostgreSQL: {mission.mission_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to save mission: {e}")
            return False

    async def get_mission(self, mission_id: str) -> Optional[MissionRecord]:
        """Récupérer une mission depuis PostgreSQL."""
        try:
            # D'abord vérifier le cache
            if mission_id in self._missions:
                return self._missions[mission_id]

            async with async_session_maker() as db:
                query = select(MissionModel).where(MissionModel.mission_id == mission_id)
                result = await db.execute(query)
                model = result.scalar_one_or_none()

                if model:
                    mission = MissionRecord.from_model(model)
                    self._missions[mission.mission_id] = mission
                    return mission

                return None
        except Exception as e:
            logger.error(f"Failed to get mission: {e}")
            return None

    async def list_missions(
        self,
        project_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[MissionRecord]:
        """Lister les missions depuis PostgreSQL avec filtres."""
        try:
            async with async_session_maker() as db:
                query = select(MissionModel)

                if project_id:
                    query = query.where(MissionModel.project_id == project_id)

                if status:
                    query = query.where(MissionModel.status == status)

                query = query.order_by(desc(MissionModel.created_at))
                query = query.limit(limit).offset(offset)

                result = await db.execute(query)
                models = result.scalars().all()

                missions = []
                for model in models:
                    mission = MissionRecord.from_model(model)
                    missions.append(mission)
                    self._missions[mission.mission_id] = mission

                return missions
        except Exception as e:
            logger.error(f"Failed to list missions: {e}")
            return []

    async def count_missions(
        self,
        status: Optional[str] = None
    ) -> int:
        """Compter les missions."""
        try:
            async with async_session_maker() as db:
                query = select(func.count()).select_from(MissionModel)

                if status:
                    query = query.where(MissionModel.status == status)

                result = await db.execute(query)
                return result.scalar() or 0
        except Exception as e:
            logger.error(f"Failed to count missions: {e}")
            return 0

    async def delete_mission(self, mission_id: str) -> bool:
        """Supprimer une mission."""
        try:
            async with async_session_maker() as db:
                query = delete(MissionModel).where(MissionModel.mission_id == mission_id)
                result = await db.execute(query)
                await db.commit()

                if result.rowcount > 0:
                    # Supprimer du cache
                    if mission_id in self._missions:
                        del self._missions[mission_id]
                    if mission_id in self._steps:
                        del self._steps[mission_id]

                    logger.info(f"Mission deleted: {mission_id}")
                    return True

                return False
        except Exception as e:
            logger.error(f"Failed to delete mission: {e}")
            return False

    # =========================================================================
    # STEPS
    # =========================================================================

    async def _get_mission_model(
        self,
        mission_id: str,
        db: Optional[AsyncSession] = None
    ) -> Optional[MissionModel]:
        """Récupérer le modèle SQLAlchemy Mission par mission_id."""
        if db is not None:
            query = select(MissionModel).where(MissionModel.mission_id == mission_id)
            result = await db.execute(query)
            return result.scalar_one_or_none()

        async with async_session_maker() as db:
            return await self._get_mission_model(mission_id, db)

    async def save_step(self, step: StepRecord) -> bool:
        """Sauvegarder une étape en PostgreSQL."""
        try:
            async with async_session_maker() as db:
                # Récupérer la mission pour avoir l'ID
                mission_model = await self._get_mission_model(step.mission_id, db)
                if not mission_model:
                    logger.error(f"Mission not found: {step.mission_id}")
                    return False

                mission_db_id = mission_model.id

                # Vérifier si l'étape existe déjà
                result = await db.execute(
                    select(MissionStep).where(
                        and_(
                            MissionStep.mission_id == mission_db_id,
                            MissionStep.step_order == step.step_order
                        )
                    )
                )
                existing = result.scalar_one_or_none()

                step_data = step.to_model(mission_db_id)
                if existing:
                    # Mise à jour
                    for key, value in step_data.items():
                        if hasattr(existing, key) and key not in ("mission_id", "step_order"):
                            setattr(existing, key, value)
                else:
                    # Insertion
                    existing = MissionStep(**step_data)
                    db.add(existing)

                await db.commit()
                await db.refresh(existing)

                # Mettre à jour le cache
                if step.mission_id not in self._steps:
                    self._steps[step.mission_id] = []
                self._steps[step.mission_id].append(step)

                logger.info(f"Step saved to PostgreSQL: {step.step_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to save step: {e}")
            return False

    async def get_steps(self, mission_id: str) -> List[StepRecord]:
        """Récupérer les étapes d'une mission depuis PostgreSQL."""
        try:
            # D'abord vérifier le cache
            if mission_id in self._steps:
                return self._steps[mission_id]

            async with async_session_maker() as db:
                # Récupérer la mission pour avoir l'ID
                mission_model = await self._get_mission_model(mission_id, db)
                if not mission_model:
                    return []

                query = select(MissionStep).where(MissionStep.mission_id == mission_model.id)
                query = query.order_by(MissionStep.step_order)

                result = await db.execute(query)
                models = result.scalars().all()

                steps = []
                for model in models:
                    step = StepRecord.from_model(model, mission_id)
                    steps.append(step)

                # Mettre à jour le cache
                self._steps[mission_id] = steps

                return steps
        except Exception as e:
            logger.error(f"Failed to get steps: {e}")
            return []

    async def get_step(
        self,
        mission_id: str,
        step_order: int
    ) -> Optional[StepRecord]:
        """Récupérer une étape spécifique."""
        steps = await self.get_steps(mission_id)
        for step in steps:
            if step.step_order == step_order:
                return step
        return None

    async def delete_steps(self, mission_id: str) -> bool:
        """Supprimer toutes les étapes d'une mission."""
        try:
            async with async_session_maker() as db:
                # Récupérer la mission pour avoir l'ID interne
                mission_model = await self._get_mission_model(mission_id, db)
                if not mission_model:
                    return False

                query = delete(MissionStep).where(MissionStep.mission_id == mission_model.id)
                result = await db.execute(query)
                await db.commit()

                # Mettre à jour le cache
                if mission_id in self._steps:
                    del self._steps[mission_id]

                logger.info(f"Steps deleted for mission: {mission_id}")
                return result.rowcount > 0
        except Exception as e:
            logger.error(f"Failed to delete steps: {e}")
            return False

    # =========================================================================
    # EVENTS
    # =========================================================================

    async def save_event(self, event: EventRecord) -> bool:
        """Sauvegarder un événement en PostgreSQL."""
        try:
            async with async_session_maker() as db:
                # Récupérer la mission pour avoir l'ID
                mission_db_id: Optional[int] = None
                if event.mission_id:
                    mission_model = await self._get_mission_model(event.mission_id, db)
                    if mission_model:
                        mission_db_id = mission_model.id

                event_model = MissionEvent(
                    event_id=event.event_id,
                    event_type=event.event_type,
                    mission_id=mission_db_id,
                    data=event.data,
                    metadata=event.metadata,
                    timestamp=_naive_utc(event.timestamp)
                )

                db.add(event_model)
                await db.commit()
                await db.refresh(event_model)

                # Mettre à jour le cache
                self._events.append(event)

                logger.info(f"Event saved to PostgreSQL: {event.event_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to save event: {e}")
            return False

    async def get_events(
        self,
        mission_id: Optional[str] = None,
        limit: int = 100
    ) -> List[EventRecord]:
        """Récupérer les événements depuis PostgreSQL."""
        try:
            async with async_session_maker() as db:
                query = select(MissionEvent)

                if mission_id:
                    # Récupérer la mission pour avoir l'ID
                    mission_model = await self._get_mission_model(mission_id, db)
                    if mission_model:
                        query = query.where(MissionEvent.mission_id == mission_model.id)

                query = query.order_by(desc(MissionEvent.timestamp))
                query = query.limit(limit)

                result = await db.execute(query)
                models = result.scalars().all()

                events = []
                for model in models:
                    event = EventRecord.from_model(
                        model,
                        mission_id=mission_id
                    )
                    events.append(event)

                return events
        except Exception as e:
            logger.error(f"Failed to get events: {e}")
            return []

    async def clear(self) -> None:
        """Effacer toutes les données (DANGER: pour tests uniquement)."""
        try:
            async with async_session_maker() as db:
                await db.execute(delete(MissionStep))
                await db.execute(delete(MissionEvent))
                await db.execute(delete(MissionModel))

                await db.commit()

                # Effacer le cache
                self._missions.clear()
                self._steps.clear()
                self._events.clear()

                logger.warning("All workflow data cleared!")
        except Exception as e:
            logger.error(f"Failed to clear data: {e}")


# =============================================================================
# INSTANCE SINGLETON
# =============================================================================

persistence = WorkflowPersistence()


def get_persistence() -> WorkflowPersistence:
    """Récupérer l'instance singleton de la persistance."""
    return persistence


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

async def persist_mission(mission: MissionRecord) -> bool:
    """Fonction utilitaire pour persister une mission."""
    return await persistence.save_mission(mission)


async def get_mission_by_id(mission_id: str) -> Optional[MissionRecord]:
    """Fonction utilitaire pour récupérer une mission."""
    return await persistence.get_mission(mission_id)
