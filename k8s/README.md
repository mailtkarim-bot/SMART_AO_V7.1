# **🐳 K8s Configurations - SMART_AO V7**
> **Configurations Kubernetes pour le déploiement production - Build 9**

---

## **📋 TABLE DES MATIÈRES**

1. [🎯 Introduction](#-introduction)
2. [📦 Pré-requis](#-pré-requis)
3. [🚀 Déploiement Rapide](#-déploiement-rapide)
4. [📁 Structure des Fichiers](#-structure-des-fichiers)
5. [⚙️ Configuration Détaillée](#-configuration-détaillée)
6. [🔧 Commandes Utiles](#-commandes-utiles)
7. [⚠️ Résolution des Problèmes](#-résolution-des-problèmes)

---

## **🎯 INTRODUCTION**

Ce dossier contient les configurations Kubernetes pour déployer SMART_AO V7 en production. Les fichiers sont optimisés pour un cluster avec :

- **PostgreSQL** : Base de données principale
- **Qdrant** : Moteur de recherche vectorielle
- **Redis** : Cache et sessions
- **SMART_AO App** : Application principale

---

## **📦 PRÉ-REQUIS**

### **Cluster Kubernetes**

- Kubernetes 1.25+
- kubectl 1.25+
- Helm 3.0+
- 16 Go RAM minimum
- 4 vCPU minimum

### **Outils Locaux**

- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [Helm](https://helm.sh/docs/intro/install/)
- [k9s](https://k9scli.io/) (optionnel, pour une interface visuelle)

---

## **🚀 DÉPLOIEMENT RAPIDE**

### **Étape 1 : Préparer le namespace**

```bash
kubectl create namespace smart-ao-v7
kubectl config set-context --current --namespace=smart-ao-v7
```

### **Étape 2 : Déployer PostgreSQL**

```bash
kubectl apply -f postgres/
```

### **Étape 3 : Déployer Qdrant**

```bash
kubectl apply -f qdrant/
```

### **Étape 4 : Déployer Redis**

```bash
kubectl apply -f redis/
```

### **Étape 5 : Déployer l'Application**

```bash
# Créer le secret avec vos configurations
kubectl create secret generic smart-ao-secrets --from-env-file=.env.k8s

# Déployer l'application
kubectl apply -f app/
```

### **Étape 6 : Vérifier le déploiement**

```bash
# Voir les pods
kubectl get pods -n smart-ao-v7

# Voir les services
kubectl get svc -n smart-ao-v7

# Voir les ingress
kubectl get ingress -n smart-ao-v7
```

### **Étape 7 : Accéder à l'application**

```bash
# Obtenir l'URL de l'ingress
kubectl get ingress smart-ao-ingress -n smart-ao-v7

# Ou utiliser le port-forward pour tester localement
kubectl port-forward svc/smart-ao-service 8000:8000 -n smart-ao-v7
```

---

## **📁 STRUCTURE DES FICHIERS**

```
k8s/
├── README.md                    # Ce fichier
├── namespace.yaml               # Définition du namespace
│
├── postgres/
│   ├── deployment.yaml          # Déploiement PostgreSQL
│   ├── service.yaml            # Service PostgreSQL
│   ├── pvc.yaml                # Persistent Volume Claim
│   └── configmap.yaml          # Configuration PostgreSQL
│
├── qdrant/
│   ├── deployment.yaml          # Déploiement Qdrant
│   ├── service.yaml            # Service Qdrant
│   ├── pvc.yaml                # Persistent Volume Claim
│   └── configmap.yaml          # Configuration Qdrant
│
├── redis/
│   ├── deployment.yaml          # Déploiement Redis
│   ├── service.yaml            # Service Redis
│   └── configmap.yaml          # Configuration Redis
│
├── app/
│   ├── deployment.yaml          # Déploiement Application
│   ├── service.yaml            # Service Application
│   ├── ingress.yaml            # Ingress Application
│   ├── hpa.yaml                # Horizontal Pod Autoscaler
│   ├── configmap.yaml          # Configuration Application
│   └── secrets.example.yaml    # Exemple de secrets
│
└── monitoring/
    ├── service-monitor.yaml    # Service Monitor pour Prometheus
    └── prometheus-rule.yaml     # Règles Prometheus
```

---

## **⚙️ CONFIGURATION DÉTAILLÉE**

### **Namespace**

Crée un namespace dédié pour isoler les ressources :

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: smart-ao-v7
  labels:
    app: smart-ao
    version: v7
    build: 9
```

### **PostgreSQL**

Configuration optimisée pour SMART_AO :
- **Mémoire :** 4 Go
- **CPU :** 1 vCPU
- **Stockage :** 50 Go SSD
- **Backup :** Automatique toutes les 24h

### **Qdrant**

Configuration pour la recherche vectorielle :
- **Mémoire :** 8 Go
- **CPU :** 2 vCPU
- **Stockage :** 100 Go SSD
- **Snapshot :** Toutes les 5 minutes

### **Redis**

Configuration pour le caching :
- **Mémoire :** 2 Go
- **CPU :** 0.5 vCPU
- **Persistance :** RDB toutes les 6 heures

### **Application**

Configuration pour l'application :
- **Réplicas :** 2-4 (autoscaling)
- **Mémoire :** 4 Go par pod
- **CPU :** 1 vCPU par pod
- **Liveness Probe :** Toutes les 30 secondes
- **Readiness Probe :** Toutes les 10 secondes

---

## **🔧 COMMANDES UTILES**

### **Vérification du statut**

```bash
# Voir tous les pods
kubectl get pods -n smart-ao-v7

# Voir les ressources
kubectl get all -n smart-ao-v7

# Voir les logs d'un pod
kubectl logs -f <pod-name> -n smart-ao-v7

# Exécuter une commande dans un pod
kubectl exec -it <pod-name> -n smart-ao-v7 -- bash
```

### **Mise à jour**

```bash
# Mettre à jour l'application (rolling update)
kubectl rollout restart deployment/smart-ao-app -n smart-ao-v7

# Voir le statut du rollout
kubectl rollout status deployment/smart-ao-app -n smart-ao-v7

# Retour à la version précédente
kubectl rollout undo deployment/smart-ao-app -n smart-ao-v7
```

### **Scaling**

```bash
# Mettre à l'échelle manuellement
kubectl scale deployment/smart-ao-app --replicas=3 -n smart-ao-v7

# Désactiver l'autoscaling
kubectl delete hpa smart-ao-hpa -n smart-ao-v7
```

### **Backup et Restauration**

```bash
# Backup PostgreSQL
kubectl exec <postgres-pod> -n smart-ao-v7 -- pg_dump -U smart_ao smart_ao_v7 > backup.sql

# Restauration PostgreSQL
cat backup.sql | kubectl exec -i <postgres-pod> -n smart-ao-v7 -- psql -U smart_ao smart_ao_v7
```

### **Nettoyage**

```bash
# Supprimer tous les ressources
kubectl delete namespace smart-ao-v7

# Supprimer les volumes persistants
kubectl delete pvc -l app=smart-ao -n smart-ao-v7
```

---

## **⚠️ RÉSOLUTION DES PROBLÈMES**

### **Problème 1 : Pod en CrashLoopBackOff**

**Cause :** Erreur de configuration ou dépendance manquante

**Solution :**
```bash
# Voir les logs
kubectl logs <pod-name> -n smart-ao-v7 --previous

# Décrire le pod pour plus de détails
kubectl describe pod <pod-name> -n smart-ao-v7

# Exécuter le pod en mode debug
kubectl run debug-pod --image=python:3.12-slim --restart=Never --rm -it -- bash
```

### **Problème 2 : Connexion à PostgreSQL échoue**

**Cause :** Problème de réseau ou identifiants incorrects

**Solution :**
```bash
# Tester la connexion depuis l'application
kubectl exec -it <app-pod> -n smart-ao-v7 -- bash
# Dans le pod :
apt-get update && apt-get install -y postgresql-client
psql -h smart-ao-postgres -U smart_ao -d smart_ao_v7
```

### **Problème 3 : Problème de mémoire**

**Cause :** Limite de mémoire insuffisante

**Solution :**
```bash
# Vérifier la consommation mémoire
kubectl top pods -n smart-ao-v7

# Augmenter la limite de mémoire
kubectl edit deployment/smart-ao-app -n smart-ao-v7
# Modifier resources.limits.memory
```

### **Problème 4 : Ingress ne fonctionne pas**

**Cause :** Problème de configuration Ingress Controller

**Solution :**
```bash
# Vérifier l'Ingress Controller
kubectl get pods -n ingress-nginx

# Vérifier la configuration de l'ingress
kubectl describe ingress smart-ao-ingress -n smart-ao-v7

# Vérifier les services
kubectl get svc -n smart-ao-v7
```

---

## **📌 NOTES DE PRODUCTION**

### **Bonnes Pratiques**

1. **Utilisez des namespaces** pour isoler les environnements
2. **Configurez les Resource Requests/Limits** pour éviter les abus
3. **Activez les Liveness et Readiness Probes** pour la résilience
4. **Utilisez des Persistent Volumes** pour la persistance des données
5. **Configurez les backups** automatiques pour PostgreSQL et Qdrant
6. **Activez le monitoring** avec Prometheus et Grafana
7. **Configurez les logs** centralisés avec ELK ou Loki

### **Sécurité**

1. **Ne stockez pas de secrets en clair** dans les fichiers YAML
2. **Utilisez des Secrets Kubernetes** pour les informations sensibles
3. **Configurez le Network Policy** pour limiter l'accès
4. **Activez le RBAC** pour le contrôle d'accès
5. **Utilisez des Pod Security Policies** pour limiter les privilèges

### **Performance**

1. **Augmentez les ressources** selon la charge
2. **Configurez l'autoscaling** pour gérer les pics de charge
3. **Optimisez les requêtes** PostgreSQL
4. **Utilisez Redis** pour le caching
5. **Configurez Qdrant** avec suffisamment de mémoire

---

## **🎯 VALIDATION GATE 9**

Pour valider Gate 9 (Déploiement Staging), exécutez :

```bash
# Vérifier que tous les pods sont en cours d'exécution
kubectl get pods -n smart-ao-v7

# Vérifier que tous les pods sont Ready
kubectl get pods -n smart-ao-v7 -o jsonpath='{.items[*].status.conditions[?(@.type=="Ready")].status}'

# Vérifier le health check de l'API
kubectl get pods -n smart-ao-v7 -l app=smart-ao-app -o jsonpath='{.items[*].metadata.name}' | \
  xargs -I {} kubectl exec {} -n smart-ao-v7 -- curl -s http://localhost:8000/api/v1/health | grep healthy
```

---

**© 2026 SMART_AO V7 - Tous droits réservés**

**Version :** 1.0.0 - Build 9
**Date :** 05/08/2026
**Statut :** Production Ready ✅
