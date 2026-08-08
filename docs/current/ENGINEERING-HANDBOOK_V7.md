
# SMART_AO - ENGINEERING HANDBOOK V7 ENGINE OS

> **Classification: CONFIDENTIEL - NIVEAU ARCHITECTE FONDATEUR V7**
> **Statut: Reference unique technique - SSoT Technique (Architecture OS: voir ARCHITECTURE_V7_ENGINE.md)**
> **Version: V7.1 Engine OS - 33 modules -> 100 scalables - 9 Engines + 2 Edge - 16 solveurs - 39 Single / 46 Fleet - 57+ tests + 8 V7.1**
> **Source fonctionnelle: RAPPORT (1).md §7.1-7.33**
> **Source architecture: ARCHITECTURE_V7_ENGINE.md**

---

## 0. HIERARCHIE DOCUMENTAIRE V7

```
MANIFESTE V7.1 = Pourquoi (commercial, prix, 33 boucliers + mention OS 9 moteurs)
RAPPORT (1).md = Que fait produit (SEULE source fonctionnelle 33 modules §7.1-7.33 + P0 §6)
ARCHITECTURE_V7_ENGINE.md = Architecture OS (SEULE source architecture - 9 Engines + 2 Edge, BaseAgent, Registry, Mission, EventBus, 5 schemas)
PLAN_MAITRE_V7.1 = Ordre + Pilotage (10 Builds 0-9 + 9.5, DAG 9 Engines + 2 Edge, gates 39/46, roadmap, suivi)
ENGINEERING-HANDBOOK V7.1 = Comment technique pur (CE DOCUMENT - ADR 001-063, C4, contrats API, schemas, mem_limit, tests 39/46, infra)
Arborescence V7.1 = Ou ranger fichier (engines/ + agents/) - 368 fichiers
```

SSoT V7:
- Fonctionnel -> RAPPORT §7.X gagne
- Architecture OS -> ARCHITECTURE_V7_ENGINE.md gagne
- Technique pur -> HANDBOOK V7 gagne
- Ordre build -> PLAN_MAITRE_V7.1 gagne (ex-MES + PLAN_CODAGE fusionnés)

---

## 1. REGLES D'OR INTANGIBLES V7 - OCCURRENCE UNIQUE

### 1.1 RBAC Financier Etancheite Absolue 33 Modules - V7.1 preserve + etendu aux Engines

Identique V6 + adaptation Engine:

- Univers SALARIE: zero EUR (marge, coeff, PAB, capacite, contentieux, risques) + nouveau: zero acces Mission.context.agent_outputs financiers + zero acces Math Engine direct
- Univers ADMIN: voit tout 33 modules + Mission trace + Math Engine outputs
- Implementation V7:

```python
# app/engines/security_engine/rbac.py V7 (deplace de app/core/security.py)
FIELDS_STRIP_V6 = ["total_ht","marge","ae_total","treasury","provisions_euros","cout_rep",
"exposition_penalites","bfr_pic","cout_caution","provision_amiante","provision_omission",
"site_coeff_impact","coeff_vente","fg","marge_brute_nette","marge_ht",
"ecart_pab","perte_materiaux","cout_contentieux","interets_lme","capacite_fr","marge_residuelle","co2_total",
"agent_outputs_financiers","math_engine_result"]  # V7 ajout

def strip_provisions_euros_v7(data: dict, role: str):
    if role=="employee":
        for f in FIELDS_STRIP_V6: data.pop(f, None)
    return data

# app/engines/api_gateway/deps.py V7 delegue Security Engine
async def require_admin(...): ...
```

Tests bloquants V7: test_api_employee_cannot_see_prices + test_rbac_28_modules_no_euro + test_rbac_mission_no_financial_leak (NOUVEAU V7) + test_rbac_33_modules_v71 (NOUVEAU V7.1) + test_front_no_price_leak 33 modules

### 1.2 Garage Mathematique ZERO LLM V7 - Math Engine

Principe V6 conserve + deplacement:

