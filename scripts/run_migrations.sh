#!/bin/bash
# SMART_AO V7 - PostgreSQL Migrations Script
# Source: ARCHITECTURE_V7_ENGINE.md §4
# Usage: bash scripts/run_migrations.sh [upgrade|downgrade|check]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "============================================================"
echo "SMART_AO V7 - PostgreSQL Migrations"
echo "============================================================"
echo "Project: $PROJECT_ROOT"
echo ""

# Load environment variables
if [ -f ".env" ]; then
    source .env
fi

# Set default values
export DB_HOST="${DB_HOST:-localhost}"
export DB_PORT="${DB_PORT:-5432}"
export DB_NAME="${DB_NAME:-smart_ao_v7}"
export DB_USER="${DB_USER:-smart_ao}"
export DB_PASSWORD="${DB_PASSWORD:-your_secure_password}"

ACTION="${1:-upgrade}"

echo "Action: $ACTION"
echo "Database: $DB_USER@$DB_HOST:$DB_PORT/$DB_NAME"
echo ""

# Check if alembic is available
if ! command -v alembic &> /dev/null; then
    echo "❌ Error: alembic not found. Install with: pip install alembic"
    exit 1
fi

# Run alembic command
case "$ACTION" in
    upgrade)
        echo "🔄 Upgrading database..."
        alembic -c alembic.ini upgrade head
        ;;
    downgrade)
        echo "🔄 Downgrading database..."
        alembic -c alembic.ini downgrade base
        ;;
    check)
        echo "🔍 Checking database status..."
        alembic -c alembic.ini current
        ;;
    history)
        echo "📜 Migration history..."
        alembic -c alembic.ini history
        ;;
    *)
        echo "❌ Unknown action: $ACTION"
        echo "Usage: $0 [upgrade|downgrade|check|history]"
        exit 1
        ;;
esac

echo ""
echo "✅ Migration $ACTION completed successfully"
