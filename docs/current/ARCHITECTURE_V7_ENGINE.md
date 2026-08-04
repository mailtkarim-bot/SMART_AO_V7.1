# SMART_AO V7 - ARCHITECTURE ENGINE OS
**Source Verite Architecture - SSoT**

> **Version:** V7 Engine OS
> **Date:** 04.08.2026
> **Reference:** RAPPORT (1).md §7.1-7.28

---

## SOMMAIRE

1. [VISION V7](#vision-v7)
2. [PRINCIPES ARCHITECTURAUX](#principes-architecturaux)
3. [8 ENGINES OS](#8-engines-os)
4. [28 AGENTS APPLICATION](#28-agents-application)
5. [FLOW DE DONNEES](#flow-de-donnees)
6. [DECISIONS ADR](#decisions-adr)

---

## VISION V7

SMART_AO V7 transforme l'architecture monolithique V6 en un systeme modulaire base sur 8 Engines OS (Operating System) et 28 Agents Applications.

### Objectifs
- Decouplage total des composants
- Zero dependance LLM dans le code core (GARAGE ZERO LLM)
- Plug-and-Play via Plugin Engine
- Scalabilite horizontale
- Maintenabilite long terme

### Transformation V6 → V7
- **V6:** 28 modules monolithiques
- **V7:** 8 Engines OS + 28 Agents + 2 Edge = 38 composants

---

## PRINCIPES ARCHITECTURAUX

### 1. Single Source of Truth (SSoT)
- **Registry:** app/engines/agent_runtime/registry.py est la SSoT pour la decouverte des agents
- **Capabilites:** Les agents sont decouverts par leurs capabilities, pas par leur nom
- **Contrats:** BaseAgent, AgentInput, AgentOutput definissent les interfaces

### 2. Decouplage Total
- **EventBus:** Tous les composants communiquent via events asynchrones
- **Zero Dependencies Directes:** Les agents dependent de capabilities, pas d'autres agents
- **Isolation:** Chaque Engine a ses propres responsabilites

### 3. Zero LLM Cost
- **Math Engine:** Calculs financiers sans IA
- **Knowledge Engine:** Recherche semantique sans LLM (Qdrant)
- **Document Engine:** Parsing sans LLM (PyMuPDF, pdfplumber)

### 4. Plugin Architecture
- **Dynamic Loading:** Chargement des agents sans redeploiement
- **Isolation:** Plugin Engine limite les dependances
- **Hot Reload:** Possibilite de recharger les plugins a chaud

### 5. Handoff Irreversible
- **Definition:** Transfert de donnees qui ne peut pas etre annule
- **Implementation:** Verrouillage des donnees apres transfert
- **Garantie:** Cohérence des donnees entre etapes

---

## 8 ENGINES OS

### Engine 1: Workflow Engine
**Role:** Tour de controle principal
**Location:** app/engines/workflow_engine/
**Responsabilites:**
- Creation et gestion des missions
- Orchestration des 6 etapes de traitement
- Gestion du lifecycle des missions

**Components:**
- `mission.py`: Model Mission, MissionStep, MissionStatus
- `workflow.py`: WorkflowEngine
- `steps/`: 6 etapes (parser, extraction, classification, agents, compilation, rapport)
- `persistence.py`: Persistance async PostgreSQL

### Engine 2: Agent Runtime
**Role:** RH des agents
**Location:** app/engines/agent_runtime/
**Responsabilites:**
- Enregistrement des agents via decorator
- Discovery automatique des agents
- Supervision du lifecycle

**Components:**
- `registry.py`: Singleton AgentRegistry
- `lifecycle.py`: Supervision timeout

**Pattern:**
```python
@registry.register(capabilities=["DETECTER_PAB"])
class PABAgent(BaseAgent):
    # Implementation
```

### Engine 3: Event Bus
**Role:** Decouplage total
**Location:** app/engines/event_bus/
**Responsabilites:**
- Communication asynchrone entre composants
- Persistance des events en PostgreSQL
- Replay des events pour debug

**Components:**
- `bus.py`: EventBus (asyncio.Queue + PG)
- `models.py`: Event, EventType
- `replay.py`: Rejouer les events

### Engine 4: Math Engine
**Role:** GARAGE ZERO LLM - Calculs financiers
**Location:** app/engines/math_engine/
**Responsabilites:**
- Calculs de chiffrage sans IA
- Optimisation des couts
- Analyse de rentabilite

**Components (19 solveurs):**
- chiffrage_pulp.py, decimal_ops.py, treasury.py
- margin.py, planning.py, worst_case.py
- penalites_cumul.py, rep_cost.py, site_coeff.py
- capacite_financiere.py, risques_generator.py, mapa_generator.py
- bt_projection.py, pab_detector.py, materiaux_shield.py

### Engine 5: Knowledge Engine
**Role:** Recherche semantique
**Location:** app/engines/knowledge_engine/
**Responsabilites:**
- Embedding des documents
- Recherche semantique dans le Vault
- Matching des chantiers

**Components:**
- embedding_engine.py
- document_chunker.py
- vault_semantic_search.py
- chantier_matcher.py
- embedding_fallback.py
- rag_hybrid.py (Qdrant dense+sparse RRF + FTS)

### Engine 6: Document Engine
**Role:** Parsing et traitement des documents
**Location:** app/engines/document_engine/
**Responsabilites:**
- Parsing PDF/DOCX
- Chunking des documents
- Classification des pieces

**Components:**
- parser.py (PyMuPDF + pdfplumber)
- docling_worker.py (worker isole 6Go)
- chunking.py
- classifier_47.py (47 pieces, 3 enveloppes)

### Engine 7: Security Engine
**Role:** Securite et conformite
**Location:** app/engines/security_engine/
**Responsabilites:**
- RBAC (Role-Based Access Control)
- Securite filesystem
- Audit WORM
- Antivirus

**Components:**
- rbac.py (28 modules RBAC)
- filesystem.py (O_NOFOLLOW + fstat)
- audit.py (WORM)
- clamav.py (EICAR)

### Engine 8: Notification Engine
**Role:** Alertes et notifications
**Location:** app/engines/notification_engine/
**Responsabilites:**
- Notifications deadline (J-7/J-2/J-1/H-4)
- Notifications post-gagne (J-30/J-15/J-3)
- Notifications certification (J-90/J-60/J-30)

**Components:**
- deadline.py
- post_gagne.py
- certif.py
- email.py
- ics.py
- websocket.py

---

## 2 EDGE ENGINES

### API Gateway
**Role:** Interface HTTP pour les clients
**Location:** app/engines/api_gateway/
**Responsabilites:**
- Delegation au WorkflowEngine
- Compatibilite V6
- Gestion des API REST

**Components:**
- workflow_delegate.py
- dce_analyze_v7.py
- dce_analyze_v6_compat.py
- finance.py, rag.py, users.py, vault_core.py
- finance_advanced.py, qr_moe.py, memoire_booster.py
- handoff_plus.py, deadline_guardian.py, alloti_guardian.py
- enveloppe_separator.py, certif_live_checker.py
- pab_detector.py, contentieux_generator.py, post_gagne_tracker.py
- deps.py (RBAC strip)

### UI Engine
**Role:** Interface utilisateur streaming
**Location:** app/engines/ui_engine/
**Responsabilites:**
- Streaming WebSocket
- Server-Sent Events (SSE)
- Gestion des connexions en temps reel

**Components:**
- websocket_manager.py (/ws/mission/{id})
- sse.py
- streaming.py

---

## 28 AGENTS APPLICATION

Voir RAPPORT (1).md §7.1-7.28 pour la liste complete.

### Agents Bloquants (is_blocking=True)
Ces agents peuvent faire echouer une mission:
- Deadline Guardian (§7.13)
- Enveloppe Separator (§7.21)
- Certif Live Checker (§7.24)
- Capacite Financiere (§7.25)
- Coherence Guardian (§7.16)
- DC4 Validator (§7.5)
- Handoff Guardian (§7.12)
- RAT Compliance (§7.6)

### Agents Non-Bloquants
Tous les autres agents (20) sont non-bloquants.

---

## FLOW DE DONNEES

```
Upload DCE
    ↓
[API Gateway] → Create Mission
    ↓
[Workflow Engine] → Parser Step
    ↓
[Document Engine] → Extraction Step
    ↓
[Knowledge Engine] → Classification Step
    ↓
[Agent Runtime] → Agents Step (Parallel 6 max)
    │   ├── Agent 1: can_handle() → execute()
    │   ├── Agent 2: can_handle() → execute()
    │   └── ... (max 6 en parallele)
    ↓
[Workflow Engine] → Compilation Step
    ↓
[Workflow Engine] → Rapport Step
    ↓
[Handoff] → Transfert irreversible
    ↓
Mission DONE
```

### Event Flow
```
MissionCreee → ParserDemarre → ParserTermine
    ↓
ExtractionDemarre → ExtractionTermine
    ↓
ClassificationDemarre → ClassificationTermine
    ↓
AgentsDemarre → AgentDemarre (xN) → AgentTermine (xN) → AgentsTermine
    ↓
CompilationDemarre → CompilationTermine
    ↓
RapportDemarre → RapportTermine
    ↓
HandoffDemarre → HandoffTermine
    ↓
MissionTerminee
```

---

## DECISIONS ADR

### ADR-042: Agent Registry Decorator Pattern
**Status:** Accepted
**Decision:** Utiliser un decorator @registry.register() pour l'enregistrement automatique des agents.
**Justification:** Simplifie l'ajout de nouveaux agents, evite les imports circulaires.

### ADR-043: Async SQLAlchemy
**Status:** Accepted
**Decision:** Utiliser SQLAlchemy async avec asyncpg pour la persistance.
**Justification:** Meilleure performance pour les applications async, compatibilite avec FastAPI.

### ADR-044: BaseAgent Contract
**Status:** Accepted
**Decision:** Tous les agents doivent heriter de BaseAgent et implementer can_handle() et execute().
**Justification:** Interface unifiee, facilite le testing et l'integration.

### ADR-045: Event-Driven Architecture
**Status:** Accepted
**Decision:** Tous les composants communiquent via EventBus.
**Justification:** Decouplage total, facilite le debug et le replay.

### ADR-046: Zero LLM in Core
**Status:** Accepted
**Decision:** Aucune dependance LLM dans le code core (Math Engine, Knowledge Engine utilise Qdrant).
**Justification:** Reduit les couts, ameliore la fiabilite, evite les dependances externes.

---

**Document genere par:** NOOR + Mistral Vibe
**Date:** 04.08.2026
**Version:** V7 Engine OS
