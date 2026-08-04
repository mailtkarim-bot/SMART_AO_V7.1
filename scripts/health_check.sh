#!/bin/bash
# =============================================================================
# SMART_AO V7 - Health Check Script
# =============================================================================
# Vérifie que tous les services sont opérationnels
# Usage: bash scripts/health_check.sh [docker|local|all]
# Auteur: NOOR - Architecte Principal
# Version: 0.1.0
# Date: 04/08/2026
# 
# EXEMPLES:
#   bash scripts/health_check.sh docker    # Vérifier services Docker
#   bash scripts/health_check.sh local     # Vérifier services locaux
#   bash scripts/health_check.sh          # Auto-détecter le mode
# =============================================================================

set -e

# =============================================================================
# CONFIGURATION
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Compteurs
PASSED=0
FAILED=0
TOTAL=0

# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

check() {
    TOTAL=$((TOTAL + 1))
    if eval "$2"; then
        echo -e "${GREEN}✅${NC} $1"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}❌${NC} $1"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

check_docker() {
    check "Docker est installé" "command -v docker &> /dev/null"
    check "Docker Compose est installé" "command -v docker-compose &> /dev/null"
    check "Docker Daemon est en cours" "docker info &> /dev/null"
}

check_python() {
    check "Python 3.12+ est installé" "command -v python3 &> /dev/null && python3 -c 'import sys; assert sys.version_info >= (3, 12)'"
    check "pip est installé" "command -v pip3 &> /dev/null || command -v pip &> /dev/null"
}

check_docker_services() {
    cd "$PROJECT_ROOT"
    
    # Vérifier que docker-compose.yml existe
    check "docker-compose.yml existe" "[ -f docker-compose.yml ]"
    
    # Vérifier que les conteneurs sont en cours
    local running_containers=$(docker-compose ps -q 2>/dev/null | wc -l)
    check "Services Docker en cours ($running_containers/3)" "[ $running_containers -ge 3 ]"
    
    # Vérifier PostgreSQL healthy
    check "PostgreSQL est healthy" "docker-compose ps 2>/dev/null | grep -q 'postgres.*healthy'"
    
    # Vérifier Qdrant healthy  
    check "Qdrant est healthy" "docker-compose ps 2>/dev/null | grep -q 'qdrant.*healthy'"
    
    # Vérifier App healthy
    check "Application est healthy" "docker-compose ps 2>/dev/null | grep -q 'app.*healthy'"
    
    # Vérifier que l'application répond sur /health
    check "Application répond sur /health" "curl -s -o /dev/null -w '%{http_code}' 'http://localhost:8000/health' | grep -q '200'"
    
    # Vérifier le registre des agents (via conteneur app)
    check "Registre des agents (30 agents)" "docker-compose exec app python3 -c 'from app.engines.agent_runtime.registry import registry; print(len(registry.get_all()))' 2>/dev/null | grep -q '30'"
}

check_local_services() {
    cd "$PROJECT_ROOT"
    
    # Vérifier PostgreSQL local
    check "PostgreSQL est accessible" "pg_isready -h localhost -p 5432 -U smart_ao -d smart_ao_v7 &> /dev/null"
    
    # Vérifier Qdrant local
    check "Qdrant est accessible" "curl -s -o /dev/null -w '%{http_code}' 'http://localhost:6333' | grep -q '200'"
    
    # Vérifier Application locale
    check "Application répond sur /health" "curl -s -o /dev/null -w '%{http_code}' 'http://localhost:8000/health' | grep -q '200'"
    
    # Vérifier le registre des agents
    check "Registre des agents (30 agents)" "python3 -c 'from app.engines.agent_runtime.registry import registry; print(len(registry.get_all()))' 2>/dev/null | grep -q '30'"
}

check_pg_connection() {
    check "Connexion PostgreSQL avec psycopg2" "python3 -c 'import psycopg2; conn = psycopg2.connect(host="localhost", port=5432, dbname="smart_ao_v7", user="smart_ao", password="your_secure_password_change_me"); conn.close()' 2>/dev/null"
}

