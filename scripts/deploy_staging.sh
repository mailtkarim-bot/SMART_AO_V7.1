#!/bin/bash
# Script de déploiement Staging pour SMART_AO V7
# Build 9 - Phase 5 - Gate 9

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =============================================================================
# FONCTIONS D'AFFICHAGE
# =============================================================================

function print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

function print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

function print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

function print_error() {
    echo -e "${RED}❌ $1${NC}"
}

function print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

# =============================================================================
# FONCTIONS DE VÉRIFICATION
# =============================================================================

function check_command() {
    if ! command -v "$1" &> /dev/null; then
        print_error "La commande '$1' n'est pas installée. Installation en cours..."
        install_dependency "$1"
    fi
}

function install_dependency() {
    local cmd="$1"
    case "$cmd" in
        docker)
            print_info "Installation de Docker..."
            curl -fsSL https://get.docker.com | sh
            ;;
        docker-compose)
            print_info "Installation de Docker Compose..."
            sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
            sudo chmod +x /usr/local/bin/docker-compose
            ;;
        kubectl)
            print_info "Installation de kubectl..."
            sudo apt-get update && sudo apt-get install -y kubectl
            ;;
        helm)
            print_info "Installation de Helm..."
            curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
            ;;
        *)
            print_error "Installation manuelle requise pour $cmd"
            exit 1
            ;;
    esac
}

function check_docker() {
    if ! docker --version &> /dev/null; then
        print_error "Docker n'est pas installé ou n'est pas en cours d'exécution"
        exit 1
    fi
}

function check_docker_compose() {
    if ! docker-compose --version &> /dev/null; then
        print_error "Docker Compose n'est pas installé"
        exit 1
    fi
}

# =============================================================================
# FONCTIONS DE DÉPLOIEMENT
# =============================================================================

function deploy_docker_local() {
    print_header "Déploiement Local avec Docker Compose"
    
    print_info "Vérification des pré-requis..."
    check_docker
    check_docker_compose
    
    print_info "Changement de répertoire vers SMART_AO_V7..."
    cd /home/noor/PROJECTS/BTP/SMART_AO_V2/SMART_AO_LAST\ 4/SMART_AO_V7
    
    print_info "Création du fichier .env si inexistant..."
    if [ ! -f .env ]; then
        cp .env.example .env
        print_warning "Le fichier .env a été créé depuis .env.example. Veuillez le configurer avant de démarrer."
    fi
    
    print_info "Construction des images Docker..."
    docker-compose build --no-cache
    
    print_info "Démarrage des conteneurs..."
    docker-compose up -d
    
    print_info "Vérification du statut des conteneurs..."
    sleep 30
    docker-compose ps
    
    print_info "Attente que les services soient prêts..."
    sleep 60
    
    print_info "Vérification du health check..."
    local max_retries=10
    local retry=0
    local success=false
    
    while [ $retry -lt $max_retries ]; do
        if curl -s http://localhost:8000/api/v1/health | grep -q "healthy"; then
            success=true
            break
        fi
        sleep 10
        retry=$((retry + 1))
    done
    
    if [ "$success" = true ]; then
        print_success "Déploiement local réussi !"
        print_success "Application disponible à : http://localhost:8000"
        print_success "API Docs disponibles à : http://localhost:8000/docs"
    else
        print_error "Le déploiement a échoué. Veuillez vérifier les logs."
        docker-compose logs
        exit 1
    fi
}

function deploy_docker_production() {
    print_header "Déploiement Production avec Docker"
    
    print_info "Vérification des pré-requis..."
    check_docker
    check_docker_compose
    
    print_info "Changement de répertoire..."
    cd /home/noor/PROJECTS/BTP/SMART_AO_V2/SMART_AO_LAST\ 4/SMART_AO_V7
    
    print_info "Création du fichier .env pour production..."
    if [ ! -f .env ]; then
        cp .env.example .env
        # Configurer pour la production
        sed -i 's/APP_ENVIRONMENT=development/APP_ENVIRONMENT=production/' .env
        sed -i 's/APP_DEBUG=True/APP_DEBUG=False/' .env
        sed -i 's/API_RELOAD=True/API_RELOAD=False/' .env
        sed -i 's/CORS_ORIGINS=.*/CORS_ORIGINS=https:\/\/votre-domaine.com/' .env
    fi
    
    print_info "Construction des images avec tag production..."
    docker build -t smart-ao-v7:9.0.0 .
    
    print_info "Démarrage avec docker-compose en mode production..."
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
    
    print_success "Déploiement production démarré !"
    print_info "Application disponible à : https://votre-domaine.com"
}

