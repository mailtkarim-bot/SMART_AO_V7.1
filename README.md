# **🚀 SMART_AO V7 - Engine OS**
> **Système Intelligent d'Analyse de DCE pour le BTP - Build 9 Production Ready**

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-9-brightgreen.svg)](https://github.com/)
[![Coverage: 90.24%](https://img.shields.io/badge/coverage-90.24%-green.svg)](https://)

---

## **📋 TABLE DES MATIÈRES**

1. [🎯 Introduction](#-introduction)
2. [🏗️ Architecture](#-architecture)
3. [📦 Installation](#-installation)
4. [⚡ Démarrage Rapide](#-démarrage-rapide)
5. [🎛️ Configuration](#-configuration)
6. [🚀 API REST](#-api-rest)
7. [🤖 Engines](#-engines)
8. [📊 Tests](#-tests)
9. [📁 Structure du Projet](#-structure-du-projet)
10. [🔧 Déploiement](#-déploiement)
11. [📖 Documentation Complète](#-documentation-complète)
12. [🤝 Contribution](#-contribution)
13. [📜 Licence](#-licence)

---

## **🎯 INTRODUCTION**

**SMART_AO V7** est un système intelligent d'analyse de DCE (Dossier de Consultation des Entreprises) spécialement conçu pour le secteur du BTP. Il automatise l'analyse des documents techniques, l'extraction des données, la classification et la génération de rapports d'analyse.

### **Fonctionnalités Clés**

| Fonctionnalité | Description |
|---------------|-------------|
| **Analyse Automatique** | Extraction intelligente des données des DCE |
| **Classification** | Identification des types de documents et risques |
| **Agents Spécialisés** | 30+ agents pour des analyses ciblées |
| **Workflow Engine** | Orchestration de 6 étapes d'analyse |
| **Event Bus** | Architecture asynchrone avec publish/subscribe |
| **Résilience** | Circuit breakers et rate limiting intégrés |
| **Persistance** | PostgreSQL pour le stockage des missions |
| **Recherche Vectorielle** | Qdrant pour la recherche sémantique |

### **Cas d'Usage**

- Analyse automatique des DCE
- Détection des risques financiers et juridiques
- Vérification de la conformité réglementaire
- Génération de rapports d'analyse complets
- Optimisation des processus de consultation

---

## **🏗️ ARCHITECTURE**

```
SMART_AO_V7/
├── app/
│   ├── core/                  # Noyau du système
│   │   ├── circuit_breaker.py # Circuit breakers (pybreaker)
│   │   ├── config.py          # Configuration centralisée
│   │   ├── database.py        # Connexion PostgreSQL
│   │   ├── logging.py         # Logging structuré
│   │   ├── resilience.py      # Gestion de la résilience
│   │   └── security.py        # Sécurité et authentification
│   │
│   ├── models/                # Modèles SQLAlchemy
│   │   ├── events.py          # Événements du système
│   │   ├── mission.py         # Missions et étapes
│   │   ├── project.py         # Projets BTP
│   │   └── vault_core.py      # Stockage des documents
│   │
│   ├── engines/               # Moteurs d'analyse
│   │   ├── workflow_engine/   # Orchestration workflow
│   │   │   ├── workflow.py    # Logique principale
│   │   │   ├── mission.py     # Gestion des missions
│   │   │   └── persistence.py # Persistance PG
│   │   │
│   │   ├── event_bus/         # Bus d'événements
│   │   │   ├── bus.py         # Publish/Subscribe
│   │   │   ├── models.py      # Modèles d'événements
│   │   │   └── replay.py      # Replay d'événements
│   │   │
│   │   ├── agent_runtime/    # Exécution des agents
│   │   │   ├── registry.py    # Registre des agents
│   │   │   └── lifecycle.py   # Cycle de vie
│   │   │
│   │   ├── notification_engine/ # Notifications
│   │   ├── plugin_engine/      # Plugins
│   │   ├── security_engine/   # Sécurité
│   │   └── ui_engine/         # Interface utilisateur
│   │
│   ├── agents/                # 30+ Agents spécialisés
│   │   ├── base_agent.py      # Base des agents
│   │   ├── agent_deadline/    # Agent délais
│   │   ├── agent_penalites/   # Agent pénalités
│   │   ├── agent_bim/         # Agent BIM
│   │   └── ... (27 autres)
│   │
│   ├── api/                   # API REST FastAPI
│   │   └── v1/
│   │       └── endpoints/
│   │           ├── agents.py      # Gestion des agents
│   │           ├── documents.py   # Gestion des documents
│   │           ├── health.py      # Health check
│   │           ├── missions.py    # Gestion des missions
│   │           └── workflows.py   # Gestion des workflows
│   │
│   ├── mcp/                   # MCP Server
│   ├── plugins/               # Plugins
│   ├── schemas/               # Schémas Pydantic
│   └── web/                   # Interface Web
│
├── tests/                    # Tests
│   ├── unit/                 # Tests unitaires (317 tests)
│   └── integration/           # Tests d'intégration (38 tests)
│
├── scripts/                  # Scripts utilitaires
│   ├── check_go_nogo.sh       # Validation structure
│   ├── validate_coverage.sh  # Validation couverture
│   └── validate_all_gates.sh  # Validation complète
│
├── docs/                     # Documentation
│   ├── ARCHITECTURE_V7_ENGINE.md
│   ├── ENGINEERING-HANDBOOK_V7.md
│   ├── DEPLOYMENT_GUIDE_V7.md
│   └── current/
│       └── [fichiers de documentation]
│
├── pytest.ini               # Configuration pytest
├── requirements.txt         # Dépendances
├── setup.py                 # Installation
└── README.md                # Ce fichier
```

### **Architecture Technique**

```
┌─────────────────────────────────────────────────────────────────┐
│                        SMART_AO V7 Engine OS                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   FastAPI     │    │   Event Bus  │    │  Workflow    │       │
│  │   (API REST)  │◄───►│ (Async)       │◄───►│  Engine      │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│          ▲                  ▲  ▲                  ▲              │
│          │                  │  │                  │              │
│  ┌───────┴───────┐  ┌─────┴  └─────┐  ┌───────┴───────┐        │
│  │   Agents      │  │  PostgreSQL   │  │  Agent        │        │
│  │ (30 spécialisés)│  │  (Missions)  │  │  Registry    │        │
│  └───────────────┘  └──────────────┘  └───────────────┘        │
│          ▲                  ▲  ▲                                    │
│          │                  │  │                                    │
│  ┌───────┴───────┐  ┌─────┴  └─────┐                              │
│  │   MCP Server   │  │   Qdrant     │                              │
│  │ (Model Context)│  │ (Vecteurs)   │                              │
│  └───────────────┘  └──────────────┘                              │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Circuit Breakers & Rate Limiting         │    │
│  │                     (Résilience & Sécurité)                  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## **📦 INSTALLATION**

### **Pré-requis**

- Python 3.12+
- PostgreSQL 14+
- Qdrant (optionnel, pour la recherche vectorielle)
- Redis (optionnel, pour le caching)
- Git

### **1. Cloner le dépôt**

```bash
git clone https://github.com/noor/SMART_AO_V7.git
cd SMART_AO_V7
```

### **2. Créer un environnement virtuel**

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### **3. Installer les dépendances**

```bash
# Installation en mode développement
pip install -e .

# Ou installation des dépendances directement
pip install -r requirements.txt
```

### **4. Configurer l'environnement**

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Modifier les variables d'environnement
nano .env  # ou utilisez votre éditeur préféré
```

**Variables d'environnement requises :**

```ini
# PostgreSQL
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/smart_ao

# Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_api_key

# Redis
REDIS_URL=redis://localhost:6379/0

# API
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=True

# Sécurité
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### **5. Initialiser la base de données**

```bash
# Créer les tables
python scripts/init_db.py

# Ou utiliser Alembic pour les migrations
alembic upgrade head
```

---

## **⚡ DÉMARRAGE RAPIDE**

### **Démarrer le serveur API**

```bash
# Mode développement
uvicorn app.main:app --reload --port 8000

# Mode production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### **Accéder à l'API**

- **URL :** `http://localhost:8000`
- **Documentation Swagger :** `http://localhost:8000/docs`
- **Documentation ReDoc :** `http://localhost:8000/redoc`

### **Tester avec curl**

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Lister les agents
curl http://localhost:8000/api/v1/agents

# Créer une mission
curl -X POST http://localhost:8000/api/v1/missions \
  -H "Content-Type: application/json" \
  -d '{"docs": ["dce.pdf"], "context": {}, "created_by": "user"}'
```

---

## **🎛️ CONFIGURATION**

### **Configuration de Base**

Le fichier `app/core/config.py` gère toutes les configurations via des variables d'environnement.

**Exemple de configuration avancée :**

```ini
# PostgreSQL
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Rate Limiting
RATE_LIMIT_DEFAULT=100/minute
RATE_LIMIT_AUTHENTICATED=1000/minute
RATE_LIMIT_CRITICAL=10000/minute

# Circuit Breakers
CIRCUIT_BREAKER_MAX_FAILURES=5
CIRCUIT_BREAKER_TIMEOUT=30
CIRCUIT_BREAKER_RESET_TIMEOUT=60

# Workflow
WORKFLOW_MAX_PARALLEL=6
WORKFLOW_TIMEOUT=3600
```

### **Configuration des Circuit Breakers**

Les circuit breakers sont pré-configurés dans `app/core/circuit_breaker.py` :

- `DB_BREAKER` : Base de données
- `LLM_BREAKER` : Modèles de langage
- `QDRANT_BREAKER` : Recherche vectorielle
- `API_EXTERNAL_BREAKER` : APIs externes
- `MINIO_BREAKER` : Stockage d'objets

### **Configuration du Rate Limiting**

6 niveaux de rate limiting disponibles dans `app/api/middleware/rate_limiting.py` :

- `DEFAULT` : 100 requêtes/minute
- `PUBLIC` : 60 requêtes/minute
- `AUTHENTICATED` : 1000 requêtes/minute
- `CRITICAL` : 10000 requêtes/minute
- `SENSITIVE` : 10 requêtes/minute
- `DEVELOPMENT` : Illimité

---

## **🚀 API REST**

### **Endpoints Principaux**

| **Endpoint** | **Méthode** | **Description** |
|--------------|-------------|-----------------|
| `/api/v1/health` | GET | Health check du système |
| `/api/v1/agents` | GET | Lister tous les agents |
| `/api/v1/agents/{name}` | GET | Détails d'un agent |
| `/api/v1/missions` | GET | Lister toutes les missions |
| `/api/v1/missions` | POST | Créer une nouvelle mission |
| `/api/v1/missions/{id}` | GET | Détails d'une mission |
| `/api/v1/missions/{id}/status` | GET | Statut d'une mission |
| `/api/v1/documents` | GET | Lister tous les documents |
| `/api/v1/documents/upload` | POST | Upload un document |
| `/api/v1/workflows` | GET | Lister tous les workflows |
| `/api/v1/workflows/{id}/run` | POST | Exécuter un workflow |

### **Exemple de Requête**

**Créer une mission :**

```bash
curl -X POST http://localhost:8000/api/v1/missions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "docs": ["dce_2024_001.pdf", "dce_2024_002.pdf"],
    "context": {
      "mission_type": "DCE_ANALYSIS",
      "project_id": "PROJ_001",
      "priority": "HIGH"
    },
    "created_by": "engineer@company.com"
  }'
```

**Réponse :**

```json
{
  "id": "MISSION_001",
  "status": "CREATED",
  "total_steps": 6,
  "completed_steps": 0,
  "created_at": "2026-08-05T18:00:00Z",
  "updated_at": "2026-08-05T18:00:00Z"
}
```

### **Exemple de Webhook**

**S'abonner aux événements :**

```bash
curl -X POST http://localhost:8000/api/v1/events/subscribe \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "MISSION_COMPLETED",
    "callback_url": "https://your-app.com/webhook/mission-completed"
  }'
```

---

## **🤖 ENGINES**

### **Workflow Engine**

Le Workflow Engine orchestré 6 étapes d'analyse :

```
1. parser_step        → Parsing du document
2. extraction_step   → Extraction des entités
3. classification_step → Classification du document
4. agents_step       → Exécution des agents
5. compilation_step  → Compilation des résultats
6. rapport_step      → Génération du rapport
```

**Statut des étapes :**
- `PENDING` : En attente
- `RUNNING` : En cours
- `DONE` : Terminée
- `FAILED` : Échec
- `SKIPPED` : Ignorée

### **Agent Runtime**

30+ agents spécialisés disponibles :

| **Agent** | **Capacité** | **Description** |
|-----------|--------------|-----------------|
| DeadlineAgent | deadline | Analyse des délais |
| PenalitesAgent | penalites | Détection des pénalités |
| BTIndexAgent | bt_index | Indexation des documents |
| TresorerieAgent | tresorerie | Analyse financière |
| GMEAgent | gme | Gestion des risques |
| DC4Agent | dc4 | Conformité DC4 |
| RATAgent | rat | Analyse des risques |
| SOGEDAgent | soged | Vérification SOGED |
| SiteContraintesAgent | contraintes | Analyse des contraintes |
| CCTPDPGFAgent | cctp | Conformité CCTP |
| QR_TactiqueAgent | qr_tactique | Questions/réponses |
| MemoireBoosterAgent | memoire | Analyse historique |
| HandoffAgent | handoff | Transition entre étapes |
| AllotiAgent | alloti | Analyse des lots |
| RSEBoosterAgent | rse | RSE et conformité |
| CoherenceAgent | coherence | Vérification cohérence |
| VarianteAgent | variante | Gestion des variantes |
| MateriauxShieldAgent | materiaux | Analyse matériaux |
| VisiteAgent | visite | Planification visites |
| EnveloppeAgent | enveloppe | Budget enveloppe |
| AvenantAgent | avenant | Gestion des avenants |
| ContentieuxAgent | contentieux | Gestion contentieux |
| CertifAgent | certification | Certifications |
| CapaciteAgent | capacite | Analyse capacité |
| RisquesAgent | risques | Gestion des risques |
| MAPAAgent | mapa | Analyse MAPA |
| EPlusCAgent | eplusc | Études prix |
| BIMAgent | bim | Modélisation BIM |
| AssuranceAgent | assurance | Vérification assurances |

### **Event Bus**

Architecture asynchrone avec :
- **Publish/Subscribe** : Émission et réception d'événements
- **Historique** : Stockage des événements pour replay
- **Types d'événements** : 12 types prédéfinis (MISSION_CREATED, STEP_COMPLETED, etc.)

**Exemple d'utilisation :**

```python
from app.engines.event_bus.bus import EventBus, EventType
from app.engines.event_bus.models import MissionCreated

# Créer un bus
event_bus = EventBus()

# Publier un événement
event_bus.publish(MissionCreated(
    mission_id="MISSION_001",
    project_id="PROJ_001",
    mission_type="DCE_ANALYSIS"
))

# S'abonner aux événements
def on_mission_created(event: MissionCreated):
    print(f"Mission {event.mission_id} créée !")

event_bus.subscribe(EventType.MISSION_CREATED, on_mission_created)
```

---

## **📊 TESTS**

### **Exécuter les Tests**

```bash
# Tous les tests
pytest tests/unit/ tests/integration/ -v

# Tests unitaires seulement
pytest tests/unit/ -v

# Tests d'intégration seulement
pytest tests/integration/ -v

# Avec couverture de code
pytest tests/unit/ tests/integration/ --cov=app --cov-report=term

# Validation complète (Gates 1-7)
bash scripts/validate_all_gates.sh
```

### **Statistiques des Tests**

| **Type** | **Nombre** | **Statut** |
|----------|------------|------------|
| Tests Unitaires | 317 | ✅ PASS |
| Tests Intégration | 38 | ✅ PASS |
| **Total** | **355** | ✅ **100%** |

### **Couverture de Code**

- **Couverture Globale :** 90.24%
- **Modules Core :** 100% (config, security, events, etc.)
- **Objectif :** >90% ✅

---

## **📁 STRUCTURE DU PROJET**

```
SMART_AO_V7/
├── app/                          # Code source
│   ├── core/                     # Noyau
│   ├── models/                   # Modèles de données
│   ├── engines/                  # Moteurs d'analyse
│   ├── agents/                   # Agents spécialisés
│   ├── api/                      # API REST
│   ├── mcp/                      # MCP Server
│   ├── plugins/                  # Plugins
│   ├── schemas/                  # Schémas Pydantic
│   └── web/                      # Interface Web
│
├── tests/                        # Tests
│   ├── unit/                     # Tests unitaires
│   └── integration/              # Tests d'intégration
│
├── scripts/                      # Scripts utilitaires
│   ├── check_go_nogo.sh          # Validation structure
│   ├── validate_coverage.sh     # Validation couverture
│   └── validate_all_gates.sh    # Validation complète
│
├── docs/                         # Documentation
│   ├── ARCHITECTURE_V7_ENGINE.md # Architecture technique
│   ├── ENGINEERING-HANDBOOK_V7.md # Guide technique
│   ├── DEPLOYMENT_GUIDE_V7.md    # Guide de déploiement
│   └── current/                  # Documentation actuelle
│
├── builds/                       # Builds précédents
│   └── build_9/                  # Build 9
│
├── venv/                         # Environnement virtuel
├── pytest.ini                    # Configuration pytest
├── requirements.txt              # Dépendances
├── setup.py                      # Installation
├── .env.example                  # Exemple de configuration
└── README.md                     # Ce fichier
```

---

## **🔧 DÉPLOIEMENT**

### **Déploiement avec Docker**

**Dockerfile :**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Initialiser la base de données
RUN python scripts/init_db.py

# Créer un utilisateur non-root
RUN useradd -m smart_ao
USER smart_ao

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml :**

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:password@db:5432/smart_ao
      - QDRANT_URL=http://qdrant:6333
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - qdrant
      - redis

  db:
    image: postgres:14
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=smart_ao
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  qdrant:
    image: qdrant/qdrant:v1.8.0
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

  redis:
    image: redis:7
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  qdrant_data:
  redis_data:
```

**Commandes Docker :**

```bash
# Construire l'image
docker build -t smart-ao-v7 .

# Démarrer avec docker-compose
docker-compose up -d

# Voir les logs
docker-compose logs -f app

# Arrêter
docker-compose down
```

### **Déploiement avec Kubernetes**

Voir `docs/DEPLOYMENT_GUIDE_V7.md` pour les configurations Kubernetes complètes.

### **CI/CD avec GitHub Actions**

**.github/workflows/test.yml :**

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: |
          pytest tests/unit/ tests/integration/ -v --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## **📖 DOCUMENTATION COMPLÈTE**

| **Document** | **Description** | **Lien** |
|--------------|-----------------|----------|
| Architecture Technique | Architecture détaillée V7 | [docs/ARCHITECTURE_V7_ENGINE.md](docs/ARCHITECTURE_V7_ENGINE.md) |
| Engineering Handbook | Guide technique complet | [docs/ENGINEERING-HANDBOOK_V7.md](docs/ENGINEERING-HANDBOOK_V7.md) |
| Manifest V7 | Philosophie et principes | [docs/current/MANIFESTE_V7.md](docs/current/MANIFESTE_V7.md) |
| Méthodologie V7 | Méthodes de développement | [docs/current/MES_V7.md](docs/current/MES_V7.md) |
| Guide de Déploiement | Déploiement production | [docs/DEPLOYMENT_GUIDE_V7.md](docs/DEPLOYMENT_GUIDE_V7.md) |
| Plan Maître | Roadmap complète | [PLAN_MAITRE_V7_FUSION_COMPLETE.md](../PLAN_MAITRE_V7_FUSION_COMPLETE.md) |
| Rapport Build 9 | Synthèse Build 9 | [RAPPORT_SYNTHESE_BUILD_9_V7.md](RAPPORT_SYNTHESE_BUILD_9_V7.md) |

---

## **🤝 CONTRIBUTION**

### **Comment Contribuer**

1. **Fork** le dépôt
2. **Créer** une branche (`git checkout -b feature/ma-fonctionnalite`)
3. **Commit** vos changements (`git commit -m 'Ajout de ma fonctionnalité'`)
4. **Push** vers la branche (`git push origin feature/ma-fonctionnalite`)
5. **Ouvrir** une Pull Request

### **Règles de Contribution**

- ✅ Respecter le style de code existant
- ✅ Ajouter des tests pour les nouvelles fonctionnalités
- ✅ Documenter les changements
- ✅ Maintenir une couverture >90%
- ✅ Suivre les conventions V7 (SSoT, DDD, etc.)

### **Conventions de Commit**

```
feat: ajouter une nouvelle fonctionnalité
fix: corriger un bug
docs: mise à jour de la documentation
style: corrections de style (espacement, format, etc.)
refactor: refactorisation de code
perf: optimisation de performance
test: ajout de tests
chore: tâches de maintenance
```

---

## **📜 LICENCE**

Ce projet est sous licence MIT. Voir [LICENSE](LICENSE) pour plus de détails.

---

## **🙏 REMERCIEMENTS**

- **Architecte Chef :** NOOR
- **Contributeurs :** Équipe SMART_AO V7
- **Technologies :** Python, FastAPI, PostgreSQL, Qdrant, Redis, SQLAlchemy, Pydantic

---

**© 2026 SMART_AO V7 - Tous droits réservés**

**Version :** Build 9 - Phase 5 - Production Ready
**Date :** 05/08/2026
**Statut :** 7/10 Gates Validés ✅
