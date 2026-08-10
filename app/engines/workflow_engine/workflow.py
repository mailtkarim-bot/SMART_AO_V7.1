"""
SMART_AO V7 - workflow.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved

PATCH P0-3: Remplacer persist() simulé par appel à persistence.py
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
import uuid

from app.engines.workflow_engine.mission import Mission, MissionStatus, MissionStep, StepStatus
from app.engines.event_bus.bus import EventBus, Event
from app.engines.agent_runtime.registry import AgentRegistry
from app.agents.base_agent import AgentInput, AgentOutput
from app.engines.workflow_engine.persistence import persistence, MissionRecord, StepRecord

logger = logging.getLogger(__name__)


class WorkflowStep:
    """Représente une étape dans un workflow."""
    def __init__(self, name: str, step_number: int, status: StepStatus = StepStatus.PENDING, step_name: str = None):
        self.name = name
        self.step_name = step_name if step_name is not None else name
        self.step_number = step_number
        self.status = status


class Workflow:
    """
    Représente un workflow pour une mission spécifique.
    Contient les 6 étapes canoniques du workflow V7.
    """
    STANDARD_STEPS = [
        "parser_step",
        "extraction_step",
        "classification_step",
        "agents_step",
        "compilation_step",
        "rapport_step",
    ]

    def __init__(self, mission: Mission):
        self.mission = mission
        self.mission_id = mission.id
        self.status = "PENDING"
        self.current_step = 0
        
        self.steps = []
        for i, step_name in enumerate(self.STANDARD_STEPS):
            step = WorkflowStep(
                name=step_name.upper().replace("_", ""),
                step_name=step_name,
                step_number=i,
                status=StepStatus.PENDING
            )
            self.steps.append(step)

    def get_current_step(self):
        """Récupérer l'étape courante."""
        if 0 <= self.current_step < len(self.steps):
            return self.steps[self.current_step]
        return None

    def advance(self):
        """Avancer à l'étape suivante."""
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1


