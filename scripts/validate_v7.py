"""
SMART_AO V7 - validate_v7.py
================================
Copyright (c) 2026 NOOR - Architecte Principal
Licence: Proprietary - All Rights Reserved
Auteur: NOOR
Date: 06/08/2026
Build: 9 - Phase: 5
"""


#!/usr/bin/env python3
"""
SMART_AO V7 - REC-013 Validation Production Complète
=====================================================
Source: PLAN_MAITRE_V7_FUSION_COMPLETE.md

Ce script valide l'intégralité du système V7 sans nécessiter PostgreSQL.
Il vérifie :
- Structure du projet
- Imports des modules
- Registre des agents
- Workflow Engine
- Event Bus
- Tous les engines
- Tests unitaires
"""

import sys
import asyncio
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import subprocess


# =============================================================================
# CONFIGURATION
# =============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# =============================================================================
# VALIDATION RESULTS
# =============================================================================

class ValidationResult:
    """Result of a validation check"""
    
    def __init__(self, name: str, passed: bool, message: str = "", details: dict = None):
        self.name = name
        self.passed = passed
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "passed": self.passed,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }


class ValidationReport:
    """Complete validation report"""
    
    def __init__(self, name: str = "REC-013 Validation"):
        self.name = name
        self.results: List[ValidationResult] = []
        self.start_time = datetime.utcnow()
        self.end_time: datetime = None
    
    def add_result(self, result: ValidationResult):
        self.results.append(result)
    
    @property
    def total(self) -> int:
        return len(self.results)
    
    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.passed)
    
    @property
    def failed(self) -> int:
        return self.total - self.passed
    
    @property
    def success_rate(self) -> float:
        return (self.passed / self.total * 100) if self.total > 0 else 0.0
    
    def print_summary(self):
        self.end_time = datetime.utcnow()
        duration = (self.end_time - self.start_time).total_seconds()
        
        print("\n" + "=" * 80)
        print(f"SMART_AO V7 - {self.name}")
        print("=" * 80)
        print(f"Date: {self.start_time.isoformat()}")
        print(f"Duration: {duration:.2f}s")
        print(f"Total: {self.total} | Passed: {self.passed} | Failed: {self.failed}")
        print(f"Success Rate: {self.success_rate:.1f}%")
        print("=" * 80)
        
        # Print detailed results
        for result in self.results:
            status = "✅ PASS" if result.passed else "❌ FAIL"
            print(f"{status} | {result.name}")
            if result.message:
                print(f"     {result.message}")
            if result.details:
                for key, value in result.details.items():
                    print(f"     {key}: {value}")
        
        print("=" * 80)
        
        if self.failed == 0:
            print("🎉 ALL VALIDATIONS PASSED - Production Ready (PostgreSQL pending)")
        else:
            print(f"⚠️  {self.failed} validation(s) failed - Review required")
        print("=" * 80)
        
        return self.failed == 0
    
    def save_report(self, file_path: str):
        """Save report to JSON file"""
        import json
        report_data = {
            "name": self.name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "success_rate": self.success_rate,
            "results": [r.to_dict() for r in self.results],
        }
        with open(file_path, "w") as f:
            json.dump(report_data, f, indent=2, default=str)
        print(f"\n📄 Report saved to: {file_path}")


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def validate_imports() -> ValidationResult:
    """Validate all critical imports"""
    try:
        # Core imports
        from app.core.database import Base, DATABASE_URL, engine, async_session_maker
        from app.engines.workflow_engine.mission import Mission, MissionStatus, MissionStep
        from app.engines.workflow_engine.workflow import WorkflowEngine
        from app.engines.event_bus.bus import EventBus, Event
        from app.engines.agent_runtime.registry import registry, AgentRegistry
        from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
        
        imports = {
            "database": "OK",
            "mission": "OK",
            "workflow_engine": "OK",
            "event_bus": "OK",
            "agent_runtime": "OK",
            "base_agent": "OK",
        }
        return ValidationResult(
            "Core Imports",
            True,
            "All core modules imported successfully",
            imports
        )
    except Exception as e:
        return ValidationResult(
            "Core Imports",
            False,
            f"Import failed: {str(e)}"
        )


