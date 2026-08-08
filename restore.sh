#!/bin/bash
# SMART_AO V7 - Script de Restauration
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

# Configuration
BACKUP_DIR="./backups"
BACKUP_FILE="${1:-$(ls -t "${BACKUP_DIR}"/smart_ao_v7_backup_*.tar.gz 2>/dev/null | head -1)}"

# Vérifier que nous sommes dans le bon répertoire
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

print_header "SMART_AO V7 - Restauration"

# Vérifier que le fichier de backup existe
if [ ! -f "$BACKUP_FILE" ]; then
    print_error "Fichier de backup non trouvé: $BACKUP_FILE"
    echo ""
    echo "Fichiers de backup disponibles dans ${BACKUP_DIR}:"
    ls -la "$BACKUP_DIR"/ 2>/dev/null || echo "Aucun backup trouvé"
    echo ""
    echo "Utilisation: ./restore.sh <fichier_backup.tar.gz>"
    exit 1
fi

print_info "Restauration depuis: $BACKUP_FILE"

# Extraire l'archive
print_info "Extraction de l'archive..."
tar -xzf "$BACKUP_FILE" -C .

print_success "Restauration terminée: $BACKUP_FILE"

# Vérifier l'intégrité
print_info "Vérification de l'intégrité..."
if [ -f "app/agents/base_agent.py" ] && [ -f "app/engines/workflow_engine/mission.py" ]; then
    print_success "Fichiers critiques vérifiés"
else
    print_error "Certains fichiers critiques manquants après restauration"
    exit 1
fi

print_header "Restauration terminée"
print_success "SMART_AO V7 a été restauré avec succès !"
echo ""
echo "Prochaines étapes:"
echo "  1. Copier .env depuis votre backup sûr"
echo "  2. Exécuter: source venv/bin/activate"
echo "  3. Exécuter: pip install -r requirements.txt"
echo "  4. Démarrer: python3 app/main.py"
