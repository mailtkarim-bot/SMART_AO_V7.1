# PLAN DE REMÉDIATION RBAC - SMART_AO V7.1
## Corrections Critiques de Sécurité - Niveau P0

**Date :** 09/08/2026  
**Priorité :** CRITIQUE (NO-GO Production)  
**Responsable :** Équipe Développement  

---

## RÉSUMÉ EXÉCUTIF

Ce document détaille le plan complet pour corriger les **failles de sécurité RBAC critiques** identifiées lors de l'audit du système SMART_AO V7.1. Ces failles permettent à des utilisateurs non-autorisés (conducteur_travaux, charge_etudes) d'accéder aux données financières confidentielles via les endpoints API directs.

---

## 1. FAILLE CRITIQUE N°1 : ENDPOINTS FINANCE SANS GARDE RBAC

### Problème
Les **21 endpoints financiers** dans `/app/engines/api_gateway/finance.py` et `/app/engines/api_gateway/finance_advanced.py` n'ont **AUCUNE garde RBAC explicite**.

**Fichiers concernés :**
- `/workspace/app/engines/api_gateway/finance.py` (15 endpoints)
- `/workspace/app/engines/api_gateway/finance_advanced.py` (6 endpoints)

### Solution
Ajouter `Depends(require_financial_access)` sur TOUS les endpoints sensibles.

### Endpoints à corriger (liste exhaustive)

#### Fichier : finance.py

| Ligne | Endpoint | Méthode | Action requise |
|-------|----------|---------|----------------|
| 127 | `/penalites/ccag` | POST | Ajouter `require_financial_access` |
| 155 | `/penalites/ccmi` | POST | Ajouter `require_financial_access` |
| 183 | `/marge/brute` | POST | Ajouter `require_financial_access` |
| 204 | `/marge/analyser` | POST | Ajouter `require_financial_access` |
| 236 | `/tresorerie/avance` | POST | Ajouter `require_financial_access` |
| 253 | `/tresorerie/bfr` | POST | Ajouter `require_financial_access` |
| 281 | `/bt01/projection` | POST | Ajouter `require_financial_access` |
| 298 | `/bt01/rapport` | POST | Ajouter `require_financial_access` |
| 319 | `/capacite/ratios` | POST | Ajouter `require_financial_access` |
| 347 | `/capacite/verifier` | POST | Ajouter `require_financial_access` |
| 381 | `/pab/detecter` | POST | Ajouter `require_financial_access` |
| 395 | `/pab/analyser-lots` | POST | Ajouter `require_financial_access` |
| 407 | `/sous-chiffrage/detecter` | POST | Ajouter `require_financial_access` |
| 421 | `/mapa/analyser` | POST | Ajouter `require_financial_access` |
| 434 | `/worst-case/analyser` | POST | Ajouter `require_financial_access` |

#### Fichier : finance_advanced.py

| Ligne | Endpoint | Méthode | Action requise |
|-------|----------|---------|----------------|
| 80 | `/chiffrage/optimiser` | POST | Ajouter `require_financial_access` |
| 103 | `/chiffrage/simuler` | POST | Ajouter `require_financial_access` |
| 144 | `/simulation/chantier` | POST | Ajouter `require_financial_access` |
| 205 | `/simulation/scenarios` | POST | Ajouter `require_financial_access` |
| 238 | `/prevision/risques` | POST | Ajouter `require_financial_access` |
| 291 | `/prevision/tresorerie` | POST | Ajouter `require_financial_access` |

---

## 2. FAILLE CRITIQUE N°2 : IMPORT NON UTILISÉ DANS missions.py

### Problème
Le fichier `/workspace/app/api/v1/endpoints/missions.py` importe `require_financial_access` ligne 24 mais ne l'utilise JAMAIS.

### Solution
Deux options :
1. **Option A** : Supprimer l'import si aucune route de mission ne nécessite de protection financière
2. **Option B** : Utiliser la garde sur les routes qui retournent des données financières

**Recommandation :** Option A (suppression) car le filtrage RBAC est déjà appliqué via `enforcer.filter_mission_data_by_role()` lignes 107, 110, 250, 253.

---

## 3. AMÉLIORATION : TESTS D'INTRUSION RBAC