def validate_structure() -> ValidationResult:
    """Validate project structure"""
    critical_paths = [
        "app/__init__.py",
        "app/main.py",
        "app/core/__init__.py",
        "app/core/database.py",
        "app/engines/__init__.py",
        "app/engines/workflow_engine/__init__.py",
        "app/engines/workflow_engine/mission.py",
        "app/engines/workflow_engine/workflow.py",
        "app/engines/event_bus/__init__.py",
        "app/engines/event_bus/bus.py",
        "app/engines/agent_runtime/__init__.py",
        "app/engines/agent_runtime/registry.py",
        "app/agents/__init__.py",
        "app/agents/base_agent.py",
        "app/models/__init__.py",
        "app/models/mission.py",
        "app/models/events.py",
        "app/alembic/__init__.py",
        "app/alembic/env.py",
        "scripts/check_go_nogo.sh",
    ]
    
    missing = []
    for path in critical_paths:
        full_path = PROJECT_ROOT / path
        if not full_path.exists():
            missing.append(path)
    
    if missing:
        return ValidationResult(
            "Project Structure",
            False,
            f"Missing files: {missing}"
        )
    else:
        return ValidationResult(
            "Project Structure",
            True,
            f"All {len(critical_paths)} critical paths exist",
            {"checked_paths": len(critical_paths)}
        )


def validate_agents() -> ValidationResult:
    """Validate all agents are importable and registered"""
    try:
        from app.engines.agent_runtime.registry import registry
        
        # Clear and re-discover
        registry.clear()
        registry.auto_discover("app.agents")
        
        agents = registry.get_all()
        stats = registry.stats()
        
        agent_names = [a.name for a in agents[:5]]
        suffix = ["..."] if len(agents) > 5 else []
        return ValidationResult(
            "Agents Registration",
            len(agents) >= 28,
            f"{len(agents)} agents registered",
            {
                "total_agents": len(agents),
                "total_capabilities": stats.get("total_capabilities", 0),
                "agents": agent_names + suffix
            }
        )
    except Exception as e:
        return ValidationResult(
            "Agents Registration",
            False,
            f"Agent validation failed: {str(e)}"
        )


def validate_mission_model() -> ValidationResult:
    """Validate Mission model enum alignment"""
    try:
        from app.engines.workflow_engine.mission import MissionStatus as WF_MissionStatus
        from app.models.mission import MissionStatus as DB_MissionStatus
        
        # Get all status values
        wf_statuses = {s.value for s in WF_MissionStatus}
        db_statuses = {s.value for s in DB_MissionStatus}
        
        # Check alignment
        if wf_statuses == db_statuses:
            return ValidationResult(
                "MissionStatus Alignment",
                True,
                f"Workflow and DB models aligned ({len(wf_statuses)} statuses)",
                {"statuses": sorted(wf_statuses)}
            )
        else:
            missing_in_db = wf_statuses - db_statuses
            extra_in_db = db_statuses - wf_statuses
            return ValidationResult(
                "MissionStatus Alignment",
                False,
                f"Misalignment: missing={missing_in_db}, extra={extra_in_db}"
            )
    except Exception as e:
        return ValidationResult(
            "MissionStatus Alignment",
            False,
            f"Alignment check failed: {str(e)}"
        )


def validate_workflow() -> ValidationResult:
    """Validate WorkflowEngine initialization"""
    try:
        from app.engines.workflow_engine.workflow import WorkflowEngine
        from app.engines.agent_runtime.registry import registry
        from app.engines.event_bus.bus import event_bus
        
        # Try to instantiate
        workflow = WorkflowEngine(
            registry=registry,
            event_bus=event_bus,
            max_parallel=6
        )
        
        return ValidationResult(
            "WorkflowEngine Initialization",
            True,
            "WorkflowEngine instantiated successfully",
            {"max_parallel": 6}
        )
    except Exception as e:
        return ValidationResult(
            "WorkflowEngine Initialization",
            False,
            f"Initialization failed: {str(e)}"
        )


def validate_event_bus() -> ValidationResult:
    """Validate EventBus"""
    try:
        from app.engines.event_bus.bus import EventBus, Event
        from app.engines.event_bus.models import EventType
        
        # Try to create event
        event = Event(
            type="TestEvent",
            mission_id="test-mission",
            payload={"test": True},
            source="Validation"
        )
        
        return ValidationResult(
            "EventBus",
            True,
            "EventBus and Event model working",
            {"event_type": event.type, "mission_id": event.mission_id}
        )
    except Exception as e:
        return ValidationResult(
            "EventBus",
            False,
            f"EventBus validation failed: {str(e)}"
        )


def validate_engines_discovery() -> ValidationResult:
    """Validate all engines are discoverable"""
    engines = [
        "workflow_engine",
        "agent_runtime",
        "event_bus",
        "math_engine",
        "knowledge_engine",
        "document_engine",
        "security_engine",
        "notification_engine",
        "api_gateway",
        "ui_engine",
    ]
    
    failed = []
    for engine in engines:
        try:
            __import__(f"app.engines.{engine}")
        except ImportError as e:
            failed.append(f"{engine}: {str(e)}")
    
    if failed:
        return ValidationResult(
            "Engines Discovery",
            False,
            f"Failed to import: {failed}"
        )
    else:
        return ValidationResult(
            "Engines Discovery",
            True,
            f"All {len(engines)} engines imported successfully",
            {"engines": engines}
        )


