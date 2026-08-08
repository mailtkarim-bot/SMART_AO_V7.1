#!/bin/bash
# SMART_AO V7 - Script d'Installation
# =====================================
# Auteur: NOOR - Architecte Principal
# Version: 1.0.0
# Date: 06/08/2026
# Build: 9 - Phase: 5

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

function print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

function print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

function print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

function print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Vérifier Python 3.8+
print_header "Vérification des pré-requis"
print_info "Vérification de Python 3.8+..."
if ! python3 --version | grep -q "3\.[891]"; then
    print_error "Python 3.8+ requis. Installation en cours..."
    sudo apt-get update
    sudo apt-get install -y python3.12 python3.12-venv python3-pip
fi
print_success "Python 3.8+ vérifié"

# Vérifier pip
print_info "Vérification de pip..."
if ! pip --version &>/dev/null; then
    print_info "Installation de pip..."
    python3 -m ensurepip --upgrade
fi
print_success "pip vérifié"

# Créer un virtual environment
print_info "Création de l'environnement virtuel..."
python3 -m venv venv
print_success "Environnement virtuel créé"

# Activer l'environnement
print_info "Activation de l'environnement..."
source venv/bin/activate

# Installer les dépendances
print_info "Installation des dépendances (voir requirements.txt)..."
pip install --upgrade pip
pip install -r requirements.txt
print_success "Dépendances installées"

# Vérifier l'installation
print_info "Vérification de l'installation..."
python3 -c "from app.agents.base_agent import BaseAgent; print('✅ BaseAgent import OK')"
python3 -c "from app.engines.workflow_engine.mission import Mission; print('✅ Mission import OK')"
python3 -c "from app.engines.agent_runtime.registry import registry; print('✅ Registry import OK')"

# Exécuter les tests
print_info "Exécution des tests..."
python3 -m pytest tests/unit/ -q --tb=line 2>&1 | tail -5

print_header "Installation terminée"
print_success "SMART_AO V7 est prêt à être utilisé !"
echo ""
echo "Pour démarrer:"
echo "  source venv/bin/activate"
echo "  python3 app/main.py"
echo ""
echo "Pour exécuter les tests:"
echo "  python3 -m pytest tests/unit/ tests/integration/ -v"