```
[DCE brut] -> [Document Engine PyMuPDF/Docling] -> [Knowledge Engine BGE-M3 Qdrant hybrid RRF] 
-> [28 Agents BaseAgent -> JSON quali ZERO EUR] -> [Workflow Engine Classification]
-> [Math Engine 16 solveurs Decimal exact to_decimal(str)] 
-> [Double sortie: Vue Salarie quali / Vue Admin quanti]
```

- Math Engine: Dossier app/engines/math_engine/ 19 fichiers ZERO import openai,mistral,anthropic,langchain - Test bloquant test_math_engine_no_llm_import.py grep -R openai app/engines/math_engine =0
- Solveurs V7.1: 16 solveurs (11 V6 conservés + 5 V7.1), formules opposables Voir RAPPORT §9 + ARCHITECTURE_V7.1 §1

### 1.3 BaseAgent Contrat Unique V7 - NOUVEAU

Voir ARCHITECTURE_V7_ENGINE.md §2 pour contrat complet. Ici reference technique opposable:

- Tous agents dans app/agents/agent_*.py heritent BaseAgent
- Proprietes: name, capabilities[], dependencies[], tags[], estimated_duration, is_blocking
- Methodes: can_handle(mission)->float 0-1, execute(AgentInput)->AgentOutput
- AgentOutput.findings = ZERO EUR regex garanti
- Registry auto-discovery via @registry.register(capabilities=[...]) au import

Test bloquant V7: test_base_agent_contract.py verifie 28 agents conformes + can_handle retourne float + execute retourne AgentOutput ZERO EUR

### 1.4 Vault A01-A12 J-30 readonly + Document Engine

Inchange V6 + Document Engine publie DocumentAnalyse. Cron vault_expiry_check 06h00 continue meme is_readonly=True. Deadline Guardian verifie Vault expire avant date limite + bloque depot + Certif Live Checker verifie expiration pendant marche.

### 1.5 HANDOFF+ irreversible + double artefact + Workflow Engine

Trigger Admin seul passage Gagne/Attribue. Generation separee BOOK_CHANTIER_COMPLET_ADMIN.pdf (avec EUR, marges, provisions, BFR, tableau risques, PAB) vs BOOK_CHANTIER_EXECUTION_SALARIE.pdf (zero EUR regex). Workflow Engine step RAPPORT genere double artefact. Test test_handoff_double_artefact conserve.

### 1.6 Corrections P0 V6 integrees bloquantes V7 preservees

Voir RAPPORT §6 + ADR-057 + ARCHITECTURE_V7 §1 Math Engine. CCAG 2021 plafond penalites 10% public + seuil 1000EUR / 5% prive NF P03-001 / Sans plafond CCMI 1/3000e + avance minimale 2024 30% Etat / 10% collectivite >60MEUR + RG max 5% remplacable garantie. Implementes dans penalites_cumul.py + treasury.py + tuile Finance Warfare + Math Engine. Tests bloquants si non conformes.

---

## 2. ADR V7 - 001-058 - SSoT Technique

### ADR 001-040 V6 conserves (Voir HANDBOOK V6)

001 Single-Tenant Pur, 002 VPS 16/32Go, 003 Souverainete OVH FR, 004 Parsing PyMuPDF+Docling worker, 005 RAG Hybrid BGE-M3 Qdrant on_disk RRF+FTS btp_french, 006 Garage ZERO LLM, 007 Decimal 28 to_decimal(str), 008 Vault A01-A12 J-30 readonly, 009 HANDOFF+ double artefact, 010 RBAC 33 modules, 011 FileLock Excel, 012 O_NOFOLLOW+fstat, 013 Build Chain par dependances, 014 Go/No-Go 39/46 V7.1, 015 Auth Argon2id JWT vps_id 2FA TOTP, 016 WORM audit, 017 ClamAV EICAR, 018 Redis AOF, 019 MinIO versioning 10, 020 Qdrant on_disk, 021 BGE-M3 1024d, 022 Embedding fallback, 023 MCP internes/externes, 024 BOAMP radar 6h idempotent, 025 CCAG P0 10%/5%/CCMI inf+1000, 026 Avance P0 30%/10%, 027 PAB P0 -20%/-30% marge min 6%, 028 Materiaux Shield P0, etc. Voir HANDBOOK V6.