# =============================================================================
# EXTERNAL VALIDATIONS
# =============================================================================

def validate_check_go_nogo() -> ValidationResult:
    """Validate check_go_nogo.sh script"""
    try:
        result = subprocess.run(
            ["bash", str(PROJECT_ROOT / "scripts" / "check_go_nogo.sh")],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            # Count passed checks
            passed_count = result.stdout.count("PASS")
            total_count = result.stdout.count("PASS") + result.stdout.count("FAIL")
            
            return ValidationResult(
                "check_go_nogo.sh",
                True,
                f"All checks passed ({passed_count}/{total_count})",
                {"passed": passed_count, "total": total_count}
            )
        else:
            return ValidationResult(
                "check_go_nogo.sh",
                False,
                f"Script failed with code {result.returncode}",
                {"stderr": result.stderr[:200]}
            )
    except Exception as e:
        return ValidationResult(
            "check_go_nogo.sh",
            False,
            f"Validation failed: {str(e)}"
        )


def validate_pip_install() -> ValidationResult:
    """Validate pip install ."""
    try:
        result = subprocess.run(
            ["pip", "install", ".", "--dry-run"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # --dry-run might not be supported, try without
        if "--dry-run" in result.stderr or result.returncode != 0:
            result = subprocess.run(
                ["python", "setup.py", "check"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=30
            )
        
        if result.returncode == 0:
            return ValidationResult(
                "pip install .",
                True,
                "Package configuration is valid",
                {}
            )
        else:
            return ValidationResult(
                "pip install .",
                False,
                f"Package check failed: {result.stderr[:200]}"
            )
    except Exception as e:
        return ValidationResult(
            "pip install .",
            False,
            f"Validation failed: {str(e)}"
        )


def validate_run_test() -> ValidationResult:
    """Validate run_test.py"""
    try:
        result = subprocess.run(
            ["python", str(PROJECT_ROOT / "run_test.py")],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and "TOUS LES TESTS RÉUSSIS" in result.stdout:
            return ValidationResult(
                "run_test.py",
                True,
                "All run_test.py checks passed",
                {}
            )
        else:
            return ValidationResult(
                "run_test.py",
                False,
                f"run_test.py failed or didn't complete",
                {"stdout": result.stdout[:200], "stderr": result.stderr[:200]}
            )
    except Exception as e:
        return ValidationResult(
            "run_test.py",
            False,
            f"Validation failed: {str(e)}"
        )


def validate_pytest() -> ValidationResult:
    """Validate pytest tests"""
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/unit/", "-v", "--tb=short"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Parse results
        passed = result.stdout.count(" PASSED")
        failed = result.stdout.count(" FAILED")
        total = passed + failed
        
        return ValidationResult(
            "pytest Tests",
            failed == 0,
            f"{passed}/{total} tests passed",
            {"passed": passed, "failed": failed, "total": total}
        )
    except Exception as e:
        return ValidationResult(
            "pytest Tests",
            False,
            f"Test execution failed: {str(e)}"
        )


# =============================================================================
# MAIN VALIDATION
# =============================================================================

def run_validation() -> ValidationReport:
    """Run all validations"""
    report = ValidationReport("REC-013 - Validation Production Complète")
    
    print("\n" + "=" * 80)
    print("🚀 DEMARRAGE VALIDATION REC-013")
    print("=" * 80)
    
    # Internal validations
    print("\n🔍 Validations Internes...")
    report.add_result(validate_structure())
    report.add_result(validate_imports())
    report.add_result(validate_mission_model())
    report.add_result(validate_agents())
    report.add_result(validate_workflow())
    report.add_result(validate_event_bus())
    report.add_result(validate_engines_discovery())
    
    # External validations
    print("\n🔍 Validations Externes...")
    report.add_result(validate_check_go_nogo())
    report.add_result(validate_pip_install())
    report.add_result(validate_run_test())
    report.add_result(validate_pytest())
    
    return report


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    report = run_validation()
    success = report.print_summary()
    
    # Save report
    report_dir = PROJECT_ROOT / "docs" / "current"
    report_dir.mkdir(parents=True, exist_ok=True)
    report.save_report(report_dir / "validation_rec013_report.json")
    
    # Exit code
    sys.exit(0 if success else 1)
