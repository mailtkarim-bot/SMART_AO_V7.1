#!/usr/bin/env bash
# SMART_AO V7.1 - check_go_nogo.sh
# Gate bloquant : 39 critères Single VPS avant premier client payant
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PASSED=0
FAILED=0
TOTAL=0

check() {
    local label="$1"
    shift
    if "$@" >/dev/null 2>&1; then
        echo "PASS: $label"
        ((PASSED++)) || true
    else
        echo "FAIL: $label"
        ((FAILED++)) || true
    fi
    ((TOTAL++)) || true
}

check_file() { check "$1 existe" test -f "$PROJECT_ROOT/$2"; }
check_dir()  { check "$1 existe" test -d "$PROJECT_ROOT/$2"; }

echo "============================================================"
echo "SMART_AO V7.1 - GO/NO-GO VALIDATION - 39 Single VPS"
echo "============================================================"
echo "Project: $PROJECT_ROOT"
echo ""

# === Fondations (8) ===
check_file ".gitignore" ".gitignore"
check_file ".env.example" ".env.example"
check_file "requirements.txt" "requirements.txt"
check_file "setup.py" "setup.py"
check_file "docker-compose.yml" "docker-compose.yml"
check_file "app/main.py" "app/main.py"
check_file "app/__init__.py" "app/__init__.py"
check "python3 disponible" command -v python3

# === Structure Core (8) ===
check_dir "app/engines" "app/engines"
check_dir "app/engines/workflow_engine" "app/engines/workflow_engine"
check_dir "app/engines/agent_runtime" "app/engines/agent_runtime"
check_file "app/engines/agent_runtime/registry.py" "app/engines/agent_runtime/registry.py"
check_dir "app/engines/event_bus" "app/engines/event_bus"
check_dir "app/engines/math_engine" "app/engines/math_engine"
check_dir "app/engines/knowledge_engine" "app/engines/knowledge_engine"

# === V7.1 Ajouts techniques (6) ===
check_file "app/engines/event_bus/dlq.py" "app/engines/event_bus/dlq.py"
check_file "app/engines/event_bus/cron_reconciliation.py" "app/engines/event_bus/cron_reconciliation.py"
check_file "app/engines/knowledge_engine/local_llm.py" "app/engines/knowledge_engine/local_llm.py"
check_file "app/engines/knowledge_engine/confidentialite_detector.py" "app/engines/knowledge_engine/confidentialite_detector.py"
check_file "app/engines/knowledge_engine/embedding_engine.py" "app/engines/knowledge_engine/embedding_engine.py"
check_dir "app/engines/fleet_engine" "app/engines/fleet_engine"

# === Modèles & Migrations (4) ===
check_file "app/models/mission.py" "app/models/mission.py"
check_file "app/models/events.py" "app/models/events.py"
check_dir "app/alembic/versions" "app/alembic/versions"
check_file "app/alembic/versions/0017_mission_v7.py" "app/alembic/versions/0017_mission_v7.py"

# === Imports critiques (8) ===
check "Import BaseAgent" python3 -c "from app.agents.base_agent import BaseAgent"
check "Import Registry" python3 -c "from app.engines.agent_runtime.registry import registry"
check "Import Mission" python3 -c "from app.engines.workflow_engine.mission import Mission"
check "Import DLQ" python3 -c "from app.engines.event_bus.dlq import DeadLetterQueue"
check "Import LocalLLM" python3 -c "from app.engines.knowledge_engine.local_llm import LocalLLMClient"
check "Import FleetUpdater" python3 -c "from app.engines.fleet_engine import FleetUpdater"
check "Import ChiffragePulpSolver" python3 -c "from app.engines.math_engine.chiffrage_pulp import ChiffragePulpSolver"
check "Import BGEEmbeddingProvider" python3 -c "from app.engines.knowledge_engine.embedding_engine import BGEEmbeddingProvider"

# === Comptage Agents / Solveurs (2) ===
check "33+ agents enregistrés" python3 -c "
from app.engines.agent_runtime.registry import registry
registry.auto_discover('app.agents')
assert len(registry.get_all()) >= 33, f'{len(registry.get_all())} agents'
"
check "16+ solveurs Math Engine" python3 -c "
import os
root = '$PROJECT_ROOT/app/engines/math_engine'
files = []
for r, _, fs in os.walk(root):
    for f in fs:
        if f.endswith('.py') and f not in ('__init__.py', 'types.py', 'decimal_ops.py'):
            files.append(f)
assert len(files) >= 16, f'{len(files)} solveurs'
"

# === Tests P0 / V7.1 (3) ===
check "Math Engine ZERO LLM" python3 -m pytest "$PROJECT_ROOT/tests/unit/test_math_engine_no_llm_import.py" -q
check "Tests V7.1 modules (5)" python3 -m pytest \
    "$PROJECT_ROOT/tests/unit/test_penibilite_rh.py" \
    "$PROJECT_ROOT/tests/unit/test_vigilance_urssaf.py" \
    "$PROJECT_ROOT/tests/unit/test_zan_trackterres.py" \
    "$PROJECT_ROOT/tests/unit/test_formule_revision.py" \
    "$PROJECT_ROOT/tests/unit/test_sourcing_api.py" -q
check "Tests V7.1 tech (5)" python3 -m pytest \
    "$PROJECT_ROOT/tests/unit/test_local_llm_fallback.py" \
    "$PROJECT_ROOT/tests/unit/test_dlq_reconciliation.py" \
    "$PROJECT_ROOT/tests/unit/test_fleet_update.py" \
    "$PROJECT_ROOT/tests/unit/test_confidentialite_detector.py" \
    "$PROJECT_ROOT/tests/unit/test_math_engine_chiffrage_pulp.py" -q

# === Compilation (1) ===
check "Compilation Python" python3 -m compileall -q "$PROJECT_ROOT/app" "$PROJECT_ROOT/tests"

echo ""
echo "============================================================"
echo "RESULTATS: $PASSED/$TOTAL passed"
echo "============================================================"
if [ "$FAILED" -eq 0 ]; then
    echo "GO: Structure et tests V7.1 valides ($PASSED/$TOTAL)"
    exit 0
else
    echo "NO-GO: $FAILED echecs"
    exit 1
fi
