# SMART AO — RAPPORT D'AUTOMATISATION INFRASTRUCTURE
## Stratégie Single-Tenant Pur Scalable — L'Usine à VPS Souverains

> **CONFIDENTIEL — USAGE INTERNE — NE PAS DIFFUSER**
> **Août 2026 — Document de référence pour l'hébergement et l'exploitation SMART AO**

---

## 1. Résumé Exécutif

SMART AO repose sur une doctrine fondatrice non négociable : **1 VPS = 1 client = 1 Postgres = 1 Qdrant = 1 MinIO = 1 Redis. 0 colonne tenant_id.**

Ce choix est un bouclier juridique, commercial et technique. Il garantit la confidentialité absolue des prix et des marges, la conformité RGPD par suppression physique, et un argument de vente souverain opposable face aux SaaS américains.

L'erreur serait de sacrifier cette isolation pour passer en multi-tenant logique avec un Control Plane central. Cette approche introduit un point de défaillance unique, une surface d'attaque critique et une dette de code complexe.

La solution est l'automatisation radicale du single-tenant. Nous ne construisons pas un Control Plane qui route, nous construisons une usine qui clone du VPS parfait.

**Objectif :** Isolation physique du single-tenant + maintenabilité du multi-tenant.

- 1 fichier Terraform = 1 client souverain provisionné en 3 minutes
- 1 image Docker unique = 500 comportements identiques
- 1 playbook Ansible = 500 VPS mis à jour en 75 minutes par batch de 10
- 1 dashboard Grafana = 500 VPS sous contrôle
- 1 système de backup = restauration en 10 minutes

---

## 2. Doctrine — Pourquoi le Single-Tenant Pur est Non Négociable

| Contrainte | Impact Multi-Tenant Logique | Impact Single-Tenant Physique |
|---|---|---|
| **Confidentialité prix** | Une fuite SQL expose les marges de tous les clients (ex: 380k€ vs 520k€ sur un PAB). Un SELECT oublié = procès. | Isolation physique Postgres/Qdrant. Fuite inter-client impossible. |
| **RGPD Art. 17 Droit à l'effacement** | Purge sélective complexe, risque de résidus dans les embeddings Qdrant, preuve difficile. | `terraform destroy` = suppression complète du VPS. Preuve opposable avec logs. |
| **DPA Art. 28** | Un seul sous-traitant pour 500 clients, audit global complexe, responsabilité totale. | 1 DPA par client, 1 VPS = 1 responsable de traitement. Souveraineté maintenue. |
| **Vault A01-A12 (Bilans, Qualibat)** | Fuite = concurrence déloyale, délit d'initié. | Filesystem isolé, LVM chiffré, AES-256-GCM. |
| **Argument commercial** | "Vos données sur notre plateforme sécurisée" = argument faible juridiquement. | "Vos données sur VOTRE VPS dédié OVH France, opéré en infogérance DPA" = vérité opposable. |
| **Performance / Noisy Neighbor** | Un client analysant un DCE de 400 pages (Docling 6Go RAM) met en OOM le Qdrant de tous les autres. | Blast radius = 1. Un OOM sur le client #247 n'affecte que le client #247. |

**Règle d'or en CI :** Aucune colonne `tenant_id`, `client_id` ou `vps_id` dans le code métier. Linter bloquant qui fait échouer le build si détecté.

**Anti-pattern interdit :** Architecture Control Plane + Execution Nodes. Elle apporte un SPOF (Control Plane down = 500 clients down), une surface d'attaque massive (1 compromission = 500 clients exposés) et une fracture produit (2 bases de code à maintenir).

---

