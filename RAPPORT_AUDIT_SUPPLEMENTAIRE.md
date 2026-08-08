# RAPPORT D'AUDIT SUPPLÉMENTAIRE — SMART_AO V7.1
## Inspection Chirurgicale Post-Audit Initial

**Date :** 2026-08-07  
**Auditeur :** Inspecteur Système Suprême (IA)  
**Périmètre :** Code source, architecture, sécurité RBAC, embedding engine, tests  

---

## 1. EXECUTIVE SUMMARY — MISE À JOUR POST-INSPECTION

### Note Révisée sur 100

| Pilier | Note Initiale | **Note Révisée** | Δ | Justification |
|--------|---------------|------------------|---|---------------|
| Architecture & Ingénierie logicielle | 72/100 | **70/100** | -2 | Confirmation dette doc/code + package `app/tests` importable |
| Sécurité & Étanchéité | 68/100 | **65/100** | -3 | **Fail-open confirmé** ligne 122 `rbac_strip.py` ; aucun endpoint ne utilise `require_admin` |
| Pertinence métier BTP | 80/100 | **80/100** | 0 | Couverture fonctionnelle toujours excellente |
| Performance & Solveurs numériques | 75/100 | **74/100** | -1 | Fallback BGE-M3 aléatoire toujours actif en production |
| **Global** | 73/100 | **71/100** | **-2** | **Les risques R1, R2, R3, R5 sont confirmés par inspection du code** |

### Constats Immédiats (Preuves à l'Appui)

1. **Le middleware RBAC est bel et bien FAIL-OPEN** :  
   - Fichier : `app/api/middleware/rbac_strip.py:119-122`  
   - Citation : `except Exception as exc: logger.warning(...); return response`  
   - **Impact** : En cas d'erreur de parsing JSON ou de body_iterator épuisé, la réponse originale NON STRIPPÉE est renvoyée → fuite financière possible.

2. **Aucun endpoint n'utilise les guards explicites `require_admin` / `require_financial_access`** :  
   - Fichier : `app/api/middleware/auth.py:237-261` définit `require_admin_access()`  
   - Recherche : `grep -rn "require_admin" app/api/v1/endpoints/*.py` → **0 résultat**  
   - **Impact** : La sécurité repose UNIQUEMENT sur le strip middleware. Un champ mal nommé (`"montant_estime"` au lieu de `"montant"`) passe au travers.

3. **Le fallback BGE-M3 aléatoire est TOUJOURS ACTIF** :  
   - Fichier : `app/engines/knowledge_engine/embedding_engine.py:66-92`  
   - Lignes 87-92 : génération d'un vecteur aléatoire déterministe via `np.random.default_rng(seed=abs(hash(text)))`  
   - **Impact** : En production, si `sentence-transformers` et `flag_embedding` échouent, le RAG produit des相似ités fausses sans lever d'erreur.

4. **Le catalogue `FIELDS_STRIP` est complet mais vulnérable au contournement par homonymie** :  
   - Fichier : `app/engines/security_engine/rbac_fields.py:27-147`  
   - 85+ champs listés (V6 + V7.1)  
   - **Failles** :  
     - Un développeur peut nommer un champ `"price_unitaire"` (non listé) au lieu de `"prix_unitaire"` → non strippé.  
     - Pas de normalisation automatique (lowercase + underscore) avant comparaison.

5. **Structure de tests problématique** :  
   - Dossier `app/tests/` existe ET est importable (mauvaise pratique).  
   - Les vrais tests sont dans `/workspace/tests/` mais pytest plante à cause de `libtmux` (mark sur fixture).

---

## 2. MATRICE DES RISQUES CRITIQUES — VERSION CORRIGÉE