function stop_deployment() {
    print_header "Arrêt du déploiement"
    
    cd /home/noor/PROJECTS/BTP/SMART_AO_V2/SMART_AO_LAST\ 4/SMART_AO_V7
    
    print_info "Arrêt des conteneurs..."
    docker-compose down
    
    print_info "Suppression des volumes (optionnel)..."
    read -p "Voulez-vous supprimer les volumes de données ? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down -v
        print_success "Volumes supprimés"
    fi
    
    print_success "Déploiement arrêté"
}

function show_status() {
    print_header "Statut du déploiement"
    
    cd /home/noor/PROJECTS/BTP/SMART_AO_V2/SMART_AO_LAST\ 4/SMART_AO_V7
    
    print_info "Statut des conteneurs :"
    docker-compose ps
    
    print_info ""
    print_info "Logs récents :"
    docker-compose logs --tail=50
}

function show_logs() {
    print_header "Affichage des logs"
    
    cd /home/noor/PROJECTS/BTP/SMART_AO_V2/SMART_AO_LAST\ 4/SMART_AO_V7
    
    read -p "Voulez-vous suivre les logs en temps réel ? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose logs -f
    else
        docker-compose logs --tail=100
    fi
}

function validate_deployment() {
    print_header "Validation du déploiement (Gate 9)"
    
    cd /home/noor/PROJECTS/BTP/SMART_AO_V2/SMART_AO_LAST\ 4/SMART_AO_V7
    
    local errors=0
    
    print_info "Vérification 1 : Conteneurs en cours d'exécution..."
    if docker-compose ps | grep -q "Up"; then
        print_success "Tous les conteneurs sont en cours d'exécution"
    else
        print_error "Certains conteneurs ne sont pas en cours d'exécution"
        errors=$((errors + 1))
    fi
    
    print_info "Vérification 2 : Health check de l'API..."
    if curl -s http://localhost:8000/api/v1/health | grep -q "healthy"; then
        print_success "Health check réussi"
    else
        print_error "Health check échoué"
        errors=$((errors + 1))
    fi
    
    print_info "Vérification 3 : Connexion à PostgreSQL..."
    if docker-compose exec postgres pg_isready &> /dev/null; then
        print_success "PostgreSQL est accessible"
    else
        print_error "PostgreSQL n'est pas accessible"
        errors=$((errors + 1))
    fi
    
    print_info "Vérification 4 : Connexion à Qdrant..."
    if curl -s http://localhost:6333 | grep -q "Qdrant"; then
        print_success "Qdrant est accessible"
    else
        print_error "Qdrant n'est pas accessible"
        errors=$((errors + 1))
    fi
    
    print_info "Vérification 5 : Connexion à Redis..."
    if docker-compose exec redis redis-cli ping &> /dev/null; then
        print_success "Redis est accessible"
    else
        print_error "Redis n'est pas accessible"
        errors=$((errors + 1))
    fi
    
    print_info ""
    if [ $errors -eq 0 ]; then
        print_success "✅ Gate 9 : VALIDÉ - Déploiement staging réussi"
        exit 0
    else
        print_error "❌ Gate 9 : ÉCHEC - $errors vérifications échouées"
        exit 1
    fi
}

# =============================================================================
# MENU PRINCIPAL
# =============================================================================

function show_menu() {
    clear
    print_header "SMART_AO V7 - Déploiement Staging (Gate 9)"
    echo ""
    echo "Sélectionnez une option :"
    echo ""
    echo "  1. 🚀 Déploiement Local (Docker Compose)"
    echo "  2. 🏭 Déploiement Production"
    echo "  3. ⏹️ Arrêter le déploiement"
    echo "  4. 📊 Statut du déploiement"
    echo "  5. 📝 Afficher les logs"
    echo "  6. ✅ Valider le déploiement (Gate 9)"
    echo "  7. ❌ Quitter"
    echo ""
    echo -n "Votre choix [1-7] : "
}

# =============================================================================
# PROGRAMME PRINCIPAL
# =============================================================================

print_header "SMART_AO V7 - Script de Déploiement Staging"
print_info "Build 9 - Phase 5 - Validation Gate 9"
echo ""

while true; do
    show_menu
    read choice
    echo ""
    
    case $choice in
        1) deploy_docker_local ;;
        2) deploy_docker_production ;;
        3) stop_deployment ;;
        4) show_status ;;
        5) show_logs ;;
        6) validate_deployment ;;
        7) 
            print_info "Au revoir !"
            exit 0
            ;;
        *)
            print_error "Option invalide. Veuillez réessayer."
            ;;
    esac
    
    echo ""
    read -p "Appuyez sur Entrée pour continuer..." -n 1 -r
    echo ""
done
