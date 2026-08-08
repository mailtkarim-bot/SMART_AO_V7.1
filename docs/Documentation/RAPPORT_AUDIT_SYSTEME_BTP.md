# RAPPORT D'AUDIT SMART_AO V7.1 — Tech, Sécurité & Valeur Métier BTP

**Projet audité :** `/home/noor/PROJECTS/BTP/SMART_AO_V2/SMART_AO_LAST 4/SMART_AO_V7`  
**Date d'audit :** 07/08/2026  
**Documents de référence :**
- `Arborescence_V7.txt`
- `ARCHITECTURE_V7_ENGINE.md`
- `ENGINEERING-HANDBOOK_V7.md`
- `MANIFESTE_V7.md`
- `MES_V7.md`
- `PLAN_MAITRE_V7_FUSION_COMPLETE.md`
- `RAPPORT (1).md`

**Méthodologie :** Audit statique du code source, exécution des tests automatisés, exécution des scripts Go/No-Go, analyse de conformité documentation/code.

---

## 1. EXECUTIVE SUMMARY

### Bilan de santé général

SMART_AO V7.1 est un projet d'ampleur, structuré comme un "système d'exploitation" métier pour les entreprises de BTP. L'architecture globale est **saine sur le fond** : single-tenant pur, séparation IA qualitative / Garage Math déterministe, registry d'agents par capacités, event bus, dead letter queue, fleet engine, fallback LLM local.

Les fondations techniques les plus critiques sont en place et validées :
- **354 tests passent, 4 skipped, 0 failed**
- **Go/No-Go Single VPS : 39/39 PASS**
- **Go/No-Go Fleet : 46/46 PASS**
- **Workflow Engine conforme aux 6 étapes canoniques** (PARSER → EXTRACTION → CLASSIFICATION → AGENTS → COMPILATION → RAPPORT)
- **Retrait complet de `tenant_id`** dans le code Python et les modèles SQLAlchemy
- **OR-Tools (`ortools`) et BGE-M3 (`sentence-transformers`) sont effectivement utilisés**
- **RBAC renforcé** par un middleware global de strip financier (`app/api/middleware/rbac_strip.py`)

### Note sur 100

| Pilier | Note | Justification |
|---|---|---|
| Architecture & Ingénierie logicielle | 72/100 | Bonne structuration OS, registry, event bus. Documentation encore partiellement en V6. Dette de cohérence doc/code. |
| Sécurité & Étanchéité | 68/100 | RBAC global actif, mais protection uniquement par strip middleware (pas de `require_admin` sur les endpoints), fail-open sur erreur de strip. Pas de RLS Postgres. |
| Pertinence métier BTP | 80/100 | Couverture fonctionnelle très large et pertinente (33 modules, 16 solveurs). Vrai ROI pour le Patron. |
| Performance & Solveurs numériques | 75/100 | Garage Math sans LLM, Decimal 28, OR-Tools + PuLP. Manque de traçabilité formelle preuve/audit des calculs. |
| **Global** | **73/100** | **Bonne base industrialisable, mais exige un sprint de durcissement sécurité et d'harmonisation documentation avant 1er client payant.** |

---

## 2. MATRICE DES RISQUES CRITIQUES