## 3. Architecture Cible — L'Usine à VPS

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLEET ORCHESTRATOR                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  Terraform  │─▶│   Ansible   │─▶│  Prometheus + Grafana   │  │
│  │  Provision  │  │   Deploy    │  │    Fleet Health         │  │
│  │  3 min/VPS  │  │  Batch 10   │  │  1 Dashboard 500 VPS    │  │
│  └──────┬──────┘  └──────┬──────┘  └───────────┬─────────────┘  │
│         │                │                      │                │
│         ▼                ▼                      ▼                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         DOCKER REGISTRY — OVH Harbor Privé              │  │
│  │    smartao:v3.2.1 — Image unique signée cosign          │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
    ┌─────────┐         ┌─────────┐         ┌─────────┐
    │ VPS #001│         │ VPS #247│         │ VPS #500│
    │ OVH GRA │         │ OVH GRA │         │ OVH GRA │
    │ vRack   │         │ vRack   │         │ vRack   │
    ├─────────┤         ├─────────┤         ├─────────┤
    │ Docker  │         │ Docker  │         │ Docker  │
    │ FastAPI │         │ FastAPI │         │ FastAPI │
    │ Docling │         │ Docling │         │ Docling │  Worker isolé
    │ Postgres│         │ Postgres│         │ Postgres│
    │ Qdrant  │         │ Qdrant  │         │ Qdrant  │  ◀─ OOM isolé
    │ MinIO   │         │ MinIO   │         │ MinIO   │
    │ Redis   │         │ Redis   │         │ Redis   │
    │ Restic  │─▶ S3    │ Restic  │─▶ S3    │ Restic  │─▶ S3 Backup
    │ NodeExp │─▶ Prom  │ NodeExp │─▶ Prom  │ NodeExp │─▶ Prometheus
    └─────────┘         └─────────┘         └─────────┘
```

**Principes :**
1.  **Identité :** Tous les VPS exécutent exactement la même image Docker `smartao:v3.2.1`
2.  **Isolation :** Aucune donnée métier ne traverse le réseau entre VPS. Seules les métriques transitent via VPN WireGuard privé.
3.  **Autonomie :** Chaque VPS peut démarrer et fonctionner sans dépendance centrale.
4.  **Immutabilité :** Aucune modification manuelle en SSH. Toute modification passe par Terraform ou Ansible.

---

## 4. Pilier 1 : Terraform Module `smartao_instance` — Le Provisionnement

**Objectif : 1 fichier `.tf` = 1 client souverain provisionné en 3 minutes, durci et reproductible.**

### 4.1 Structure

```
/infra/terraform/
  modules/smartao_instance/
    main.tf
    variables.tf
    outputs.tf
    templates/
      cloud-init.yml.tftpl
      docker-compose.yml.tftpl
      nginx.conf.tftpl
  live/
    backend.tf (S3 OVH tfstate verrouillé)
    client_001_acme_btp.tf
    client_247_dupont.tf
```

### 4.2 Contrat du Module

```hcl
variable "client_id"    { type = string } # ex: dupont-batiment-59
variable "client_name"  { type = string } # DUPONT BATIMENT SARL
variable "client_siret" { type = string } # 14 chiffres pour DPA

variable "region"       { default = "GRA11" } # Gravelines, France - Souveraineté EU
variable "flavor"       { default = "b3-16-45" } # 4 vCPU 16Go minimum / b3-32-90 = 8 vCPU 32Go recommandé
variable "root_disk"    { default = 100 } # Go NVMe système
variable "data_disk"    { default = 200 } # Go NVMe données (MinIO/Postgres/Qdrant)

variable "image_version"{ default = "v3.2.1" }
variable "domain"       { type = string } # dupont.smartao.fr
variable "v_rack"       { default = true } # Isolation réseau OVH vRack
variable "ssh_key_name" { default = "fleet_admin_ed25519" }
```

### 4.3 Cloud-Init Bootstrap Complet — 12 Étapes

Ce fichier est exécuté au premier boot du VPS. Il transforme une Ubuntu 22.04 vierge en VPS SMART AO durci.

```yaml
#cloud-config
# SMART AO — Cloud-Init Bootstrap — 12 runcmd

package_update: true
package_upgrade: true
packages:
  - docker-ce
  - docker-compose-plugin
  - docker-ce-rootless-extras
  - fail2ban
  - ufw
  - restic
  - prometheus-node-exporter
  - nginx
  - certbot
  - python3-certbot-dns-ovh
  - wireguard
  - auditd
  - jq
  - mc

users:
  - name: smartao_admin
    groups: [docker, sudo]
    shell: /bin/bash
    ssh-authorized-keys: [${SSH_PUB_KEY_FLEET}]

