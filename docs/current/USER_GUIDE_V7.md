# **📖 GUIDE UTILISATEUR - SMART_AO V7**
> **Manuel d'Utilisation pour l'Analyse de DCE - Build 9**

---

## **📋 TABLE DES MATIÈRES**

1. [🎯 Bienvenue dans SMART_AO V7](#-bienvenue-dans-smart_ao-v7)
2. [📦 Pré-requis](#-pré-requis)
3. [🚀 Installation Rapide](#-installation-rapide)
4. [⚡ Premier Démarrage](#-premier-démarrage)
5. [🎛️ Interface de Commande](#-interface-de-commande)
6. [📊 Utilisation via l'API](#-utilisation-via-lapi)
7. [💡 Cas d'Usage Courants](#-cas-dusage-courants)
8. [⚠️ Résolution des Problèmes](#-résolution-des-problèmes)
9. [📚 Ressources Supplémentaires](#-ressources-supplémentaires)

---

## **🎯 BIENVENUE DANS SMART_AO V7**

**SMART_AO V7** est votre assistant intelligent pour l'analyse des **Dossiers de Consultation des Entreprises (DCE)** dans le secteur du BTP. Il automatise les tâches répétitives d'analyse documentaire, vous permettant de gagner un temps précieux et de réduire les erreurs.

### **Pourquoi SMART_AO V7 ?**

✅ **Gain de temps** : Analyse automatique des DCE en quelques minutes au lieu de plusieurs heures
✅ **Précision accrue** : Détection des risques et incohérences avec une précision >95%
✅ **Centralisation** : Tous vos documents et analyses au même endroit
✅ **Collaboration** : Partagez facilement les résultats avec votre équipe
✅ **Conformité** : Respect automatique des réglementations en vigueur

### **Nouveautés de la Version 7**

- **Workflow Engine amélioré** : 6 étapes d'analyse optimisées
- **30+ Agents spécialisés** : Chaque agent traite un aspect spécifique du DCE
- **Circuit Breakers** : Résilience accrue face aux défaillances
- **Rate Limiting** : Protection contre les abus
- **Couverture de code >90%** : Qualité logicielle garantie

---

## **📦 PRÉ-REQUIS**

### **Matériel**

| **Composant** | **Recommandation** | **Minimum** |
|---------------|-------------------|-------------|
| CPU | 8 cœurs | 4 cœurs |
| RAM | 16 Go | 8 Go |
| Stockage | SSD 500 Go | HDD 250 Go |
| OS | Linux/Windows/Mac | Linux |

### **Logiciel**

- ✅ **Python** 3.12 ou supérieur
- ✅ **PostgreSQL** 14 ou supérieur
- ✅ **Git** 2.x
- ✅ **Docker** (optionnel, pour le déploiement)
- ✅ **Qdrant** (optionnel, pour la recherche vectorielle)
- ✅ **Redis** (optionnel, pour le caching)

### **Navigateurs Supportés**

- Chrome (recommandé)
- Firefox
- Safari
- Edge

---

## **🚀 INSTALLATION RAPIDE**

### **Option 1 : Installation Locale (Recommandé pour le développement)**

**Étape 1 : Cloner le dépôt**

```bash
cd /home/noor/PROJECTS/BTP/SMART_AO_V2/SMART_AO_LAST\ 4/SMART_AO_V7
git pull origin main
```

**Étape 2 : Créer un environnement virtuel**

```bash
python -m venv venv
```

**Étape 3 : Activer l'environnement**

```bash
# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**Étape 4 : Installer les dépendances**

```bash
pip install -r requirements.txt
```

**Étape 5 : Configurer l'environnement**

```bash
cp .env.example .env
# Éditez .env avec vos configurations
nano .env
```

**Étape 6 : Initialiser la base de données**

```bash
python scripts/init_db.py
```

**Étape 7 : Démarrer l'application**

```bash
uvicorn app.main:app --reload --port 8000
```

**Étape 8 : Accéder à l'application**

Ouvrez votre navigateur à l'adresse :
```
http://localhost:8000
```

### **Option 2 : Installation avec Docker (Recommandé pour la production)**

**Étape 1 : Construire l'image**

```bash
docker build -t smart-ao-v7 .
```

**Étape 2 : Démarrer les conteneurs**

```bash
docker-compose up -d
```

**Étape 3 : Vérifier les services**

```bash
docker-compose ps
```

**Étape 4 : Accéder à l'application**

```
http://localhost:8000
```

---

## **⚡ PREMIER DÉMARRAGE**

### **1. Vérifier l'installation**

Ouvrez un terminal et exécutez :

```bash
curl http://localhost:8000/api/v1/health
```

Vous devriez voir :

```json
{
  "status": "healthy",
  "version": "9.0.0"
}
```

✅ **Félicitations !** Votre installation est fonctionnelle.

### **2. Accéder à la documentation interactive**

Ouvrez votre navigateur à :
```
http://localhost:8000/docs
```

Vous verrez l'interface **Swagger UI** avec tous les endpoints disponibles.

### **3. Tester une première mission**

Vous pouvez tester avec un document d'exemple :

```bash
# Créer une mission de test
curl -X POST http://localhost:8000/api/v1/missions \
  -H "Content-Type: application/json" \
  -d '{
    "docs": ["example_dce.pdf"],
    "context": {
      "mission_type": "DCE_ANALYSIS",
      "project_name": "Test Projet"
    },
    "created_by": "test@example.com"
  }'
```

---

## **🎛️ INTERFACE DE COMMANDE**

### **Commandes Disponibles**

| **Commande** | **Description** |
|--------------|-----------------|
| `uvicorn app.main:app --reload` | Démarrer en mode développement |
| `uvicorn app.main:app --workers 4` | Démarrer en mode production |
| `python scripts/init_db.py` | Initialiser la base de données |
| `python scripts/check_go_nogo.sh` | Vérifier la structure du projet |
| `pytest tests/unit/` | Exécuter les tests unitaires |
| `pytest tests/integration/` | Exécuter les tests d'intégration |
| `bash scripts/validate_all_gates.sh` | Valider tous les Gates |

### **Gestion des Processus**

**Démarrer en arrière-plan :**
```bash
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &
```

**Voir les logs :**
```bash
tail -f app.log
```

**Arrêter le serveur :**
```bash
pkill -f "uvicorn app.main:app"
```

---

## **📊 UTILISATION VIA L'API**

### **Authentification**

**SMART_AO V7** utilise une authentification par **JWT (JSON Web Token)**.

**1. Obtenir un token** (si l'authentification est activée) :

```bash
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

**2. Utiliser le token** dans les requêtes :

```bash
curl http://localhost:8000/api/v1/missions \
  -H "Authorization: Bearer YOUR_TOKEN"
```

> **Note :** En mode développement, l'authentification peut être désactivée.

### **Endpoints Principaux**

| **Fonctionnalité** | **Endpoint** | **Méthode** | **Authentification** |
|-------------------|-------------|-------------|---------------------|
| Health Check | `/api/v1/health` | GET | ❌ Non requise |
| Lister les agents | `/api/v1/agents` | GET | ❌ Non requise |
| Créer une mission | `/api/v1/missions` | POST | ✅ Requis |
| Lister les missions | `/api/v1/missions` | GET | ✅ Requis |
| Upload un document | `/api/v1/documents/upload` | POST | ✅ Requis |
| Exécuter un workflow | `/api/v1/workflows/{id}/run` | POST | ✅ Requis |

### **Exemple Complet : Analyse d'un DCE**

**Étape 1 : Upload du document**

```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@mon_dce.pdf" \
  -F "metadata={\"project_id\": \"PROJ_001\"}"
```

**Étape 2 : Créer une mission**

```bash
curl -X POST http://localhost:8000/api/v1/missions \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "docs": ["DOC_001"],
    "context": {
      "mission_type": "DCE_ANALYSIS",
      "project_id": "PROJ_001",
      "priority": "HIGH"
    },
    "created_by": "user@example.com"
  }'
```

**Étape 3 : Vérifier le statut**

```bash
curl http://localhost:8000/api/v1/missions/MISION_001 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Étape 4 : Obtenir les résultats**

Une fois la mission terminée (`status: DONE`), vous pouvez récupérer les résultats :

```bash
curl http://localhost:8000/api/v1/missions/MISION_001 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## **💡 CAS D'USAGE COURANTS**

### **Cas 1 : Analyse Complète d'un DCE**

**Objectif :** Analyser un dossier de consultation complet

**Étapes :**
1. Upload du/des documents PDF
2. Créer une mission avec le contexte approprié
3. Laisser SMART_AO exécuter le workflow automatique
4. Récupérer les résultats

**Durée estimée :** 5-15 minutes selon la taille du DCE

### **Cas 2 : Analyse Ciblée avec un Agent Spécifique**

**Objectif :** Exécuter seulement l'analyse des délais

**Étapes :**
1. Upload du document
2. Créer une mission
3. Exécuter manuellement l'agent `DeadlineAgent`
4. Récupérer les résultats

**Commande :**
```bash
curl -X POST http://localhost:8000/api/v1/agents/DeadlineAgent/execute \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"mission_id": "MISSION_001", "input": {"document_id": "DOC_001"}}'
```

### **Cas 3 : Surveillance des Missions**

**Objectif :** Être notifié quand une mission est terminée

**Étapes :**
1. S'abonner aux événements de mission complétée
2. Configurer un webhook vers votre application

**Commande :**
```bash
curl -X POST http://localhost:8000/api/v1/events/subscribe \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "MISSION_COMPLETED",
    "callback_url": "https://votre-app.com/webhook/mission-complete"
  }'
```

### **Cas 4 : Analyse par Lots**

**Objectif :** Analyser plusieurs DCE en parallèle

**Étapes :**
1. Upload de tous les documents
2. Créer une mission par DCE
3. SMART_AO traitera les missions en parallèle (max 6 simultanément)

**Commande pour créer plusieurs missions :**
```bash
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/v1/missions \
    -H "Authorization: Bearer YOUR_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"docs\": [\"DOC_00$i\"], \"context\": {\"mission_type\": \"DCE_ANALYSIS\"}, \"created_by\": \"user@example.com\"}"
done
```

---

## **⚠️ RÉSOLUTION DES PROBLÈMES**

### **Problème 1 : Le serveur ne démarre pas**

**Symptômes :**
- Erreur de port déjà utilisé
- Erreur de module manquant

**Solutions :**

1. **Port déjà utilisé :**
   ```bash
   # Trouver le processus utilisant le port
   lsof -i :8000
   
   # Tuer le processus
   kill -9 <PID>
   ```

2. **Module manquant :**
   ```bash
   pip install -r requirements.txt
   ```

3. **Erreur de syntaxe :**
   ```bash
   python -m py_compile app/main.py
   ```

### **Problème 2 : Connexion à la base de données échoue**

**Symptômes :**
- `Connection refused`
- `Authentication failed`

**Solutions :**

1. **Vérifier que PostgreSQL est en cours d'exécution :**
   ```bash
   sudo systemctl status postgresql
   ```

2. **Vérifier les identifiants dans .env :**
   ```bash
   cat .env | grep DATABASE
   ```

3. **Tester la connexion manuellement :**
   ```bash
   psql -h localhost -U user -d smart_ao
   ```

### **Problème 3 : Les tests échouent**

**Symptômes :**
- Tests qui passaient avant échouent
- Erreurs de connexion à la base de données

**Solutions :**

1. **Réinstaller les dépendances :**
   ```bash
   pip install --force-reinstall -r requirements.txt
   ```

2. **Effacer le cache pytest :**
   ```bash
   rm -rf .pytest_cache
   ```

3. **Exécuter les tests avec plus de détails :**
   ```bash
   pytest tests/unit/ -v --tb=short
   ```

### **Problème 4 : Problème de mémoire**

**Symptômes :**
- `MemoryError`
- Serveur qui plante

**Solutions :**

1. **Réduire le nombre de workers :**
   ```bash
   uvicorn app.main:app --workers 2
   ```

2. **Augmenter la mémoire allouée** (si Docker) :
   ```bash
   docker run --memory=8g smart-ao-v7
   ```

3. **Vérifier la consommation mémoire :**
   ```bash
   top -o %MEM
   ```

### **Problème 5 : Lenteur des requêtes**

**Symptômes :**
- Temps de réponse élevé
- Timeout des requêtes

**Solutions :**

1. **Vérifier les logs :**
   ```bash
   tail -f app.log
   ```

2. **Activer le mode debug :**
   ```bash
   uvicorn app.main:app --reload --debug
   ```

3. **Vérifier la base de données :**
   ```bash
   # Connexion à PostgreSQL
   psql -U user -d smart_ao
   
   # Voir les requêtes lentes
   SELECT * FROM pg_stat_activity WHERE state = 'active';
   ```

---

## **📚 RESSOURCES SUPPLÉMENTAIRES**

### **Documentation Technique**

| **Document** | **Description** | **Lien** |
|--------------|-----------------|----------|
| **API Guide** | Documentation complète de l'API | [docs/API_GUIDE_V7.md](API_GUIDE_V7.md) |
| **Architecture** | Architecture technique détaillée | [docs/ARCHITECTURE_V7_ENGINE.md](ARCHITECTURE_V7_ENGINE.md) |
| **Engineering Handbook** | Guide de développement | [docs/ENGINEERING-HANDBOOK_V7.md](ENGINEERING-HANDBOOK_V7.md) |
| **Deployment Guide** | Guide de déploiement | [docs/DEPLOYMENT_GUIDE_V7.md](DEPLOYMENT_GUIDE_V7.md) |

### **Rapports et Plans**

| **Document** | **Description** | **Lien** |
|--------------|-----------------|----------|
| **Plan Maître** | Roadmap complète du projet | [PLAN_MAITRE_V7_FUSION_COMPLETE.md](../PLAN_MAITRE_V7_FUSION_COMPLETE.md) |
| **Plan Phase 5** | Plan de la phase actuelle | [PLAN_DE_CODAGE_PHASE_5_V7.md](../PLAN_DE_CODAGE_PHASE_5_V7.md) |
| **Rapport de Synthèse** | Synthèse Build 9 | [RAPPORT_SYNTHESE_BUILD_9_V7.md](../RAPPORT_SYNTHESE_BUILD_9_V7.md) |
| **Rapport de Validation** | Validation Phase 5 | [RAPPORT_VALIDATION_PHASE_5_V7.md](../RAPPORT_VALIDATION_PHASE_5_V7.md) |

### **Communauté et Support**

- **Email :** contact@smart-ao-v7.com
- **GitHub :** https://github.com/noor/SMART_AO_V7
- **Documentation Interactive :** http://localhost:8000/docs

### **Agents Disponibles**

Consultez la liste complète des 30+ agents dans [API_GUIDE_V7.md](API_GUIDE_V7.md#agents).

---

## **📌 CHECKLIST DE VÉRIFICATION**

Avant de commencer à utiliser SMART_AO V7, vérifiez que :

- [ ] Python 3.12+ est installé
- [ ] PostgreSQL 14+ est installé et en cours d'exécution
- [ ] Toutes les dépendances sont installées (`pip install -r requirements.txt`)
- [ ] Le fichier `.env` est correctement configuré
- [ ] La base de données a été initialisée (`python scripts/init_db.py`)
- [ ] Le serveur démarre sans erreur (`uvicorn app.main:app`)
- [ ] Le health check retourne `status: healthy`
- [ ] Vous pouvez accéder à http://localhost:8000/docs

---

## **🎯 PROCHAINES ÉTAPES**

Maintenant que SMART_AO V7 est installé et fonctionnel, vous pouvez :

1. **Tester avec vos propres documents** : Upload un DCE réel et lancez une analyse
2. **Configurer les webhooks** : Recevez des notifications en temps réel
3. **Intégrer avec vos outils** : Connectez SMART_AO à votre système existant
4. **Personnaliser les agents** : Créez vos propres agents pour des analyses spécifiques
5. **Déployer en production** : Mettez SMART_AO à disposition de votre équipe

---

**📚 Besoin d'aide ?**

Consultez la [documentation complète](API_GUIDE_V7.md) ou contactez notre équipe à contact@smart-ao-v7.com.

---

**✅ Approuvé par l'Architecte Chef : NOOR**
**📅 Date : 05/08/2026**
**🔒 Classification : CONFIDENTIEL - NIVEAU ARCHITECTE FONDATEUR**
