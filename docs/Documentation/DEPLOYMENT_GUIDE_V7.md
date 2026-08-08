# 🚀 SMART_AO V7 - Guide de Déploiement
*Version 0.1.0 - Dernière mise à jour : 04/08/2026*
*Architecte Principal: NOOR*

---

## 📋 Sommaire

1. [Prérequis](#prérequis)
2. [Installation Rapide](#installation-rapide)
3. [Déploiement Local (Développement)](#déploiement-local-développement)
4. [Déploiement Docker](#déploiement-docker)
5. [Déploiement Cloud (VPS)](#déploiement-cloud-vps)
6. [Configuration](#configuration)
7. [Commandes Utiles](#commandes-utiles)
8. [Résolution des Problèmes](#résolution-des-problèmes)
9. [Architecture](#architecture)
10. [Contribuer](#contribuer)
11. [Historique des Versions](#historique-des-versions)
12. [Contact & Support](#contact--support)

---

## 📌 1. Prérequis

### 1.1 Prérequis Matériels

| Environnement | CPU | RAM | Disk | OS |
|---------------|-----|-----|------|----|
| **Développement Local** | 2 cores | 4GB | 10GB | Linux/macOS/Windows |
| **Docker Local** | 2 cores | 8GB | 20GB | Linux/macOS/Windows |
| **Production Cloud** | 4 cores | 16GB | 50GB | Linux (Ubuntu 22.04+) |

> ⚠️ **Note Importante** : SMART_AO V7 est optimisé pour **16GB RAM** (contrainte Single-Tenant).
> Pour des charges plus lourdes, prévoir un scaling horizontal (V2).

---

### 1.2 Prérequis Logiciels

#### Pour le Déploiement Local (sans Docker)
- ✅ **Python** : 3.12.x
- ✅ **pip** : 24.x
- ✅ **PostgreSQL** : 15+
- ✅ **Qdrant** : 1.8.x *(optionnel pour le développement basique)*

#### Pour le Déploiement Docker (Recommandé)
- ✅ **Docker** : 24.x+
- ✅ **Docker Compose** : 2.x+
- ✅ **Git** : 2.x *(pour cloner le projet)*

#### Validation des Prérequis
```bash
# Vérifier les versions
python3 --version      # Doit afficher Python 3.12.x
docker --version       # Doit afficher Docker 24.x
docker-compose --version  # Doit afficher Docker Compose 2.x
```

---

## 🚀 2. Installation Rapide

### 2.1 Cloner le Projet
```bash
# Cloner le dépôt
cd /opt
.git clone https://github.com/noor/SMART_AO_V2.git
cd SMART_AO_V2/SMART_AO_LAST 4/SMART_AO_V7

# Vérifier la structure
ls -la
```

### 2.2 Déploiement Docker (Méthode Recommandée)
```bash
# 1. Copier le fichier d'environnement
cp .env.docker .env

# 2. (IMPORTANT) Modifier les mots de passe dans .env
nano .env
# Changez au minimum DB_PASSWORD

# 3. Démarrer le déploiement
bash scripts/deploy_v7.sh docker
```

**Résultat attendu :**
```
✅ PostgreSQL est prêt
✅ Qdrant est prêt
✅ Déploiement Docker terminé!

URL: http://localhost:8000
```

### 2.3 Valider le Déploiement
```bash
# Vérifier que tout fonctionne
bash scripts/health_check.sh docker

# Tester l'API
curl http://localhost:8000/health

# Voir les logs
docker-compose logs -f
```

---

## 💻 3. Déploiement Local (Sans Docker)

### 3.1 Installer les Dépendances
```bash
# Créer un environnement virtuel
python3 -m venv venv

# Activer l'environnement (Linux/macOS)
source venv/bin/activate

# Sur Windows
# venv\Scripts\activate

# Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt

# Désactiver l'environnement
# deactivate
```

### 3.2 Configurer PostgreSQL
```bash
# Installer PostgreSQL (Ubuntu/Debian)
sudo apt update
sudo apt install -y postgresql postgresql-contrib postgresql-client

# Créer l'utilisateur et la base
sudo -u postgres psql -c "CREATE USER smart_ao WITH PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "CREATE DATABASE smart_ao_v7 OWNER smart_ao;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE smart_ao_v7 TO smart_ao;"

# Activer les extensions nécessaires
sudo -u postgres psql -d smart_ao_v7 -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
```

### 3.3 Configurer Qdrant *(Optionnel)*
```bash
# Télécharger Qdrant
curl -fsSL https://github.com/qdrant/qdrant/releases/download/v1.8.0/qdrant_x86_64-unknown-linux-musl -o qdrant
chmod +x qdrant

# Démarrer Qdrant
./qdrant &

# Vérifier que Qdrant répond
curl http://localhost:6333
```

### 3.4 Démarrer l'Application
```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Exécuter les migrations
alembic -c alembic.ini upgrade head

# Démarrer l'application
python app/main.py
```

---

## 🐳 4. Déploiement Docker

### 4.1 Structure des Fichiers

```
SMART_AO_V7/
├── Dockerfile              # Définition de l'image application
├── docker-compose.yml      # Orchestration des services
├── .env.docker             # Template de configuration
├── .dockerignore           # Fichiers à exclure du build
└── scripts/
    ├── deploy_v7.sh        # Script de déploiement
    ├── health_check.sh     # Vérification des services
    └── wait_for_services.sh # Attente des dépendances
```

---

### 4.2 Commandes de Base

| Commande | Description |
|----------|-------------|
| `bash scripts/deploy_v7.sh docker` | Démarrer tous les services |
| `bash scripts/deploy_v7.sh down` | Arrêter tous les services |
| `bash scripts/deploy_v7.sh status` | Voir le statut |
| `bash scripts/deploy_v7.sh logs` | Voir les logs en temps réel |
| `docker-compose ps` | Liste des conteneurs |
| `docker-compose up -d` | Démarrer manuellement |
| `docker-compose down` | Arrêter manuellement |

---

### 4.3 Accéder aux Services

| Service | URL | Authentification |
|---------|-----|-----------------|
| **Application** | `http://localhost:8000` | - |
| **API Health** | `http://localhost:8000/health` | - |
| **PostgreSQL** | `postgresql://localhost:5432` | `smart_ao` / *(mot de passe dans .env)* |
| **Qdrant** | `http://localhost:6333` | - |
| **Qdrant Dashboard** | `http://localhost:6333/dashboard` | - |

---

### 4.4 Gérer les Conteneurs

```bash
# Lister tous les conteneurs (même arrêtés)
docker ps -a

# Voir les logs d'un conteneur spécifique
docker logs smart_ao_app

# Exécuter une commande dans un conteneur
docker exec -it smart_ao_app bash

# Redémarrer un conteneur
docker-compose restart app

# Rebuilder l'image (après modification du code)
docker-compose build --no-cache

# Supprimer tous les conteneurs et volumes
docker-compose down -v
```

---

### 4.5 Gérer les Volumes (Données)

```bash
# Lister les volumes
docker volume ls

# Sauvegarder un volume (PostgreSQL)
docker run --rm \
  -v smart_ao_postgres_data:/data \
  -v $(pwd)/backups:/backup \
  alpine \
  tar cvf /backup/postgres_backup_$(date +%Y%m%d_%H%M%S).tar /data

# Restaurer un volume (PostgreSQL)
docker run --rm \
  -v smart_ao_postgres_data:/data \
  -v $(pwd)/backups:/backup \
  alpine \
  tar xvf /backup/postgres_backup_latest.tar -C /

# Nettoyer les volumes non utilisés
docker volume prune
```

---

## ☁️ 5. Déploiement Cloud (VPS)

### 5.1 Prérequis VPS

- ✅ **OS** : Ubuntu 22.04 LTS *(recommandé)*
- ✅ **Docker** : Installé et configuré
- ✅ **Docker Compose** : Installé
- ✅ **Mémoire** : 16GB minimum
- ✅ **Espace disque** : 50GB minimum
- ✅ **Ports ouverts** : 80, 443, 8000, 5432, 6333

---

### 5.2 Installation de Docker sur VPS

```bash
# Mettre à jour le système
sudo apt update && sudo apt upgrade -y

# Installer les dépendances
sudo apt install -y ca-certificates curl gnupg lsb-release

# Ajouter la clé GPG officielle de Docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Ajouter le dépôt Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Installer Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Ajouter l'utilisateur au groupe docker (pour éviter sudo)
sudo usermod -aG docker $USER
newgrp docker

# Vérifier l'installation
docker --version
docker-compose --version
```

---

### 5.3 Déploiement sur VPS

```bash
# Se connecter au VPS
ssh user@votre-serveur

# Cloner le projet
git clone https://github.com/noor/SMART_AO_V2.git
cd SMART_AO_V2/SMART_AO_LAST 4/SMART_AO_V7

# Copier la configuration production
cp .env.docker .env

# MODIFIER LE FICHIER .env AVEC VOS MOTS DE PASSE
nano .env
# Changez TOUS les mots de passe !
# DB_PASSWORD=your_very_secure_password
# QDRANT_PASSWORD=your_qdrant_password

# Démarrer le déploiement
bash scripts/deploy_v7.sh cloud
```

---

### 5.4 Configuration Production

#### Utiliser docker-compose.prod.yml *(Optionnel)*

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  postgres:
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_prod_data:/var/lib/postgresql/data
    
  qdrant:
    environment:
      QDRANT__SERVICE__API_KEY: ${QDRANT_API_KEY}
    volumes:
      - qdrant_prod_data:/qdrant/storage
    
  app:
    environment:
      ENVIRONMENT: production
      LOG_LEVEL: WARNING
    ports:
      - "80:8000"  # Accès direct sur port 80
    
volumes:
  postgres_prod_data:
  qdrant_prod_data:
```

#### Démarrer avec la configuration production
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

### 5.5 Configuration Nginx *(Optionnel pour V1)*

Pour une configuration production complète avec HTTPS, utilisez Nginx comme reverse proxy.

```bash
# Installer Nginx
sudo apt install -y nginx certbot python3-certbot-nginx

# Créer la configuration Nginx
sudo nano /etc/nginx/sites-available/smart_ao
```

Exemple de configuration Nginx :
```nginx
server {
    listen 80;
    server_name smart-ao.votre-domaine.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

### 5.6 Configuration SSL avec Let's Encrypt

```bash
# Obtenir un certificat SSL
sudo certbot --nginx -d smart-ao.votre-domaine.com

# Renouvellement automatique
sudo certbot renew --dry-run
```

---

## ⚙️ 6. Configuration

### 6.1 Variables d'Environnement

Le fichier `.env` contient toutes les configurations nécessaires. Voici les principales variables :

| Variable | Valeur par défaut | Description |
|----------|-------------------|-------------|
| `APP_PORT` | 8000 | Port de l'application |
| `ENVIRONMENT` | development | Environnement (development/staging/production) |
| `LOG_LEVEL` | INFO | Niveau de logs (DEBUG/INFO/WARNING/ERROR) |
| `DB_HOST` | postgres | Hôte PostgreSQL |
| `DB_PORT` | 5432 | Port PostgreSQL |
| `DB_NAME` | smart_ao_v7 | Nom de la base de données |
| `DB_USER` | smart_ao | Utilisateur PostgreSQL |
| `DB_PASSWORD` | ***CHANGEZ-CELA** | Mot de passe PostgreSQL |
| `QDRANT_HOST` | qdrant | Hôte Qdrant |
| `QDRANT_PORT` | 6333 | Port Qdrant |

---

### 6.2 Configuration de PostgreSQL

#### Dans docker-compose.yml
```yaml
environment:
  POSTGRES_USER: smart_ao
  POSTGRES_PASSWORD: ${DB_PASSWORD}
  POSTGRES_DB: smart_ao_v7
  POSTGRES_INITDB_ARGS: "--data-checksums --encoding=UTF8 --locale=C"
```

#### Optimisation des Performances
```yaml
environment:
  # Mémoire (50% de 16GB)
  POSTGRES_MEMORY_LIMIT: "4GB"
  # Connexions maximales
  POSTGRES_MAX_CONNECTIONS: "100"
  # Work mem
  POSTGRES_WORK_MEM: "16MB"
```

---

### 6.3 Configuration de Qdrant

```yaml
environment:
  # Désactiver le clustering (single node pour V1)
  QDRANT__CLUSTER__ENABLED: "false"
  # Sauvegarde automatique
  QDRANT__PERSISTENCE__SAVE_INTERVAL_SEC: "60"
  QDRANT__PERSISTENCE__SNAPSHOT_INTERVAL_SEC: "300"
  # Mémoire allouée (4GB)
  QDRANT__MEMORY__MAP_SIZE: "4294967296"
```

---

### 6.4 Configuration de l'Application

#### Variables de Performance
```yaml
environment:
  MAX_PARALLEL_AGENTS: "6"  # Max agents en parallèle (16GB RAM)
  WORKFLOW_TIMEOUT: "3600"   # Timeout du workflow (secondes)
  AGENT_TIMEOUT: "600"       # Timeout par agent (secondes)
```

---

## 💡 7. Commandes Utiles

### 7.1 Commandes Docker

```bash
# Lister tous les conteneurs (y compris arrêtés)
docker ps -a

# Lister uniquement les conteneurs en cours
docker ps

# Voir les logs d'un conteneur
docker logs smart_ao_app

# Suivre les logs en temps réel
docker logs -f smart_ao_app

# Exécuter une commande dans un conteneur
docker exec -it smart_ao_app bash

# Arrêter un conteneur spécifique
docker stop smart_ao_app

# Démarrer un conteneur arrêté
docker start smart_ao_app

# Supprimer un conteneur
docker rm smart_ao_app

# Supprimer tous les conteneurs arrêtés
docker container prune

# Nettoyer le système Docker (⚠️ ATTENTION)
docker system prune -a --volumes

# Voir les statistiques (CPU, RAM, etc.)
docker stats
```

---

### 7.2 Commandes Docker Compose

```bash
# Démarrer tous les services
docker-compose up -d

# Arrêter tous les services
docker-compose down

# Arrêter et supprimer les volumes
docker-compose down -v

# Rebuilder les images
docker-compose build --no-cache

# Voir le statut des services
docker-compose ps

# Voir les logs de tous les services
docker-compose logs

# Suivre les logs en temps réel
docker-compose logs -f

# Exécuter une commande dans le service app
docker-compose exec app python app/main.py

# Exécuter les migrations manuellement
docker-compose exec app alembic -c /app/alembic.ini upgrade head

# Exécuter les tests
docker-compose exec app pytest tests/unit/ -v
```

---

### 7.3 Commandes de Déploiement

```bash
# Déploiement Docker (recommandé)
bash scripts/deploy_v7.sh docker

# Déploiement local
bash scripts/deploy_v7.sh local

# Arrêter tout
bash scripts/deploy_v7.sh down

# Voir le statut
bash scripts/deploy_v7.sh status

# Voir les logs
bash scripts/deploy_v7.sh logs

# Vérifier la santé des services
bash scripts/health_check.sh docker

# Vérifier la santé (mode local)
bash scripts/health_check.sh local
```

---

### 7.4 Commandes de Base de Données

```bash
# Se connecter à PostgreSQL (via Docker)
docker-compose exec postgres psql -U smart_ao -d smart_ao_v7

# Exécuter une requête SQL
docker-compose exec postgres psql -U smart_ao -d smart_ao_v7 -c "SELECT * FROM missions;"

# Lister toutes les tables
docker-compose exec postgres psql -U smart_ao -d smart_ao_v7 -c "\dt"

# Exporter la base de données
docker-compose exec postgres pg_dump -U smart_ao smart_ao_v7 > backup_$(date +%Y%m%d_%H%M%S).sql

# Importer la base de données
cat backup.sql | docker-compose exec -i postgres psql -U smart_ao smart_ao_v7

# Vérifier les connexions actives
docker-compose exec postgres psql -U smart_ao -d smart_ao_v7 -c "SELECT * FROM pg_stat_activity;"
```

---

### 7.5 Commandes Qdrant

```bash
# Vérifier que Qdrant répond
curl http://localhost:6333

# Voir le dashboard Qdrant
# Ouvrir http://localhost:6333/dashboard dans votre navigateur

# Lister les collections
curl http://localhost:6333/collections

# Vérifier la santé
curl http://localhost:6333/readyz
```

---

### 7.6 Commandes Application

```bash
# Tester l'API Health
curl http://localhost:8000/health

# Vérifier le nombre d'agents enregistrés
curl http://localhost:8000/agents/stats

# Exécuter un workflow de test (si disponible)
curl -X POST http://localhost:8000/workflows/test \
  -H "Content-Type: application/json" \
  -d '{"documents": ["test.pdf"]}'
```

---

## 🐛 8. Résolution des Problèmes

### 8.1 Erreurs Courantes et Solutions

| **Problème** | **Cause Probable** | **Solution** |
|--------------|---------------------|--------------|
| `Port 8000 déjà utilisé` | Autre service utilise le port | `lsof -i :8000` puis `kill <PID>` |
| `Port 5432 déjà utilisé` | PostgreSQL local en cours | `sudo service postgresql stop` ou changez le port |
| `Connection refused (PostgreSQL)` | PostgreSQL non démarré | Vérifiez `docker-compose ps` et attendez |
| `Connection refused (Qdrant)` | Qdrant non démarré | Qdrant peut mettre 30-60s à démarrer |
| `ModuleNotFoundError: psycopg2` | psycopg2 non installé dans le conteneur | `docker-compose build --no-cache` |
| `Docker build échoue` | Problème dans Dockerfile | Vérifiez les logs, corrigez Dockerfile |
| `No such file or directory` | Fichier manquant | Vérifiez les chemins dans docker-compose.yml |
| `Permission denied` | Problèmes de permissions | Utilisez `chown` ou `COPY --chown` dans Dockerfile |
| `Migrations échouées` | Base déjà existe | `docker-compose down -v` puis relancez |

---

### 8.2 Problèmes Spécifiques

#### Problème : Les conteneurs démarre mais crash immédiatement

```bash
# Voir les logs pour identifier la cause
docker-compose logs app

# Problèmes courants:
# 1. DB_PASSWORD incorrect dans .env
# 2. Port déjà utilisé
# 3. Dépendance manquante dans requirements.txt
```

**Solution :**
1. Vérifiez `.env`
2. Vérifiez les ports avec `netstat -tuln`
3. Testez manuellement `pip install -r requirements.txt`

---

#### Problème : PostgreSQL ne démarre pas

```bash
# Vérifier les logs PostgreSQL
docker-compose logs postgres

# Problèmes courants:
# 1. Volume corrompu
# 2. Mot de passe trop long/complexe
# 3. Problème de permissions sur le volume
```

**Solution :**
```bash
# Supprimer le volume et redémarrer
docker-compose down -v
docker-compose up -d
```

---

#### Problème : Qdrant ne démarre pas

```bash
# Qdrant peut prendre 30-60 secondes à démarrer
# Vérifiez avec
docker-compose logs qdrant

# Si Qdrant crash en boucle, essayez:
docker-compose down -v
docker-compose pull qdrant  # Mettre à jour l'image
docker-compose up -d
```

---

#### Problème : L'application ne répond pas sur /health

```bash
# Vérifiez que l'application a démarré
docker-compose logs app

# Vérifiez que PostgreSQL est prêt
docker-compose exec app python -c "import psycopg2; print(psycopg2.__version__)"

# Testez la connexion PostgreSQL manuellement
docker-compose exec app python -c "
import psycopg2
conn = psycopg2.connect(host='postgres', port=5432, dbname='smart_ao_v7', user='smart_ao', password='your_password')
print('Connection OK')
conn.close()
"
```

---

#### Problème : Les migrations échouent

```bash
# Essayez d'exécuter les migrations manuellement
docker-compose exec app alembic -c /app/alembic.ini history

# Si les tables existent déjà:
docker-compose down -v  # ⚠️ Cela supprime toutes les données
docker-compose up -d

# Si vous voulez conserver les données, utilisez:
docker-compose exec app alembic -c /app/alembic.ini upgrade head --sql-only
```

---

### 8.3 Debug Mode

```bash
# Démarrer avec des logs détaillés
docker-compose up --build --force-recreate

# Voir tous les logs
docker-compose logs -f

# Se connecter à un conteneur en mode interactif
docker exec -it smart_ao_app /bin/bash

# Tester la connexion PostgreSQL depuis le conteneur app
docker exec -it smart_ao_app python -c "
from app.core.database import engine, async_session_maker
import asyncio

async def test_db():
    async with engine.begin() as conn:
        result = await conn.execute('SELECT 1')
        print('Database connection OK:', result.scalar())

asyncio.run(test_db())
"
```

---

### 8.4 Vérifier les Ressources

```bash
# Voir l'utilisation CPU/RAM
docker stats

# Voir l'utilisation disque
docker system df

# Nettoyer les images non utilisées
docker image prune

# Nettoyer les volumes non utilisés (⚠️ ATTENTION)
docker volume prune
```

---

## 🏗️ 9. Architecture

### 9.1 Schéma d'Architecture Docker

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SMART_AO V7 - Architecture Docker                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                            HÔTE (Votre Machine)                           │   │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────────┐  │   │
│  │  │   Client    │───▶│   Nginx     │───▶│      Reverse Proxy       │  │   │
│  │  │  (Browser)  │    │  (Optionnel) │    │  (Port 80/443)           │  │   │
│  │  └─────────────┘    └─────────────┘    └─────────────────────────┘  │   │
│  │                                                                     │   │
│  │  ┌───────────────────────────────────────────────────────────────┐  │   │
│  │  │                    Docker Network: smart_ao_network                │  │   │
│  │  │                                                                   │  │   │
│  │  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │  │   │
│  │  │  │  PostgreSQL  │    │    App      │    │       Qdrant        │  │  │   │
│  │  │  │  (Port 5432) │◀───┤  (Port 8000)│◀───┤     (Port 6333)    │  │  │   │
│  │  │  │  Container   │    │  Container   │    │     Container       │  │  │   │
│  │  │  └─────────────┘    └─────────────┘    └─────────────────────┘  │  │   │
│  │  │        ▲                    ▲                    ▲              │  │   │
│  │  └────────┼────────────────────┼────────────────────┼──────────────┘  │   │
│  │           │                    │                    │                 │   │
│  │  ┌────────▼────────┐  ┌────────▼────────┐  ┌────────▼────────┐    │   │
│  │  │ postgres_data    │  │   (tmpfs)        │  │   qdrant_data     │    │   │
│  │  │ (Volume Docker)  │  │   (Mémoire)      │  │   (Volume Docker)  │    │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘    │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 9.2 Flux de Déploiement

```
┌─────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  User   │────▶│ git clone    │────▶│ cp .env.docker│────▶│ Modify .env   │
└─────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                                                                          │
                                                                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        deploy_v7.sh docker                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐       │
│  │ docker-compose   │  │ wait_for_services│  │ Exécuter        │       │
│  │ build           │──▶│ .sh              │──▶│ migrations      │       │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘       │
└─────────────────────────────────────────────────────────────────────────┘
                                                                          │
┌─────────────────────────────────────────────────────────────────────────┐
│                        Déploiement Terminé                                 │
│  ✅ PostgreSQL: localhost:5432                                            │
│  ✅ Qdrant: http://localhost:6333                                         │
│  ✅ App: http://localhost:8000                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### 9.3 Topologie des Conteneurs

| Service | Conteneur | Port Interne | Port Externe | Volume | Health Check |
|---------|-----------|--------------|--------------|--------|--------------|
| PostgreSQL | smart_ao_postgres | 5432 | 5432 | postgres_data | pg_isready |
| Qdrant | smart_ao_qdrant | 6333 | 6333 | qdrant_data | HTTP 200 |
| Application | smart_ao_app | 8000 | 8000 | app_logs | /health 200 |

---

### 9.4 Configuration Matérielle Recommandée

| Environnement | vCPU | RAM | Disk | Network |
|---------------|------|-----|------|---------|
| Développement | 2 | 8GB | 20GB | 1Gbps |
| Staging | 4 | 16GB | 50GB | 1Gbps |
| Production | 8 | 32GB | 100GB | 10Gbps |

---

## 🤝 10. Contribuer

### 10.1 Développement Local

```bash
# Cloner le projet
git clone https://github.com/noor/SMART_AO_V2.git
cd SMART_AO_V2/SMART_AO_LAST 4/SMART_AO_V7

# Créer une branche pour votre feature
git checkout -b feature/nom-de-votre-feature

# Faire vos modifications, puis:
git add .
git commit -m "feat: description de votre feature"
git push origin feature/nom-de-votre-feature

# Créer une Pull Request
gh pr create
```

---

### 10.2 Tests

```bash
# Exécuter tous les tests unitaires
pytest tests/unit/ -v

# Exécuter un test spécifique
pytest tests/unit/test_integration_engines_v7.py::TestWorkflowEngine -v

# Tests avec couverture de code
pytest --cov=app tests/unit/

# Générer un rapport HTML de couverture
pytest --cov=app --cov-report=html tests/unit/
```

---

### 10.3 Bonnes Pratiques

1. **Commits atomiques** : Un commit = une seule fonctionnalité/bugfix
2. **Messages de commit clairs** : Utilisez le format `type(scope): description`
   - `feat(agents): ajouter nouveau agent`
   - `fix(migration): corriger erreur de migration`
   - `docs(readme): mettre à jour la documentation`
3. **Tests obligatoires** : Tout nouveau code doit avoir des tests
4. **Revue de code** : Toute PR doit être revue avant merge
5. **Respect des conventions** : Suivez le style de code existant

---

## 📜 11. Historique des Versions

| Version | Date | Auteur | Changements |
|---------|------|--------|-------------|
| 0.1.0 | 04/08/2026 | NOOR | Version initiale - REC-014 |

---

## 📧 12. Contact & Support

| Type | Contact | Temps de Réponse |
|------|---------|------------------|
| **Bug Report** | [GitHub Issues](https://github.com/noor/SMART_AO_V2/issues) | 24-48h |
| **Question Technique** | [GitHub Discussions](https://github.com/noor/SMART_AO_V2/discussions) | 12-24h |
| **Support Commercial** | noor@your-domain.com | 4-6h |
| **Urgent (Production)** | +XX XXX XXX XXX | Immédiat |

---

## 📄 Licence

Ce projet est sous licence **Propriétaire - Tous droits réservés**. 

> ⚠️ **IMPORTANT** : L'utilisation de ce logiciel est soumise à acceptation préalable. 
> Contactez NOOR pour obtenir une licence.

---

**© 2026 SMART_AO V7 - Tous droits réservés**
**Architecte Principal: NOOR**
**Email: noor@your-domain.com**

---

*Documentation générée automatiquement via REC-014 - Déploiement V7*