### ADR 041-058 V7 NOUVEAUX - Architecture OS

**ADR-041 Workflow Engine - Tour de controle**
- Decision: Workflow Engine = tour de controle, ne fait rien lui-meme, orchestre Missions 6 steps [PARSER, EXTRACTION, CLASSIFICATION, AGENTS, COMPILATION, RAPPORT]
- Implementation: app/engines/workflow_engine/ Mission, MissionStep, WorkflowEngine, persistance PG tables missions, mission_steps, retry/timeout per step, semaphore 6 max parallel pour 16Go
- Justification: Observabilite, rejouabilite, parallelisation controlee, retry/timeout, traçabilite

**ADR-042 Agent Registry - Decouverte par capacites**
- Decision: Orchestrateur ne connait plus aucun fichier agent. Il connait des capacites. Registry find_by_capability()
- Implementation: app/agents/registry.py Singleton, register decorator, auto-discovery via pkgutil.iter_modules au boot, find_by_capability, find_by_tags, get_all, scoring can_handle
- Justification: OCP, ajout 100 agents sans toucher coeur, testabilite Registry mockable

**ADR-043 Event Bus - Pub/Sub intra-VPS**
- Decision: Event Bus asyncio.Queue + table events PG pour replay, pas Kafka/Redis Streams (contrainte 16Go RAM)
- Implementation: app/engines/event_bus/ Event, EventBus, publish persistance PG + queue memoire + subscribers dict, subscribe decorator, replay(mission_id)
- Events standardises: MissionCreee, DocumentAnalyse, EntitesExtraites, ClassificationTerminee, AgentDemarre, AgentTermine, RisqueDetecte, AnalyseTerminee, MissionEchouee
- Justification: Decouplage total, Parser ne connait personne, ajout Assurance Agent sans modifier Parser

**ADR-044 BaseAgent - Contrat uniforme**
- Decision: Tous agents repondent aux 4 memes questions: name, capabilities, dependencies, can_handle, execute
- Implementation: app/agents/base_agent.py ABC, AgentInput, AgentOutput ZERO EUR, 4 props + 2 methodes, estimated_duration, is_blocking
- Justification: Junior comprend en 5min, junior ajoute agent en copiant PABAgent, tests uniformes

**ADR-045 Math Engine - Extraction mathbox**
- Decision: Deplacement app/mathbox/ -> app/engines/math_engine/ 19 fichiers, ZERO LLM conserve, Decimal 28 conserve
- Implementation: PuLP 3.3.2 CBC + OR-Tools 9.15 CP-SAT + Decimal 28 to_decimal(str), 16 solveurs, referentiels data/referentiels/ injectes via Knowledge Engine
- Justification: Math Engine = moteur transverse utilise par tous agents comme Word utilise Windows

**ADR-046 Knowledge Engine - RAG Hybrid**
- Decision: RAG Hybrid Dense+Sparse+RRF+Fallback FTS btp_french = Knowledge Engine transverse
- Implementation: app/engines/knowledge_engine/ embedding_engine.py, document_chunker.py, vault_semantic_search.py, btp_french custom dict, Qdrant on_disk, collections dce,vault,chantiers,traps sans prefix tenant
- Justification: Tous agents utilisent meme RAG, pas duplication

**ADR-047 Document Engine - Parser isole**
- Decision: Parser PyMuPDF/pdfplumber + Docling worker separe = Document Engine transverse
- Implementation: app/engines/document_engine/ parser.py, docling_worker.py, chunking, 47 pieces classification, event DocumentAnalyse publie
- Justification: Isolation Docling lourd 6Go RAM, ne bloque pas API

**ADR-048 Security Engine - RBAC+FS isolation**
- Decision: RBAC 33 modules + O_NOFOLLOW+fstat+BASE_ROOT non-symlink + FileLock + WORM + ClamAV = Security Engine transverse
- Implementation: app/engines/security_engine/ rbac.py, filesystem.py, audit.py, clamav.py, wrapper app/core/security.py conserve compat
- Justification: Securite = moteur transverse, toute API passe par Security Engine

