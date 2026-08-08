# SMART_AO V7 - Architecture de Deployement
*Version 0.1.0 - 05/08/2026*
*Architecte Principal: NOOR*

---

## Sommaire

1. [Vue d'Ensemble](#vue-densemble)
2. [Architecture des Conteneurs](#architecture-des-conteneurs)
3. [Configuration Reseau](#configuration-reseau)
4. [Strategie de Persistance](#strategie-de-persistance)
5. [Configuration des Ressources](#configuration-des-ressources)
6. [Securite](#securite)
7. [Observabilite](#observabilite)
8. [Workflows de Deployement](#workflows-de-deployement)
9. [Architecture Future (V2)](#architecture-future-v2)

---

## Vue d'Ensemble

### Principes Clés
- **Single-Tenant** : 1 instance = 1 client (contrainte 16GB RAM)
- **Architecture Modulaire** : Séparation PostgreSQL, Qdrant, Application
- **Asynchrone** : async/await pour les opérations I/O-bound
- **Multi-stage Build** : Images Docker optimisées
- **Health Checks** : Surveillance proactive de tous les services

### Stack Technologique

| Composant | Technologie | Version | Rôle |
|-----------|-------------|---------|------|
| Application | Python/FastAPI | 3.12 | API REST, Orchestration |
| Base de Données | PostgreSQL | 16 | Persistance SQL |
| Recherche Vectorielle | Qdrant | 1.8.0 | Embeddings, Similarité |
| Conteneurisation | Docker | 24+ | Isolation |
| Orchestration | Docker Compose | 2.x | Gestion multi-conteneurs |

---

## Architecture des Conteneurs

### Diagramme d'Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        HOTE (16GB RAM)                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐              │
│  │   PostgreSQL  │    │    Qdrant     │    │  Application  │              │
│  │   (4GB RAM)   │    │   (4GB RAM)   │    │   (2GB RAM)   │              │
│  │  Port: 5432   │    │ Port: 6333/4  │    │  Port: 8000   │              │
│  └──────────────┘    └──────────────┘    └──────────────┘              │
│           │                     │                     │                 │
│           └─────────────────────┼─────────────────────┘                 │
│                             │                                          │
│                    ┌────────────▼────────────┐                         │
│                    │   smart_ao_network       │                         │
│                    │   (Réseau Docker Bridge) │                         │
│                    └─────────────────────────┘                         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Topologie Docker Compose

```yaml
Services:
  ├── postgres:16-alpine    # Base de données SQL
  ├── qdrant:v1.8.0        # Moteur vectoriel
  └── app:latest           # Application SMART_AO

Networks:
  └── smart_ao_network     # Réseau isolé Bridge

Volumes:
  ├── smart_ao_postgres_data  # Données PostgreSQL
  ├── smart_ao_qdrant_data    # Données Qdrant
  └── smart_ao_app_logs       # Logs application
```

---

## Configuration Reseau

### Configuration IP et Ports

| Service | Container Port | Host Port | Protocole | Accès |
|---------|----------------|-----------|-----------|-------|
| PostgreSQL | 5432 | 5432 | TCP | Interne + Host (optionnel) |
| Qdrant HTTP | 6333 | 6333 | TCP | Interne + Host (optionnel) |
| Qdrant gRPC | 6334 | 6334 | TCP | Interne |
| Application | 8000 | 8000 | TCP | Host + Externe |

### Résolution DNS Interne
- `postgres` → Résout vers le conteneur PostgreSQL
- `qdrant` → Résout vers le conteneur Qdrant
- `app` → Résout vers le conteneur Application

### Connexions Externes
- **Application** : `http://localhost:8000` ou `http://<server-ip>:8000`
- **Base de données** : Accessible via le conteneur app uniquement (sécurité)
- **Qdrant** : Accessible via le conteneur app uniquement (sécurité)

---

## Strategie de Persistance

### Volumes Docker

| Volume | Montage | Persistance | Taille Estimée |
|--------|---------|-------------|----------------|
| postgres_data | /var/lib/postgresql/data | ✅ Oui | 1-5GB |
| qdrant_data | /qdrant/storage | ✅ Oui | 500MB-2GB |
| app_logs | /app/logs | ✅ Oui | 100MB-1GB |

### Configuration PostgreSQL
- **Checksums** : Activés pour intégrité des données
- **Encoding** : UTF8
- **Locale** : C (performances optimisées)
- **Mémoire** : 4GB (50% de 16GB total)

### Configuration Qdrant
- **Single Node** : Pas de clustering en V1
- **Persistence** : Sauvegarde toutes les 60 secondes
- **Snapshots** : Toutes les 5 minutes
- **Mémoire** : 4GB (4294967296 bytes)
- **Map Size** : 4GB pour les index

---

## Configuration des Ressources

### Allocation Memoire (16GB Total)

| Composant | Allocation | Utilisation Typique | Pic Maximum |
|-----------|------------|--------------------|-------------|
| PostgreSQL | 4GB | 2-3GB | 4GB |
| Qdrant | 4GB | 1-2GB | 4GB |
| Application | 2GB | 500MB-1GB | 2GB |
| Buffer Systeme | 6GB | - | - |

### Limites CPU
- **Production** : 4 cœurs recommandés
- **Développement** : 2 cœurs minimum
- **Conteneur App** : Pas de limite stricte (utilise ce qui est disponible)

### Configuration Application
```python
MAX_PARALLEL_AGENTS = 6      # 6 agents simultanés
WORKFLOW_TIMEOUT = 3600      # 1 heure par workflow
```

---

## Securite

### Mesures de Securité Implémentées

#### 1. Isolation des Conteneurs
- Chaque service dans son propre conteneur
- Réseau Docker isolé (smart_ao_network)
- Pas d'accès direct depuis l'hôte (sauf ports exposés)

#### 2. Sécurité de l'Application
- **Utilisateur non-root** : Conteneur app exécute sous `smart_ao:smart_ao`
- **Gestion des secrets** : Variables d'environnement (pas de hardcoding)
- **Fichier .env** : Exclu du git via .gitignore

#### 3. Sécurité PostgreSQL
- Authentification par mot de passe requis
- Utilisateur dédié (`smart_ao`)
- Base de données dédiée (`smart_ao_v7`)

#### 4. Sécurité Qdrant
- Pas d'authentification en V1 (réseau isolé = sécurisé)
- En production : Activer l'authentification Qdrant (V2)

#### 5. Health Checks
- PostgreSQL : `pg_isready` toutes les 10 secondes
- Qdrant : `wget --spider` toutes les 10 secondes
- Application : Requête HTTP `/health` toutes les 30 secondes

### Recommandations de Securité pour la Production

1. **Changer TOUS les mots de passe** dans .env
2. **Utiliser des secrets Docker** au lieu de variables d'environnement
3. **Configurer HTTPS** avec Let's Encrypt (Nginx reverse proxy)
4. **Activer l'authentification Qdrant** avec API key
5. **Configurer un firewall** (ufw) pour limiter les ports exposés
6. **Mettre à jour régulièrement** les images Docker
7. **Sauvegarder les volumes** régulièrement

---

## Observabilite

### Metriques de Sante

#### Health Check Endpoints
| Service | Endpoint | Méthode | Fréquence |
|---------|----------|---------|-----------|
| Application | `/health` | GET | 30s |
| PostgreSQL | `pg_isready` | CMD | 10s |
| Qdrant | `/` | GET | 10s |

#### Commande de Validation
```bash
# Validation complète
bash scripts/health_check.sh docker

# Vérification individuelle
bash scripts/health_check.sh docker postgres
bash scripts/health_check.sh docker qdrant
bash scripts/health_check.sh docker app
```

### Logs
- **Application** : `/app/logs/app.log` (monté sur volume)
- **PostgreSQL** : `docker logs smart_ao_postgres`
- **Qdrant** : `docker logs smart_ao_qdrant`

### Monitoring Recommandé (V2)
- Prometheus + Grafana pour les métriques
- ELK Stack pour les logs centralisés
- Jaeger pour le tracing distribué

---

## Workflows de Deployement

### Workflow 1 : Développement Local

```bash
# 1. Cloner le projet
git clone <repository>
cd SMART_AO_V7

# 2. Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Démarrer les services
bash scripts/deploy_v7.sh local

# 5. Valider
bash scripts/health_check.sh local
```

### Workflow 2 : Déploiement Docker

```bash
# 1. Configurer l'environnement
cp .env.docker .env
nano .env  # Modifier DB_PASSWORD

# 2. Build et démarrage
docker-compose build
bash scripts/deploy_v7.sh docker

# 3. Vérifier
bash scripts/health_check.sh docker

# 4. Voir les logs
docker-compose logs -f
```

### Workflow 3 : Déploiement Cloud (VPS)

```bash
# 1. Se connecter au serveur
ssh user@server-ip

# 2. Cloner le projet
git clone <repository>
cd SMART_AO_V7

# 3. Installer Docker
bash scripts/deploy_v7.sh setup-docker

# 4. Déployer
bash scripts/deploy_v7.sh cloud

# 5. Valider
bash scripts/health_check.sh cloud

# 6. Configurer Nginx (HTTPS)
bash scripts/deploy_v7.sh setup-nginx
```

### Workflow 4 : Mise à Jour

```bash
# 1. Tirer les dernières modifications
git pull origin main

# 2. Rebuild les conteneurs
docker-compose down
docker-compose build --no-cache

# 3. Redémarrer
bash scripts/deploy_v7.sh docker

# 4. Valider
bash scripts/health_check.sh docker
```

---

## Architecture Future (V2)

### Evolutions Prévues

#### 1. Scaling Horizontal
- **Multi-Tenant** : 1 instance par tenant avec isolation complète
- **Load Balancing** : Nginx/Traefik pour répartir la charge
- **Auto-scaling** : Kubernetes (EKS/GKE) pour scaling automatique

#### 2. Haute Disponibilité
- **PostgreSQL** : Réplication master-slave + failover automatique
- **Qdrant** : Cluster multi-nœuds avec sharding
- **Application** : Multiples réplicas derrière load balancer

#### 3. Observabilité Avancée
- **Prometheus** : Collecte de métriques
- **Grafana** : Tableaux de bord en temps réel
- **Loki** : Agrégation des logs
- **Tempo** : Tracing distribué

#### 4. Sécurité Renforcée
- **Authentification** : OAuth2/OIDC avec Keycloak
- **Chiffrement** : TLS mutuel entre services
- **Secrets Management** : HashiCorp Vault ou AWS Secrets Manager
- **Network Policies** : Restriction des flux inter-pods

#### 5. Performances
- **Cache** : Redis pour les requêtes fréquentes
- **Message Queue** : RabbitMQ/Kafka pour le traitement asynchrone
- **CDN** : Cloudflare pour les assets statiques

### Diagramme d'Architecture V2 (Cible)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        CLOUD PROVIDER                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐              │
│  │   Load        │    │   Kubernetes  │    │   Monitoring  │              │
│  │   Balancer    │    │   (EKS/GKE)   │    │   (Prom+Graf) │              │
│  └──────────────┘    └──────────────┘    └──────────────┘              │
│           │                     │                     │                 │
│           ▼                     ▼                     ▼                 │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │                        Kubernetes Cluster                      │       │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │       │
│  │  │  App Pod x3  │  │ PostgreSQL   │  │  Qdrant      │             │       │
│  │  │  (Replicas)  │  │  (HA)        │  │  (Cluster)   │             │       │
│  │  └─────────────┘  └─────────────┘  └─────────────┘             │       │
│  └─────────────────────────────────────────────────────────────┘       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Decisions Architecturales Clés

### Pourquoi Docker Compose pour V1 ?
- **Simplicité** : Facile à déployer et maintenir
- **Ressources** : Adapté à lscale Single-Tenant (16GB)
- **Coût** : Pas de surcoût d'orchestration
- **Portabilité** : Fonctionne partout (local, VPS, cloud)

### Pourquoi PostgreSQL + Qdrant ?
- **PostgreSQL** : Maturity, ACID, SQL puissant, bon pour les données structurées
- **Qdrant** : Optimisé pour les embeddings, recherche vectorielle rapide, scalable
- **Séparation** : Meilleure isolation, optimisation spécifique par type de données

### Pourquoi async/await ?
- **I/O-Bound** : SMART_AO est principalement I/O-bound (appels API, DB, etc.)
- **Performance** : Permet de gérer 100+ requêtes simultanées avec peu de ressources
- **Scalabilité** : Facile à passer en async complet (V2)

### Pourquoi Multi-stage Build ?
- **Taille d'image** : Réduction de ~50% (de ~1GB à ~500MB)
- **Sécurité** : Moins de packages = moins de vulnérabilités
- **Best Practice** : Standard de l'industrie pour les images de production

---

## Verification et Validation

### Checklist Pre-Deployement
- [ ] Docker installé et fonctionnel
- [ ] Docker Compose v2+ installé
- [ ] 16GB RAM disponibles
- [ ] Ports 8000, 5432, 6333, 6334 disponibles
- [ ] .env configuré avec les bons mots de passe
- [ ] Volumes Docker créables (permissions)

### Checklist Post-Deployement
- [ ] `docker-compose ps` montre 3 services healthy
- [ ] `bash scripts/health_check.sh docker` passe
- [ ] `curl http://localhost:8000/health` retourne 200
- [ ] Logs propres (pas d'erreurs critiques)
- [ ] Tests de validation passés

### Commandes de Dépannage

```bash
# Voir les logs de tous les services
docker-compose logs -f

# Voir les logs d'un service spécifique
docker logs smart_ao_postgres

# Redémarrer un service
docker-compose restart app

# Inspecter un conteneur
docker inspect smart_ao_app

# Exécuter une commande dans un conteneur
docker exec -it smart_ao_app bash

# Vérifier l'utilisation des ressources
docker stats

# Nettoyer et recommencer
docker-compose down -v
```

---

## Documentation Connexe

- [DEPLOYMENT_GUIDE_V7.md](./DEPLOYMENT_GUIDE_V7.md) - Guide pas à pas
- [ARCHITECTURE_V7_ENGINE.md](../current/ARCHITECTURE_V7_ENGINE.md) - Architecture moteur
- [ENGINEERING-HANDBOOK_V7.md](../current/ENGINEERING-HANDBOOK_V7.md) - Bonnes pratiques
- [PLAN_MAITRE_V7_FUSION_COMPLETE.md](../current/PLAN_MAITRE_V7_FUSION_COMPLETE.md) - Plan global

---

## Historique des Versions

| Version | Date | Auteur | Modifications |
|---------|------|--------|---------------|
| 0.1.0 | 05/08/2026 | NOOR | Version initiale - REC-014 |

---

*Document généré pour SMART_AO V7 - Déploiement REC-014*
*© 2026 - NOOR Architecte Principal*
