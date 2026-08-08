# **📚 GUIDE API - SMART_AO V7**
> **Documentation Technique de l'API REST - Build 9**

---

## **📋 TABLE DES MATIÈRES**

1. [🎯 Introduction](#-introduction)
2. [📡 Base URL](#-base-url)
3. [🔐 Authentification](#-authentification)
4. [📊 Endpoints](#-endpoints)
   - [Health](#health)
   - [Agents](#agents)
   - [Missions](#missions)
   - [Documents](#documents)
   - [Workflows](#workflows)
   - [Events](#events)
5. [📝 Schémas de Données](#-schémas-de-données)
6. [🔄 Codes de Statut](#-codes-de-statut)
7. [⚠️ Gestion des Erreurs](#-gestion-des-erreurs)
8. [📈 Exemples Complets](#-exemples-complets)
9. [🔒 Sécurité](#-sécurité)
10. [📊 Rate Limiting](#-rate-limiting)

---

## **🎯 INTRODUCTION**

L'API REST de SMART_AO V7 permet d'interagir avec le système d'analyse de DCE de manière programmatique. Elle suit les principes REST et utilise JSON pour les requêtes et réponses.

### **Fonctionnalités de l'API**

- ✅ **Gestion des Missions** : Créer, lire, mettre à jour, supprimer
- ✅ **Gestion des Agents** : Lister, filtrer, exécuter
- ✅ **Gestion des Documents** : Upload, download, métier
- ✅ **Gestion des Workflows** : Exécuter, surveiller
- ✅ **Événements en Temps Réel** : Webhooks et subscriptions
- ✅ **Sécurité** : Authentification JWT, Rate Limiting

### **Version de l'API**

```
Version : v1
Status : Production Ready
Last Updated : 05/08/2026
```

---

## **📡 BASE URL**

```
https://api.smart-ao-v7.com/v1
```

**Pour le développement local :**
```
http://localhost:8000/v1
```

---

## **🔐 AUTHENTIFICATION**

L'API utilise **JWT (JSON Web Token)** pour l'authentification.

### **Obtenir un Token**

```bash
POST /api/v1/auth/token
Content-Type: application/x-www-form-urlencoded

username=your_username&password=your_password
```

**Réponse :**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### **Utilisation du Token**

Ajoutez le token dans l'en-tête `Authorization` :

```bash
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### **Rafraîchir le Token**

```bash
POST /api/v1/auth/refresh
Authorization: Bearer REFRESH_TOKEN
```

---

## **📊 ENDPOINTS**

---

## **⚕️ Health**

### **Health Check**

Vérifie que le service est opérationnel.

**Requête :**
```bash
GET /api/v1/health
```

**Réponse (200 OK) :**
```json
{
  "status": "healthy",
  "timestamp": "2026-08-05T18:00:00Z",
  "version": "9.0.0",
  "services": {
    "database": "healthy",
    "event_bus": "healthy",
    "workflow_engine": "healthy",
    "agent_registry": "healthy"
  }
}
```

---

## **🤖 Agents**

### **Lister tous les agents**

**Requête :**
```bash
GET /api/v1/agents
```

**Query Parameters :**
- `capability` (optional) : Filtrer par capacité
- `status` (optional) : Filtrer par statut (active/inactive)
- `limit` (optional, default=50) : Nombre maximum de résultats
- `offset` (optional, default=0) : Offset pour la pagination

**Réponse (200 OK) :**
```json
{
  "total": 30,
  "limit": 50,
  "offset": 0,
  "agents": [
    {
      "name": "DeadlineAgent",
      "capabilities": ["deadline", "delai"],
      "description": "Analyse des délais et échéances",
      "version": "1.0.0",
      "status": "active",
      "is_blocking": true,
      "execution_time_ms": 150
    },
    {
      "name": "PenalitesAgent",
      "capabilities": ["penalites", "penalty"],
      "description": "Détection des pénalités de retard",
      "version": "1.0.0",
      "status": "active",
      "is_blocking": true,
      "execution_time_ms": 200
    }
  ]
}
```

### **Obtenir un agent spécifique**

**Requête :**
```bash
GET /api/v1/agents/{name}
```

**Réponse (200 OK) :**
```json
{
  "name": "DeadlineAgent",
  "capabilities": ["deadline", "delai"],
  "description": "Analyse des délais et échéances",
  "version": "1.0.0",
  "status": "active",
  "is_blocking": true,
  "execution_time_ms": 150,
  "configuration": {
    "timeout": 30,
    "max_retries": 3
  },
  "created_at": "2026-08-05T18:00:00Z",
  "updated_at": "2026-08-05T18:00:00Z"
}
```

### **Exécuter un agent**

**Requête :**
```bash
POST /api/v1/agents/{name}/execute
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "mission_id": "MISSION_001",
  "input": {
    "document_id": "DOC_001",
    "context": {
      "priority": "HIGH"
    }
  }
}
```

**Réponse (202 Accepted) :**
```json
{
  "execution_id": "EXEC_001",
  "agent_name": "DeadlineAgent",
  "mission_id": "MISSION_001",
  "status": "queued",
  "created_at": "2026-08-05T18:00:00Z"
}
```

---

## **🚀 Missions**

### **Lister toutes les missions**

**Requête :**
```bash
GET /api/v1/missions
Authorization: Bearer YOUR_TOKEN
```

**Query Parameters :**
- `status` (optional) : Filtrer par statut (CREATED, PARSING, EXTRACTING, etc.)
- `project_id` (optional) : Filtrer par projet
- `created_by` (optional) : Filtrer par créateur
- `limit` (optional, default=20) : Nombre maximum de résultats
- `offset` (optional, default=0) : Offset pour la pagination

**Réponse (200 OK) :**
```json
{
  "total": 10,
  "limit": 20,
  "offset": 0,
  "missions": [
    {
      "id": "MISSION_001",
      "mission_id": "MISSION_2026_001",
      "name": "Analyse DCE - Projet A",
      "description": "Analyse complète du DCE pour le projet A",
      "status": "DONE",
      "total_steps": 6,
      "completed_steps": 6,
      "progress": 100.0,
      "created_at": "2026-08-05T18:00:00Z",
      "updated_at": "2026-08-05T18:05:00Z",
      "completed_at": "2026-08-05T18:05:00Z",
      "created_by": "user@example.com",
      "project_id": "PROJ_001"
    }
  ]
}
```

### **Créer une mission**

**Requête :**
```bash
POST /api/v1/missions
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "docs": ["dce_2026_001.pdf", "dce_2026_002.pdf"],
  "context": {
    "mission_type": "DCE_ANALYSIS",
    "project_id": "PROJ_001",
    "priority": "HIGH",
    "client": "Client A",
    "project_name": "Construction Immeuble A"
  },
  "created_by": "user@example.com"
}
```

**Réponse (201 Created) :**
```json
{
  "id": 1,
  "mission_id": "MISSION_2026_003",
  "name": "Analyse DCE - Projet A",
  "description": null,
  "status": "CREATED",
  "total_steps": 6,
  "completed_steps": 0,
  "progress": 0.0,
  "created_at": "2026-08-05T18:00:00Z",
  "updated_at": "2026-08-05T18:00:00Z",
  "completed_at": null,
  "created_by": "user@example.com",
  "project_id": "PROJ_001",
  "error_message": null,
  "extra_metadata": {}
}
```

### **Obtenir une mission spécifique**

**Requête :**
```bash
GET /api/v1/missions/{id}
Authorization: Bearer YOUR_TOKEN
```

**Réponse (200 OK) :**
```json
{
  "id": 1,
  "mission_id": "MISSION_2026_003",
  "name": "Analyse DCE - Projet A",
  "description": "Analyse complète du DCE",
  "status": "AGENT_RUNNING",
  "total_steps": 6,
  "completed_steps": 4,
  "progress": 66.67,
  "created_at": "2026-08-05T18:00:00Z",
  "updated_at": "2026-08-05T18:04:00Z",
  "completed_at": null,
  "created_by": "user@example.com",
  "project_id": "PROJ_001",
  "workflow": [
    {
      "step_name": "parser_step",
      "step_order": 0,
      "status": "DONE",
      "started_at": "2026-08-05T18:00:01Z",
      "completed_at": "2026-08-05T18:01:00Z",
      "duration_ms": 59000,
      "agent_name": null
    },
    {
      "step_name": "extraction_step",
      "step_order": 1,
      "status": "DONE",
      "started_at": "2026-08-05T18:01:01Z",
      "completed_at": "2026-08-05T18:02:00Z",
      "duration_ms": 59000,
      "agent_name": null
    },
    {
      "step_name": "classification_step",
      "step_order": 2,
      "status": "DONE",
      "started_at": "2026-08-05T18:02:01Z",
      "completed_at": "2026-08-05T18:03:00Z",
      "duration_ms": 59000,
      "agent_name": null
    },
    {
      "step_name": "agents_step",
      "step_order": 3,
      "status": "RUNNING",
      "started_at": "2026-08-05T18:03:01Z",
      "completed_at": null,
      "duration_ms": null,
      "agent_name": "DeadlineAgent"
    }
  ],
  "events": [],
  "error_message": null,
  "extra_metadata": {}
}
```

### **Mettre à jour une mission**

**Requête :**
```bash
PATCH /api/v1/missions/{id}
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "status": "PAUSED",
  "priority": "CRITICAL",
  "extra_metadata": {
    "manual_review": true,
    "reviewer": "senior_engineer"
  }
}
```

**Réponse (200 OK) :**
```json
{
  "id": 1,
  "mission_id": "MISSION_2026_003",
  "status": "PAUSED",
  "priority": "CRITICAL",
  "extra_metadata": {
    "manual_review": true,
    "reviewer": "senior_engineer"
  },
  "updated_at": "2026-08-05T18:05:00Z"
}
```

### **Supprimer une mission**

**Requête :**
```bash
DELETE /api/v1/missions/{id}
Authorization: Bearer YOUR_TOKEN
```

**Réponse (204 No Content)**

---

## **📄 Documents**

### **Lister tous les documents**

**Requête :**
```bash
GET /api/v1/documents
Authorization: Bearer YOUR_TOKEN
```

**Query Parameters :**
- `mission_id` (optional) : Filtrer par mission
- `status` (optional) : Filtrer par statut
- `limit` (optional, default=50) : Nombre maximum de résultats
- `offset` (optional, default=0) : Offset pour la pagination

**Réponse (200 OK) :**
```json
{
  "total": 50,
  "limit": 50,
  "offset": 0,
  "documents": [
    {
      "id": 1,
      "document_id": "DOC_2026_001",
      "file_name": "dce_projet_a.pdf",
      "file_path": "/storage/dce_projet_a.pdf",
      "file_type": "application/pdf",
      "file_size": 2097152,
      "content_hash": "a1b2c3d4e5f6...",
      "status": "processed",
      "pages": 45,
      "metadata": {
        "author": "Client A",
        "title": "DCE - Construction Immeuble A",
        "subject": "Appel d'offres"
      },
      "mission_id": "MISSION_2026_001",
      "created_at": "2026-08-05T18:00:00Z",
      "processed_at": "2026-08-05T18:01:00Z"
    }
  ]
}
```

### **Upload un document**

**Requête :**
```bash
POST /api/v1/documents/upload
Authorization: Bearer YOUR_TOKEN
Content-Type: multipart/form-data

-- Boundary
Content-Disposition: form-data; name="file"; filename="dce.pdf"
Content-Type: application/pdf

<contenu du fichier>
-- Boundary
Content-Disposition: form-data; name="metadata"

{"mission_id": "MISSION_001", "project_id": "PROJ_001"}
-- Boundary--
```

**Réponse (201 Created) :**
```json
{
  "id": 1,
  "document_id": "DOC_2026_002",
  "file_name": "dce.pdf",
  "file_path": "/storage/DOC_2026_002.pdf",
  "file_type": "application/pdf",
  "file_size": 1048576,
  "content_hash": "f1e2d3c4b5a6...",
  "status": "uploaded",
  "mission_id": "MISSION_001",
  "created_at": "2026-08-05T18:00:00Z"
}
```

### **Obtenir un document spécifique**

**Requête :**
```bash
GET /api/v1/documents/{id}
Authorization: Bearer YOUR_TOKEN
```

**Réponse (200 OK) :**
```json
{
  "id": 1,
  "document_id": "DOC_2026_002",
  "file_name": "dce.pdf",
  "file_path": "/storage/DOC_2026_002.pdf",
  "file_type": "application/pdf",
  "file_size": 1048576,
  "content_hash": "f1e2d3c4b5a6...",
  "status": "processed",
  "pages": 45,
  "metadata": {
    "author": "Client A",
    "title": "DCE - Projet",
    "subject": "Appel d'offres"
  },
  "mission_id": "MISSION_001",
  "created_at": "2026-08-05T18:00:00Z",
  "processed_at": "2026-08-05T18:01:00Z"
}
```

### **Download un document**

**Requête :**
```bash
GET /api/v1/documents/{id}/download
Authorization: Bearer YOUR_TOKEN
```

**Réponse (200 OK) :**
- Fichier binaire avec headers :
  - `Content-Disposition: attachment; filename="dce.pdf"`
  - `Content-Type: application/pdf`

---

## **🔄 Workflows**

### **Lister tous les workflows**

**Requête :**
```bash
GET /api/v1/workflows
Authorization: Bearer YOUR_TOKEN
```

**Réponse (200 OK) :**
```json
{
  "total": 5,
  "workflows": [
    {
      "id": 1,
      "name": "DCE Analysis v7",
      "description": "Workflow standard d'analyse DCE",
      "steps": 6,
      "status": "active",
      "created_at": "2026-08-05T18:00:00Z"
    }
  ]
}
```

### **Exécuter un workflow**

**Requête :**
```bash
POST /api/v1/workflows/{id}/run
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "mission_id": "MISSION_001",
  "docs": ["DOC_001", "DOC_002"],
  "context": {
    "priority": "HIGH"
  }
}
```

**Réponse (202 Accepted) :**
```json
{
  "workflow_id": 1,
  "mission_id": "MISSION_001",
  "execution_id": "EXEC_001",
  "status": "queued",
  "created_at": "2026-08-05T18:00:00Z"
}
```

### **Obtenir le statut d'un workflow**

**Requête :**
```bash
GET /api/v1/workflows/{execution_id}/status
Authorization: Bearer YOUR_TOKEN
```

**Réponse (200 OK) :**
```json
{
  "execution_id": "EXEC_001",
  "workflow_id": 1,
  "mission_id": "MISSION_001",
  "status": "running",
  "current_step": 3,
  "total_steps": 6,
  "progress": 50.0,
  "started_at": "2026-08-05T18:00:00Z",
  "steps": [
    {"name": "parser_step", "status": "DONE", "duration_ms": 5000},
    {"name": "extraction_step", "status": "DONE", "duration_ms": 8000},
    {"name": "classification_step", "status": "DONE", "duration_ms": 3000},
    {"name": "agents_step", "status": "RUNNING", "duration_ms": null},
    {"name": "compilation_step", "status": "PENDING", "duration_ms": null},
    {"name": "rapport_step", "status": "PENDING", "duration_ms": null}
  ]
}
```

---

## **📡 Events**

### **Lister les événements**

**Requête :**
```bash
GET /api/v1/events
Authorization: Bearer YOUR_TOKEN
```

**Query Parameters :**
- `mission_id` (optional) : Filtrer par mission
- `event_type` (optional) : Filtrer par type d'événement
- `limit` (optional, default=100) : Nombre maximum de résultats

**Réponse (200 OK) :**
```json
{
  "total": 50,
  "limit": 100,
  "events": [
    {
      "id": 1,
      "event_type": "MISSION_CREATED",
      "event_data": {
        "mission_id": "MISSION_001",
        "project_id": "PROJ_001"
      },
      "source": "workflow_engine",
      "mission_id": "MISSION_001",
      "step_id": null,
      "created_at": "2026-08-05T18:00:00Z"
    }
  ]
}
```

### **S'abonner aux événements (Webhook)**

**Requête :**
```bash
POST /api/v1/events/subscribe
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "event_type": "MISSION_COMPLETED",
  "callback_url": "https://your-app.com/webhook/mission-completed",
  "secret": "your_webhook_secret"
}
```

**Réponse (201 Created) :**
```json
{
  "subscription_id": "SUB_001",
  "event_type": "MISSION_COMPLETED",
  "callback_url": "https://your-app.com/webhook/mission-completed",
  "status": "active",
  "created_at": "2026-08-05T18:00:00Z"
}
```

### **Se désabonner**

**Requête :**
```bash
DELETE /api/v1/events/subscribe/{subscription_id}
Authorization: Bearer YOUR_TOKEN
```

---

## **📝 SCHÉMAS DE DONNÉES**

### **Mission**

```json
{
  "id": "integer",
  "mission_id": "string (64 chars max)",
  "name": "string (255 chars max)",
  "description": "string (text)",
  "status": "enum: CREATED, PARSING, EXTRACTING, CLASSIFYING, AGENT_RUNNING, COMPILING, REPORTING, DONE, FAILED",
  "created_at": "datetime",
  "updated_at": "datetime",
  "completed_at": "datetime (nullable)",
  "total_steps": "integer",
  "completed_steps": "integer",
  "progress": "float (calculated)",
  "error_message": "string (text, nullable)",
  "extra_metadata": "object",
  "project_id": "string (nullable)",
  "created_by": "string"
}
```

### **Agent**

```json
{
  "name": "string",
  "capabilities": "array[string]",
  "description": "string",
  "version": "string",
  "status": "enum: active, inactive, maintenance",
  "is_blocking": "boolean",
  "execution_time_ms": "float",
  "configuration": "object",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### **Document**

```json
{
  "id": "integer",
  "document_id": "string (64 chars max)",
  "file_name": "string (512 chars max)",
  "file_path": "string (1024 chars max)",
  "file_type": "string (128 chars max)",
  "file_size": "integer",
  "content_hash": "string (64 chars)",
  "status": "enum: uploaded, processing, processed, failed",
  "pages": "integer",
  "metadata": "object",
  "mission_id": "string (nullable)",
  "created_at": "datetime",
  "processed_at": "datetime (nullable)"
}
```

### **Event**

```json
{
  "id": "integer",
  "event_type": "enum: MISSION_CREATED, MISSION_STARTED, MISSION_COMPLETED, MISSION_FAILED, STEP_STARTED, STEP_COMPLETED, STEP_FAILED, DOCUMENT_UPLOADED, DOCUMENT_PROCESSED, AGENT_REGISTERED, AGENT_EXECUTED, SYSTEM_ERROR",
  "event_data": "object",
  "source": "string (128 chars max)",
  "mission_id": "integer (nullable)",
  "step_id": "integer (nullable)",
  "created_at": "datetime"
}
```

---

## **🔄 CODES DE STATUT**

| **Code** | **Description** | **Signification** |
|----------|-----------------|-------------------|
| 200 | OK | Requête réussie |
| 201 | Created | Ressource créée |
| 202 | Accepted | Requête acceptée (traitement asynchrone) |
| 204 | No Content | Requête réussie, pas de contenu à retourner |
| 400 | Bad Request | Requête mal formée |
| 401 | Unauthorized | Authentification requise |
| 403 | Forbidden | Accès refusé |
| 404 | Not Found | Ressource non trouvée |
| 405 | Method Not Allowed | Méthode HTTP non autorisée |
| 422 | Unprocessable Entity | Données de requête invalides |
| 429 | Too Many Requests | Rate limit dépassé |
| 500 | Internal Server Error | Erreur serveur |
| 503 | Service Unavailable | Service temporairement indisponible |

---

## **⚠️ GESTION DES ERREURS**

### **Format des Erreurs**

Toutes les erreurs suivent ce format :

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": "object (optional)",
    "timestamp": "datetime"
  }
}
```

### **Exemples d'Erreurs**

**400 Bad Request :**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Les données de requête sont invalides",
    "details": {
      "field": "docs",
      "error": "Must be a list of strings"
    },
    "timestamp": "2026-08-05T18:00:00Z"
  }
}
```

**401 Unauthorized :**
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Token d'authentification manquant ou invalide",
    "timestamp": "2026-08-05T18:00:00Z"
  }
}
```

**404 Not Found :**
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Mission avec ID MISSION_001 non trouvée",
    "timestamp": "2026-08-05T18:00:00Z"
  }
}
```

**429 Too Many Requests :**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit dépassé. Veuillez réessayer dans 60 secondes.",
    "details": {
      "limit": 100,
      "remaining": 0,
      "reset_in": 60
    },
    "timestamp": "2026-08-05T18:00:00Z"
  }
}
```

**500 Internal Server Error :**
```json
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "Une erreur interne est survenue",
    "details": {
      "request_id": "REQ_123456"
    },
    "timestamp": "2026-08-05T18:00:00Z"
  }
}
```

---

## **📈 EXEMPLES COMPLETS**

### **Exemple 1 : Analyse Complète d'un DCE**

```bash
# 1. Upload du document
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@dce_projet_a.pdf" \
  -F "metadata={\"mission_type\": \"DCE_ANALYSIS\", \"project_id\": \"PROJ_001\"}"

# 2. Créer une mission
curl -X POST http://localhost:8000/api/v1/missions \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"docs": ["DOC_001"], "context": {"priority": "HIGH"}, "created_by": "user@example.com"}'

# 3. Vérifier le statut
curl http://localhost:8000/api/v1/missions/MISION_001 \
  -H "Authorization: Bearer YOUR_TOKEN"

# 4. Obtenir les résultats
curl http://localhost:8000/api/v1/missions/MISION_001 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### **Exemple 2 : Exécution d'un Agent Spécifique**

```bash
# Exécuter DeadlineAgent sur une mission
curl -X POST http://localhost:8000/api/v1/agents/DeadlineAgent/execute \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"mission_id": "MISSION_001", "input": {"document_id": "DOC_001"}}'

# Vérifier le résultat
curl http://localhost:8000/api/v1/missions/MISION_001 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### **Exemple 3 : Webhook pour les Événements**

```bash
# S'abonner aux événements de mission complétée
curl -X POST http://localhost:8000/api/v1/events/subscribe \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"event_type": "MISSION_COMPLETED", "callback_url": "https://your-app.com/webhook"}'

# Votre application recevra des POST vers https://your-app.com/webhook
# avec le payload:
{
  "event_type": "MISSION_COMPLETED",
  "event_data": {
    "mission_id": "MISSION_001",
    "total_steps": 6,
    "completed_steps": 6,
    "status": "DONE"
  },
  "timestamp": "2026-08-05T18:05:00Z"
}
```

---

## **🔒 SÉCURITÉ**

### **Authentification JWT**

- **Algorithme :** HS256
- **Expiration :** 30 minutes (configurable)
- **Rafraîchissement :** Tokens de rafraîchissement disponibles
- **Stockage :** Side serveur uniquement

### **Bonnes Pratiques**

1. **Ne jamais stocker le secret en clair**
2. **Utiliser HTTPS en production**
3. **Rotater les secrets régulièrement**
4. **Limiter les permissions des tokens**
5. **Valider les tokens côté serveur**

### **Configuration de la Sécurité**

```ini
# Dans .env
SECRET_KEY=your_very_strong_secret_key_at_least_32_chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

---

## **📊 RATE LIMITING**

### **Limites par Défaut**

| **Niveau** | **Limite** | **Fenêtre** |
|-----------|------------|-------------|
| PUBLIC | 60 | par minute |
| AUTHENTICATED | 1000 | par minute |
| CRITICAL | 10000 | par minute |
| SENSITIVE | 10 | par minute |
| DEVELOPMENT | Illimité | - |

### **En-têtes de Rate Limiting**

Toutes les réponses incluent :

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 60
```

### **Gestion des Erreurs 429**

Voir [Gestion des Erreurs](#-gestion-des-erreurs) pour le format détaillé.

---

## **📌 NOTES FINALES**

- **Version de l'API :** v1
- **Compatibilité :** Python 3.12+
- **Framework :** FastAPI
- **Documentation Interactive :** `/docs` (Swagger), `/redoc` (ReDoc)
- **Support :** contact@smart-ao-v7.com

**© 2026 SMART_AO V7 - Tous droits réservés**

**Version :** 1.0.0 - Build 9
**Date :** 05/08/2026
**Statut :** Production Ready ✅