**ADR-049 Notification Engine - Deadlines**
- Decision: Deadline J-7/J-2/J-1/H-4 + PostGagne J-30/J-15/J-3 + Certif J-90/J-60/J-30 = Notification Engine transverse
- Implementation: app/engines/notification_engine/ deadline.py, post_gagne.py, certif.py, email.py, ics.py, websocket.py
- Justification: Tous agents peuvent declencher notification via EventBus, pas duplication

**ADR-050 Plugin Engine - Chargement sans redeploiement**
- Decision: Plugin Engine = chargement agents externes BIM/Assurance/Facturation sans redeploiement via Manifest YAML + importlib
- Implementation: app/engines/plugin_engine/ loader.py, manifest.py, isolation DI BaseAgent + Engines only, pas import app/core direct
- Justification: Scalabilite 100 agents, partenaires peuvent fournir agents sans toucher coeur

**ADR-051 API Gateway - Delegation Workflow**
- Decision: API Gateway endpoints deleguent au Workflow Engine, plus d'appel direct agents
- Implementation: app/engines/api_gateway/ workflow_delegate.py POST /api/dce/analyze cree Mission soumet WorkflowEngine, deps.py require_admin + strip_provisions_euros_v7
- Justification: API = entree, Workflow = tour de controle, separation responsabilites

**ADR-052 UI Engine - Streaming**
- Decision: UI Engine streaming SSE/WebSocket depuis Workflow Engine, plus de polling
- Implementation: app/engines/ui_engine/ websocket_manager.py, sse.py, endpoint /ws/mission/{id} streaming steps AgentDemarre/AgentTermine
- Justification: Observabilite temps reel, Patron voit avancement Mission #254

**ADR-053 Mission vs Project - Separation technique/metier**
- Decision: Mission = technique ephemere (analyse DCE), Project = metier 15 statuts (DEPOSE, GAGNE, EXECUTION)
- Implementation: Mission.status != Project.status, mapping: Mission DONE + Go => Project ANALYSE_TERMINEE, etc., Voir schema 5 ARCHITECTURE_V7
- Justification: Evite duplication state machine, Project = metier, Mission = execution

**ADR-054 Parallelisation controlee**
- Decision: Semaphore 6 max parallel pour 16Go RAM, tri agents par can_handle score decroissant, timeout per agent via estimated_duration * 2
- Implementation: WorkflowEngine.run_agents_parallel() asyncio.Semaphore(6), asyncio.gather + timeout, filtrage can_handle >=0.2
- Justification: 28 agents en parallel OOM sur 16Go, 6 = compromis perf/RAM

**ADR-055 Compatibilite V6 - Migration sans big bang**
- Decision: Build 0-2 inchanges, Builds 3-8 re-specifies en Engines, pas de big bang, feature flag USE_WORKFLOW_ENGINE
- Implementation: Phase1 Contrat+Registry cohabite ancien if/else, Phase2 Mission+EventBus feature flag, Phase3 Engines deplacement, Phase4 suppression ancien
- Justification: Risque zero, rollback possible, flow V7.1 vert 39/46

**ADR-056 Observabilite V7**
- Decision: Chaque step trace started_at/ended_at/retry_count/error/output_ref, chaque event persiste PG, replay mission_id, Prometheus metrics workflow_engine_steps_total, event_bus_published_total
- Implementation: tables missions, mission_steps, events, Prometheus metrics, WORM audit conserve
- Justification: Debug mission #254 echouee, rejouabilite, audit

**ADR-057 P0 Preservation V7**
- Decision: Corrections P0 V6 CCAG 10%/5%/CCMI inf+1000 + avance 2024 30%/10% + PAB + Materiaux conservees dans Math Engine, pas modifiees par migration OS
- Implementation: penalites_cumul.py P0 + tresorerie.py P0 + pab_detector.py + materiaux_shield.py deplaces dans math_engine/ sans modif formule
- Tests P0 bloquants conservent

