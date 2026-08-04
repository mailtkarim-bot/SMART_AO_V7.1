# =============================================================================
# SMART_AO V7 - Dockerfile
# =============================================================================
# Multi-stage build pour optimiser la taille de l'image
# Auteur: NOOR - Architecte Principal
# Version: 0.1.0
# Date: 04/08/2026
# =============================================================================

# --- BUILD STAGE : Installation des dépendances ---
FROM python:3.12-slim as builder

WORKDIR /app

# Copier uniquement les fichiers nécessaires pour l'installation
COPY requirements.txt .

# Installer les dépendances dans un virtual environment isolé
# Utiliser --user pour éviter les conflits de permissions
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# --- RUNTIME STAGE : Image finale optimisée ---
FROM python:3.12-slim

# Créer un utilisateur non-root pour la sécurité (meilleure pratique)
RUN groupadd -r smart_ao && useradd -r -g smart_ao smart_ao

# Créer le répertoire de travail
WORKDIR /app

# Copier le virtual environment du builder
COPY --from=builder --chown=smart_ao:smart_ao /opt/venv /opt/venv

# Copier le code source (tout sauf ce qui est dans .dockerignore)
COPY --chown=smart_ao:smart_ao . .

# Définir les variables d'environnement
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONFAULTHANDLER=1

# Changer l'utilisateur pour la sécurité
USER smart_ao

# Exposer le port par défaut de l'application
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health', timeout=5).raise_for_status()" || exit 1

# Commande par défaut
CMD ["python", "app/main.py"]
