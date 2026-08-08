#!/bin/bash
# SMART_AO V7 - Script de Sauvegarde
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
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="smart_ao_v7_backup_${DATE}.tar.gz"

# Vérifier que nous sommes dans le bon répertoire
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

print_header "SMART_AO V7 - Sauvegarde"

# Créer le répertoire de backup
print_info "Création du répertoire de sauvegarde..."
mkdir -p "$BACKUP_DIR"

# Exclure les fichiers temporaires
print_info "Création de l'archive de sauvegarde..."
tar --exclude='venv' \
    --exclude='.env' \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='backups' \
    --exclude='data' \
    --exclude='logs' \
    -czf "${BACKUP_DIR}/${BACKUP_NAME}" \
    .

print_success "Sauvegarde créée: ${BACKUP_DIR}/${BACKUP_NAME}"

# Vérifier la taille
BACKUP_SIZE=$(du -h "${BACKUP_DIR}/${BACKUP_NAME}" | cut -f1)
print_info "Taille de la sauvegarde: ${BACKUP_SIZE}"

# Nettoyer les anciennes sauvegardes (garder les 7 dernières)
print_info "Nettoyage des anciennes sauvegardes..."
ls -t "${BACKUP_DIR}"/smart_ao_v7_backup_*.tar.gz 2>/dev/null | tail -n +8 | xargs -I {} rm -f {} 2>/dev/null || true

print_header "Sauvegarde terminée"
print_success "Sauvegarde terminée avec succès !"
echo ""
echo "Fichier: ${BACKUP_DIR}/${BACKUP_NAME}"
echo "Pour restaurer: ./restore.sh ${BACKUP_NAME}"