**ADR-058 Testabilite V7**
- Decision: Registry mockable, EventBus in-memory pour tests, agents unit testables sans WorkflowEngine
- Implementation: EventBus(mode="memory") pour tests, Registry.get_all() mockable, BaseAgent execute testable avec AgentInput fake
- Tests nouveaux: test_registry_discovery.py, test_event_bus.py, test_workflow_engine.py, test_base_agent_contract.py, test_mission_e2e_3_agents.py, test_plugin_engine_load.py

**ADR 059-063 V7.1 NOUVEAUX - Voir ARCHITECTURE_V7_ENGINE.md §7 pour contenu.**

**ADR-064 Routeur LLM Souverain (V3.2 → V7.1)**
- Decision: Routeur LLM unique héritant du choix v3.2, avec défaut souverain Mistral EU, local Ollama pour DCE Confidentiel Défense/Nucléaire, opt-in explicite pour hors-UE (OpenAI/DeepSeek/Kimi) avec disclaimer RGPD.
- Implementation: `app/engines/knowledge_engine/llm_router.py` avec LLMRouter class, support multi-providers, detection confidentiel.
- Justification: Respect souveraineté (AI Act + DPA art28) + flexibilité client. Doctrine inchangée : LLM ne calcule JAMAIS les euros.
- Test bloquant: test_llm_router_mistral_default.py + test_llm_router_confidential_local.py + test_llm_router_optin_disclaimer.py

**ADR-065 Pont Tauri-UI Engine WebSocket (V3.2 → V7.1)**
- Decision: Tauri (Client Edge Natif) consomme UI Engine via WebSocket `/ws/mission/{id}` au lieu de polling REST. Streaming temps réel des events AgentDémarré, RisqueDétecté, MathEngineDone.
- Implementation: `desktop/src/bridge.ts` (WebSocket client) + `app/engines/ui_engine/websocket_manager.py` (serveur) + `app/engines/ui_engine/streaming.py`
- Justification: Élimine la charge serveur du polling. Le salarié voit la progression des 33 boucliers en streaming. 16Go RAM préservés.
- Test bloquant: test_ui_streaming.py (déjà existant V7) + test_tauri_websocket_connection.py (V32-1)

**ADR-066 Mode Panique = Mission URGENTE Fast-Track (V3.2 → V7.1)**
- Decision: Mode Panique V3.2 (Ctrl+Shift+M, deadline < 48h) → Mission à priorité URGENTE avec FAST_TRACK_CAPS. WorkflowEngine bypass agents longs.
- Implementation: `app/engines/workflow_engine/mission.py` (MissionPriority.URGENTE) + `workflow.py` (FAST_TRACK_CAPS) + déclencheur Tauri/API Gateway
- Justification: Intégration propre dans l'architecture OS. E2E <3min, ZIP minimum vital (MAPA Generator, DC1/DC4, DPGF template, Enveloppe Separator).
- Test bloquant: test_mission_urgente_fast_track.py (V32-2) + test_mode_panique_e2e_3min.py (V32-2)

**ADR-067 Migration pgvector→Qdrant One-Shot (V3.2 → V7.1)**
- Decision: Script de migration unique exécutable une fois. Lire embeddings pgvector v3.2, upsert dans Qdrant avec payload complet (doc_id, chunk, meta).
- Implementation: `scripts/migrate_pgvector_qdrant.py` avec vérification intégrité (count avant/après, checksum embeddings).
- Justification: Migration sans downtime, 100% des données préservées. pgvector abandonnée (aveugle au jargon BTP) au profit de Qdrant BGE-M3 1024d hybrid RRF.
- Test bloquant: test_migrate_pgvector_qdrant_complete.py (V32-1) + test_qdrant_collection_integrity.py