| ID | Risque | Gravité | Probabilité | Impact si réalisé | Mitigation actuelle | Action requise |
|---|---|---|---|---|---|---|
| R1 | **Fuite de données financières** si un endpoint renvoie un champ hors `FIELDS_STRIP` | CRITIQUE | Moyenne | Perte de confiance Patron, fuite marge vers salariés, litige | Middleware RBAC strip + catalogue `FIELDS_STRIP` | Auditer exhaustivement les réponses API ; ajouter des tests de fuite par champ ; durcir les endpoints avec `require_admin` |
| R2 | **Fail-open du middleware RBAC** en cas d'erreur interne (JSON corrompu, body_iterator vide) | CRITIQUE | Faible | Réponse originale non stripée = fuite possible | `except Exception: return response` | Transformer en fail-close pour les rôles non-Patron ou au moins logger/incident |
| R3 | **Aucun `require_admin`/`require_patron` sur les endpoints** — protection uniquement par strip | ÉLEVÉE | Moyenne | Un bug de nommage expose tout | Middleware global | Ajouter des guards explicites sur les endpoints sensibles (défense en profondeur) |
| R4 | **Documentation RAPPORT (1).md encore en partie V6** — incohérences 28/33 modules, 24/39 critères | ÉLEVÉE | Élevée | Décisions métier sur base fausse, mauvaise implémentation par équipe | Corrections partielles effectuées | Harmonisation complète : transformer les sections V6 non marquées en archive ou les mettre à jour |
| R5 | **Fallback BGE-M3 aléatoire** si `sentence-transformers` échoue au runtime | ÉLEVÉE | Faible | RAG dégradé, faux positifs/négatifs, mauvaise analyse DCE | Fallback déterministe en test | Bloquer le fallback aléatoire en production ; lever une erreur 503 si BGE-M3 ne charge pas |
| R6 | **Tests V7.1 modules et tech** ne couvrent pas exhaustivement les cas limites | MOYENNE | Moyenne | Régression en production | 354 tests passent | Ajouter des tests d'intégration E2E avec DCE réels et golden files |
| R7 | **Pas de preuve formelle d'audit des calculs Garage** (hash, signature, replay) | MOYENNE | Moyenne | Contestation d'expert-comptable ou tribunal | Logs et Decimal 28 | Ajouter un `CalculationAuditLog` avec hash SHA-256 des entrées/sorties solveur |
| R8 | **Fleet engine / cosign** non testé en conditions réelles multi-VPS | MOYENNE | Faible | Mise à jour fleet corrompue | Clé cosign dans scripts | Test E2E de déploiement fleet sur 2 VPS |
| R9 | **Absence de `planning_ortools.py`** dédié — OR-Tools utilisé seulement dans `chiffrage_pulp.py` | FAIBLE | Faible | Fonctionnalités de scheduling avancées non délivrées | `chiffrage_pulp.py` utilise `pywraplp` | Créer `planning_ortools.py` si le Mémoire Booster Gantt en a besoin |
| R10 | **Dépendances non-verrouillées** — `requirements.txt` sans hashes | MOYENNE | Moyenne | Supply-chain attack, incompatibilité | Versions fixes | Migrer vers `requirements.lock` avec hashes ou `poetry.lock` |

---

## 3. AUTOPSIE TECHNIQUE (Code & Archi)

### 3.1 Architecture générale

Le projet suit une architecture en **couches spécialisées** :
- `app/engines/` : moteurs métier (workflow, agent_runtime, math_engine, knowledge_engine, security_engine, event_bus, fleet_engine...)
- `app/agents/` : agents IA héritant de `BaseAgent`
- `app/api/` : endpoints FastAPI
- `app/models/` : modèles SQLAlchemy
- `app/schemas/` : schémas Pydantic
- `tests/` : tests unitaires et d'intégration

**Forces :**
- Séparation claire entre les préoccupations.
- `AgentRegistry` singleton avec auto-discovery par capacités (`ADR-042`).
- `EventBus` + `DLQ` pour la résilience.
- `FleetUpdater` / `cosign_verifier` / `license_checker` pour le déploiement multi-VPS.

**Faiblesses :**
- Plusieurs fichiers `app/tests/` et `tests/` — potentielle duplication ou confusion.
- Le package `app/tests` est importable depuis l'application, ce qui n'est pas une bonne pratique.
- La documentation contient encore des sections V6 non marquées "Archive", ce qui crée de l'ambiguïté.

### 3.2 Workflow Engine — conformité 6 étapes

`app/engines/workflow_engine/workflow.py:69-76` définit bien les 6 étapes canoniques :

```python
STANDARD_STEPS = [
    "parser_step",
    "extraction_step",
    "classification_step",
    "agents_step",
    "compilation_step",
    "rapport_step",
]
```

✅ **Conforme.** L'ancien commentaire mentionnant 10 étapes a été corrigé.

### 3.3 Retrait de `tenant_id`

Commande de vérification :

```bash
grep -R "tenant_id" app/ tests/ scripts/ --include="*.py" --include="*.sh"
```

Résultat : seuls deux commentaires indiquent l'absence volontaire de `tenant_id`.

✅ **Retrait effectif.** Modèles nettoyés (`Mission`, `MissionStep`, `MissionEvent`, `Project`, `User`, `VaultDocument`, `AuditLog`).

### 3.4 Math Engine — Solveurs et OR-Tools

- `app/engines/math_engine/chiffrage_pulp.py` importe `ortools.linear_solver.pywraplp` (ligne 34) et l'utilise comme solveur primaire (ligne 257-259).
- 16 solveurs sont présents : les 11 V6 historiques/étendus + `penibilite_solver.py`, `vigilance_solver.py`, `zan_solver.py`, `formule_algebra_checker.py`, `sourcing_api_solver.py`.
- Aucun import LLM dans `app/engines/math_engine/`.

