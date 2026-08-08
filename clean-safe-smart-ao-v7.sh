#!/usr/bin/env bash
# clean-safe-smart-ao-v7.sh - Nettoyage SMART_AO_V7 sans risque
# Supprime UNIQUEMENT le cache et les artefacts régénérables.
# Usage: ./clean-safe-smart-ao-v7.sh

set -u

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT" || exit 1

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  SMART AO V7 - Nettoyage Safe${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Dossier: $PROJECT_ROOT"
echo "Espace libre actuel:"
df -h "$PROJECT_ROOT" | tail -1
echo ""

# 1. Vérif git
echo -e "${YELLOW}[1/4] Vérification git (sécurité)...${NC}"
if [ -d ".git" ]; then
  if ! git diff --quiet || ! git diff --cached --quiet; then
    echo -e "${RED}⚠️  Tu as des modifications non commitées !${NC}"
    git status --short | head -20
    echo ""
    read -p "Continuer quand même ? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
      echo "Annulé. Fais d'abord: git add . && git commit -m 'backup'"
      exit 1
    fi
  else
    echo -e "${GREEN}✓ Git propre, tout ton code source est sauvegardé${NC}"
  fi
else
  echo -e "${YELLOW}Pas de dépôt git détecté, on continue mais fais une copie manuelle si besoin${NC}"
fi
echo ""

# 2. Analyse de ce qui pèse lourd
echo -e "${YELLOW}[2/4] Analyse de ce qui pèse lourd (safe à supprimer)...${NC}"

# Dossiers cibles (whitelist stricte)
declare -a DIR_TARGETS=(
  "venv"
  "build"
  "builds"
  "dist"
  "htmlcov"
  ".pytest_cache"
  ".ruff_cache"
  ".mypy_cache"
  "smart_ao_v7.egg-info"
)

# Fichiers cibles (whitelist stricte)
declare -a FILE_TARGETS=(
  ".coverage"
  "coverage"
)

TO_DELETE_DIRS=()
TO_DELETE_FILES=()
TOTAL_ESTIMATED=0

for p in "${DIR_TARGETS[@]}"; do
  if [ -d "$p" ]; then
    SIZE=$(du -sh "$p" 2>/dev/null | cut -f1)
    echo -e "  📁 ${CYAN}$p${NC}  ->  ${RED}$SIZE${NC}"
    TO_DELETE_DIRS+=("$p")
  fi
done

for p in "${FILE_TARGETS[@]}"; do
  if [ -f "$p" ]; then
    SIZE=$(du -sh "$p" 2>/dev/null | cut -f1)
    echo -e "  📄 ${CYAN}$p${NC}  ->  ${RED}$SIZE${NC}"
    TO_DELETE_FILES+=("$p")
  fi
done

# Compte les __pycache__ récursifs
PYCACHE_COUNT=$(find . -type d -name "__pycache__" 2>/dev/null | wc -l)
if [ "$PYCACHE_COUNT" -gt 0 ]; then
  PYCACHE_SIZE=$(find . -type d -name "__pycache__" -exec du -ch {} + 2>/dev/null | tail -1 | cut -f1)
  echo -e "  📁 ${CYAN}__pycache__/${NC} (x${PYCACHE_COUNT})  ->  ${RED}${PYCACHE_SIZE}${NC}"
fi

# Compte les .pyc récursifs
PYC_COUNT=$(find . -type f -name "*.pyc" 2>/dev/null | wc -l)
if [ "$PYC_COUNT" -gt 0 ]; then
  PYC_SIZE=$(find . -type f -name "*.pyc" -exec du -ch {} + 2>/dev/null | tail -1 | cut -f1)
  echo -e "  📄 ${CYAN}*.pyc${NC} (x${PYC_COUNT})  ->  ${RED}${PYC_SIZE}${NC}"
fi

if [ ${#TO_DELETE_DIRS[@]} -eq 0 ] && [ ${#TO_DELETE_FILES[@]} -eq 0 ] && [ "$PYCACHE_COUNT" -eq 0 ] && [ "$PYC_COUNT" -eq 0 ]; then
  echo -e "${GREEN}Rien à nettoyer, déjà propre !${NC}"
  exit 0
fi
echo ""

# 3. Confirmation
echo -e "${YELLOW}[3/4] Confirmation${NC}"
echo "Ce qui va être supprimé :"
echo "  • Dossiers cache/artefacts listés ci-dessus"
echo "  • Tous les __pycache__/ récursivement"
echo "  • Tous les fichiers *.pyc récursivement"
echo ""
echo -e "${GREEN}Ce qui est PRÉSERVÉ (jamais touché) :${NC}"
echo "  app/  tests/  config/  data/  docs/  k8s/  scripts/  uploads/"
echo "  *.py  *.sh  *.md  *.yml  *.yaml  *.ini  *.txt  Dockerfile*"
echo "  .env*  .git/  .github/  alembic.ini  requirements.txt  setup.py"
echo ""
read -p "Supprimer tout ce cache ? (y/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Annulé."
  exit 0
fi

# 4. Nettoyage
echo ""
echo -e "${YELLOW}[4/4] Nettoyage en cours...${NC}"

# Suppression des dossiers whitelistés
for p in "${TO_DELETE_DIRS[@]}"; do
  # Double sécurité : on ne supprime que si le nom est dans la whitelist
  case "$p" in
    venv|build|builds|dist|htmlcov|.pytest_cache|.ruff_cache|.mypy_cache|smart_ao_v7.egg-info)
      echo -e "  🗑️  Suppression dossier ${RED}$p${NC}..."
      rm -rf "$p"
      ;;
    *)
      echo -e "${RED}  ⛔ Sécurité: refus de supprimer $p (non whitelisté)${NC}"
      ;;
  esac
done

# Suppression des fichiers whitelistés
for p in "${TO_DELETE_FILES[@]}"; do
  case "$p" in
    .coverage|coverage)
      echo -e "  🗑️  Suppression fichier ${RED}$p${NC}..."
      rm -f "$p"
      ;;
    *)
      echo -e "${RED}  ⛔ Sécurité: refus de supprimer $p (non whitelisté)${NC}"
      ;;
  esac
done

# Suppression récursive des __pycache__
if [ "$PYCACHE_COUNT" -gt 0 ]; then
  echo -e "  🗑️  Suppression de ${RED}$PYCACHE_COUNT __pycache__/${NC}..."
  find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
fi

# Suppression récursive des .pyc
if [ "$PYC_COUNT" -gt 0 ]; then
  echo -e "  🗑️  Suppression de ${RED}$PYC_COUNT *.pyc${NC}..."
  find . -type f -name "*.pyc" -delete 2>/dev/null || true
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Terminé !${NC}"
echo -e "${GREEN}========================================${NC}"
df -h "$PROJECT_ROOT" | tail -1
echo ""
echo -e "${BLUE}Taille du projet maintenant :${NC}"
du -sh . 2>/dev/null || echo "Impossible de mesurer"
echo ""
echo -e "${BLUE}Pour tout restaurer quand tu veux recoder :${NC}"
echo "  python3 -m venv venv"
echo "  source venv/bin/activate"
echo "  pip install -r requirements.txt"
echo ""
echo -e "${BLUE}Ton code source est intact dans :${NC}"
echo "  app/  tests/  config/  data/  docs/  k8s/  scripts/  uploads/"
