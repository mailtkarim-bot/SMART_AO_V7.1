#!/bin/bash
# SMART_AO V7 - Script de Mise à Jour des Agents
# =================================================
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

print_header "SMART_AO V7 - Mise à Jour des Agents"

# Recharger les modules Python
print_info "Rechargement des modules Python..."
python3 -c "
import importlib
import sys
from pathlib import Path

# Recharger tous les agents
agents_dir = Path('app/agents')
for agent_file in agents_dir.glob('agent_*.py'):
    module_name = f'app.agents.{agent_file.stem}'
    if module_name in sys.modules:
        importlib.reload(sys.modules[module_name])
        print(f'✅ {module_name} rechargé')
    else:
        print(f'ℹ️ {module_name} pas encore chargé')

# Recharger le registry
if 'app.engines.agent_runtime.registry' in sys.modules:
    importlib.reload(sys.modules['app.engines.agent_runtime.registry'])
    print('✅ Registry rechargé')

# Vérifier le nombre d'agents
from app.engines.agent_runtime.registry import registry
print(f'\\n📊 Agents enregistrés: {registry.stats()[\"total_agents\"]}')
"

print_success "Mise à jour des agents terminée"