**ADR-069 Migration Redis(Files)→MinIO(S3) (V3.2 → V7.1)**
- Decision: Abandon de Redis pour le stockage de fichiers lourds au profit de MinIO (S3-compatible).
- Implementation: Migration des fichiers de `redis_files` vers `minio/s3` avec presigned URLs. `scripts/migrate_redis_minio.py` à créer.
- Justification: Redis n'est pas fait pour le stockage de fichiers lourds (Plans PDF, ZIP DCE). MinIO (S3-compatible) avec presigned URLs est le standard V7.1 pour le stockage objet. Redis conservé uniquement pour les queues (Docling worker AOF).
- Test bloquant: test_migrate_redis_minio_complete.py (V32-1) + test_minio_presigned_urls.py

**ADR-068 CLI Unifiée `smartao` (V3.2 → V7.1)**
- Decision: CLI unique héritant de V3.2, unifie backend + Tauri + web + stop. Commandes : `smartao`, `smartao --dev`, `smartao --web`, `smartao --stop`.
- Implementation: `scripts/smartao` (bash script) avec détection environnement, gestion Docker Compose, rebuild Tauri à chaud.
- Justification: Simplicité d'utilisation préservée de V3.2. Cohérence avec philosophie Anti-ERP (1 commande = tout lancer).
- Test bloquant: test_cli_smartao_all_commands.py (V32-1)

---

## 2.5 ÉVOLUTIONS TECHNIQUES V3.2 → V7.1 (À documenter pour éviter régression)

**Il est crucial de noter pourquoi certaines stacks V3.2 ont été *upgradées* (pour éviter qu'un dev ne tente de réintégrer l'ancienne stack) :**

1. **pgvector ➔ Qdrant (Hybrid RRF)** : pgvector est limité pour le RAG Hybride (Dense + Sparse SPLADE) sur des DCE de 800 pages. Qdrant on_disk est obligatoire pour la performance V7.1 avec embeddings BGE-M3 1024d + Recherche Hybride (Dense + Sparse RRF).

2. **Redis (Files) ➔ MinIO (S3)** : Redis n'est pas fait pour le stockage de fichiers lourds (Plans PDF, ZIP DCE). MinIO (S3-compatible) avec presigned URLs est le standard V7.1 pour le stockage objet. Redis est conservé uniquement pour les queues (Docling worker AOF).

3. **SQLAlchemy 2 + Alembic** : Conservé et renforcé (Single-Tenant pur, 0 `tenant_id`, migrations robustes).

---

## 3. ARCHITECTURE C4 V7

### C4 Context V7 - Identique V6 + Plugin Engine

System SMART_AO V7 OS single-tenant VPS OVH FR, Users Patron/Admin/Salarie, External BOAMP/PLACE, Plugin Agents BIM/Assurance.

### C4 Container V7.1 - 9 Engines + 2 Edge

- Web: React Wizard 12 steps + Cockpit Finance Warfare 5 tuiles + Deadline Guardian + Contentieux + Certif + PAB + Enveloppe etc. -> API Gateway
- API Gateway: FastAPI -> Workflow Engine
- Workflow Engine: Mission 6 steps -> Event Bus <-> Agent Runtime -> Math Engine / Knowledge Engine / Document Engine / Security Engine / Notification Engine / Plugin Engine
- Postgres: missions, mission_steps, events, projects, vault A01-A12, users, audit WORM
- Qdrant: dce, vault, chantiers, traps on_disk dense+sparse
- MinIO: documents, versions 10
- Redis: AOF queue Docling worker
- Docling Worker: separe 6Go RAM
- ClamAV: EICAR

### C4 Component V7 - Engines detail

Voir ARCHITECTURE_V7_ENGINE.md §1 pour detail responsabilites chaque Engine.

---

## 4. CONTRATS API V7 - 230+ endpoints + 11 V6 + delegation Workflow

Core V5 150+ + 11 V6 + 7 V7 nouveaux:

