#!/bin/bash
# =============================================================================
# SMART_AO V7 - Wait for Services Script
# =============================================================================
# Attend que PostgreSQL et Qdrant soient prêts avant de démarrer l'application.
# Utilisé comme entrypoint dans docker-compose.yml
# Auteur: NOOR - Architecte Principal
# Version: 0.1.0
# Date: 04/08/2026
# =============================================================================

set -e

# =============================================================================
# CONFIGURATION
# =============================================================================

# Variables d'environnement avec valeurs par défaut
DB_HOST="${DB_HOST:-postgres}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-smart_ao_v7}"
DB_USER="${DB_USER:-smart_ao}"
DB_PASSWORD="${DB_PASSWORD:-your_secure_password_change_me}"

QDRANT_HOST="${QDRANT_HOST:-qdrant}"
QDRANT_PORT="${QDRANT_PORT:-6333}"

# Timeout maximal (en secondes)
MAX_RETRIES=30
RETRY_INTERVAL=5

# =============================================================================
# FONCTIONS
# =============================================================================

log_info() {
    echo "[WAIT] $1"
}

log_error() {
    echo "[ERROR] $1" >&2
}

check_postgres() {
    local retry=0
    
    log_info "Attente de PostgreSQL ($DB_HOST:$DB_PORT)..."
    
    while ! python3 -c "
import psycopg2
import os
import time

try:
    conn = psycopg2.connect(
        host=os.environ.get('DB_HOST', '$DB_HOST'),
        port=int(os.environ.get('DB_PORT', $DB_PORT)),
        dbname=os.environ.get('DB_NAME', '$DB_NAME'),
        user=os.environ.get('DB_USER', '$DB_USER'),
        password=os.environ.get('DB_PASSWORD', '$DB_PASSWORD')
    )
    conn.close()
    print('PostgreSQL est prêt')
    exit(0)
except Exception as e:
    print(f'PostgreSQL non prêt: {e}')
    exit(1)
" 2>/dev/null; do
        
        retry=$((retry + 1))
        
        if [ $retry -ge $MAX_RETRIES ]; then
            log_error "Timeout: PostgreSQL n'est pas prêt après $MAX_RETRIES tentatives"
            exit 1
        fi
        
        log_info "PostgreSQL non prêt, réessai $retry/$MAX_RETRIES..."
        sleep $RETRY_INTERVAL
    done
    
    log_info "✅ PostgreSQL est prêt"
}

check_qdrant() {
    local retry=0
    
    log_info "Attente de Qdrant ($QDRANT_HOST:$QDRANT_PORT)..."
    
    while ! curl -s -o /dev/null -w "%{http_code}" "http://$QDRANT_HOST:$QDRANT_PORT" | grep -q "200"; do
        retry=$((retry + 1))
        
        if [ $retry -ge $MAX_RETRIES ]; then
            log_error "Timeout: Qdrant n'est pas prêt après $MAX_RETRIES tentatives"
            exit 1
        fi
        
        log_info "Qdrant non prêt, réessai $retry/$MAX_RETRIES..."
        sleep $RETRY_INTERVAL
    done
    
    log_info "✅ Qdrant est prêt"
}

run_migrations() {
    log_info "Exécution des migrations Alembic..."
    
    if command -v alembic &> /dev/null; then
        cd /app
        alembic -c alembic.ini upgrade head 2>&1 | while read -r line; do
            log_info "$line"
        done
        log_info "✅ Migrations Alembic terminées"
    else
        log_info "⚠️  Alembic non installé,skip des migrations"
    fi
}

# =============================================================================
# EXÉCUTION
# =============================================================================

log_info "Démarrage du script d'attente des services..."
log_info "Timeout maximal: $((MAX_RETRIES * RETRY_INTERVAL)) secondes"

# Vérifier PostgreSQL
check_postgres

# Vérifier Qdrant
check_qdrant

# Exécuter les migrations de base de données
run_migrations

log_info "✅ Tous les services sont prêts !"
log_info "✅ Migrations exécutées !"
log_info "Démarrage de la commande principale..."

# Exécuter la commande principale (passée en arguments)
exec "$@"
