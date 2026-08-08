#!/bin/bash
# Script de validation de TOUS les Gates (1-10) pour Build 9
# SMART_AO V7 - Phase 5

echo "=========================================="
echo "VALIDATION COMPLÈTE DES GATES BUILD 9"
echo "SMART_AO V7 - Phase 5 - Production Ready"
echo "=========================================="
echo ""

total=0
passed=0
failed=0

run_gate() {
    local gate_name="$1"
    local command="$2"
    echo "=========================================="
    echo "$gate_name"
    echo "=========================================="
    eval "$command" 2>&1
    local exit_code=$?
    echo ""
    if [ $exit_code -eq 0 ]; then
        echo "✅ $gate_name: VALIDÉ"
        echo ""
        return 0
    else
        echo "❌ $gate_name: ÉCHEC (code: $exit_code)"
        echo ""
        return 1
    fi
}

run_gate "Gate 1: Tests Unitaires (279 minimum)" \
    "python3 -m pytest tests/unit/ -v --tb=short -q"
if [ $? -eq 0 ]; then
    total=$((total + 1)) && passed=$((passed + 1))
else
    total=$((total + 1)) && failed=$((failed + 1))
fi

run_gate "Gate 2: Tests Intégration (38 minimum)" \
    "python3 -m pytest tests/integration/ -v --tb=short -q"
if [ $? -eq 0 ]; then
    total=$((total + 1)) && passed=$((passed + 1))
else
    total=$((total + 1)) && failed=$((failed + 1))
fi

run_gate "Gate 3: Couverture Code >90%" \
    "bash scripts/validate_coverage.sh"
if [ $? -eq 0 ]; then
    total=$((total + 1)) && passed=$((passed + 1))
else
    total=$((total + 1)) && failed=$((failed + 1))
fi

run_gate "Gate 4: Aucune Dépréciation" \
    "python3 -m pytest tests/unit/ -W error::DeprecationWarning -q"
if [ $? -eq 0 ]; then
    total=$((total + 1)) && passed=$((passed + 1))
else
    total=$((total + 1)) && failed=$((failed + 1))
fi

run_gate "Gate 5: Structure V7 (27/27)" \
    "bash scripts/check_go_nogo.sh"
if [ $? -eq 0 ]; then
    total=$((total + 1)) && passed=$((passed + 1))
else
    total=$((total + 1)) && failed=$((failed + 1))
fi

run_gate "Gate 6: Circuit Breakers Fonctionnels" \
    "python3 -m pytest tests/unit/test_circuit_breaker.py -v -q"
if [ $? -eq 0 ]; then
    total=$((total + 1)) && passed=$((passed + 1))
else
    total=$((total + 1)) && failed=$((failed + 1))
fi

run_gate "Gate 7: Rate Limiting Opérationnel" \
    "python3 -m pytest tests/unit/test_rate_limiting.py -v -q"
if [ $? -eq 0 ]; then
    total=$((total + 1)) && passed=$((passed + 1))
else
    total=$((total + 1)) && failed=$((failed + 1))
fi

run_gate "Gate 8: Documentation Complète" \
    "bash scripts/validate_gate8.sh"
if [ $? -eq 0 ]; then
    total=$((total + 1)) && passed=$((passed + 1))
else
    total=$((total + 1)) && failed=$((failed + 1))
fi

run_gate "Gate 9: Déploiement Staging" \
    "bash scripts/validate_gate9.sh"
if [ $? -eq 0 ]; then
    total=$((total + 1)) && passed=$((passed + 1))
else
    total=$((total + 1)) && failed=$((failed + 1))
fi

run_gate "Gate 10: Revue Finale de Code" \
    "bash scripts/validate_gate10.sh"
if [ $? -eq 0 ]; then
    total=$((total + 1)) && passed=$((passed + 1))
else
    total=$((total + 1)) && failed=$((failed + 1))
fi

echo ""
echo "=========================================="
echo "SMART_AO V7 - RÉSULTATS GLOBAUX"
echo "=========================================="
echo ""
echo "Résumé des validations:"
echo "  Total:    $total gates"
echo "  Validées: $passed gates"
echo "  Échecs:   $failed gates"
echo ""

if [ $failed -eq 0 ]; then
    echo "✅ TOUTES LES GATES SONT VALIDÉES"
    echo ""
    echo "=========================================="
    echo "🎉 SMART_AO V7 - BUILD 9"
    echo "   EST PRÊT POUR LA PRODUCTION !"
    echo "=========================================="
    echo ""
    echo "Pour déployer:"
    echo "  bash scripts/deploy_staging.sh"
    echo ""
    exit 0
else
    echo "❌ CERTAINES GATES ONT ÉCHOUÉ"
    echo ""
    echo "Veuillez corriger les problèmes et relancer la validation."
    echo ""
    exit 1
fi