- POST /api/dce/analyze V7: cree Mission, soumet WorkflowEngine, retourne mission_id (au lieu de lancer agents direct) - Voir ADR-051
- GET /api/missions/{id} V7 nouveau: status Mission + steps + events replay
- GET /api/missions/{id}/events V7 nouveau: replay events
- WS /ws/mission/{id} V7 nouveau: streaming steps temps reel
- GET /api/finance-warfare/bt-projection P0 + /penalites P0 10%/5%/inf+1000 + /treasury-warfare P0 avance 30%/10%
- 11 V6: /deadline/guardian, /alloti, /enveloppe/separator, /certif/live-checker, /pab/detector, /contentieux/generate, /post-gagne/tracker, /capacite/financiere, /risques/tableau, /mapa/generator, /eplusc/calculator, /materiaux/shield tous require_admin + strip_provisions_euros_v7
- 7 V7: /registry/capabilities, /workflow/missions, /events/replay, /plugins/load, /math-engine/solveurs, /document-engine/parse, /knowledge-engine/search

Tous require_admin + strip_provisions_euros_v7 ou require_employee selon module Voir RAPPORT §3.1bis RBAC.

---

## 5. TESTS BLOQUANTS V7 - 50+ V6 + 7 V7 + 8 V7.1 = 65+

| # | Test V7 | Build | Bloquant | Source |
|---|---------|-------|----------|--------|
| 1-12 | V5 socle auth JWT vps_id, filesystem O_NOFOLLOW, excel FileLock, math_engine no LLM, no conflict, strip financier, vault J-30, heartbeat whitelist, rollback, backup AES, ClamAV, Golden 3x400p | 0-2 | Oui | V5 |
| 13 | test_28_agents_trap_detector.py 28 agents JSON ZERO EUR confiance >0.8 | 6 | Oui P0 | V6 |
| 14 | test_16_solveurs_vert 16 solveurs Decimal to_decimal(str) 0 LLM | 4 | Oui P0 | V7.1 |
| 15-17 | test_rbac_33_modules_no_euro, test_rbac_provisions V7.1 33 modules, test_handoff_double_artefact 2 PDFs distincts 0EUR | 7 | Oui | V7.1 |
| 18-24 | 7 V6: test_deadline_guardian, test_alloti_guardian, test_enveloppe_separator, test_certif_live_checker, test_pab_detector, test_contentieux_generator, test_post_gagne_tracker | 6-7 | Oui V6 | V6 |
| 25+ | test_rse_booster, test_coherence, test_variante, test_materiaux_shield P0, test_visite_auto, test_capacite_financiere, test_risques_generator, test_mapa, test_eplusc | 6 | Oui V6 | V6 |
| 25 | test_workflow_engine.py V7 - Mission creee 6 steps persistance PG retry timeout | 5 | Oui V7 | V7 |
| 26 | test_event_bus.py V7 - publish/subscribe + persistance PG + replay mission_id | 5 | Oui V7 | V7 |
| 27 | test_registry_discovery.py V7 - find_by_capability retourne bons agents scoring can_handle | 5 | Oui V7 | V7 |
| 28 | test_base_agent_contract.py V7 - 28 agents heritent BaseAgent ZERO EUR + can_handle float + execute AgentOutput | 5-6 | Oui V7 | V7 |
| 29 | test_math_engine_no_llm_import.py V7 - grep -R openai app/engines/math_engine =0 apres deplacement | 4 | Oui V7 | V7 |
| 30 | test_mission_e2e_3_agents.py V7 - Mission #254 bout en bout 3 pilotes Deadline/PAB/Certif DONE | 5-6 | Oui V7 | V7 |
| 31 | test_plugin_engine_load.py V7 - chargement BIMAgent externe Manifest YAML sans redeploiement | 8 | Oui V7 | V7 |
| 32 | test_penibilite_rh.py V7.1 - Détection contraintes + Vault A04 + surcoût intérim | 6 | Oui V7.1 | V7.1 |
| 33 | test_vigilance_urssaf.py V7.1 - Blocage DC4 attestation >6 mois + exposition | 6 | Oui V7.1 | V7.1 |
| 34 | test_zan_trackterres.py V7.1 - Coût évacuation + ISDI + Trackterres | 6 | Oui V7.1 | V7.1 |
| 35 | test_formule_revision.py V7.1 - Σ(coeffs)=1 + indices INSEE + Q/R | 6 | Oui V7.1 | V7.1 |
| 36 | test_sourcing_api.py V7.1 - DUME JSON + push API + horodatage | 8 | Oui V7.1 | V7.1 |
| 37 | test_local_llm_fallback.py V7.1 - DCE Confidentiel -> Mistral 7B local | 5 | Oui V7.1 | V7.1 |
| 38 | test_dlq_reconciliation.py V7.1 - Events stuck -> DLQ -> replay | 5 | Oui V7.1 | V7.1 |
| 39 | test_fleet_update.py V7.1 - Pull-based update cosign verify | 9 | Oui V7.1 | V7.1 |
| **40-48** | **Tests Intégration V3.2 → V7.1 (Sprints V32)** | | | |
| 40 | test_llm_router_mistral_default.py - Routeur LLM défaut Mistral EU | 3 | Oui V32 | V32-1 |
| 41 | test_llm_router_confidential_local.py - Routeur LLM local Ollama pour Confidentiel | 3 | Oui V32 | V32-1 |
| 42 | test_migrate_pgvector_qdrant_complete.py - Migration complète sans perte | 3 | Oui V32 | V32-1 |
| 43 | test_cli_smartao_all_commands.py - CLI unifiée fonctionnelle | 0 | Oui V32 | V32-1 |
| 44 | test_tauri_websocket_connection.py - Pont Tauri ↔ UI Engine WS | 7 | Oui V32 | V32-1 |
| 45 | test_mission_urgente_fast_track.py - Mission URGENTE fast-track | 5 | Oui V32 | V32-2 |
| 46 | test_mode_panique_e2e_3min.py - Mode Panique E2E <3min | 7 | Oui V32 | V32-2 |
| 47 | test_onboarding_5_steps.py - Onboarding complet | 3 | Oui V32 | V32-2 |
| 48 | test_license_checker_perpetual.py - Licences perpétuelles honorées | 9 | Oui V32 | V32-3 |
| 49 | test_license_checker_watermark.py - Watermark correct par type | 9 | Oui V32 | V32-3 |
| 50+ | wizard_flow_12_steps.spec.ts + test_front_no_price_leak 33 modules + backup restore AES + test_api_gateway_delegates + test_ui_streaming + test_rbac_mission_no_financial_leak | 7-9 | Oui | V6+V7 |

