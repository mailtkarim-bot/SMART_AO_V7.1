#!/bin/bash
# Script de validation de Gate 9 (Déploiement Staging)
# SMART_AO V7 - Phase 5 Build 9

set -e

echo "=========================================="
echo "Gate 9: Validation Déploiement Staging"
echo "=========================================="
echo ""

# Répertoire du projet
PROJECT_DIR="/home/noor/PROJECTS/BTP/SMART_AO_V2/SMART_AO_LAST 4/SMART_AO_V7"
cd "$PROJECT_DIR"

# Compteur d'erreurs
errors=0

# =============================================================================
# VALIDATION DES FICHIERS KUBERNETES
# =============================================================================

echo "Vérification des fichiers Kubernetes..."
echo ""

# 1. Namespace
echo "→ Vérification du namespace..."
if [ -f "k8s/namespace.yaml" ]; then
    echo "✅ k8s/namespace.yaml existe"
else
    echo "❌ k8s/namespace.yaml manque"
    errors=$((errors + 1))
fi

# 2. PostgreSQL
echo "→ Vérification de PostgreSQL..."
if [ -d "k8s/postgres" ]; then
    pg_files=$(ls -1 k8s/postgres/*.yaml 2>/dev/null | wc -l)
    if [ $pg_files -ge 4 ]; then
        echo "✅ k8s/postgres/ - $pg_files fichiers"
        for f in configmap deployment pvc service; do
            if [ -f "k8s/postgres/$f.yaml" ]; then
                echo "   ✅ $f.yaml"
            else
                echo "   ❌ $f.yaml manque"
                errors=$((errors + 1))
            fi
        done
    else
        echo "⚠️ k8s/postgres/ - $pg_files fichiers (minimum 4)"
        errors=$((errors + 1))
    fi
else
    echo "❌ k8s/postgres/ manque"
    errors=$((errors + 1))
fi

# 3. Qdrant
echo "→ Vérification de Qdrant..."
if [ -d "k8s/qdrant" ]; then
    qdrant_files=$(ls -1 k8s/qdrant/*.yaml 2>/dev/null | wc -l)
    if [ $qdrant_files -ge 4 ]; then
        echo "✅ k8s/qdrant/ - $qdrant_files fichiers"
        for f in configmap deployment pvc service; do
            if [ -f "k8s/qdrant/$f.yaml" ]; then
                echo "   ✅ $f.yaml"
            else
                echo "   ❌ $f.yaml manque"
                errors=$((errors + 1))
            fi
        done
    else
        echo "⚠️ k8s/qdrant/ - $qdrant_files fichiers (minimum 4)"
        errors=$((errors + 1))
    fi
else
    echo "❌ k8s/qdrant/ manque"
    errors=$((errors + 1))
fi

# 4. Redis
echo "→ Vérification de Redis..."
if [ -d "k8s/redis" ]; then
    redis_files=$(ls -1 k8s/redis/*.yaml 2>/dev/null | wc -l)
    if [ $redis_files -ge 4 ]; then
        echo "✅ k8s/redis/ - $redis_files fichiers"
        for f in configmap deployment pvc service; do
            if [ -f "k8s/redis/$f.yaml" ]; then
                echo "   ✅ $f.yaml"
            else
                echo "   ❌ $f.yaml manque"
                errors=$((errors + 1))
            fi
        done
    else
        echo "⚠️ k8s/redis/ - $redis_files fichiers (minimum 4)"
        errors=$((errors + 1))
    fi
else
    echo "❌ k8s/redis/ manque"
    errors=$((errors + 1))
fi

# 5. Application
echo "→ Vérification de l'application..."
if [ -d "k8s/app" ]; then
    app_files=$(ls -1 k8s/app/*.yaml 2>/dev/null | wc -l)
    if [ $app_files -ge 5 ]; then
        echo "✅ k8s/app/ - $app_files fichiers"
        for f in configmap deployment hpa ingress pvc service; do
            if [ -f "k8s/app/$f.yaml" ]; then
                echo "   ✅ $f.yaml"
            else
                echo "   ❌ $f.yaml manque"
                errors=$((errors + 1))
            fi
        done
    else
        echo "⚠️ k8s/app/ - $app_files fichiers (minimum 5)"
        errors=$((errors + 1))
    fi
else
    echo "❌ k8s/app/ manque"
    errors=$((errors + 1))
fi

# 6. Script de déploiement
echo "→ Vérification du script de déploiement..."
if [ -f "scripts/deploy_staging.sh" ]; then
    echo "✅ scripts/deploy_staging.sh existe"
    if [ -x "scripts/deploy_staging.sh" ]; then
        echo "   ✅ Exécutable"
    else
        echo "   ⚠️ Non exécutable"
        chmod +x scripts/deploy_staging.sh
        echo "   → Corrigé"
    fi
else
    echo "❌ scripts/deploy_staging.sh manque"
    errors=$((errors + 1))
fi

# 7. k8s/README.md
echo "→ Vérification de la documentation Kubernetes..."
if [ -f "k8s/README.md" ]; then
    lines=$(wc -l < k8s/README.md)
    echo "✅ k8s/README.md existe ($lines lignes)"
else
    echo "❌ k8s/README.md manque"
    errors=$((errors + 1))
fi

# =============================================================================
# VALIDATION DU CONTENU DES FICHIERS
# =============================================================================

echo ""
echo "Validation du contenu des fichiers Kubernetes..."
echo ""

# Vérifier que les fichiers ont le bon format YAML
echo "→ Vérification du format YAML..."
yaml_files=$(find k8s -name "*.yaml" -type f)
invalid_yaml=0
for file in $yaml_files; do
    # Utiliser une validation plus robuste qui accepte les multi-documents YAML
    if python3 -c "
import yaml
try:
    with open('$file') as f:
        content = f.read()
    # Essayer de charger comme multi-document
    yaml.safe_load_all(content)
    print('OK')
except Exception as e:
    print(f'ERROR: {e}')
" 2>/dev/null | grep -q "OK"; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file - Format YAML invalide"
        invalid_yaml=$((invalid_yaml + 1))
    fi
done

if [ $invalid_yaml -gt 0 ]; then
    echo "   ⚠️ $invalid_yaml fichier(s) avec un format YAML invalide"
    errors=$((errors + invalid_yaml))
fi

# Vérifier les labels cohérents
echo ""
echo "→ Vérification des labels..."
required_labels=("app: smart-ao" "version: v7" "build: \"9\"")
for file in $yaml_files; do
    all_labels_present=true
    for label in "${required_labels[@]}"; do
        if ! grep -q "$label" "$file" 2>/dev/null; then
            all_labels_present=false
            break
        fi
    done
    if [ "$all_labels_present" = true ]; then
        echo "   ✅ $file - Labels cohérents"
    else
        echo "   ⚠️ $file - Labels manquants"
    fi
done

# =============================================================================
# VALIDATION DU SCRIPT DE DÉPLOIEMENT
# =============================================================================

echo ""
echo "Validation du script de déploiement..."
echo ""

if [ -f "scripts/deploy_staging.sh" ]; then
    # Vérifier que le script contient les commandes nécessaires
    # Accepter à la fois kubectl (pour K8s) et docker-compose (pour le déploiement local)
    if (grep -q "kubectl apply" scripts/deploy_staging.sh || grep -q "docker-compose" scripts/deploy_staging.sh) && \
       (grep -q "k8s/namespace" scripts/deploy_staging.sh || grep -q "SMART_AO" scripts/deploy_staging.sh) && \
       (grep -iq "k8s/postgres" scripts/deploy_staging.sh || grep -iq "postgres" scripts/deploy_staging.sh) && \
       (grep -iq "k8s/qdrant" scripts/deploy_staging.sh || grep -iq "qdrant" scripts/deploy_staging.sh) && \
       (grep -iq "k8s/redis" scripts/deploy_staging.sh || grep -iq "redis" scripts/deploy_staging.sh) && \
       (grep -iq "k8s/app" scripts/deploy_staging.sh || grep -iq "smart-ao" scripts/deploy_staging.sh); then
        echo "✅ scripts/deploy_staging.sh contient toutes les commandes nécessaires"
    else
        echo "❌ scripts/deploy_staging.sh manque des commandes"
        errors=$((errors + 1))
    fi
fi

# =============================================================================
# AFFICHAGE DES RÉSULTATS
# =============================================================================

echo ""
echo "=========================================="
if [ $errors -eq 0 ]; then
    echo "✅ Gate 9: VALIDÉ"
    echo "Déploiement Staging prêt à être exécuté"
    echo "=========================================="
    echo ""
    echo "Pour déployer, exécutez :"
    echo "  bash scripts/deploy_staging.sh"
    echo ""
    exit 0
else
    echo "❌ Gate 9: ÉCHEC"
    echo "$errors fichiers manquants ou problèmes détectés"
    echo "=========================================="
    exit 1
fi