### Problème
Aucun test automatisé ne vérifie que les rôles non-PATRON sont correctement bloqués sur les endpoints financiers.

### Solution
Créer `/workspace/tests/unit/test_rbac_finance_endpoints.py` avec :
- Tests pour chaque endpoint financier
- Vérification que les rôles `conducteur_travaux`, `charge_etudes`, `qsse`, `sous_traitant` reçoivent une erreur 403
- Vérification que le rôle `patron` obtient un succès 200

---

## 4. AMÉLIORATION : AUDIT TRAIL DES ACCÈS FINANCIERS

### Problème
Aucun logging systématique des accès (succès/échec) aux données financières.

### Solution
Enrichir `/workspace/app/engines/security_engine/audit.py` avec :
- Fonction `log_financial_access()` 
- Logging de chaque tentative d'accès aux endpoints `/api/v1/finance/*`
- Inclusion : user_id, role, resource, action, succès/échec, IP, timestamp

---

## FEUILLE DE ROUTE DÉTAILLÉE

### Phase 1 : Corrections Immédiates (J+1)

**Tâche 1.1 :** Modifier `/workspace/app/engines/api_gateway/finance.py`
- Importer `require_financial_access` depuis `app.api.middleware.auth`
- Ajouter `_: dict = Depends(require_financial_access)` à chaque endpoint financier
- Temps estimé : 2 heures

**Tâche 1.2 :** Modifier `/workspace/app/engines/api_gateway/finance_advanced.py`
- Importer `require_financial_access` depuis `app.api.middleware.auth`
- Ajouter `_: dict = Depends(require_financial_access)` à chaque endpoint financier
- Temps estimé : 1 heure

**Tâche 1.3 :** Nettoyer `/workspace/app/api/v1/endpoints/missions.py`
- Supprimer l'import non utilisé ligne 24
- Temps estimé : 15 minutes

### Phase 2 : Tests de Non-Régression (J+2)

**Tâche 2.1 :** Créer `/workspace/tests/unit/test_rbac_finance_endpoints.py`
- Implémenter tests paramétrés pour tous les endpoints financiers
- Couverture : 4 rôles × 21 endpoints = 84 tests minimum
- Temps estimé : 4 heures

**Tâche 2.2 :** Exécuter la suite de tests complète
- Vérifier que tous les tests existants passent toujours
- Vérifier que les nouveaux tests RBAC passent
- Temps estimé : 1 heure

### Phase 3 : Audit Trail (J+3)

**Tâche 3.1 :** Enrichir `/workspace/app/engines/security_engine/audit.py`
- Ajouter fonction `log_financial_access()`
- Intégrer le logging dans les endpoints finance
- Temps estimé : 3 heures

**Tâche 3.2 :** Configurer le logging centralisé
- S'assurer que les logs d'audit sont envoyés vers SIEM/Syslog
- Temps estimé : 2 heures

### Phase 4 : Validation Finale (J+4)

**Tâche 4.1 :** Audit de sécurité manuel
- Tester manuellement chaque endpoint avec différents rôles
- Vérifier l'absence de fuites de données
- Temps estimé : 4 heures

**Tâche 4.2 :** Mise à jour documentation
- Documenter les gardes RBAC dans ARCHITECTURE_V7_ENGINE.md
- Mettre à jour les spécifications de sécurité
- Temps estimé : 2 heures

---

## CRITÈRES D'ACCEPTATION

Pour que ce plan soit considéré comme complété :

1. ✅ **TOUS** les endpoints financiers ont une garde `require_financial_access` explicite
2. ✅ L'import non utilisé dans `missions.py` est supprimé
3. ✅ **100%** des tests RBAC passent (rôles non-PATRON bloqués avec 403)
4. ✅ L'audit trail des accès financiers est implémenté et fonctionnel
5. ✅ Aucun test existant n'est cassé par les modifications
6. ✅ La documentation de sécurité est mise à jour

---

## VALIDATION GO/NO-GO

Après exécution de ce plan :

- **GO** si tous les critères d'acceptation sont validés
- **NO-GO** si au moins un endpoint financier reste sans garde RBAC

**Décision finale :** Comité de direction + RSSI requis avant déploiement production.

---

*Document généré par l'Auditeur Principal & Inspecteur Système Suprême*  
*Copyright 2026 - Usage interne uniquement*