check_migrations() {
    cd "$PROJECT_ROOT"
    check "Migrations PostgreSQL appliquées" "docker-compose exec app python3 -c 'from app.core.database import engine; from app.models.mission import Base; import asyncio; async def check(): async with engine.begin() as conn: return await conn.run_sync(Base.metadata反射.tables.keys); asyncio.run(check()'" 2>/dev/null
}

# =============================================================================
# AFFICHAGE DES RÉSULTATS
# =============================================================================

print_results() {
    echo ""
    echo -e "${BLUE}================================================================================${NC}"
    echo -e "${BLUE}📊 RÉSULTATS HEALTH CHECK${NC}"
    echo -e "${BLUE}================================================================================${NC}"
    echo -e "${YELLOW}Total: $TOTAL | Réussis: $PASSED | Échoués: $FAILED${NC}"
    echo -e "${YELLOW}Score: $((PASSED * 100 / TOTAL))%${NC}"
    echo -e "${BLUE}================================================================================${NC}"
    
    if [ $FAILED -eq 0 ]; then
        echo -e "${GREEN}🎉 TOUS LES HEALTH CHECKS ONT RÉUSSI !${NC}"
        exit 0
    else
        echo -e "${RED}❌ $FAILED HEALTH CHECKS ONT ÉCHOUÉ${NC}"
        exit 1
    fi
}

# =============================================================================
# DÉTECTION AUTOMATIQUE DU MODE
# =============================================================================

detect_mode() {
    if [ -f "$PROJECT_ROOT/docker-compose.yml" ] && docker-compose ps &> /dev/null; then
        echo "docker"
    elif pg_isready -h localhost -p 5432 &> /dev/null; then
        echo "local"
    else
        echo "none"
    fi
}

# =============================================================================
# PARSING DES ARGUMENTS
# =============================================================================

MODE="${1:-auto}"

# =============================================================================
# EXÉCUTION
# =============================================================================

echo -e "${CYAN}================================================================================${NC}"
echo -e "${CYAN}🚀 SMART_AO V7 - Health Check${NC}"
echo -e "${CYAN}================================================================================${NC}"
echo ""

case "$MODE" in
    docker)
        echo -e "${BLUE}[MODE]${NC} Vérification des services Docker..."
        echo ""
        check_docker
        check_docker_services
        print_results
        ;;
    local)
        echo -e "${BLUE}[MODE]${NC} Vérification des services locaux..."
        echo ""
        check_python
        check_local_services
        print_results
        ;;
    all)
        echo -e "${BLUE}[MODE]${NC} Vérification complète (Docker + Local)..."
        echo ""
        
        # Essayer Docker d'abord
        if check_docker; then
            echo ""
            check_docker_services
        fi
        
        echo ""
        check_python
        check_local_services
        print_results
        ;;
    help|--help|-h)
        echo ""
        echo "Usage: bash $0 [docker|local|all|help]"
        echo ""
        echo "Options:"
        echo "  docker   - Vérifier les services Docker"
        echo "  local    - Vérifier les services locaux"
        echo "  all      - Vérifier Docker + Local"
        echo "  help     - Afficher cette aide"
        echo ""
        exit 0
        ;;
    *)
        # Mode auto
        DETECTED_MODE=$(detect_mode)
        echo -e "${BLUE}[MODE AUTO]${NC} Mode détecté: $DETECTED_MODE"
        echo ""
        
        case "$DETECTED_MODE" in
            docker)
                check_docker
                check_docker_services
                ;;
            local)
                check_python
                check_local_services
                ;;
            *)
                echo -e "${YELLOW}[WARN]${NC} Aucun service détecté. Vérification basique..."
                echo ""
                check_docker
                check_python
                ;;
        esac
        
        print_results
        ;;
esac

exit 0
