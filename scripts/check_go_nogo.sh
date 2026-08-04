#!/usr/bin/env bash
# SMART_AO V7 - check_go_nogo.sh
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PASSED=0
FAILED=0
TOTAL=0

echo "============================================================"
echo "SMART_AO V7 - GO/NO-GO VALIDATION"
echo "============================================================"
echo "Project: $PROJECT_ROOT"
echo ""

check() {
    if [ $? -eq 0 ]; then
        echo "PASS: $1"
        ((PASSED++))
    else
        echo "FAIL: $1"
        ((FAILED++))
    fi
    ((TOTAL++))
}

# Structure de base
[ -f "$PROJECT_ROOT/.gitignore" ] && check ".gitignore existe"
[ -f "$PROJECT_ROOT/.env.example" ] && check ".env.example existe"
[ -f "$PROJECT_ROOT/requirements.txt" ] && check "requirements.txt existe"
[ -f "$PROJECT_ROOT/setup.py" ] && check "setup.py existe"
[ -f "$PROJECT_ROOT/docker-compose.yml" ] && check "docker-compose.yml existe"

# Package Python
[ -f "$PROJECT_ROOT/app/__init__.py" ] && check "app/__init__.py existe"
[ -f "$PROJECT_ROOT/app/main.py" ] && check "app/main.py existe"
[ -f "$PROJECT_ROOT/app/agents/__init__.py" ] && check "app/agents/__init__.py existe"
[ -f "$PROJECT_ROOT/app/agents/base_agent.py" ] && check "app/agents/base_agent.py existe"
[ -d "$PROJECT_ROOT/app/engines" ] && check "app/engines/ existe"

# Agents (28 requis)
AGENT_FILES=$(find "$PROJECT_ROOT/app/agents" -maxdepth 1 -name "agent_*.py" | wc -l)
[ "$AGENT_FILES" -ge 28 ] && check "$AGENT_FILES agents trouves"

# Engines V7
[ -d "$PROJECT_ROOT/app/engines/workflow_engine" ] && check "workflow_engine/ existe"
[ -d "$PROJECT_ROOT/app/engines/agent_runtime" ] && check "agent_runtime/ existe"
[ -f "$PROJECT_ROOT/app/engines/agent_runtime/registry.py" ] && check "registry.py existe"
[ -d "$PROJECT_ROOT/app/engines/event_bus" ] && check "event_bus/ existe"
[ -f "$PROJECT_ROOT/app/engines/event_bus/bus.py" ] && check "bus.py existe"

# Modeles et Schemas
[ -f "$PROJECT_ROOT/app/models/mission.py" ] && check "app/models/mission.py existe"
[ -f "$PROJECT_ROOT/app/models/events.py" ] && check "app/models/events.py existe"
[ -f "$PROJECT_ROOT/app/models/__init__.py" ] && check "app/models/__init__.py existe"
[ -f "$PROJECT_ROOT/app/schemas/mission.py" ] && check "app/schemas/mission.py existe"
[ -f "$PROJECT_ROOT/app/schemas/event.py" ] && check "app/schemas/event.py existe"

# Migrations
[ -d "$PROJECT_ROOT/app/alembic/versions" ] && check "alembic/versions/ existe"
[ -f "$PROJECT_ROOT/app/alembic/versions/0017_mission_v7.py" ] && check "0017_mission_v7.py existe"
[ -f "$PROJECT_ROOT/app/alembic/versions/0018_events_v7.py" ] && check "0018_events_v7.py existe"

# Python imports
cd "$PROJECT_ROOT"
python3 -c "from app.agents.base_agent import BaseAgent" 2>/dev/null && check "BaseAgent import OK"
python3 -c "from app.engines.agent_runtime.registry import registry" 2>/dev/null && check "Registry import OK"
python3 -c "from app.engines.workflow_engine.mission import Mission" 2>/dev/null && check "Mission import OK"

echo ""
echo "============================================================"
echo "RESULTATS: $PASSED/$TOTAL passed"
echo "============================================================"
if [ "$FAILED" -eq 0 ]; then
    echo "GO: Structure V7 valide"
    exit 0
else
    echo "NO-GO: $FAILED echecs"
    exit 1
fi