| ID | Risque | Gravité | Probabilité | Preuve Code | Action Requise |
|----|--------|---------|-------------|-------------|----------------|
| **R1** | Fuite données financières via champ non-listé | CRITIQUE | Moyenne | `rbac_fields.py` liste fermée ; pas de wildcard | Ajouter tests unitaires par champ + normalisation |
| **R2** | **Fail-open du middleware RBAC** | **CRITIQUE** | **Moyenne** | **`rbac_strip.py:122`** `return response` | Transformer en `HTTP 500` ou réponse vide pour rôles non-Patron |
| **R3** | Aucun garde-fou sur endpoints sensibles | ÉLEVÉE | Moyenne | `grep require_admin endpoints/*.py` = 0 | Ajouter `Depends(require_admin_access)` sur `/finance/*`, `/vault/*`, `/handoff` |
| **R4** | Fallback BGE-M3 aléatoire en production | ÉLEVÉE | Faible | `embedding_engine.py:87-92` | Lever `RuntimeError` si backend = `"fallback"` et `ENV=production` |
| **R5** | Documentation incohérente (V6 vs V7.1) | ÉLEVÉE | Élevée | `RAPPORT_AUDIT_SYSTEME_BTP.md` contient sections V6 | Harmoniser ou archiver explicitement |
| **R6** | Package `app/tests` importable en prod | MOYENNE | Moyenne | Dossier `app/tests/__init__.py` existe | Déplacer vers `tests/` racine uniquement |
| **R7** | Pas de Row Level Security Postgres | MOYENNE | Faible | Single-tenant pur assumé | Documenter comme choix architectural (ADR) |
| **R8** | Supply-chain : pas de hashes requirements | MOYENNE | Moyenne | `requirements.txt` sans hashes | Migrer vers `poetry.lock` ou `pip-tools` |

---

## 3. AUTOPSIE TECHNIQUE DÉTAILLÉE

### 3.1 Architecture RBAC — Défense en Profondeur Absente

**État actuel :**
```
Requête → [Middleware RBAC Strip] → Endpoint → Réponse JSON → [Strip si nécessaire] → Client
```

**Problème :** Une seule couche de défense. Si le middleware échoue (exception), la réponse brute passe.

**Recommandation : Defense-in-Depth**
```
Requête → [Auth JWT] → [Guard Endpoint (require_admin)] → Endpoint → [Strip Middleware] → Réponse → Client
```

**Fichiers à modifier :**
1. `app/api/v1/endpoints/finance.py` — Ajouter `Depends(require_financial_access)` sur chaque route.
2. `app/api/v1/endpoints/vault_core.py` — idem.
3. `app/api/v1/endpoints/handoff_plus.py` — idem.
4. `app/api/middleware/rbac_strip.py:119-122` — Remplacer `return response` par :
   ```python
   if role_value is None or not _role_can_access_financial(role_value):
       # Fail-close : on ne renvoie jamais la réponse originale
       return Response(
           content=json.dumps({"error": "RBAC strip failed"}),
           status_code=500,
           headers={"X-RBAC-Strip-Failed": "true"},
           media_type="application/json",
       )
   ```

### 3.2 Embedding Engine — Fallback Dangereux

**Extrait incriminé (`embedding_engine.py:87-92`) :**
```python
else:
    # Fallback déterministe par hash pour les tests
    rng = np.random.default_rng(seed=abs(hash(text)) % (2 ** 31))
    emb = rng.random(DEFAULT_DIM).astype(np.float32)
    norm = np.linalg.norm(emb)
    emb = emb / norm if norm > 0 else emb
```

**Correction requise :**
```python
else:
    # Production : on lève une erreur critique
    if settings.ENVIRONMENT == "production":
        logger.critical("BGE-M3 unavailable in production — aborting")
        raise RuntimeError("Embedding provider BGE-M3 failed to load")
    # Tests/dev only : fallback déterministe
    logger.warning("BGE-M3 fallback activé (embeddings aléatoires normalisés)")
    # ... (code fallback inchangé)
```

### 3.3 Structure du Projet — `app/tests` à Supprimer

**Problème :** Le dossier `app/tests/` contient des fichiers `__init__.py` et est donc un package Python importable. Cela signifie que :
- Les tests peuvent être embarqués en production.
- Confusion entre `app/tests/` et `/workspace/tests/`.

**Action :**
```bash
mv app/tests/unit/* tests/unit/ 2>/dev/null || true
mv app/tests/integration/* tests/integration/ 2>/dev/null || true
rm -rf app/tests/
```

### 3.4 Catalogue `FIELDS_STRIP` — Vulnérabilité Nommage

**Exemple d'attaque :**
Un développeur nomme un champ `"priceUnitaire"` (camelCase) au lieu de `"prix_unitaire"`.  
Le middleware compare `key.lower()` mais `"priceunitaire".lower()` n'est pas dans `FIELDS_STRIP`.

