#!/bin/bash
# Script de validation de Gate 8 (Documentation)
# SMART_AO V7 - Phase 5 Build 9

set -e

echo "=========================================="
echo "Gate 8: Validation Documentation"
echo "=========================================="
echo ""

# Répertoire du projet
PROJECT_DIR="/home/noor/PROJECTS/BTP/SMART_AO_V2/SMART_AO_LAST 4/SMART_AO_V7"
cd "$PROJECT_DIR"

# Compteur d'erreurs
errors=0

# =============================================================================
# VALIDATION DES FICHIERS DE DOCUMENTATION
# =============================================================================

echo "Vérification des fichiers de documentation..."
echo ""

# 1. README.md
if [ -f "README.md" ]; then
    echo "✅ README.md existe"
    lines=$(wc -l < README.md)
    echo "   - Lignes: $lines"
    if [ $lines -ge 500 ]; then
        echo "   - ✅ Contenu complet"
    else
        echo "   - ⚠️ Contenu minimal"
    fi
else
    echo "❌ README.md manque"
    errors=$((errors + 1))
fi

# 2. docs/API_GUIDE_V7.md
if [ -f "docs/API_GUIDE_V7.md" ]; then
    echo "✅ docs/API_GUIDE_V7.md existe"
    lines=$(wc -l < docs/API_GUIDE_V7.md)
    echo "   - Lignes: $lines"
    if [ $lines -ge 500 ]; then
        echo "   - ✅ Contenu complet"
    else
        echo "   - ⚠️ Contenu minimal"
    fi
else
    echo "❌ docs/API_GUIDE_V7.md manque"
    errors=$((errors + 1))
fi

# 3. docs/USER_GUIDE_V7.md
if [ -f "docs/USER_GUIDE_V7.md" ]; then
    echo "✅ docs/USER_GUIDE_V7.md existe"
    lines=$(wc -l < docs/USER_GUIDE_V7.md)
    echo "   - Lignes: $lines"
    if [ $lines -ge 300 ]; then
        echo "   - ✅ Contenu complet"
    else
        echo "   - ⚠️ Contenu minimal"
    fi
else
    echo "❌ docs/USER_GUIDE_V7.md manque"
    errors=$((errors + 1))
fi

# 4. .env.example
if [ -f ".env.example" ]; then
    echo "✅ .env.example existe"
    vars=$(grep -c "^#\|^[A-Z_]*=" .env.example)
    echo "   - Variables: $vars"
else
    echo "❌ .env.example manque"
    errors=$((errors + 1))
fi

# 5. Dockerfile
if [ -f "Dockerfile" ]; then
    echo "✅ Dockerfile existe"
    lines=$(wc -l < Dockerfile)
    echo "   - Lignes: $lines"
else
    echo "❌ Dockerfile manque"
    errors=$((errors + 1))
fi

# 6. docker-compose.yml
if [ -f "docker-compose.yml" ]; then
    echo "✅ docker-compose.yml existe"
    services=$(grep -c "^  [a-z]" docker-compose.yml)
    echo "   - Services: $services"
else
    echo "❌ docker-compose.yml manque"
    errors=$((errors + 1))
fi

# 7. k8s/README.md
if [ -f "k8s/README.md" ]; then
    echo "✅ k8s/README.md existe"
    lines=$(wc -l < k8s/README.md)
    echo "   - Lignes: $lines"
else
    echo "❌ k8s/README.md manque"
    errors=$((errors + 1))
fi

# 8. k8s/namespace.yaml
if [ -f "k8s/namespace.yaml" ]; then
    echo "✅ k8s/namespace.yaml existe"
else
    echo "❌ k8s/namespace.yaml manque"
    errors=$((errors + 1))
fi

# 9. k8s/postgres/
if [ -d "k8s/postgres" ]; then
    files=$(ls -1 k8s/postgres/*.yaml 2>/dev/null | wc -l)
    if [ $files -ge 3 ]; then
        echo "✅ k8s/postgres/ - $files fichiers"
    else
        echo "⚠️ k8s/postgres/ - $files fichiers (minimum 3)"
    fi
else
    echo "❌ k8s/postgres/ manque"
    errors=$((errors + 1))
fi

# 10. Scripts de déploiement
if [ -f "scripts/deploy_staging.sh" ]; then
    echo "✅ scripts/deploy_staging.sh existe"
    if [ -x "scripts/deploy_staging.sh" ]; then
        echo "   - ✅ Exécutable"
    else
        echo "   - ⚠️ Non exécutable"
        chmod +x scripts/deploy_staging.sh
    fi
else
    echo "❌ scripts/deploy_staging.sh manque"
    errors=$((errors + 1))
fi

# =============================================================================
# VALIDATION DU CONTENU
# =============================================================================

echo ""
echo "Validation du contenu des fichiers..."
echo ""

# Vérifier que README.md contient les sections importantes
if grep -Eq "#.*🚀 SMART_AO V7" README.md && \
   grep -Eq "##.*📋 TABLE DES MATIÈRES" README.md && \
   grep -Eq "##.*🏗️ ARCHITECTURE" README.md && \
   grep -Eq "##.*📦 INSTALLATION" README.md && \
   grep -Eq "##.*🚀 API REST" README.md; then
    echo "✅ README.md a toutes les sections requises"
else
    echo "❌ README.md manque des sections"
    errors=$((errors + 1))
fi

# Vérifier que API_GUIDE contient les endpoints
if grep -Ei "##.*📊 ENDPOINTS" docs/API_GUIDE_V7.md && \
   grep -Ei "###.*[Hh]ealth" docs/API_GUIDE_V7.md && \
   grep -Ei "###.*[Aa]gent" docs/API_GUIDE_V7.md && \
   grep -Ei "###.*[Mm]ission" docs/API_GUIDE_V7.md; then
    echo "✅ API_GUIDE_V7.md a tous les endpoints requis"
else
    echo "❌ API_GUIDE_V7.md manque des endpoints"
    errors=$((errors + 1))
fi

# Vérifier que USER_GUIDE contient les cas d'usage
if grep -Ei "##.*🚀.*[Ii]nstallation.*[Rr]apide" docs/USER_GUIDE_V7.md && \
   grep -Ei "##.*⚡.*[Pp]remier.*[Dd]émarrage" docs/USER_GUIDE_V7.md && \
   grep -Ei "##.*💡.*[Cc]as.*[Dd]'[Uu]sage" docs/USER_GUIDE_V7.md; then
    echo "✅ USER_GUIDE_V7.md a tous les cas d'usage requis"
else
    echo "❌ USER_GUIDE_V7.md manque des sections"
    errors=$((errors + 1))
fi

# =============================================================================
# AFFICHAGE DES RÉSULTATS
# =============================================================================

echo ""
echo "=========================================="
if [ $errors -eq 0 ]; then
    echo "✅ Gate 8: VALIDÉ"
    echo "Documentation complète disponible"
    echo "=========================================="
    exit 0
else
    echo "❌ Gate 8: ÉCHEC"
    echo "$errors fichiers manquants ou incomplets"
    echo "=========================================="
    exit 1
fi