⚠️ **Remarque :** OR-Tools n'est utilisé que dans le solveur de chiffrage. Le fichier `planning_ortools.py` mentionné dans la doc n'existe pas. Si le Gantt OR-Tools du Mémoire Booster est attendu, il faut le créer.

### 3.5 Embedding Engine — BGE-M3

`app/engines/knowledge_engine/embedding_engine.py` :
- Préfère `sentence-transformers` (BAAI/bge-m3).
- Fallback `flag_embedding`.
- Fallback aléatoire déterministe pour les tests.

⚠️ **Risque :** Le fallback aléatoire en production rendrait le RAG inutilisable sans échec visible. Il faut soit le désactiver en `ENV=production`, soit lever une exception.

### 3.6 Sécurité — RBAC

**Points positifs :**
- `RBACFinancialStripMiddleware` est monté dans `app/main.py:80`.
- Catalogue `FIELDS_STRIP` étendu aux champs V7.1 (pénibilité, URSSAF, ZAN, formules, sourcing).
- Seul `Role.PATRON` voit les données financières.

**Points de fragilité :**
- Le middleware est **fail-open** : en cas d'erreur, il renvoie la réponse originale (`return response` ligne 122). Un bug JSON ou un body_iterator épuisé expose les données.
- Aucun endpoint n'utilise de garde explicite (`require_admin`, `require_patron`). Toute la sécurité repose sur le strip. Si un développeur nomme un champ `"montant_estime"` au lieu de `"montant"`, il passe.
- Pas de Row Level Security (RLS) Postgres. C'est acceptable en single-tenant pur mais doit être documenté comme choix assumé.

### 3.7 Tests

```text
354 passed, 4 skipped, 8 warnings
```

✅ Couverture correcte pour une base industrielle. Les 4 skipped doivent être identifiés et traités (probablement des tests conditionnels sur des dépendances optionnelles).

---

## 4. VERDICT MÉTIER (Le regard du Patron BTP)

### 4.1 Résolution du vrai problème

**Verdict : OUI, le logiciel attaque les bons problèmes.**

Les 33 modules couvrent les axes mortels des AO BTP :
- **Juridique/financier** : BT index, pénalités, BFR, avance/RG, PAB, capacité financière.
- **Technique/site** : RAT amiante, SOGED REP, site occupé, ZAN/Trackterres, matériaux post-Covid.
- **Administratif/élimination** : deadline, alloti, enveloppe 47 pièces, DC4 plafond, certif live.
- **Note technique** : mémoire booster, RSE +15%, E+C-, variante.
- **Post-gagné** : avenant tracker, contentieux generator, post-gagné tracker.
- **Nouveaux risques 2026** : pénurie main-d'œuvre, vigilance URSSAF, syntaxe formules révision, dépôt API.

### 4.2 Adéquation terrain

**Forces :**
- Le workflow salarié → admin → dépôt reflète la répartition des rôles dans une PME BTP.
- Le double artefact HANDOFF+ (complet admin / expurgé salarié) est une vraie réponse au risque de fuite.
- La doctrine "IA lit, Garage chiffre, Patron valide" est exactement ce qu'il faut pour un tribunal ou un expert-comptable.

**Faiblesses :**
- L'intégration API Profil Acheteur (PLACE, BOAMP, etc.) est simulée/testée mais pas prouvée en production. Les API publiques changent souvent.
- Le détecteur de "prix-mémoire cohérence" repose sur des données historiques qui doivent être alimentées manuellement ou par un vault prix-mémoire ; sans historique, l'agent est inopérant.

### 4.3 Impact ROI

**Verdict : AVANTAGE CONCURRENTIEL RÉEL.**

- Un seul piège V7.1 évité (ex: pénurie RH 42 k€, ZAN 28 k€, URSSAF 140 k€, formule erronée 64 k€) rentabilise plusieurs années d'abonnement (549 €/mois).
- Le logiciel transforme l'AO d'une course au prix le plus bas en une décision de comité avec chiffrage des risques.

---

## 5. PLAN DE REMÉDIATION CHIRURGICAL

### 5.1 Sécurité (priorité P0)

