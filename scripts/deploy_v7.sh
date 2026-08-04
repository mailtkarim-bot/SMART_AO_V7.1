#!/bin/bash
# =============================================================================
# SMART_AO V7 - Script de Déploiement Principal
# =============================================================================
# Usage: bash scripts/deploy_v7.sh [local|docker|cloud|down|status|logs|help]
# Auteur: NOOR - Architecte Principal
# Version: 0.1.0
# Date: 04/08/2026
# 
# EXEMPLES:
#   bash scripts/deploy_v7.sh docker     # Déploiement Docker (recommandé)
#   bash scripts/deploy_v7.sh down       # Arrêter tous les services
#   bash scripts/deploy_v7.sh status     # Voir le statut
#   bash scripts/deploy_v7.sh logs       # Voir les logs
# =============================================================================

set -e

# =============================================================================
# CONFIGURATION GLOBALE
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Fichier de log
LOG_FILE="$PROJECT_ROOT/deploy_$(date +%Y%m%d_%H%M%S).log"

# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] $1" >> "$LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WARN] $1" >> "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $1" >> "$LOG_FILE"
}

log_step() {
    echo -e "${BLUE}================================================================================${NC}"
    echo -e "${BLUE}🎯 $1${NC}"
    echo -e "${BLUE}================================================================================${NC}"
    echo "" >> "$LOG_FILE"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ===== $1 =====" >> "$LOG_FILE"
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 est requis mais non installé"
        log_error "Installez-le avant de continuer."
        exit 1
    fi
    log_info "✅ $1 est installé"
}

# =============================================================================
# FONCTIONS DE DÉPLOIEMENT
# =============================================================================

deploy_local() {
    log_step "Déploiement LOCAL (sans Docker) - Mode développement"
    
    # Vérifier Python
    check_command python3
    check_command pip
    
    log_info "Installation des dépendances..."
    cd "$PROJECT_ROOT"
    
    # Créer un environnement virtuel si inexistant
    if [ ! -d "venv" ]; then
        log_info "Création de l'environnement virtuel..."
        python3 -m venv venv
    fi
    
    # Activer et installer
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    deactivate
    
    log_info "✅ Dépendances installées"
    
    # Exécuter les migrations
    log_info "Exécution des migrations..."
    source venv/bin/activate
    cd "$PROJECT_ROOT"
    python -m app.core.database init_db
    deactivate
    
    log_info "✅ Migrations exécutées"
    log_info ""
    log_info "🚀 Démarrage de l'application..."
    log_info "Appuyez sur Ctrl+C pour arrêter"
    log_info ""
    
    source venv/bin/activate
    cd "$PROJECT_ROOT"
    python app/main.py
}

deploy_docker() {
    log_step "Déploiement DOCKER (avec docker-compose) - RECOMMANDÉ"
    
    cd "$PROJECT_ROOT"
    
    # Vérifier Docker
    check_command docker
    check_command docker-compose
    
    # Vérifier le fichier .env
    if [ ! -f ".env" ]; then
        log_info "Création de .env depuis .env.docker..."
        cp .env.docker .env
        log_warn "⚠️  Modifiez .env pour personnaliser les mots de passe !"
    fi
    
    # Builder l'image
    log_info "Build de l'image Docker..."
    docker-compose build --no-cache 2>&1 | tee -a "$LOG_FILE"
    
    # Démarrer les services
    log_info "Démarrage des services..."
    docker-compose up -d 2>&1 | tee -a "$LOG_FILE"
    
    # Attendre que les services soient prêts
    log_info "Attente des services (30-60 secondes)..."
    sleep 15
    
    # Exécuter les migrations via un conteneur temporaire
    log_info "Exécution des migrations..."
    docker-compose exec app /app/scripts/wait_for_services.sh \
        alembic -c /app/alembic.ini upgrade head 2>&1 | tee -a "$LOG_FILE"
    
    # Valider le déploiement
    validate_deployment
    
    log_info ""
    log_info "🎉 DÉPLOIEMENT DOCKER TERMINÉ !"
    log_info ""
    log_info "📋 Services déployés:"
    log_info "   - Application:  http://localhost:8000"
    log_info "   - PostgreSQL:   localhost:5432 (user: smart_ao)"
    log_info "   - Qdrant:       http://localhost:6333"
    log_info ""
    log_info "🔧 Commandes utiles:"
    log_info "   - Voir les logs:         bash scripts/deploy_v7.sh logs"
    log_info "   - Voir le statut:       bash scripts/deploy_v7.sh status"
    log_info "   - Arrêter tout:         bash scripts/deploy_v7.sh down"
    log_info "   - Vérifier la santé:   bash scripts/health_check.sh docker"
    log_info ""
}