class WorkflowEngine:
    """
    Tour de contrôle V7 - Kernel OS
    Persistance PG missions + mission_steps via persistence.py
    Parallelisation contrôlée semaphore 6 max pour 16Go RAM
    Gestion des 6 étapes canoniques d'analyse DCE
    """

    def __init__(self, registry: AgentRegistry, event_bus: EventBus, max_parallel: int = 6):
        self.registry = registry
        self.event_bus = event_bus
        self.max_parallel = max_parallel
        logger.info(f"WorkflowEngine initialized max_parallel={max_parallel} - V7 OS")

    async def create_mission(self, docs: List[str], context: Dict[str, Any], created_by: str, project_id: Optional[str] = None, priority: str = "NORMALE") -> Mission:
        mission = Mission(
            documents=docs,
            context=context,
            created_by=created_by,
            project_id=project_id,
            priority=priority,
        )
        await self._persist_mission(mission)
        
        from app.engines.event_bus.models import MissionCreated
        self.event_bus.publish(MissionCreated(
            mission_id=mission.id,
            project_id=project_id,
            mission_type=context.get("mission_type", "UNKNOWN"),
            context=context
        ))
        logger.info(f"Mission {mission.id} created with {len(docs)} docs")
        return mission

    async def _persist_mission(self, mission: Mission) -> bool:
        """
        Persiste une mission en PostgreSQL via persistence.py (P0-3 FIX).
        Convertit Mission (Pydantic) en MissionRecord (dataclass).
        """
        try:
            mission_record = MissionRecord(
                mission_id=mission.id,
                project_id=mission.project_id,
                mission_type=mission.type,
                name=f"Mission {mission.id}",
                description=f"Analyse de {len(mission.documents)} documents",
                context=mission.context,
                status=mission.status.value,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                total_steps=len(mission.workflow),
                completed_steps=mission.current_step_idx,
                error_message=mission.error_message if hasattr(mission, 'error_message') else None,
                extra_metadata={"priority": mission.priority}
            )
            
            result = await persistence.save_mission(mission_record)
            logger.debug(f"Persisted mission {mission.id} to PostgreSQL status={mission.status}")
            return result
        except Exception as e:
            logger.error(f"Failed to persist mission {mission.id}: {e}")
            return False

    async def persist(self, mission: Mission):
        """
        Wrapper pour compatibilité - délègue à _persist_mission.
        En prod: UPSERT PG via persistence.py (P0-3 FIX).
        """
        mission.updated_at = datetime.now(timezone.utc)
        return await self._persist_mission(mission)

    async def _persist_step(self, mission: Mission, step: MissionStep) -> bool:
        """
        Persiste une étape de mission en PostgreSQL via persistence.py.
        """
        try:
            step_record = StepRecord(
                step_id=f"{mission.id}_{step.name}_{datetime.now(timezone.utc).isoformat()}",
                mission_id=mission.id,
                step_name=step.name,
                step_order=mission.current_step_idx,
                status=step.status.value,
                input_data=mission.context.get("input_data", {}),
                output_data=mission.context,
                error_message=step.error,
                started_at=step.started_at,
                completed_at=step.ended_at,
                agent_name=None,
                execution_time_ms=step.duration_ms or 0,
                created_at=datetime.now(timezone.utc)
            )
            
            result = await persistence.save_step(step_record)
            logger.debug(f"Persisted step {step.name} for mission {mission.id} to PostgreSQL")
            return result
        except Exception as e:
            logger.error(f"Failed to persist step {step.name} mission {mission.id}: {e}")
            return False

    async def run(self, mission: Mission) -> Mission:
        """Run complet 6 steps"""
        logger.info(f"Starting Mission {mission.id} workflow 6 steps")
        try:
            for idx, step in enumerate(mission.workflow):
                mission.current_step_idx = idx
                mission.status = self._map_step_to_mission_status(step.name)
                await self.persist(mission)

                try:
                    await self.execute_step(mission, step)
                    step.status = StepStatus.DONE
                    step.ended_at = datetime.now(timezone.utc)
                    await self._persist_step(mission, step)
                    
                    self.event_bus.publish(Event(
                        f"{step.name}Terminé",
                        mission_id=mission.id,
                        payload={"step": step.name, "duration_ms": step.duration_ms},
                        source="WorkflowEngine"
                    ))
                except Exception as e:
                    step.status = StepStatus.FAILED
                    step.error = str(e)
                    step.ended_at = datetime.now(timezone.utc)
                    await self._persist_step(mission, step)
                    logger.error(f"Step {step.name} failed mission {mission.id}: {e}")

                    if self._is_blocking_step(step.name):
                        mission.status = MissionStatus.FAILED
                        await self.persist(mission)
                        self.event_bus.publish(Event(
                            "MissionÉchouée",
                            mission_id=mission.id,
                            payload={"error": str(e), "step": step.name},
                            source="WorkflowEngine"
                        ))
                        raise

                await self.persist(mission)

            mission.status = MissionStatus.DONE
            await self.persist(mission)
            self.event_bus.publish(Event(
                "AnalyseTerminée",
                mission_id=mission.id,
                payload={"total_steps": len(mission.workflow)},
                source="WorkflowEngine"
            ))
            logger.info(f"Mission {mission.id} DONE")
            return mission

        except Exception as e:
            logger.exception(f"Mission {mission.id} FAILED: {e}")
            mission.status = MissionStatus.FAILED
            await self.persist(mission)
            raise

    def _map_step_to_mission_status(self, step_name: str) -> MissionStatus:
        mapping = {
            "PARSER": MissionStatus.PARSING,
            "EXTRACTION": MissionStatus.EXTRACTING,
            "CLASSIFICATION": MissionStatus.CLASSIFYING,
            "AGENTS": MissionStatus.AGENT_RUNNING,
            "COMPILATION": MissionStatus.COMPILING,
            "RAPPORT": MissionStatus.REPORTING,
        }
        return mapping.get(step_name, MissionStatus.CREATED)

    def _is_blocking_step(self, step_name: str) -> bool:
        return step_name in ["PARSER", "CLASSIFICATION"]

    async def execute_step(self, mission: Mission, step: MissionStep):
        """
        Dispatch par step - 6 étapes canoniques V7.1
        PARSER / EXTRACTION / CLASSIFICATION / AGENTS / COMPILATION / RAPPORT
        """
        step.status = StepStatus.RUNNING
        step.started_at = datetime.now(timezone.utc)
        logger.info(f"Executing step {step.name} mission {mission.id}")

        if step.name == "PARSER":
            await self._run_parser(mission, step)
        elif step.name == "EXTRACTION":
            await self._run_extraction(mission, step)
        elif step.name == "CLASSIFICATION":
            await self._run_classification(mission, step)
        elif step.name == "AGENTS":
            await self.run_agents_parallel(mission, step)
        elif step.name == "COMPILATION":
            await self._run_compilation(mission, step)
        elif step.name == "RAPPORT":
            await self._run_rapport(mission, step)
        else:
            raise ValueError(f"Unknown step {step.name}")

    async def _run_parser(self, mission: Mission, step: MissionStep):
        # Simulation avec Document Engine - Ready for production integration
        await asyncio.sleep(0.1)
        mission.context["parsed_pages"] = 412
        self.event_bus.publish(Event(
            "DocumentAnalysé",
            mission_id=mission.id,
            payload={"pages": 412, "duree_parse": "3.2s", "chunks": 1240},
            source="DocumentEngine"
        ))

    async def _run_extraction(self, mission: Mission, step: MissionStep):
        # Simulation avec Knowledge Engine - Ready for production integration
        await asyncio.sleep(0.05)
        mission.context["adn_extracted"] = True
        self.event_bus.publish(Event(
            "EntitésExtraites",
            mission_id=mission.id,
            payload={"traps": 12, "adn_local": "<50km"},
            source="KnowledgeEngine"
        ))

    async def _run_classification(self, mission: Mission, step: MissionStep):
        """
        Classification = décide needed_capabilities
        """
        await asyncio.sleep(0.02)
        needed = [
            "DETECTER_PAB",
            "CHECK_DEADLINE",
            "CHECK_CERTIF",
            "DETECTER_RISQUE_FINANCIER",
            "DETECTER_RISQUE_JURIDIQUE",
        ]
        if "RSE" in str(mission.context):
            needed.append("BOOSTER_RSE")

        mission.context["needed_capabilities"] = needed
        self.event_bus.publish(Event(
            "ClassificationTerminée",
            mission_id=mission.id,
            payload={"needed_capabilities": needed},
            source="WorkflowEngine"
        ))

    async def run_agents_parallel(self, mission: Mission, step: MissionStep):
        """
        Cœur V7 - remplace les 28 if
        1. Demande au Registry qui sait traiter chaque capability
        2. Score can_handle 0-1, filtre <0.2
        3. Tri décroissant pertinence
        4. Exécution parallèle semaphore 6 max (16Go RAM)
        """
        needed_caps: List[str] = mission.context.get("needed_capabilities", [])
        agents_to_run = []
        seen = set()

        for cap in needed_caps:
            found = self.registry.find_by_capability(cap)
            for agent in found:
                if agent.name not in seen:
                    agents_to_run.append(agent)
                    seen.add(agent.name)

        scored = []
        for agent in agents_to_run:
            try:
                score = agent.can_handle(mission)
                if score >= 0.2:
                    scored.append((score, agent))
                else:
                    logger.debug(f"Agent {agent.name} skipped score {score} <0.2")
            except Exception as e:
                logger.warning(f"can_handle failed {agent.name}: {e}")
                scored.append((0.5, agent))

        scored.sort(key=lambda x: x[0], reverse=True)
        agents_sorted = [a for _, a in scored]

        logger.info(f"Mission {mission.id} AGENTS step: {len(agents_sorted)}/{len(agents_to_run)} pertinents sur {len(needed_caps)} capabilities")

        semaphore = asyncio.Semaphore(self.max_parallel)
        results: List[AgentOutput] = []

        async def run_one(agent):
            async with semaphore:
                return await self.run_one_agent(mission, agent)

        try:
            results = await asyncio.wait_for(
                asyncio.gather(*[run_one(a) for a in agents_sorted], return_exceptions=True),
                timeout=step.timeout_seconds
            )
        except asyncio.TimeoutError:
            logger.error(f"AGENTS step timeout {step.timeout_seconds}s mission {mission.id}")
            raise

        agent_outputs: Dict[str, AgentOutput] = {}
        for res in results:
            if isinstance(res, Exception):
                logger.error(f"Agent failed: {res}")
                continue
            if isinstance(res, AgentOutput):
                agent_outputs[res.capability] = res

        mission.context["agent_outputs"] = {k: v.dict() for k, v in agent_outputs.items()}
        mission.context["agents_executed"] = len(agent_outputs)

    async def run_one_agent(self, mission: Mission, agent) -> AgentOutput:
        """
        Exécute un agent avec timeout = estimated_duration *2
        Publie AgentDémarré / AgentTerminé
        """
        timeout = agent.estimated_duration.total_seconds() * 2 + 10

        self.event_bus.publish(Event(
            "AgentDémarré",
            mission_id=mission.id,
            payload={"agent": agent.name, "capabilities": agent.capabilities},
            source="AgentRuntime"
        ))

        start = datetime.now(timezone.utc)
        try:
            agent_input = AgentInput(
                mission_id=mission.id,
                dce_chunks=mission.context.get("dce_chunks", []),
                parsed_docs={"pages": mission.context.get("parsed_pages", 0)},
                context=mission.context,
                previous_outputs=mission.context.get("agent_outputs", {})
            )

            output: AgentOutput = await asyncio.wait_for(
                agent.execute(agent_input),
                timeout=timeout
            )

            output.execution_time_ms = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)

            if output.status == "FAILED" and agent.is_blocking:
                logger.error(f"Blocking agent {agent.name} failed -> Mission FAILED")
                raise RuntimeError(f"Blocking agent {agent.name} failed")

            self.event_bus.publish(Event(
                "AgentTerminé",
                mission_id=mission.id,
                payload={"agent": agent.name, "status": output.status, "confidence": output.confidence},
                source="AgentRuntime"
            ))

            return output

        except asyncio.TimeoutError:
            logger.error(f"Agent {agent.name} timeout {timeout}s mission {mission.id}")
            self.event_bus.publish(Event(
                "AgentTerminé",
                mission_id=mission.id,
                payload={"agent": agent.name, "status": "FAILED", "error": "timeout"},
                source="AgentRuntime"
            ))
            return AgentOutput(
                agent_name=agent.name,
                mission_id=mission.id,
                capability=agent.capabilities[0] if agent.capabilities else "UNKNOWN",
                confidence=0.0,
                status="FAILED",
                findings=[{"error": "timeout"}],
                execution_time_ms=int(timeout*1000)
            )

    async def _run_compilation(self, mission: Mission, step: MissionStep):
        # Simulation avec Math Engine - Ready for production integration
        await asyncio.sleep(0.05)
        mission.context["compilation_done"] = True
        self.event_bus.publish(Event(
            "CompilationTerminée",
            mission_id=mission.id,
            payload={"agents": mission.context.get("agents_executed", 0)},
            source="WorkflowEngine"
        ))

    async def _run_rapport(self, mission: Mission, step: MissionStep):
        # Simulation avec Report Engine - Ready for production integration
        await asyncio.sleep(0.05)
        mission.context["rapport_generated"] = True
        self.event_bus.publish(Event(
            "RapportTerminé",
            mission_id=mission.id,
            payload={"pages": mission.context.get("rapport_pages", 0)},
            source="WorkflowEngine"
        ))
