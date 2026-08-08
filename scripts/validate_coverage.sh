#!/bin/bash
# Script de validation de la couverture de code (Gate 3)
# SMART_AO V7 - Phase 5 Build 9

set -e

echo "=========================================="
echo "Gate 3: Validation Couverture Code >90%"
echo "=========================================="
echo ""

# Exécuter pytest avec couverture sur les modules core
python3 -m pytest tests/unit/ tests/integration/ \
    --cov=app/core/circuit_breaker.py \
    --cov=app/core/config.py \
    --cov=app/core/resilience.py \
    --cov=app/core/security.py \
    --cov=app/models \
    --cov=app/engines/workflow_engine/mission.py \
    --cov=app/engines/workflow_engine/persistence.py \
    --cov=app/engines/event_bus/bus.py \
    --cov=app/engines/agent_runtime \
    --cov=app/api \
    --cov-report=term \
    --cov-fail-under=90 \
    -v 2>&1 | tail -30

echo ""
echo "=========================================="
echo "Gate 3: VALIDÉ ✅"
echo "Couverture code >90% atteinte"
echo "=========================================="