| Action | Fichier(s) | Détails |
|---|---|---|
| Durcir le middleware RBAC en fail-close | `app/api/middleware/rbac_strip.py:119-122` | Si le strip échoue pour un rôle non-Patron, retourner une erreur 500 ou une réponse vide, jamais la réponse originale. |
| Ajouter des guards sur endpoints sensibles | `app/api/v1/endpoints/*.py` | Utiliser `require_admin` / `require_patron` sur les routes finance, vault admin, handoff complet. |
| Tests de fuite par champ | `tests/unit/test_rbac_strip_extended.py` | Pour chaque champ de `FIELDS_STRIP`, vérifier qu'il est absent des réponses salarié. |
| Désactiver fallback BGE-M3 aléatoire en prod | `app/engines/knowledge_engine/embedding_engine.py:66-69` | Lever `RuntimeError` si ni sentence-transformers ni flag_embedding ne chargent. |
| Ajouter RLS Postgres (documenté) | `ENGINEERING-HANDBOOK_V7.md` | Même en single-tenant, activer RLS sur les tables sensibles comme couche de défense supplémentaire. |

### 5.2 Documentation (priorité P0)

| Action | Fichier | Détails |
|---|---|---|
| Harmoniser totalement RAPPORT (1).md | `docs/RAPPORT (1).md` | Transformer toutes les sections V6 non marquées en "Archive V6" ou les mettre à jour (28→33, 11→16, 24→39, 31→46). Vérifier les liens internes. |
| Vérifier MANIFESTE_V7.md | `docs/MANIFESTE_V7.md` | Confirmer que les 17 corrections sont appliquées et cohérentes avec RAPPORT (1).md. |
| Documenter le choix fail-open/fail-close | `ENGINEERING-HANDBOOK_V7.md §Sécurité` | Expliquer pourquoi le middleware est fail-open et la feuille de route pour le durcir. |

### 5.3 Solveurs et Math Engine (priorité P1)

| Action | Fichier | Détails |
|---|---|---|
| Créer `CalculationAuditLog` | `app/engines/security_engine/audit.py` ou nouveau fichier | Hash SHA-256 des entrées/sorties de chaque solveur pour traçabilité tribunal. |
| Créer `planning_ortools.py` si besoin | `app/engines/math_engine/planning_ortools.py` | Scheduling Gantt avec OR-Tools pour le Mémoire Booster. |
| Tests cas limites solveurs V7.1 | `tests/unit/test_*_solver.py` | Vérifier division par zéro, indices INSEE manquants, attestation URSSAF None, etc. |

### 5.4 Industrialisation (priorité P1)

| Action | Fichier | Détails |
|---|---|---|
| Supprimer `app/tests` du package applicatif | déplacer vers `tests/` | Éviter d'embarquer les tests en production. |
| Verrouiller les dépendances | `requirements.lock` | Ajouter des hashes pour la supply-chain security. |
| Tester Fleet E2E | infrastructure | Déploiement sur 2 VPS, vérifier cosign + isolation. |
| Traiter les 4 tests skipped | `pytest -v` | Identifier pourquoi ils sont skipped et les activer ou documenter. |

### 5.5 Métier (priorité P2)

| Action | Fichier | Détails |
|---|---|---|
| Connecteur API Profil Acheteur réel | `app/engines/api_gateway/sourcing_api_solver.py` | Implémenter les appels vers PLACE / API Marchés Publics avec retries et cache. |
| Alimenter le Vault Prix-Mémoire | `docs/RAPPORT (1).md §7.16` | Définir comment l'entreprise injecte ses prix historiers pour activer la cohérence. |
| Mode Panique / Emergency Bypass | V7.1 | Si ce module est annoncé, il manque sa spécification et son implémentation. |

---

## 6. CONCLUSION

SMART_AO V7.1 est **un projet solide, bien architecturé et fonctionnellement très pertinent** pour le BTP. Les fondations (single-tenant, IA/Garage séparés, RBAC, OR-Tools, BGE-M3, tests, Go/No-Go) sont en place et validées.

Le principal écart avant une mise en production client réside dans :
1. **La sécurité en profondeur** : remplacer le strip middleware unique par une défense en profondeur (guards endpoints + fail-close).
2. **La cohérence documentaire** : harmoniser RAPPORT (1).md sur les chiffres V7.1 (33 modules, 16 solveurs, 39/46 critères).
3. **La traçabilité des calculs** : ajouter un audit log des solveurs pour la défense juridique.

**Recommandation : GO conditionnel.** Le projet peut passer en pré-production / beta fermée dès que les actions P0 sécurité et documentation sont traitées. Le 1er client payant doit attendre la validation des tests E2E avec DCE réels et la revue de sécurité fail-close.

---

**Fin du rapport.**