deploy_cloud() {
    log_step "Déploiement CLOUD (VPS/Production)"
    
    cd "$PROJECT_ROOT"
    
    # Vérifier Docker
    check_command docker
    check_command docker-compose
    
    # Vérifier le fichier .env
    if [ ! -f ".env" ]; then
        log_info "Création de .env depuis .env.docker..."
        cp .env.docker .env
        log_warn "⚠️  IMPORTANT: Changez TOUS les mots de passe dans .env pour la production !"
        log_warn "    Exécutez: nano .env"
        log_warn "    Puis relancez ce script."
        exit 1
    fi
    
    # Builder et démarrer
    log_info "Build de l'image Docker..."
    docker-compose build --no-cache 2>&1 | tee -a "$LOG_FILE"
    
    log_info "Démarrage des services..."
    docker-compose up -d 2>&1 | tee -a "$LOG_FILE"
    
    # Attendre les services
    log_info "Attente des services..."
    sleep 20
    
    # Exécuter les migrations
    log_info "Exécution des migrations..."
    docker-compose exec app /app/scripts/wait_for_services.sh \
        alembic -c /app/alembic.ini upgrade head 2>&1 | tee -a "$LOG_FILE"
    
    # Valider le déploiement
    validate_deployment
    
    log_info ""
    log_info "🎉 DÉPLOIEMENT CLOUD TERMINÉ !"
    log_info ""
    log_info "🌐 Accès:"
    log_info "   - Application: http://<VOTRE_IP>:8000"
    log_info "   - PostgreSQL:  <VOTRE_IP>:5432"
    log_info "   - Qdrant:      http://<VOTRE_IP>:6333"
    log_info ""
}

deploy_down() {
    log_step "Arrêt des services"
    
    cd "$PROJECT_ROOT"
    
    if [ -f "docker-compose.yml" ]; then
        log_info "Arrêt des conteneurs Docker..."
        docker-compose down 2>&1 | tee -a "$LOG_FILE"
        log_info "✅ Tous les conteneurs arrêtés"
    else
        log_warn "Aucun docker-compose.yml trouvé"
    fi
    
    log_info ""
    log_info "💀 Tous les services sont arrêtés"
}

deploy_status() {
    log_step "Statut des services"
    
    cd "$PROJECT_ROOT"
    
    if [ -f "docker-compose.yml" ]; then
        echo ""
        docker-compose ps
        echo ""
        log_info "Logs récents:"
        docker-compose logs --tail=20
    else
        log_warn "Aucun docker-compose.yml trouvé"
    fi
}

deploy_logs() {
    log_step "Logs des services (suivi en temps réel)"
    
    cd "$PROJECT_ROOT"
    
    if [ -f "docker-compose.yml" ]; then
        docker-compose logs -f
    else
        log_warn "Aucun docker-compose.yml trouvé"
    fi
}

