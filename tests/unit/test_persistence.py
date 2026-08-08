"""
SMART_AO V7 - test_persistence.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


"""
SMART_AO V7 - Tests Persistence
================================
Tests unitaires pour la persistance.
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timezone

project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

from app.engines.workflow_engine.persistence import WorkflowPersistence, MissionRecord, StepRecord
from app.core.database import Base, engine, async_session_maker
from app.models.project import Project
from sqlalchemy import text


@pytest.fixture(scope="function", autouse=True)
async def setup_database():
    """Crée les tables et un projet de test avant chaque test, puis nettoie les données."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Nettoyer les données et créer un projet de test pour satisfaire la clé étrangère
    async with async_session_maker() as session:
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        
        project = Project(
            project_id="project-001",
            name="Projet Test"
        )
        session.add(project)
        await session.commit()
    
    yield

    # NOTE: On ne dispose PAS l'engine global ici. Les sessions sont
    # maintenant gérées correctement par context manager dans WorkflowPersistence.
    # Disposer l'engine global casserait les tests API qui utilisent TestClient
    # et partagent le même engine.


class TestWorkflowPersistence:
    """Tests de la persistance."""
    
    @pytest.mark.asyncio
    async def test_save_and_get_mission(self):
        """Test de sauvegarde et récupération d'une mission."""
        persistence = WorkflowPersistence()
        
        mission = MissionRecord(
            mission_id="mission-001",
            project_id="project-001",
            mission_type="DCE",
            context={"type": "DCE"},
            status="PENDING",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        assert await persistence.save_mission(mission)
        retrieved = await persistence.get_mission("mission-001")
        assert retrieved is not None
        assert retrieved.mission_id == "mission-001"
    
    @pytest.mark.asyncio
    async def test_list_missions(self):
        """Test de listage des missions."""
        persistence = WorkflowPersistence()
        
        for i in range(3):
            mission = MissionRecord(
                mission_id=f"mission-{i}",
                project_id="project-001",
                mission_type="DCE",
                context={},
                status="PENDING",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            await persistence.save_mission(mission)
        
        missions = await persistence.list_missions()
        assert len(missions) == 3
    
    @pytest.mark.asyncio
    async def test_save_and_get_step(self):
        """Test de sauvegarde et récupération d'une étape."""
        persistence = WorkflowPersistence()
        
        mission = MissionRecord(
            mission_id="mission-001",
            project_id="project-001",
            mission_type="DCE",
            context={},
            status="PENDING",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        await persistence.save_mission(mission)
        
        step = StepRecord(
            step_id="step-001",
            mission_id="mission-001",
            step_name="parser_step",
            step_order=1,
            status="COMPLETED",
            input_data={"status": "ok"},
            output_data={},
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            execution_time_ms=100,
            created_at=datetime.now(timezone.utc)
        )
        
        assert await persistence.save_step(step)
        steps = await persistence.get_steps("mission-001")
        assert len(steps) == 1
        assert steps[0].step_name == "parser_step"
    
    @pytest.mark.asyncio
    async def test_clear(self):
        """Test de l'effacement."""
        persistence = WorkflowPersistence()
        
        mission = MissionRecord(
            mission_id="mission-001",
            project_id="project-001",
            mission_type="DCE",
            context={},
            status="PENDING",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        await persistence.save_mission(mission)
        
        await persistence.clear()
        assert await persistence.get_mission("mission-001") is None
        missions = await persistence.list_missions()
        assert len(missions) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
