# 🚀 SMART_AO V7.1 ENGINE OS — PLAN MAÎTRE RÉFÉRENCE ULTIME (FUSION MES)

> **Architecte Chef :** Noor | **Date :** 07/08/2026 | **Version :** 5.0 FINAL — FUSION MES INTÉGRÉE
> **Classification :** CONFIDENTIEL — NIVEAU ARCHITECTE FONDATEUR
> **Ce document REMPLACE :** MES_V7.md + PLAN_MAITRE_V7_FUSION_COMPLETE.md + PLAN_CODAGE_V7.md
> **SSoT Ordre Build :** CE DOCUMENT est désormais la source unique pour l'ordre de construction.

---

## 📋 TABLE DES MATIÈRES

**PARTIE 1 : SYNTHÈSE ET STRATÉGIE**
1. [Synthèse Exécutive](#1-synthèse-exécutive)
2. [SSoT — Hiérarchie Documentaire V7.1](#2-ssot-hiérarchie-documentaire-v71)
3. [État Initial du Projet](#3-état-initial-du-projet)

**PARTIE 2 : ARCHITECTURE ET CONCEPTION**
4. [Philosophie Build Chain V7.1](#4-philosophie-build-chain-v71)
5. [Les 9 Engines OS V7.1](#5-les-9-engines-os-v71)
6. [Graphe de Dépendances DAG V7.1](#6-graphe-de-dépendances-dag-v71)
7. [Les 10 Builds V7.1 en Détail + DoD](#7-les-10-builds-v71-en-détail--dod)

**PARTIE 3 : EXÉCUTION OPÉRATIONNELLE**
8. [Roadmap Hebdomadaire Détaillée](#8-roadmap-hebdomadaire-détaillée)
9. [Matrice de Suivi et Checklist Quotidienne](#9-matrice-de-suivi-et-checklist-quotidienne)

**PARTIE 4 : QUALITÉ ET CONTRÔLE**
10. [Gates Go/No-Go V7.1 — 39 Single / 46 Fleet](#10-gates-gono-go-v71)
11. [Tests Bloquants V7.1](#11-tests-bloquants-v71)
12. [Règles d'Or Intangibles V7.1](#12-règles-dor-intangibles-v71)

**PARTIE 5 : RÉFÉRENCES ET PROCÉDURES**
13. [Matrice Modules → Agents V7.1](#13-matrice-modules--agents-v71)
14. [Infra RAM V7.1](#14-infra-ram-v71)
15. [Procédures d'Urgence](#15-procédures-durgence)
16. [Commandes Utiles](#16-commandes-utiles)
17. [Structure des Commits Git](#17-structure-des-commits-git)

**PARTIE 6 : ANNEXES**
18. [Annexes Complètes](#18-annexes)

---

## PARTIE 1 : SYNTHÈSE ET STRATÉGIE

### 1. SYNTHÈSE EXÉCUTIVE

#### 1.1 Objectif Global

Reconstruire SMART_AO V7.1 depuis ZÉRO selon l'Arborescence_V7.1.txt (368 fichiers) en 10-12 semaines, avec :

- ✅ Structure 100% conforme à Arborescence_V7.1.txt (368 fichiers)
- ✅ Code compilable et testable à chaque étape
- ✅ Migration V6→V7.1 sans Big Bang (100% rétrocompatible)
- ✅ 39/39 tests Single verts (Single-Tenant)
- ✅ 46/46 tests Fleet verts (Multi-VPS)
- ✅ Production Ready avec Go/No-Go automatisés

#### 1.2 Fusion MES → PLAN_MAITRE

| Avant (V7.0) | Après (V7.1) |
|---|---|
| MES_V7.md (ordre build séparé) | **FUSIONNÉ dans ce document** |
| PLAN_CODAGE_V7.md (checklist séparée) | **FUSIONNÉ dans ce document** |
| PLAN_MAITRE_V7.md (pilotage séparé) | **CE DOCUMENT — source unique** |
| 3 documents pour l'ordre | **1 document pour l'ordre** |

**Règle :** Si un développeur cherche "dans quel ordre builder", il ouvre CE document. Point final.

#### 1.3 Score Initial vs Cible

| Catégorie | État Initial | Cible V7.1 | Écart | Statut |
|---|---|---|---|---|
| Fichiers Python | 7 fichiers | 368 fichiers | -361 | 🔴 |
| Structure | Non conforme | Arborescence_V7.1 | À créer | 🔴 |
| Tests Single | 1❌ | 39 tests | -38 | 🔴 |
| Tests Fleet | 0 | 46 tests | -46 | 🔴 |
| Engines | 3⚠️ partiels | 9 + 2 Edge | -8 | 🔴 |
| Agents | 2 | 33 + 2 plugins | -33 | 🔴 |
| Builds terminés | 0 | 10 builds (0-9 + 9.5) | -10 | 🔴 |

#### 1.4 Les 5 Piliers de la Réussite

🎯 **Pilier 1 : Documentation Parfaite (Bible)**

La hiérarchie SSoT V7.1 est désormais :

```
MANIFESTE_V7.md        = Pourquoi (commercial, 33 boucliers, prix)
RAPPORT (1).md         = Que fait produit (33 modules §7.1-7.33)
ARCHITECTURE_V7_ENGINE = Architecture OS (9 Engines, BaseAgent, ADR)
CE DOCUMENT            = Ordre + Pilotage (Builds 0-9.5, roadmap, suivi)
HANDBOOK_V7.md         = Comment technique pur (ADR 001-063, C4, tests)
Arborescence_V7.1.txt  = Où ranger les fichiers (368 fichiers)
```

**Règles de conflit INTANGIBLES :**
- Fonctionnel/Commercial → RAPPORT (1).md gagne
- Technique pur → ENGINEERING-HANDBOOK_V7 gagne
- Architecture OS → ARCHITECTURE_V7_ENGINE.md gagne
- **Ordre Build → CE DOCUMENT gagne (ex-MES + PLAN_CODAGE fusionnés)**
- Structure fichiers → Arborescence_V7.1.txt gagne

🎯 **Pilier 2 : Phasage Réaliste (10-12 Semaines)**

"On ne pose pas les fenêtres avant les fondations."
"On ne pose pas les Applications (agents) avant le Kernel (Workflow+Registry+EventBus)."

🎯 **Pilier 3 : Règles Bloquantes**

Aucune violation des règles d'or (voir §12). Chaque build = compilable, testable, stable.

🎯 **Pilier 4 : Parallélisation Intelligente**

Build 2 || Build 4 après Build 1 (zéro dépendance Vault/RAG pour Garage).

🎯 **Pilier 5 : Zéro Big Bang**

Feature flag `USE_WORKFLOW_ENGINE` jusqu'à Build 9. Rollback possible à tout moment.

---

### 2. SSoT — HIÉRARCHIE DOCUMENTAIRE V7.1

> **Cette section remplace l'ancien §1 de MES_V7.md.**

| Document | Rôle unique SSoT | Ne contient PAS |
|---|---|---|
| MANIFESTE V7.1 | Commercial Pourquoi + 33 boucliers + prix | Aucune tech |
| RAPPORT (1).md | SEULE source fonctionnelle 33 modules §7.1-7.33 + P0 §6 | Pas d'ordre build |
| ARCHITECTURE_V7_ENGINE.md | SEULE source architecture OS — 9 Engines, BaseAgent, Registry, Mission, EventBus, 5 schémas | Pas de détail fonctionnel module, pas de mem_limit |
| **CE DOCUMENT (PLAN_MAITRE)** | **Ordre build V7.1 0-9.5, graphe DAG 9 Engines, gates 39/46, DoD par Build, roadmap, suivi** | Pas de détail fonctionnel → Voir RAPPORT §7.X, pas de contrat tech → Voir HANDBOOK |
| ENGINEERING-HANDBOOK V7.1 | Technique pur ADR 001-063, C4, contrats API, schémas, mem_limit, tests 39/46 | Pas de redéfinition fonctionnelle |
| Arborescence V7.1 | Liste finale V7.1 engines/ + agents/ (368 fichiers) | Sans historique |

**Règle anti-dette V7.1 :** Si module défini dans RAPPORT §7.X, ce document ne le redéfinit PAS. Si architecture définie dans ARCHITECTURE_V7, ce document référence uniquement.

---

### 3. ÉTAT INITIAL DU PROJET

> **Cette section remplace l'ancien §2 du PLAN_MAITRE et §3 de MES_V7.md.**

#### 3.1 Fichiers Existants V7.1 (368/368 fichiers)

##### 3.1.1 Structure Complète V7.1

On part de **ZÉRO** et on reconstruit SMART_AO V7.1 selon Arborescence_V7.1.txt (368 fichiers) en 10-12 semaines.

**Fichiers existants validés :**
- Structure 100% conforme à Arborescence_V7.1.txt
- Tous fichiers Python déplacés/renommés et validés (py_compile OK)
- Tous `__init__.py` créés (engines, agents, tests, e2e, models, schemas)
- Configuration complète (requirements.txt, setup.py, .env)
- Imports absolus fonctionnels (zéro imports relatifs)

##### 3.1.2 Documentation Existante V7.1 (7 documents BIBLE)

| Document | Rôle | SSoT Pour | Statut V7.1 |
|----------|------|-----------|--------------|
| Arborescence_V7.1.txt | Structure physique (368 fichiers) | STRUCTURE | ✅ BIBLE |
| ARCHITECTURE_V7_ENGINE.md | Architecture OS 9 Engines + 2 Edge | ARCHITECTURE | ✅ BIBLE |
| ENGINEERING-HANDBOOK_V7.1.md | Technique pure (ADR 001-063) | TECHNIQUE | ✅ BIBLE |
| **PLAN_MAITRE_V7.1** (ce doc) | Ordre Build 0-9 + 9.5 + Pilotage | ORDRE + PILOTAGE | ✅ BIBLE |
| RAPPORT (1).md | Fonctionnel 33 modules §7.1-7.33 | FONCTIONNEL | ✅ BIBLE |
| MANIFESTE_V7.md | Vision produit 33 boucliers | COMMERCIAL | ⚠️ À corriger |

---

## PARTIE 2 : ARCHITECTURE ET CONCEPTION

### 4. PHILOSOPHIE BUILD CHAIN V7.1

> **Cette section remplace l'ancien §2 de MES_V7.md.**

Principe fondateur V12 (ADR-013) conservé : On découpe par dépendances techniques, pas par fonctionnalités. Chaque Build = compilable, testable, stable.

- V6 : 10 Builds 0-8 avec 3.5 et 4.5 intercalaires
- V7 : 10 Builds 0-9 re-spécifiés OS
- **V7.1 : 10 Builds 0-9 + Build 9.5 (Fleet + DLQ + Local LLM)**

Séquence V7.1 :
```
Fondations → Données+Mission → Document+Vault → Knowledge+Security
→ Math → Kernel (EventBus+Workflow+Registry+DLQ)
→ Agents Apps → Edge (API+UI+Notif) → MCP+Plugin
→ Durcissement → Build 9.5 Fleet & Durcissement final
```

On ne pose pas les fenêtres avant les fondations. En V7.1, on ne pose pas les Applications (agents) avant le Kernel (Workflow+Registry+EventBus+DLQ).

---

### 5. LES 9 ENGINES OS V7.1

> **Cette section remplace l'ancien §3 de MES_V7.md et l'ancien §3.2 du PLAN_MAITRE.**

| Layer | Engine | Fonction Principale | Localisation | Build |
|---|---|---|---|---|
| L0 | Security Engine | RBAC 33 modules, O_NOFOLLOW, FileLock, WORM, ClamAV, Argon2id, JWT vps_id | app/engines/security_engine/ | 3 |
| L1 | Document Engine | Parser PyMuPDF/pdfplumber, Docling worker isolé, OCR, chunking, 47 pièces classif | app/engines/document_engine/ | 2 |
| L2 | Knowledge Engine | RAG Hybrid BGE-M3 1024dim, Qdrant on_disk RRF, FTS btp_french, **Local LLM Fallback** | app/engines/knowledge_engine/ | 3 |
| L3 | Math Engine | 16 solveurs ZERO LLM : PuLP, OR-Tools, Decimal 28 to_decimal(str) | app/engines/math_engine/ | 4 |
| L4 | Agent Runtime | Registry, cycle de vie, supervision, can_handle scoring | app/engines/agent_runtime/ | 5 |
| L5 | Workflow Engine | Mission, 6 Steps, tour de contrôle, persistance Postgres, rejouabilité | app/engines/workflow_engine/ | 5 |
| L6 | Event Bus | Pub/Sub intra-VPS asyncio + persistence + **DLQ + Cron Reconciliation** | app/engines/event_bus/ | 5 |
| L7 | Notification Engine | Deadline J-7/J-2, Post-Gagné J-30/J-15/J-3, Certif J-90/J-60/J-30, ICS, email, WebSocket | app/engines/notification_engine/ | 7 |
| L8 | Plugin Engine | Chargement agents externes BIM/Assurance sans redéploiement | app/engines/plugin_engine/ | 8 |
| **L9** | **Fleet Management Engine** | **Pull-based updates, cosign verify, docker pull chiffré, heartbeat licensing** | app/engines/fleet_engine/ | **9.5** |
| Edge | API Gateway | Auth, rate-limit, routing → délègue au Workflow Engine | app/engines/api_gateway/ | 7 |
| Edge | UI Engine | Rendering, streaming SSE/WebSocket depuis Workflow Engine | app/engines/ui_engine/ | 7 |

---

### 6. GRAPHE DE DÉPENDANCES DAG V7.1

> **Cette section remplace l'ancien §4 de MES_V7.md et l'ancien §6 du PLAN_MAITRE.**

```
Build 0 [Fondations & Sécurité]
  Docker FastAPI PG Redis MinIO Qdrant Auth Argon2id JWT vps_id 2FA TOTP
  logs WORM check_ram.sh 16/32
   │
   ▼
Build 1 [Données & State Machine + Mission]
  Vault A01-A12, Project 15 statuts HANDOFF irreversible,
  Mission + MissionStep + Event modèles, ALLOWED_TRANSITIONS
   │
   ├───────────────────────────────────┐
   │                                   │
   ▼                                   ▼
Build 2 [Vault & Document Engine]    Build 4 [Math Engine] ← PARALLÉLISABLE
  OCR PyMuPDF/pdfplumber/tesseract    16 solveurs ZERO LLM Decimal 28
  ClamAV EICAR                        PuLP OR-Tools
  FS isolation O_NOFOLLOW+fstat       bt_projection INSEE 36m
  Document Engine Parser + Docling    penalites_cumul P0 10%/5%/CCMI∞+1000
  Event DocumentAnalyse               rep_cost ADEME, site_coeff
   │                                  + 5 solveurs V7.1 (penibilite,
   │                                    vigilance, zan, formule, sourcing)
   │                                  data/referentiels 13 JSON
   ▼                                   │
Build 3 [Knowledge + Security Engine]  │
  BGE-M3 1024d on_disk RRF + FTS      │
  Local LLM Fallback (Mistral 7B)     │
  Confidentialité detector             │
  RBAC 33 modules strip_provisions     │
   │                                   │
   ├───────────────────┘               │
   │                                   │
   ▼                                   ▼
Build 5 [Kernel OS]
  EventBus asyncio.Queue + PG + DLQ + Cron Reconciliation
  WorkflowEngine Mission 6 steps retry timeout persistance PG
  AgentRuntime Registry find_by_capability can_handle 0-1 lifecycle
  BaseAgent contrat unique 4 props + 2 méthodes ZERO EUR
   │
   ▼
Build 6 [Agents V7.1 — Applications OS]
  33 agents migres BaseAgent app/agents/agent_*.py @registry.register
  12 historiques + 16 V6 + 5 V7.1
  IA ZERO EUR → JSON quali → Math Engine chiffre
   │
   ▼
Build 7 [Edge — API + UI + Notification]
  API Gateway délègue WorkflowEngine
  UI Engine WebSocket SSE streaming Mission
  Notification Engine Deadline/PostGagne/Certif
   │
   ▼
Build 8 [MCP + Plugin Engine]
  BOAMP radar 6h idempotent publie DCERecu sur EventBus
  PLACE, update-agent heartbeat whitelist 0 métier
  Plugin Engine Manifest YAML importlib DI sans redéploiement
   │
   ▼
Build 9 [Durcissement & Prod V7.1]
  Go/No-Go 39 Single / 46 Fleet
  backup AES-256-GCM <15min
  Prometheus, ClamAV Fleet
  E2E 3 DCE 412p 47 pièces
   │
   ▼
Build 9.5 [Fleet & Durcissement Final V7.1] ← NOUVEAU
  Fleet Management Engine: Pull-based update + cosign verify
  DLQ EventBus: Cron reconciliation + replay stuck events
  Local LLM Fallback: DCE Confidentiel → Ollama Mistral 7B
  Tests V7.1: 8 nouveaux tests verts
  E2E: 3 DCE réels + 1 DCE Confidentiel Défense + 1 MAPA
```

**Validation :** DAG sans cycle. 33 modules / 16 solveurs + gates DEPOSE V6 + 7 gates V7 + 8 gates V7.1.

---

### 7. LES 10 BUILDS V7.1 EN DÉTAIL + DoD

> **Cette section fusionne les anciens §5-6 de MES_V7.md avec les anciens §5 du PLAN_MAITRE.**

#### Vue Synthétique

| Build | Nom V7.1 | Objectif | Livrables clés | Gate |
|---|---|---|---|---|
| 0 | Fondations | Sécurité base | Docker, Auth, WORM, check_ram | Auth vert |
| 1 | Données+Mission | State Machine + Mission | Project 15 statuts + Mission 6 steps + Event | test_mission_model |
| 2 | Document Engine | Vault+Parser | Document Engine + Docling worker + Vault J-30 | test_document_engine |
| 3 | Knowledge+Security | RAG+RBAC+Local LLM | Knowledge Engine + Security Engine RBAC 33 | test_hybrid_search + test_rbac_33 |
| 4 | Math Engine | Garage 16 solveurs | math_engine 16 solveurs Decimal P0 preserve | 16 tests solveurs |
| 5 | Kernel OS | EventBus+Workflow+Registry+DLQ | EventBus + DLQ + WorkflowEngine + BaseAgent + Registry | test_workflow + test_event_bus + test_registry + test_dlq |
| 6 | Agents Apps | 33 agents BaseAgent | app/agents/ 33 agents @register | test_33_agents + test_base_contract |
| 7 | Edge | API+UI+Notif | API Gateway + UI WebSocket + Notif Deadline | test_api_gateway + test_ui_streaming |
| 8 | MCP+Plugin | Automatisation+Extensibilité | BOAMP→EventBus + Plugin Engine Manifest | test_plugin_load |
| 9 | Prod V7.1 | Durcissement 39/46 | check_go_nogo 39/46 + backup + E2E 3 DCE | 39/39 + 46/46 verts |
| 9.5 | Fleet V7.1 | Fleet+DLQ+Local LLM | Fleet Engine + DLQ + Local LLM + 8 tests V7.1 | 8 tests V7.1 verts |

#### Build 0 — DoD
- Docker compose mem_limit/oom_score_adj profils 16Go pic 14.3/21.5
- Auth Argon2id JWT vps_id 2FA TOTP logs WORM
- check_ram.sh refuse <16Go
- **Gate :** Auth + JWT + 2FA + check_ram.sh vert

#### Build 1 — DoD
- Models Vault A01-A12 + Project 15 statuts HANDOFF irreversible + Mission + MissionStep + Event
- Migrations alembic 0016 + 0017 mission + 0018 events
- **Gate :** test_mission_model.py vert : création Mission 6 steps persistance PG replay

#### Build 2 — DoD
- Document Engine parser PyMuPDF <2s/page + Docling worker isolé
- Upload ClamAV EICAR + FS isolation O_NOFOLLOW+fstat+BASE_ROOT non-symlink
- Event DocumentAnalyse publié
- **Gate :** test_document_engine_parse vert

#### Build 3 — DoD
- Knowledge Engine BGE-M3 lifespan CACHE_DIR Qdrant on_disk dense+sparse RRF FTS btp_french fallback
- **Local LLM Fallback (Mistral 7B/Llama 3 via Ollama) + Confidentialité detector**
- Security Engine RBAC 33 modules FIELDS_STRIP_V6 + strip_provisions_euros_v7
- **Gate :** test_hybrid_search + test_fallback + test_rbac_33_modules_no_euro + test_local_llm_fallback verts

#### Build 4 — DoD (CRITIQUE P0)
- Math Engine déplacement mathbox→engines/math_engine 19+ fichiers ZERO LLM grep=0
- 16 solveurs Decimal to_decimal(str) PuLP OR-Tools formules opposables Voir RAPPORT §9
- P0 preserve CCAG 10%/5%/CCMI∞+seuil 1000 + avance 30%/10% + PAB + Matériaux
- **5 solveurs V7.1 :** penibilite_solver, vigilance_solver, zan_solver, formule_algebra_checker, sourcing_api_solver
- **Gate :** 16 tests solveurs verts + scan ZERO LLM passe

#### Build 5 — DoD (Kernel OS)
- EventBus asyncio.Queue + PG events persistance + replay mission_id + subscribe decorator
- **DLQ (Dead Letter Queue) + Cron Reconciliation toutes les heures**
- WorkflowEngine Mission 6 steps retry timeout semaphore 6 max persistance PG
- AgentRuntime Registry register find_by_capability find_by_tags get_all can_handle scoring
- BaseAgent contrat unique 4 props + 2 méthodes ZERO EUR garanti
- **Gate :** test_event_bus.py + test_workflow_engine.py + test_registry_discovery.py + test_dlq_reconciliation.py verts
- Mission #254 avec 3 pilotes DONE

#### Build 6 — DoD (Apps)
- 33 agents migrés BaseAgent app/agents/agent_*.py @registry.register
- can_handle >=0.2 filtre pertinence, scoring tri
- AgentOutput findings ZERO EUR + source_pages traçabilité
- **5 agents V7.1 :** agent_penibilite_rh, agent_vigilance_urssaf, agent_zan_trackterres, agent_formule_revision, agent_sourcing_api
- **Gate :** test_33_agents_trap_detector + test_agent_no_euro + test_base_agent_contract verts

#### Build 7 — DoD (Edge)
- API Gateway POST /api/dce/analyze crée Mission soumet WorkflowEngine, plus d'if/else
- UI Engine WebSocket /ws/mission/{id} streaming steps
- Notification Engine Deadline J-7/J-2/H-4 ICS + PostGagné J-30/J-15/J-3 + Certif J-90/J-60/J-30
- **Gate :** test_api_gateway_delegates + test_ui_streaming verts + RBAC 33 modules conservé

#### Build 8 — DoD
- MCP BOAMP publie DCERecu sur EventBus, plus d'appel direct
- Plugin Engine Manifest YAML importlib DI chargement sans redéploiement
- **Gate :** test_plugin_engine_load vert : BIMAgent externe chargé sans redéploiement

#### Build 9 — DoD (Prod V7.1)
- check_go_nogo.sh 39/39 Single + check_go_nogo_fleet.sh 46/46 Fleet verts
- 7 critères V7 verts + 24/31 V6 verts + 8 nouveaux V7.1 verts
- Backup AES-256-GCM quotidien restore <15min @500Mbps AES-NI
- E2E 3 DCE réels 412p 47 pièces Go/No-Go 39 critères <48h

#### Build 9.5 — DoD (Fleet & Durcissement Final V7.1) ← NOUVEAU
- Fleet Management Engine : Pull-based update + cosign verify + docker pull chiffré
- DLQ EventBus : Cron reconciliation + replay stuck events
- Local LLM Fallback : DCE Confidentiel → Ollama Mistral 7B
- Tests V7.1 : 8 nouveaux tests verts
- E2E : 3 DCE réels 412p + 1 DCE Confidentiel Défense + 1 MAPA
- **Gate :** test_fleet_update + test_dlq_reconciliation + test_local_llm_fallback + 5 tests modules V7.1 verts

---

## PARTIE 3 : EXÉCUTION OPÉRATIONNELLE

### 8. ROADMAP HEBDOMADAIRE DÉTAILLÉE

> **Cette section remplace l'ancien §7 du PLAN_MAITRE.**

#### 8.1 Philosophie du Phasage V7.1

> "On ne pose pas les fenêtres avant les fondations."
> "On ne pose pas les Applications (agents) avant le Kernel (Workflow+Registry+EventBus+DLQ)."

**Ordre strict DAG V7.1 :**
1. Fondations (Build 0) → 2. Données+Mission (Build 1) → 3. Document+Vault || Math (Builds 2 || 4) → 4. Knowledge+Security (Build 3) → 5. Kernel OS (Build 5) → 6. Agents Apps (Build 6) → 7. Edge (Build 7) → 8. MCP+Plugin (Build 8) → 9. Durcissement (Build 9) → 9.5. Fleet+DLQ+Local LLM

**Principes DAG :**
- Valider chaque build avant de passer au suivant (principe DAG strict)
- Paralléliser intelligemment : Build 2 || Build 4 après Build 1
- Maintenir feature flag `USE_WORKFLOW_ENGINE` jusqu'à Build 9
- Rollback possible à tout moment

#### 8.2 Roadmap par Phase (10-12 Semaines)

| Phase | Semaines | Builds | Objectifs | Tests Cible | Completion |
|-------|----------|--------|-----------|-------------|-------------|
| **Phase 0** | S0 ✅ | Build 0 | Préparation + Structure + Sécurité | - | 100% DONE |
| **Phase 1** | S1-2 | Builds 1-2 | Fondations (Données + Vault + Document + Mission) | 10/39 Single | 26% |
| **Phase 2** | S3-4 | Builds 3-4 | Cœur Technique (Knowledge + Security + Math + 5 solveurs V7.1) | 20/39 Single | 51% |
| **Phase 3** | S5-7 | Builds 5-6 | Orchestration + Agents (33/33) + Fleet Engine | 30/39 Single | 77% |
| **Phase 4** | S8 | Builds 7-8 | Interface (API Gateway + UI Engine + MCP + Plugin) | 35/39 Single | 90% |
| **Phase 5** | S9-12 | Builds 9-9.5 | Production (Durcissement + Go/No-Go 39/46 + DLQ + Local LLM) | **39/39 + 46/46** | **100%** |

#### 8.3 Détail par Semaine

##### Semaine 0 : PRÉPARATION (1 jour - DONE)
**Objectif :** Préparer l'environnement et comprendre chaque détail
- T0.1 : Parser Arborescence_V7.1.txt → file_list_v7.1.csv
- T0.2 : Audit détaillé des fichiers existants
- T0.3 : Matrice de mapping Existant → Cible V7.1
- T0.4 : Atelier de validation avec Architecte
- T0.5 : Créer dépôt Git propre
- T0.6 : Configurer environnement Python 3.11+
- T0.7 : Créer bootstrap_v7.1.py
- T0.8 : Validation finale Week 0

**Livrables :** file_list_v7.1.csv, audit_existant_v7.1.md, mapping_existant_cible_v7.1.md, bootstrap_v7.1.py
**Statut :** ✅ DONE

##### Semaine 1 : FONDATIONS (5 jours - JOUR 1 à 5)
**Objectif :** Créer la structure complète et déplacer le code existant

**JOUR 1 :** Génération de la Structure Complète
- T1.1 : Exécuter bootstrap_v7.1.py
- T1.2 : Vérifier tous les dossiers créés (368 fichiers)
- T1.3 : Ajouter .gitkeep dans dossiers vides
- T1.4 : Créer app/__init__.py avec imports conditionnels

**JOUR 2 :** Déplacement Code Existant (Batch 1 - Agents)
- T2.1-T2.4 : Déplacer base_agent, registry, agent_deadline, agent_pab
- T2.5-T2.6 : Corriger imports dans tous les agents existants
- T2.7 : Tester import global

**JOUR 3 :** Déplacement Code Existant (Batch 2 - Engines)
- T3.1-T3.5 : Déplacer mission.py, workflow.py, bus.py, + 2 nouveaux engines V7.1
- T3.6-T3.7 : Corriger imports dans workflow.py, mission.py, bus.py
- T3.8-T3.10 : Créer __init__.py pour tous les engines

**JOUR 4 :** Déplacement Test + Correction Imports
- T4.1-T4.3 : Déplacer tous les tests existants
- T4.4-T4.6 : Corriger TOUS les imports dans les tests
- T4.7-T4.8 : Ajouter __init__.py dans tests/unit/ et tests/
- T4.9 : Tester et vérifier import global

**JOUR 5 :** Nettoyage et Validation Hebdomadaire
- T5.1 : Supprimer dossier obsolète (ex: Codes/)
- T5.2 : Vérifier tous les fichiers existants déplacés
- T5.3 : Audit complet py_compile
- T5.4 : Créer validate_structure_v7.1.py
- T5.5 : Exécuter validate_structure_v7.1.py
- T5.6 : Commit Git : `git commit -m "S1: Fondations V7.1 - Structure + 8 fichiers migres"`
- T5.7 : Réunion de validation Semaine 1

**Livrables :** Structure complète SMART_AO/ avec 368 fichiers, 8+ fichiers Python déplacés et fonctionnels, 10 tests E2E passant
**Validation :** 10/39 Single verts ✅

##### Semaine 2 : CŒUR TECHNIQUE (5 jours - JOUR 6 à 10)
**Objectif :** Implémenter les composants critiques manquants pour atteindre 20/39 tests

**JOUR 6 :** Agent Runtime et Lifecycle
- T6.1 : Créer app/engines/agent_runtime/__init__.py
- T6.2 : registry.py déjà déplacé (vérifier)
- T6.3 : Créer lifecycle.py (AgentLifecycle class)
- T6.4 : Créer app/agents/__init__.py (auto-discovery)
- T6.5 : Mettre à jour app/engines/__init__.py
- T6.6 : Test test_registry_discovery.py vert

**JOUR 7 :** Event Bus Complet + DLQ
- T7.1-T7.3 : Créer __init__.py, models.py, replay.py, dlq.py (V7.1)
- T7.4 : Corriger bus.py si nécessaire
- T7.5 : Créer cron_reconciliation.py (V7.1)
- T7.6 : Test test_event_bus.py vert
- T7.7 : Test test_dlq_reconciliation.py vert (V7.1)

**JOUR 8 :** Workflow Engine Complet
- T8.1-T8.3 : __init__.py, mission.py, workflow.py déjà faits
- T8.4-T8.11 : Créer steps/__init__.py, parser_step.py, extraction_step.py, classification_step.py, agents_step.py, compilation_step.py, rapport_step.py, persistence.py
- T8.12 : Test test_workflow_engine.py vert

**JOUR 9 :** Modèles et Schémas Critiques
- T9.1-T9.3 : Créer app/models/__init__.py, mission.py, events.py
- T9.4-T9.7 : Créer app/schemas/__init__.py, mission.py, event.py, agent.py
- T9.8 : Test test_mission_model.py vert

**JOUR 10 :** Validation Hebdomadaire Semaine 2
- T10.1 : Exécuter TOUS les tests existants
- T10.2 : Corriger les échecs
- T10.3 : Audit de code pylint + bandit
- T10.4 : Commit Git : `git commit -m "S2: Coeur V7.1 - 8 Engines + 2 Edge implantes"`
- T10.5 : Réunion de validation Semaine 2

**Livrables :** Cœur V7.1 fonctionnel, 20/39 Single verts ✅, Structure 100% conforme

##### Semaine 3 : MATH ENGINE + 5 SOLVEURS V7.1 (5 jours - JOUR 11 à 15)
**Objectif :** Implémenter Math Engine complet avec 5 nouveaux solveurs V7.1

**JOUR 11 :** Math Engine Base (CRITIQUE P0)
- T11.1-T11.4 : Créer __init__.py, types.py, decimal_ops.py, treasury.py
- T11.5-T11.7 : Créer margin.py, planning.py, worst_case.py
- T11.8 : Déplacer mathbox → engines/math_engine (19 fichiers)
- T11.9 : Vérifier ZERO import LLM (grep bloquant)
- T11.10 : Test test_math_engine_no_llm_import.py vert

**JOUR 12 :** 5 Nouveaux Solveurs V7.1
- T12.1 : Créer penibilite_solver.py (7.29)
- T12.2 : Créer vigilance_solver.py (7.30)
- T12.3 : Créer zan_solver.py (7.31)
- T12.4 : Créer formule_algebra_checker.py (7.32)
- T12.5 : Créer sourcing_api_solver.py (7.33)
- T12.6 : Intégrer dans math_engine/__init__.py
- T12.7 : Tests unitaires pour chaque solveur
- T12.8 : **16 solveurs total** (11 V6 + 5 V7.1) validés

**JOUR 13 :** Knowledge Engine + Local LLM Fallback
- T13.1-T13.5 : Compléter knowledge_engine/ (embedding, vault_semantic_search, etc.)
- T13.6-T13.7 : Créer local_llm.py + confidentialite_detector.py (V7.1)
- T13.8 : Configurer Ollama Mistral 7B pour DCE Confidentiel
- T13.9 : Test test_hybrid_search + test_local_llm_fallback verts (V7.1)

**JOUR 14 :** Security Engine + RBAC 33 modules
- T14.1-T14.5 : Créer __init__.py, rbac.py, filesystem.py, audit.py, clamav.py
- T14.6 : Mettre à jour RBAC pour 33 modules (FIELDS_STRIP_V7)
- T14.7 : Test test_rbac_33_modules_no_euro vert (V7.1)

**JOUR 15 :** Validation Hebdomadaire Semaine 3
- T15.1-T15.2 : Exécuter tests et corriger échecs
- T15.3 : Audit sécurité bandit + radon
- T15.4 : Commit Git : `git commit -m "S3: Coeur Technique V7.1 - Math 16 solveurs + Knowledge + Security"`
- T15.5 : Réunion de validation Semaine 3

**Livrables :** 9 Engines + 2 Edge complets, 16 solveurs, 25/39 Single verts ✅, 0 vulnérabilité critique

##### Semaine 4 : AGENTS (5 jours - JOUR 16 à 20)
**Objectif :** Créer les 33 agents BaseAgent pour atteindre 30/39 tests

**JOUR 16 :** Création des 11 premiers Agents (Batch 1)
- agent_bt_index.py, agent_penalites.py, agent_tresorerie.py, agent_gme.py, agent_dc4.py
- agent_rat.py, agent_soged.py, agent_site_contraintes.py, agent_cctp_dpgf.py, agent_qr_tactique.py
- agent_memoire_booster.py
- Tests : test_base_agent_contract.py vert pour Batch 1

**JOUR 17 :** Création des 11 Agents suivants (Batch 2)
- agent_handoff.py, agent_alloti.py, agent_rse_booster.py, agent_coherence.py
- agent_variante.py, agent_materiaux_shield.py, agent_visite.py, agent_enveloppe.py
- agent_avenant.py, agent_contentieux.py, agent_certif.py
- Tests : test_28_agents_trap_detector.py vert

**JOUR 18 :** Création des 11 derniers Agents (Batch 3) + 5 V7.1
- agent_capacite.py, agent_risques.py, agent_mapa.py, agent_eplusc.py
- agent_penibilite_rh.py (7.29), agent_vigilance_urssaf.py (7.30)
- agent_zan_trackterres.py (7.31), agent_formule_revision.py (7.32)
- agent_sourcing_api.py (7.33)
- Tests : test_33_agents_trap_detector.py vert

**JOUR 19 :** Edge Components (API Gateway + UI Engine)
- T19.1-T19.3 : Créer api_gateway/__init__.py, workflow_delegate.py, deps.py
- T19.4-T19.6 : Créer ui_engine/__init__.py, websocket_manager.py, sse.py
- T19.7 : Test test_api_gateway_delegates.py vert
- T19.8 : Test test_ui_streaming.py vert

**JOUR 20 :** Finalisation Semaine 4
- T20.1-T20.2 : Exécuter tests et corriger échecs
- T20.3 : Commit Git : `git commit -m "S4: Agents V7.1 - 33/33 agents + Edge implantes"`
- T20.4 : Réunion de validation Semaine 4

**Livrables :** 33 agents complets, 30/39 Single verts ✅

##### Semaine 5-7 : KERNEL OS + FLEET ENGINE (3 semaines)
**Objectif :** Compléter Build 5 (Kernel OS) + Build 9.5 (Fleet Engine)

- **Build 5 :** EventBus+Workflow+Registry+DLQ intégrés
- **Build 6 :** 33 agents migrés BaseAgent
- **Build 9.5 :** Fleet Management Engine + Local LLM + DLQ
- **Atteindre :** 35/39 Single verts

##### Semaine 8 : MCP + PLUGIN ENGINE
**Objectif :** Implémenter MCP externes et Plugin Engine
- MCP BOAMP : radar 6h, publie DCERecu sur EventBus
- PLACE : update-agent heartbeat whitelist
- Plugin Engine : Manifest YAML, DI sans redéploiement
- Tests : test_plugin_engine_load.py, test_boamp_mcp.py verts
- **Atteindre :** 35/39 Single + 30/46 Fleet verts

##### Semaines 9-12 : PRODUCTION + GO/NO-GO
**Objectif :** Tests Fleet, Durcissement, Validation Finale
- **Semaine 9 :** Compléter tests Fleet (38→46)
- **Semaine 10 :** Backup/restore AES-256-GCM validé
- **Semaine 11 :** E2E 3 DCE réels 412p + 1 DCE Confidentiel
- **Semaine 12 :** Go/No-Go 39/39 + 46/46 verts
- **Livraison :** `v7.1-engine-os-1.0` ✅ 100% COMPLET

#### 8.4 Résumé des Phases et Livrables V7.1

| Phase | Semaines | Builds | Objectifs | Tests Cible | Livrables | Statut |
|-------|----------|--------|-----------|-------------|------------|--------|
| **Phase 0** | S0 ✅ | Build 0 | Préparation + Structure | - | Environnement prêt | ✅ DONE |
| **Phase 1** | S1-2 | Builds 1-2 | Fondations | 10/39 Single | Structure 368 fichiers | ✅ |
| **Phase 2** | S3-4 | Builds 3-4 | Cœur Technique | 20/39 Single | 9 Engines + 16 solveurs | ✅ |
| **Phase 3** | S5-7 | Builds 5-6 | Orchestration | 30/39 Single | Kernel OS + 33 agents | ✅ |
| **Phase 4** | S8 | Builds 7-8 | Interface | 35/39 Single | API+UI+MCP+Plugin | ✅ |
| **Phase 5** | S9-12 | Builds 9-9.5 | Production | **39/39 + 46/46** | **LIVRAISON FINALE** | ✅ |

---

### 9. MATRICE DE SUIVI ET CHECKLIST QUOTIDIENNE

> **Cette section remplace l'ancien §8 du PLAN_MAITRE.**

#### 9.1 Tableau de Bord Global V7.1

| Phase | Semaines | Builds | Tests Single (Cible/Réel) | Tests Fleet (Cible/Réel) | Completion | Statut | Blocages |
|-------|----------|--------|---------------------------|---------------------------|-------------|--------|----------|
| Phase 0 | S0 ✅ | Build 0 | - / - | - / - | 100% | ✅ DONE | Aucun |
| Phase 1 | S1-2 | Builds 1-2 | 10 / ___ | - / ___ | ___% | IN PROGRESS | ___ |
| Phase 2 | S3-4 | Builds 3-4 | 20 / ___ | - / ___ | ___% | PENDING | ___ |
| Phase 3 | S5-7 | Builds 5-6 | 30 / ___ | 0 / ___ | ___% | PENDING | ___ |
| Phase 4 | S8 | Builds 7-8 | 35 / ___ | 30 / ___ | ___% | PENDING | ___ |
| Phase 5 | S9-12 | Builds 9-9.5 | 39 / ___ | 46 / ___ | ___% | PENDING | ___ |

**Objectif Final :** 39/39 Single + 46/46 Fleet = 100% Go/No-Go vert

#### 9.2 Tableau de Bord par Semaine

| Semaine | Phase | Builds | Objectifs | Tests Single Cible/Réel | Tests Fleet Cible/Réel | Completion | Statut | Blocages |
|--------|-------|--------|-----------|----------------------------|---------------------------|-------------|--------|----------|
| **S0** | Phase 0 | Build 0 | Préparation | - / - | - / - | 100% | ✅ DONE | - |
| **S1** | Phase 1 | Builds 0-1 | Fondations | 10 / ___ | - / ___ | ___% | IN PROGRESS | ___ |
| **S2** | Phase 1 | Builds 0-2 | Fondations | 10 / ___ | - / ___ | ___% | IN PROGRESS | ___ |
| **S3** | Phase 2 | Builds 3 | Cœur Technique | 15 / ___ | - / ___ | ___% | PENDING | ___ |
| **S4** | Phase 2 | Builds 3-4 | Cœur Technique | 20 / ___ | - / ___ | ___% | PENDING | ___ |
| **S5** | Phase 3 | Build 5 | Orchestration | 25 / ___ | 0 / ___ | ___% | PENDING | ___ |
| **S6** | Phase 3 | Builds 5-6 | Orchestration | 28 / ___ | 0 / ___ | ___% | PENDING | ___ |
| **S7** | Phase 3 | Build 6 | Agents | 30 / ___ | 0 / ___ | ___% | PENDING | ___ |
| **S8** | Phase 4 | Builds 7-8 | Interface | 35 / ___ | 30 / ___ | ___% | PENDING | ___ |
| **S9** | Phase 5 | Build 9 | Durcissement | 39 / ___ | 40 / ___ | ___% | PENDING | ___ |
| **S10** | Phase 5 | Build 9 | Durcissement | 39 / ___ | 44 / ___ | ___% | PENDING | ___ |
| **S11** | Phase 5 | Build 9.5 | Fleet | 39 / ___ | 46 / ___ | ___% | PENDING | ___ |
| **S12** | Phase 5 | Build 9.5 | LIVRAISON | **39/39** | **46/46** | **100%** | **SUCCESS** | - |

#### 9.3 Checklist Quotidienne

**À exécuter chaque jour avant commit :**

```
[ ] Code compilable : python -m py_compile app/**/*.py → NO ERROR
[ ] Tests Single exécutés : pytest tests/unit/ -v → ___/39 Single
[ ] Tests Fleet exécutés : pytest tests/unit/ -k fleet -v → ___/46 Fleet
[ ] Nombre de fichiers créés : ___/368
[ ] Commit Git : git commit -m "Jour X: [description]" → DONE
[ ] Push Git : git push origin main → DONE
[ ] Blocages identifiés : [Liste]
[ ] Validation Architecte : ✅ GO / ❌ NO-GO
```

**Commandes de vérification rapide :**
```bash
# Vérifier structure
python -m py_compile app/**/*.py

# Lancer tests
pytest tests/unit/ -v --tb=short
pytest tests/unit/ -k fleet -v --tb=short

# Vérifier imports
python -c "from app import engines, agents, models, schemas"

# Vérifier Go/No-Go
./scripts/check_go_nogo.sh
./scripts/check_go_nogo_fleet.sh
```
```
[ ] Code compilable : python -m py_compile app/**/*.py → NO ERROR
[ ] Tests Single exécutés : pytest tests/unit/ -v → ___/39 Single
[ ] Tests Fleet exécutés : pytest tests/unit/ -k fleet -v → ___/46 Fleet
[ ] Nombre de fichiers créés : ___/368
[ ] Commit Git : git commit -m "Jour X: [description]" → DONE
[ ] Push Git : git push origin main → DONE
[ ] Blocages identifiés : [Liste]
[ ] Validation Noor : ✅ GO / ❌ NO-GO
```

---

## PARTIE 4 : INTÉGRATION V3.2 → V7.1 — PLAN DE MIGRATION TECHNIQUE

> **Cette partie intègre le rapport d'audit "V3.2 to V7.1" et définit la stratégie de migration.**
> **SSoT Intégration :** Ce document section §14-17 + RAPPORT (1).md §7.1-7.33 + ARCHITECTURE_V7_ENGINE.md §7-8

### 14. CONTEXTE ET STRATÉGIE D'INTÉGRATION

#### 14.1 Diagnostic V3.2 : 4 Frictions Mortelles à Corriger

La V3.2 est un excellent MVP Desktop, mais présente 4 failles structurelles pour le marché BTP français 2026 (marchés publics hostiles, inflation, ZAN, pénurie main-d'œuvre) :

| # | Friction | Risque BTP | Correction V7.1 |
|---|----------|------------|-----------------|
| **1** | Péril Hallucinatoire | LLM calcule les chiffres → erreur virgule ou marge inventée = **PAB ou faillite** | **Ségrégation Cognitive** : Knowledge Engine (IA) lit/extrait/classe ZERO €. Math Engine (Garage) calcule avec **PuLP, OR-Tools, Decimal 28** (16 solveurs, corrections P0 CCAG 10%/5%/CCMI). |
| **2** | Myopie Sémantique | pgvector aveugle au jargon BTP (CCAG vs CCMI, DTU, clauses révision) | **Qdrant** (mode `on_disk`) + embeddings **BGE-M3 1024d** + Recherche Hybride (Dense + Sparse RRF) + Fallback Full-Text Search Postgres avec dictionnaire custom `btp_french`. |
| **3** | Monolithe Synchrone | API FastAPI avec endpoints métiers bloquants → freeze wizard si parsing 200 pages | **Architecture OS avec 9 Engines** + 33 modules = Agents (`BaseAgent`) orchestrés par `WorkflowEngine` (6 étapes canoniques) via `EventBus` asynchrone (`asyncio.Queue` + persistance PG + DLQ). |
| **4** | Absence d'Étanchéité Financière | Pas de ségrégation stricte des données financières dans les réponses API | **RBAC V7.1** = survie pour le Patron. **Salarié = Zéro € visible** (sinon fuite = mort). **Patron = Finance Warfare Dashboard**. `Security Engine` applique `strip_provisions_euros_v7` sur chaque réponse API + génère double artefact HANDOFF+. |

#### 14.2 Stratégie "Pont Tauri" : Greffer V7.1 sous le capot Tauri

**Objectif :** Conserver le shell Tauri Desktop (Anti-ERP, UX fluide, Mode Panique) tout en remplaçant son cerveau par le Kernel V7.1 Single-Tenant.

**Philosophie :** La V3.2 = bonne base UX sur mauvaise base technique. V7.1 = excellente base technique, UX à parfaire. **Solution : transplanter le cœur V7.1 sous le shell V3.2.**

**3 actifs UX V3.2 à sauver (irremplaçables) :**
1. ✅ **Shell Tauri** — Application Desktop native (React/TS/Tailwind/Zustand) → devient Client Edge Natif
2. ✅ **Mode Panique** (Ctrl+Shift+M) → transformé en **Mission `priority=URGENTE`** fast-track
3. ✅ **Onboarding 5 étapes** → seul morceau UX manquant à construire

**Tout le reste de V3.2 est soit déjà supérieur dans V7.1, soit à abandonner (chatbot).**

**Bilan intégration :** 8 RÉUTILISER · 8 ADAPTER · 3 CONSTRUIRE · 1 MIGRER (pgvector→Qdrant) · 1 ABANDONNER (Chat Orchestrateur).

### 15. MATRICE D'INTÉGRATION FONCTIONNELLE V3.2 → V7.1 (21 fonctions)

> **Source unique :** Rapport d'audit V3.2 to V7.1 Passe 2/2 §I

| # | Fonction v3.2 | Atterrissage V7.1 | Statut V7.1 | Verdict | Sprint |
|---|---------------|------------------|-------------|---------|--------|
| 1 | App Desktop Tauri v2 (React/TS/Tailwind/Zustand) | Edge UI Engine + shell Tauri | UI Engine présent (stubs), Tauri absent | 🟡 **ADAPTER** : conserver shell Tauri, consomme API Gateway + WS V7.1 | V32-1 |
| 2 | Onboarding 5 étapes | Absent | Absent | 🔵 **CONSTRUIRE** : wizard onboarding (serveur, LLM, Vault) | V32-2 |
| 3 | Wizard 12 étapes | Wizard 10 étapes (PLAN_WIZARD) + 12 étapes RAPPORT | Partiel | 🟡 **ADAPTER** : aligner sur 10 étapes, préserver UX v3.2 | V32-2 |
| 4 | Mode Panique (<48h / Ctrl+Shift+M) | Absent | Absent | 🔵 **CONSTRUIRE** : Mission `URGENTE` fast-track | V32-2 |
| 5 | Chat Orchestrateur (intent) | Absent (doctrine : pas de chatbot) | Absent | ⚫ **ABANDONNER** (feature flag ENABLE_CHAT=false) | - |
| 6 | Go/No-Go scoring adaptation | Go/No-Go 39/46 gates | Présent | 🟢 **RÉUTILISER** : mapper scoring sur gates | - |
| 7 | Extraction métré (CCTP + DPGF/OCR) | Document Engine + Cross-Check 7.9 | Partiel | 🟡 **ADAPTER** | V32-1 |
| 8 | Chiffrage déboursé sec + OR-Tools | Math Engine `chiffrage_pulp` + `planning` OR-Tools | Présent | 🟢 **RÉUTILISER** | - |
| 9 | Audit conformité DTU | Knowledge Engine RAG (DTU) | Partiel | 🟡 **ADAPTER** | V32-1 |
| 10 | Analyse clauses + Rapport Négociation | Q/R Tactique 7.10 + Contentieux 7.23 | Présent | 🟢 **RÉUTILISER** | - |
| 11 | 45+ documents générés | Générateurs DOCX/PDF | Partiel | 🟡 **ADAPTER** | V32-3 |
| 12 | Sélecteur ZIP manuel | Enveloppe Separator 7.21 | Présent | 🟡 **ADAPTER** : UI sélection manuelle | V32-2 |
| 13 | Licences & Watermark (demo/essentiel/pro) | Fleet `license_checker` | Partiel | 🟡 **ADAPTER** : watermark demo + perpetual | V32-3 |
| 14 | Profil entreprise qualifié | Vault A01-A12 | Présent | 🟢 **RÉUTILISER** | - |
| 15 | Analytics & Dashboard | Dashboards cockpit | Présent | 🟢 **RÉUTILISER** | - |
| 16 | Workflow multi-utilisateurs | RBAC rôles (PATRON/SALARIÉ) | Présent | 🟢 **RÉUTILISER** | - |
| 17 | RAG historique entreprise | Collection Qdrant `chantiers` | Présent | 🟢 **RÉUTILISER** | - |
| 18 | Charte graphique personnalisée | Personnalisation entreprise | Partiel | 🟡 **ADAPTER** | V32-3 |
| 19 | Export Word natif | Génération DOCX | Partiel | 🟢 **RÉUTILISER** (python-docx) | - |
| 20 | Stack pgvector/Redis/MinIO/Compose 1 cmd | Qdrant/Redis/MinIO/Compose | Présent | 🔵 **MIGRER** : pgvector→Qdrant | V32-1 |
| 21 | CLI `smartao` / `--dev` / `--web` / `--stop` | scripts/ | Partiel | 🟡 **ADAPTER** : CLI unifié | V32-1 |

**Bilan final intégration :** La v3.2 n'apporte presque rien de *nouveau* sur le métier (V7.1 est strictement supérieur), mais apporte **3 actifs UX irremplaçables** : le shell Tauri, le Mode Panique, et l'onboarding.

### 16. SPRINTS D'INTÉGRATION V3.2 → V7.1 (Ordre imposé : V32-1 → V32-2 → V32-3)

> **Règle critique :** Ne pas toucher au Kernel V7.1 pendant ces sprints. Maintenir feature flag `USE_WORKFLOW_ENGINE` jusqu'à validation complète.

#### Sprint V32-1 : Ponts Stack (1-2 semaines)

**Objectif :** Établir les fondations techniques de la migration.

| Élément | Description | Fichiers concernés | Gate |
|---------|-------------|-------------------|------|
| Routeur LLM OpenAI-compatible | Hérite du choix v3.2, impose défaut souverain Mistral EU, local Ollama pour DCE Confidentiel | `app/engines/knowledge_engine/llm_router.py` | ✅ Routeur fonctionnel + test vert |
| Migration pgvector→Qdrant | Script one-shot : lire embeddings pgvector v3.2, upsert dans Qdrant avec payload complet | `scripts/migrate_pgvector_qdrant.py` | ✅ Migration 100% chunks sans perte |
| CLI unifié `smartao` | Hérite CLI v3.2, unifie backend + Tauri | `scripts/smartao` | ✅ CLI fonctionnel |
| Pont Tauri ↔ UI Engine (WebSocket) | Tauri conserve WebView, se branche sur WS V7.1 `/ws/mission/{id}` | `desktop/src/bridge.ts` | ✅ Streaming temps réel |

**Livrables V32-1 :**
- `llm_router.py` avec support Mistral EU + opt-in OpenAI/DeepSeek + local Ollama
- `migrate_pgvector_qdrant.py` exécutable et testé
- `scripts/smartao` unifié (backend + Tauri + web + stop)
- `desktop/src/bridge.ts` avec WebSocket vers UI Engine

**Gate V32-1 :** Routeur + migration verts + CLI fonctionnel

#### Sprint V32-2 : Mode Panique + Onboarding (1-2 semaines)

**Objectif :** Implémenter les fonctionnalités UX critiques de V3.2 dans V7.1.

| Élément | Description | Fichiers concernés | Gate |
|---------|-------------|-------------------|------|
| Mode Panique → Mission URGENTE | Mission à priorité URGENTE, fast-track, bypass agents longs | `app/engines/workflow_engine/mission.py` + `workflow.py` | ✅ Mode Panique E2E <3min |
| FAST_TRACK_CAPS | Liste des capabilities essentiels pour le mode panique | `app/engines/workflow_engine/workflow.py` | ✅ Agents survie seulement |
| Déclencheur | `deadline < 48h` auto OU raccourci `Ctrl+Shift+M` Tauri → POST `/api/dce/analyze` avec `priority="URGENTE"` | Tauri + API Gateway | ✅ Déclenchement validé |
| Onboarding 5 étapes | Bienvenue → connexion VPS → routeur LLM → import Vault A01-A12 → premier AO golden file | UI Tauri + Backend | ✅ Onboarding complet |

**Code Mode Panique (extrait) :**
```python
# app/engines/workflow_engine/mission.py
class MissionPriority(str, Enum):
    BASSE = "BASSE"
    NORMALE = "NORMALE"
    HAUTE = "HAUTE"
    URGENTE = "URGENTE"  # MODE PANIQUE

# app/engines/workflow_engine/workflow.py
FAST_TRACK_CAPS = {
    "CHECK_DEADLINE", "GENERER_DC4", "SEPARER_ENVELOPPE",
    "DETECTER_PAB", "GENERER_MEMOIRE_TEMPLATE", "GENERER_DPGF_TEMPLATE",
}
async def run(self, mission: Mission) -> Mission:
    if mission.priority == MissionPriority.URGENTE:
        mission.context["fast_track"] = True
        mission.context["needed_capabilities"] = sorted(FAST_TRACK_CAPS)
        # bypass des agents longs (Mémoire Booster, RSE)
```

**Livrables V32-2 :**
- Mission URGENTE implémentée et testée
- FAST_TRACK_CAPS défini et fonctionnel
- Onboarding 5 étapes opérationnel
- Intégration Tauri → V7.1 validée

**Gate V32-2 :** Mode Panique E2E <3min, ZIP minimum vital généré

#### Sprint V32-3 : Modèle Commercial + Licences (1 semaine)

**Objectif :** Réconciliation des modèles commerciaux V3.2 (licence perpétuelle 3700€) et V7.1 (549€/mois).

| Élément | Description | Fichiers concernés | Gate |
|---------|-------------|-------------------|------|
| Fleet Engine `license_checker` | Support des deux modèles : perpétuel (3700€) + abonnement (549€/mois) + demo | `app/engines/fleet_engine/license_checker.py` | ✅ Licences perpétuelles validées |
| LicenseType | Énumération des types de licence | `app/engines/fleet_engine/license_checker.py` | ✅ Typage validé |
| Watermark | Absent pour perpétuels, présent pour demo | `app/engines/fleet_engine/license_checker.py` | ✅ Watermark correct |
| Règle commerciale | Clients v3.2 perpétuels gardent licence sans watermark mais **sans** boucliers V7.1 (7.29-7.33) sauf upgrade | Fleet Engine + Manifeste | ✅ Règle documentée |

**Code License Checker (extrait) :**
```python
# app/engines/fleet_engine/license_checker.py
class LicenseType(str, Enum):
    PERPETUELLE = "perpetuelle"   # héritage v3.2 (3 700€)
    ABONNEMENT  = "abonnement"    # 549€/mois
    DEMO        = "demo"

class LicenseChecker:
    def check(self, key: str) -> LicenseType: ...
    def watermark(self, lt: LicenseType):
        return None if lt == LicenseType.PERPETUELLE else "DEMO - NON VALABLE POUR DEPOT"
```

**Livrables V32-3 :**
- `license_checker.py` avec support perpétuel/abonnement/demo
- Règles de watermark implémentées
- Clients V3.2 perpétuels honorés sans watermark
- Nouveau clients partent sur 549€/mois

**Gate V32-3 :** Licence perpétuelle validée sans watermark, modèle commercial réconcilié

### 17. PLAN D'ACTION CODE POUR L'ENCODEUR (Sprints priorisés)

> **Ordre imposé :** V32-1 → V32-2 → V32-3. Maintenir feature flag `USE_WORKFLOW_ENGINE` pendant ces sprints.

| Sprint | Contenu | Fichiers | Gate | Durée |
|--------|---------|---------|------|-------|
| **V32-1** | Ponts stack : routeur LLM, migrate pgvector→Qdrant, CLI unifié, pont Tauri WS | `llm_router.py`, `migrate_pgvector_qdrant.py`, `scripts/smartao`, `desktop/src/bridge.ts` | Routeur + migration verts | 1-2 semaines |
| **V32-2** | Mode Panique + onboarding | `mission.py` (URGENTE), `workflow.py` (FAST_TRACK), wizard onboarding | Mode Panique E2E <3min | 1-2 semaines |
| **V32-3** | Modèle commercial : license_checker perpétuel/abonnement + watermark | `fleet_engine/license_checker.py` | Licence perpétuelle validée sans watermark | 1 semaine |

**Condition de succès finale :**
- V32-1/2/3 verts
- ET 39/39 Single + 46/46 Fleet verts
- → Produit prêt : shell agréable V3.2 + cerveau souverain V7.1

**Risque zéro :** Pas de big bang. Rollback possible à tout moment via feature flag.

### 18. GO/NO-GO D'INTÉGRATION V3.2 → V7.1

| Critère | Exigence | Statut | Sprint |
|---------|----------|--------|--------|
| Shell Tauri branché sur API Gateway + WS V7.1 | WS streaming OK | À construire | V32-1 |
| Mode Panique = Mission URGENTE fast-track | E2E <3min, ZIP minimum vital | À construire | V32-2 |
| pgvector→Qdrant sans perte | upsert 100% chunks | À exécuter | V32-1 |
| Licences perpétuelles v3.2 honorées | watermark absent pour perpétuels | À construire | V32-3 |
| Chat Orchestrateur | désactivé par défaut | Décision : ABANDONNER | - |
| Gates V7.1 | 39/39 Single + 46/46 Fleet | Inchangés, bloquants | Tous |

**Verdict final :** L'intégration est faisable en 3 sprints (V32-1/2/3) sans casser le Kernel. Une fois V32-1/2/3 verts ET 39/39 + 46/46 verts, le produit est le monopole décrit : le shell agréable de la v3.2, le cerveau souverain et le coffre-fort de la V7.1.

---

## PARTIE 5 : QUALITÉ ET CONTRÔLE

### 10. GATES GO/NO-GO V7.1 — 39 SINGLE / 46 FLEET

> **Cette section remplace l'ancien §7 de MES_V7.md et l'ancien §9 du PLAN_MAITRE.**

**24 Single V6 + 7 V7 + 8 V7.1 = 39 Single**
**31 Fleet V6 + 7 V7 + 8 V7.1 = 46 Fleet**

#### 7 critères V7 (conservés) :
1. test_workflow_engine.py vert
2. test_event_bus.py vert
3. test_registry_discovery.py vert
4. test_base_agent_contract.py vert
5. test_math_engine_no_llm_import après déplacement vert
6. test_mission_e2e_3_agents vert
7. test_plugin_engine_load.py vert

#### 8 critères V7.1 (NOUVEAUX) :
8. test_penibilite_rh.py vert — Détection contraintes + Vault A04 + surcoût intérim
9. test_vigilance_urssaf.py vert — Blocage DC4 attestation >6 mois + exposition
10. test_zan_trackterres.py vert — Coût évacuation + ISDI + Trackterres
11. test_formule_revision.py vert — Σ(coeffs)=1 + indices INSEE + Q/R
12. test_sourcing_api.py vert — DUME JSON + push API + horodatage
13. test_local_llm_fallback.py vert — DCE Confidentiel → Mistral 7B local
14. test_dlq_reconciliation.py vert — Events stuck → DLQ → replay
15. test_fleet_update.py vert — Pull-based update cosign verify

**Gate BLOQUANT :** Si un critère rouge, interdiction 1er client payant.
Script `check_go_nogo.sh` et `check_go_nogo_fleet.sh` = vert obligatoire.

Voir RAPPORT §12 pour définition fonctionnelle + HANDBOOK V7.1 §5 pour détails techniques.

---

### 11. TESTS BLOQUANTS V7.1

> **Cette section remplace l'ancien §9 du PLAN_MAITRE et §7 de MES_V7.md.**

**Total :** 39 tests Single + 46 tests Fleet = 85 tests bloquants

#### 11.1 Classification des Tests V7.1

| Catégorie | Nombre | Description | Priorité | Statut Cible |
|-----------|--------|-------------|----------|--------------|
| Tests Single VPS | 39 | Tests unitaires Single-Tenant | CRITICAL | 39/39 verts |
| Tests Fleet Multi-VPS | 46 | Tests multi-VPS | CRITICAL | 46/46 verts |
| Tests E2E | 3+ | Tests bout-en-bout avec DCE réels | CRITICAL | Tout vert |
| **Total** | **85+** | - | - | **100%** |

#### 11.2 Liste des 39 Tests Single V7.1

**Build 0 - Fondations & Sécurité (5 tests)**
| N | Test | Module | Build | Priorité | Statut |
|---|------|--------|-------|----------|--------|
| 1 | test_auth_argon2id.py | Auth | 0 | CRITICAL P0 | ✅ |
| 2 | test_jwt_vps_id.py | Auth | 0 | CRITICAL P0 | ✅ |
| 3 | test_2fa_totp.py | Auth | 0 | CRITICAL P0 | ✅ |
| 4 | test_check_ram_16_32.py | Infra | 0 | CRITICAL | ✅ |
| 5 | test_filesystem_isolation.py | Security | 0 | CRITICAL P0 | ✅ |

**Build 1 - Données & Mission (3 tests)**
| N | Test | Module | Build | Priorité | Statut |
|---|------|--------|-------|----------|--------|
| 6 | test_state_machine.py | Project | 1 | CRITICAL | ✅ |
| 7 | test_handoff_irreversible.py | Project | 1 | CRITICAL | ✅ |
| 8 | test_mission_model.py | Mission | 1 | CRITICAL | ✅ |

**Build 2 - Document Engine (3 tests)**
| N | Test | Module | Build | Priorité | Statut |
|---|------|--------|-------|----------|--------|
| 9 | test_document_engine_parse.py | Document Engine | 2 | CRITICAL | ✅ |
| 10 | test_vault_upload.py | Vault | 2 | HIGH | ✅ |
| 11 | test_vault_expiry.py | Vault | 2 | HIGH | ✅ |

**Build 3 - Knowledge + Security (5 tests)**
| N | Test | Module | Build | Priorité | Statut |
|---|------|--------|-------|----------|--------|
| 12 | test_hybrid_search.py | Knowledge Engine | 3 | CRITICAL | ✅ |
| 13 | test_fallback.py | Knowledge Engine | 3 | HIGH | ✅ |
| 14 | test_local_llm_fallback.py | Knowledge Engine | 3 | CRITICAL V7.1 | ✅ |
| 15 | test_rbac_33_modules_no_euro.py | Security Engine | 3 | CRITICAL P0 | ✅ |
| 16 | test_confidentialite_detector.py | Security Engine | 3 | CRITICAL V7.1 | ✅ |

**Build 4 - Math Engine (8 tests)**
| N | Test | Module | Build | Priorité | Statut |
|---|------|--------|-------|----------|--------|
| 17 | test_math_engine_no_llm_import.py | Math Engine | 4 | CRITICAL P0 | ✅ |
| 18 | test_math_engine_chiffrage_pulp.py | Math Engine | 4 | CRITICAL P0 | ✅ |
| 19 | test_math_engine_treasury.py | Math Engine | 4 | CRITICAL P0 | ✅ |
| 20 | test_penalites_cumul.py | Math Engine | 4 | CRITICAL P0 | ✅ |
| 21 | test_pab_detector.py | Math Engine | 4 | CRITICAL P0 | ✅ |
| 22 | test_materiaux_shield.py | Math Engine | 4 | CRITICAL P0 | ✅ |
| 23 | test_penibilite_rh.py | Math Engine | 4 | CRITICAL V7.1 | ✅ |
| 24 | test_vigilance_urssaf.py | Math Engine | 4 | CRITICAL V7.1 | ✅ |

**Build 5 - Kernel OS (5 tests)**
| N | Test | Module | Build | Priorité | Statut |
|---|------|--------|-------|----------|--------|
| 25 | test_event_bus.py | EventBus | 5 | CRITICAL | ✅ |
| 26 | test_workflow_engine.py | Workflow Engine | 5 | CRITICAL | ✅ |
| 27 | test_registry_discovery.py | Registry | 5 | CRITICAL | ✅ |
| 28 | test_dlq_reconciliation.py | EventBus DLQ | 5 | CRITICAL V7.1 | ✅ |
| 29 | test_base_agent_contract.py | BaseAgent | 5 | CRITICAL | ✅ |

**Build 6 - Agents Apps (3 tests)**
| N | Test | Module | Build | Priorité | Statut |
|---|------|--------|-------|----------|--------|
| 30 | test_33_agents_trap_detector.py | 33 Agents | 6 | CRITICAL | ✅ |
| 31 | test_agent_no_euro.py | Agents | 6 | CRITICAL P0 | ✅ |
| 32 | test_28_agents_trap_detector.py | Agents Batch 2 | 6 | CRITICAL | ✅ |

**Build 7 - Edge (2 tests)**
| N | Test | Module | Build | Priorité | Statut |
|---|------|--------|-------|----------|--------|
| 33 | test_api_gateway_delegates.py | API Gateway | 7 | HIGH | ✅ |
| 34 | test_ui_streaming.py | UI Engine | 7 | HIGH | ✅ |

**Build 8 - MCP + Plugin (2 tests)**
| N | Test | Module | Build | Priorité | Statut |
|---|------|--------|-------|----------|--------|
| 35 | test_plugin_engine_load.py | Plugin Engine | 8 | HIGH | ✅ |
| 36 | test_mcp_boamp.py | MCP BOAMP | 8 | HIGH | ✅ |

**Build 9 - Production (3 tests)**
| N | Test | Module | Build | Priorité | Statut |
|---|------|--------|-------|----------|--------|
| 37 | test_fleet_update.py | Fleet Engine | 9 | CRITICAL V7.1 | ✅ |
| 38 | test_formule_revision.py | Math Engine | 9 | CRITICAL V7.1 | ✅ |
| 39 | test_sourcing_api.py | Math Engine | 9 | CRITICAL V7.1 | ✅ |

#### 11.3 Liste des 46 Tests Fleet V7.1

**Tests Fleet par Catégorie (à exécuter avec `-k fleet`)**

| N | Test | Description | Priorité |
|---|------|-------------|----------|
| F1-F31 | Tests Single adaptés Fleet | 31 tests V6 adaptés | CRITICAL |
| F32-F38 | Tests V7 adaptés Fleet | 7 tests V7 adaptés | CRITICAL |
| F39-F46 | **Nouveaux Tests V7.1 Fleet** | 8 tests V7.1 | CRITICAL V7.1 |

**Nouveaux Tests Fleet V7.1 :**
1. test_fleet_pull_based_update.py - Fleet Management Engine
2. test_fleet_cosign_verify.py - Cosign verification
3. test_fleet_docker_pull_encrypted.py - Docker pull chiffré
4. test_dlq_fleet_events.py - DLQ multi-VPS
5. test_dlq_cron_reconciliation_fleet.py - Cron reconciliation Fleet
6. test_local_llm_fallback_fleet.py - Local LLM Fleet
7. test_penibilite_rh_fleet.py - Module 7.29 Fleet
8. test_vigilance_urssaf_fleet.py - Module 7.30 Fleet

#### 11.4 Tests P0 Bloquants (15 tests critiques)

| ID | Test | Règle | Conséquence |
|----|------|-------|-------------|
| P0-1 | test_math_engine_no_llm_import.py | Zéro import LLM dans Math Engine | ❌ FAIL Bloquant |
| P0-2 | test_agent_no_euro.py | Zéro € dans AgentOutput.findings | ❌ FAIL Bloquant |
| P0-3 | test_filesystem_isolation.py | Imports absolus + isolation | ❌ FAIL Bloquant |
| P0-4 | test_base_agent_contract.py | Tous agents héritent de BaseAgent | ❌ FAIL Bloquant |
| P0-5 | test_rbac_33_modules_no_euro.py | RBAC Financier étanche 33 modules | ❌ FAIL Bloquant |
| P0-6 | test_2fa_totp.py | Auth 2FA TOTP | ❌ FAIL Go/No-Go |
| P0-7 | test_jwt_vps_id.py | JWT vps_id | ❌ FAIL Go/No-Go |
| P0-8 | test_check_ram_16_32.py | RAM 16Go minimum | ❌ FAIL Go/No-Go |
| P0-9 | test_handoff_irreversible.py | HANDOFF+ double artefact | ❌ FAIL Bloquant |
| P0-10 | test_math_engine_chiffrage_pulp.py | Solveurs P0 | ❌ FAIL Bloquant |
| P0-11 | test_penalites_cumul.py | Pénalités P0 | ❌ FAIL Bloquant |
| P0-12 | test_pab_detector.py | PAB détecté | ❌ FAIL Bloquant |
| P0-13 | test_materiaux_shield.py | Matériaux P0 | ❌ FAIL Bloquant |
| P0-14 | test_dlq_reconciliation.py | DLQ fonctionnel | ❌ FAIL Bloquant |
| P0-15 | test_fleet_update.py | Fleet Engine | ❌ FAIL Bloquant |

**Gate BLOQUANT :** Si UN SEUL test P0 est rouge, interdiction premier client payant.
**Scripts :** `check_go_nogo.sh` (39 Single) et `check_go_nogo_fleet.sh` (46 Fleet) doivent être VERTS.

---

### 12. RÈGLES D'OR INTANGIBLES V7.1

> **Cette section remplace l'ancien §9 de MES_V7.md et l'ancien §10 du PLAN_MAITRE.**

#### Règles de Codage (BLOQUANTES)

| ID | Règle | Test Bloquant | Conséquence |
|---|---|---|---|
| R1 | Zéro import LLM dans Math Engine | test_math_engine_no_llm_import.py | ❌ FAIL Bloquant |
| R2 | Zéro € dans AgentOutput.findings | test_agent_no_euro.py | ❌ FAIL Bloquant |
| R3 | Zéro tenant_id dans code métier | Linter Go/No-Go | ❌ FAIL Go/No-Go |
| R4 | Tous agents héritent de BaseAgent | test_base_agent_contract.py | ❌ FAIL Bloquant |
| R5 | Tous agents ont @registry.register() | Agent non découvert | ❌ FAIL Agent ignoré |
| R6 | Tous imports absolus | test_absolute_imports.py | ❌ FAIL ImportError |
| R7 | Chaque dossier a un __init__.py | test_init_py_exists.py | ❌ FAIL Module not found |

#### Règles Métier (CRITIQUES)

| ID | Règle | Source | Test |
|---|---|---|---|
| RBAC | Salarié = zéro € | RAPPORT §3.1 | test_rbac_* |
| HANDOFF+ | Double artefact irréversible | RAPPORT §7.12 | test_handoff_* |
| Vault | J-30 readonly + badges rouges | RAPPORT §4 | test_vault_* |
| Deadline | Blocage dépôt si rouge | RAPPORT §7.13 | test_deadline_guardian |
| P0 | Corrections CCAG/PAB/Matériaux | RAPPORT §6 | test_penalites_*, test_pab_*, test_materiaux_* |

#### Règles V7.1 (NOUVELLES)

| ID | Règle | Source | Test |
|---|---|---|---|
| V7.1-1 | Fleet Engine pull-based cosign | ARCHITECTURE §7 ADR-059 | test_fleet_update |
| V7.1-2 | Local LLM Fallback DCE Confidentiel | ARCHITECTURE §7 ADR-060 | test_local_llm_fallback |
| V7.1-3 | DLQ EventBus reconciliation | ARCHITECTURE §7 ADR-061 | test_dlq_reconciliation |
| V7.1-4 | 5 modules métier 7.29-7.33 | RAPPORT §7.29-7.33 | 5 tests modules |

---

## PARTIE 5 : RÉFÉRENCES ET PROCÉDURES

### 13. MATRICE MODULES → AGENTS V7.1

> **Cette section remplace l'ancien §8 de MES_V7.md.**

33 modules V7.1 §7.1-7.33 mappés vers Agents V7.1 app/agents/ :

| Module | Agent | Capabilities |
|---|---|---|
| 7.1 BT Index Guardian | agent_bt_index.py | ["DETECTER_BT", "CALCULER_PROJECTION_BT"] |
| 7.2 Pénalités | agent_penalites.py | ["DETECTER_PENALITES", "CALCULER_PLAFOND_PENALITES_P0"] |
| 7.3 Trésorerie | agent_tresorerie.py | ["ANALYSER_TRESORERIE", "VERIFIER_AVANCE"] |
| 7.4 GME | agent_gme.py | ["ANALYSER_GME"] |
| 7.5 DC4 | agent_dc4.py | ["GENERER_DC4"] |
| 7.6 RAT Amiante | agent_rat.py | ["ANALYSER_RAT"] |
| 7.7 SOGED | agent_soged.py | ["ANALYSER_SOGED"] |
| 7.8 Site Contraintes | agent_site_contraintes.py | ["ANALYSER_SITE"] |
| 7.9 Cross-Check | agent_cctp_dpgf.py | ["ANALYSER_CCTP", "COMPARER_DPGF"] |
| 7.10 Q/R Tactique | agent_qr_tactique.py | ["GENERER_QR", "ANALYSER_TACTIQUE"] |
| 7.11 Mémoire Booster | agent_memoire_booster.py | ["BOOSTER_MEMOIRE"] |
| 7.12 HANDOFF+ | agent_handoff.py | ["PREPARER_HANDOFF"] |
| 7.13 Deadline Guardian | agent_deadline.py | ["CHECK_DEADLINE"] is_blocking=True |
| 7.14 Alloti Guardian | agent_alloti.py | ["VERIFIER_ALLOTI"] |
| 7.15 RSE Booster | agent_rse_booster.py | ["BOOSTER_RSE"] |
| 7.16 Prix-Mémoire Coherence | agent_coherence.py | ["VERIFIER_COHERENCE"] |
| 7.17 Variante Guardian | agent_variante.py | ["ANALYSER_VARIANTE"] |
| 7.18 Matériaux Shield | agent_materiaux_shield.py | ["PROTEGER_MATERIAUX"] |
| 7.19 PAB Detector | agent_pab.py | ["DETECTER_PAB"] |
| 7.20 Visite Auto | agent_visite.py | ["PLANIFIER_VISITE"] |
| 7.21 Enveloppe Separator | agent_enveloppe.py | ["SEPARER_ENVELOPPE"] |
| 7.22 Avenant Tracker | agent_avenant.py | ["SUIVRE_AVENANT"] |
| 7.23 Contentieux Generator | agent_contentieux.py | ["GENERER_CONTENTIEUX"] |
| 7.24 Certif Live Checker | agent_certif.py | ["VERIFIER_CERTIF"] |
| 7.25 Capacité Financière | agent_capacite.py | ["CALCULER_CAPACITE"] |
| 7.26 Tableau Risques | agent_risques.py | ["GENERER_RISQUES"] |
| 7.27 MAPA Generator | agent_mapa.py | ["GENERER_MAPA"] |
| 7.28 E+C- Detector | agent_eplusc.py | ["CALCULER_EPLUSC"] |
| **7.29 Pénurie & Pénibilité RH** | **agent_penibilite_rh.py** | **["DETECTER_PENIBILITE", "CROSS_CHECK_VAULT_RH"]** |
| **7.30 Vigilance URSSAF** | **agent_vigilance_urssaf.py** | **["VERIFY_SOUS_TRAITANT_URSSAF"]** |
| **7.31 ZAN & Trackterres** | **agent_zan_trackterres.py** | **["CALCULER_COUT_EVACUATION_ZAN"]** |
| **7.32 Syntax Checker Formules** | **agent_formule_revision.py** | **["VALIDER_FORMULE_CCAP"]** |
| **7.33 Sourcing & API Profil Acheteur** | **agent_sourcing_api.py** | **["DEPOSER_API_PROFIL_ACHETEUR"]** |
| Plugin BIM | agent_bim.py | ["ANALYSER_BIM"] |
| Plugin Assurance | agent_assurance.py | ["VERIFIER_ASSURANCE"] |

Tous pointent vers RAPPORT §7.X pour fonctionnel.

---

### 14. INFRA RAM V7.1

> **Cette section remplace l'ancien §10 de MES_V7.md.**

- 14.3/21.5 Go pics V6 inchangés + EventBus asyncio léger + WorkflowEngine PG léger
- **Fleet Engine pull-based cosign** (léger, pas de daemon permanent)
- 16Go minimum / 32Go recommandé conservé
- Docling worker isolé 6Go RAM conservé
- BGE-M3 + Qdrant on_disk hybrid conservé
- **Local LLM Mistral 7B Ollama** (option 32Go+ pour DCE Confidentiel)
- Voir HANDBOOK V7.1 § infra pour mem_limit

---

### 15. PROCÉDURES D'URGENCE

> **Cette section remplace l'ancien §11 du PLAN_MAITRE.**

#### 15.1 Si un Test Échoue

1. **Identifier la cause :** Lire le traceback complet
2. **Vérifier l'environnement :** `python -m pytest tests/unit/test_<nom>.py -v`
3. **Vérifier les dépendances :** `pip list | grep -E "(pydantic|fastapi|psycopg2|qdrant)"`
4. **Vérifier la base de données :** `docker exec postgres psql -c "SELECT table_name FROM information_schema.tables;"`
5. **Corriger le code :** Ne PAS modifier le test, corriger le code source
6. **Relancer le test :** `pytest tests/unit/test_<nom>.py -v`
7. **Valider la correction :** Commit avec message clair : `git commit -m "FIX: [test_<nom>] - [description de la correction]"`
8. **Si bloqué > 4h :** Escalader immédiatement à l'Architecte

#### 15.2 Si un Import Échoue

1. **Vérifier le chemin :** `python -c "from app.engines.event_bus import bus"`
2. **Vérifier __init__.py :** Chaque dossier doit avoir `__init__.py`
3. **Vérifier la casse :** Les noms de fichiers doivent être exacts (Linux est case-sensitive)
4. **Vérifier le working directory :** `pwd` doit être la racine du projet
5. **Corriger l'import :** Utiliser UNIQUEMENT des imports absolus : `from app.engines.xxx import yyy`
6. **Tester :** `python -m py_compile app/**/*.py` doit retourner 0 erreur

#### 15.3 Si la Structure est Incorrecte

1. **Comparer avec l'arborescence :** `tree SMART_AO/ > tree_actuel.txt && diff tree_actuel.txt Arborescence_V7.1.txt`
2. **Identifier les fichiers manquants :** `comm -23 <(ls -R SMART_AO/ | sort) <(cat Arborescence_V7.1.txt | grep -v "^#" | grep -v "^>" | sort)`
3. **Créer les fichiers manquants :** `touch [fichier manquant]` + ajouter le contenu approprié
4. **Vérifier les __init__.py :** Tous les packages doivent avoir `__init__.py`
5. **Valider :** `python -c "import app"` doit fonctionner

#### 15.4 Si Blocage Technique

1. **Documenter le problème :** Créer un fichier `BLOCAGE_[date]_[problème].md` dans /docs/blocages/
2. **Inclure :**
   - Description du problème
   - Commandes exécutées
   - Erreurs complètes
   - Capture d'écran si UI
3. **Rechercher dans la documentation :** `grep -r "[mot-clé]" docs/current/`
4. **Vérifier les ADR :** `grep -r "[mot-clé]" ENGINEERING-HANDBOOK_V7.1.md`
5. **Demander de l'aide :**
   - Canal Discord : #smart-ao-v7
   - Email : architecte@smart-ao.fr
   - Réunion quotidienne : 9h30
6. **Escalade automatique si > 4h :** Bloquant = priorité absolue

#### 15.5 Si Violation d'une Règle d'Or

| Règle Violée | Action Immédiate | Responsable | Délai |
|--------------|-------------------|-------------|-------|
| Import LLM dans Math Engine | Supprimer l'import, trouver alternative | Architecte | 1h |
| € dans AgentOutput | Corriger le code pour masquer les montants | Architecte | 1h |
| tenant_id dans code | Remplacer par vps_id ou supprimer | Architecte | 1h |
| Agent sans BaseAgent | Faire hériter de BaseAgent | Développeur | 2h |
| @registry.register manquant | Ajouter le décorateur | Développeur | 1h |
| Import relatif | Remplacer par import absolu | Développeur | 1h |

**Règle :** Aucune violation d'une règle d'or n'est acceptable. Tout code violant une règle d'or doit être corrigé AVANT de passer au build suivant.

---

### 16. COMMANDES UTILES

> **Cette section remplace l'ancien §12 du PLAN_MAITRE.**

#### 16.1 Vérification Structure et Compilation

```bash
# Vérifier que tous les fichiers Python compilent
python -m py_compile app/**/*.py

# Vérifier les imports (doit retourner 0 erreur)
python -c "from app import engines, agents, models, schemas, core, mcp, worker"

# Lister tous les fichiers Python
find app/ -name "*.py" | wc -l  # Doit = 368 fichiers

# Vérifier la structure vs Arborescence
python scripts/validate_structure.py

# Compter les __init__.py
find app/ -name "__init__.py" | wc -l  # Doit = nombre de packages
```

#### 16.2 Exécution des Tests

```bash
# Tous les tests unitaires
pytest tests/unit/ -v --tb=short

# Tests Single uniquement
pytest tests/unit/ -v -k "not fleet"

# Tests Fleet uniquement
pytest tests/unit/ -v -k "fleet"

# Un test spécifique
pytest tests/unit/test_math_engine_no_llm_import.py -v

# Tests avec coverage
pytest tests/unit/ --cov=app --cov-report=html

# Vérifier Go/No-Go
./scripts/check_go_nogo.sh      # 39/39 Single requis
./scripts/check_go_nogo_fleet.sh  # 46/46 Fleet requis
```

#### 16.3 Linter et Sécurité

```bash
# Linting Python
pylint app/ --rcfile=.pylintrc
bandit -r app/ -ll  # Niveau de sécurité bas
mypy app/ --ignore-missing-imports
radon cc app/ -a  # Complexité cyclomatique

# Vérifier les imports LLM interdits dans Math Engine
grep -r "import openai\|import anthropic\|import langchain\|import mistralai" app/engines/math_engine/
echo "Exit code: $? (doit être 1 = non trouvé)"

# Vérifier les imports € interdits dans les agents
grep -r "€\|EUR\|provision\|marge\|prix\|tarif" app/agents/*.py | grep -v "# " | grep -v '"'
echo "Exit code: $? (doit être 1 = non trouvé)"
```

#### 16.4 Git

```bash
# Statut
git status
git diff --stat

# Commit
git add .
git commit -m "[TYPE]: [description] - [détails]"

# Push (après validation)
git push origin main

# Voir les commits récents
git log --oneline -20

# Créer une branche
git checkout -b feature/[nom-de-la-feature]

# Tags V7.1
git tag v7.1-s0-preparation
git tag v7.1-s1-fondations
git tag v7.1-s2-coeur
git tag v7.1-s3-engines
git tag v7.1-s4-agents
git tag v7.1-s5-edge
git tag v7.1-s8-fleet
git tag v7.1-engine-os-1.0

# Vérifier les tags
git tag -l | sort -V | tail -10
```

#### 16.5 Docker

```bash
# Builder les images
docker-compose build

# Démarrer tous les services
docker-compose up -d

# Voir les logs
docker-compose logs -f --tail=50

# Exécuter un conteneur
docker exec -it smart-ao-app bash

# Vérifier les services
./scripts/wait_for_services.sh

# Arrêter tous les services
docker-compose down

# Nettoyer (attention!)
docker system prune -a --volumes
```

#### 16.6 Base de Données (PostgreSQL)

```bash
# Se connecter
docker exec -it smart-ao-postgres psql -U postgres -d smart_ao

# Lister les tables
docker exec smart-ao-postgres psql -c "\dt"

# Voir la structure d'une table
docker exec smart-ao-postgres psql -c "\d missions"

# Exécuter les migrations Alembic
alembic upgrade head

# Vérifier les migrations
alembic current

# Backup de la base
docker exec smart-ao-postgres pg_dump -U postgres smart_ao > backup_$(date +%Y%m%d).sql

# Restore de la base
cat backup.sql | docker exec -i smart-ao-postgres psql -U postgres -d smart_ao
```

#### 16.7 Stockage et Indexation

```bash
# MinIO
mc ls smart-ao-minio/

# Qdrant
docker exec -it smart-ao-qdrant curl http://localhost:6333/collections

# Vérifier que Qdrant est en mode on_disk
docker exec smart-ao-qdrant cat /qdrant/storage/config.yaml | grep storage
```

#### 16.8 Monitoring

```bash
# Vérifier l'utilisation mémoire
docker stats --no-stream

# Vérifier l'espace disque
docker system df

# Prometheus (si configuré)
curl http://localhost:9090

# ClamAV
docker exec smart-ao-clamav freshclam
docker exec smart-ao-clamav clamscan /data/upload
```

---

### 17. STRUCTURE DES COMMITS GIT

> **Cette section remplace l'ancien §13 du PLAN_MAITRE.**

#### 17.1 Nomenclature des Commits

**Format :** `[TYPE]: [description concise] - [détails optionnels]`

| Type | Utilisation | Exemple |
|------|-------------|---------|
| `FEAT` | Nouvelle fonctionnalité | `FEAT: Ajout agent_penibilite_rh.py (7.29) - Pénurie & Pénibilité RH` |
| `FIX` | Correction de bug | `FIX: test_rbac_33_modules - Champ manquant dans FIELDS_STRIP_V7` |
| `REFACTOR` | Refactoring sans changement fonctionnel | `REFACTOR: Déplacement mathbox → engines/math_engine/` |
| `DOCS` | Documentation | `DOCS: Mise à jour ARCHITECTURE_V7_ENGINE.md §7 ADR-059-063` |
| `TEST` | Ajout/modification de tests | `TEST: Ajout test_dlq_reconciliation.py V7.1` |
| `CHORE` | Maintenance/tâches diverses | `CHORE: Mise à jour requirements.txt` |
| `BUILD` | Configuration build/Docker | `BUILD: Ajout Fleet Engine à docker-compose.yml` |
| `PERF` | Amélioration de performance | `PERF: Optimisation BGE-M3 RRF scoring` |
| `SEC` | Sécurité | `SEC: Correction vulnerability bandit CVE-2024-XXXX` |

#### 17.2 Bonnes Pratiques

1. **Commits atomiques :** Un commit = une seule logique de changement
2. **Messages clairs :** [50-72 caractères] + détails optionnels
3. **Référence aux documents :** `Voir RAPPORT §7.29` ou `Voir ARCHITECTURE §7 ADR-062`
4. **Pas de commits cassés :** Toujours vérifier que le code compile et les tests passent avant commit
5. **Squash des commits mineurs :** Utiliser `git rebase -i` pour regrouper les petits commits

#### 17.3 Workflow Git V7.1

**Workflow standard :**
```
1. git checkout main
2. git pull origin main
3. git checkout -b feature/[nom-de-la-feature]
4. [Développer + tester]
5. git add .
6. git commit -m "[TYPE]: [description]"
7. git push origin feature/[nom-de-la-feature]
8. Créer Pull Request → main
9. Attendre validation + tests CI verts
10. Merge après approval
```

**Workflow pour les corrections urgentes :**
```
1. git checkout main
2. git pull origin main
3. git checkout -b hotfix/[problème]
4. [Corriger]
5. git commit -m "FIX: [description du problème] - [solution]"
6. git push origin hotfix/[problème]
7. Créer PR → main avec label "URGENT"
8. Merge immédiat après validation
```

#### 17.4 Tags V7.1

**Tags de livraison par phase :**
```
v7.1-s0-preparation        # Fin Semaine 0 - Préparation
v7.1-s1-fondations        # Fin Semaine 1-2 - Fondations
v7.1-s2-coeur             # Fin Semaine 2-4 - Cœur Technique
v7.1-s3-engines           # Fin Semaine 5-7 - Engines complets
v7.1-s4-agents            # Fin Semaine 8 - Agents complets
v7.1-s5-edge              # Fin Semaine 8 - Edge complet
v7.1-s8-fleet             # Fin Semaine 9-12 - Fleet + Production
v7.1-engine-os-1.0       # LIVRAISON FINALE 39/39 + 46/46
```

**Créer un tag :**
```bash
git tag v7.1-s1-fondations -m "Fin Semaine 1-2: Fondations V7.1 complètes - Build 0-2"
git push origin v7.1-s1-fondations
```

**Vérifier les tags :**
```bash
git tag -l | sort -V
git show v7.1-s1-fondations
```

---

## PARTIE 6 : ANNEXES

### 18. ANNEXES

#### 18.1 Glossaire

> **Cette section remplace l'ancien §14.1 du PLAN_MAITRE. Mis à jour avec les termes V7.1.**

| Terme | Définition | Document Source |
|-------|-----------|-----------------|
| **AO** | Appel d'Offres | RAPPORT §1 |
| **BFR** | Besoin en Fonds de Roulement | RAPPORT §7.3 |
| **CCTP** | Cahier des Clauses Techniques Particulières | RAPPORT §4 |
| **CCAP** | Cahier des Clauses Administratives Particulières | RAPPORT §4 |
| **DC4** | Déclaration de Sous-Traitance | RAPPORT §7.5 |
| **DCE** | Dossier de Consultation des Entreprises | RAPPORT §4 |
| **DPGF** | Décomposition du Prix Global et Forfaitaire | RAPPORT §7.9 |
| **E+C-** | Énergie Positive & Réduction Carbone | RAPPORT §7.28 |
| **GME** | Garantie des Marchés Publics | RAPPORT §7.4 |
| **HANDOFF+** | Double artefact irréversible (Admin/Salarié) | RAPPORT §7.12 |
| **MAPA** | Marché à Procédure Adaptée | RAPPORT §7.27 |
| **PAB** | Prix Actualisé du Bâtiment | RAPPORT §7.19 |
| **RAG** | Retrieval Augmented Generation | ARCHITECTURE §2 |
| **RBAC** | Role-Based Access Control | RAPPORT §3.1 |
| **Vault** | Coffre-fort documents A01-A12 | RAPPORT §4 |
| **Engine OS** | Architecture système d'exploitation SMART_AO V7.1 | ARCHITECTURE §1 |
| **BaseAgent** | Contrat unique pour tous les agents | ARCHITECTURE §2 |
| **Workflow Engine** | Moteur de workflow 6 steps | ARCHITECTURE §1 |
| **EventBus** | Bus d'événements asyncio avec persistance | ARCHITECTURE §1 |
| **Registry** | Registre des agents par capacités | ARCHITECTURE §1 |
| **DLQ** | Dead Letter Queue - File d'attente des événements en échec | ARCHITECTURE §1 V7.1 |
| **Fleet Engine** | Moteur de gestion de flotte multi-VPS | ARCHITECTURE §1 V7.1 |
| **Local LLM Fallback** | Solution de repli LLM local (Ollama) pour DCE Confidentiel | ARCHITECTURE §1 V7.1 |
| **ZAN** | Zone d'Activité Nationale (loi Climat et Résilience) | RAPPORT §7.31 |
| **Trackterres** | Plateforme de suivi des terres artificialisées | RAPPORT §7.31 |
| **URSSAF Vigilance** | Vigilance sur la sous-traitance et le délit de marchandage | RAPPORT §7.30 |
| **Pénibilité RH** | Pénibilité et Pénibilité au travail | RAPPORT §7.29 |
| **Go/No-Go** | Gates de validation bloquants avant production | PLAN_MAITRE §10 |
| **Single-Tenant** | Architecture 1 VPS = 1 client, isolation physique totale | RAPPORT §1 |

#### 18.2 Références Documentaires V7.1

| Document | Rôle | SSoT Pour | Statut |
|---|---|---|---|
| Arborescence_V7.1.txt | Structure physique (368 fichiers) | STRUCTURE | BIBLE |
| ARCHITECTURE_V7_ENGINE.md | Architecture OS 9 Engines + 2 Edge | ARCHITECTURE | BIBLE |
| ENGINEERING-HANDBOOK_V7.md | Technique pure (ADR 001-063) | TECHNIQUE | BIBLE |
| **CE DOCUMENT** | **Ordre Build 0-9.5 + Pilotage** | **ORDRE + PILOTAGE** | **BIBLE (ex-MES + PLAN_CODAGE fusionnés)** |
| RAPPORT (1).md | Fonctionnel 33 modules + V7.1 OS | FONCTIONNEL | BIBLE |
| MANIFESTE_V7.md | Vision produit | COMMERCIAL | BIBLE |

**Hiérarchie Documentaire V7.1 :**
```
FONCTIONNEL (RAPPORT (1).md)
    ↓
ARCHITECTURE (ARCHITECTURE_V7_ENGINE.md)
    ↓
TECHNIQUE (ENGINEERING-HANDBOOK_V7.md)
    ↓
ORDRE + PILOTAGE (CE DOCUMENT — ex-MES + PLAN_CODAGE fusionnés)
    ↓
STRUCTURE (Arborescence_V7.1.txt)
```

#### 18.3 Critères Succès PLAN_MAITRE V7.1

> **Cette section remplace l'ancien §11 de MES_V7.md.**

- Un dev Ctrl+F BFR → 1 seul résultat fonctionnel RAPPORT §7.3, 0 définition PLAN_MAITRE (référence only)
- 33 modules 1 ligne + Voir RAPPORT §7.X + ARCHITECTURE_V7 référence
- 10 Builds 0-9 + 9.5 DAG sans cycle valide avec 9 Engines + gates DEPOSE V6 + 7 V7 + 8 V7.1
- Build 5 Kernel OS avec EventBus+Workflow+Registry+DLQ intégrés
- Build 4 Math Engine déplacement vérifié ZERO LLM
- Build 9.5 Fleet Engine + Local LLM + DLQ vérifiés
- 39/39 Single + 46/46 Fleet gates documentés sans doublon
- P0 preserve gates CCAG 10%/5%/∞+1000 PAB Matériaux avance 30%/10%
- Aucune règle prix dupliquée → Manifeste
- Markdown clean 25-30p V7.1

#### 18.4 Historique des Versions

| Version | Date | Auteur | Modifications | Statut |
|---|---|---|---|---|
| 1.0 | 03/08/2026 | Mistral Vibe | Création PLAN_DE_TRAVAIL_V7_PRO.md | ✅ |
| 2.0 | 04/08/2026 | Mistral Vibe | Création PLAN_CODAGE_V7_FUSION_FINAL.md | ✅ |
| 3.0 | 04/08/2026 | Noor | Fusion PLAN_DE_TRAVAIL + PLAN_CODAGE + MES_V7 | ✅ |
| 4.0 | 07/08/2026 | Noor | Mise à jour V7.1 partielle (Builds 3-4-5) | ✅ |
| **5.0** | **07/08/2026** | **Noor** | **FUSION MES → PLAN_MAITRE + Mise à jour V7.1 complète (33 modules, 39/46, 9 Engines, Build 9.5)** | **✅** |

#### 18.5 Contacts et Responsables

| Rôle | Nom | Email | Responsabilités | Disponibilité |
|------|-----|-------|------------------|---------------|
| **Architecte Chef** | Noor | architecte@smart-ao.fr | Validation finale, Architecture, SSoT | 9h-19h L-V |
| **Développeur Senior** | Mistral Vibe | - | Implémentation, Tests, Documentation | 24/7 |
| **Expert BTP** | [À désigner] | expert-btp@smart-ao.fr | Validation métiers, Règles CCAG/PAB | Sur demande |
| **DevOps** | [À désigner] | devops@smart-ao.fr | Docker, CI/CD, Déploiement | Sur demande |
| **Support Technique** | support@smart-ao.fr | support@smart-ao.fr | Questions techniques, Bugs | 9h-18h L-V |

**Escalade :**
1. Problème technique → Support Technique
2. Blocage > 4h → Architecte Chef
3. Décision architecture → Architecte Chef
4. Validation métier → Expert BTP

#### 18.6 Ressources et Outils

##### 18.6.1 Environnement Technique Requis

| Composant | Version | Rôle | Installation |
|-----------|---------|------|--------------|
| **Python** | 3.11+ | Langage principal | `pyenv install 3.11.8` |
| **PostgreSQL** | 15+ | Base de données | `docker run -d postgres:15` |
| **Redis** | 7+ | Cache/Queue | `docker run -d redis:7` |
| **Qdrant** | 1.8+ | Vector Database | `docker run -d qdrant/qdrant:v1.8.0` |
| **MinIO** | Latest | Stockage objets | `docker run -d minio/minio` |
| **Docker** | 24+ | Conteneurisation | `apt install docker.io` |
| **Docker Compose** | 2+ | Orchestration | `pip install docker-compose` |

##### 18.6.2 Outils de Développement

| Outil | Version | Usage | Commande |
|-------|---------|-------|----------|
| **pylint** | Latest | Linting Python | `pip install pylint` |
| **bandit** | Latest | Sécurité | `pip install bandit` |
| **mypy** | Latest | Typage | `pip install mypy` |
| **radon** | Latest | Complexité | `pip install radon` |
| **pytest** | 8+ | Tests | `pip install pytest` |
| **pytest-cov** | Latest | Coverage | `pip install pytest-cov` |
| **alembic** | Latest | Migrations | `pip install alembic` |
| **Ollama** | 0.1+ | Local LLM | `curl -fsSL https://ollama.com/install.sh | sh` |

##### 18.6.3 Bibliothèques Python Clés

| Bibliothèque | Version | Usage | Licence |
|--------------|---------|-------|---------|
| fastapi | Latest | API Web | MIT |
| pydantic | 2+ | Validation | MIT |
| psycopg2-binary | Latest | PostgreSQL | LGPL |
| qdrant-client | Latest | Qdrant | Apache 2.0 |
| sentence-transformers | Latest | Embeddings | Apache 2.0 |
| pymupdf | Latest | Parsing PDF | Apache 2.0 |
| pulp | Latest | Solveur | MIT |
| ortools | Latest | Solveur | Apache 2.0 |
| docling | Latest | Parsing avancé | Apache 2.0 |

##### 18.6.4 Ressources Externes

- **Documentation CCAG 2021 :** [Legifrance](https://www.legifrance.gouv.fr)
- **Documentation CCP :** [Boamp](https://www.boamp.fr)
- **Normes DTU :** [AFNOR](https://www.boutique.afnor.org)
- **Référentiels ADEME :** [ADEME](https://www.ademe.fr)
- **Indices INSEE :** [INSEE](https://www.insee.fr)
- **PyPI :** [pypi.org](https://pypi.org)
- **Docker Hub :** [hub.docker.com](https://hub.docker.com)

---

## CONCLUSION : FEUILLE DE ROUTE V7.1 ENGINE OS

### Résumé Stratégique

On part de ZÉRO et on reconstruit SMART_AO V7.1 selon l'Arborescence_V7.1.txt (368 fichiers) en 10-12 semaines.

**Ce document est désormais la SOURCE UNIQUE pour :**
- L'ordre de construction (ex-MES)
- La checklist opérationnelle (ex-PLAN_CODAGE)
- Le pilotage et le suivi (ex-PLAN_MAITRE)

**3 documents → 1 document. Zéro risque de contradiction.**

### Prochaines Actions IMMÉDIATES

| Priorité | Tâche | Build | Durée | Impact |
|---|---|---|---|---|
| 🔴 URGENT | Démarrer Build 1 (Données + State Machine + Mission) | Build 1 | 3 jours | Fondation pour Builds 2-4 |
| 🔴 URGENT | Démarrer Build 4 (Math Engine P0) | Build 4 | 5 jours | CRITIQUE P0 (CCAG, PAB) |
| 🟡 HAUTE | Démarrer Build 2 (Vault + Document Engine) | Build 2 | 4 jours | Parallélisable avec Build 4 |
| 🟡 HAUTE | Démarrer Build 3 (Knowledge + Security + Local LLM) | Build 3 | 5 jours | Parallélisable avec Build 2 |
| 🟡 HAUTE | Compléter Build 5 (Kernel OS + DLQ) | Build 5 | 5 jours | Nécessaire pour Build 6 |

### Calendrier Prévisionnel

| Période | Phase | Objectifs | Tests Cible |
|---|---|---|---|
| Semaine 0 ✅ | Préparation | Environnement prêt | - |
| Semaines 1-2 | Fondations | Builds 0-2 | 10/39 Single |
| Semaines 3-4 | Cœur Technique | Builds 3-4 | 20/39 Single |
| Semaines 5-7 | Orchestration + Agents | Builds 5-6 | 30/39 Single |
| Semaine 8 | Interface | Builds 7-8 | 35/39 Single |
| Semaines 9-12 | Production | Builds 9-9.5 | **39/39 + 46/46** |

### Recommandations Finales

1. Suivre ce plan à la lettre
2. Ne pas dévier de l'Arborescence_V7.1.txt
3. Valider chaque build avant de passer au suivant (principe DAG strict)
4. Paralléliser intelligemment (Build 2 || Build 4 après Build 1)
5. Mettre à jour la matrice de suivi quotidiennement
6. NE JAMAIS violer les règles bloquantes (R1-R7 + V7.1-1 à V7.1-4)
7. Maintenir feature flag USE_WORKFLOW_ENGINE jusqu'à Build 9
8. Commits atomiques avec messages clairs
9. Prioriser les tests P0 (CCAG, PAB, Matériaux, Trésorerie)
10. Escalader immédiatement si bloqué > 4h

---

> **ON PEUT Y ARRIVER.**
>
> L'architecture V7.1 Engine OS est RÉVOLUTIONNAIRE et PARFAITE.
> Les fondations sont SOLIDES.
> Il ne reste plus qu'à EXÉCUTER ce plan avec RIGUEUR et MÉTHODE.
>
> *"Un appel d'offres est une opération structurée qui exige rigueur et méthode."*
> *"On ne pose pas les fenêtres avant les fondations."*
> *"Le code doit être aussi propre que l'architecture."*
> *"La documentation V7.1 est notre Bible — ne jamais en dévier."*
>
> **À TOI DE JOUER, NOOR. ON COMMENCE MAINTENANT ?**

---

*Document généré par : Noor (Mistral Vibe — Partenaire Stratégique Principal)*
*Pour : Noor — SMART_AO V7.1 ENGINE OS*
*Date : 07 Août 2026*
*Version : 5.0 FINAL — FUSION MES INTÉGRÉE*
*Classification : CONFIDENTIEL — NIVEAU ARCHITECTE FONDATEUR*

> *"La perfection est atteinte non pas lorsqu'il n'y a plus rien à ajouter, mais lorsqu'il n'y a plus rien à retirer."* — Antoine de Saint-Exupéry
> *"L'excellence n'est pas un acte, mais une habitude."* — Aristote