validate_deployment() {
    log_step "Validation du déploiement"
    
    cd "$PROJECT_ROOT"
    
    local passed=0
    local failed=0
    
    # Vérifier que les conteneurs sont up
    if [ "$(docker-compose ps -q | wc -l)" -eq 0 ]; then
        log_error "Aucun service en cours d'exécution"
        return 1
    fi
    
    # Compter les services healthy
    local healthy=$(docker-compose ps | grep -c "healthy" || echo "0")
    local total=$(docker-compose ps | grep -c "Up" || echo "0")
    
    if [ "$healthy" -eq "$total" ] && [ "$total" -gt 0 ]; then
        log_info "✅ $healthy/$total services sont healthy"
        passed=$((passed + 1))
    else
        log_warn "⚠️  $healthy/$total services sont healthy"
        failed=$((failed + 1))
    fi
    
    # Vérifier que l'application répond
    if curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000/health" | grep -q "200"; then
        log_info "✅ Application répond sur /health"
        passed=$((passed + 1))
    else
        log_warn "⚠️  Application ne répond pas sur /health"
        failed=$((failed + 1))
    fi
    
    # Vérifier PostgreSQL
    if docker-compose ps | grep -q "postgres.*healthy"; then
        log_info "✅ PostgreSQL est healthy"
        passed=$((passed + 1))
    else
        log_warn "⚠️  PostgreSQL n'est pas healthy"
        failed=$((failed + 1))
    fi
    
    # Vérifier Qdrant
    if docker-compose ps | grep -q "qdrant.*healthy"; then
        log_info "✅ Qdrant est healthy"
        passed=$((passed + 1))
    else
        log_warn "⚠️  Qdrant n'est pas healthy"
        failed=$((failed + 1))
    fi
    
    echo ""
    if [ $failed -eq 0 ]; then
        log_info "🎉 VALIDATION RÉUSSIE: $passed/$((passed + failed)) checks passés"
        return 0
    else
        log_error "❌ VALIDATION ÉCHOUÉE: $failed/$((passed + failed)) checks échoués"
        return 1
    fi
}

show_usage() {
    cat <<EOF

${CYAN}🚀 SMART_AO V7 - Script de Déploiement${NC}
${CYAN}=======================================${NC}

${PURPLE}Usage:${NC} bash $0 [COMMANDE] [OPTIONS]

${PURPLE}Commandes disponibles:${NC}

  ${GREEN}local${NC}       - Déploiement local (sans Docker, pour développement)
  ${GREEN}docker${NC}      - Déploiement avec Docker Compose (recommandé)
  ${GREEN}cloud${NC}       - Déploiement sur VPS/Cloud (production)
  ${GREEN}down${NC}        - Arrêter tous les services
  ${GREEN}status${NC}      - Afficher le statut des services
  ${GREEN}logs${NC}        - Afficher les logs des services (suivi)
  ${GREEN}help${NC}        - Afficher cette aide

${PURPLE}Exemples:${NC}

  bash $0 docker          # Déploiement Docker local (recommandé)
  bash $0 down            # Arrêter tous les services
  bash $0 status          # Voir le statut des services
  bash $0 logs            # Voir les logs en temps réel

${PURPLE}Configuration:${NC}

  - Copiez .env.docker en .env et modifiez les mots de passe
  - Pour la production: changez TOUS les mots de passe
  - Les logs sont sauvegardés dans: deploy_*.log

${PURPLE}Prérequis:${NC}

  - Docker 24+ (pour docker-compose)
  - Docker Compose 2+
  - Python 3.12+ (pour déploiement local)

${PURPLE}Documentation:${NC}

  Voir: docs/DEPLOYMENT_GUIDE_V7.md

EOF
}

# =============================================================================
# ANALYSE DES ARGUMENTS
# =============================================================================

# Si aucun argument, afficher l'aide
if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

ACTION="$1"
shift

# =============================================================================
# EXÉCUTION DES COMMANDES
# =============================================================================

case "$ACTION" in
    local)
        deploy_local
        ;;
    docker)
        deploy_docker
        ;;
    cloud)
        deploy_cloud
        ;;
    down)
        deploy_down
        ;;
    status)
        deploy_status
        ;;
    logs)
        deploy_logs
        ;;
    help|--help|-h)
        show_usage
        exit 0
        ;;
    *)
        log_error "Commande inconnue: $ACTION"
        show_usage
        exit 1
        ;;
esac

exit 0