write_files:
  - path: /opt/smartao/.env
    permissions: '0600'
    content: |
      CLIENT_ID=${CLIENT_ID}
      SMARTAO_VERSION=${IMAGE_VERSION}
      POSTGRES_PASSWORD=${PG_PASS}
      REDIS_PASSWORD=${REDIS_PASS}
      MINIO_ROOT_PASSWORD=${MINIO_PASS}
      QDRANT_API_KEY=${QDRANT_KEY}
      JWT_SECRET=${JWT_SECRET}
      BACKUP_REPO=s3:https://s3.gra.io.cloud.ovh.net/smartao-backups/${CLIENT_ID}
      BACKUP_PASSWORD=${BACKUP_PASSWORD}
      WG_PRIVATE_KEY=${WG_PRIVATE_KEY}
  - path: /etc/wireguard/wg0.conf
    permissions: '0600'
    content: |
      [Interface]
      PrivateKey = ${WG_PRIVATE_KEY}
      Address = 10.0.1.${WG_OCTET}/24
      [Peer]
      PublicKey = ${MONITORING_WG_PUB}
      AllowedIPs = 10.0.0.0/8
      Endpoint = monitoring.smartao.fr:51820
      PersistentKeepalive = 25

runcmd:
  # 1. LVM Chiffré pour /data
  - pvcreate /dev/sdb && vgcreate vg_data /dev/sdb && lvcreate -l 100%FREE -n lv_data vg_data && mkfs.ext4 /dev/vg_data/lv_data && mkdir -p /data && mount /dev/vg_data/lv_data /data && echo "/dev/vg_data/lv_data /data ext4 defaults 0 2" >> /etc/fstab
  # 2. Firewall UFW strict - SSH uniquement vRack
  - ufw default deny incoming && ufw default allow outgoing && ufw allow from 10.0.0.0/8 to any port 22 && ufw allow 80/tcp && ufw allow 443/tcp && ufw allow from ${PROMETHEUS_IP} to any port 9100 && ufw --force enable
  # 3. Fail2ban
  - systemctl enable fail2ban && systemctl start fail2ban
  # 4. WireGuard VPN vers monitoring
  - systemctl enable wg-quick@wg0 && systemctl start wg-quick@wg0
  # 5. Docker Rootless + Login Registry privé
  - loginctl enable-linger smartao_admin && docker login harbor.gra11.ovh.smartao.fr -u fleet -p ${REGISTRY_TOKEN}
  # 6. Pull image signée
  - cd /opt/smartao && docker pull harbor.gra11.ovh.smartao.fr/smartao/smartao:${IMAGE_VERSION}
  # 7. Lancement stack
  - cd /opt/smartao && IMAGE_VERSION=${IMAGE_VERSION} docker compose up -d
  # 8. Restic init bucket dédié
  - export RESTIC_REPOSITORY="s3:https://s3.gra.io.cloud.ovh.net/smartao-backups/${CLIENT_ID}" && export RESTIC_PASSWORD="${BACKUP_PASSWORD}" && restic init || true
  # 9. Node Exporter métriques
  - systemctl enable prometheus-node-exporter && systemctl start prometheus-node-exporter
  # 10. SSL Certbot DNS-01 OVH
  - certbot certonly --dns-ovh --dns-ovh-credentials /etc/ovh.ini -d ${CLIENT_ID}.smartao.fr --non-interactive --agree-tos -m infra@smartao.fr
  # 11. Nginx TLS 1.3 HSTS rate limiting
  - cp /opt/smartao/nginx/nginx.conf /etc/nginx/sites-enabled/smartao && nginx -t && systemctl reload nginx
  # 12. Auditd + Hardening kernel
  - systemctl enable auditd && systemctl start auditd && sysctl -w kernel.randomize_va_space=2