Go/No-Go V7.1: 31 Single (24+7) + 38 Fleet (31+7) + 8 V7.1 + 10 V32 = **47 Single / 56 Fleet** verts obligatoires check_go_nogo.sh + check_go_nogo_fleet.sh

---

## 6. REFERENCES CROISEES V7

- Fonctionnel 7.1-7.33: RAPPORT (1).md §7.1-7.33 source unique
- Architecture OS: ARCHITECTURE_V7_ENGINE.md 9 Engines + 2 Edge + BaseAgent + Registry + Mission + EventBus + DLQ + 5 schemas Mermaid
- Build Chain 39/46: PLAN_MAITRE_V7.1 (ex-MES + PLAN_CODAGE fusionnés)
- Technique 33 modules 16 solveurs 13 JSON + 8 nouveaux tests V7.1: CE DOCUMENT
- Arborescence 340 fichiers V7 -> 368 fichiers V7.1 (28 deplaces + 28 nouveaux Engines): Arborescence V7
- Commercial 33 boucliers + mention OS: MANIFESTE V7

---

## 7. INFRA V7 - mem_limit, oom_score, Docker

- Docker compose @sha256 pin conserve + mem_limit profils 16Go pic 14.3Go / 32Go pic 21.5Go + EventBus leger asyncio + WorkflowEngine leger PG + Document Engine Docling worker isole 6Go
- Redis.conf AOF conserve
- Caddyfile + ClamAV conserve
- Fleet terraform OVH FR conserve
- Backup AES-256-GCM quotidien restore <15min @500Mbps AES-NI conserve

---

Fin ENGINEERING HANDBOOK V7.1 ENGINE OS - 63 ADR - 33->133 agents - 16 solveurs - 39/46 Go/No-Go - 65+ tests - Architecture OS