**Mitigation :**
1. Ajouter des alias dans `FIELDS_STRIP` : `"priceunitaire"`, `"prixunitaire"`, `"unit_price"`, etc.
2. OU : Normaliser les clés avant comparaison (snake_case → lowercase).
3. OU : Utiliser un modèle Pydantic avec validation des noms de champs autorisés.

---

## 4. VERDICT MÉTIER (Rappel Patron BTP)

**Le logiciel reste une ARME DE GUERRE COMMERCIALE**, mais :

1. **La faille R2 (fail-open)** pourrait exposer tes marges brutes à un conducteur de travaux mécontent → risque juridique + perte de confiance.
2. **Le fallback R4 (BGE-M3 aléatoire)** pourrait faire rater un appel d'offres parce que le RAG a retourné des documents non pertinents → perte sèche de CA.

**ROI toujours excellent** : un seul piège V7.1 évité (URSSAF 140 k€, ZAN 28 k€) rembourse 20 ans d'abonnement. Mais la crédibilité du outil est en jeu si une fuite arrive.

---

## 5. PLAN DE REMÉDIATION CHIRURGICAL — PRIORITISÉ

### P0 (Urgence < 48h)

| # | Action | Fichier(s) | Commande / Patch |
|---|--------|------------|------------------|
| 1 | **Transformer le middleware en fail-close** | `app/api/middleware/rbac_strip.py:119-122` | Voir patch section 3.1 |
| 2 | **Ajouter guards sur endpoints finance** | `app/api/v1/endpoints/finance.py`, `finance_advanced.py` | `@router.get(..., dependencies=[Depends(require_financial_access)])` |
| 3 | **Désactiver fallback BGE-M3 en prod** | `app/engines/knowledge_engine/embedding_engine.py:87-92` | Voir patch section 3.2 |
| 4 | **Supprimer `app/tests/`** | Shell | `rm -rf app/tests/` après migration |

### P1 (Semaine 1)

| # | Action | Fichier(s) | Détails |
|---|--------|------------|---------|
| 5 | Tests de fuite par champ | `tests/unit/test_rbac_strip_extended.py` | Pour chaque champ de `FIELDS_STRIP`, vérifier absence dans réponses salarié |
| 6 | Normalisation noms de champs | `app/engines/security_engine/rbac_fields.py` | Fonction `normalize_field_name()` + alias |
| 7 | Documentation harmonisée | `docs/RAPPORT (1).md` | Marquer sections V6 comme "Archive" ou mettre à jour chiffres |
| 8 | RLS Postgres (optionnel) | `ENGINEERING-HANDBOOK_V7.md` | Documenter comme choix assumé single-tenant |

### P2 (Mois 1)

| # | Action | Fichier(s) | Détails |
|---|--------|------------|---------|
| 9 | Migration poetry/pip-tools | `pyproject.toml` / `requirements.lock` | Hashes pour supply-chain security |
| 10 | Connecteur API Profil Acheteur réel | `app/engines/api_gateway/sourcing_api_solver.py` | Implémenter PLACE / BOAMP avec retries |
| 11 | Audit log des solveurs | `app/engines/security_engine/audit.py` | Hash SHA-256 entrées/sorties pour traçabilité tribunal |

---

## 6. CONCLUSION FINALE

**SMART_AO V7.1 est un projet SOLIDE mais avec 3 failles CRITIQUES confirmées :**

1. ✅ **Architecture globale saine** (single-tenant, IA/Garage séparés, registry, event bus).
2. ❌ **Sécurité RBAC trop fragile** (fail-open, pas de guards endpoints).
3. ❌ **Fallback embedding dangereux en production**.
4. ⚠️ **Documentation partiellement incohérente**.

**Recommandation : GO CONDITIONNEL MAINTENU**, mais **interdiction formelle de mettre en production client avant correction P0**.

**Prochaine étape :** Exécuter les 4 actions P0, relancer les tests Go/No-Go, puis beta fermée avec 3 clients pilotes.

---

**Fin du rapport supplémentaire.**

*Généré par l'Inspecteur Système Suprême — 2026-08-07*