final_message: "SMART AO VPS ${CLIENT_ID} ready in 180s - Version ${IMAGE_VERSION}"
```

**Résultat :** `terraform apply -target=module.client_247` = 3 minutes, VPS identique, logué dans tfstate S3, IP privée vRack 10.x.x.x + IP publique Nginx uniquement.

### 4.4 Coût Infrastructure par Client

| Profil | VPS OVH | Stockage | Backup S3 | Total/mois | % CA (base 2490€) |
|---|---|---|---|---|---|
| Minimum (4 vCPU, 16Go) | 15€ | 5€ | 3€ | 23€ | 0.9% |
| Recommandé (8 vCPU, 32Go) Docling | 35€ | 8€ | 5€ | 48€ | 1.9% |
| Premium (16 vCPU, 64Go + LLM local) | 70€ | 15€ | 10€ | 95€ | 3.8% |

---

## 5. Pilier 2 : Ansible Playbook `deploy-fleet.yml` — Le Déploiement

**Objectif : Mettre à jour 500 VPS en parallèle par batch de 10, en zero-downtime avec rollback automatique.**

### 5.1 Inventaire Dynamique

Généré automatiquement depuis le tfstate Terraform :

```ini
[smartao_fleet]
client_001 ansible_host=10.0.1.1 version=v3.2.0
client_247 ansible_host=10.0.1.47 version=v3.2.0
[smartao_fleet:vars]
ansible_user=smartao_admin
ansible_ssh_common_args='-J bastion@10.0.0.1' # Bastion vRack
```

### 5.2 Playbook Blue-Green avec Rescue et Handlers

```yaml
---
- name: Déploiement Fleet SMART AO Blue-Green
  hosts: smartao_fleet
  serial: 10 # Rolling 10 par 10
  strategy: free
  become: yes

  vars:
    target_version: "v3.2.1"
    registry: "harbor.gra11.ovh.smartao.fr/smartao"
    backup_before_deploy: true
    slack_webhook: "https://hooks.slack.com/services/.../fleet"

  pre_tasks:
    - name: Vérifier version actuelle
      shell: docker inspect smartao-app --format='{{.Config.Image}}' || echo "none"
      register: current_version
    - name: Skip si déjà à jour
      meta: end_host
      when: target_version in current_version.stdout
    - name: Backup pré-déploiement
      shell: docker exec smartao-postgres pg_dump -U smartao -Fc smartao_db | restic backup --stdin --stdin-filename db_{{ ansible_date_time.iso8601 }}.dump
      when: backup_before_deploy

  tasks:
    - block:
        - name: Pull image {{ target_version }}
          docker_image: {name: "{{ registry }}/smartao:{{ target_version }}", source: pull}

        - name: Lancer conteneur green sur 8001
          docker_container:
            name: smartao-app-green
            image: "{{ registry }}/smartao:{{ target_version }}"
            env_file: /opt/smartao/.env
            networks: [{name: smartao_network}]
            ports: ["127.0.0.1:8001:8000"]
            state: started
            healthcheck: {test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"], interval: 10s, retries: 6}

        - name: Health check green
          uri: {url: "http://localhost:8001/api/health", status_code: 200}
          register: health_green
          until: health_green.status == 200
          retries: 30
          delay: 10

        - name: Switch Nginx vers green
          template: {src: nginx-upstream-green.j2, dest: /etc/nginx/conf.d/smartao-upstream.conf}
          notify: reload nginx

        - name: Drain connexions blue 30s
          pause: {seconds: 30}

        - name: Stop blue et rename green->blue
          shell: docker stop smartao-app || true && docker rename smartao-app-green smartao-app

        - name: Nettoyer images >72h
          shell: docker image prune -f --filter "until=72h"

      rescue:
        - name: Rollback
          shell: docker stop smartao-app-green || true; docker start smartao-app || true
        - name: Alerte Slack Rollback
          uri: {url: "{{ slack_webhook }}", method: POST, body: '{"text":"ROLLBACK {{ inventory_hostname }} {{ target_version }}"}', body_format: json}
        - fail: {msg: "Deploy failed {{ inventory_hostname }}"}

      always:
        - name: Notif Slack Success
          uri: {url: "{{ slack_webhook }}", method: POST, body: '{"text":"✅ {{ inventory_hostname }} updated {{ target_version }}"}', body_format: json}
          when: health_green.status == 200

  handlers:
    - name: reload nginx
      service: {name: nginx, state: reloaded}
```

**Commandes opérationnelles :**
```bash
ansible-playbook deploy-fleet.yml -i inventory/fleet.ini # 500 VPS ~25 min
ansible-playbook deploy-fleet.yml -i inventory/fleet.ini --limit client_247 # hotfix 1 client
ansible-playbook deploy-fleet.yml -i inventory/fleet.ini --limit batch_1 # test A/B 10 clients
```

**CI/CD :** Build image -> Trivy scan -> cosign sign -> Push Harbor -> Deploy staging batch 1 -> Smoke tests -> Deploy prod fleet.

---

## 6. Pilier 3 : Prometheus + Grafana Fleet — L'Observabilité

**Objectif : 1 dashboard pour 500 VPS. Pas 500 dashboards.**

### 6.1 Architecture

- Agent par VPS : `node_exporter :9100`, `cAdvisor :8080`, `postgres_exporter`, `qdrant_exporter`, `blackbox_exporter` pour `/api/health`
- Central : VPS `monitoring.smartao.fr` avec Prometheus + Thanos (rétention 1 an) + Grafana + Alertmanager
- Liaison via WireGuard vRack chiffré, métriques uniquement, jamais données métier

### 6.2 Dashboard Unique "Fleet Health"

**Panel 1 — Vue Globale :**
Total VPS 500, En ligne 498, Version v3.2.1 : 480 (20 en v3.2.0 pending), Alertes actives 3

**Panel 2 — Carte Thermique :**
Axe X = Heures, Axe Y = Client ID, Couleur = CPU%. Rouge = Qdrant surcharge (Docling worker probable)

**Panel 3 — Tableau Détaillé Drill-down :**
| Client | VPS | Version | CPU | RAM | Disk | Qdrant | Backup | SSL |
|---|---|---|---|---|---|---|---|---|
| ACME BTP | #001 | v3.2.1 | 45% | 12/16G | 45% | OK | OK | OK |
| BTP Dupont | #247 | v3.2.1 | 92% | 15.8/16G | 78% | **OOM** | OK | OK |

Cliquer sur #247 ouvre le dashboard détaillé client avec logs Loki.

### 6.3 Règles d'Alerte Critiques

```yaml
groups:
  - name: smartao_fleet
    rules:
      - alert: QdrantOOM
        expr: (container_memory_usage_bytes{name="smartao-qdrant"} / container_spec_memory_limit_bytes{name="smartao-qdrant"}) > 0.95
        for: 2m
        labels: {severity: critical}
        annotations: {summary: "Qdrant OOM client {{ $labels.client_id }}", runbook_url: "https://wiki.smartao/runbooks/qdrant-oom"}

      - alert: BackupAbsent24h
        expr: time() - restic_last_backup_timestamp > 86400
        for: 5m
        labels: {severity: warning}
        annotations: {summary: "Backup absent >24h client {{ $labels.client_id }}"}

      - alert: VersionDrift
        expr: count by (version) (smartao_build_info) > 1
        for: 10m
        labels: {severity: warning}
        annotations: {summary: "Version drift {{ $value }} versions actives"}
```

Alertmanager -> Slack #fleet-alerts + PagerDuty + auto-remediation Ansible.

---

## 7. Pilier 4 : Restic Backup Orchestrator — La Sauvegarde

**Objectif : Backup chiffré, testé, alerté. Restauration en 10 minutes.**

### 7.1 Architecture

Chaque VPS -> Restic Agent (cron 4h) -> S3 OVH (1 bucket par client) -> Chiffrement AES-256-GCM -> Déduplication

Données jamais hors VPS client sauf chiffrées sur S3 OVH France région GRA.

### 7.2 Script Complet 8 Étapes

```bash
#!/bin/bash
# /etc/smartao/backup.sh — 8 Steps
set -euo pipefail
source /opt/smartao/.env
export RESTIC_REPOSITORY="s3:https://s3.gra.io.cloud.ovh.net/smartao-backups/${CLIENT_ID}"
export RESTIC_PASSWORD="${BACKUP_PASSWORD}"
TMP=/tmp/backup-$(date +%s)
mkdir -p $TMP

echo "[1/8] Backup Postgres"
docker exec smartao-postgres pg_dump -U smartao -Fc smartao_db | restic backup --stdin --stdin-filename postgres/smartao_db.dump --tag postgres

echo "[2/8] Backup Qdrant snapshot API"
curl -s -X POST "http://localhost:6333/collections/dce/snapshots" -H "api-key: ${QDRANT_API_KEY}" -d '{}'
curl -s -X POST "http://localhost:6333/collections/vault/snapshots" -H "api-key: ${QDRANT_API_KEY}" -d '{}'
sleep 3
docker cp smartao-qdrant:/qdrant/snapshots $TMP/qdrant_snapshots
restic backup $TMP/qdrant_snapshots --tag qdrant

echo "[3/8] Backup MinIO"
mc alias set local http://localhost:9000 ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD} --api S3v4
mc mirror --overwrite --remove local/smartao-documents $TMP/minio_docs
restic backup $TMP/minio_docs --tag minio

echo "[4/8] Backup Redis RDB"
docker exec smartao-redis redis-cli -a ${REDIS_PASSWORD} BGSAVE
sleep 5
docker cp smartao-redis:/data/dump.rdb $TMP/redis_dump.rdb
restic backup $TMP/redis_dump.rdb --tag redis

echo "[5/8] Backup Vault A01-A12"
restic backup /opt/smartao/vault/ --tag vault --exclude '*.tmp'

echo "[6/8] Forget/prune rétention 30j/4sem/12mois"
restic forget --keep-daily 30 --keep-weekly 4 --keep-monthly 12 --prune --tag daily || true

echo "[7/8] Integrity check 10% le dimanche"
if [ $(date +%u) -eq 7 ]; then restic check --read-data-subset=10%; fi

echo "[8/8] Push métrique Prometheus"
SIZE=$(restic stats --json | jq -r '.total_size // 0')
echo "restic_last_backup_timestamp{client_id=\"${CLIENT_ID}\"} $(date +%s)" | curl --data-binary @- http://localhost:9091/metrics/job/restic/client/${CLIENT_ID}

rm -rf $TMP
```

Cron : `0 */4 * * * root /etc/smartao/backup.sh` → 6 backups/jour, rétention 30j glissants + 4 semaines + 12 mois.

Restore complet : `ansible-playbook restore-client.yml --limit client_247 --extra-vars "snapshot_id=abc123"` → <10 min.

---

## 8. Pilier 5 : Image Docker Unique — `smartao:v3.2.1`

**Objectif : Une seule image validée pour les 500 VPS. Même code, même comportement. Pas de fork.**

### 8.1 Dockerfile Multi-Stage Sécurisé

```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.12-slim
RUN groupadd -r smartao && useradd -r -g smartao smartao
RUN apt-get update && apt-get install -y libpq-dev tesseract-ocr tesseract-ocr-fra poppler-utils curl && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=builder /root/.local /home/smartao/.local
COPY . /app
RUN chown -R smartao:smartao /app && chmod -R 750 /app
ENV PATH=/home/smartao/.local/bin:$PATH
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
USER smartao
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 CMD curl -f http://localhost:8000/api/health || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**Règles :** Aucun VPS ne pull `latest`. Tous pull une version taggée explicitement `v3.2.1`. Tag injecté par Ansible. Image signée cosign + SBOM + scan Trivy bloquant si HIGH/CRITICAL.

### 8.2 Docker Compose Stack Complète — 8 Services

```yaml
version: '3.8'
services:
  app:
    image: harbor.gra11.ovh.smartao.fr/smartao/smartao:${SMARTAO_VERSION:-v3.2.1}
    container_name: smartao-app
    restart: unless-stopped
    env_file: .env
    ports: ["127.0.0.1:8000:8000"]
    volumes: [./vault:/app/vault:ro, ./data:/app/data, ./logs:/app/logs]
    depends_on:
      postgres: {condition: service_healthy}
      qdrant: {condition: service_healthy}
      redis: {condition: service_healthy}
      minio: {condition: service_healthy}
    networks: [smartao_network]
    security_opt: [no-new-privileges:true]
    read_only: true
    tmpfs: [/tmp]
    user: "1000:1000"
    deploy: {resources: {limits: {memory: 4G}}}
    healthcheck: {test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"], interval: 30s, timeout: 10s, retries: 3}

  docling-worker:
    image: harbor.gra11.ovh.smartao.fr/smartao/smartao:${SMARTAO_VERSION}
    container_name: smartao-docling
    command: ["python", "-m", "app.workers.docling_worker"]
    env_file: .env
    volumes: [./vault:/app/vault:ro, ./data:/app/data]
    networks: [smartao_network]
    deploy: {resources: {limits: {memory: 6G}, reservations: {memory: 4G}}}

  postgres:
    image: postgres:16-alpine
    container_name: smartao-postgres
    volumes: [postgres_data:/var/lib/postgresql/data]
    networks: [smartao_network]
    healthcheck: {test: ["CMD-SHELL", "pg_isready -U smartao"], interval: 10s, retries: 5}

  qdrant:
    image: qdrant/qdrant:v1.11.0
    container_name: smartao-qdrant
    volumes: [qdrant_data:/qdrant/storage]
    networks: [smartao_network]
    deploy: {resources: {limits: {memory: 6G}}}
    healthcheck: {test: ["CMD", "curl", "-f", "http://localhost:6333/healthz"], interval: 15s}

  redis:
    image: redis:7-alpine
    container_name: smartao-redis
    command: redis-server --requirepass ${REDIS_PASSWORD} --appendonly yes
    volumes: [redis_data:/data]
    networks: [smartao_network]

  minio:
    image: minio/minio:latest
    container_name: smartao-minio
    command: server /data --console-address ":9001"
    env_file: .env
    volumes: [minio_data:/data]
    networks: [smartao_network]

  nginx:
    image: nginx:alpine
    container_name: smartao-nginx
    ports: ["80:80", "443:443"]
    volumes: [./nginx/nginx.conf:/etc/nginx/nginx.conf:ro, ./nginx/ssl:/etc/nginx/ssl:ro]
    depends_on: [app]
    networks: [smartao_network]

  node-exporter:
    image: prom/node-exporter:latest
    container_name: smartao-node-exporter
    volumes: [/proc:/host/proc:ro, /sys:/host/sys:ro, /:/rootfs:ro]
    command: ['--path.procfs=/host/proc', '--path.rootfs=/rootfs', '--path.sysfs=/host/sys']
    networks: [smartao_network]

  pushgateway:
    image: prom/pushgateway:latest
    container_name: smartao-pushgateway
    ports: ["127.0.0.1:9091:9091"]
    networks: [smartao_network]

volumes: {postgres_data:, qdrant_data:, redis_data:, minio_data:}
networks: {smartao_network: {driver: bridge, ipam: {config: [{subnet: 172.20.0.0/16}]}}}
```

Si le client #247 a un bug, reproduction locale immédiate avec `docker run harbor...:v3.2.1` bit-for-bit identique.

---

## 9. Sécurité Fleet — Renforcement Multi-Couches

| Couche | Mesure | Vérification |
|---|---|---|
| OS | Ubuntu 22.04 LTS minimal sans GUI | `lsb_release -a` |
| Kernel | ASLR, NX, AppArmor activés | `sysctl kernel.randomize_va_space` |
| Réseau | vRack privé 10.0.0.0/8, Bastion unique point d'entrée SSH | `ufw status verbose` |
| SSH | Port 22 vRack uniquement, clé ed25519, 2FA TOTP bastion | `sshd -T \| grep ListenAddress` |
| Docker | Rootless mode, seccomp, no-new-privileges, non-root user | `docker info \| grep Security` |
| Secrets | Vault HashiCorp central mTLS, injection runtime, jamais dans image | `grep -r PASSWORD Dockerfile` = 0 |
| Logs | Auditd + rsyslog forward centralisé | `ausearch -ts recent` |
| Backup | Chiffrement AES-256-GCM Restic, 1 clé par client | `restic cat config` |
| Supply Chain | Image signée cosign, scan Trivy, SBOM attesté | `cosign verify` |

**Schéma accès SSH :** Internet -> Bastion OVH FR (IP fixe, 2FA, sessions enregistrées) -> vRack privé 10.0.0.0/8 -> VPS Fleet (SSH désactivé sur IP publique).

---

## 10. Scalabilité — Projections 1 → 5000 Clients

| Phase | Clients | Infra | Temps MàJ Fleet | Coût Infra/mois | CA Cumulé (2490€) | Marge |
|---|---|---|---|---|---|---|
| Lancement | 1-5 | 5 VPS manuels | 5 min | 115-240€ | 12 450€ | 98% |
| Bootstrap | 5-30 | Fleet auto | 10 min | 720-1440€ | 74 700€ | 98% |
| Croissance | 30-150 | Fleet + batch + CI/CD | 25 min | 3 600-7 200€ | 373 500€ | 98% |
| Scale | 150-500 | Thanos + Cortex + auto-scaling | 25 min | 12 000-24 000€ | 1 245 000€ | 98% |
| Enterprise | 500-5000 | Multi-région optionnel | 45 min | 120 000€ | 12 450 000€ | 99% |

**Point de rupture Kubernetes :** Jamais avant 500 clients. Kubernetes ajoute une complexité inutile pour des VPS identiques. À évaluer seulement si >20% des clients sont hors EU, alors multi-région OVH GRA+SBG+BHS.

Coût humain : 0.2 ETP DevOps avec l'usine vs 3 ETP support sans automatisation.

---

## 11. Comparaison — Single-Tenant Fleet vs Multi-Tenant Logique

| Critère | Single-Tenant Fleet (Cible) | Multi-Tenant Logique |
|---|---|---|
| Isolation données | Physique (VPS+PG+Qdrant) | Logique (tenant_id + RLS) |
| Fuite possible | Nécessite compromission VPS individuel | SQLi sur Control Plane = tous les clients |
| RGPD effacement | `terraform destroy` 1 commande | Purge sélective, risque résidus embeddings |
| Rollback | Restore Restic 1 client isolé | Rollback base partagée = tous impactés |
| Debug incident | 1 VPS isolé, logs locaux | Corrélation multi-tenant bruitée |
| Coût dev | Code simple, 0 tenant_id | Code complexe routing/sharding |
| Argument vente | "VOTRE serveur dédié" | "Notre plateforme sécurisée" |
| Scalabilité | 5000 VPS Terraform 3 min chacun | 5000 tenants avec sharding |

---

## 12. Plan de Mise en Œuvre — 12 Semaines

**Phase 1 — Fondations (Semaines 1-4) :**
- Terraform module `smartao_instance` + backend S3 + vRack + cloud-init 12 steps
- Docker image v3.2.1 multi-stage + cosign + Harbor privé
- Ansible deploy-fleet.yml blue-green batch 10 + inventory.py + bastion
- Tests : provision 5 VPS pilotes, déploiement, rollback

**Phase 2 — Observabilité (Semaines 5-7) :**
- Prometheus central WireGuard + scraping 500 targets + Thanos
- Grafana Fleet Health heatmap + drill-down Loki
- Alertes Qdrant OOM, BackupAbsent, VersionDrift + runbooks auto-remediation

**Phase 3 — Backup & DR (Semaines 8-9) :**
- Restic orchestrator cron 4h + rétention 30j/4sem/12mois + 1 bucket/client
- Restore test mensuel + integrity check 10%

**Phase 4 — Hardening & Doc (Semaines 10-11) :**
- Bastion + vRack + Vault HashiCorp mTLS + CIS Benchmark Ansible role
- Documentation RUNBOOKS + procédures incident response

**Phase 5 — Production (Semaine 12) :**
- Migration 5 premiers clients staging→prod via terraform import
- Monitoring 24/7 + Go/No-Go Fleet 38 critères validés

---

## 13. Go/No-Go Fleet — 38 Critères

24 critères single VPS + 31 critères fleet + 7 nouveaux automatisation :

32. `terraform plan` clean sur tout le fleet (0 drift)
33. Image Docker signée cosign vérifiée avant pull sur 100% VPS
34. `restic_last_backup_timestamp <24h` sur 100% fleet
35. Fleet Health dashboard green (0 case rouge >5m)
36. Rollback Ansible blue-green testé avec succès sur 1 client pilote
37. `inventory.py` == `tfstate` (0 VPS orphelin)
38. Monitoring VPN WireGuard up + Prometheus scrape 100% targets

Script : `check_go_nogo_fleet.sh` doit être vert avant client #51.

---

## 14. Conclusion — Thèse Finale

Le single-tenant pur n'est pas un obstacle technique. C'est une arme stratégique.

La vraie simplicité ne vient pas de la mutualisation, mais de l'automatisation radicale d'une simplicité physique.

Avec Terraform + Ansible + Prometheus + Restic + Docker, vous obtenez :
- L'isolation physique du single-tenant (confidentialité, RGPD, argument de vente)
- La maintenabilité du multi-tenant (1 image, 1 playbook, 1 dashboard)
- La scalabilité du cloud (5000 VPS en 3 minutes chacun)
- Le coût négligeable (1.9% du CA en profil recommandé)

**Ne construisez pas un Control Plane. Construisez une usine à VPS.**

1 client = 1 `terraform apply` = 1 VPS isolé = 1 souveraineté garantie = 1 facture justifiée.

C'est ça, le vrai niveau supérieur.

---
*Document de référence — SMART AO Infrastructure Automation — Août 2026*
*Source unique pour MANIFESTE, PLAN_CODAGE, ENGINEERING-HANDBOOK*
