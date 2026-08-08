> **V7.1 ENGINE OS - Note d'architecture :** L'architecture de SMART AO a été repensée en système d'exploitation ; les 33 modules décrits ici sont désormais des agents autonomes conformes au contrat BaseAgent, orchestrés par un Workflow Engine (Mission 6 steps) via un Event Bus et découverts par un Agent Registry par capacités. Leur comportement fonctionnel reste identique. Voir ARCHITECTURE_V7_ENGINE.md pour la couche OS. Ce RAPPORT reste SSoT fonctionnel §2.1, §3.1-3.2, §7.1-7.34.
>
> V7.1 intègre l'ADN V3.2 : Application Desktop Native (Tauri), Mode Panique, Onboarding 5 étapes, CLI unifiée. V7.1 ajoute 6 modules métier (7.29-7.34) couvrant : Pénurie & Pénibilité RH, Vigilance URSSAF, ZAN & Trackterres, Syntax Checker, Sourcing API, Mode Panique Emergency Bypass. Corrections P0 : mathbox -> math_engine, Fleet Management, Local LLM Fallback, Dead Letter Queue EventBus, pgvector->Qdrant.

# SMART_AO - RAPPORT STRATÉGIQUE INTÉGRAL V7.1 ENGINE OS

> **Confidentiel - Usage Interne - Ne Pas Diffuser**
> **Source unique fonctionnelle des 33 modules - 39 single / 46 fleet - Édition Fusion V7.1 - 33 boucliers - 16 solveurs Garage**
> **Version V12 -> V7.1 Fusion : 17->39 critères single V6/V7.1, 24->46 fleet V6/V7.1, 12->28 modules V6, 28->33 modules V7.1 (+5 nouveaux: 7.29-7.33), 5->16 solveurs Garage V7.1, corrections P0 CCAG/PAB/Matériaux/Avance + mathbox->math_engine**

> **SSoT : Ce document est la source unique fonctionnelle. Les autres documents (MANIFESTE, PLAN_MAITRE_V7.1, ENGINEERING-HANDBOOK) RÉFÈRENT ce document par "Voir RAPPORT §7.X" pour les spécifications modules, §3.1 pour RBAC, §12 pour Go/No-Go.**


## 1. Compromis Fondateurs Non Négociables (Single-Tenant Pur + Souveraineté)

| Décision Architecturale | Valeur | Justification |
|---|---|---|
| Architecture | **Single-tenant pur** — 1 VPS = 1 client = 1 Postgres = 1 Qdrant = 1 MinIO = 1 Redis. 0 colonne tenant_id / client_id / vps_id en code métier. Isolation physique par serveur dédié. | Un client analysant DCE 400 pages ne ralentit pas les autres. Fail Qdrant n'affecte qu'un client. Effacement RGPD = suppression VPS. |
| Code multi-tenant | **Interdit** — 0 if tenant_id en code. Scan linter bloquant. | Simplifie sécurité, audit, conformité. |
| VPS minimum / recommandé | **16 Go RAM / 4 vCPU minimum** (refus install dessous). **32 Go RAM / 8 vCPU recommandé** (Docling lourd + Mistral 7B local opt). Profil 4/8 Go supprimé. | BGE-M3 + Qdrant hybrid on_disk + parsing 400p demandent RAM. |
| Souveraineté | **OVH FR EU**. Données ne sortent jamais du VPS. LLM défaut **API Mistral EU**. DeepSeek/hors UE = opt-in explicite + disclaimer RGPD + case cochée Admin. Mistral 7B local = option 32Go+ pas path critique. | Argument central vs SaaS US. Conforme AI Act + DPA art28. |
| Parsing | **PyMuPDF + pdfplumber d'abord** (rapide <2s/page). **Docling = worker séparé async**, pas dans process API. BGE-M3 multilingue 1024dim. | Docling lourd 6Go RAM — isolation worker évite OOM API. |
| RAG | **Hybrid Dense + Sparse + RRF + Fallback FTS Postgres** (btp_french custom dict). Pas "7 couches" marketing. Collections: dce, vault, chantiers, traps sans préfixe tenant. | Hybrid = recall exact mots + sémantique. RRF. Fallback FTS si Qdrant down. |
| Calculs €|**Garage Mathématique ZERO LLM** — app/engines/math_engine/ sans import openai/anthropic/langchain/mistralai. PuLP (simplexe) + OR-Tools (scheduling) + Decimal 28 to_decimal(str) obligatoire. LLM ne calcule jamais €.|Règle d'or: LLM structure, solveur chiffre, humain valide. Hallucination € = faillite.|
| Offres commerciales | **A Souverain / B Infogéré assumé DPA art.28**. Formule correcte: "Vos données sur votre VPS dédié EU, opéré en infogérance avec DPA. Souveraineté physique maintenue." Slogan "je n'héberge rien" INTERDIT — mensongère. | Modèle B assume infogérance avec DPA, pas mensonge souveraineté. |
| Chiffres marketing | "40h→2h", "÷10 temps", "30% SIRET" = objectifs d'usage / formulation qualitative, pas faits prouvés. Disclaimer obligatoire. | Évite allégation trompeuse. |
| Go/No-Go sécurité|**39 critères single VPS** (31 V6/V7.1 +8 V7.1) avant premier client payant.  **46 critères Fleet**  (38 V6/V7.1 +8 V7.1 Fleet). Gate bloquant check_go_nogo.sh vert.|Voir §12.|

---

#### Archive V12 §1 préservée (Ne pas supprimer - enrichissement V6)
> Évolution : V12 annonçait 17 critères single / 24 fleet. V6 Fusion passe à 24 single / 31 fleet (+7 critères V6). V7.1 passe à 39 single / 46 fleet (+8 critères V7.1). Voir RAPPORT §12 pour liste complète.

## 1. Compromis Fondateurs Non Négociables (Single-Tenant Pur + Souveraineté)

| Décision Architecturale | Valeur |Justification |
|---|---|---|
| Architecture | **Single-tenant pur** - 1 VPS = 1 client = 1 Postgres = 1 Qdrant = 1 MinIO = 1 Redis. 0 colonne tenant_id / client_id / vps_id en code métier. Isolation physique par serveur dédié. | Un client analysant DCE 400 pages ne ralentit pas les autres. Fail Qdrant n'affecte qu'un client. Effacement RGPD = suppression VPS. |
| Code multi-tenant | **Interdit** - 0 if tenant_id en code. Scan linter bloquant. | Simplifie sécurité, audit, conformité. |
| VPS minimum / recommandé | **16 Go RAM / 4 vCPU minimum** (refus install dessous). **32 Go RAM / 8 vCPU recommandé ** (Docling lourd + Mistral 7B local opt). Profil 4/8 Go supprimé. | BGE-M3 + Qdrant hybrid on_disk + parsing 400p demandent RAM. |
| Souveraineté | **OVH FR EU**. Données ne sortent jamais du VPS. LLM défaut **API Mistral EU**. DeepSeek/hors UE = opt-in explicite + disclaimer RGPD + case cochée Admin. Mistral 7B local = option 32Go+ pas path critique. | Argument central vs SaaS US. Conforme AI Act + DPA art28. |
| Parsing | **PyMuPDF + pdfplumber d'abord** (rapide <2s/page). **Docling = worker séparé async**, pas dans process API. BGE-M3 multilingue 1024dim. | Docling lourd 6Go RAM - isolation worker évite OOM API. |
| RAG | **Hybrid Dense + Sparse + RRF + Fallback FTS Postgres** (btp_french custom dict). Pas "7 couches" marketing. Collections: dce, vault, chantiers, traps sans préfixe tenant. | Hybrid = recall exact mots + sémantique. RRF . Fallback FTS si Qdrant down. |
| Calculs € | **Garage Mathématique ZERO LLM** - app/mathbox/ [V12 préservé — V7.1: app/engines/math_engine/] sans import openai/anthropic/langchain/mistralai. PuLP (simplexe) + OR-Tools (scheduling) + Decimal 28 to_decimal(str) obligatoire. LLM ne calcule jamais €. | Règle d'or: LLM structure, solveur chiffre, humain valide. Hallucination € = faillite. |
| Offres commerciales | **A Souverain / B Infogéré assumé DPA art.28**. Formule correcte: "Vos données sur votre VPS dédié EU, opéré en infogérance avec DPA. Souveraineté physique maintenue." Slogan "je n'héberge rien" INTERDIT - mensongère. | Modèle B assume infogérance avec DPA, pas mensonge souveraineté. |
| Chiffres marketing | "40h→2h", "÷10 temps", "30% SIRET" = objectifs d'usage / formulation qualitative, pas faits prouvés. Disclaimer obligatoire. | Évite allégation trompeuse. |
| Go/No-Go sécurité|**39 critères single VPS** (31 V6/V7.1 +8 V7.1) avant premier client payant.  **46 critères Fleet**  (38 V6/V7.1 +8 V7.1 Fleet). Gate bloquant check_go_nogo.sh vert.|Voir §12.|

---
## 2. Vision Produit & Doctrine Opérationnelle (Manifeste Synthétique)

### 2.1 Setup & Onboarding — Configuration Initial et Wizard 5 Étapes (TRÉSOR 5)

> **Source unique :** Cette section document le processus d'onboarding hérité de V3.2, essentiel pour la première expérience utilisateur.

**Processus d'onboarding V3.2 préservé dans V7.1 :**

1. **Bienvenue** — Écran d'accueil avec promesse produit et philosophies Anti-ERP
2. **Connexion au serveur** — Configuration de l'accès au VPS dédié (adresse, credentials, test de connexion)
3. **Configuration Routeur LLM** (TRÉSOR 4) — Choix du provider IA :
   - **Défaut :** Mistral EU (souverain, conformité AI Act + DPA art28)
   - **Opt-in :** OpenAI, DeepSeek, Kimi (avec disclaimer RGPD explicite + case cochée Admin)
   - **Confidentiel :** Ollama Mistral 7B/Llama 3 local (zéro sortie de données, pour DCE Défense/Nucléaire)
4. **Import Vault A01-A12** — Chargement des 12 documents core de l'entreprise (KBIS, Qualibat, assurances, etc.)
5. **Premier AO golden file** — Analyse d'un AO historique pour calibrer les ratios et générer le premier HANDOFF+ Book

**Philosophie :** "On ne vous demande pas de configurer 50 paramètres. On vous guide en 5 étapes, et après vous êtes opérationnel."

**Implémentation :**
- CLI : `scripts/smartao` (V32-1) gère le workflow complet
- UI : Tauri conserve son onboarding natif avec progression visuelle
- Backend : Voir PLAN_MAITRE_V7.1 §16.2 (Sprint V32-2)
- Tests : test_onboarding_5_steps.py (V32-2)

**Lien avec Trésors :**
- Trésor 1 (Desktop Native) : Le shell Tauri héberge cet onboarding
- Trésor 4 (Routeur LLM) : Étape 3 configure le provider
- Trésor 5 (CLI) : `smartao` unifie l'expérience

---

### 2.2 Promesse Produit Unique

> **"DCE déposé → Go/No-Go chiffré sécurisé + dossier complet déposable en 48h sans exposition risque non provisionné."**

Objectifs d'usage: 1er AO avec remplissage Vault = temps réduit fortement (objectif usage, pas garantie). Dès 2e AO = accélération grâce Vault pré-rempli + preuves A08 réutilisées. Réduit cause majeure élimination formelle = objectif réduction significative (pas 0%).

### 2.3 Analyse Marché & Différenciation (Synthèse)

Marché actuel échoue:
- SaaS US (Ariba, Procore, Autodesk): données hors UE, abonnement perpétuel, BTP FR peu pris en compte, 40 onglets.
- Excel+Word+Drive: "final_final_CORRIGE.xlsx", versions multiples, risque vice forme, temps élevé.
- ERP lourds (Sage, Cegid, SAP): 50k€, 6 mois formation, personne s'en sert.
- Cabinets spécialisés: 3k€/dossier, 2 semaines délai, dépendance.

Doctrine SMART_AO :
- "Un appel d'offres est une opération structurée qui exige rigueur et méthode."
- "Le salarié est un opérateur guidé. Le patron garde le contrôle et la décision finale."
- "On ne laisse jamais l'IA calculer seule. LLM structure. Solveur chiffre. Humain valide."
- **Double moteur:** Moteur Cognitif IA (RAG multi-agents CCAG 2021, CCP, DTU, CCTP) lit, extrait, détecte qualitatif ZERO €. Garage Math calcule exact € Decimal.
- **UX:** Pas tableau bord 40 boutons. Barre progression. Un bouton à la fois. Salarié ne peut pas se tromper. Wizard 12 étapes.

### 2.3 Différenciateurs Durables

1. 20 ans expérience BTP injectés dans chaque règle codée (ex: RAT <1997, solidarité GME, coeff site occupé hôpital = +15%).
2. Architecture hybride IA + Garage Mathématique déjà codée BTP ENGINE/ChiffrageEngine — pas bullshit.
3. Vault A01-A12 immuable avec J-30 readonly bloquant dépôt.
4. DCE Trap Detector + **33 modules** = système arme juridique et financière complète.
5. Mémoire Booster 18/20 avec preuves géolocalisées A08 <50km + Gantt Météo France + bilan carbone ADEME FDES.
6. HANDOFF+ double artefact étanche financier.
7. **V6:** 16 modules supplémentaires couvrant élimination bête, boost de note, protection juridique prix, post-signature et contentieux.
**V7.1 Fusion 33 boucliers :** 12 historiques + 16 V6 + 5 V7.1: Q Pénurie & Pénibilité RH Shield, R Vigilance URSSAF & Délit Marchandage, S ZAN & Trackterres Shield, T Syntax Checker Formules Révision, U Sourcing & API Profil Acheteur
Voir RAPPORT §7.13 à §7.33 pour spécifications complètes.

### 2.4 Positionnement Offensif

Modèle A Souverain: Vos données sur VOTRE VPS OVH FR, opéré par vous, support éditeur sans accès données.
Modèle B Infogéré assumé avec DPA art.28: Vos données sur votre VPS dédié OVH FR, opéré en infogérance par éditeur avec DPA. Souveraineté physique maintenue (serveur EU dédié, pas mutualisé). Transparence totale.

---

#### Enrichissement V6 - Différenciateurs 12->28 boucliers + 16 nouveaux modules
- Anciennement 12 boucliers (BT, Pénalités, Trésorerie, GME, DC4, RAT, SOGED, Site, Cross-Check, Q/R, Mémoire, HANDOFF)
- **V6 Fusion 28 boucliers :** 12 historiques + 16 nouveaux :
  A Deadline Guardian, B Alloti Guardian, C RSE Booster +15% note, D Prix-Mémoire Coherence, E Variante Guardian, F Matériaux Shield, G PAB Detector, H Visite Auto GPS, I Enveloppe Separator 47 pièces 3 enveloppes, J Avenant Tracker OS récolement avenant max 20%, K Contentieux Generator, L Certif Live Checker J-90/J-60/J-30, M Capacité Financière, N Tableau Risques, O MAPA Generator, P E+C- Detector
- **Voir RAPPORT §7.13 à §7.28 pour spécifications complètes.**

#### Archive V12 §2 préservée

## 2. Vision Produit & Doctrine Opérationnelle (Manifeste Synthétique - Pas de Redondance)

### 2.1 Promesse Produit Unique

> **"DCE déposé → Go/No-Go chiffré sécurisé + dossier complet déposable en 48h sans exposition risque non provisionné."**

Objectifs d'usage: 1er AO avec remplissage Vault = temps réduit fortement (objectif usage, pas garantie). Dès 2e AO = accélération grâce Vault pré-rempli + preuves A08 réutilisées. Réduit cause majeure élimination formelle = objectif réduction significative (pas 0%).

### 2.2 Analyse Marché & Différenciation (Synthèse)

Marché actuel échoue:
- SaaS US (Ariba, Procore, Autodesk): données hors UE, abonnement perpétuel, BTP FR peu pris en compte, 40 onglets.
- Excel+Word+Drive: "final_final_CORRIGE.xlsx", versions multiples, risque vice forme, temps élevé.
- ERP lourds (Sage, Cegid, SAP): 50k€, 6 mois formation, personne s'en sert.
- Cabinets spécialisés: 3k€/dossier, 2 semaines délai, dépendance.

Doctrine SMART_AO :
- "Un appel d'offres est une opération structurée qui exige rigueur et méthode."
- "Le salarié est un opérateur guidé. Le patron garde le contrôle et la décision finale."
- "On ne laisse jamais l'IA calculer seule. LLM structure. Solveur chiffre. Humain valide."
- **Double moteur:** Moteur Cognitif IA (RAG multi-agents CCAG 2021, CCP, DTU, CCTP) lit, extrait, détecte qualitatif ZERO €. Garage Math calcule exact € Decimal.
- **UX:** Pas tableau bord 40 boutons. Barre progression. Un bouton à la fois. Salarié ne peut pas se tromper. Wizard 12 étapes.

### 2.3 Différenciateurs Durables

1. 20 ans expérience BTP injectés dans chaque règle codée (ex: RAT <1997, solidarité GME, coeff site occupé hôpital = +15%).
2. Architecture hybride IA + Garage Mathématique déjà codé BTP ENGINE/ChiffrageEngine - pas bullshit.
3. Vault A01-A12 immuable avec J-30 readonly bloquant dépôt.
4. DCE Trap Detector + 12 modules = système arme juridique et financière.
5. Mémoire Booster 18/20 avec preuves géolocalisées A08 <50km + Gantt Météo France + bilan carbone ADEME FDES.
6. HANDOFF+ double artefact étanche financier.

### 2.4 Positionnement Offensif

Modèle A Souverain: Vos données sur VOTRE VPS OVH FR, opéré par vous, support éditeur sans accès données.
Modèle B Infogéré assumé avec DPA art.28: Vos données sur votre VPS dédié OVH FR, opéré en infogérance par éditeur avec DPA. Souveraineté physique maintenue (serveur EU dédié, pas mutualisé). Transparence totale.

---
## 3. Architecture des Rôles & Workflow — Spécification Fonctionnelle Unique

### 3.1 Matrice RBAC Financier Étendue — SOURCE UNIQUE

C'est l'unique définition RBAC financier. Autres docs RÉFÈRENT cette section. Règle: Salarié = nature + criticité OUI/NON sans €. Admin/Patron = montant exact + graph + provision à valider.

| Ressource / Action | Salarié (Opérateur Guidé) | Admin / Patron (Contrôle Absolu) | Test Bloquant | Serializer / Middleware |
|---|---|---|---|---|
| Prix unitaires DPGF/BPU, coeff vente, marge nette | Non - ne voit jamais. Masquage DOM. | Oui ajustable, seul signe AE. | test_api_employee_cannot_see_prices.py + test_front_no_price_leak.spec.ts | strip_provisions_euros + require_admin deps.py |

---

### 3.2 Charte UX Anti-ERP & Règles d'Interface (TRÉSOR 2) — SOURCE UNIQUE

> **Philosophie fondatrice V3.2 :** SMART_AO n'est pas un ERP. C'est un compagnon de réponse aux AO. Cette charte UX est **la seule définition autorisée** des règles d'interface dans tout le corpus. Autres docs RÉFÈRENT cette section par "Voir RAPPORT §3.2".

**RÈGLES ANTI-ERP INTANGIBLES (héritage V3.2) :**

1. **Pas de sidebar permanente** — L'écran principal est **la liste des AO**, pas un menu latéral. Le salarié doit voir immédiatement ce qui compte : ses AO en cours.

2. **Un bouton à la fois** — Philosophie "un bouton à la fois, zéro erreur possible". Pas de multi-sélection, pas d'actions batch. Chaque écran = une action unique.

3. **Max 4 champs visibles par écran** — Tout formulaire avec plus de 4 champs est interdit. Si plus d'informations sont nécessaires, on découpe en étapes.

4. **Terminologie "Votre IA"** — Jamais mention de "Mistral", "LLM", "OpenAI", "modèle de langage" dans l'interface. C'est toujours "Votre IA" ou "l'assistant".

5. **Zéro tableau de bord avec 12 widgets** — Le Cockpit Admin a **5 tuiles maximum** (Finance Warfare, Vault, Deadline, Certif, Avenant). Pas de dashboard surchargé.

6. **Pas de chatbot qui demande « Posez une question »** — Doctrine V7.1 : un bouton à la fois, pas de chatbot. Le Chat Orchestrateur V3.2 est **ABANDONNÉ** (voir §V.1 Trésor 3).

7. **Pas de mention du modèle LLM dans l'interface** — L'utilisateur ne doit pas savoir quel modèle est utilisé. Seulement son résultat.

8. **Pas de navigation par onglets dans le wizard** — Le wizard est **linéaire, guidé**. Pas de retour en arrière possible (sauf validation obligatoire).

9. **Barre de progression toujours visible** — Le salarié doit toujours savoir où il en est dans le processus.

10. **Aide contextuelle DTU/CCAG** — Chaque champ a une aide contextuelle avec référence au DTU ou CCAG concerné.

**Implémentation technique :**
- Frontend : Respect strict dans React/TS + Tailwind. Tests frontaux : test_front_no_sidebar.spec.ts, test_max_4_fields.spec.ts, test_no_chatbot.spec.ts
- Backend : Aucune logique métier dans l'UI. Tout passe par l'API.
- Tests bloquants : Voir ENGINEERING-HANDBOOK §5 pour tests UX

**Pourquoi c'est critique :** Ces règles ont fait le succès commercial de V3.2. Les violer = perdre l'avantage concurrentiel "Anti-ERP".

---

### 3.3 Workflow Lifecycle 12 États — State Machine Unique (Opérateur Guidé) | Admin / Patron (Contrôle Absolu) | Test Bloquant | Serializer / Middleware |
|---|---|---|---|---|
| Prix unitaires DPGF/BPU, coeff vente, marge nette | Non — ne voit jamais. Masquage DOM. | Oui ajustable, seul signe AE. | test_api_employee_cannot_see_prices.py + test_front_no_price_leak.spec.ts | strip_provisions_euros + require_admin deps.py |
| Provisions € inflation BT (bt_projection) | Nature + criticité "Risque inflation élevé — Formule sans butoir" Badge rouge/jaune/vert. Pas de montant. | Montant exact -47 320€ + graph INSEE 36 mois + 3 scénarios érosion marge + provision 8% à valider | test_rbac_provisions.py | strip provisions |
| Exposition pénalités € cumul | Liste qualitative 6 pénalités dont 2 cachées avec page. Pas de plafond €. | Exposition max 124.5k€ 12% CA + plafond CCAG 10% dépassé + provision 16k€ + clause plafonnement générée | test_rbac_provisions.py | idem |
| BFR pic trésorerie € | Alerte "Trésorerie tendue M4-M6" courbe sans € + S-curve temps | Pic BFR -180k€ + courbe mois/mois + coût caution 960€ vs coût RG immobilisé 40k€ + arbitrage à valider | test_rbac_provisions.py + FinanceWarfareDashboard | idem |
| Coût REP déchets € | "Obligation SOGED 7 flux — Saisir exutoire" badge. Pas de coût. | Coût réel 4.2k€ + ventilation kg flux (bois, plâtre, inerte...) + SOGED généré + preuve factures tri | test_rbac_provisions.py | idem |
| Provision amiante RAT € SS4 | "RAT manquant — Saisir surface" + obligation SS4. Pas €. | Provision 18.5k€ + ratio 185€/m2 + délai 3 semaines + aléa + SOP SS4 | test_rbac_provisions.py | idem |
| Provision omission Cross-Check € | "4 portes vues plan RDC non chiffrées DPGF" + pastille plan. | Provision 3.1k€ + Qté plan * PU moyen + Question R2111-7 générée | test_rbac_provisions.py | idem |
| Provision site contraintes € | "+2.5h/j — Accès <3m — Site occupé hôpital" temps sans € | Impact 18k€ + 2 sem + coeff détaillé +15% occupé +10% accès | test_rbac_provisions.py | idem |
| Solidarité GME exposition | Alerte juridique "Solidarité élargie — Exposition hors marché" sans € | Exposition 180k€ + DC1 corrigé + répartition 100% + pièces manquantes | test_rbac_provisions.py | idem |
| DC4 sous-traitance cumul | Saisie nom/nature sous-traitant masquée après validation. Pas de cumul visible. | Cumul 62% >50% plafond + montant sous-traité + DC4 généré avec Vault A03 Qualibat | test_api_employee_cannot_see_prices | idem |
| Vault A01-A12 | Lecture + dépôt "A VALIDER" — badge J-30 visible. | Validation + J-30 badge rouge bloquant dépôt ZIP si A01-A03 EXPIRE + extraction SIRET + cohérence | test_vault_j30_readonly.py | readonly cron continue même is_readonly |
| Métrés Qté / Temps | Oui écriture Qté m2/ml/u + Temps h sans €. | Lecture + temps corrigé financier + impact € + coeff site appliqué | frontend RBAC | strip |
| Mémoire Booster | Rédige technique 80% auto avec preuves <50km sans prix. | Verrouille + ajoute marge + planning Gantt + bilan RE2020 + FDES + matrice conformité RC | generator_memoire | double version |
| Q/R Tactique MOE/MOA | Rédige technique + relecture tech 7 questions. | Valide juridique + enjeu 288k€ + export DOCX Profil Acheteur + trace mémoire réclamation | generator_qr_tactique | double artefact |
| Dépôt AE/DC1/DC4 | Brouillon sans montants. | Seul signe valide + montants + RIB + caution | generator_dc4 | require_admin |
| HANDOFF+ Book | Version expurgée sans marge sans € — Book conducteur 30p risques qualitatifs sans montants | Complète + expurgée double artefact + audit log + coffre-fort marge/BFR + Book complet marge provisions BFR | test_handoff_double_artefact.py + test_handoff_irreversible.py | double PDF physiquement distincts |
| **Modules V6 Admin Only** | | | | |
| Contentieux & Réclamation | Aucun accès. | Génération mémoire réclamation, mise en demeure, calcul intérêts LME | test_rbac_contentieux.py | require_admin |
| Capacité Financière | Aucun accès. | Ratios bilan, alerte élimination silencieuse | test_rbac_capacite.py | require_admin |
| Tableau Risques Comité | Aucun accès. | Génération 1 page PDF comité direction | test_rbac_tableau_risques.py | require_admin |

**Implémentation RBAC unique:**
- Backend: deps.py `require_admin` + `strip_provisions_euros(obj)` masque récursif champs: total_ht, marge, ae_total, treasury, provision_euros, cout_rep, exposition_penalites, bfr_pic, cout_caution, provision_amiante, provision_omission, cout_tresorerie, provision_site, montant_marche_ht, pic_bfr, marge_nette, cout_ss4.
- Frontend: test_front_no_price_leak.spec.ts scan DOM salarié 28 modules regex € `/(\d+\s?€|\bEUR\b|k€|provision|marge)/i` = 0 occurrence.
- Double artefact HANDOFF: génération 2 PDFs physiquement séparés — BOOK_CHANTIER_COMPLET_ADMIN.pdf avec marges/provisions/BFR coffre-fort Admin / BOOK_CHANTIER_EXECUTION_SALARIE.pdf sans aucune donnée €.

### 3.2 Workflow Lifecycle 12 États — State Machine Unique

`BROUILLON -> ANALYSE -> GO -> METRE -> SITE_CONTRAINTES -> MEMOIRE -> DOCS_ADMIN -> HANDOFF -> CHIFFRAGE_ADMIN -> VALIDATION_ADMIN -> DEPOSE -> ARCHIVE -> GAGNE/PERDU`

Transitions autorisées:
- ANALYSE -> GO (après Go/No-Go 39 critères salarié + admin validation)
- GO -> METRE -> SITE_CONTRAINTES -> MEMOIRE -> DOCS_ADMIN -> HANDOFF
- HANDOFF irréversible côté salarié: seul Admin peut passer HANDOFF -> CHIFFRAGE_ADMIN avec rejection_reason obligatoire si retour.
- CHIFFRAGE_ADMIN -> {METRE, MEMOIRE, BROUILLON} avec rejection_reason obligatoire tracé audit log.
- CHIFFRAGE_ADMIN -> VALIDATION_ADMIN -> DEPOSE -> ARCHIVE
- ARCHIVE -> GAGNE (déclenche HANDOFF+ Book généré en 2s, 30 pages) ou PERDU.

Gates bloquantes:
- Impossible passer GO si Vault A01-A03 EXPIRE (J-30 badge rouge).
- Impossible DEPOSE si provisions non validées Admin.
- Impossible GENERER BOOK si statut != GAGNE + seul Admin.
- **V6:** Impossible DEPOSE si Deadline Guardian alerte rouge active (pièce manquante ou délai dépassé).
- **V6:** Impossible DEPOSE si Certification Live Checker alerte rouge (Qualibat manquant ou expiré pendant marché).

### 3.3 Wizard Salarié 12 Étapes — Fonctionnel

Vision: "Un bouton à la fois, zéro erreur possible." Barre progression + % + temps restant estimé.

1. **Identify DCE:** Saisie BOAMP/PLACE URL ou upload ZIP DCE + SIRET acheteur auto extraction.
2. **Upload DCE:** Panoplie boutons: RC, CCAP, CCTP(s), DPGF/BPU Excel, Plans PDF, Diags, Planning, AE, DC1. Upload worker async avec progression. Parsing PyMuPDF+pdfplumber instantané, Docling worker séparé.
3. **Analyze 33 modules:** Lancement 33 agents IA qualitatifs ZERO € + 16 solveurs Garage. Affichage tuiles qualitatives sans €, badges couleurs, page référence. 2 colonnes: Checklist + Pièges Prix masqués (badge).
4. **Go/No-Go 39 critères:** Dashboard Go/No-Go salarié + admin. 39 critères (25 agents vert, 16 solveurs vert, RBAC provisions test vert, HANDOFF double artefact vert, agent no euro vert). Badge Go/No-Go avec justification.
5. **Site Visit (Contraintes §4.8):** Saisie salarié: site occupé (hôpital/EHPAD/école), accès <3m, hauteur >4m, stockage impossible, horaires restreints 8h-12h, centre-ville dense, bruit <70dB, photos terrain, notice. Extraction automatique CCTP 00 contraintes.
6. **Métré Temps Corrigé Site:** Saisie Qté m2/ml/u + temps h sans €. Application coeff site contrainte (§4.8) + temps corrigé affiché sans € côté salarié (ex: "+2.5h/j"). Pastilles plans.
7. **SOGED Saisie Exutoires (§4.7):** Saisie exutoires 7 flux (bois, plâtre, inerte, métaux, plastique, DIB, amiante) + transport km + REP. Obligation PEMD/SOGED détectée.
8. **Mémoire Booster A08-A10 + Gantt (§5):** Génération 80% auto: 50 contraintes CCTP extraites + preuves A08 géolocalisées <50km + méthodes A10 + planning Gantt OR-Tools avec intempéries Météo France 10 ans + RE2020 + FDES A09.
9. **Q/R Tactique Relecture (§4.10):** Relecture 8 questions max générées, tri enjeu € masqué salarié, ajustement technique salarié.
10. **AdminDocs DC1/DC2/DC4 (§4.5):** Saisie DC1 groupement + sous-traitants DC4 rang/plafond. Brouillon sans montants salarié.
11. **TechDocs:** Génération PPSPS, SOGED, Mémoire expurgé.
12. **Handoff Preview Expurgé:** Preview Book expurgé sans € + checklist dépôt + bouton Handoff vers Admin.

UX: 1 question à la fois, aide contextuelle DTU/CCAG, autosave, retour arrière, validation obligatoire avant next.

### 3.4 Cockpit Administrateur — Dashboard Principal (Tuiles Gros Boutons)

Vision: "Le Patron est le Maître — Contrôle absolu sans complexité."

Tuiles principales:
- **AO en cours** (Kanban par état workflow 12 étapes)
- **Finance Warfare Dashboard** (5 tuiles avec €, graphs, provisions à valider — voir §10)
- **Vault Dashboard** A01-A12 J-30 + cohérence SIRET/Qualibat + badge rouge bloquant
- **Personnalisation Entreprise** (logo, couleurs mémoire, base de prix PU moyens A01...)
- **Comptes Salariés** (création, RBAC, sandbox isolé par salarié via filesystem O_NOFOLLOW + fstat + BASE_ROOT non-symlink + owner check)
- **Contrôle Financier & Validation** (DCE Trap Detector + Garage Math + provisions 7 types à valider)
- **HANDOFF+ Dashboard** (bouton Générer Book + double artefact log + preview complet/expurgé selon rôle + audit log)
- **Analytics & Performance** (taux Go, marge moyenne, pièges fréquents)
- **Paramètres & Sécurité** (2FA TOTP Argon2id, API Mistral EU key, opt-in hors UE, backup/restore AES-256-GCM <15min, rollback snapshot LVM, cosign verify)
- **V6 — Deadline Guardian** (compte à rebours J-7/J-2/J-1/H-4, checklist pièces, blocage dépôt)
- **V6 — Contentieux & Réclamation** (génération mémoire réclamation, mise en demeure, suivi délais)
- **V6 — Post-Gagné Tracker** (avenants, récolements, levées réserves, alertes J-30)

---

### 3.1bis Matrice RBAC Étendue V7.1 - 14 V6 + 5 V7.1 Lignes (Source Unique - Ne Pas Dupliquer)

> Respecte SSoT RBAC : Salarié = nature + criticité sans €, Admin = montant exact + provision. Voir RAPPORT §3.1 pour règle de base. Ajout V6 = 14 lignes + V7.1 = 5 lignes suivantes.

| Ressource / Action V7.1 | Salarié (Opérateur Guidé) | Admin / Patron (Contrôle Absolu) | Test Bloquant V7.1 | Voir Module |
|---|---|---|---|---|
| **Deadline Guardian J-7/J-2/J-1 blocage dépôt** | Compte à rebours J-7/J-2/J-1/H-4/H-1 + checklist verte/rouge pièces obligatoires. Pas de forçage dépôt si rouge. | Forçage dépôt loggué avec motif + historique horodaté + badge bloquant rouge si Vault expire avant date limite. | test_deadline_guardian.py : blocage dépôt si pièce manquante ou Vault expire + compte à rebours exact fuseau plateforme | §7.13 |
| **Alloti Guardian similarité <85%** | Wizard séparé par lot, badge vert/orange/rouge par lot. Similarité mémoire inter-lots affichée qualitative sans détail. | Scoring similarité <85% obligatoire, détection lot piège, décision stratégique par lot, 5 mémoires + 5 DPGF générés. | test_alloti_guardian.py : détection alloti + séparation lots + similarité <85% contrôlée | §7.14 |
| **Enveloppe Separator 47 pièces 3 enveloppes DUME vs DC1/DC2** | Interface drag & drop 3 colonnes candidature/offre/prix-technique, compteur par enveloppe, alerte si DUME vs DC1/DC2 incohérent. | Vérification complétude 3 enveloppes + génération 3 ZIP prêts dépôt + checklist dépôt PDF, classification auto 47 pièces. | test_enveloppe_separator.py : classification auto 47 pièces + tri correct 3 enveloppes + DUME vs DC1/DC2 vérifié | §7.21 |
| **Certif Live Checker J-90/J-60/J-30 Qualibat/RGE/MASE** | Badge "2 qualifications manquantes" + alerte expiration qualitative, upload Qualibat. | Dashboard match exact qualifications demandées vs Vault A03 + planning renouvellement J-90/J-60/J-30 + Q/R qualifications générée. | test_certif_live_checker.py : match exact + expiration pendant marché détectée + zone géo | §7.24 |
| **PAB Detector écart -27% marge min 6% Admin only** | Badge "Prix à vérifier - Risque anormalement bas" sans montant. | Dashboard "Prix 380k€ vs moyenne 520k€ - Écart -27% PAB ÉLEVÉ" + marge min 6% + note justification 48h + simulation prix PDF. | test_pab_detector.py : alerte si écart <-20% orange, <-30% rouge + note justification générée | §7.19 |
| **Post-Gagné Avenant Tracker OS récolement avenant max 20%** | Tableau échéances chantier + alertes J-30 sans montants. | Dashboard calendrier échéances post-signature (OS, récolement, levée réserves, fin garantie décennale) + PV récolement + demande avenant + montant cumulé vs plafond 20% + reste disponible. | test_post_gagne_tracker.py : alertes J-30 échéances + PV récolement + demande avenant générés + calcul 20% | §7.22 |
| **RSE Booster +15% note** | Badge RSE 15% note + saisie heures/partenaire insertion. | Score prévisionnel RSE /20 + pénalité insertion 4 194€ (2×SMIC) + chapitre RSE auto + bilan RE2020 + calcul heures réalisables. | test_rse_booster.py | §7.15 |
| **Prix-Mémoire Coherence** | Badge "Mémoire vs DPGF - Vérifier cohérence" qualitatif. | Dashboard "Mémoire/DPGF = 62% IRRÉALISTE" + ratio coût mémoire / DPGF total + score cohérence + recommandations ajustement. | test_coherence.py | §7.16 |
| **Variante Guardian** | Wizard onglet Base + Variante + alerte irrégularité sans montants chiffrés. | Vérification dépôt 2 mémoires + 2 DPGF + ordre correct base obligatoire + 2 mémoires DOCX distincts. | test_variante_guardian.py | §7.17 |
| **Matériaux Shield** | Badge "Clause matériaux détectée - Vérifier protection" | Dashboard "Acier +40% = perte 90k€" + simulation par matériau (acier bois cuivre bitume ciment alu) + formule perte=montant*variation*duree/12 + Q/R matériaux DOCX | test_materiaux_shield.py + materiaux_shield.py formule vérifiée | §7.18 |
| **Attestation Visite Auto** | Alerte calendrier J-2 + upload photo GPS + checklist visite terrain qualitative. | Attestation visite pré-remplie + validation GPS coordonnées chantier vs photo + CR visite DOCX + photos ZIP horodatées. | test_visite_auto.py | §7.20 |
| **MAPA Generator** | Wizard 4 étapes MAPA simplifié + pré-remplissage Vault A01-A12. | Génération dossier MAPA complet PDF 10-15p + ZIP dépôt prêt + vérification complétude + checklist MAPA. | test_mapa_generator.py | §7.27 |
| **E+C- Detector** | Badge "Label E+C- détecté - Justificatifs à préparer" | Dashboard niveau visé vs atteignable + calcul empreinte carbone vs seuil (E1C1/E2C1/E3C2...) + attestation + ACV Excel + FDES. | test_eplusc_detector.py + eplusc_calculator CO2 vs seuils | §7.28 |
| **Contentieux, Capacité Financière, Tableau Risques (Admin Only)** | Aucun accès salarié. | Contentieux: mémoire réclamation + mise en demeure + intérêts LME 3×BCE. Capacité: FR=CapPerm-Immo, CAF, endettement vs seuils RC. Tableau Risques: agrégation impact total € + marge résiduelle <3% = No-Go, 1 page PDF comité + PPT 3 slides + Excel. | test_contentieux_generator.py + test_capacite + test_tableau_risques | §7.23 / §7.25 / §7.26 |
| Pénurie & Pénibilité RH|Badge "Contraintes pénibilité détectées — Vérifier disponibilité RH" sans montant|Dashboard impact intérim +42 000€ + coefficient majoration + provision à valider|test_penibilite_rh.py|§7.29|
| Vigilance URSSAF Sous-Traitant|Badge "Attestation URSSAF à vérifier" sans montant|Blocage pénal si attestation expirée + exposition solidarité 140 000€ + DC4 bloqué|test_vigilance_urssaf.py|§7.30|
| ZAN & Trackterres|Badge "Évacuation terres détectée — Vérifier exutoire" sans montant|Coût transport + ISDI + Trackterres +28 000€ + provision à valider|test_zan_trackterres.py|§7.31|
| Syntax Checker Formules Révision|Badge "Formule révision à vérifier" sans montant|Erreur CCAP détectée somme coeffs ≠ 1 + Q/R générée + impact 8% marge|test_formule_revision.py|§7.32|
| Sourcing & API Profil Acheteur|Wizard dépôt simplifié + statut envoi|Bouton "Déposer" pousse directement sur Profil Acheteur + horodatage cryptographique + DUME natif JSON|test_sourcing_api.py|§7.33|

**Rappel SSoT :** Toute autre documentation doit référencer "Voir RAPPORT §3.1" ou "Voir RAPPORT §3.1bis" pour RBAC, jamais dupliquer.

#### Archive V12 §3 préservée

## 3. Architecture des Rôles & Workflow - Spécification Fonctionnelle Unique (Pas de Répétition Ailleurs)

### 3.1 Matrice RBAC Financier Étendue - SOURCE UNIQUE (Ne Pas Dupliquer Ailleurs)

C'est l'unique définition RBAC financier. Autres docs RÉFÈRENT cette section. Règle: Salarié = nature + criticité OUI/NON sans €. Admin/Patron = montant exact + graph + provision à valider.

| Ressource / Action | Salarié (Opérateur Guidé) | Admin / Patron (Contrôle Absolu) | Test Bloquant | Serializer / Middleware |
|---|---|---|---|---|
| Prix unitaires DPGF/BPU, coeff vente, marge nette | Non - ne voit jamais. Masquage DOM. | Oui ajustable, seul signe AE. | test_api_employee_cannot_see_prices.py + test_front_no_price_leak.spec.ts | strip_provisions_euros + require_admin deps.py |
| Provisions € inflation BT (bt_projection) | Nature + criticité "Risque inflation élevé - Formule sans butoir" Badge rouge/jaune/vert. Pas de montant. | Montant exact -47 320€ + graph INSEE 36 mois + 3 scénarios érosion marge + provision 8% à valider | test_rbac_provisions.py | strip provisions |
| Exposition pénalités € cumul | Liste qualitative 6 pénalités dont 2 cachées avec page. Pas de plafond €. | Exposition max 124.5k€ 12% CA + plafond CCAG 5% dépassé + provision 16k€ + clause plafonnement générée | test_rbac_provisions.py | idem |
| BFR pic trésorerie € | Alerte "Trésorerie tendue M4-M6" courbe sans € + S-curve temps | Pic BFR -180k€ + courbe mois/mois + coût caution 960€ vs coût RG immobilisé 40k€ + arbitrage à valider | test_rbac_provisions.py + FinanceWarfareDashboard | idem |
| Coût REP déchets € | "Obligation SOGED 7 flux - Saisir exutoire" badge. Pas de coût. | Coût réel 4.2k€ + ventilation kg flux (bois, plâtre, inerte...) + SOGED généré + preuve factures tri | test_rbac_provisions.py | idem |
| Provision amiante RAT € SS4 | "RAT manquant - Saisir surface" + obligation SS4. Pas €. | Provision 18.5k€ + ratio 185€/m2 + délai 3 semaines + aléa + SOP SS4 | test_rbac_provisions.py | idem |
| Provision omission Cross-Check € | "4 portes vues plan RDC non chiffrées DPGF" + pastille plan. | Provision 3.1k€ + Qté plan * PU moyen + Question R2111-7 générée | test_rbac_provisions.py | idem |
| Provision site contraintes € | "+2.5h/j - Accès <3m - Site occupé hôpital" temps sans € | Impact 18k€ + 2 sem + coeff détaillé +15% occupé +10% accès | test_rbac_provisions.py | idem |
| Solidarité GME exposition | Alerte juridique "Solidarité élargie - Exposition hors marché" sans € | Exposition 180k€ + DC1 corrigé + répartition 100% + pièces manquantes | test_rbac_provisions.py | idem |
| DC4 sous-traitance cumul | Saisie nom/nature sous-traitant masquée après validation. Pas de cumul visible. | Cumul 62% >50% plafond + montant sous-traité + DC4 généré avec Vault A03 Qualibat | test_api_employee_cannot_see_prices | idem |
| Vault A01-A12 | Lecture + dépôt "A VALIDER" - badge J-30 visible. | Validation + J-30 badge rouge bloquant dépôt ZIP si A01-A03 EXPIRE + extraction SIRET + cohérence | test_vault_j30_readonly.py | readonly cron continue même is_readonly |
| Métrés Qté / Temps | Oui écriture Qté m2/ml/u + Temps h sans €. | Lecture + temps corrigé financier + impact € + coeff site appliqué | frontend RBAC | strip |
| Mémoire Booster | Rédige technique 80% auto avec preuves <50km sans prix. | Verrouille + ajoute marge + planning Gantt + bilan RE2020 + FDES + matrice conformité RC | generator_memoire | double version |
| Q/R Tactique MOE/MOA | Rédige technique + relecture tech 7 questions. | Valide juridique + enjeu 288k€ + export DOCX Profil Acheteur + trace mémoire réclamation | generator_qr_tactique | double artefact |
| Dépôt AE/DC1/DC4 | Brouillon sans montants. | Seul signe valide + montants + RIB + caution | generator_dc4 | require_admin |
| HANDOFF+ Book | Version expurgée sans marge sans € - Book conducteur 30p risques qualitatifs sans montants | Complète + expurgée double artefact + audit log + coffre-fort marge/BFR + Book complet marge provisions BFR | test_handoff_double_artefact.py + test_handoff_irreversible.py | double PDF physiquement distincts |

**Implémentation RBAC unique:**
- Backend: deps.py `require_admin` + `strip_provisions_euros(obj)` masque récursif champs: total_ht, marge, ae_total, treasury, provision_euros, cout_rep, exposition_penalites, bfr_pic, cout_caution, provision_amiante, provision_omission, cout_tresorerie, provision_site, montant_marche_ht, pic_bfr, marge_nette, cout_ss4.
- Frontend: test_front_no_price_leak.spec.ts scan DOM salarié 12 modules regex € `/(\\d+\\s?€|\\bEUR\\b|k€|provision|marge)/i` = 0 occurrence.
- Double artefact HANDOFF: génération 2 PDFs physiquement séparés - BOOK_CHANTIER_COMPLET_ADMIN.pdf avec marges/provisions/BFR coffre-fort Admin / BOOK_CHANTIER_EXECUTION_SALARIE.pdf sans aucune donnée €.

### 3.2 Workflow Lifecycle 12 États - State Machine Unique

`BROUILLON -> ANALYSE -> GO -> METRE -> SITE_CONTRAINTES -> MEMOIRE -> DOCS_ADMIN -> HANDOFF -> CHIFFRAGE_ADMIN -> VALIDATION_ADMIN -> DEPOSE -> ARCHIVE -> GAGNE/PERDU`

Transitions autorisées:
- ANALYSE -> GO (après Go/No-Go 17 critères salarié + admin validation)
- GO -> METRE -> SITE_CONTRAINTES -> MEMOIRE -> DOCS_ADMIN -> HANDOFF
- HANDOFF irréversible côté salarié: seul Admin peut passer HANDOFF -> CHIFFRAGE_ADMIN avec rejection_reason obligatoire si retour.
- CHIFFRAGE_ADMIN -> {METRE, MEMOIRE, BROUILLON} avec rejection_reason obligatoire tracé audit log.
- CHIFFRAGE_ADMIN -> VALIDATION_ADMIN -> DEPOSE -> ARCHIVE
- ARCHIVE -> GAGNE (déclenche HANDOFF+ Book généré en 2s, 30 pages) ou PERDU.

Gates bloquantes:
- Impossible passer GO si Vault A01-A03 EXPIRE (J-30 badge rouge).
- Impossible DEPOSE si provisions non validées Admin.
- Impossible GENERER BOOK si statut != GAGNE + seul Admin.

### 3.3 Wizard Salarié 12 Étapes - Fonctionnel

Vision: "Un bouton à la fois, zéro erreur possible." Barre progression + % + temps restant estimé.

1. **Identify DCE:** Saisie BOAMP/PLACE URL ou upload ZIP DCE + SIRET acheteur auto extraction.
2. **Upload DCE:** Panoplie boutons: RC, CCAP, CCTP(s), DPGF/BPU Excel, Plans PDF, Diags, Planning, AE, DC1. Upload worker async avec progression. Parsing PyMuPDF+pdfplumber instantané, Docling worker séparé.
3. **Analyze 12 modules :** Lancement 12 agents IA qualitatifs ZERO € + 5 solveurs Garage. Affichage tuiles qualitatives sans €, badges couleurs, page référence. 2 colonnes: Checklist + Pièges Prix masqués (badge).
4. **Go/No-Go 12+5 critères:** Dashboard Go/No-Go salarié + admin. 12 critères +5 critères (12 agents vert, 5 solveurs vert, RBAC provisions test vert, HANDOFF double artefact vert, agent no euro vert). Badge Go/No-Go avec justification.
5. **Site Visit (Contraintes §4.8):** Saisie salarié: site occupé (hôpital/EHPAD/école), accès <3m, hauteur >4m, stockage impossible, horaires restreints 8h-12h, centre-ville dense, bruit <70dB, photos terrain, notice. Extraction automatique CCTP 00 contraintes.
6. **Métré Temps Corrigé Site:** Saisie Qté m2/ml/u + temps h sans €. Application coeff site contrainte (§4.8) + temps corrigé affiché sans € côté salarié (ex: "+2.5h/j"). Pastilles plans.
7. **SOGED Saisie Exutoires (§4.7):** Saisie exutoires 7 flux (bois, plâtre, inerte, métaux, plastique, DIB, amiante) + transport km + REP. Obligation PEMD/SOGED détectée.
8. **Mémoire Booster A08-A10 + Gantt (§5):** Génération 80% auto: 50 contraintes CCTP extraites + preuves A08 géolocalisées <50km + méthodes A10 + planning Gantt OR-Tools avec intempéries Météo France 10 ans + RE2020 + FDES A09.
9. **Q/R Tactique Relecture (§4.10):** Relecture 8 questions max générées, tri enjeu € masqué salarié, ajustement technique salarié.
10. **AdminDocs DC1/DC2/DC4 (§4.5):** Saisie DC1 groupement + sous-traitants DC4 rang/plafond. Brouillon sans montants salarié.
11. **TechDocs:** Génération PPSPS, SOGED, Mémoire expurgé.
12. ** Handoff Preview Expurgé:** Preview Book expurgé sans € + checklist dépôt + bouton Handoff vers Admin.

UX: 1 question à la fois, aide contextuelle DTU/CCAG, autosave, retour arrière, validation obligatoire avant next.

### 3.4 Cockpit Administrateur - Dashboard Principal (Tuiles Gros Boutons)

Vision: "Le Patron est le Maître - Contrôle absolu sans complexité."

Tuiles principales:
- **AO en cours** (Kanban par état workflow 12 étapes)
- **Finance Warfare Dashboard ** (5 tuiles avec €, graphs, provisions à valider - voir §10)
- **Vault Dashboard** A01-A12 J-30 + cohérence SIRET/Qualibat + badge rouge bloquant
- **Personnalisation Entreprise** (logo, couleurs mémoire, base de prix PU moyens A01...)
- **Comptes Salariés** (création, RBAC, sandbox isolé par salarié via filesystem O_NOFOLLOW + fstat + BASE_ROOT non-symlink + owner check)
- **Contrôle Financier & Validation** (DCE Trap Detector + Garage Math + provisions 7 types à valider)
- **HANDOFF+ Dashboard** (bouton Générer Book + double artefact log + preview complet/expurgé selon rôle + audit log)
- **Analytics & Performance** (taux Go, marge moyenne, pièges fréquents)
- **Paramètres & Sécurité** (2FA TOTP Argon2id, API Mistral EU key, opt-in hors UE, backup/restore AES-256-GCM <15min, rollback snapshot LVM, cosign verify)

---
## 4. Vault A01-A12 — Base Immuable Documentaire & Inventaire Core

### 4.1 Définition 12 Documents Core (90% éliminations évitables)

Vault = coffre-fort immuable versionné 10 versions max FileLock single worker.

- **A01 Juridique Fiscal:** URSSAF, DGFIP, Kbis <3 mois, attestation fiscale, SIRET cohérence. OCR + extraction dates.
- **A02 Assurances:** RC, Décennale avec activités parsées, dates validité, plafond.
- **A03 Qualifications:** Qualibat, Qualifelec, domaines, niveaux.
- **A04 Moyens Humains:** CV, CACES, AIPR, habilitations électriques.
- **A05 Moyens Matériels:** parc engins, cartes grises, VGP.
- **A06 Références:** ATT, PV réception, fiches chantier type, montants, maîtres d'ouvrage.
- **A07 Financier:** bilans 3 ans, CA, attestations banque, RIB.
- **A08 Preuves Terrain ADN Local:** photothèque géolocalisée avec EXIF + légende + date + PV + distance <50km chantier auto. Coeur Mémoire Booster 18/20.
- **A09 Environnemental QSE:** ISO 14001, 9001, FDES perso, RE2020 base, charte chantier propre.
- **A10 Méthodologie:** PPSPS type, SOP SS4 amiante, modèles SOGED, DUERP, mode opératoire plomb.
- **A11 Administratif Marchés:** DC1/DC2/DUME pré-remplis, modèle mémoire, attestation visite.
- **A12 Cautions Garanties:** modèles caution RG, avance, retenue garantie.

### 4.2 Pipeline J-30 & SIRET Guardian

- **Cron quotidien continue même is_readonly=True** — test `test_vault_j30_readonly.py` vert.
- Emails J-30/J-7/J-1 à Admin. Badge rouge bloquant si A01-A03 EXPIRE. Impossible générer ZIP dépôt si EXPIRE.
- **SIRET Guardian:** extraction SIRET via OCR + cohérence: SIRET Kbis vs URSSAF vs DGFIP vs RC vs Qualibat. Si incohérence 1 chiffre = badge rouge bloquant. Source 30% éliminations formelles.
- **SMART IA Upload Worker:** à chaque upload DCE/Vault, extraction auto SIRET, dates, activités, montants quali, indexation Qdrant vault collection.

Réf tech détaillée Vault (mem_limit, FileLock, versioning, code): Voir ENGINEERING-HANDBOOK- section Vault.

---

#### Archive V12 §4 préservée

## 4. Vault A01-A12 - Base Immuable Documentaire & Inventaire Core

### 4.1 Définition 12 Documents Core (90% éliminations évitables)

Vault = coffre-fort immuable versionné 10 versions max FileLock single worker.

- **A01 Juridique Fiscal:** URSSAF, DGFIP, Kbis <3 mois, attestation fiscale, SIRET cohérence. OCR + extraction dates.
- **A02 Assurances:** RC, Décennale avec activités parsées, dates validité, plafond.
- **A03 Qualifications:** Qualibat, Qualifelec, domaines, niveaux.
- **A04 Moyens Humains:** CV, CACES, AIPR, habilitations électriques.
- **A05 Moyens Matériels:** parc engins, cartes grises, VGP.
- **A06 Références:** ATT, PV réception, fiches chantier type, montants, maîtres d'ouvrage.
- **A07 Financier:** bilans 3 ans, CA, attestations banque, RIB.
- **A08 Preuves Terrain ADN Local:** photothèque géolocalisée avec EXIF + légende + date + PV + distance <50km chantier auto. Coeur Mémoire Booster 18/20.
- **A09 Environnemental QSE:** ISO 14001, 9001, FDES perso, RE2020 base, charte chantier propre.
- **A10 Méthodologie:** PPSPS type, SOP SS4 amiante, modèles SOGED, DUERP, mode opératoire plomb.
- **A11 Administratif Marchés:** DC1/DC2/DUME pré-remplis, modèle mémoire, attestation visite.
- **A12 Cautions Garanties:** modèles caution RG, avance, retenue garantie.

### 4.2 Pipeline J-30 & SIRET Guardian

- **Cron quotidien continue même is_readonly=True** - test `test_vault_j30_readonly.py` vert.
- Emails J-30/J-7/J-1 à Admin. Badge rouge bloquant si A01-A03 EXPIRE. Impossible générer ZIP dépôt si EXPIRE.
- **SIRET Guardian:** extraction SIRET via OCR + cohérence: SIRET Kbis vs URSSAF vs DGFIP vs RC vs Qualibat. Si incohérence 1 chiffre = badge rouge bloquant. Source 30% éliminations formelles.
- **SMART IA Upload Worker:** à chaque upload DCE/Vault, extraction auto SIRET, dates, activités, montants quali, indexation Qdrant vault collection.

Réf tech détaillée Vault (mem_limit, FileLock, versioning, code): Voir ENGINEERING-HANDBOOK- section Vault.

---
## 5. Les 5 Moteurs Produit + 4 Armes Innovatrices + DCE Trap Detector

### 5.0 Synthèse Moteurs

**Moteur 1: Smart IA Upload Worker**
Async worker Celery/Redis AOF. Upload -> PyMuPDF+pdfplumber parse <2s/page -> Docling worker séparé si pdf image >10p -> OCR Tesseract BTP dict -> extraction SIRET/dates/activités -> embedding BGE-M3 -> Qdrant dce collection on_disk=True sparse on_disk=True. Progression WebSocket.

**Moteur 2: ADN Extractor**
RAG + LLM Mistral EU structuré: extrait 50 contraintes spécifiques CCTP (ex: "bruit <45dB chantier école occupé + poussière <10mg/m3 + horaires 8h-12h + accès <2.5m + hauteur sous plafond 3.2m + RE2020 + ...") + distance agence-chantier + nom conducteur + spécificités climatiques commune. Output JSON strict sans hallucination €. Utilisé par Mémoire Booster 18/20.

**Moteur 3: DCE Trap Detector — 4 Familles (Base + Routage vers 28 modules)**
Agent RAG multi-agents CCAG 2021, CCP, DTU. Lit N'IMPORTE QUEL DCE (AP-HP 412p, NOVO centrale groupes électrogènes...) et détecte pièges. Classification 4 familles originelles + routage 28 modules (§7.1-7.28):
- Famille 1 Pièces Contractuelles & Risques Juridiques: GME solidarité (§7.4), CCTP marques impératives R2111-7 (§7.9), CCAP pénalités (§7.2), clause butoir (§7.1), PAB (§7.16), variantes (§7.15), délais (§7.13)
- Famille 2 Aspects Techniques & Site: RAT amiante <1997 (§7.6), site occupé accès hauteur (§7.8), SOGED REP (§7.7), E+C- (§7.28)
- Famille 3 Financiers & Quantitatifs: BT index sans butoir (§7.1), BFR avance/RG (§7.3), DPGF vs CCTP incohérences (§7.9), matériaux post-Covid (§7.17), capacité financière (§7.24)
- Famille 4 Autres Pièges: DC4 plafond (§7.5), Q/R tactique (§7.10), GME DC1 pièces manquantes (§7.4), deadline (§7.13), alloti (§7.14), enveloppes (§7.19), visite (§7.18)

Sortie JSON: `{"famille": "...", "module_route": "7.X", "page": 123, "extrait": "...", "niveau": "rouge/orange/vert", "confiance": 0.92}` ZERO €.

**Moteur 4: GARAGE MATHÉMATIQUE (BTP ENGINE) — PuLP + OR-Tools + Decimal — ZERO LLM**
Règle absolue: Aucun fichier dans app/engines/math_engine/ n'importe openai, anthropic, langchain, mistralai. Scan test_math_engine_no_llm_import.py bloquant. PuLP SimpleX CBC solveur + OR-Tools CP-SAT/Gantt + Decimal 28 to_decimal(str) obligatoire — JAMAIS float pour €.
- 5 solveurs historiques: ChiffrageEngine marge, Treasury BFR, Planning Gantt, Quantité, Coeff site
- 10 solveurs Étendus V6 (§9): bt_projection INSEE, penalites_cumul, rep_cost ADEME, site_coeff, incoherence_solver, capacite_financiere, risques_generator, mapa_generator, eplusc_calculator, pab_detector, materiaux_shield
Voir §9 pour contrats fonctionnels détaillés. Technique: Voir ENGINEERING-HANDBOOK.

**Moteur 5: RAG Engine Hybrid Dense+Sparse+RRF+Fallback FTS**
4 collections Qdrant sans préfixe tenant: dce (RC/CCAP/CCTP/Plans/BPU/Diags), vault (A01-A12), chantiers (historique prix), traps (base connaissance pièges). BGE-M3 embeddings multilingues e5 + sparse SPLADE. Hybrid search natif Qdrant: dense 0.7 + sparse 0.3 + RRF k=60. Fallback FTS Postgres btp_french custom dict si Qdrant down. Use cases: DCE Trap Detector RAG, Vault Semantic Search sans nom, Chantier Matcher mémoire infinie prix (prix moyen au m2 par type chantier <50km), QA mémoire.
Code vivant embedding_engine.py: API key obligatoire Qdrant, on_disk=True pour dense+sparse, pas de tenant param — conformité single-tenant pur.
Réf tech: Voir ENGINEERING-HANDBOOK RAG Pipeline.

### 5.1 Les 4 Armes Innovatrices (Différenciation)

**Arme 1: SIRET Guardian — Cohérence Automatique**
Voir §4.2 — Bloque 30% éliminations. Scan cross-documents Kbis/URSSAF/DGFIP/Assurances.

**Arme 2: SMART IA Upload — Extraction Auto à l'Upload**
Voir Moteur 1 — Zéro saisie manuelle dates validité, activités, SIRET.

**Arme 3: DCE Trap Detector + Garage Math — Ne Pas Perdre d'Argent**
Moteur 3 + Moteur 4 couplés: IA détecte piège qualitatif ZERO €, Garage calcule exact provision € Decimal. Séparation stricte rôles via RBAC §3.1.

**Arme 4: Mémoire Booster 18/20 + HANDOFF+ Double Artefact**
Voir §8 et §9 — Transforme AO détecteur en système protection marge + mémoire qui gagne + book démarrage chantier étanche.

### 5.2 RAG Pipeline Résumé (Détail tech Voir Handbook)

Pourquoi RAG change tout: CCAG 2021 + CCP + DTU + 12 docs Vault + historique chantiers = 5000 pages par client — impossible LLM context seul. RAG hybrid permet recherche sémantique exacte page/paragraphe avec source citée.

Chunking intelligent par type: RC 800 tokens, CCTP 1200 tokens avec overlap titre paragraphe DTU, DPGF ligne par ligne Excel, Plans OCR bloc.

Ce qui change dans arborescence: app/services/embedding_engine.py, document_chunker.py, dce_trap_detector_rag.py, vault_semantic_search.py, chantier_matcher.py, embedding_fallback.py, embedding_preloader.py.

### 5.3 MCP Externe + Interne (Synopsis — Détail tech Voir Handbook)

**Pourquoi MCP:** Pivot — au lieu appeler APIs direct, on expose tools standard Model Context Protocol pour agents IA.

**MCP Externe BOAMP/PLACE — 3 tools:**
- boamp_search: recherche AO par CPV/département/montant/date
- boamp_get_dce: download DCE ZIP depuis PLACE/BOAMP
- boamp_track: suivi AO favoris + alerte modif DCE + J-30
Radar 6h cron + workflow: Voir ENGINEERING-HANDBOOK pour code.

**MCP Interne — 3 servers CŒUR + Pricing Memory:**
- Filesystem MCP Server (13 tools complet + annotations + Roots flow) FORK Python SMART_AO: `_check_access(path)` non négociable avec BASE_ROOT non symlink + O_NOFOLLOW + fstat + owner check (voir §21.1 ). Tools: read_file, write_file, list_dir, search, etc. Sandbox /data/minio.
- Excel MCP (FileLock + versioning 10 + validation header + single worker thread-safety).
- Pricing Memory MCP (CUSTOM, pas officiel — 4 tools validés): get_chantier_price (historique prix moyen m2), detect_sous_chiffrage (-12% flag rouge 10k€/ligne), save_price_after_win, compare_pu_base_prix. Détecte sous-chiffrage ligne DPGF vs base prix Admin.

Décision finale: On prend Filesystem custom (fork sécurisé) + Excel custom + Pricing Memory custom. Memory MCP officiel non pris (risque fuite).

Host unique app/mcp/internal/host.py tourne thread FastAPI, pas process séparé + audit log middleware.

Technique pure MCP: Voir ENGINEERING-HANDBOOK section MCP_DOCS_V2 fusionnée.

---

#### Archive V12 §5 préservée

## 5. Les 5 Moteurs Produit + 4 Armes Innovatrices + DCE Trap Detector

### 5.0 Synthèse Moteurs

**Moteur 1: Smart IA Upload Worker**
Async worker Celery/Redis AOF. Upload -> PyMuPDF+pdfplumber parse <2s/page -> Docling worker séparé si pdf image >10p -> OCR Tesseract BTP dict -> extraction SIRET/dates/activités -> embedding BGE-M3 -> Qdrant dce collection on_disk=True sparse on_disk=True. Progression WebSocket.

**Moteur 2: ADN Extractor**
RAG + LLM Mistral EU structuré: extrait 50 contraintes spécifiques CCTP (ex: "bruit <45dB chantier école occupé + poussière <10mg/m3 + horaires 8h-12h + accès <2.5m + hauteur sous plafond 3.2m + RE2020 + ...") + distance agence-chantier + nom conducteur + spécificités climatiques commune. Output JSON strict sans hallucination €. Utilisé par Mémoire Booster 18/20.

**Moteur 3: DCE Trap Detector - 4 Familles (Base + Routage vers 12 modules)**
Agent RAG multi-agents CCAG 2021, CCP, DTU. Lit N'IMPORTE QUEL DCE (AP-HP 412p, NOVO centrale groupes électrogènes...) et détecte pièges. Classification 4 familles originelles + routage 12 modules (§4.1-4.10):
- Famille 1 Pièces Contractuelles & Risques Juridiques: GME solidarité (§4.4), CCTP marques impératives R2111-7 (§4.9), CCAP pénalités (§4.2), clause butoir (§4.1)
- Famille 2 Aspects Techniques & Site: RAT amiante <1997 (§4.6), site occupé accès hauteur (§4.8), SOGED REP (§4.7)
- Famille 3 Financiers & Quantitatifs: BT index sans butoir (§4.1), BFR avance/RG (§4.3), DPGF vs CCTP incohérences (§4.9)
- Famille 4 Autres Pièges: DC4 plafond (§4.5), Q/R tactique (§4.10), GME DC1 pièces manquantes (§4.4)

Sortie JSON: `{"famille": "...", "module_route": "4.X", "page": 123, "extrait": "...", "niveau": "rouge/orange/vert", "confiance": 0.92}` ZERO €.

**Moteur 4: GARAGE MATHÉMATIQUE (BTP ENGINE) - PuLP + OR-Tools + Decimal - ZERO LLM**
Règle absolue: Aucun fichier dans app/engines/math_engine/ n'importe openai, anthropic, langchain, mistralai. Scan test_math_engine_no_llm_import.py bloquant. PuLP SimpleX CBC solveur + OR-Tools CP-SAT/Gantt + Decimal 28 to_decimal(str) obligatoire - JAMAIS float pour €.
- 5 solveurs historiques: ChiffrageEngine marge, Treasury BFR, Planning Gantt, Quantité, Coeff site
- 5 nouveaux solveurs Étendus (§10): bt_projection INSEE, penalites_cumul, rep_cost ADEME, site_coeff, incoherence_solver
Voir §10 pour contrats fonctionnels détaillés. Technique: Voir ENGINEERING-HANDBOOK.

**Moteur 5: RAG Engine Hybrid Dense+Sparse+RRF+Fallback FTS**
4 collections Qdrant sans préfixe tenant: dce (RC/CCAP/CCTP/Plans/BPU/Diags), vault (A01-A12), chantiers (historique prix), traps (base connaissance pièges). BGE-M3 embeddings multilingues e5 + sparse SPLADE. Hybrid search natif Qdrant: dense 0.7 + sparse 0.3 + RRF k=60. Fallback FTS Postgres btp_french custom dict si Qdrant down. Use cases: DCE Trap Detector RAG, Vault Semantic Search sans nom, Chantier Matcher mémoire infinie prix (prix moyen au m2 par type chantier <50km), QA mémoire.
Code vivant embedding_engine.py: API key obligatoire Qdrant, on_disk=True pour dense+sparse, pas de tenant param - conformité single-tenant pur.
Réf tech: Voir ENGINEERING-HANDBOOK RAG Pipeline.

### 5.1 Les 4 Armes Innovatrices (Différenciation)

**Arme 1: SIRET Guardian - Cohérence Automatique**
Voir §4.2 - Bloque 30% éliminations. Scan cross-documents Kbis/URSSAF/DGFIP/Assurances.

**Arme 2: SMART IA Upload - Extraction Auto à l'Upload**
Voir Moteur 1 - Zéro saisie manuelle dates validité, activités, SIRET.

**Arme 3: DCE Trap Detector + Garage Math - Ne Pas Perdre d'Argent**
Moteur 3 + Moteur 4 couplés: IA détecte piège qualitatif ZERO €, Garage calcule exact provision € Decimal. Séparation stricte rôles via RBAC §3.1.

**Arme 4: Mémoire Booster 18/20 + HANDOFF+ Double Artefact**
Voir §8 et §9 - Transforme AO détecteur en système protection marge + mémoire qui gagne + book démarrage chantier étanche.

### 5.2 RAG Pipeline Résumé (Détail tech Voir Handbook)

Pourquoi RAG change tout: CCAG 2021 + CCP + DTU + 12 docs Vault + historique chantiers = 5000 pages par client - impossible LLM context seul. RAG hybrid permet recherche sémantique exacte page/paragraphe avec source citée.

Chunking intelligent par type: RC 800 tokens, CCTP 1200 tokens avec overlap titre paragraphe DTU, DPGF ligne par ligne Excel, Plans OCR bloc.

Ce qui change dans arborescence: app/services/embedding_engine.py, document_chunker.py, dce_trap_detector_rag.py, vault_semantic_search.py, chantier_matcher.py, embedding_fallback.py, embedding_preloader.py.

### 5.3 MCP Externe + Interne (Synopsis - Détail tech Voir Handbook)

**Pourquoi MCP:** Pivot - au lieu appeler APIs direct, on expose tools standard Model Context Protocol pour agents IA.

**MCP Externe BOAMP/PLACE - 3 tools:**
- boamp_search: recherche AO par CPV/département/montant/date
- boamp_get_dce: download DCE ZIP depuis PLACE/BOAMP
- boamp_track: suivi AO favoris + alerte modif DCE + J-30
Radar 6h cron + workflow: Voir ENGINEERING-HANDBOOK pour code.

**MCP Interne - 3 servers CŒUR + Pricing Memory:**
- Filesystem MCP Server (13 tools complet + annotations + Roots flow) FORK Python SMART_AO: `_check_access(path)` non négociable avec BASE_ROOT non symlink + O_NOFOLLOW + fstat + owner check (voir §21.1 ). Tools: read_file, write_file, list_dir, search, etc. Sandbox /data/minio.
- Excel MCP (FileLock + versioning 10 + validation header + single worker thread-safety) - .
- Pricing Memory MCP (CUSTOM, pas officiel - 4 tools validés): get_chantier_price (historique prix moyen m2), detect_sous_chiffrage (-12% flag rouge 10k€/ligne), save_price_after_win, compare_pu_base_prix. Détecte sous-chiffrage ligne DPGF vs base prix Admin.

Décision finale: On prend Filesystem custom (fork sécurisé) + Excel custom + Pricing Memory custom. Memory MCP officiel non pris (risque fuite).

Host unique app/mcp/internal/host.py tourne thread FastAPI, pas process séparé + audit log middleware.

Technique pure MCP: Voir ENGINEERING-HANDBOOK section MCP_DOCS_V2 fusionnée.

---
## 6. Corrections Juridiques Critiques V6 (P0 — Bloquant Avant Production)

### 6.1 CCAG 2021 : Plafond Pénalités = 10% (Public) / 5% (Privé) / Sans Plafond (CCMI)

**Erreur V5 corrigée:** Le module Pénalités (7.2) citait un "plafond CCAG 5%" de manière universelle.

**Vérité juridique:**
- **CCAG Travaux 2021 (art. 19.2.1)** : plafond des pénalités de retard = **10%** du montant HT, avec seuil d'exonération de **1 000 €**
- **Marchés privés (NF P 03-001)** : plafond de **5%**
- **CCMI (contrats avec particuliers)** : pénalités de **1/3 000e par jour**, **sans plafond**

**Impact:** Sur un marché public de 800 k€, la différence entre 5% et 10% = 40 000 € de risque non détecté. Sur un CCMI de 200 k€, le plafond inexistant peut coûter 60 000 €.

**Correction intégrée:** Module 7.2 V6 détecte auto le type de marché via le RC (public/privé/CCMI) et applique le bon plafond + seuil d'exonération 1 000 € dans le calcul Garage.

### 6.2 Prix Abnormalement Bas (PAB) — Piège Mortel Ignoré

**Problème:** En France, si votre prix est inférieur de **20 à 30%** à l'estimation MOA ou à la moyenne des offres, vous êtes déclaré "anormalement bas". Vous devez justifier en 48h. Si vous ne pouvez pas = élimination ou négociation forcée à la baisse.

**Solution:** Module 7.16 — PAB Detector (voir §7.16).

### 6.3 Clauses Matériaux Post-Covid

**Problème:** Depuis 2021-2022, les CCAP intègrent des clauses spécifiques de révision des prix matériaux (acier, bois, cuivre, bitume) avec des formules propres, distinctes du BT01. Le module BT Index Guardian (7.1) ne détectait que les indices BT.

**Solution:** Module 7.17 — Matériaux & Rupture de Stock Shield (voir §7.17).

### 6.4 Avance Minimale 2024 & Retenue de Garantie

- **Avance minimale 2024** : 30% pour marchés État, 10% pour EPA >60M€ et collectivités >60M€ dépenses. Plus de plafond max depuis décret 2020, garantie facultative au-delà de 30%.
- **Retenue garantie** : max 5%, remplaçable par garantie à première demande ou caution personnelle et solidaire si acheteur ne s'y oppose pas.

**Correction:** Module 7.3 Trésorerie Simulator intègre ces seuils actualisés.

---


### 6.5 Stack Technique Simplifiée - Préservé V12 (SSoT technique voir ENGINEERING-HANDBOOK, ici synthèse préservée)

> Cette section est l'ancien §6 du RAPPORT V12, préservée intégralement pour respecter "Ne supprime RIEN". La vérité juridique nouvelle prime en §6.1 à §6.4 ci-dessus. Pour stack technique détaillé, voir aussi ENGINEERING-HANDBOOK et MANIFESTE, mais ce RAPPORT §6bis reste source fonctionnelle synthèse.


## 6. Stack Technique Simplifiée + Modèle Commercial (Synthèse - Détail Voir Handbook/Manifeste)

**Stack en une page :**
- Frontend: Next.js 15 + shadcn/ui + Tailwind + React Query - Wizard 12 étapes + Cockpit tuiles + Finance Warfare Dashboard 5 tuiles + Vault Dashboard + HANDOFF+ Dashboard
- Backend: FastAPI + SQLAlchemy single-tenant (0 tenant_id) + Postgres 16 + MinIO + Qdrant hybrid + Redis AOF + Celery worker + BGE-M3 + Mistral API EU + Docling worker séparé
- Garage Math: PuLP + OR-Tools + Decimal 28 + référentiels JSON data/referentiels/
- Infra: Docker Compose + OVH VPS 16/32Go + backup AES-256-GCM S3 + LVM snapshot + ClamAV EICAR + cosign verify
- MCP: 3 servers internes + BOAMP externe 3 tools
- Sécurité: JWT vps_id middleware + 2FA TOTP Argon2id + filesystem O_NOFOLLOW+fstat+BASE_ROOT non-symlink+owner + Excel FileLock + no LLM import mathbox + strip financier + Vault J-30 readonly cron continue + heartbeat whitelist 0 donnée métier

**Modèle Commercial - Formule Unique Entreprise (Synthèse, détail Voir MANIFESTE-):**
Formule Unique Entreprise: Paiement unique pas abonnement. Mise à jour 30s via Docker pull + backup auto. Prix: Modèle A Souverain VPS client OVH + Licence unique. Modèle B Infogéré assumé DPA art28 VPS dédié EU opéré éditeur avec DPA. Pas de SaaS mutualisé. Pas de % CA.

Argumentaire: Souveraineté + Vitesse objectif usage + Fiabilité objectif réduction élimination + Prix unique + UX 1 bouton + Conformité RGPD/AI Act.

---

---


## 7. SECTION COEUR — SPÉCIFICATIONS FONCTIONNELLES DÉTAILLÉES DES 28 MODULES — SOURCE UNIQUE ABSOLUE

> **RÈGLE CRITIQUE :** Cette section 7 est la SEULE définition fonctionnelle complète des 28 modules. Pour chaque module 7.1 à 7.28, une seule description complète avec Trigger, Entrées DCE, IA Qualitative ZERO €, Solver Garage Exact, Référentiels, Vue Salarié Sans €, Action Patron Avec €, Générateurs Output, Risque Si Non Détecté. Aucune duplication ailleurs. Autres docs citent "Voir RAPPORT section 7.X".


### 7.1 Module 7.1 — BT Index Guardian / Indice Inflation Piège (Le tueur de marge lente)

**Position dans workflow:** Analyse §3.3 étape 3 + cockpit Finance Warfare tuile 1.

**Problème terrain:** CCAP art 10-12 formule révision sans date base, sans butoir, indices BT01/BT06a mal choisis, prix fermes actualisables cachés. Marge fond 3% par an sans provision. Sur 24 mois chantier 800k€, perte -47k€ si BT01 +6% non provisionnée.

**Trigger:** Upload CCAP + CCTP + AE montant. Détection automatique présence clause prix révisable/ferme/actualisable. Si formule BT détectée, activation.

**Entrées DCE:**
- CCAP art 10-12 (formule révision, type prix, indices, date base, butoir)
- AE/BPU/DPGF montant HT total
- Planning durée mois extrait (ex: 18 mois)
- Vault A07 bilans (pour contexte trésorerie — quali seulement)

**IA Qualitative ZERO €:**
- Extrait via RAG: type prix (ferme, révisable, actualisable), formule complète OCR, indices mentionnés (BT01, BT06a, BT38...), date base (mois/year), présence butoir, clause sauvegarde.
- Classification risque: si prix ferme sans actualisation + durée >6 mois => Risque critique. Si formule sans date base => Non conforme. Si sans butoir + indices volatils => Risque élevé inflation.
- Output JSON quali: `{type_prix: "ferme actualisable", formule: "P=P0*0.15+0.85*BT01(m)/BT01(m0)", indices: ["BT01"], date_base: "2023-03", butoir: false, risque: "critique", page: 12, extrait: "...", confiance: 0.94}` ZERO CALCUL €.

**Solver Garage Mathématique Exact (bt_projection):**
- **Nom:** `bt_projection` — `app/engines/math_engine/bt_projection.py` — ZERO LLM import — scan bloquant.
- **Entrées:** formule, indices, date_base, durée_chantier_mois (18), montant_marche_ht Decimal.
- **Référentiel:** `data/referentiels/bt_indices_insee_36m.json` — BT01/BT06a/BT38 36 mois glissants source INSEE https://www.insee.fr dernière maj 2026-07-01.
- **Calcul:** Projection INSEE 3 scénarios: conservateur (moyenne glissante 12m + tendance linéaire), médian (régression 36m), pessimiste (p95 hausse 36m). Érosion marge exacte = montant_marche * (indice_projeté_fin - indice_base)/indice_base * coeff pondération formule (ex: 0.85). Decimal 28 to_decimal(str).
- **Output:** `{"periode": 18, "bt01_base": 125.3, "bt01_projete_18m_conserv": 132.1, "bt01_med": 133.8, "bt01_pess": 135.2, "erosion_conserv": -22300.00, "erosion_med": -38900.00, "erosion_pess": -47320.00, "provision_recommandee_pct": 8, "graph_data": [...]}`
- **Test:** test_5_solveurs_ vert + bt_projection INSEE exact.

**Référentiels utilisés:** bt_indices_insee_36m.json + INSEE API.

**Vue Salarié (Sans €):**
- Badge couleur: rouge "Risque Inflation Critique — Formule sans butoir" / orange "Risque modéré" / vert "Couvert".
- Texte quali: "CCAP art12: Prix fermes actualisables sans date base explicite. Durée 18 mois. Exposition inflation si BT01 +6%. Prévoir question MOE."
- Pas de montant €, pas de graph €, pas de provision visible.
- Pastille CCAP page 12 extrait.

**Action Patron (Avec €):**
- Finance Warfare Dashboard tuile 1 BT01 Projection: courbe INSEE 36m historique + projection 3 scénarios + zone érosion.
- Montants exacts: "Perte potentielle scénario pessimiste -47 320€ (5.9% marge) — Provision recommandée 8% soit 64 000€".
- Graph: érosion marge par mois.
- Checklist actions: Ajouter clause butoir, provisionner, question MOE "Confirmer date base BT01 et présence butoir 5%".
- Provision à valider checkbox + commentaire.

**Générateurs Output:** Finance Warfare tuile BT, Q/R tactique Q1 si risque critique, Mémoire Booster chapitre Risques.

**Risque si non détecté:** -30k€ à -80k€ marge fondue inflation sans recours.

---

### 7.2 Module 7.2 — Pénalités Detector / Cumuls Cachés (Le piège qui tue trésorerie)

**Problème:** Pénalités éparses CCAP/CCTP/Planning + pénalités cachées (absence réunion, retard DIUO, absence SOGED, retard levée réserves, absence DOE...). Cumul sans plafond ou plafond CCAG non rappelé. Exposition réelle 12% CA = 124k€.

**Trigger:** Upload CCAP + CCTP(s) + Planning + RC. Extraction regex pénalités.

**Entrées:** CCAP art pénalités, CCTP 00 généralités, CCTP lot pénalités particulières, Planning jalons, CCAG 2021 réf.

**IA Qualitative ZERO €:**
- Extrait toutes pénalités via RAG + regex: type (retard, absence réunion, absence PPSPS, absence SOGED, retard DOE/DIUO, retard levée réserve...), montant (x €/jour ou % ), plafond mentionné, base (par jour calendaire/ouvré).
- Catégorise 6 types: retard global, jalons intermédiaires, absence documents, absence réunions, hygiène sécurité, levée réserves.
- **V6 Correction:** Détection auto type de marché (public/privé/CCMI) pour appliquer bon plafond: CCAG 2021 public = 10% + seuil exonération 1 000€ / NF P 03-001 privé = 5% / CCMI = sans plafond 1/3000e.
- Détecte si plafond CCAG mentionné ou absent, si pénalités particulières cumulables.
- Output: `{"penalites": [{"type": "retard global", "montant": "500€/j cal", "plafond": "Non mentionné", "page": 15, "cumulable": true}, ...], "nb_cachees": 2, "plafond_cite": false, "type_marche": "public", "plafond_applicable": "10%"}`

**Solver Garage Exact (penalites_cumul):**
- Nom: `penalites_cumul.py`
- Calcul exposition max = somme (montant_jour * durée estimée retard moyen 10j) pour chaque pénalité sans plafond + plafond CCAG 10% public comparé (5% privé, ∞ CCMI).
- Si plafond absent: exposition = 124 500€ (12% marché) flag rouge.
- Provision recommandée = 10% exposition max si pas de clause plafonnement.
- Output: `{"exposition_max": 124500, "exposition_pct_marche": 12, "plafond_applicable": 80000, "depasse_plafond": true, "liste_sans_plafond": 3, "provision": 16000}`

**Vue Salarié:** Liste quali "6 pénalités détectées dont 2 cachées (page 22 absence réunion 150€/réunion, page 45 retard DIUO 200€/j). Risque plafond non cité. Badge rouge."
**Action Patron:** Barre exposition 124.5k€ vs plafond 80k€ (10% public) + liste sans plafond + provision 16k€ à valider + clause plafonnement générée "Les pénalités cumulées sont plafonnées à 10% du montant HT conformément CCAG 2021 art 19.2" (ou 5% NF P03-001 privé). Graph.

**Risque si non détecté:** 12% CA pénalités = cessation de paiement possible.

---

### 7.3 Module 7.3 — Trésorerie Simulator / BFR Warfare (Le tueur d'entreprise saine)

**Problème:** Avance 0% ou 5% sans caution, RG 5% sans caution, délai paiement 30j contractuel 60j réel, facturation mensuelle, retenue 5% + RG 5% = 10% immobilisé. Pic BFR -180k€ mois 4-6 + coût caution vs RG arbitrage.

**Trigger:** CCAP avance %, RG %, délai paiement, caution exigée.

**Entrées:** CCAP art avance, RG, caution, délais règlement, Planning facturation, DPGF total.

**IA Qualitative ZERO €:**
- Extrait: avance % (0/5/10/20/30), condition (caution à première demande?), RG % (5%), caution RG remplace RG?, délai paiement (30j contractuel), date début paiement.
- **V6:** Détection type acheteur (État 30% avance / Collectivité >60M€ 10% / privé variable).
- Détecte: avance sans caution = risque trésorerie, RG sans caution = immobilisation.
- Output quali: `{"avance": "5% sans caution", "rg": "5% sans caution remplaçable", "delai": "30j + 15j MOE", "risque": "BFR élevé M4-6", "type_acheteur": "collectivite"}`

**Solver Garage (treasury + treasury_bfr):**
- Calcul S-curve avancement: décaissement MO matériaux + encaissement factures - RG - avance remboursement.
- Pic BFR = -180 000€ mois 5 (calcul Decimal exact mensualisé).
- Coût caution vs RG: coût caution à première demande = montant * taux 1.2% vs coût immobilisation RG = montant * taux découvert 4% * durée/12. Arbitrage: caution 960€ vs 40 000€ immobilisés = gain trésorerie.
- Graph mensuel BFR.

**Vue Salarié:** "Trésorerie tendue M4-6 — Avance 5% sans caution — RG 5% non cautionnable — Courbe tension sans €"
**Action Patron:** Courbe BFR -180k€ pic + arbitrage caution 960€ vs 40k€ immobilisés + provision BFR à valider + planning facturation optimisé.

**Risque si non détecté:** BFR -180k€ = cessation de paiement entreprise saine.

---

### 7.4 Module 7.4 — GME Guardian / Solidarité Cachée (Le piège juridique qui engage au-delà du lot)

**Problème:** DC1/AE/CCAP groupement: conjoint vs solidaire, solidarité élargie extension au-delà lot (ex: mandataire solidaire des autres lots), répartition % non 100%, pièces manquantes, cotraitant sans Qualibat.

**Trigger:** Détection mot clé groupement, cotraitance, GME, mandataire dans AE/DC1/CCAP.

**Entrées:** DC1, AE, CCAP groupement, Vault A03 qualifications cotraitants (si fournis).

**IA Qualitative ZERO €:**
- Détecte: type groupement (conjoint / solidaire), clause solidarité élargie ("mandataire solidaire de l'ensemble des cotraitants y compris hors marché"), répartition % (ex: 60/30/10 = 100%?), pièces manquantes (DC2 cotraitant, attestations).
- Output: `{"type": "solidaire avec extension", "risque": "critique - solidarité au-delà lot", "repartition_ok": false, "pieces_manq": ["DC2 cotraitant 2"], "page": 8}`

**Solver Garage:** Contrôle cohérence 100% somme %, checklist pièces Vault (A01-A03) par cotraitant, calcul exposition = montant marché total si solidaire élargie.

**Vue Salarié:** Alerte juridique critique "Solidarité élargie détectée page 8 — Exposition hors lot — Vérifier répartition"
**Action Patron:** Exposition 180k€ (montant total marché solidaire) + DC1 corrigé + checklist sécurisation + clause à négocier + Q/R "Clarifier étendue solidarité art 3.2".

**Risque si non détecté:** Solidarité élargie 180k€ hors lot = faillite si cotraitant défaille.

---

### 7.5 Module 7.5 — DC4 Guardian Cascade / Plafond Sous-Traitance (Le piège qui fait dépasser 100%)

**Problème:** CCAP plafond sous-traitance 50% ou 70% ou 80%, rang DC4, cumul DC4 62% > plafond, sous-traitant sans Qualibat A03, sous-traitance en cascade non autorisée.

**Trigger:** CCAP clause sous-traitance + saisie salarié sous-traitants + montant sous-traité.

**Entrées:** CCAP plafond %, saisie salarié nom/nature/montant/rang sous-traitant, Vault A03 Qualibat sous-traitant, DPGF.

**IA Qualitative ZERO €:**
- Lit plafond %, identifie rang 1/2, détecte cascade (sous-traitant de sous-traitant).
- Output: `{"plafond": "50%", "cumul_actuel": "62%", "depasse": true, "cascade": false}`

**Solver Garage:** Contrôle cumul < plafond Decimal exact, calcul exact montant sous-traité, génération DC4 avec Vault A03 qualification + RIB.

**Vue Salarié:** Saisie nom/nature sous-traitant puis masquée après validation (plus visible). Badge "Plafond dépassé — Voir Admin".
**Action Patron:** Cumul 62% >50% + montant sous-traité + DC4 généré avec A03 + alerte bloquante si > plafond.

**Risque si non détecté:** >100% sous-traitance = rejet offre + amende 75k€.

---

### 7.6 Module 7.6 — RAT Amiante Analyzer / SS4 Provision (Le piège mortel chantier)

**Problème:** Bâtiment <1997 obligation RAT/RDTA Amiante/Plomb/Termites vs pièces jointes DCE. Si RAT absent et <1997 = suspicion amiante + provision SS4 + délai + SOP. Sans provision 18.5k€.

**Trigger:** Date permis bâtiment <1997 ou absence date + CCTP démolition + absence RAT dans DCE.

**Entrées:** CCTP démolition/curage, Diagnostics (PDF), Plans état existant, date bâtiment, Vault A10 SOP SS4, Vault A04 CACES amiante.

**IA Qualitative ZERO €:**
- Croise obligation RAT vs pièces jointes: si <1997 et RAT non joint => obligation.
- Détecte présence "amiante", "plomb", "pollution", "RAT", "DTA".
- Output: `{"bat_avant_1997": true, "rat_joint": false, "obligation": "RAT + RDTA avant travaux", "risque": "critique - SS4 obligatoire", "page_obligation": 5}`

**Solver Garage (amiante_ss4):**
- Calcul provision SS4 = Surface_saisie_sal * Ratio référentiel amiante €/m2. Ex: 100m2 * 185€ = 18 500€ + aléa 20% + délai 3 sem + coût formation.
- Référentiel: ratios_amiante_ss4.json {curage_léger 85€/m2, curage_lourd 185€/m2, démolition 250€/m2}

**Vue Salarié:** "RAT manquant — Saisir surface concernée m2 — Obligation SS4"
**Action Patron:** Provision 18 500€ + délai + SOP SS4 Vault A10 + PPSPS amiante + question MOE "Merci confirmer RAT joint ou prévoir RDTA avant travaux + délais d'accès".

**Risque si non détecté:** Amiante sans SS4 = arrêt chantier + amende 75k€ + risque pénal patron.

---

### 7.7 Module 7.7 — SOGED REP Tracker / Déchets — Ecoulement REP (Le coût caché qui double)

**Problème:** CCTP obligation SOGED/PEMD/Diagnostic déchets + REP PMCB depuis 2023 + 7 flux tri + exutoires + traçabilité. Coût tri+transport+exutoire-REP = 4.2k€ non provisionné classique.

**Trigger:** CCTP démolition/gros œuvre + mots SOGED, PEMD, déchets, REP, PMCB.

**Entrées:** CCTP, Métré salarié m2 cloison/voile/sol, Photos, Vault A09 FDES, Vault A10 modèle SOGED, saisie exutoires salarié.

**IA Qualitative ZERO €:**
- Détecte obligation SOGED/PEMD/Diagnostic Produit Matériaux Déchets, obligation REP PMCB, 7 flux.
- Output: `{"soged_oblig": true, "pemd_oblig": true, "rep": true, "flux": 7}`

**Solver Garage (rep_cost — ADEME):**
- Formule: Coût réel = Σ (Poids_kg * (tri €/kg + transport €/kg + exutoire €/kg - reprise_REP_bois/métal €/kg))
- Poids = Surface_métré * ratio_kg_m2 référentiel ADEME. Ex: BA13 cloison 72/48 ratio 12kg/m2 dont 70% plâtre 10% métal 20% inerte.
- Référentiel data/referentiels/ratios_ademes_dechets.json + prix_defaut tri/transport/exutoire/reprise REP.
- Output: 4 200€ ventilation par flux + SOGED généré auto avec exutoires + bordereau.

**Vue Salarié:** "Obligation SOGED 7 flux — Saisir exutoire + distance km — SOGED à générer"
**Action Patron:** Coût 4 200€ détaillé + SOGED généré + preuve factures + provision + FDES A09.

**Risque si non détecté:** 75k€ amende REP non conforme + chantier bloqué.

---

### 7.8 Module 7.8 — Site Contraintes Check / Visite Site (Le temps que personne ne chiffre)

**Problème:** CCTP 00 site occupé (hôpital/EHPAD/école = +15% MO), accès <3m ou impossible nacelle <1.5m +10-18% MO, hauteur >4m +20%, stockage impossible +8%, horaires restreints 8h-12h +12%, centre-ville dense +10%, bruit <70dB +5%. Temps perdu 2.5h/j non provisionné = 18k€ + 2 semaines.

**Trigger:** CCTP 00 contraintes site + visite obligatoire + Photos salarié + notice site.

**Entrées:** CCTP 00, notice contraintes, photos terrain upload salarié, saisie salarié case à cocher 7 contraintes, Vault A08 photos chantier similaire.

**IA Qualitative ZERO €:**
- Détection NLP contraintes site occupé, accès, hauteur, stockage, horaires, centre-ville, bruit.
- Output: `{"site_occupe": "hôpital - badge critique", "acces": "<3m", "hauteur": ">4m", "coeffs": ["+15% occupé", "+10% accès"]}`

**Solver Garage (site_coeff):**
- Formule: temps_corrige = temps_base * (1 + sum(coeffs actifs)). Coeffs référentiel data/referentiels/coeffs_site_contraintes.json.
- Ex: site occupé hôpital 0.15 + accès difficile <3m 0.10 + hauteur sup 4m 0.20 = 0.45 => +45% MO.
- Impact financier = temps_sup * taux horaire moyen DPGF (base prix Admin).
- Output: Impact 18k€ + 2 semaines délai.

**Vue Salarié:** "+2.5h/j — Site occupé hôpital — Accès impossible + Badge — Photos à l'appui"
**Action Patron:** Impact 18k€ + 2 sem + détail coeff + planning ajusté + provision site à valider + photo pastillée + question MOE moyens levage.

**Risque si non détecté:** +53% MO non provisionné = -18k€ + litige retard.

---

### 7.9 Module 7.9 — Cross-Check CCTP-DPGF-Plans / Incohérences & Oubli (La marge qui s'évapore)

**Problème:** Triple incohérence: CCTP dit 120m2 BA13 hydrorésistant, DPGF 80m2 BA13 standard, Plans 135m2 cloisons. 4 portes vues plan RDC non chiffrées DPGF. Marques imposées sans équivalent R2111-7 CCP (ex: "Porte DALH 45 référence X sans équivalent") = illégal + piège.

**Trigger:** Présence CCTP + DPGF/BPU Excel + Plans PDF.

**Entrées:** CCTP lot, DPGF Excel parsed ligne/ligne Qté/PU, Plans PDF parcellaire comptage portes/fenêtres/surfaces AI vision, Vault base prix PU moyens.

**IA Qualitative ZERO €:**
- Triple compare: extraction quantités CCTP vs DPGF vs Plans via AI vision comptage + NLP.
- Détecte: oublis (porte vue plan non chiffrée DPGF), écarts >2%, marques sans équivalent R2111-7.
- Output: `{"incoherences": [{"lot": "Cloisons", "cctp": "120m2 hydro", "dpgf": "80m2 std", "plans": "135m2", "ecart": "40%"}, {"oublis": "4 portes RDC vues plan non DPGF"}], "marques_sans_equivalent": 1}`

**Solver Garage (incoherence_solver):**
- Provision omission = Qté lue sur plan * PU moyen base prix Admin. Ex: 4 portes * 450€ = 1 800€.
- Calcul total écarts = Σ écart_qté * PU moyen.
- Seuil >2% déclenche provision.

**Vue Salarié:** "Incohérence: 4 portes RDC non chiffrées DPGF — CCTP 120m2 vs DPGF 80m2 vs Plans 135m2 — Pastille plan"
**Action Patron:** Provision omission 3 100€ + total écarts 18.2k€ + Question R2111-7 générée "Confirmer absence référence marque impérative contraire R2111-7 CCP ou accepter équivalent" + Q/R tactique.

**Risque si non détecté:** Oubli + marques illégales = litige + perte marge directe.

---

### 7.10 Module 7.10 — Assistant Questions-Réponses MOE/MOA Tactique (L'arme juridique qui sécurise)

**Problème:** 48h avant date limite questions = dernière chance neutraliser pièges ou créer trace écrite pour futur mémoire en réclamation.

**Trigger:** Date limite questions -48h (calcul date RC) + agrégation alertes rouges modules 7.1 à 7.9.

**Entrées:** Tous pièges rouges/oranges 7.1-7.9 + pages/extraits + montants totaux enjeu + CCAP/CCTP pages + Vault A10 jurisprudence.

**IA Qualitative ZERO € (Moteur templating juridique, pas Garage €):**
- Agrège 9 modules en 8 questions max (limite Profil Acheteur), triées par enjeu € décroissant.
- Rédaction opposable langage MOE/MOA non agressif mais verrouillant: "Il semble que... Pourriez-vous confirmer... Dans l'affirmative, ... Dans la négative, ...".
- Chaque question vise: soit faire neutraliser piège (ex: ajouter butoir BT01), soit créer trace écrite pour futur mémoire réclamation (ex: "Nous notons absence RAT malgré obligation").
- Référence exacte page/paragraphe.
- Output: DOCX 8 questions max avec enjeu € par question.

**Solver Garage:** Aucun €, mais moteur templating tri enjeu € décroissant + numérotation.

**Vue Salarié:** "7 questions générées — Relecture technique — Ajuster vocabulaire métier — Vérifier faisabilité"
**Action Patron:** Validation juridique + enjeu total 288k€ détaillé par question (Q1 192k€ solidarité, Q2 47k€ BT...) + Export DOCX/PDF prêt à déposer sur Profil Acheteur + bouton Dépôt. Chaque question = arme future mémoire réclamation.

**Risque si non détecté:** Sans Q/R pièges non neutralisés = perte 288k€.

---

### 7.11 Module 7.11 — Moteur Génération Mémoire Technique Booster 18/20 (Le tueur de concurrence)

**Objectif:** Générer mémoire noté 18/20, pas 12/20. Zéro copier-coller générique.

**Trigger:** Passage workflow MEMOIRE + Vault A01-A12 complet + Métré + Site contraintes + ADN Extractor 50 contraintes.

**Entrées:** RC pondération critères (Valeur technique 60% Prix 40%...), Vault A08-A10, ADN 50 contraintes CCTP, Métré temps corrigé, Site contraintes, Référentiels Météo France/INSEE/ADEME.

**5.1 Ingestion ADN Local et Contraintes CCTP:**
IA extrait 50 contraintes spécifiques CCTP (ex: "bruit <45dB chantier école occupé", "poussière <10mg/m3", "distance agence-chantier 12km", "accès <2.5m", "HSP 3.2m", "RE2020", "délai 18 mois dont 2 mois hiver..."). Injection données locales: distance agence-chantier calculée via adresse chantier vs siège, nom conducteur chantier, spécificités climatiques commune (pluie/neige). Mémoire répond point par point contrainte => preuve écoute CCTP, pas générique.

**5.2 Injection Preuves Matérielles Vault A08-A10:**
Pour chaque affirmation "Nous maîtrisons coulage béton en site occupé", moteur va chercher automatiquement dans Vault A08 photo chantier similaire géolocalisée <50km avec EXIF + légende + date + PV + attestation. Insertion auto dans mémoire avec légende "Chantier EHPAD Saint-Martin 2024 à 18km — Coulage voile site occupé — PV 12/04/2024". Preuve matérielle notée 18/20 vs concurrent générique "Nous maîtrisons..." sans preuve.

**5.3 Planning Gantt sous Contraintes Intempéries Régionales — Garage OR-Tools:**
Entrées: durée tâches saisie Salarié, calendrier, DTU délais séchage/cure béton. Garage récupère historique Météo France sur 10 ans pour département via `meteo_france_intemperies_10ans.json` (jours intempéries moyens par mois) et intègre marge. Génère Gantt avec marge intempéries crédible + chemin critique + jalon. Sortie PNG + MS Project .mpp. Mémoire chapitre Planning crédible vs concurrent planning lisse irréaliste.

**5.4 Volet Environnemental RE2020, FDES & SOGED:**
Génère chapitre environnemental à partir Vault A09 (ISO 14001, FDES perso, bilan carbone) + module 7.7 SOGED. Insère FDES produits, calcul empreinte, gestion déchets 7 flux, charte chantier propre, bilan carbone calculé. Conforme RE2020.

**5.5 Matrice de Conformité RC:**
Génère tableau conformité critère par critère RC (Valeur technique 60% décomposée: 20% moyens humains, 15% moyens matériels, 15% méthode, 10% environnement... Prix 40%). Renvoi page par page mémoire. Permet MOE de noter sans effort = note maximale.

**RBAC:** Salarié rédige commente 80% auto sans prix. Admin verrouille + ajoute marge + graph + validation.

**Output:** Mémoire 40-60 pages DOCX/PDF + Gantt PNG + MS Project + FDES annexes.

**Risque si non détecté:** Mémoire générique 12/20 = perdu.

---

### 7.12 Module 7.12 — HANDOFF+ Book de Démarrage Chantier (Le pont entre AO et exécution — Double Artefact Étanche)

**Trigger:** Passage statut AO de "En attente" à "Gagné / Attribué" par Admin uniquement. Irréversible salarié.

**7.12.1 Structure du Book de Démarrage PDF Interactif 30 pages généré en 2 secondes:**
- Page 1: Fiche identité marché, contacts MOA/MOE/CSPS/bureau contrôle, montant HT, délais, jalons, cautions.
- Page 2: DPGF annoté de guerre: chaque ligne contient commentaires Salarié ("Attention: accès nacelle impossible prévoir échafaudage — Saisie étape 5") mais SANS prix (expurgé) / AVEC prix complet (version complète).
- Page 3-5: Risques résiduels validés par Patron liste qualitative sans montants (expurgé) / avec montants provisions (complet).
- Page 6-10: Plans avec pastilles d'alerte (amiante SS4 zone, accès <3m, hauteur >4m, SOGED benne, oublis DPGF 4 portes).
- Page 11-15: Kit Administratif: DC4 sous-traitants validés, modèles situation travaux, OS types, planning Gantt avec intempéries, PPSPS pré-rempli Vault A10 + SS4 si RAT, SOGED avec exutoires, DICT.
- Page 16-20: Mémoire technique version chantier + SOGED + DOE modèle + ATT modèle + RAG historique chantiers similaires <50km.
- Annexes: Vault A01-A12 extraits utiles chantier.

**7.12.2 Gestion des Vues Restreintes — Double Artefact Physiquement Distinct (Étanchéité):**
Deux PDFs générés physiquement séparés sur filesystem distinct, pas un seul PDF avec masquage JS (fuite possible).
- `BOOK_CHANTIER_COMPLET_ADMIN.pdf`: Avec marges, provisions, BFR, coût caution, temps corrigé financier, PU, coeff vente, marge nette. Stocké coffre-fort Admin /data/minio/admin/ — seul Admin peut télécharger. Audit log accès.
- `BOOK_CHANTIER_EXECUTION_SALARIE.pdf`: Sans aucune donnée €, sans marge, sans provisions. Risques qualitatifs uniquement ("Présence amiante possible zone X — Porter EPI — Voir SOP SS4"). DPGF sans PU, sans total, uniquement commentaires qualitatifs. C'est celui reçu par Conducteur de Travaux. L'étanchéité garantie par génération 2 artefacts séparés + test `test_handoff_double_artefact.py` scan regex € = 0 occurrence + test `test_handoff_irreversible.py` seul Admin déclenche.

Frontend: test_front_no_handoff_leak.spec.ts vérifie conducteur ne peut pas deviner URL admin.

**Risque si non détecté:** Conducteur voit marge = fuite = mort entreprise.

---

### 7.13 Module 7.13 — A / Deadline Guardian (Le gardien de l'horloge)

**Problème terrain:** 40% des éliminations digitales = dépôt après l'heure. Horodatage plateforme (Profil Acheteur, PLACE, BOAMP) fait foi. 1 minute après = mort. Offre hors délai éliminée sans recours.

**Trigger:** Import DCE depuis BOAMP/PLACE ou upload manuel. Extraction auto de la date limite de dépôt dans le RC.

**Entrées DCE:**
- RC: date limite de dépôt, heure limite, fuseau horaire plateforme (CET/CEST)
- Vault A01-A06: état de validité (J-30, J-7, EXPIRE)
- Liste pièces obligatoires par type de marché (public/privé/MAPA/CCMI)

**IA Qualitative ZERO €:**
- Extraction date/heure limite + fuseau horaire plateforme vs local
- Détection type de marché pour définir la liste des pièces obligatoires
- Vérification cohérence: si date limite < J+7 et Vault A01-A06 expirent avant = alerte rouge critique
- Output: `{"date_limite": "2026-09-15T17:00:00+02:00", "fuseau_plateforme": "CEST", "fuseau_local": "CEST", "jours_restant": 12, "pieces_obligatoires": ["DC1", "AE", "Mémoire", "DPGF"], "vault_expire_avant_limite": ["A02 Assurance"], "risque": "critique"}`

**Solver Garage:** Aucun calcul €. Logique temporelle et checklist.

**Vue Salarié:**
- Compte à rebours visuel: J-7, J-2, J-1, H-4, H-1 avec alertes SMS/email/push
- Checklist pièce par pièce: chaque document uploadé = case verte. Rouge = manquant
- Badge bloquant: "Dépôt bloqué — A02 Assurance expire le 10/09, avant la date limite 15/09"
- Bouton dépôt désactivé tant que checklist rouge ou Vault expire

**Action Patron:**
- Dashboard "Mes AO en cours" avec compte à rebours par projet
- Alerte si salarié tente de déposer avec pièce manquante = blocage + notification Admin
- Historique des dépôts: date/heure réelle, pièces déposées, confirmation plateforme

**Générateurs Output:** Checklist dépôt PDF, confirmation horodatée, alertes calendrier (ICS export)

**Risque si non détecté:** Dépôt 1 minute en retard = 0€ + 40h perdues. Pièce manquante = élimination immédiate.

---

### 7.14 Module 7.14 — B / Alloti Guardian (Le détecteur de lots pièges)

**Problème terrain:** Marché alloti, 5 lots. Vous répondez au lot 1 avec le mémoire du lot 2 = 0€. Vous oubliez le lot 3. Vous copiez-collez le même mémoire sur 2 lots sans adapter = élimination technique.

**Trigger:** Détection mot "alloti", "lots", "coupes" dans le RC. Ou présence de plusieurs CCTP numérotés (CCTP Lot 1, CCTP Lot 2...).

**Entrées DCE:**
- RC: nombre de lots, pondération par lot, critères par lot
- CCTP par lot: descriptif, quantités, contraintes spécifiques
- AE: montant par lot (si fourni)

**IA Qualitative ZERO €:**
- Détection auto "marché alloti" et nombre de lots
- Extraction des critères techniques par lot (ex: Lot 1 GO — valeur technique 40%, Lot 2 Peinture — valeur technique 20%)
- Détection du "lot piège": critères très exigeants mais prix très bas = lot de référence pour noter les autres (ne pas y répondre agressivement)
- Output: `{"nb_lots": 5, "lots": [{"num": 1, "nature": "Gros Oeuvre", "valeur_tech_pct": 40, "montant_estime": 400000, "lot_piege": false}, {"num": 2, "nature": "Peinture", "valeur_tech_pct": 10, "montant_estime": 45000, "lot_piege": true}], "recommandation": "Lot 2 = lot piège. Ne pas chiffrer agressivement."}`

**Solver Garage:** Aucun calcul €. Logique de pondération et de stratégie de réponse.

**Vue Salarié:**
- Interface séparée par lot: chaque lot = un wizard séparé, un mémoire séparé, ses propres pièges
- Badge par lot: vert (prêt), orange (en cours), rouge (piège détecté)
- Alerte si même mémoire détecté sur 2 lots = "Mémoire du lot 1 détecté dans lot 2 — Adapter obligatoire"

**Action Patron:**
- Vue globale des 5 lots avec progression % par lot
- Décision stratégique: "Ne pas répondre au lot 3 (trop risqué)" ou "Chiffrer lot 2 en référence"
- Génération des 5 mémoires séparés + 5 DPGF + 5 DC1

**Générateurs Output:** 5 mémoires DOCX, 5 DPGF Excel, 5 DC1 pré-remplis, tableau stratégie lots

**Risque si non détecté:** Mémoire lot 1 dans lot 2 = élimination technique immédiate. Lot piège mal chiffré = marge négative.


### 7.15 Module 7.15 — C / RSE & Clause Sociale Booster (+15% de note)

**Problème terrain:** Les acheteurs publics pondèrent la RSE (environnement, insertion sociale, égalité pro) à **10-15%** de la note finale, avec un minimum de 10% pour le critère insertion. Les entrepreneurs BTP ignorent cette clause ou la remplissent à la va-vite. Résultat: -1,5 à -3 points sur 20 = élimination ou 3ème place.

**Trigger:** Détection dans le RC de "RSE", "clause sociale", "insertion", "égalité professionnelle", "environnement", "bilan carbone", "RE2020".

**Entrées DCE:**
- RC: pondération RSE (10-15%), critères détaillés (insertion, environnement, égalité)
- CCAP: clause insertion (nb heures, type public, structure partenaire), matériaux bas carbone
- Vault A09: ISO 14001, MASE, charte diversité, FDES
- Vault A10: partenariats structures insertion, historique heures insertion

**IA Qualitative ZERO €:**
- Extraction de la pondération RSE et des sous-critères
- Détection de la clause insertion: nb heures, type de public (jeunes, seniors, RSA...), % en CDI, structure partenaire exigée
- Détection exigences RE2020: bilan carbone, performance énergétique, matériaux bas carbone
- Output: `{"rse_ponderee": 15, "insertion_heures": 500, "insertion_public": "jeunes <26 ans", "insertion_cdi_pct": 35, "re2020_exige": true, "environnement_pct": 5, "risque": "orange si Vault A09 incomplet"}`

**Solver Garage:**
- Calcul faisabilité insertion: `heures_realisables = effectif_moyen * 6.5h/j * 20j/mois * duree_mois * taux_insertion_historique`
- Alerte si `heures_realisables < heures_exigees`: "Clause intenable — 500h exigées, 320h réalisables dans votre zone"
- Calcul pénalité insertion: `penalite = (heures_manquantes * 2 * SMIC_horaire)`
- Ex: 180h manquantes * 2 * 11.65€ = 4 194€ de pénalité

**Vue Salarié:**
- Badge "RSE 15% de la note — Chapitre à rédiger"
- Saisie simplifiée: nb heures insertion prévues, partenaire structure, % matériaux bas carbone
- Alerte si Vault A09 incomplet: "ISO 14001 manquant — Note RSE impactée"

**Action Patron:**
- Dashboard RSE: score prévisionnel sur 20 (ex: "Votre RSE actuelle = 6/20 — Manque ISO 14001 + partenaire insertion")
- Génération auto chapitre RSE dans le mémoire avec preuves Vault
- Calcul pénalité insertion: "500h exigées — 320h réalisables — Pénalité potentielle 4 194€ — Négocier clause ou trouver partenaire"
- Génération RE2020: bilan carbone chantier, FDES matériaux, charte chantier propre

**Générateurs Output:** Chapitre RSE DOCX (5-8 pages), bilan RE2020 PDF, tableau insertion Excel, liste partenaires insertion locaux

**Risque si non détecté:** -3 points sur 20 = passage de 1er à 3ème sur 1,2M€. Pénalité insertion 4 000€+ non prévue.

---

### 7.16 Module 7.16 — D / Prix-Mémoire Coherence Check (Le détecteur de mensonge)

**Problème terrain:** Votre mémoire promet 6 ouvriers + 2 grues + planning serré. Votre DPGF est à 35€/h. Les évaluateurs (souvent d'anciens conducteurs de travaux) voient immédiatement que c'est irréaliste. Résultat: note technique qui chute, ou pire, déclaration de PAB (Prix Abnormalement Bas).

**Trigger:** Présence mémoire technique + DPGF/BPU. Calcul auto après génération mémoire et chiffrage.

**Entrées DCE:**
- Mémoire technique: moyens humains déclarés (nb ouvriers, compagnons, chef de chantier), moyens matériels (grues, nacelles, camions), planning déclaré
- DPGF/BPU: prix unitaires MO, matériaux, matériel
- Vault base prix: taux horaire moyen par métier, coût matériel/jour

**IA Qualitative ZERO €:**
- Extraction mémoire: "6 ouvriers + 2 grues + 1 chef de chantier sur 6 mois"
- Extraction DPGF: poste MO à 35€/h, poste matériel à 120€/j
- Output: `{"moyens_humains_memoire": {"ouvriers": 6, "chef": 1, "duree_mois": 6}, "moyens_materiels_memoire": {"grues": 2, "duree_mois": 6}, "cout_mo_dpgf": 35, "cout_materiel_dpgf": 120, "coherence": "faible"}`

**Solver Garage:**
- Calcul coût réel mémoire: `cout_memoire = (6 ouvriers * 35€/h * 8h * 20j * 6mois) + (1 chef * 45€/h * 8h * 20j * 6mois) + (2 grues * 120€/j * 20j * 6mois)`
- Comparaison avec DPGF total: `ratio = cout_memoire / dpgf_total`
- Alerte si ratio > 60%: "Mémoire irréaliste — Vos moyens coûtent 60% du prix total, il reste 40% pour matériaux et marge = impossible"
- Score cohérence: "Crédible / Surévalué / Sous-évalué / Irréaliste"

**Vue Salarié:**
- Badge "Mémoire vs DPGF — Vérifier cohérence"
- Message quali: "Votre mémoire déclare 6 ouvriers sur 6 mois — Vérifiez que le prix couvre ces moyens"
- Pas de montant €, pas de ratio chiffré

**Action Patron:**
- Dashboard cohérence: "Mémoire vs DPGF = 62% — IRRÉALISTE"
- Détail calcul: "MO mémoire = 201 600€ + Matériel = 28 800€ = 230 400€. DPGF total = 380 000€. Reste 149 600€ pour matériaux + marge. Taux de marge nécessaire = 39% sur le reste. Ajustez mémoire ou prix."
- Recommandation: "Réduire mémoire à 4 ouvriers OU augmenter DPGF de 15%"

**Générateurs Output:** Rapport cohérence PDF, recommandations ajustement mémoire/DPGF

**Risque si non détecté:** Note technique 6/20 au lieu de 15/20 = perdu. Déclenchement PAB = élimination ou négociation forcée.

---

### 7.17 Module 7.17 — E / Variante Guardian (Le maître des variantes)

**Problème terrain:** Le RC autorise une variante. Vous proposez la variante (plus rapide, moins chère) mais vous oubliez de répondre à la solution de base. Résultat: irrégularité = élimination.

**Trigger:** Détection dans le RC de "variante autorisée", "variante acceptée", "proposition alternative".

**Entrées DCE:**
- RC: clause variante (autorisée/interdite), conditions (base obligatoire + variante en complément)
- Mémoire technique: détection de 2 versions (base + variante)

**IA Qualitative ZERO €:**
- Détection auto "variante autorisée" dans le RC
- Extraction conditions: "La variante doit être accompagnée de la réponse de base" / "Variante seule autorisée"
- Output: `{"variante_autorisee": true, "base_obligatoire": true, "variante_detectee_memoire": false, "base_detectee_memoire": true, "risque": "critique — variante sans base"}`

**Solver Garage:** Aucun calcul €. Logique documentaire.

**Vue Salarié:**
- Wizard variante: "Variante autorisée détectée — Réponse de base obligatoire ? OUI / NON" + "Variante proposée ? OUI / NON"
- Alerte si variante proposée sans base: "🔴 IRRÉGULARITÉ — Variante sans réponse de base = Élimination"
- Interface séparée: onglet "Base" + onglet "Variante"

**Action Patron:**
- Vérification avant dépôt: "Enveloppe Offre = Mémoire Base + Mémoire Variante + DPGF Base + DPGF Variante"
- Génération de deux mémoires séparés: base + variante
- Vérification que les deux sont déposés dans le bon ordre (base d'abord, variante en annexe)

**Générateurs Output:** 2 mémoires DOCX (base + variante), 2 DPGF Excel, checklist dépôt variantes

**Risque si non détecté:** Variante sans base = irrégularité = élimination immédiate sur 400k€+.

---

### 7.18 Module 7.18 — F / Matériaux & Rupture de Stock Shield (Le bouclier post-Covid)

**Problème terrain:** Clause prix ferme sur 18 mois + acier +40% en 2022 = faillite. Ce n'est pas du BT01, c'est une clause spécifique "matériaux" avec révision propre (acier, bois, cuivre, bitume, ciment).

**Trigger:** Détection dans le CCAP de clauses "révision prix matériaux", "index matériaux", "acier", "bois", "cuivre", "bitume", "ciment" + formule de révision.

**Entrées DCE:**
- CCAP art prix: clause matériaux spécifique, indices matériaux (acier, bois, cuivre, bitume, ciment, aluminium)
- DPGF: part des matériaux dans le prix total par lot
- Planning: durée chantier

**IA Qualitative ZERO €:**
- Détection auto des clauses "révision prix matériaux" distinctes du BT01
- Extraction des matériaux indexés: acier, bois, cuivre, bitume, ciment, aluminium
- Détection formule propre: ex "Pmat = P0 * (Indice Acier n / Indice Acier 0)"
- Output: `{"matériaux_indexes": ["acier", "bois"], "formule_acier": "P=Po*IndiceAcier(n)/IndiceAcier(0)", "date_base_acier": "2024-01", "prix_ferme": true, "risque": "critique — acier non protégé sur 18 mois"}`

**Solver Garage:**
- Calcul perte matériaux: `perte = montant_materiaux * variation_indice_materiau * duree_mois / 12`
- Ex: acier 150 000€ * +40% * 18/12 = 90 000€ de perte
- Comparaison avec BT01: "BT01 prévoit +6% — Votre clause acier prévoit +40% = écart 34% non couvert"
- Alerte si prix ferme sans clause matériaux sur marché > 6 mois

**Vue Salarié:**
- Badge "Clause matériaux détectée — Acier indexé — Vérifier protection"
- Message quali: "CCAP §14 prévoit révision acier — Confirmer que votre prix couvre cette variation"
- Pas de montant € de perte

**Action Patron:**
- Dashboard matériaux: "Acier indexé — Variation potentielle +40% sur 18 mois = Perte 90 000€"
- Simulation par matériau: acier, bois, cuivre, bitume avec leurs indices propres
- Recommandation: "Négocier clause révision acier OU provisionner +25% sur poste acier"
- Génération Q/R: "Demander clause de révision acier avec index INSEE acier BTP"

**Générateurs Output:** Simulation matériaux PDF, Q/R matériaux DOCX, alerte matériaux dashboard

**Référentiels:** indices_matériaux_insee.json (acier, bois, cuivre, bitume, ciment, aluminium — 36 mois glissants)

**Risque si non détecté:** Acier +40% sur 800k€ = perte 90 000€. Bois +30% = perte 45 000€.

---

### 7.19 Module 7.19 — G / PAB Detector (Prix Abnormalement Bas)

**Problème terrain:** Votre prix est 25% en dessous de l'estimation MOA. Vous êtes déclaré "anormalement bas". Vous devez justifier en 48h. Si vous ne pouvez pas = élimination ou négociation forcée à la baisse. Les entrepreneurs "cassent les prix" sans savoir ce risque.

**Trigger:** Après chiffrage DPGF/AE. Comparaison avec estimation MOA et base prix historique.

**Entrées DCE:**
- DPGF/AE: prix total HT, prix au m2 par poste
- Base prix SMART_AO: historique prix m2 par type de chantier, département, année
- RC: estimation MOA (si mentionnée), fourchette attendue

**IA Qualitative ZERO €:**
- Estimation prix moyen attendu par le MOA: basée sur base prix historique SMART_AO + estimation MOA
- Comparaison: `ecart_pct = (prix_propose - prix_moyen) / prix_moyen`
- Output: `{"prix_propose": 380000, "prix_moyen_estime": 520000, "ecart_pct": -27, "risque_pab": "critique", "seuil_pab": -20}`

**Solver Garage:**
- Calcul risque PAB: si écart < -20% = alerte orange. Si écart < -30% = alerte rouge critique.
- Estimation marge minimum viable: `marge_min = prix_propose * 0.06` (6% marge nette minimum BTP)
- Si marge estimée < 6% + écart > -25% = "Double risque: PAB + marge insuffisante"

**Vue Salarié:**
- Badge "Prix à vérifier — Risque anormalement bas"
- Message quali: "Votre prix est significativement en dessous de la fourchette habituelle — Préparez une justification"
- Pas de montant € de l'estimation, pas de pourcentage chiffré

**Action Patron:**
- Dashboard PAB: "Prix proposé 380 000€ — Moyenne estimée 520 000€ — Écart -27% — RISQUE PAB ÉLEVÉ"
- Génération note de justification économique: achats groupés, optimisation process, matériaux alternatifs, sous-traitance compétitive, savoir-faire spécifique
- Alerte si écart < -30%: "Risque élimination PAB quasi-certain — Augmenter prix ou préparer justification solide"
- Simulation: "Si prix à 450 000€ (-13%) = risque PAB faible, marge 8% = viable"

**Générateurs Output:** Note justification PAB DOCX (3-5 pages), simulation prix PDF, alerte PAB dashboard

**Risque si non détecté:** Élimination PAB = 0€ + 40h perdues. Négociation forcée = perte 50 000€ à 100 000€ de marge.

---

### 7.20 Module 7.20 — H / Attestation de Visite Auto (Le visiteur virtuel)

**Problème terrain:** Le RC exige une "visite des lieux obligatoire" à une date précise. Vous ne voyez pas la clause. Vous ne vous présentez pas. Ou vous y allez mais vous perdez l'attestation. Élimination.

**Trigger:** Détection dans le RC de "visite des lieux obligatoire", "visite préalable obligatoire", "visite obligatoire".

**Entrées DCE:**
- RC: date et heure de la visite, lieu de rendez-vous, contact MOA
- CCTP: contraintes site à vérifier lors de la visite

**IA Qualitative ZERO €:**
- Détection auto dans le RC: "visite des lieux obligatoire"
- Extraction date, heure, lieu, contact
- Output: `{"visite_obligatoire": true, "date_visite": "2026-08-10T09:00:00", "lieu": "Chantier 12 rue de la Paix", "contact_moa": "M. Dupont 06 12 34 56 78", "attestation_requise": true, "jours_restants": 8}`

**Solver Garage:** Aucun calcul €. Logique calendaire et checklist.

**Vue Salarié:**
- Alerte calendrier: "Visite obligatoire le 10/08 à 9h — 12 rue de la Paix — Contact M. Dupont"
- Rappel J-1, H-2
- Upload photo géolocalisée sur site = preuve de visite (GPS, timestamp intégré EXIF)
- Checklist visite: contraintes à vérifier (accès, HSP, stockage, bruit...)

**Action Patron:**
- Génération modèle attestation de visite pré-rempli: nom entreprise, date, adresse, MOA, signature
- Vérification photo GPS: coordonnées vs adresse chantier = validation auto
- Blocage dépôt si attestation de visite manquante: "Dépôt bloqué — Attestation de visite requise"
- Historique visites: date, photos, compte-rendu, coordonnées GPS

**Générateurs Output:** Attestation visite PDF pré-remplie, compte-rendu visite DOCX, photos géolocalisées ZIP

**Risque si non détecté:** Visite manquante = élimination immédiate. Attestation perdue = élimination si contestée.

---

### 7.21 Module 7.21 — I / Candidature vs Offre Separator (Le trieur de 47 pièces)

**Problème terrain:** 47 pièces à trier. Vous mettez le DC1 (candidature) dans l'enveloppe offre = irrégularité. Ou vous mettez le mémoire technique dans l'enveloppe candidature = élimination. Le tri est manuel, stressant, et fait à 23h le vendredi.

**Trigger:** Upload des 47 pièces DCE. Détection auto du type de marché (public/privé/MAPA/CCMI) pour définir les enveloppes requises.

**Entrées DCE:**
- RC: type de procédure (appel d'offres ouvert, restreint, MAPA, dialogue compétitif, CCMI)
- 47 pièces uploadées: DC1, DC2, AE, mémoire, DPGF, SOGED, PPSPS, attestations, KBIS, assurances, Qualibat...

**IA Qualitative ZERO €:**
- Classification auto de chaque pièce uploadée par type: candidature / offre / prix / technique / administratif
- Détection du type de marché pour définir le nombre d'enveloppes: 2 (candidature + offre) ou 3 (candidature + technique + prix)
- Output: `{"type_marche": "public ouvert", "enveloppes": 3, "enveloppe1_candidature": ["DC1", "DC2", "KBIS", "Assurances", "Qualibat"], "enveloppe2_technique": ["Mémoire", "SOGED", "PPSPS", "Gantt"], "enveloppe3_prix": ["AE", "DPGF", "BPU"], "pieces_non_classees": ["doc_scan_2026.pdf"], "risque": "orange si pièce non classée"}`

**Solver Garage:** Aucun calcul €. Logique documentaire et classification.

**Vue Salarié:**
- **Sélecteur ZIP Interactif (TRÉSOR 6)** : Interface drag & drop des 47 pièces vers les 3 enveloppes (Candidature / Technique / Prix)
- Chaque pièce uploadée = badge couleur selon l'enveloppe détectée
- Alerte si pièce non classée: "doc_scan_2026.pdf non reconnu — Veuillez classer manuellement"
- Compteur par enveloppe: "Enveloppe 1 = 8/8 pièces — Enveloppe 2 = 11/12 — Enveloppe 3 = 1/1"

**Action Patron:**
- Vérification avant dépôt: "Enveloppe 1 Candidature = 8 pièces / Enveloppe 2 Technique = 12 pièces / Enveloppe 3 Prix = 1 pièce"
- Alerte si pièce dans mauvaise enveloppe: "DC1 détecté dans Enveloppe Offre — Déplacer vers Enveloppe Candidature"
- **Export Word .docx natif (TRÉSOR 6)** : Exigence d'export .docx via `python-docx` pour le Mémoire Technique et le PPSPS (permet retouche manuelle avant dépôt)
- Génération des 3 ZIP conformes à la plateforme (PLACE, Profil Acheteur, etc.)
- Blocage dépôt si enveloppe incomplète

**Générateurs Output:** 3 ZIP prêts à déposer (Candidature.zip, Technique.zip, Prix.zip), checklist dépôt PDF, fichiers DOCX natifs pour retouche manuelle

**Risque si non détecté:** DC1 dans offre = irrégularité = élimination. Mémoire dans candidature = élimination.

---

### 7.22 Module 7.22 — J / Avenant & Post-Gagné Tracker (Le suivi après signature)

**Problème terrain:** Vous gagnez, mais vous oubliez les avenants, les récolements, les levées de réserves = pénalités. Un avenant oublié = 10 000€ à 50 000€ non facturés. Une levée de réserves tardive = pénalités 1 000€/jour.

**Trigger:** Passage statut AO à "Gagné/Attribué". Extraction des échéances contractuelles du CCAP.

**Entrées DCE:**
- CCAP: dates de récolement, délai levée réserves, durée garantie décennale, clauses avenant (délai, montant max, justification)
- AE: montant initial, délai d'exécution
- Planning: jalons contractuels

**IA Qualitative ZERO €:**
- Extraction des échéances contractuelles: date OS, date récolement provisoire, date récolement définitif, délai levée réserves (30j, 60j, 90j), fin garantie décennale (10 ans)
- Détection clause avenant: "Avenant possible jusqu'à 20% du montant initial", "Délai avenant 15j avant échéance"
- Output: `{"date_os": "2026-10-01", "date_recolement_prov": "2027-04-01", "delai_levee_reserves_jours": 60, "date_fin_garantie_decennale": "2037-04-01", "avenant_max_pct": 20, "alertes": ["J-30 récolement", "J-15 levée réserves"]}`

**Solver Garage:**
- Calcul pénalité retard levée réserves: `penalite = jours_retard * montant_jour_penalite`
- Ex: 10j retard * 500€/j = 5 000€ de pénalité
- Calcul montant avenant possible: `avenant_max = montant_initial * 0.20`

**Vue Salarié:**
- Tableau de bord "Mes chantiers en cours" avec échéances
- Alertes: J-30 récolement, J-15 levée réserves, J-90 fin garantie décennale
- Saisie avenant: date, montant, justification, pièce jointe

**Action Patron:**
- Dashboard post-gagné: calendrier des échéances par chantier
- Alerte pénalité: "Levée réserves J-3 — Pénalité de retard 500€/j si dépassé"
- Génération PV de récolement pré-rempli (modèle Vault A10)
- Génération demande d'avenant pré-remplie avec justification économique
- Suivi des avenants: montant cumulé vs plafond 20%, reste disponible

**Générateurs Output:** PV récolement DOCX, demande avenant DOCX, calendrier échéances PDF, alertes email/SMS

**Risque si non détecté:** Avenant oublié = 30 000€ non facturés. Levée réserves tardive = 5 000€ pénalité. Garantie décennale non suivie = litige à 10 ans.

---

### 7.23 Module 7.23 — K / Contentieux & Mémoire en Réclamation Generator (L'avocat virtuel)

**Problème terrain:** Vous perdez un AO injustement (élimination pour vice de forme, notation opaque). Vous ne savez pas faire un recours. Ou le MOA retarde les paiements de 90 jours. Vous ne savez pas rédiger une mise en demeure. Les cabinets d'avocats facturent 300-500€/h.

**Trigger:** Déclenchement manuel par Admin: "Perte injuste" ou "Retard paiement" ou "Élimination vice de forme".

**Entrées DCE:**
- Dossier AO complet: RC, CCAP, CCTP, DPGF, mémoire, pièces déposées
- Correspondance MOA: courrier d'élimination, PV de récolement, factures impayées
- Vault A11: modèles contentieux, jurisprudence, historique réclamations

**IA Qualitative ZERO €:**
- Analyse du motif d'élimination: vice de forme (pièce manquante, délai dépassé), notation opaque (note technique anormale), irrégularité MOA (délai questions non respecté)
- Détection retard paiement: délai contractuel vs délai réel, intérêts moratoires applicables (Loi LME: 3× taux BCE)
- Output: `{"motif": "elimination_vice_forme", "type_recours": "reclamation_pre_attribution", "delai_recours_jours": 10, "force_juridique": "forte", "preuves": ["Attestation visite présente", "DC1 complet"]}`

**Solver Garage:**
- Calcul intérêts moratoires: `interets = montant_impaye * taux_bce * 3 * jours_retard / 365`
- Ex: 100 000€ impayés * 4% * 3 * 90j / 365 = 2 958€ d'intérêts
- Calcul pénalité retard paiement LME: idem + frais de recouvrement forfaitaire 40€

**Vue Salarié:** Aucun accès. Module Admin uniquement (contentieux = stratégique patron).

**Action Patron:**
- Génération mémoire en réclamation (recours contre l'attribution):
  - Motifs d'irrégularité: référence au RC, au CCAG, à la jurisprudence
  - Demande de déclassification: "Nous demandons la déclassification de notre offre et la réouverture de la consultation"
  - Pièces à joindre: liste auto depuis le dossier déposé
- Génération mise en demeure retard paiement:
  - Référence LME, taux BCE, montant dû, intérêts calculés
  - Délai de paiement: 8 jours avant procédure
  - Mise en demeure formelle avec accusé de réception
- Suivi des délais de recours: 10 jours pour réclamation, 2 mois pour TA, 1 an pour contentieux
- Alerte si délai de recours approche (J-3, J-1)

**Générateurs Output:** Mémoire réclamation DOCX (5-10 pages), mise en demeure DOCX (2-3 pages), calcul intérêts PDF, suivi délais Excel

**Référentiels:** jurisprudence_contentieux_btp.json, taux_bce_mensuel.json, modeles_recours.json

**Risque si non détecté:** Recours non fait = marché de 1M€ perdu définitivement. Retard paiement non réclamé = 100 000€ impayés + intérêts perdus.

---

### 7.24 Module 7.24 — L / Certification & Qualification Live Checker (Le vérifieur de badges)

**Problème terrain:** Le marché demande Qualibat 2112 + mention "étanchéité". Vous avez Qualibat 2112 mais pas la mention. Vous êtes éliminés. Ou votre certification expire dans 3 mois, pendant l'exécution du marché = élimination ou contentieux.

**Trigger:** Upload CCTP + extraction qualifications demandées. Cross-check avec Vault A03.

**Entrées DCE:**
- CCTP: qualifications exigées (Qualibat, Qualifelec, RGE, OPQIBI, MASE, ISO), mentions spécifiques, niveaux
- Vault A03: qualifications entreprise, dates de validité, mentions, zones géographiques

**IA Qualitative ZERO €:**
- Détection auto des qualifications demandées dans le CCTP: "Qualibat 2112 mention étanchéité", "RGE Qualibat", "OPQIBI 1411"
- Cross-check avec Vault A03: "Qualibat 2112 OK, mais mention 'ravalement' manquante" / "Qualibat 2112 valide jusqu'au 15/03/2027, marché dure 18 mois = expire pendant l'exécution"
- Détection zone géographique: "Qualibat valide national OK" / "Qualibat valide région Occitanie uniquement, marché à Paris = non couvert"
- Output: `{"qualifications_demandees": ["Qualibat 2112 étanchéité", "RGE"], "qualifications_vault": ["Qualibat 2112"], "manquantes": ["mention étanchéité", "RGE"], "expiration_pendant_marche": ["Qualibat 2112"], "risque": "critique — élimination probable"}`

**Solver Garage:** Aucun calcul €. Logique de matching et de validité temporelle.

**Vue Salarié:**
- Badge "Qualifications à vérifier — 2 manquantes"
- Liste quali: "Qualibat 2112 OK — Mention étanchéité MANQUANTE — RGE MANQUANT"
- Alerte si expiration pendant marché: "Qualibat expire en cours de chantier — Renouveler avant dépôt"

**Action Patron:**
- Dashboard qualifications: match exact demandé vs détenu
- Alerte bloquante si qualification manquante: "Dépôt bloqué — Qualibat 2112 mention étanchéité requise"
- Liste des certifications à obtenir/renouveler avant dépôt avec délais (J-90, J-60, J-30)
- Génération Q/R: "Demander acceptation Qualibat 2112 sans mention étanchéité si lot ne concerne pas l'étanchéité"
- Génération planning renouvellement certifications

**Générateurs Output:** Tableau qualifications PDF, planning renouvellement Excel, Q/R qualifications DOCX

**Risque si non détecté:** Élimination pour qualification manquante = 0€ + 30h perdues. Expiration pendant marché = contentieux + arrêt chantier.

---

### 7.25 Module 7.25 — M / Capacité Financière Analyzer (Le vérifieur de bilan)

**Problème terrain:** Pour les marchés > 100 k€, le RC exige souvent des bilans des 3 derniers exercices, le CA et des ratios financiers (fonds de roulement, capacité d'autofinancement). Les entreprises fournissent leurs bilans, mais personne ne vérifie si les ratios sont suffisants pour le marché. Si vous êtes en dessous des seuils, vous êtes éliminés sans que personne ne vous le dise.

**Trigger:** Détection dans le RC de "capacité financière", "bilans", "fonds de roulement", "CA", "ratios financiers".

**Entrées DCE:**
- RC: seuils implicites ou explicites (ex: "fonds de roulement > 50 k€", "CA > 500 k€")
- Vault A07: bilans 3 ans, CA, RIB, attestations bancaires

**IA Qualitative ZERO €:**
- Extraction des exigences financières du RC: CA minimum, fonds de roulement minimum, endettement maximum
- Output: `{"ca_min_exige": 500000, "fr_min_exige": 80000, "endettement_max": 3.0, "ratios_demandes": true}`

**Solver Garage:**
- Calcul ratios depuis bilans Vault A07:
  - Fonds de roulement = Capitaux permanents - Actif immobilisé
  - Capacité d'autofinancement = Résultat net + Dotations - Reprises
  - Endettement = Dettes / Capitaux propres
- Comparaison avec seuils RC: `fr_reel = 50000`, `fr_min = 80000` => `fr_reel < fr_min` = alerte rouge
- Alerte: "Votre fonds de roulement est de 50 k€, ce marché exige 80 k€ — Risque d'élimination"

**Vue Salarié:** Aucun accès. Module financier = Admin uniquement.

**Action Patron:**
- Dashboard capacité financière: ratios calculés vs seuils exigés
- Alerte si ratio insuffisant: "FR 50 k€ < 80 k€ exigé — Élimination probable"
- Recommandations: "Augmenter capital de 30 k€", "Attestation bancaire de soutien", "Garantie parentale"
- Génération note financière: justification des ratios, attestation banque, lettre d'engagement actionnaire

**Générateurs Output:** Tableau ratios PDF, note financière DOCX, recommandations ajustement Excel

**Référentiels:** ratios_financiers_btp.json (seuils moyens par type de marché)

**Risque si non détecté:** Élimination silencieuse pour bilan insuffisant = 0€ + 40h perdues.

---

### 7.26 Module 7.26 — N / Tableau des Risques Generator (Le comité de direction)

**Problème terrain:** Quand vous décidez de déposer un AO, vous devez souvent présenter un tableau des risques au comité de direction ou à votre associé. Vous perdez du temps à le refaire pour chaque AO.

**Trigger:** Passage workflow à l'étape "Go/No-Go" ou sur demande Admin.

**Entrées DCE:**
- Tous les pièges détectés par modules 7.1-7.25
- Provisions validées par Admin
- Montant du marché, marge nette, BFR pic

**IA Qualitative ZERO €:**
- Agrégation des pièges par famille: juridique, financier, technique, administratif
- Classification par niveau de risque: faible (vert), moyen (orange), élevé (rouge), critique (noir)
- Output: `{"risques": [{"famille": "financier", "module": "7.1 BT", "niveau": "rouge", "description": "Prix fermes 24 mois sans butoir", "provision_requise": true}, ...]}`

**Solver Garage:**
- Calcul impact financier total: `impact_total = sum(provisions_euros)`
- Calcul marge résiduelle: `marge_residuelle = marge_brute - impact_total`
- Alerte si marge résiduelle < 3%: "Marge trop faible après provisions — Recommandé: No-Go"

**Vue Salarié:** Aucun accès. Document comité = Admin uniquement.

**Action Patron:**
- Génération tableau des risques PDF (1 page) prêt pour comité:
  - Colonne 1: Risque (ex: "Inflation BT01")
  - Colonne 2: Probabilité (Élevée/Moyenne/Faible)
  - Colonne 3: Impact (€)
  - Colonne 4: Mitigation (provision, Q/R, clause)
  - Colonne 5: Responsable (Patron, Salarié, Avocat)
  - Ligne finale: Marge résiduelle après provisions
- Score global: "Risque global ÉLEVÉ — 5 risques rouges — Marge résiduelle 2,8% — RECOMMANDATION: No-Go ou renégocier"
- Bouton export: PDF, PowerPoint, Excel

**Générateurs Output:** Tableau risques PDF 1 page, présentation PowerPoint 3 slides, Excel détaillé

**Risque si non détecté:** Comité sans info = décision aveugle. Marge résiduelle 2% non vue = chantier à perte.

---

### 7.27 Module 7.27 — O / MAPA Dossier Generator (Le petit dossier)

**Problème terrain:** Les MAPA (marchés à procédure adaptée) exigent souvent un dossier simplifié: lettre de candidature, références, prix. Mais le format change d'un acheteur à l'autre. Vous perdez 2h à chaque MAPA.

**Trigger:** Détection dans le RC de "procédure adaptée", "MAPA", "marché < 90 000€", "dossier simplifié".

**Entrées DCE:**
- RC: liste des pièces exigées pour MAPA (lettre de candidature, références, prix, délai)
- Vault A01-A12: données administratives pré-remplies

**IA Qualitative ZERO €:**
- Détection auto "MAPA" et extraction du format demandé
- Output: `{"type": "MAPA", "pieces_exigees": ["lettre_candidature", "references_3_ans", "prix_forfaitaire", "delai"], "format": "PDF unique ou 2 enveloppes"}`

**Solver Garage:** Aucun calcul €. Assemblage documentaire.

**Vue Salarié:**
- Wizard MAPA simplifié: 4 étapes (Candidature / Références / Prix / Délai)
- Saisie: prix forfaitaire, délai en semaines, 3 références
- Pré-remplissage auto depuis Vault: KBIS, assurances, Qualibat

**Action Patron:**
- Génération dossier MAPA complet PDF + ZIP:
  - Lettre de candidature pré-remplie (adresse MOA, objet, références)
  - Fiche références 3 ans (extrait Vault A08)
  - Prix forfaitaire (saisie salarié, validation Admin)
  - Délai et planning simplifié
- Adaptation dynamique au format du RC: "2 enveloppes" ou "1 dossier unique"
- Vérification complétude avant dépôt

**Générateurs Output:** Dossier MAPA PDF (10-15 pages), ZIP dépôt prêt, checklist MAPA

**Risque si non détecté:** 2h perdues par MAPA × 20 MAPA/an = 40h/an. Erreur de format = élimination.

---

### 7.28 Module 7.28 — P / Label E+C- Detector (Le détecteur de performance carbone)

**Problème terrain:** De plus en plus de marchés (notamment publics) exigent le **Label E+C-** (niveau énergie positive, niveau carbone). Vous devez fournir les justificatifs: calculs, FDES, analyse de cycle de vie. Souvent le CCTP ne le dit pas explicitement, mais il est sous-entendu dans les annexes.

**Trigger:** Détection dans le RC ou annexes de "E+C-", "E2C1", "E3C2", "bâtiment à énergie positive", "carbone", "bilan carbone".

**Entrées DCE:**
- RC + annexes: mentions E+C-, niveau exigé (E2C1, E3C2...)
- CCTP: exigences RE2020, performance énergétique
- Vault A09: FDES produits, ISO 14001, bilan carbone entreprise

**IA Qualitative ZERO €:**
- Détection mentions E+C- dans RC et annexes: "niveau E2C1 exigé", "attestation E+C-"
- Vérification présence justificatifs Vault A09: FDES produits proposés, calculs E+C-
- Output: `{"label_exige": "E+C-", "niveau": "E2C1", "justificatifs_vault": ["FDES BA13", "FDES beton"], "justificatifs_manquants": ["Attestation E+C- niveau E2C1", "Calcul ACV"], "risque": "orange — label sous-entendu"}`

**Solver Garage:**
- Calcul empreinte carbone chantier: `co2_total = sum(surface_m2 * co2_kg_m2_par_produit)`
- Comparaison avec seuil E+C- niveau E2C1: `seuil_e2c1 = 800 kg CO2/m2` (exemple)
- Alerte si `co2_total > seuil`: "Vos matériaux dépassent le seuil E2C1 — Changer produits ou viser niveau inférieur"

**Vue Salarié:**
- Badge "Label E+C- détecté — Niveau E2C1 — Justificatifs à préparer"
- Liste quali: "FDES BA13 OK — Attestation E+C- manquante — Calcul ACV à faire"

**Action Patron:**
- Dashboard E+C-: niveau visé vs niveau atteignable avec matériaux actuels
- Génération justificatifs E+C-: calcul ACV, fiches FDES, attestation label
- Recommandation: "Vos matériaux actuels atteignent E2C1 — Validez avec bureau étude" ou "Vos matériaux atteignent seulement E1C1 — Négocier niveau ou changer produits"
- Alerte si label sous-entendu mais non détecté: "Annexe 3 mentionne 'bilan carbone' — E+C- probablement exigé"

**Générateurs Output:** Attestation E+C- PDF, calcul ACV Excel, fiches FDES produits, recommandation niveau DOCX

**Référentiels:** seuils_eplusc.json (seuils CO2 par niveau E+C-), fdes_produits_btp.json

**Risque si non détecté:** Label E+C- non détecté = élimination technique. Justificatifs manquants = -2 points sur 20.

---

### 7.34 Module 7.34 — Mode Panique (Emergency Bypass) (TRÉSOR 3)

**Problème terrain:** Deadline < 48h, équipe submergée, risque d'élimination pour non-dépôt. Le Mode Panique V3.2 sauvait des AO en générant le minimum vital en urgence. V7.1 l'élève au rang de **Mission à priorité URGENTE** avec bypass des optimisations.

**Trigger:** Deadline < 48h (détection automatique) **OU** raccourci clavier `Ctrl+Shift+M` (côté Tauri) → `POST /api/dce/analyze` avec `priority="URGENTE"`

**Entrées DCE:** Mission existante avec deadline critique ou action manuelle utilisateur

**IA Qualitative ZERO €:** Aucune analyse longue. Utilisation exclusive des templates Vault pré-validés.

**Solver Garage:** Bypass complet des optimisations lourdes (Mémoire Booster complet, RSE, E+C-)

**Workflow FAST_TRACK:**
- `FAST_TRACK_CAPS = {"CHECK_DEADLINE", "GENERER_DC4", "SEPARER_ENVELOPPE", "DETECTER_PAB", "GENERER_MEMOIRE_TEMPLATE", "GENERER_DPGF_TEMPLATE"}`
- Mission `priority=URGENTE`, `is_blocking=True`
- Semaphore max 6 agents pour garantir performance <3 minutes

**Vue Salarié:** Badge "MODE PANIQUE ACTIF" + compte à rebours + liste des documents minimum vitaux en génération

**Action Patron:** Validation express du ZIP généré, vérification des pièces critiques (DUME, mémoire template, PPSPS simplifié, DPGF, AE)

**Générateurs Output:** ZIP "Minimum Vital" non bloquant contenant : DUME template + Mémoire Technique template + PPSPS simplifié + DPGF template + AE, généré en **<3 minutes**

**Implémentation:** Voir ARCHITECTURE_V7_ENGINE.md §9.3 + PLAN_MAITRE_V7.1 §16.2 (Sprint V32-2)

**Risque si non détecté:** Non-détection deadline <48h = élimination pour non-dépôt. Absence de Mode Panique = perte de marchés gagnables en urgence.

---

7.29 Module 7.29 — Q / Pénurie & Pénibilité RH Shield (Le vrai tueur de marge 2026)

Position dans workflow: Analyse §3.3 étape 3 + cockpit Finance Warfare tuile 6.
Problème terrain: Le CCTP exige du travail de nuit, en espace confiné, ou avec EPI lourds. L'entreprise n'a pas les compagnons qualifiés disponibles. Recours intérim à +40% ou heures sup majorées. La marge de 12% fond à -5%.
Trigger: Détection mots-clés pénibilité dans CCTP (travail de nuit, week-end, espace confiné, port charge >30kg, milieu hospitalier, SS4) + croisement Vault A04 RH.
Entrées DCE: CCTP: contraintes pénibilité, horaires, EPI spécifiques; Vault A04: CV, CACES, habilitations, disponibilités; Vault A07: bilans
IA Qualitative ZERO €: Détecte mots-clés pénibilité, croise avec Vault A04, output JSON qualitatif
Solver Garage (penibilite_solver): Formule surcout_intérim = nb_manquants × taux_horaire × coeff_majoration (1.35-1.45) × heures × durée. Référentiel: taux_interim_btp.json
Output: {"surcout_estime": 42000, "coeff_majoration": 1.40, "nb_manquants": 3, "duree_semaines": 8}
Vue Salarié: Badge "Contraintes pénibilité détectées — Vérifier disponibilité RH"
Action Patron: Dashboard impact +42 000€ + provision + Q/R + recommandation formation
Générateurs Output: Finance Warfare tuile 6 + Q/R tactique + Mémoire Booster chapitre pénibilité
Risque si non détecté: Marge 12% -> -5% = perte 80k€ sur marché 1M€

---

7.30 Module 7.30 — R / Vigilance URSSAF & Délit de Marchandage (Le bouclier pénal)

Position dans workflow: DOCS_ADMIN §3.3 étape 10 + blocage dépôt.
Problème terrain: Loi L8241-1. Attestation de vigilance URSSAF doit être renouvelée tous les 6 mois.
Trigger: Saisie SIRET sous-traitant dans DC4 + upload attestation URSSAF.
Entrées DCE: DC4: SIRET, rang, montant; Vault A03: Qualibat; API externe: URSSAF/Infogreffe
IA Qualitative ZERO €: Vérifie attestation, date, cohérence SIRET. Output JSON qualitatif
Solver Garage (vigilance_solver): Blocage si attestation > 6 mois ou SIRET en liquidation. Output: {"exposition_solidaire": 140000, "blocage_depot": true}
Vue Salarié: Badge "Attestation URSSAF sous-traitant expirée — DC4 bloqué — Voir Admin"
Action Patron: Blocage pénal + exposition 140 000€ + relance + Q/R + DC4 régénéré
Générateurs Output: DC4 bloqué + alerte email + checklist conformité
Risque si non détecté: Solidarité financière 140k€ + amende pénale 75k€

---

7.31 Module 7.31 — S / ZAN & Trackterres Shield (Le cauchemar du terrassement)

Position dans workflow: Analyse §3.3 étape 3 + SOGED §3.3 étape 7.
Problème terrain: Loi ZAN + ISDI. Terre polluée catégorie 2 = 65€/m3. Obligation Trackterres.
Trigger: CCTP terrassement + mots "déblais", "évacuation", "terres", "remblai" + rapport sol G1/G2.
Entrées DCE: CCTP terrassement: volumes, type terre; Rapport sol G1/G2; Vault A09; Référentiel: ISDI géolocalisées
IA Qualitative ZERO €: Détecte évacuation, estime volume, détecte pollution, vérifie réemploi. Output JSON
Solver Garage (zan_solver): Calcul coût = volume × (tri + transport × distance + exutoire). Référentiel: isdi_geolocalisees.json
Output: {"cout_total": 28000, "volume": 1200, "distance_km": 45, "cout_m3": 23.33}
Vue Salarié: Badge "Évacuation 1200m3 terres — ISDI à 45km — Trackterres obligatoire"
Action Patron: Coût 28 000€ + provision + Q/R + SOGED mis à jour
Générateurs Output: Finance Warfare + SOGED + Q/R + provision
Risque si non détecté: 15€/m3 vs 65€/m3 = +60 000€ perte

---

7.32 Module 7.32 — T / Syntax Checker Formules de Révision (Le piège mathématique du CCAP)

Position dans workflow: Analyse §3.3 étape 3 + Finance Warfare.
Problème terrain: MOA rédige formules paramétriques complexes. Somme coefficients ≠ 1.00. Indice INSEE inexistant.
Trigger: CCAP formule révision détectée + indices mentionnés.
Entrées DCE: CCAP art prix: formule complète; Indices cités; Référentiel INSEE: indices valides
IA Qualitative ZERO €: Extrait formule, identifie indices, détecte structure. Output JSON
Solver Garage (formule_algebra_checker): Vérification Σ(coefficients) = 1.00 ±0.001, indices valides, date base cohérente
Output: {"somme_coefficients": 1.08, "erreur": true, "indice_inexistant": "BT08", "impact_estime_pct": 8}
Vue Salarié: Badge "Formule révision CCAP — Erreur détectée somme ≠ 1 — Voir Admin"
Action Patron: Erreur CCAP + somme 1.08 + Q/R générée + impact 8% marge
Générateurs Output: Finance Warfare + Q/R + clause correction
Risque si non détecté: 8% inflation artificielle = perte 64k€ sur 800k€

---

7.33 Module 7.33 — U / Sourcing & API Profil Acheteur (L'automatisation ultime)

Position dans workflow: DEPOSE §3.2 + étape 12 Wizard.
Problème terrain: Dématérialisation totale DUME + API Profil Acheteur/PLACE. Salarié perd 45 min par dépôt.
Trigger: Passage statut DEPOSE + type marché détecté (public/PLACE/BOAMP).
Entrées DCE: RC: type procédure, plateforme; Vault A11: DC1/DC2/DUME; Certificat électronique; SIRET
IA Qualitative ZERO €: Détecte plateforme, vérifie compatibilité, pré-remplit JSON DUME. Output JSON
Solver Garage: Génération DUME JSON natif via API + push direct sur serveur État avec horodatage cryptographique
Vue Salarié: Wizard "Dépôt simplifié — 1 clic — Statut envoi en cours"
Action Patron: Bouton "Déposer" pousse directement + confirmation horodatée + preuve dépôt
Générateurs Output: DUME JSON + 3 ZIP + confirmation horodatée + accusé réception
Risque si non détecté: 45 min × 20 AO/an = 15h/an + risque rejet

---

#### Compléments V7.1 - Rappel structure module (Trigger IA ZERO € Garage Vue Salarié Action Patron Output Risque)

Chaque module 7.13 à 7.28 respecte le gabarit obligatoire :

- **Trigger** : événement déclencheur (import DCE, détection mot-clé RC, etc.)
- **Entrées DCE** : pièces sources (RC, CCAP, CCTP, DPGF, Plans, Vault...)
- **IA Qualitative ZERO €** : extraction, classification, badge, sans jamais calculer € (Voir RAPPORT §7.X pour exemple). Agent RAG BTP dict + CCAG 2021 + DTU, confiance >0.8, JSON sans champ €.
- **Garage Math ZERO LLM** : solveur exact Decimal (`app/engines/math_engine/` sans import LLM), `to_decimal(str)`, formule auditée.
- **Vue Salarié Sans €** : badge, couleur, temps, Qté, alerte qualitative, pas de € (strip_provisions_euros).
- **Action Admin / Patron** : montant exact, provision à valider, graph, slider, justification, audit log.
- **Output Générateur** : DOCX, PDF, ZIP, 3 enveloppes, planning, attestation, etc.
- **Risque si ignoré** : érosion marge, élimination, contentieux, pénalités, BFR négatif.

Voir RAPPORT §7.13 à §7.33 pour détails complets.

#### Archive V12 §7 préservée - Modules 4.1 à 4.10 + 5 + 6 détaillés (Intégrale V12 conservée)

> Ci-dessous le contenu intégral de l'ancien §7 V12 (12 modules) préservé. Les modules V6 7.13-7.28 sont au-dessus en source unique. Référence SSoT : Voir RAPPORT §7.X pour module X.


## 7. SECTION COEUR - SPÉCIFICATIONS FONCTIONNELLES DÉTAILLÉES DES 12 MODULES - SOURCE UNIQUE ABSOLUE

> **RÈGLE CRITIQUE :** Cette section 7 est la SEULE définition fonctionnelle complète des 12 modules. Pour chaque module 7.1 à 7.12, une seule description complète avec Trigger, Entrées DCE, IA Qualitative ZERO €, Solver Garage Exact, Référentiels, Vue Salarié Sans €, Action Patron Avec €, Générateurs Output, Risque Si Non Détecté. Aucune duplication ailleurs. Autres docs citent "Voir RAPPORT section 7.X".

### 7.1 Module 4.1 - BT Index Guardian / Indice Inflation Piège (Le tueur de marge lente)

**Position dans workflow:** Analyse §3.3 étape 3 + cockpit Finance Warfare tuile 1.

**Problème terrain "":** CCAP art 10-12 formule révision sans date base, sans butoir, indices BT01/BT06a mal choisis, prix fermes actualisables cachés. Marge fond 3% par an sans provision. Sur 24 mois chantier 800k€, perte -47k€ si BT01 +6% non provisionnée.

**Trigger:** Upload CCAP + CCTP + AE montant. Détection automatique présence clause prix révisable/ferme/actualisable. Si formule BT détectée, activation.

**Entrées DCE:**
- CCAP art 10-12 (formule révision, type prix, indices, date base, butoir)
- AE/BPU/DPGF montant HT total
- Planning durée mois extrait (ex: 18 mois)
- Vault A07 bilans (pour contexte trésorerie - quali seulement)

**IA Qualitative ZERO € (Agent 1 - 12 agents Trap Detector):**
- Extrait via RAG: type prix (ferme, révisable, actualisable), formule complète OCR, indices mentionnés (BT01, BT06a, BT38...), date base (mois/year), présence butoir, clause sauvegarde.
- Classification risque: si prix ferme sans actualisation + durée >6 mois => Risque critique. Si formule sans date base => Non conforme. Si sans butoir + indices volatils => Risque élevé inflation.
- Output JSON quali: `{type_prix: "ferme actualisable", formule: "P=P0*0.15+0.85*BT01(m)/BT01(m0)", indices: ["BT01"], date_base: "2023-03", butoir: false, risque: "critique", page: 12, extrait: "...", confiance: 0.94}` ZERO CALCUL €.

**Solver Garage Mathématique Exact (bt_projection - 5 nouveaux solveurs ):**
- **Nom:** `bt_projection` - `app/engines/math_engine/bt_projection.py` - ZERO LLM import - scan bloquant.
- **Entrées:** formule, indices, date_base, durée_chantier_mois (18), montant_marche_ht Decimal.
- **Référentiel:** `data/referentiels/bt_indices_insee_36m.json` - BT01/BT06a/BT38 36 mois glissants source INSEE https://www.insee.fr dernière maj 2026-07-01.
- **Calcul:** Projection INSEE 3 scénarios:
 - Scénario conservateur: moyenne glissante 12m + tendance linéaire.
 - Scénario médian: régression 36m.
 - Scénario pessimiste: p95 hausse 36m.
 - Érosion marge exacte = montant_marche * (indice_projeté_fin - indice_base)/indice_base * coeff pondération formule (ex: 0.85). Decimal 28 to_decimal(str).
- **Output:** `{"periode": 18, "bt01_base": 125.3, "bt01_projete_18m_conserv": 132.1, "bt01_med": 133.8, "bt01_pess": 135.2, "erosion_conserv": -22300.00, "erosion_med": -38900.00, "erosion_pess": -47320.00, "provision_recommandee_pct": 8, "graph_data": [...]}`
- **Test:** test_5_solveurs_ vert + bt_projection INSEE exact.

**Référentiels utilisés:** bt_indices_insee_36m.json + INSEE API.

**Vue Salarié (Sans €):**
- Badge couleur: rouge "Risque Inflation Critique - Formule sans butoir" / orange "Risque modéré" / vert "Couvert".
- Texte quali: "CCAP art12: Prix fermes actualisables sans date base explicite. Durée 18 mois. Exposition inflation si BT01 +6%. Prévoir question MOE."
- Pas de montant €, pas de graph €, pas de provision visible.
- Pastille CCAP page 12 extrait.

**Action Patron (Avec €):**
- Finance Warfare Dashboard tuile 1 BT01 Projection: courbe INSEE 36m historique + projection 3 scénarios + zone érosion.
- Montants exacts: "Perte potentielle scénario pessimiste -47 320€ (5.9% marge) - Provision recommandée 8% soit 64 000€".
- Graph: érosion marge par mois.
- Checklist actions: Ajouter clause butoir, provisionner, question MOE "Confirmer date base BT01 et présence butoir 5%".
- Provision à valider checkbox + commentaire.

**Générateurs Output:** Finance Warfare tuile BT, Q/R tactique Q1 si risque critique, Mémoire Booster chapitre Risques.

**Risque si non détecté:** -30k€ à -80k€ marge fondue inflation sans recours.

---

### 7.2 Module 4.2 - Pénalités Detector / Cumuls Cachés (Le piège qui tue trésorerie)

**Problème:** Pénalités éparses CCAP/CCTP/Planning + pénalités cachées (absence réunion, RETard DIUO, absence SOGED, retard levée réserves, absence DOE...). Cumul sans plafond ou plafond 5% CCAG non rappelé. Exposition réelle 12% CA = 124k€.

**Trigger:** Upload CCAP + CCTP(s) + Planning + RC. Extraction regex pénalités.

**Entrées:** CCAP art pénalités, CCTP 00 généralités, CCTP lot pénalités particulières, Planning jalons, CCAG 2021 réf.

**IA Qualitative ZERO €:**
- Extrait toutes pénalités via RAG + regex: type (retard, absence réunion, absence PPSPS, absence SOGED, retard DOE/DIUO, retard levée réserve...), montant (x €/jour ou % ), plafond mentionné, base (par jour calendaire/ouvré).
- Catégorise 6 types: retard global, jalons intermédiaires, absence documents, absence réunions, hygiène sécurité, levée réserves.
- Détecte si plafond 5% CCAG mentionné ou absent, si pénalités particulières cumulables.
- Output: `{"penalites": [{"type": "retard global", "montant": "500€/j cal", "plafond": "Non mentionné", "page": 15, "cumulable": true}, ...], "nb_cachees": 2, "plafond_cite": false}`

**Solver Garage Exact (penalites_cumul):**
- Nom: `penalites_cumul.py`
- Calcul exposition max = somme (montant_jour * durée estimée retard moyen 10j) pour chaque pénalité sans plafond + plafond CCAG 5% comparé.
- Si plafond absent: exposition = 124 500€ (12% marché) flag rouge.
- Provision recommandée = 10% exposition max si pas de clause plafonnement.
- Output: `{"exposition_max": 124500, "exposition_pct_marche": 12, "plafond_ccag_5pct": 40000, "depasse_plafond": true, "liste_sans_plafond": 3, "provision": 16000}`

**Vue Salarié:** Liste quali "6 pénalités détectées dont 2 cachées (page 22 absence réunion 150€/réunion, page 45 RETard DIUO 200€/j). Risque plafond non cité. Badge rouge."
**Action Patron:** Barre exposition 124.5k€ vs plafond 40k€ + liste sans plafond + provision 16k€ à valider + clause plafonnement générée "Les pénalités cumulées sont plafonnées à 5% du montant HT conformément CCAG 2021 art 14.2". Graph.

---

### 7.3 Module 4.3 - Trésorerie Simulator / BFR Warfare (Le tueur d'entreprise saine)

**Problème:** Avance 0% ou 5% sans caution, RG 5% sans caution, délai paiement 30j contractuel 60j réel, facturation mensuelle, retenue 5% + RG 5% = 10% immobilisé. Pic BFR -180k€ mois 4-6 + coût caution vs RG arbitrage.

**Trigger:** CCAP avance %, RG %, délai paiement, caution exigée.

**Entrées:** CCAP art avance, RG, caution, délais règlement, Planning facturation, DPGF total.

**IA Qualitative ZERO €:**
- Extrait: avance % (0/5/10/20), condition (caution à première demande?), RG % (5%), caution RG remplace RG?, délai paiement (30j contractuel), date début paiement.
- Détecte: avance sans caution = risque trésorerie, RG sans caution = immobilisation.
- Output quali: `{"avance": "5% sans caution", "rg": "5% sans caution remplaçable", "delai": "30j + 15j MOE", "risque": "BFR élevé M4-6"}`

**Solver Garage (treasury + nouveau treasury_bfr):**
- Calcul S-curve avancement: décaissement MO matériaux + encaissement factures - RG - avance remboursement.
- Pic BFR = -180 000€ mois 5 (calcul Decimal exact mensualisé).
- Coût caution vs RG: coût caution à première demande = montant * taux 1.2% vs coût immobilisation RG = montant * taux découvert 4% * durée/12. Arbitrage: caution 960€ vs 40 000€ immobilisés = gain trésorerie.
- Graph mensuel BFR.

**Vue Salarié:** "Trésorerie tendue M4-6 - Avance 5% sans caution - RG 5% non cautionnable - Courbe tension sans €"
**Action Patron:** Courbe BFR -180k€ pic + arbitrage caution 960€ vs 40k€ immobilisés + provision BFR à valider + planning facturation optimisé.

---

### 7.4 Module 4.4 - GME Guardian / Solidarité Cachée (Le piège juridique qui engage au-delà du lot)

**Problème:** DC1/AE/CCAP groupement: conjoint vs solidaire, solidarité élargie extension au-delà lot (ex: mandataire solidaire des autres lots), répartition % non 100%, pièces manquantes, cotraitant sans Qualibat.

**Trigger:** Détection mot clé groupement, cotraitance, GME, mandataire dans AE/DC1/CCAP.

**Entrées:** DC1, AE, CCAP groupement, Vault A03 qualifications cotraitants (si fournis).

**IA Qualitative ZERO €:**
- Détecte: type groupement (conjoint / solidaire), clause solidarité élargie ("mandataire solidaire de l'ensemble des cotraitants y compris hors marché"), répartition % (ex: 60/30/10 = 100%?), pièces manquantes (DC2 cotraitant, attestations).
- Output: `{"type": "solidaire avec extension", "risque": "critique - solidarité au-delà lot", "repartition_ok": false, "pieces_manq": ["DC2 cotraitant 2"], "page": 8}`

**Solver Garage:** Contrôle cohérence 100% somme %, checklist pièces Vault (A01-A03) par cotraitant, calcul exposition = montant marché total si solidaire élargie.

**Vue Salarié:** Alerte juridique critique "Solidarité élargie détectée page 8 - Exposition hors lot - Vérifier répartition"
**Action Patron:** Exposition 180k€ (montant total marché solidaire) + DC1 corrigé + checklist sécurisation + clause à négocier + Q/R "Clarifier étendue solidarité art 3.2".

---

### 7.5 Module 4.5 - DC4 Guardian Cascade / Plafond Sous-Traitance (Le piège qui fait dépasser 100%)

**Problème:** CCAP plafond sous-traitance 50% ou 70% ou 80%, rang DC4, cumul DC4 62% > plafond, sous-traitant sans Qualibat A03, sous-traitance en cascade non autorisée.

**Trigger:** CCAP clause sous-traitance + saisie salarié sous-traitants + montant sous-traité.

**Entrées:** CCAP plafond %, saisie salarié nom/nature/montant/rang sous-traitant, Vault A03 Qualibat sous-traitant, DPGF.

**IA Qualitative ZERO €:**
- Lit plafond %, identifie rang 1/2, détecte cascade (sous-traitant de sous-traitant).
- Output: `{"plafond": "50%", "cumul_actuel": "62%", "depasse": true, "cascade": false}`

**Solver Garage:** Contrôle cumul < plafond Decimal exact, calcul exact montant sous-traité, génération DC4 avec Vault A03 qualification + RIB.

**Vue Salarié:** Saisie nom/nature sous-traitant puis masquée après validation (plus visible). Badge "Plafond dépassé - Voir Admin".
**Action Patron:** Cumul 62% >50% + montant sous-traité + DC4 généré avec A03 + alerte bloquante si > plafond.

---

### 7.6 Module 4.6 - RAT Amiante Analyzer / SS4 Provision (Le piège mortel chantier)

**Problème:** Bâtiment <1997 obligation RAT/RDTA Amiante/Plomb/Termites vs pièces jointes DCE. Si RAT absent et <1997 = suspicion amiante + provision SS4 + délai + SOP. Sans provision 18.5k€.

**Trigger:** Date permis bâtiment <1997 ou absence date + CCTP démolition + absence RAT dans DCE.

**Entrées:** CCTP démolition/curage, Diagnostics (PDF), Plans état existant, date bâtiment, Vault A10 SOP SS4, Vault A04 CACES amiante.

**IA Qualitative ZERO €:**
- Croise obligation RAT vs pièces jointes: si <1997 et RAT non joint => obligation.
- Détecte présence "amiante", "plomb", "pollution", "RAT", "DTA".
- Output: `{"bat_avant_1997": true, "rat_joint": false, "obligation": "RAT + RDTA avant travaux", "risque": "critique - SS4 obligatoire", "page_obligation": 5}`

**Solver Garage (amiante_ss4):**
- Calcul provision SS4 = Surface_saisie_sal ** Ratio référentiel amiante €/m2. Ex: 100m2 * 185€ = 18 500€ + aléa 20% + délai 3 sem + coût formation.
- Référentiel: ratios_amiante_ss4.json {curage_léger 85€/m2, curage_lourd 185€/m2, démolition 250€/m2}

**Vue Salarié:** "RAT manquant - Saisir surface concernée m2 - Obligation SS4"
**Action Patron:** Provision 18 500€ + délai + SOP SS4 Vault A10 + PPSPS amiante + question MOE "Merci confirmer RAT joint ou prévoir RDTA avant travaux + délais d'accès".

---

### 7.7 Module 4.7 - SOGED REP Tracker / Déchets - Ecoulement REP (Le coût caché qui double)

**Problème:** CCTP obligation SOGED/PEMD/Diagnostic déchets + REP PMCB depuis 2023 + 7 flux tri + exutoires + traçabilité. Coût tri+transport+exutoire-REP = 4.2k€ non provisionné classique.

**Trigger:** CCTP démolition/gros œuvre + mots SOGED, PEMD, déchets, REP, PMCB.

**Entrées:** CCTP, Métré salarié m2 cloison/voile/sol, Photos, Vault A09 FDES, Vault A10 modèle SOGED, saisie exutoires salarié.

**IA Qualitative ZERO €:**
- Détecte obligation SOGED/PEMD/Diagnostic Produit Matériaux Déchets, obligation REP PMCB, 7 flux.
- Output: `{"soged_oblig": true, "pemd_oblig": true, "rep": true, "flux": 7}`

**Solver Garage (rep_cost nouveau - ADEME):**
- Formule: Coût réel = Σ (Poids_kg * (tri €/kg + transport €/kg + exutoire €/kg - reprise_REP_bois/métal €/kg))
- Poids = Surface_métré * ratio_kg_m2 référentiel ADEME. Ex: BA13 cloison 72/48 ratio 12kg/m2 dont 70% plâtre 10% métal 20% inerte.
- Référentiel data/referentiels/ratios_ademes_dechets.json + prix_defaut tri/transport/exutoire/reprise REP.
- Output: 4 200€ ventilation par flux + SOGED généré auto avec exutoires + bordereau.

**Vue Salarié:** "Obligation SOGED 7 flux - Saisir exutoire + distance km - SOGED à générer"
**Action Patron:** Coût 4 200€ détaillé + SOGED généré + preuve factures + provision + FDES A09.

---

### 7.8 Module 4.8 - Site Contraintes Check / Visite Site (Le temps que personne ne chiffre)

**Problème:** CCTP 00 site occupé (hôpital/EHPAD/école = +15% MO), accès <3m ou impossible nacelle <1.5m +10-18% MO, hauteur >4m +20%, stockage impossible +8%, horaires restreints 8h-12h +12%, centre-ville dense +10%, bruit <70dB +5%. Temps perdu 2.5h/j non provisionné = 18k€ + 2 semaines.

**Trigger:** CCTP 00 contraintes site + visite obligatoire + Photos salarié + notice site.

**Entrées:** CCTP 00, notice contraintes, photos terrain upload salarié, saisie salarié case à cocher 7 contraintes, Vault A08 photos chantier similaire.

**IA Qualitative ZERO €:**
- Détection NLP contraintes site occupé, accès, hauteur, stockage, horaires, centre-ville, bruit.
- Output: `{"site_occupe": "hôpital - badge critique", "acces": "<3m", "hauteur": ">4m", "coeffs": ["+15% occupé", "+10% accès"]}`

**Solver Garage (site_coeff):**
- Formule: temps_corrige = temps_base * (1 + sum(coeffs actifs)). Coeffs référentiel data/referentiels/coeffs_site_contraintes.json.
- Ex: site occupé hôpital 0.15 + accès difficile <3m 0.10 + hauteur sup 4m 0.20 = 0.45 => +45% MO.
- Impact financier = temps_sup * taux horaire moyen DPGF (base prix Admin).
- Output: Impact 18k€ + 2 semaines délai.

**Vue Salarié:** "+2.5h/j - Site occupé hôpital - Accès impossible + Badge - Photos à l'appui"
**Action Patron:** Impact 18k€ + 2 sem + détail coeff + planning ajusté + provision site à valider + photo pastillée + question MOE moyens levage.

---

### 7.9 Module 4.9 - Cross-Check CCTP-DPGF-Plans / Incohérences & Oubli (La marge qui s'évapore)

**Problème:** Triple incohérence: CCTP dit 120m2 BA13 hydrorésistant, DPGF 80m2 BA13 standard, Plans 135m2 cloisons. 4 portes vues plan RDC non chiffrées DPGF. Marques imposées sans équivalent R2111-7 CCP (ex: "Porte DALH 45 référence X sans équivalent") = illégal + piège.

**Trigger:** Présence CCTP + DPGF/BPU Excel + Plans PDF.

**Entrées:** CCTP lot, DPGF Excel parsed ligne/ligne Qté/PU, Plans PDF parcellaire comptage portes/fenêtres/surfaces AI vision, Vault base prix PU moyens.

**IA Qualitative ZERO €:**
- Triple compare: extraction quantités CCTP vs DPGF vs Plans via AI vision comptage + NLP.
- Détecte: oublis (porte vue plan non chiffrée DPGF), écarts >2%, marques sans équivalent R2111-7.
- Output: `{"incoherences": [{"lot": "Cloisons", "cctp": "120m2 hydro", "dpgf": "80m2 std", "plans": "135m2", "ecart": "40%"}, {"oublis": "4 portes RDC vues plan non DPGF"}], "marques_sans_equivalent": 1}`

**Solver Garage (incoherence_solver):**
- Provision omission = Qté lue sur plan * PU moyen base prix Admin. Ex: 4 portes * 450€ = 1 800€.
- Calcul total écarts = Σ écart_qté * PU moyen.
- Seuil >2% déclenche provision.

**Vue Salarié:** "Incohérence: 4 portes RDC non chiffrées DPGF - CCTP 120m2 vs DPGF 80m2 vs Plans 135m2 - Pastille plan"
**Action Patron:** Provision omission 3 100€ + total écarts 18.2k€ + Question R2111-7 générée "Confirmer absence référence marque impérative contraire R2111-7 CCP ou accepter équivalent" + Q/R tactique.

---

### 7.10 Module 4.10 - Assistant Questions-Réponses MOE/MOA Tactique (L'arme juridique qui sécurise)

**Problème:** 48h avant date limite questions = dernière chance neutraliser pièges ou créer trace écrite pour futur mémoire en réclamation.

**Trigger:** Date limite questions -48h (calcul date RC) + agrégation alertes rouges modules 4.1 à 4.9.

**Entrées:** Tous pièges rouges/oranges 4.1-4.9 + pages/extraits + montants totaux enjeu + CCAP/CCTP pages + Vault A10 jurisprudence.

**IA Qualitative ZERO € (Moteur templating juridique, pas Garage €):**
- Agrège 9 modules en 8 questions max (limite Profil Acheteur), triées par enjeu € décroissant.
- Rédaction opposable langage MOE/MOA non agressif mais verrouillant: "Il semble que... Pourriez-vous confirmer... Dans l'affirmative, ... Dans la négative, ...".
- Chaque question vise: soit faire neutraliser piège (ex: ajouter butoir BT01), soit créer trace écrite pour futur mémoire réclamation (ex: "Nous notons absence RAT malgré obligation").
- Référence exacte page/paragraphe.
- Output: DOCX 8 questions max avec enjeu € par question.

**Solver Garage:** Aucun €, mais moteur templating tri enjeu € décroissant + numérotation.

**Vue Salarié:** "7 questions générées - Relecture technique - Ajuster vocabulaire métier - Vérifier faisabilité"
**Action Patron:** Validation juridique + enjeu total 288k€ détaillé par question (Q1 192k€ solidarité, Q2 47k€ BT...) + Export DOCX/PDF prêt à déposer sur Profil Acheteur + bouton Dépôt. Chaque question = arme future mémoire réclamation.

---

### 7.11 Module 5 - Moteur Génération Mémoire Technique Booster 18/20 (Le tueur de concurrence)

**Objectif:** Générer mémoire noté 18/20, pas 12/20. Zéro copier-coller générique.

**Trigger:** Passage workflow MEMOIRE + Vault A01-A12 complet + Métré + Site contraintes + ADN Extractor 50 contraintes.

**Entrées:** RC pondération critères (Valeur technique 60% Prix 40%...), Vault A08-A10, ADN 50 contraintes CCTP, Métré temps corrigé, Site contraintes, Référentiels Météo France/INSEE/ADEME.

**5.1 Ingestion ADN Local et Contraintes CCTP:**
IA extrait 50 contraintes spécifiques CCTP (ex: "bruit <45dB chantier école occupé", "poussière <10mg/m3", "distance agence-chantier 12km", "accès <2.5m", "HSP 3.2m", "RE2020", "délai 18 mois dont 2 mois hiver..."). Injection données locales: distance agence-chantier calculée via adresse chantier vs siège, nom conducteur chantier, spécificités climatiques commune (pluie/neige). Mémoire répond point par point contrainte => preuve écoute CCTP, pas générique.

**5.2 Injection Preuves Matérielles Vault A08-A10:**
Pour chaque affirmation "Nous maîtrisons coulage béton en site occupé", moteur va chercher automatiquement dans Vault A08 photo chantier similaire géolocalisée <50km avec EXIF + légende + date + PV + attestation. Insertion auto dans mémoire avec légende "Chantier EHPAD Saint-Martin 2024 à 18km - Coulage voile site occupé - PV 12/04/2024". Preuve matérielle notée 18/20 vs concurrent générique "Nous maîtrisons..." sans preuve.

**5.3 Planning Gantt sous Contraintes Intempéries Régionales - Garage OR-Tools:**
Entrées: durée tâches saisie Salarié, calendrier, DTU délais séchage/cure béton. Garage récupère historique Météo France sur 10 ans pour département via `meteo_france_intemperies_10ans.json` (jours intempéries moyens par mois) et intègre marge. Génère Gantt avec marge intempéries crédible + chemin critique + jalon. Sortie PNG + MS Project .mpp. Mémoire chapitre Planning crédible vs concurrent planning lisse irréaliste.

**5.4 Volet Environnemental RE2020, FDES & SOGED:**
Génère chapitre environnemental à partir Vault A09 (ISO 14001, FDES perso, bilan carbone) + module 4.7 SOGED. Insère FDES produits, calcul empreinte, gestion déchets 7 flux, charte chantier propre, bilan carbone calculé. Conforme RE2020.

**5.5 Matrice de Conformité RC:**
Génère tableau conformité critère par critère RC (Valeur technique 60% décomposée: 20% moyens humains, 15% moyens matériels, 15% méthode, 10% environnement... Prix 40%). Renvoi page par page mémoire. Permet MOE de noter sans effort = note maximale.

**RBAC:** Salarié rédige/comment 80% auto sans prix. Admin verrouille + ajoute marge + graph + validation.

**Output:** Mémoire 40-60 pages DOCX/PDF + Gantt PNG + MS Project + FDES annexes.

---

### 7.12 Module 6 - HANDOFF+ Book de Démarrage Chantier (Le pont entre AO et exécution - Double Artefact Étanche)

**Trigger:** Passage statut AO de "En attente" à "Gagné / Attribué" par Admin uniquement. Irreversible salarié.

**7.12.1 Structure du Book de Démarrage PDF Interactif 30 pages généré en 2 secondes:**
- Page 1: Fiche identité marché, contacts MOA/MOE/CSPS/bureau contrôle, montant HT, délais, jalons, cautions.
- Page 2: DPGF annoté de guerre: chaque ligne contient commentaires Salarié ("Attention: accès nacelle impossible prévoir échafaudage - Saisie étape 5") mais SANS prix (expurgé) / AVEC prix complet (version complète).
- Page 3-5: Risques résiduels validés par Patron liste qualitative sans montants (expurgé) / avec montants provisions (complet).
- Page 6-10: Plans avec pastilles d'alerte (amiante SS4 zone, accès <3m, hauteur >4m, SOGED benne, oublis DPGF 4 portes).
- Page 11-15: Kit Administratif: DC4 sous-traitants validés, modèles situation travaux, OS types, planning Gantt avec intempéries, PPSPS pré-rempli Vault A10 + SS4 si RAT, SOGED avec exutoires, DICT.
- Page 16-20: Mémoire technique version chantier + SOGED + DOE modèle + ATT modèle + RAG historique chantiers similaires <50km.
- Annexes: Vault A01-A12 extraits utiles chantier.

**7.12.2 Gestion des Vues Restreintes - Double Artefact Physiquement Distinct (Étanchéité):**
Deux PDFs générés physiquement séparés sur filesystem distinct, pas un seul PDF avec masquage JS (fuite possible).
- `BOOK_CHANTIER_COMPLET_ADMIN.pdf`: Avec marges, provisions, BFR, coût caution, temps corrigé financier, PU, coeff vente, marge nette. Stocké coffre-fort Admin /data/minio/admin/ - seul Admin peut télécharger. Audit log accès.
- `BOOK_CHANTIER_EXECUTION_SALARIE.pdf`: Sans aucune donnée €, sans marge, sans provisions. Risques qualitatifs uniquement ("Présence amiante possible zone X - Porter EPI - Voir SOP SS4"). DPGF sans PU, sans total, uniquement commentaires qualitatifs. C'est celui reçu par Conducteur de Travaux. L'étanchéité garantie par génération 2 artefacts séparés + test `test_handoff_double_artefact.py` scan regex € = 0 occurrence + test `test_handoff_irreversible.py` seul Admin déclenche.

Frontend: test_front_no_handoff_leak.spec.ts vérifie conducteur ne peut pas deviner URL admin.

---

---


## 8. Tableau Récapitulatif Unique — Synthèse Architecture Données & Processus (Seul Tableau Autorisé)

> **RÈGLE D'OR:** Un seul tableau récap dans tout RAPPORT. Pas de tableau en double dans autres sections. Si besoin référence, réfère "Voir §8 Tableau Récap". Autres docs (MANIFESTE, etc.) n'ont pas de tableau récap modules.

| Module | Entrées DCE Principales | IA Qualitative ZERO € (Agent RAG) | Solver Garage Math Exact (ZERO LLM) | Référentiels | Vue Salarié Sans € | Vue Admin Avec € | Output Générateur |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Trap Detector base** | RC, CCAP, CCTP(s), DPGF, Plans, Diags | Classification 4 familles + page/extrait niveau confiance | Routage vers 7.1-7.28 selon piège | CCAG 2021, DTU, BTP dict | Liste pièges quali sans € | Liste + confiance + priorité + provision future | JSON traps + badges workflow |
| **7.1 BT Index Guardian** | CCAP art10-12 formule, AE montant, Planning durée | Extrait type prix, formule, indices, date base, butoir | bt_projection INSEE 3 scénarios érosion marge exacte Decimal | bt_indices_insee_36m.json INSEE | Badge Risque Inflation Critique formule sans butoir | Perte -47 320€ + graph 3 scénarios + provision 8% à valider | Finance Warfare tuile1 + Q/R + Mémoire chapitre Risques |
| **7.2 Pénalités Detector** | CCAP, CCTP, Planning jalons | Extrait 6 types cumul, plafond, base jour cal/ouvré, 2 cachées | penalites_cumul exposition max vs plafond 10% public / 5% privé / CCMI ∞ | CCAG 2021 art 19.2 + NF P03-001 | Liste 6 pénalités dont 2 cachées | Exposition 124.5k€ 12% CA + provision 16k€ + clause plafonnement générée | Finance Warfare tuile2 + clause docx |
| **7.3 Trésorerie Simulator** | CCAP avance %, RG %, délais paiement, caution | Extrait avance/RG/délai/caution 30% État / 10% collectivité | treasury BFR S-curve mensuelle pic -180k€ + arbitrage caution 960€ vs RG 40k€ | taux découvert 4%, taux caution 1.2% | Alert "Trésorerie tendue M4-6" courbe sans € | Pic BFR -180k€ + coût caution vs RG + planning facturation | Finance Warfare tuile3 BFR + Graph S-curve + planning financement |
| **7.4 GME Guardian** | DC1, AE, CCAP groupement, Vault A03 cotraitants | Détecte conjoint/solidaire/élargie, répartition 100%, pièces manq | Contrôle cohérence 100% + pièces + exposition solidaire | CCP groupement | Alerte juridique critique solidarité élargie | Exposition 180k€ solidaire totale + DC1 corrigé + checklist + Q/R | DC1 corrigé + checklist + Q/R |
| **7.5 DC4 Cascade** | CCAP plafond %, saisie salarié sous-traitant, Vault A03 | Lit plafond, rang 1/2, cascade | Contrôle cumul < plafond Decimal + génération DC4 avec A03 | CCP sous-traitance | Saisie nom/nature masquée après | Cumul 62% >50% + montant sous-traité + DC4 généré | DC4 PDF + AE |
| **7.6 RAT Amiante Analyzer** | CCTP démo, Diags, Plans, Date bâtiment <1997, Vault A10 SOP SS4 | Croise obligation RAT vs pièces jointes, date <1997 | provision SS4 = Surface * Ratio 185€/m2 + aléa + délai | ratios_amiante_ss4.json | "RAT manquant saisir surface m2" | Provision 18 500€ + délai 3sem + SOP SS4 + PPSPS amiante | Provision + PPSPS amiante + Q/R |
| **7.7 SOGED REP Tracker** | CCTP, Métré salarié m2, Photos, Vault A09/A10 | Détecte SOGED/PEMD/REP 7 flux tri | rep_cost ADEME Poids kg/m2 * (tri+transport+exutoire-REP) | ratios_ademes_dechets.json ADEME | "SOGED obligatoire 7 flux saisir exutoire" | Coût réel 4.2k€ ventilé + SOGED généré + bordereau traçabilité | SOGED PDF + bilan déchets + FDES |
| **7.8 Site Contraintes Check** | CCTP 00, Photos, Notice, Saisie salarié 7 contraintes | Extraction accès HSP site occupé bruit horaires | site_coeff temps_corrige = temps_base*(1+sum coeff) +15% occupé +10% accès +20% hauteur | coeffs_site_contraintes.json | "+2.5h/j site occupé hôpital Accès impossible" | Impact 18k€ +2 semaines provision site + planning ajusté | DPGF annoté + Pastilles plans + Mémoire chapitre Contraintes |
| **7.9 Cross-Check CCTP-DPGF-Plans** | CCTP, DPGF Excel, Plans PDF, Vault base prix PU | Triple compare quantités tri-dimensionnelle + marque sans équivalent R2111-7 | incoherence_solver écart Qté*PU moyen total oublis >2% provision | base prix Admin PU moyens | "Incohérence 120m2 vs 80m2 vs 135m2 4 portes non chiffrées" | Oubli 4 950€ + total écarts 18.2k€ + provision 3.1k€ + Q/R R2111-7 | Provision omission + Q/R + DPGF annoté |
| **7.10 Q/R Tactique** | Tous pièges rouges 7.1-7.9 + pages extraits + enjeu total | Génération 8 questions max opposables réf page/§ non agressives verrouillantes | Tri enjeu € décroissant templating juridique | Vault A10 jurisprudence | "7 questions générées relecture tech" | Docx Questions prêt Enjeu 288k€ Q1 192k€ validation juridique export Profil Acheteur | DOCX Q/R + trace mémoire réclamation |
| **7.11 Mémoire Booster 18/20** | RC pondération, Vault A08-A10, ADN 50 contraintes CCTP, Métré, Site | Extraction critères RC + ADN local 50 contraintes + météo + RE2020 | OR-Tools Gantt Météo France 10 ans + calcul bilan carbone FDES + matrice conformité | meteo_france_intemperies_10ans.json, FDES, ADEME | Rédaction 80% preuves <50km sans prix | Validation marge + planning Gantt + bilan RE2020 | Mémoire 40-60p DOCX/PDF + Gantt PNG + MPP + Matrice conformité |
| **7.12 HANDOFF+ Book** | Projet statut GAGNE, DPGF chiffrée, Pièges validés, Vault | Assemblage DCE annoté kit admin PPSPS SOGED DICT DC4 DOE | Trésorerie finale planning réaliste double artefact | — | Book conducteur sans marge nette 30p risques qualitatifs plans pastillés kit admin | Book complet avec marge provisions BFR coût caution temps corrigé coffre-fort audit log | 2 PDFs distincts 30p + audit log |
| **7.13 A Deadline Guardian** | RC date limite, fuseau horaire plateforme | Extraction date/heure limite + fuseau + checklist pièces | Logique temporelle + blocage dépôt si incomplet | — | Compte à rebours J-7/J-2/J-1/H-4 + checklist verte/rouge | Forçage dépôt loggué + historique horodaté | Checklist dépôt PDF + ICS export + confirmation horodatée |
| **7.14 B Alloti Guardian** | RC allotissement, CCTP lots multiples | Détection alloti + nb lots + critères par lot + similarité mémoire inter-lots | Logique pondération + détection lot piège | — | Wizard séparé par lot + badge vert/orange/rouge par lot | Scoring lots pièges + décision stratégique par lot | 5 mémoires DOCX + 5 DPGF + tableau stratégie lots |
| **7.15 C RSE Booster** | RC critère RSE, CCAP clause insertion, RE2020 | Extraction pondération RSE 10-15% + clause insertion + RE2020 | Calcul heures insertion réalisables vs exigées + pénalité 2×SMIC | SMIC horaire, taux insertion historique | Badge RSE 15% note + saisie heures/partenaire | Score prévisionnel RSE /20 + pénalité insertion 4 194€ + chapitre RSE auto | Chapitre RSE DOCX + bilan RE2020 PDF + tableau insertion Excel |
| **7.16 D Prix-Mémoire Coherence** | Mémoire technique + DPGF/BPU | Extraction moyens humains/matériels mémoire vs prix DPGF | Calcul ratio coût mémoire / DPGF total + score cohérence | base prix Admin PU moyens | Badge "Mémoire vs DPGF — Vérifier cohérence" | Dashboard "Mémoire/DPGF = 62% IRRÉALISTE" + recommandations | Rapport cohérence PDF + recommandations ajustement |
| **7.17 E Variante Guardian** | RC clause variante, mémoire technique | Détection variante autorisée + base obligatoire + conditions | Logique documentaire base+variante | — | Wizard onglet Base + Variante + alerte irrégularité | Vérification dépôt 2 mémoires + 2 DPGF + ordre correct | 2 mémoires DOCX + 2 DPGF Excel + checklist variantes |
| **7.18 F Matériaux Shield** | CCAP clause matériaux, indices acier/bois/cuivre | Détection clauses matériaux spécifiques distinctes BT01 | Calcul perte matériaux = montant × variation indice × durée/12 | indices_matériaux_insee.json | Badge "Clause matériaux détectée — Vérifier protection" | Dashboard "Acier +40% = perte 90k€" + simulation par matériau + Q/R | Simulation matériaux PDF + Q/R matériaux DOCX |
| **7.19 G PAB Detector** | DPGF/AE prix total, base prix historique, RC estimation | Estimation prix moyen attendu + écart % vs seuil -20% | Calcul risque PAB + marge min viable 6% + simulation prix | base prix historique SMART_AO | Badge "Prix à vérifier — Risque anormalement bas" | Dashboard "Prix 380k€ vs moyenne 520k€ — Écart -27% PAB ÉLEVÉ" | Note justification PAB DOCX + simulation prix PDF |
| **7.20 H Visite Auto** | RC visite obligatoire, CCTP contraintes | Détection visite obligatoire + date/heure/lieu/contact | Logique calendaire + checklist + validation GPS | — | Alerte calendrier J-2 + upload photo GPS + checklist visite | Attestation visite pré-remplie + validation GPS coordonnées vs chantier | Attestation visite PDF + compte-rendu DOCX + photos ZIP |
| **7.21 I Enveloppe Separator** | RC type procédure, 47 pièces uploadées | Classification auto pièce par pièce: candidature/offre/prix/technique | Logique documentaire + vérification DUME vs DC1/DC2 | — | Interface drag & drop 3 colonnes + compteur par enveloppe | Vérification complétude 3 enveloppes + génération 3 ZIP | 3 ZIP prêts dépôt + checklist dépôt PDF |
| **7.22 J Post-Gagné Tracker** | CCAP échéances, AE montant initial, Planning jalons | Extraction dates OS, récolement, levée réserves, garantie décennale | Calcul pénalité retard levée réserves + montant avenant max 20% | — | Tableau échéances chantier + alertes J-30 | Dashboard calendrier échéances + PV récolement + demande avenant | PV récolement DOCX + demande avenant DOCX + calendrier PDF |
| **7.23 K Contentieux Generator** | Dossier AO complet, courrier élimination/retard | Analyse motif élimination/retard paiement + force juridique | Calcul intérêts moratoires LME 3×BCE + frais recouvrement | taux_bce_mensuel.json, jurisprudence | Aucun accès (Admin only) | Génération mémoire réclamation + mise en demeure + suivi délais | Mémoire réclamation DOCX + mise en demeure DOCX + calcul intérêts PDF |
| **7.24 L Certif Live Checker** | CCTP qualifications, Vault A03 | Extraction Qualibat/RGE/MASE/OPQIBI demandées + cross-check Vault | Logique matching exact + validité temporelle + zone géo | — | Badge "2 qualifications manquantes" + alerte expiration | Dashboard match exact + planning renouvellement J-90/J-60/J-30 | Tableau qualifications PDF + planning Excel + Q/R qualifications |
| **7.25 M Capacité Financière** | RC ratios exigés, Vault A07 bilans | Extraction CA min, FR min, endettement max exigés | Calcul FR, CAF, endettement depuis bilans + comparaison seuils | ratios_financiers_btp.json | Aucun accès (Admin only) | Dashboard ratios calculés vs seuils + note financière + recommandations | Tableau ratios PDF + note financière DOCX + recommandations Excel |
| **7.26 N Tableau Risques Comité** | Tous pièges 7.1-7.25 + provisions validées | Agrégation par famille + classification niveau risque | Calcul impact total € + marge résiduelle + alerte si <3% | — | Aucun accès (Admin only) | Tableau 1 page PDF comité + score global + recommandation Go/No-Go | Tableau risques PDF + PowerPoint 3 slides + Excel détaillé |
| **7.27 O MAPA Generator** | RC procédure adaptée, Vault A01-A12 | Détection MAPA + extraction format + pièces exigées | Assemblage documentaire auto | — | Wizard 4 étapes MAPA simplifié + pré-remplissage Vault | Génération dossier MAPA complet PDF + ZIP + vérification complétude | Dossier MAPA PDF 10-15p + ZIP dépôt prêt + checklist MAPA |
| **7.28 P Label E+C- Detector** | RC/annexes E+C-, CCTP RE2020 | Détection label E+C- niveau E2C1/E3C2 + justificatifs manquants | Calcul empreinte carbone vs seuil niveau + comparaison | seuils_eplusc.json, fdes_produits_btp.json | Badge "Label E+C- détecté — Justificatifs à préparer" | Dashboard niveau visé vs atteignable + génération justificatifs | Attestation E+C- PDF + calcul ACV Excel + fiches FDES + recommandation DOCX |

**Conclusion Architecturale tableau:** SMART_AO n'est pas outil chiffrage. C'est système arme juridique et financière. Salarié apporte intelligence terrain, IA vigilance exhaustive ZERO €, Garage Math vérité des euros Decimal, Patron garde clé coffre RBAC. Avec 28 modules, on couvre l'intégralité de la chaîne: veille → dépôt sans erreur → marge protégée → note maximale → chantier sécurisé → contentieux géré.

---

#### Archive V12 §8 préservée - Tableau 12 lignes historique (conservé pour traçabilité)

> Tableau V12 = 12 modules. Tableau V6 = 28 lignes (Trap Detector base + 28 modules). Voir RAPPORT §8 pour tableau V6 à jour 28 lignes.


## 8. Tableau Récapitulatif Unique - Synthèse Architecture Données & Processus (Seul Tableau Autorié)

> **RÈGLE D'OR:** Un seul tableau récap dans tout RAPPORT. Pas de tableau en double dans autres sections. Si besoin référence, réfère "Voir §8 Tableau Récap". Autres docs (MANIFESTE, etc.) n'ont pas de tableau récap modules.

| Module | Entrées DCE Principales | IA Qualitative ZERO € (Agent RAG) | Solver Garage Math Exact (ZERO LLM) | Référentiels | Vue Salarié Sans € | Vue Admin Avec € | Output Générateur |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Trap Detector base** | RC, CCAP, CCTP(s), DPGF, Plans, Diags | Classification 4 familles + page/extrait niveau confiance | Routage vers 4.1-4.10 selon piège | CCAG 2021, DTU, BTP dict | Liste pièges quali sans € | Liste + confiance + priorité + provision future | JSON traps + badges workflow |
| **4.1 BT Index Guardian** | CCAP art10-12 formule, AE montant, Planning durée | Extrait type prix, formule, indices, date base, butoir | bt_projection INSEE 3 scénarios érosion marge exacte Decimal | bt_indices_insee_36m.json INSEE | Badge Risque Inflation Critique formule sans butoir | Perte -47 320€ + graph 3 scénarios + provision 8% à valider | Finance Warfare tuile1 + Q/R + Mémoire chapitre Risques |
| **4.2 Pénalités Detector** | CCAP, CCTP, Planning jalons | Extrait 6 types cumul, plafond, base jour cal/ouvré, 2 cachées | penalites_cumul exposition max vs plafond 5% CCAG | CCAG 2021 art pénalités | Liste 5 pénalités dont 2 cachées | Exposition 124.5k€ 12% CA + provision 16k€ + clause plafonnement générée | Finance Warfare tuile2 + clause docx |
| **4.3 Trésorerie Simulator** | CCAP avance %, RG %, délais paiement, caution | Extrait avance/RG/délai/caution | treasury BFR S-curve mensuelle pic -180k€ + arbitrage caution 960€ vs RG 40k€ | taux découvert 4%, taux caution 1.2% | Alert "Trésorerie tendue M4-6" courbe sans € | Pic BFR -180k€ + coût caution vs RG + planning facturation | Finance Warfare tuile3 BFR + Graph S-curve + planning financement |
| **4.4 GME Guardian** | DC1, AE, CCAP groupement, Vault A03 cotraitants | Détecte conjoint/solidaire/élargie, répartition 100%, pièces manq | Contrôle cohérence 100% + pièces + exposition solidaire | CCP groupement | Alerte juridique critique solidarité élargie | Exposition 180k€ solidaire totale + DC1 corrigé + checklist + Q/R | DC1 corrigé + checklist + Q/R |
| **4.5 DC4 Cascade** | CCAP plafond %, saisie salarié sous-traitant, Vault A03 | Lit plafond, rang 1/2, cascade | Contrôle cumul < plafond Decimal + génération DC4 avec A03 | CCP sous-traitance | Saisie nom/nature masquée après | Cumul 62% >50% + montant sous-traité + DC4 généré | DC4 PDF + AE |
| **4.6 RAT Amiante Analyzer** | CCTP démo, Diags, Plans, Date bâtiment <1997, Vault A10 SOP SS4 | Croise obligation RAT vs pièces jointes, date <1997 | provision SS4 = Surface * Ratio 185€/m2 + aléa + délai | ratios_amiante_ss4.json | "RAT manquant saisir surface m2" | Provision 18 500€ + délai 3sem + SOP SS4 + PPSPS amiante | Provision + PPSPS amiante + Q/R |
| **4.7 SOGED REP Tracker** | CCTP, Métré salarié m2, Photos, Vault A09/A10 | Détecte SOGED/PEMD/REP 7 flux tri | rep_cost ADEME Poids kg/m2 * (tri+transport+exutoire-REP) | ratios_ademes_dechets.json ADEME | "SOGED obligatoire 7 flux saisir exutoire" | Coût réel 4.2k€ ventilé + SOGED généré + bordereau traçabilité | SOGED PDF + bilan déchets + FDES |
| **4.8 Site Contraintes Check** | CCTP 00, Photos, Notice, Saisie salarié 7 contraintes | Extraction accès HSP site occupé bruit horaires | site_coeff temps_corrige = temps_base*(1+sum coeff) +15% occupé +10% accès +20% hauteur | coeffs_site_contraintes.json | "+2.5h/j site occupé hôpital Accès impossible" | Impact 18k€ +2 semaines provision site + planning ajusté | DPGF annoté + Pastilles plans + Mémoire chapitre Contraintes |
| **4.9 Cross-Check CCTP-DPGF-Plans** | CCTP, DPGF Excel, Plans PDF, Vault base prix PU | Triple compare quantités tri-dimensionnelle + marque sans équivalent R2111-7 | incoherence_solver écart Qté*PU moyen total oublis >2% provision | base prix Admin PU moyens | "Incohérence 120m2 vs 80m2 vs 135m2 4 portes non chiffrées" | Oubli 4 950€ + total écarts 18.2k€ + provision 3.1k€ + Q/R R2111-7 | Provision omission + Q/R + DPGF annoté |
| **4.10 Q/R Tactique** | Tous pièges rouges 4.1-4.9 + pages extraits + enjeu total | Génération 8 questions max opposables réf page/§ non agressives verrouillantes | Tri enjeu € décroissant templating juridique | Vault A10 jurisprudence | "7 questions générées relecture tech" | Docx Questions prêt Enjeu 288k€ Q1 192k€ validation juridique export Profil Acheteur | DOCX Q/R + trace mémoire réclamation |
| **5 Mémoire Booster 18/20** | RC pondération, Vault A08-A10, ADN 50 contraintes CCTP, Métré, Site | Extraction critères RC + ADN local 50 contraintes + météo + RE2020 | OR-Tools Gantt Météo France 10 ans + calcul bilan carbone FDES + matrice conformité | meteo_france_intemperies_10ans.json, FDES, ADEME | Rédaction 80% preuves <50km sans prix | Validation marge + planning Gantt + bilan RE2020 | Mémoire 40-60p DOCX/PDF + Gantt PNG + MPP + Matrice conformité |
| **6 HANDOFF+ Book** | Projet statut GAGNE, DPGF chiffrée, Pièges validés, Vault | Assemblage DCE annoté kit admin PPSPS SOGED DICT DC4 DOE | Trésorerie finale planning réaliste double artefact | - | Book conducteur sans marge nette 30p risques qualitatifs plans pastillés kit admin | Book complet avec marge provisions BFR coût caution temps corrigé coffre-fort audit log | 2 PDFs distincts 30p + audit log |

**Conclusion Architecturale tableau:** SMART_AO n'est pas outil chiffrage. C'est système arme juridique et financière. Salarié apporte intelligence terrain, IA vigilance exhaustive ZERO €, Garage Math vérité des euros Decimal, Patron garde clé coffre RBAC. C'est ainsi qu'on arrête perdre argent sur AO mal analysés.

---

---


## 9. Garage Math Étendu — 10+ Solveurs + Référentiels — Synthèse Fonctionnelle

**Règle d'or absolue:** Aucun fichier dans `app/engines/math_engine/` n'importe `openai, anthropic, langchain, mistralai, langchain_core, cohere, groq`. Scan `test_math_engine_no_llm_import.py` bloquant build si import détecté. Librairies autorisées: `pulp 3.3.2 + ortools 9.15 + decimal + json + math + datetime`. `to_decimal(str)` obligatoire JAMAIS float pour €.

**5 Solveurs Historiques:**
- chiffrage_pulp.py: optimisation marge sous contraintes MO/matériaux.
- treasury.py: BFR mensuel.
- planning_ortools.py: Gantt chemin critique.
- quantite.py: vérif quantités.
- coeff_site.py de base.

**10+ Solveurs Étendus V6 — SOURCE FONCTIONNELLE UNIQUE ICI:**

1. **bt_projection.py** — Projection INSEE BT01/BT06a/BT38 36 mois + érosion marge exacte 3 scénarios.
2. **penalites_cumul.py** — Somme exposition max pénalités avec/sans plafond CCAG 10% public / 5% privé / CCMI ∞ + comparaison + seuil exonération 1 000€.
3. **rep_cost.py** — Coût réel déchets ADEME. Formule détaillée §7.7.
4. **site_coeff.py étendu** — Application coeffs correcteurs MO. Formule: temps_corrige = temps_base * (1 + Σ coeffs actifs).
5. **incoherence_solver.py** — Détection oublis et écarts >2% CCTP-DPGF-Plans + provision omission Qté plan * PU moyen base prix.
6. **capacite_financiere.py** — Calcul ratios bilan (FR, CAF, endettement) depuis Vault A07 + comparaison seuils RC.
7. **risques_generator.py** — Agrégation impact total € + marge résiduelle + alerte si <3%.
8. **mapa_generator.py** — Assemblage documentaire MAPA (aucun calcul €, logique structuration).
9. **eplusc_calculator.py** — Calcul empreinte carbone chantier vs seuil E+C- niveau exigé.
10. **pab_detector.py** — Calcul écart prix vs moyenne estimation + risque PAB + simulation prix.
11. **materiaux_shield.py** — Calcul perte matériaux spécifiques (acier, bois, cuivre, bitume) vs indices INSEE.
V7.1: `penibilite_solver.py` — Surcoût intérim/pénibilité. Formule: nb_manquants × taux × coeff_majoration × heures. Référentiel taux_interim_btp.json
V7.1: `vigilance_solver.py` — Blocage URSSAF + exposition solidarité. Formule: montant_sous_traité × risque. Blocage si attestation > 6 mois.
V7.1: `zan_solver.py` — Coût évacuation terres ZAN. Formule: volume × (tri + transport × distance + exutoire). Référentiel isdi_geolocalisees.json
V7.1: `formule_algebra_checker.py` — Vérification Σ(coeffs) = 1 + indices INSEE valides. Formule: abs(sum(coeffs) - 1.0) < 0.001
V7.1: `sourcing_api_solver.py` — Assemblage DUME JSON + push API Profil Acheteur. Aucun calcul €, logique documentaire.

**Référentiels data/referentiels/ — JSON exemples fonctionnels:**

- `bt_indices_insee_36m.json`: BT01/BT06a/BT38 36 mois glissants source INSEE.
- `ratios_ademes_dechets.json`: ratio kg/m2 + flux % + prix tri/transport/exutoire/reprise REP.
- `coeffs_site_contraintes.json`: coeffs correcteurs MO site occupé/accès/hauteur/stockage/horaires/centre-ville/bruit.
- `meteo_france_intemperies_10ans.json`: jours intempéries moyens mensuels par département.
- `ratios_amiante_ss4.json`: curage_léger 85€/m2, curage_lourd 185€/m2, démolition 250€/m2.
- **V6:** `indices_matériaux_insee.json`: acier, bois, cuivre, bitume, ciment, aluminium 36 mois glissants.
- **V6:** `seuils_eplusc.json`: seuils CO2 kg/m2 par niveau E+C- (E1C1, E2C1, E3C2...).
- **V6:** `fdes_produits_btp.json`: empreinte carbone par produit (BA13 12kg CO2/m2, béton 250kg/m3...).
- **V6:** `ratios_financiers_btp.json`: seuils moyens CA/FR/endettement par type marché.
- **V6:** `jurisprudence_contentieux_btp.json`: modèles recours, délais, motifs.
- **V6:** `taux_bce_mensuel.json`: taux BCE mensuel pour calcul intérêts moratoires LME.
V7.1: `taux_interim_btp.json`: taux par métier (coffreur, maçon, électricien...) et région, coeff majoration 1.35-1.45
V7.1: `isdi_geolocalisees.json`: liste ISDI/ISDND agréées par département, coordonnées GPS, capacité, tarifs
V7.1: `indices_insee_valides.json`: liste exhaustive indices INSEE BT/TP/matériaux avec dates de validité

Mise à jour référentiels: cron mensuel + Admin peut surcharger via Vault A09/A10.

---


#### 9.1 Solveurs V6 Formules Explicites

#### 9.2 Phrases exactes exigées mission - pour validation automatique (SSoT) - PRESERVE

capacite_financiere FR=CapPerm-Immo CAF endettement
risques_generator marge résiduelle <3% No-Go
mapa_generator
eplusc_calculator CO2 vs seuils
pab_detector -20% orange -30% rouge + justif 48h
materiaux_shield perte=montant*variation*duree/12

 - Exigences Mission

Cette sous-section détaille explicitement les formules requises par la mission chirurgicale, avec référence SSoT Garage Math.

1. **capacite_financiere.py — FR=CapPerm-Immo, CAF, endettement :**
   - FR = Capitaux Permanents - Immobilisations Nettes (Vault A07 bilans)
   - FR > 0 et FR >= 10% CA exigé si RC le demande
   - CAF = Résultat Net + Dotations - Reprises + VCEAC - PCEAC
   - Endettement = Dettes Financières / Capitaux Propres < seuil RC (ex: <1)
   - Output JSON : {"FR": Decimal, "CAF": Decimal, "endettement_ratio": Decimal, "alerte_elimination_silencieuse": bool}
   - Voir RAPPORT §7.25

2. **risques_generator.py — Marge résiduelle <3% = No-Go :**
   - Impact total = Σ provisions validées (BT + pénalités + BFR + REP + amiante + omission + site + GME + DC4 + PAB + matériaux + ...)
   - Marge résiduelle = (Montant HT - Coût direct - Impact total) / Montant HT
   - Si marge résiduelle < 3% => Go/No-Go = NO-GO automatique comité direction
   - Output : Tableau 1 page PDF + PPT 3 slides + Excel détaillé
   - Voir RAPPORT §7.26

3. **mapa_generator.py — Assemblage documentaire MAPA (aucun calcul €, logique structuration) :**
   - Détection MAPA si procédure adaptée < seuils
   - Extraction format + pièces exigées RC
   - Assemblage auto Vault A01-A12 + génération dossier 10-15p PDF + ZIP
   - Voir RAPPORT §7.27

4. **eplusc_calculator.py — CO2 vs seuils E+C- :**
   - Empreinte chantier = Σ (Qté produit * FDES kgCO2/m2 ou /m3)
   - Seuils comparés : seuils_eplusc.json E1C1, E2C1, E3C2...
   - Score E+C- = niveau visé vs atteignable, justificatifs manquants
   - Voir RAPPORT §7.28

5. **pab_detector.py — -20% orange -30% rouge + justif 48h :**
   - Moyenne attendue = moyenne des prix base historique + estimation RC si fournie
   - Écart = (Prix proposé - Moyenne) / Moyenne *100
   - -20% à -30% = alerte orange PAB potentiel, <-30% = rouge PAB élevé
   - Marge min viable 6% : si marge <6% après PAB = alerte Admin only
   - Justification 48h générée DOCX avec décomposition coûts
   - Formule : marge = (Prix - Coût) / Prix, doit être >=0.06
   - Voir RAPPORT §7.19

6. **materiaux_shield.py — Perte = montant * variation * durée/12 :**
   - Indices matériaux INSEE : acier, bois, cuivre, bitume, ciment, aluminium (indices_matériaux_insee.json 36 mois)
   - Variation = (Indice actuel - Indice base) / Indice base
   - Perte = Montant lot * Variation * (Durée mois /12)
   - Séparé du BT01 : acier bois cuivre distincts BT01
   - Output : simulation par matériau + Q/R matériaux DOCX
   - Voir RAPPORT §7.18

7. **bt_projection.py — Voir FINANCE + site_coeff étendu :**
   - Projection INSEE BT01/BT06a/BT38 3 scénarios + érosion marge exacte Decimal
   - Formule érosion : (Formule CCAP appliquée avec butoir si présent)
   - Voir RAPPORT §7.1

8. **penalites_cumul.py — Plafond CCAG 10% public + 1000€ seuil / 5% privé / CCMI ∞ :**
   - CCAG 2021 art 19.2.1 plafond 10% HT public + seuil exonération 1000€
   - Privé NF P03-001 plafond 5%
   - CCMI 1/3000e/jour sans plafond
   - Voir RAPPORT §6.1 + §7.2

9. **treasury.py — Avance 30% État / 10% EPA>60M€ + RG max 5% :**
   - Avance minimale 2024 : 30% État, 10% collectivités EPA >60M€ dépenses, garantie facultative >30%
   - RG max 5% remplaçable garantie première demande
   - BFR S-curve + arbitrage caution 960€ vs RG immobilisé 40k€
   - Voir RAPPORT §6.4 + §7.3

10. **Autres solveurs : rep_cost, site_coeff étendu, incoherence_solver, etc. - Voir RAPPORT §7.1 à §7.33 et §9 source pour liste complète 16 solveurs.**

> Règle d'or Garage : Aucun import LLM dans app/engines/math_engine/. Scan test_math_engine_no_llm_import.py bloquant. to_decimal(str) obligatoire. Voir RAPPORT §9 source.

#### Archive V12 §9 préservée - 5 solveurs historiques + référentiels


## 9. Garage Math Étendu - 5 Nouveaux Solveurs + Référentiels - Synthèse Fonctionnelle (Technique Voir Handbook)

**Règle d'or absolue:** Aucun fichier dans `app/engines/math_engine/` n'importe `openai, anthropic, langchain, mistralai, langchain_core, cohere, groq`. Scan `test_math_engine_no_llm_import.py` bloquant build si import détecté. Librairies autorisées: `pulp 3.3.2 + ortools 9.15 + decimal + json + math + datetime`. `to_decimal(str)` obligatoire JAMAIS float pour €.

**5 Solveurs Historiques :**
- chiffrage_pulp.py: optimisation marge sous contraintes MO/matériaux.
- treasury.py: BFR mensuel.
- planning_ortools.py: Gantt chemin critique.
- quantite.py: vérif quantités.
- coeff_site.py de base.

**5 Nouveaux Solveurs Étendus - SOURCE FONCTIONNELLE UNIQUE ICI (contrats API Voir Handbook):**

1. **bt_projection.py** - Projection INSEE BT01/BT06a/BT38 36 mois + érosion marge exacte 3 scénarios. Input: formule, indices, date base, durée, montant HT Decimal. Output: erosion conserv/med/pess, provision %, graph_data 36 points.

2. **penalites_cumul.py** - Somme exposition max pénalités avec/sans plafond CCAG 5% + comparaison. Input: liste pénalités (type, montant jour, plafond mentionné, cumulable) + montant marché. Output: exposition max €, %, liste sans plafond, provision recommandée 10% si sans plafond, clause plafonnement texte.

3. **rep_cost.py** - Coût réel déchets ADEME. Formule détaillée §7.7. Input: surfaces métrées par ouvrage + exutoires + km transport. Réf: `ratios_ademes_dechets.json` (ratio kg/m2 + flux % + prix tri/transport/exutoire/reprise REP). Output: coût total ventilé par flux + bilan kg + SOGED data.

4. **site_coeff.py étendu** - Application coeffs correcteurs MO. Formule: temps_corrige = temps_base * (1 + Σ coeffs actifs). Coeffs Réf: `coeffs_site_contraintes.json` {site_occupe_hopital_EHPAD_ecole 0.15, acces_difficile_lt_3m 0.10, acces_impossible_lt_1_5m 0.18, hauteur_sup_4m 0.20, stockage_impossible 0.08, horaires_restreints_8h_12h 0.12, centre_ville_dense 0.10, bruit_lt_70dB 0.05}. Output: temps corrigé h, impact financier €, délai supplémentaire semaines.

5. **incoherence_solver.py** - Détection oublis et écarts >2% CCTP-DPGF-Plans + provision omission Qté plan * PU moyen base prix. Input: quantités triple source + PU moyens Vault base prix. Output: liste incohérences % écart + provision omission + total écarts.

**Référentiels data/referentiels/ - JSON exemples fonctionnels (schéma Voir Handbook):**

- `bt_indices_insee_36m.json`: `{"BT01": [{"date": "2023-01", "valeur": 125.3}, ... 36 mois], "BT06a": [...], "source": "INSEE https://www.insee.fr", "derniere_maj": "2026-07-01"}`
- `ratios_ademes_dechets.json`: `{"BA13 cloison 72/48": {"ratio_kg_m2": 12, "flux": {"platre": 0.7, "metal": 0.1, "inerte": 0.2}}, "BETON voile 20cm": {"ratio_kg_m2": 45, ...}, "source": "ADEME", "prix_defaut": {"tri": 45, "transport": 35, "exutoire_inerte": 25, "exutoire_platre": 95, "reprise_REP_bois": -20}}`
- `coeffs_site_contraintes.json`: `{"site_occupe_hopital_EHPAD_ecole": 0.15, "acces_difficile_lt_3m": 0.10, ... "formule": "temps_corrige = temps_base * (1 + sum(coeffs actifs))"}`
- `meteo_france_intemperies_10ans.json`: `{"38 Isere": {"1": 8, "2": 6, ... "source": "Meteo France 10 ans"}, "methode": "jours intemperies moyens mensuels dept - bloque Gantt si journee intemperie + DTU delai cure"}`
- `ratios_amiante_ss4.json`: `{"curage_leger": 85, "curage_lourd": 185, "demolition": 250, "unite": "€/m2", "source": "Base prix + retours chantiers"}`

Mise à jour référentiels: cron mensuel + Admin peut surcharger via Vault A09/A10.

---

---


## 10. Dashboards Fonctionnels — Spécification Fonctionnelle

### 10.1 Finance Warfare Dashboard (Admin Only — 5 Tuiles Avec €)

Tuile 1 **BT01 Projection:** courbe INSEE 36m historique + 3 scénarios projection + 3 montants érosion + provision 8% slider à valider. Graph Recharts.
Tuile 2 **Pénalités Cumul:** barre horizontale exposition max 124.5k€ vs plafond CCAG 80k€ (10% public) + liste 6 pénalités dont 3 sans plafond badge rouge + provision 16k€ + bouton "Générer clause plafonnement".
Tuile 3 **Trésorerie BFR Warfare:** courbe S-curve mois/mois BFR -180k€ pic + courbe encaissement/décaissement + coût caution 960€ vs coût RG immobilisé 40k€ arbitrage + tableau cash-flow mensuel + provision BFR.
Tuile 4 **REP Coût Ventilation:** donut kg par flux + barre coût réel 4.2k€ vs prévu 2k€ + tableau exutoires + bouton "Générer SOGED".
Tuile 5 **Site Coeff Impact:** comparatif temps base vs temps corrigé + délai + impact financier 18k€ + 2 semaines + détail coeffs actifs + photos pastillées.

Chaque tuile: provision à valider checkbox + commentaire Admin + audit log.

### 10.2 Vault Dashboard

A01-A12 liste alphabétique + badge couleur validité (vert OK, orange J-30, rouge EXPIRE bloquant) + cohérence SIRET/Qualibat badge + bouton upload + versioning 10 + preview OCR. Impossible déposer ZIP si A01-A03 EXPIRE.

### 10.3 HANDOFF+ Dashboard

Bouton "Générer Book de Démarrage" (visible que si statut GAGNE + Admin). Double artefact log (date génération, taille, checksum, par qui). Preview expurgé/complet selon rôle (Admin voit 2 previews, Salarié 1 seul expurgé). Audit log accès (qui a téléchargé quel version quand). Bouton envoi email conducteur.

### 10.4 V6 — Deadline Guardian Dashboard

Compte à rebours visuel par projet: J-7, J-2, J-1, H-4, H-1. Checklist pièces obligatoires par type de marché. Badge bloquant rouge si pièce manquante ou Vault expire avant date limite. Bouton dépôt désactivé si checklist rouge. Historique dépôts horodatés.

### 10.5 V6 — Contentieux & Post-Gagné Dashboard (Admin Only)

- Calendrier échéances post-signature par chantier: OS, récolement, levée réserves, fin garantie décennale.
- Alertes J-30, J-15, J-3 avec bouton génération PV/avenant.
- Module contentieux: liste recours possibles, délais restants, bouton génération mémoire réclamation / mise en demeure.
- Suivi avenants: montant cumulé vs plafond 20%, reste disponible.

### 10.6 V6 — Qualifications & Capacité Financière Dashboard (Admin Only)

- Tableau match qualifications: demandé vs détenu vs manquant vs expiration pendant marché.
- Planning renouvellement certifications J-90/J-60/J-30.
- Ratios financiers: FR, CAF, endettement calculés vs seuils RC exigés.

### 10.7 Wizard Salarié UX 12 Étapes (Sans € — Voir §3.3)

Tuiles qualitatives sans €, barre progression %, bouton à la fois, aide contextuelle DTU/CCAG, autosave, pastilles plans.

---


#### 10.8 Synthèse Dashboards V6 - Extensions requises

- **Deadline Dashboard V6** : Compte à rebours J-7/J-2/J-1/H-4/H-1, checklist pièces obligatoires par type marché (public/MAPA/CCMI), badge bloquant rouge si Vault expire avant dépôt, bouton dépôt désactivé si checklist rouge, historique dépôts horodatés, export ICS. Voir RAPPORT §7.13

- **Contentieux Dashboard V6** : Calendrier échéances post-signature (OS, récolement, levée réserves, garantie décennale), alertes J-30/J-15/J-3 avec bouton génération PV/avenant, module contentieux liste recours, délais restants, bouton génération mémoire réclamation / mise en demeure, suivi avenants montant cumulé vs plafond 20%, reste disponible. Admin Only. Voir RAPPORT §7.22 et §7.23

- **Qualifications Dashboard V6** : Tableau match qualifications demandé vs détenu vs manquant vs expiration pendant marché, planning renouvellement J-90/J-60/J-30 Qualibat/RGE/MASE/OPQIBI, ratios financiers FR CAF endettement vs seuils RC. Admin Only. Voir RAPPORT §7.24 et §7.25

- Finance Warfare Dashboard existant conserve 5 tuiles avec € Admin Only (BT projection, pénalités cumul plafond 10% public, trésorerie BFR S-curve avance 30% / RG 5%, REP coût, Site coeff). Voir RAPPORT §10.1

- Voir RAPPORT §10.2 Vault Dashboard J-30 readonly bloquant, §10.3 HANDOFF+ double artefact, §10.7 Wizard Salarié 12 étapes sans €.

#### Archive V12 §10 préservée


## 10. Dashboards Fonctionnels - Spécification Fonctionnelle

### 10.1 Finance Warfare Dashboard (Admin Only - 5 Tuiles Avec €)

Tuile 1 **BT01 Projection:** courbe INSEE 36m historique + 3 scénarios projection + 3 montants érosion + provision 8% slider à valider. Graph Recharts. Data: bt_projection solver.

Tuile 2 **Pénalités Cumul:** barre horizontale exposition max 124.5k€ vs plafond CCAG 40k€ (5%) + liste 6 pénalités dont 3 sans plafond badge rouge + provision 16k€ + bouton "Générer clause plafonnement". Data: penalites_cumul solver.

Tuile 3 **Trésorerie BFR Warfare:** courbe S-curve mois/mois BFR -180k€ pic + courbe encaissement/décaissement + coût caution 960€ vs coût RG immobilisé 40k€ arbitrage + tableau cash-flow mensuel + provision BFR. Data: treasury solver étendu.

Tuile 4 **REP Coût Ventilation:** donut kg par flux (bois 30%, plâtre 40%, inerte 20%...) + barre coût réel 4.2k€ vs prévu 2k€ + tableau exutoires + bouton "Générer SOGED". Data: rep_cost solver.

Tuile 5 **Site Coeff Impact:** comparatif temps base vs temps corrigé + délai + impact financier 18k€ + 2 semaines + détail coeffs actifs + photos pastillées. Data: site_coeff solver.

Chaque tuile: provision à valider checkbox + commentaire Admin + audit log.

### 10.2 Vault Dashboard

A01-A12 liste alphabétique + badge couleur validité (vert OK, orange J-30, rouge EXPIRE bloquant) + cohérence SIRET/Qualibat badge + bouton upload + versioning 10 + preview OCR. Impossible déposer ZIP si A01-A03 EXPIRE.

### 10.3 HANDOFF+ Dashboard

Bouton "Générer Book de Démarrage" (visible que si statut GAGNE + Admin). Double artefact log (date génération, taille, checksum, par qui). Preview expurgé/complet selon rôle (Admin voit 2 previews, Salarié 1 seul expurgé). Audit log accès (qui a téléchargé quel version quand). Bouton envoi email conducteur.

### 10.4 Wizard Salarié UX 12 Étapes (Sans € - Voir §3.3)

Tuiles qualitatives sans €, barre progression %, bouton à la fois, aide contextuelle DTU/CCAG, autosave, pastilles plans.

---

---


## 11. Modèle Commercial & Pricing — Synthèse (Détail Commercial Voir MANIFESTE-)

**Formule Unique Entreprise:** Paiement unique licence perpétuelle + VPS OVH facturé client (16Go min) OU infogéré assumé DPA art28. Pas d'abonnement. Pas de % CA. MAJ 30s via docker pull.

Modèle A Souverain: Client propriétaire VPS OVH FR, opère lui-même, support éditeur sans accès données métier (heartbeat whitelist 0 donnée DCE/Vault/prix).

Modèle B Infogéré assumé: VPS dédié EU par client, opéré en infogérance par éditeur avec DPA art28. Souveraineté physique maintenue (serveur dédié pas mutualisé). Formule correcte obligatoire, slogan "je n'héberge rien" interdit.

Pricing indicatif (Voir MANIFESTE): Licence unique + coût VPS OVH ~ 80-150€/mois facturé direct OVH client. Pas de commission cachée.

**V6 — Argumentaire ROI 28 modules:**
- Abonnement SMART_AO: 549€/mois = 6 588€/an
- Un seul marché protégé (inflation non provisionnée) = 80 000€ sauvés → ROI 1 214%
- Un seul recours gagné (Module K) = 1 000 000€ récupérés → ROI 15 000%
- Un seul élimination évitée (Modules A, B, H, I, L) = 500 000€ de CA sauvé → ROI 7 500%
- Un seul PAB détecté à temps = 50 000€ de marge préservée

Garantie: Voir MANIFESTE — objectif usage pas garantie chiffrée.

---

#### Archive V12 §11 préservée

## 11. Modèle Commercial & Pricing - Synthèse (Détail Commercial Voir MANIFESTE-)

**Formule Unique Entreprise:** Paiement unique licence perpétuelle + VPS OVH facturé client (16Go min) OU infogéré assumé DPA art28. Pas d'abonnement. Pas de % CA. MAJ 30s via docker pull.

Modèle A Souverain: Client propriétaire VPS OVH FR, opère lui-même, support éditeur sans accès données métier (heartbeat whitelist 0 donnée DCE/Vault/prix).

Modèle B Infogéré assumé: VPS dédié EU par client, opéré en infogérance par éditeur avec DPA art28. Souveraineté physique maintenue (serveur dédié pas mutualisé). Formule correcte obligatoire, slogan "je n'héberge rien" interdit.

Pricing indicatif (Voir MANIFESTE): Licence unique + coût VPS OVH ~ 80-150€/mois facturé direct OVH client. Pas de commission cachée.

Garantie: Voir MANIFESTE - objectif usage pas garantie chiffrée.

---

---


## 12. Go/No-Go Production — 39 Critères Single VPS / 46 Fleet — Gate Bloquant Unique

> **RÈGLE:** Gate bloquant avant 1er client payant. Pas avant 1er commit. `check_go_nogo.sh` et `check_go_nogo_fleet.sh` doivent être verts. Voir PLAN_MAITRE_V7.1 §10 pour script. Ici définition fonctionnelle critères.

**Single VPS 39 critères (31 V6/V7.1 +8 V7.1):**

1. **auth JWT vps_id middleware:** JWT vérifié + vps_id obligatoire pas de tenant_id + 2FA TOTP Argon2id.
2. **filesystem isolation O_NOFOLLOW+fstat+BASE_ROOT non-symlink+owner:** `_check_access(path)` non contournable.
3. **Excel FileLock single worker+versioning10+validate_header:** FileLock pour DPGF concurrent + versioning 10 max + validation header ligne.
4. **Math Engine no LLM import:** Aucun import openai/anthropic/langchain/mistralai dans app/engines/math_engine/.
5. **No conflict Garage PuLP+OR-Tools:** Coexistence CBC + OR-Tools sans conflit lib.
6. **Strip financier API employee cannot see prices:** API salarié 0 champ prix/marge/provision.
7. **Vault J-30 readonly cron is_readonly continue:** Cron J-30 continue même si is_readonly=True.
8. **Heartbeat whitelist 0 donnée métier DCE/Vault/prix:** Heartbeat support ne remonte que métriques infra (CPU/RAM/disk/uptime).
9. **Rollback snapshot LVM+backup PG + cosign verify:** Snapshot LVM avant MAJ + backup Postgres AES-256-GCM + restore <15min.
10. **Backup/restore AES-256-GCM <15min:** Chiffrement backups AES-256-GCM + objectif restore 15min 500Mbps.
11. **ClamAV EICAR scan upload:** Tout upload DCE/Vault scanné ClamAV, EICAR bloqué.
12. **Golden Files 3×400p DCE réels parse <5min:** 3 DCE réels 400p chaque parse complet <5min.
13. **test_28_agents_trap_detector.py vert:** 28 agents IA qualitative ZERO € avec JSON sans € + confiance >0.8. Aucun agent ne calcule €.
14. **test_16_solveurs_vert:** 16 solveurs Garage Decimal exact, to_decimal(str), 0 import LLM, tests unitaires avec cas limites + référentiels JSON existants.
15. **test_rbac_provisions.py vert:** Aucune provision € visible salarié sur 28 modules + regex scans DOM + API scan + serializer strip + double artefact test provision.
16. **test_handoff_double_artefact.py vert:** Double PDF générés physiquement distincts + 0 occurrence € ni marge dans version salariée + checksum distincts + 2 artefacts log.
17. **test_agent_no_euro.py vert:** Scan code 28 agents IA aucun calcul €, aucun regex €, aucun champ provision/marge généré côté IA.
18. **V6 test_deadline_guardian.py vert:** Blocage dépôt si pièce manquante ou délai dépassé + compte à rebours exact.
19. **V6 test_alloti_guardian.py vert:** Détection alloti + séparation lots + similarité mémoire inter-lots <85%.
20. **V6 test_enveloppe_separator.py vert:** Classification auto 47 pièces + tri correct 3 enveloppes + DUME vs DC1/DC2 vérifié.
21. **V6 test_certif_live_checker.py vert:** Match exact qualifications demandées vs Vault + expiration pendant marché détectée.
22. **V6 test_pab_detector.py vert:** Alerte PAB si écart <-20% + note justification générée.
23. **V6 test_contentieux_generator.py vert:** Mémoire réclamation + mise en demeure générées avec délais corrects + calcul intérêts LME exact.
24. **V6 test_post_gagne_tracker.py vert:** Alertes J-30 échéances + PV récolement + demande avenant générés.
25. **V7.1 test_penibilite_rh.py vert:** Détection contraintes + croisement Vault A04 + calcul surcoût intérim.
26. **V7.1 test_vigilance_urssaf.py vert:** Blocage DC4 si attestation > 6 mois + exposition solidarité calculée.
27. **V7.1 test_zan_trackterres.py vert:** Coût évacuation + ISDI géolocalisée + Trackterres obligatoire.
28. **V7.1 test_formule_revision.py vert:** Σ(coeffs) = 1 vérifié + indices INSEE valides + Q/R générée si erreur.
29. **V7.1 test_sourcing_api.py vert:** DUME JSON généré + push API simulé + horodatage.
30. **V7.1 test_local_llm_fallback.py vert:** DCE Confidentiel -> Mistral 7B local.
31. **V7.1 test_dlq_reconciliation.py vert:** Events stuck -> DLQ -> replay.

**Fleet 46 critères (38 V6/V7.1 single étendus +8 Fleet V7.1):** 19 Fleet = 12 ci-dessus + ClamAV EICAR Fleet, Golden Files 3×400p Fleet 3 clients, Qdrant isolation 0 cross-tenant, MinIO isolation, Postgres isolation, Redis isolation, backup fleet chiffré, restore fleet <30min, monitoring fleet Prometheus, log fleet centralisé sans donnée métier, etc. + mêmes 12 V6 ci-dessus + 8 V7.1 Fleet.

**Total V7.1: 39 Single (31+8) + 46 Fleet (38+8) verts obligatoires**

**Gate BLOQUANT:** Si un critère rouge, interdiction 1er client payant. Script `app/scripts/check_go_nogo.sh` et `check_go_nogo_fleet.sh` = vert obligatoire.

---


#### 12.1 Détail tests bloquants V6 - 7 nouveaux (Source Unique)

- **test_deadline_guardian** : Vérifie blocage dépôt si pièce manquante ou Vault expire avant date limite, fuseau plateforme CEST vs CET, compte à rebours exact J-7/J-2/J-1/H-4.
- **test_alloti_guardian** : Détection marché alloti + séparation lots + similarité mémoire inter-lots <85% (cosinus + Jaccard). Si >85% = alerte orange, >95% = rouge bloquant dépôt.
- **test_enveloppe_separator** : Classification auto 47 pièces (DC1, DC2, DUME, AE, DPGF, BPU, CCAP, CCTP, CCTG, CCAG, RC, CRTI, SOP, SOGED, PGC, PPSPS, DICT, DOE, etc.) tri correct 3 enveloppes candidature/offre/prix-technique + vérification DUME vs DC1/DC2.
- **test_certif_live_checker** : Match exact qualifications demandées (Qualibat 2111, 2211, RGE Qualibat, MASE, OPQIBI) vs Vault A03 + détection expiration pendant durée marché + zone géographique chantier vs implantation entreprise <50km preuve A08.
- **test_pab_detector** : Alerte PAB si écart <-20% orange, <-30% rouge, marge min 6% Admin only, justification 48h générée conforme art. L2122-2.
- **test_contentieux_generator** : Mémoire en réclamation 5-10 pages + mise en demeure 2-3 pages générées avec délais corrects (16j mise en demeure, 30j mémoire réclamation) + calcul intérêts moratoires LME 3×BCE + frais recouvrement 40€ + taux_bce_mensuel.json.
- **test_post_gagne_tracker** : Alertes J-30 échéances OS/récolement/levée réserves/garantie décennale + PV récolement + demande avenant générés + montant avenant max 20% = vérification cumul.

Total Single VPS 39 critères = 17 historiques (auth JWT vps_id, filesystem O_NOFOLLOW, Excel FileLock versioning10, MathBox no LLM import, PuLP+OR-Tools conflit, strip financier, Vault J-30 readonly cron, Heartbeat whitelist, Rollback LVM+backup PG+cosign, backup/restore AES-256-GCM <15min, ClamAV EICAR, Golden Files 3×400p <5min, 12 agents trap detector V12, 5 solveurs V12, RBAC provisions, handoff double artefact, agent no euro) + 7 V6 ci-dessus + 8 V7.1 ci-dessus (Pénibilité RH, Vigilance URSSAF, ZAN Trackterres, Syntax Checker, Sourcing API, Local LLM Fallback, DLQ Reconciliation, Fleet License Updater).

Fleet 46 = 39 single + 7 fleet historiques (Qdrant isolation 0 cross-tenant, MinIO isolation, Postgres isolation, Redis isolation, backup fleet chiffré, restore fleet <30min, monitoring fleet Prometheus, log fleet centralisé sans donnée métier) + mêmes 7 V6 + 8 V7.1 Fleet (License Updater, Cosign Verify Fleet, Multi-VPS Backup, Fleet Monitoring, Fleet Heartbeat, Fleet RBAC Centralisé, Fleet Audit Log, Fleet Isolation Tests).

Voir RAPPORT §12 pour gate bloquant check_go_nogo.sh vert.

#### Archive V12 §12 préservée (17 critères historiques)


## 12. Go/No-Go Production - 17 Critères Single VPS / 24 Fleet - Gate Bloquant Unique

> **RÈGLE:** Gate bloquant avant 1er client payant. Pas avant 1er commit. `check_go_nogo.sh` et `check_go_nogo_fleet.sh` doivent être verts. Voir PLAN_MAITRE_V7.1 §10 pour script. Ici définition fonctionnelle critères.

**Single VPS 17 critères (12 +5 ):**

1. **auth JWT vps_id middleware:** JWT vérifié + vps_id obligatoire pas de tenant_id + 2FA TOTP Argon2id. Test: test_auth_jwt_vps.py vert.
2. **filesystem isolation O_NOFOLLOW+fstat+BASE_ROOT non-symlink+owner:** `_check_access(path)` non contournable via symlink / TOCTOU. BASE_ROOT vérifié non symlink au démarrage. O_NOFOLLOW + fstat vérif owner. Test: test_filesystem_nemesis.py vert (10 attaques).
3. **Excel FileLock single worker+versioning10+validate_header:** FileLock pour DPGF concurrent + versioning 10 max + validation header ligne. Test: test_excel_concurrency.py vert.
4. **Math Engine no LLM import:** Aucun import openai/anthropic/langchain/mistralai dans app/engines/math_engine/. Test: test_math_engine_no_llm_import.py scan bloquant vert.
5. **No conflict Garage PuLP+OR-Tools:** Coexistence CBC + OR-Tools sans conflit lib. Test: test_pulp_ortools_no_conflict.py vert.
6. **Strip financier API employee cannot see prices:** API salarié 0 champ prix/marge/provision. Serializer strip_provisions_euros. Test: test_api_employee_cannot_see_prices.py vert + regex € scan 0 occurrence.
7. **Vault J-30 readonly cron is_readonly continue:** Cron J-30 continue même si is_readonly=True (cas hiver suspension). Test: test_vault_j30_readonly.py vert.
8. **Heartbeat whitelist 0 donnée métier DCE/Vault/prix:** Heartbeat support ne remonte que métriques infra (CPU/RAM/disk/uptime) jamais DCE/Vault/prix. Whitelist explicite. Test: test_heartbeat_no_business_data.py vert.
9. **Rollback snapshot LVM+backup PG + cosign verify:** Snapshot LVM avant MAJ + backup Postgres AES-256-GCM + restore <15min objectif 500Mbps + cosign signature image Docker vérifiée. Test: test_backup_restore.py vert.
10. **Backup/restore AES-256-GCM <15min:** Chiffrement backups AES-256-GCM + objectif restore 15min 500Mbps. Test: test_backup_restore_aes.py vert.
11. **ClamAV EICAR scan upload:** Tout upload DCE/Vault scanné ClamAV, EICAR bloqué. Test: test_clamav_eicar.py vert.
12. **Golden Files 3×400p DCE réels parse <5min:** 3 DCE réels 400p chaque (AP-HP, Centre pénitentiaire, Lycée) parse complet <5min. Test: test_golden_files.py vert.

**+5 Critères :**

13. **test_12_agents_trap_detector.py vert:** 12 agents IA qualitative ZERO € (BT, Pénalités, Trésorerie, GME, DC4, RAT, SOGED, Site, Cross-Check, Q/R, Mémoire, Handoff) avec JSON sans € + confiance >0.8. Aucun agent ne calcule €.

14. **test_5_solveurs_ vert:** 5 nouveaux solveurs Garage (bt_projection, penalites_cumul, rep_cost, site_coeff, incoherence_solver) Decimal exact, to_decimal(str), 0 import LLM, tests unitaires avec cas limites + référentiels JSON existants.

15. **test_rbac_provisions.py vert:** Aucune provision € visible salarié sur 12 modules + regex scans DOM 12 pages + API scan + serializer strip + double artefact test provision.

16. **test_handoff_double_artefact.py vert:** Double PDF générés physiquement distincts + 0 occurrence € ni marge dans version salariée + checksum distincts + 2 artefacts log + test_front_no_handoff_leak.

17. **test_agent_no_euro.py vert:** Scan code 12 agents IA aucun calcul €, aucun regex €, aucun champ provision/marge généré côté IA - preuve que IA ne calcule pas euros - seulement Garage.

**Fleet 24 critères (19 +5 ci-dessus):** 19 Fleet = 12 ci-dessus + ClamAV EICAR Fleet, Golden Files 3×400p Fleet 3 clients, Qdrant isolation 0 cross-tenant, MinIO isolation, Postgres isolation, Redis isolation, backup fleet chiffré, restore fleet <30min, monitoring fleet Prometheus, log fleet centralisé sans donnée métier, etc. + mêmes 5 ci-dessus.

**Gate BLOQUANT:** Si un critère rouge, interdiction 1er client payant. Script `app/scripts/check_go_nogo.sh` et `check_go_nogo_fleet.sh` = vert obligatoire.

---

---


## 13. Références Croisées Obligatoires & Règles d'Or pour l'Avenir (Zéro Doublon)

### 13.1 Références Croisées

- Pour **BUILD order, dépendances, gates, graphe, Go/No-Go script, roadmap, suivi** → Voir **PLAN_MAITRE_V7.1** (ex-MES + PLAN_CODAGE fusionnés, ne redéfinit pas modules fonctionnels, réfère "Voir RAPPORT section 7.X").
- Pour **CODE, 23+ ADR, C4, contrats API, schemas DB, mem_limit, infra Docker/OVH, sécurité filesystem, RAG config Qdrant hybrid, MCP code, tests bloquants** → Voir **ENGINEERING-HANDBOOK.md** (pas de redéfinition fonctionnelle modules, juste contrats techniques qui implémentent RAPPORT §7).
- Pour **liste fichiers finale alphabétique propre 230+ fichiers** → Voir **Arborescence.txt** (sans historique, sans delta, marquée pour fichiers ).
- Pour **promesse commerciale, positionnement offensif, prix formule unique, slogan interdit, argumentaire, garanties** → Voir **MANIFESTE.md** (commercial pur, pas de technique modules — réfère §7).
- Pour **Vault A01-A12 détails documents + pipeline J-30** → Ce document §4 source fonctionnelle, Handbook source technique.
- Pour **Finance Warfare 5 tuiles** → Ce document §10 fonctionnel + Handbook contrats API `/api/finance-warfare/*`.
- Pour **28 modules détaillés** → Ce document §7 source unique fonctionnelle.

**Règle inter-doc stricte:**
- Si conflit fonctionnel module (Trigger/IA/Garage/Vue Salarié/Action Patron) → **RAPPORT §7 gagne.**
- Si conflit technique pur (contrat API, schema, mem_limit, code) → **ENGINEERING-HANDBOOK- gagne.**
- Si conflit ordre build/gate → **PLAN_MAITRE_V7.1 gagne (ex-MES + PLAN_CODAGE fusionnés).**

### 13.2 Règles d'Or pour l'Avenir (Maintenabilité — Non Négociable)

1. **28 modules:** Toute modification module (Trigger, IA, Garage, Vue, Action) ne doit être faite QUE dans RAPPORT.md section 7.X. Autres docs citent référence croisée uniquement "Voir RAPPORT section 7.X" — ZÉRO copier-coller. Si vous voyez définition module ailleurs, c'est une erreur bloquante à corriger.

2. **Pas de tableaux récap en double:** Un seul tableau récap autorisé dans tout pack: celui de RAPPORT section 8. Supprimer tableaux récap en double dans MANIFESTE, HANDBOOK, ARBO.

3. **Pas de répétition règles d'or (RBAC, Garage, Vault, HANDOFF) plus d'une fois par fichier:** RBAC financier défini UNE SEULE FOIS dans RAPPORT §3.1 + une seule fois technique dans Handbook (contrats). Garage règle ZERO LLM définie UNE FOIS §9 + une fois Handbook ADR. Vault J-30 UNE FOIS §4 + une fois Handbook technique. HANDOFF double artefact UNE FOIS §7.12 + une fois Handbook code.

4. **Format lisible maintenable:** Document unique avec table des matières claire, format unique, lisible, maintenable, sans historique collé ni annexes redondantes dupliquées.

5. **Zero copier-coller inter-docs:** Si contenu existe ailleurs (ex: définition BT Guardian), mettre référence croisée pas copier. Seule exception: RAPPORT est autorisé à contenir tout car source unique. Autres docs ne doivent pas recopier modules.

6. **Taille cible respectée:** RAPPORT exhaustif car source unique 33 modules détaillés Trigger/IA/Garage/Vue/Action pour 7.1 à 7.33 + tableau recap unique §8 + garage + dashboards + Go/No-Go + conclusion. MANIFESTE 10-15 pages max commercial pur. HANDBOOK 40-60 pages technique pur 63 ADR. PLAN_MAITRE_V7.1 25-30 pages Build Chain + Pilotage (ex-MES + PLAN_CODAGE fusionnés). Arborescence liste unique propre.

---

#### Archive V12 §13 préservée

## 13. Références Croisées Obligatoires & Règles d'Or pour l'Avenir (Zéro Doublon)

### 13.1 Références Croisées

- Pour **BUILD order, dépendances, gates, graphe, Go/No-Go script, roadmap, suivi** → Voir **PLAN_MAITRE_V7.1** (ex-MES + PLAN_CODAGE fusionnés, ne redéfinit pas modules fonctionnels, réfère "Voir RAPPORT section 7.X").
- Pour **CODE, 23 ADR, C4, contrats API, schemas DB, mem_limit, infra Docker/OVH, sécurité filesystem, RAG config Qdrant hybrid, MCP code, tests bloquants** → Voir **ENGINEERING-HANDBOOK.md** (pas de redéfinition fonctionnelle modules, juste contrats techniques qui implémentent RAPPORT §7).
- Pour **liste fichiers finale alphabétique propre 230+ fichiers** → Voir **Arborescence.txt** (sans historique, sans delta, marquée pour fichiers ).
- Pour **promesse commerciale, positionnement offensif, prix formule unique, slogan interdit, argumentaire, garanties** → Voir **MANIFESTE.md** (commercial pur, pas de technique modules - réfère §7).
- Pour **Vault A01-A12 détails documents + pipeline J-30** → Ce document §4 source fonctionnelle, Handbook source technique.
- Pour **Finance Warfare 5 tuiles** → Ce document §10 fonctionnel + Handbook contrats API `/api/finance-warfare/*`.

**Règle inter-doc stricte:**
- Si conflit fonctionnel module (Trigger/IA/Garage/Vue Salarié/Action Patron) → **RAPPORT §7 gagne.**
- Si conflit technique pur (contrat API, schema, mem_limit, code) → **ENGINEERING-HANDBOOK- gagne.**
- Si conflit ordre build/gate → **PLAN_MAITRE_V7.1 gagne (ex-MES + PLAN_CODAGE fusionnés).**

### 13.2 Règles d'Or pour l'Avenir (Maintenabilité - Non Négociable)

1. ** 12 modules:** Toute modification module (Trigger, IA, Garage, Vue, Action) ne doit être faite QUE dans RAPPORT.md section 7.X. Autres docs citent référence croisée uniquement "Voir RAPPORT section 7.X" - ZÉRO copier-coller. Si vous voyez définition module ailleurs, c'est une erreur bloquante à corriger.

2. **Pas de tableaux récap en double:** Un seul tableau récap autorisé dans tout pack: celui de RAPPORT section 8. Supprimer tableaux récap en double dans MANIFESTE, HANDBOOK, ARBO. S'ils listent modules, doivent référencer tableau unique §8.

3. **Pas de répétition règles d'or (RBAC, Garage, Vault, HANDOFF) plus d'une fois par fichier:** RBAC financier défini UNE SEULE FOIS dans RAPPORT §3.1 + une seule fois technique dans Handbook (contrats). Garage règle ZERO LLM définie UNE FOIS §9 + une fois Handbook ADR. Vault J-30 UNE FOIS §4 + une fois Handbook technique. HANDOFF double artefact UNE FOIS §7.12 + une fois Handbook code. Pas de répétition dans même fichier.

6. **Format lisible maintenable:** Document unique avec table des matières claire, format unique, lisible, maintenable, sans historique collé ni annexes redondantes dupliquées. Un seul flow logique: Vision → RBAC → Vault → Moteurs → 12 Modules détaillés une seule fois → Tableau unique → Garage → Dashboards → Go/No-Go → Conclusion.

7. **Zero copier-coller inter-docs:** Si contenu existe ailleurs (ex: définition BT Guardian), mettre référence croisée pas copier. Seule exception: RAPPORT est autorisé à contenir tout car source unique. Autres docs ne doivent pas recopier modules.

8. **Taille cible respectée:** RAPPORT exhaustif car source unique 12 modules détaillés Trigger/IA/Garage/Vue/Action pour 4.1 à 4.10 + 5 + 6 + tableau recap unique. MANIFESTE 10-15 pages max commercial pur. HANDBOOK 40-60 pages technique pur 23 ADR. MES 15-20 pages Build Chain. PLAN_CODAGE 15-20 pages 10 builds. Arborescence liste unique propre.

---

---


## 14. Conclusion Architecte — Vision Système d'Arme Marge & Trésorerie

Cette édition V6 Fusion transforme SMART_AO de détecteur vices forme en **système d'exploitation complet de l'entrepreneur BTP** — de la veille à la réclamation, 28 modules couvrant 500k€ à 1,5M€ de risque par marché complexe.

**Ce que nous construisons:**
- Pas outil chiffrage. Système protection marge + note + survie juridique.
- Salarié apporte intelligence terrain (métrés h, photos site, saisie exutoire, relecture Q/R) guidé 12 étapes sans €.
- IA apporte vigilance exhaustive (28 agents RAG lisent 400p DCE, extraient 50 contraintes, détectent 4 familles + 24 pièges avancés avec page/extrait/confiance ZERO €) — ne calcule jamais €.
- Garage Math apporte vérité des euros Decimal 28 exact (5 solveurs historiques + 10+ nouveaux — bt_projection INSEE, penalites_cumul, treasury BFR, rep_cost ADEME, site_coeff, incoherence_solver, capacite_financiere, pab_detector, materiaux_shield, eplusc_calculator, risques_generator) avec référentiels INSEE/ADEME/Météo France.
- Patron garde clé coffre RBAC étanche (strip_provisions_euros + double artefact HANDOFF+ + test_front_no_price_leak + test_rbac_provisions).

**C'est l'étanchéité financière qui fait confiance Patron:** Aucune provision € visible salarié = Patron peut déléguer sans peur fuite marge vers salariés/centre travaux. Tests `test_api_employee_cannot_see_prices` + `test_rbac_provisions` + `test_handoff_double_artefact` + `test_front_no_price_leak` verts bloquants.

**C'est le calcul exact 11 solveurs + INSEE ADEME Météo France qui fait différence entre marché gagné et chantier qui tue entreprise:** Exemples réels intégrés: BT sans butoir -47k€, pénalités sans plafond 124k€ 12% CA, BFR -180k€ pic M4-6, solidarité élargie 180k€, DC4 cumul 62% >50%, RAT manquant 18.5k€ SS4, REP 4.2k€, site occupé +15% MO 18k€ +2 sem, oublis DPGF 3.1k€ + écarts 18.2k€, Q/R enjeu 288k€ neutralisable, acier +40% 90k€, PAB -27% risque élimination, RSE -3 points/20, visite oubliée = 0€, DC1 dans offre = élimination, avenant oublié 30k€, recours non fait = 1M€ perdu.

**Workflow V6 complet:** DCE déposé → 28 modules IA + 11 solveurs Garage → Go/No-Go 24 critères chiffré sécurisé → Métré temps corrigé site → SOGED → Mémoire Booster 18/20 avec preuves A08 <50km + Gantt Météo France + RE2020 + matrice RC → Q/R tactique 8 questions opposables → Docs Admin DC1/DC4 génération + Finance Warfare Dashboard 5 tuiles provisions à valider + Deadline Guardian + Alloti Guardian + Enveloppe Separator + Certif Live Checker + Visite Auto + PAB Detector + Matériaux Shield + RSE Booster + Variante Guardian + Prix-Mémoire Coherence → Handoff → Chiffrage Admin validation provisions → ZIP 3 enveloppes + Mémoire + SOGED + DC4 + Q/R → Dépôt Profil Acheteur → Statut GAGNE → HANDOFF+ Book 30p double artefact expurgé/complet + Post-Gagné Tracker échéances → Contentieux Generator si besoin → Chantier sécurisé.

**Chaque euro affiché Patron est calculé Garage Math Decimal exact, jamais halluciné LLM. Chaque information vue Salarié purgée tout prix via strip_provisions_euros + double artefact séparé. C'est la confiance. C'est la différence.**

---

> **SMART_AO V6 Fusion — Source Unique Fonctionnelle 28 Modules Exhaustive — Fin Document Principal**

---

#### Archive V12 §14 préservée

## 14. Conclusion Architecte - Vision Système d'Arme Marge & Trésorerie

Cette édition transforme SMART_AO de détecteur vices forme (/) en **système d'arme juridique et financière protection marge et trésorerie + mémoire booster 18/20 + HANDOFF+ book double artefact étanche**.

**Ce que nous construisons:**
- Pas outil chiffrage. Système protection marge.
- Salarié apporte intelligence terrain (métrés h, photos site, saisie exutoire, relecture Q/R) guidé 12 étapes sans €.
- IA apporte vigilance exhaustive (12 agents RAG lisent 400p DCE, extraient 50 contraintes, détectent 4 familles + 10 pièges avancés avec page/extrait/confiance ZERO €) - ne calcule jamais €.
- Garage Math apporte vérité des euros Decimal 28 exact (5 solveurs historiques + 5 nouveaux - bt_projection INSEE, penalites_cumul, treasury BFR, rep_cost ADEME, site_coeff, incoherence_solver) avec référentiels INSEE/ADEME/Météo France.
- Patron garde clé coffre RBAC étanche (strip_provisions_euros + double artefact HANDOFF+ + test_front_no_price_leak + test_rbac_provisions).

**C'est l'étanchéité financière qui fait confiance Patron:** Aucune provision € visible salarié = Patron peut déléguer sans peur fuite marge vers salariés/centre travaux. Tests `test_api_employee_cannot_see_prices` + `test_rbac_provisions` + `test_handoff_double_artefact` + `test_front_no_price_leak` verts bloquants.

**C'est le calcul exact 5 solveurs + INSEE ADEME Météo France qui fait différence entre marché gagné et chantier qui tue entreprise:** Exemples réels intégrés: BT sans butoir -47k€, pénalités sans plafond 124k€ 12% CA, BFR -180k€ pic M4-6, solidarité élargie 180k€, DC4 cumul 62% >50%, RAT manquant 18.5k€ SS4, REP 4.2k€, site occupé +15% MO 18k€ +2 sem, oublis DPGF 3.1k€ + écarts 18.2k€, Q/R enjeu 288k€ neutralisable.

**Workflow :** DCE déposé → 12 modules IA + 5 solveurs Garage → Go/No-Go 17 critères chiffré sécurisé → Métré temps corrigé site → SOGED → Mémoire Booster 18/20 avec preuves A08 <50km + Gantt Météo France + RE2020 + matrice RC → Q/R tactique 8 questions opposables → Docs Admin DC1/DC4 génération + Finance Warfare Dashboard 5 tuiles provisions à valider → Handoff → Chiffrage Admin validation provisions → ZIP 3 enveloppes + Mémoire + SOGED + DC4 + Q/R → Dépôt Profil Acheteur → Statut GAGNE → HANDOFF+ Book 30p double artefact expurgé/complet → Chantier sécurisé.

**:** Chaque euro affiché Patron est calculé Garage Math Decimal exact, jamais halluciné LLM. Chaque information vue Salarié purgée tout prix via strip_provisions_euros + double artefact séparé. C'est la confiance. C'est la différence.

---

> **

---

---

# ANNEXES V6 FUSION - SOURCE UNIQUE 28 MODULES





## ANNEXE A — DCE Trap Detector: 4 Familles + Routage 28 Modules

### A.1 Famille 1 — Pièces Contractuelles & Risques Juridiques
Routage: BT → 7.1, pénalités → 7.2, GME → 7.4, DC4 → 7.5, marque → 7.9, PAB → 7.19, variante → 7.17, deadline → 7.13, alloti → 7.14, enveloppe → 7.21, contentieux → 7.23.

### A.2 Famille 2 — Aspects Techniques & Site
Routage: site → 7.8, RAT → 7.6, SOGED → 7.7, cross-check → 7.9, E+C- → 7.28, RSE → 7.15.

### A.3 Famille 3 — Financiers & Quantitatifs
Routage: BT →7.1, trésorerie →7.3, SOGED →7.7, cross-check →7.9, matériaux →7.18, capacité financière →7.25, PAB →7.19, cohérence prix-mémoire →7.16.

### A.4 Famille 4 — Autres Pièges Fréquents
Routage: DC4 →7.5, Q/R →7.10, GME DC1 →7.4, deadline →7.13, alloti →7.14, visite →7.20, certif →7.24, MAPA →7.27, tableau risques →7.26.

---



## ANNEXE B — Vault A01-A12 Détail Fonctionnel Complet (Complément §4)

### B.1 Règles Absolues des 12 Documents Core
- Versioning 10 max FIFO, FileLock single worker, O_NOFOLLOW + fstat.
- Upload: OCR Tesseract + BTP dict custom + extraction SIRET/dates/activités + Qdrant vault collection.
- Workflow validation: Salarié dépôt A VALIDER -> Admin valide -> vert. Si EXPIRE -> rouge bloquant.
- Pipeline J-30: Cron quotidien 06h00, même si `is_readonly=True` (cas suspension hiver chantier). Emails J-30/J-7/J-1 + badge. Test `test_vault_j30_readonly.py` vert.
- Cohérence SIRET: Kbis SIRET = URSSAF SIRET = DGFIP SIRET = Assurance SIRET. Si un chiffre diffère => rouge bloquant. 30% éliminations formelles évitées.

### B.2 Mapping Vault vers Mémoire Booster & Générateurs
- A08 Preuves Terrain -> Mémoire Booster photos géolocalisées <50km auto.
- A09 Environnemental -> Mémoire volet RE2020 + FDES.
- A10 Méthodologie -> Mémoire méthode + PPSPS + SOGED modèles + SOP SS4.
- A03 Qualifications -> DC4 génération + Mémoire moyens matériels.
- A04 Humains -> Mémoire moyens humains CV CACES AIPR.
- A06 Références -> Mémoire références chantiers similaires.
- A02 Assurances -> Dossier Admin assurances.

### B.3 Les 39 Documents Hors Scope (Liste Non Limitative)
Pour traçabilité, 39 documents type hors Vault core mais gérés en upload DCE: notice sécurité, plan install chantier, diagnostic amiante, diagnostic plomb, étude sol, PGC SPS, notice acoustique, notice thermique RE2020, notice accessibilité PMR, etc. Non stockés Vault, stockés DCE collection.

---



## ANNEXE C — Cockpit Administrateur — Modules Détail Fonctionnel

### C.1 Module Personnalisation Entreprise
Saisie logo, couleurs, base de prix PU moyens (béton, BA13, peinture...), taux horaires MO, coeff site défaut modifiable, modèles mémoire, modèles SOGED, modèles DC4. Versioning.

### C.2 Module Documentation Vault
Dashboard A01-A12 (voir §10.2) + upload + OCR + validation + J-30.

### C.3 Gestion Comptes Salariés
Création salarié email/mot de passe, rôle salarié/admin, 2FA TOTP, sandbox isolé filesystem BASE_ROOT /data/minio/{user_id} + O_NOFOLLOW + owner check. Test nemesis. Révocation accès. Audit log connexions.

### C.4 Appels d'Offres en Cours — Vue Globale Kanban
Kanban 12 colonnes workflow + filtres par salarié, état, Go/No-Go, date limite, montant estimé. Cartes AO avec progression %, badges pièges rouges, temps restant Q/R. Drag & drop Admin + rejet avec raison obligatoire.

### C.5 Contrôle Financier & Validation (Cœur)
Liste provisions 7 types à valider (BT, pénalités, BFR, RAT, REP, site, omission) + montants + graphs + commentaires salarié (temps, surfaces, photos) + bouton Valider/Provisionner/Rejeter + commentaire + audit log. Bloque dépôt si non validées.

### C.6 Analytics & Performance
Taux Go/No-Go, marge moyenne par type chantier, pièges fréquents, temps moyen analyse, taux transfo Gagné/Perdu, BFR moyen, coût REP moyen. Graphiques sans données métier si test heartbeat.

### C.7 Paramètres & Sécurité
Clé API Mistral EU, opt-in DeepSeek/hors UE disclaimer RGPD case, backup AES-256-GCM config, LVM snapshot, cosign verify, 2FA, argon2id, clé Qdrant, Redis AOF, ClamAV.

### C.8 Notifications & Alertes
Emails J-30 Vault, alerte nouveau DCE, alerte Q/R J-2, alerte piège critique 7.1-7.9, alerte BFR pic, alerte provision à valider, WebSocket temps réel wizard.

### C.9 V6 — Deadline Guardian Dashboard
Compte à rebours par AO, checklist pièces, alertes SMS/email/push J-7/J-2/J-1/H-4, blocage dépôt si incomplet, historique horodaté.

### C.10 V6 — Contentieux & Post-Gagné Dashboard
Calendrier échéances post-signature, alertes J-30, génération PV/avenant, suivi avenants cumul vs 20%, boutons mémoire réclamation / mise en demeure.

### C.11 V6 — Qualifications & Capacité Financière Dashboard
Tableau match qualif demandé/détenu/manquant, planning renouvellement J-90/J-60/J-30, ratios financiers calculés vs seuils.

---



## ANNEXE D — Wizard Salarié 12 Étapes Détail UX + Règles Gestion

### D.0 Manifeste UX
"Un bouton à la fois, zéro erreur possible." Barre progression linéaire + % + Temps restant estimé basé sur moyenne chantiers similaires. Autosave toutes les 30s. Aide contextuelle DTU/CCAG/R2111-7 au survol. Pas de jargon. Illustrations pastillées plans.

### D.1 Étape 1 Identification DCE
Champ URL BOAMP/PLACE auto extraction via MCP boamp_search ou upload ZIP DCE drag & drop. SIRET acheteur auto extraction + nom MOA/MOE + date limite Q/R + date limite dépôt + type procédure. Bouton Suivant vert gros.

### D.2 Téléchargement Documents DCE — Panoplie Boutons
Grille boutons upload par type: RC, CCAP, CCTP 00, CCTP lots (multi), DPGF/BPU Excel (validation header obligatoire — colonnes Qté/PU...), Plans PDF (multi), Diags, Planning, AE, DC1, Notice site. Chaque bouton change couleur vert quand upload + OCR OK. Progression + taille. Worker async PyMuPDF <2s/page + Docling worker séparé si >10p image. FileLock.

### D.3 Analyse IA 28 Modules — 2 Colonnes
Lancement analyse bouton "Analyser DCE (2-5 min)". Backend lance 33 agents IA quali + 16 solveurs Garage en parallèle Celery. WS progression agent par agent. UI 2 colonnes: Gauche Checklist conformité (12 docs présents, SIRET cohérent, J-30 OK) + Droite Pièges Prix badge rouge/jaune sans €. Chaque piège carte avec page extrait + niveau + accès Q/R. Pas de €.

### D.4 Go/No-Go Gate Humaine
Dashboard Go/No-Go : 39 critères checklist (17 historiques +7 V6 +8 V7.1). Chaque critère badge vert/rouge + explication quali. Bouton salarié "Proposer GO" avec commentaire + bouton "Proposer NO-GO" avec raison. Admin validation finale GO/NO-GO obligatoire.

### D.5 Visite Site
Case à cocher 7 contraintes + upload photos terrain (EXIF conservé) + notice + saisie distance agence-chantier + commentaires qualitatifs (ex: "Accès camion 12m impossible — Prévoir transpalett). Extraction auto CCTP 00 contraintes en suggestions.

### D.6 Métré & Quantitatif
Saisie Qté m2/ml/u + temps h: tableau DPGF-like sans € (Qté + Temps h + Observations). Application coeff site auto (si site occupé +15% => temps corrigé affiché sans € "Temps base 10h -> Temps corrigé 11.5h (+15% occupé)"). Pastilles plans: clic sur plan pour ajouter point comptage portes.

### D.7 Rédaction Mémoire Technique Booster 18/20
Génération 80% auto bouton "Générer mémoire". Affichage mémoire DOCX preview sans prix. Sections: ADN local 50 contraintes, preuves A08 <50km photos, planning Gantt PNG, RE2020, matrice conformité. Saisie salarié commentaires techniques. Sauvegarde brouillon.

### D.8 Génération SOGED & AdminDocs
Wizard SOGED: saisie exutoires 7 flux + km + tri. Génération SOGED PDF bouton. AdminDocs: DC1 groupement + DC4 sous-traitants saisie nom/nature/rang/montant (montant masqué après validation salarié).

### D.9 Q/R Tactique
Liste 8 questions max générées tri enjeu masqué salarié. Saisie salarié relecture technique, ajustement langue métier. Bouton "Valider relecture tech". Admin validation juridique finale + export DOCX.

### D.10 TechDocs
Génération PPSPS, DOE modèle, SOGED, DICT.

### D.11 Validation Finale Handoff
Preview Book expurgé sans € + checklist dépôt (Vault OK, provisions validées Admin, mémoires, SOGED, DC4, Q/R). Bouton Handoff vers Admin vert gros.

### D.12 Ce Que Salarié Ne Voit JAMAIS
PU, marge, coeff vente, provisions €, BFR pic €, coût REP €, provision amiante €, provision omission €, exposition pénalités €, trésorerie €, montants marchés HT, marge nette, coût caution, Vault montants, Analytics marge, PAB estimation, capacité financière ratios, contentieux stratégie, tableau risques comité. Test bloquant `test_front_no_price_leak` + `test_api_employee_cannot_see_prices`.

---



## ANNEXE E — RAG Pipeline Hybrid Fonctionnel Détaillé (Synthèse Non-Technique)

**Pourquoi BGE-M3:** multilingue FR/EN, 1024 dim, support dense+sparse natif, on_disk = économise RAM, meilleur recall BTP (CCAG, DTU, CCTP).

**4 Collections Qdrant (sans préfixe tenant — single-tenant pur):**
- dce: RC/CCAP/CCTP/Plans/BPU/Diags/Planning/AE/DC1/Notices — chunking intelligent par type (RC 800 tokens, CCTP 1200 tokens overlap titre DTU, DPGF ligne par ligne Excel, Plans OCR bloc)
- vault: A01-A12 OCR + dates + SIRET + activités
- chantiers: historique prix chantiers gagnés/perdus (m2, PU, temps, ex: cloison BA13 45€/m2 2024 dept 38)
- traps: base connaissance pièges 200 cas-types (ex: BT sans butoir, pénalités sans plafond...)

**Hybrid Search:** Query -> embedding BGE-M3 dense + sparse SPLADE -> Qdrant search dense top 20 + sparse top 20 -> RRF k=60 -> top 10 chunks avec page/extrait/confiance. Fallback FTS Postgres `btp_french` custom dict si Qdrant down (table `documents_fts`).

**Use Cases:** DCE Trap Detector, Vault Semantic Search, Chantier Matcher mémoire infinie prix, QA mémoire.

**Fallback Zéro Erreur:** Si RAG tombe, outil survit en mode dégradé FTS, pas d'exception bloquante.

---



## ANNEXE F — MCP Externe + Interne Fonctionnel (Synthèse)

### F.1 Pourquoi MCP > API directe
MCP = standard outil pour agents IA. Au lieu coder appel API BOAMP/Pricing direct dans agent, on expose tool MCP que agent appelle via host unique. Avantage: isolation, audit log, versioning, test unitaire tools, réutilisabilité.

### F.2 MCP Externe BOAMP/PLACE — 3 Tools
- **boamp_search:** Input: {cpv: ["45210000"], dept: ["38","69"], montant_min: 50000, date_depuis: "2026-07-01"} Output: liste AO (titre, MOA, date limite, valeur estimée, URL DCE)
- **boamp_get_dce:** Input: {url_ao} -> Download ZIP DCE -> upload worker -> analyse auto. Gère captcha PLACE via 2captcha fallback.
- **boamp_track:** Suivi AO favoris + alerte email si DCE modifié (nouvelle version RC) + J-30 dépôt + rappel Q/R J-2.
Radar 6h cron: scan BOAMP nouveautés correspondant profil Vault (ex: Qualibat 2112 + dept 38) + notif.

### F.3 MCP Interne 3 Servers Cœur
**Filesystem MCP Server — 13 tools complets + Roots flow — VERSION COMPLÈTE NON SIMPLIFIÉE:**
Tools: read_file, write_file, list_dir, search_files, get_file_info, create_dir, move_file, delete_file, read_excel_sheet, write_excel_sheet, search_text_in_files, get_vault_doc, list_vault. Sécurité `_check_access(path)` non négociable: BASE_ROOT vérifié non symlink au démarrage + O_NOFOLLOW + fstat + owner check + TOCTOU protection + path traversal bloqué. Sandbox /data/minio/{user_id}. Audit log chaque tool call. Roots flow: client MCP donne root /data/minio -> serveur vérifie within root.

**Excel MCP:** Thread-safety FileLock single worker + versioning 10 + validate_header DPGF (colonnes obligatoires: Désignation, Qté, U). 4 tools: read_dpgf, write_dpgf_cell, validate_dpgf_header, get_version.

**Pricing Memory MCP — CUSTOM 4 tools validés (pas officiel):**
- get_chantier_price: historique prix moyen m2 par type ouvrage dept année ex: BA13 45€/m2 2024 38.
- detect_sous_chiffrage: compare PU saisi vs base prix Admin + historique. Flag rouge si -12% = 10k€/ligne potentiel oubli.
- save_price_after_win: après GAGNE, sauvegarde prix dans chantiers collection pour futur Matcher.
- compare_pu_base_prix: compare DPGF entier vs base prix ligne par ligne écart >2%.

Host unique `app/mcp/internal/host.py` tourne thread FastAPI pas process séparé + audit log middleware `mcp_audit_log.py`.

### F.4 Décision Finale Tableau
| MCP | Pris ? | Pourquoi |
|---|---|---|
| Filesystem officiel @modelcontextprotocol/server-filesystem | Fork Python custom | Sécurité O_NOFOLLOW + owner + non-symlink + TOCTOU + owner check nécessaire BTP — version JS non auditable |
| Excel officiel | Fork custom | FileLock + versioning 10 + validate_header BTP nécessaire |
| Memory officiel @modelcontextprotocol/server-memory | NON | Risque fuite Vault/données métier via knowledge graph non chiffré — on fait Pricing Memory custom 4 tools isolés |
| Pricing Memory custom | OUI | 4 tools validés — CŒUR métier historique prix BTP <50km |
| BOAMP externe | OUI 3 tools | Veille AO auto + download DCE + tracking |

---



## ANNEXE G — Stack Technique & Données — Synthèse Fonctionnelle

### G.1 Stack une page rappel
- Frontend: Next.js 15 App Router + TypeScript + shadcn/ui + Tailwind + React Query + Zustand + Recharts Finance Warfare + React-PDF viewer + OpenLayers pastilles plans.
- Backend: FastAPI + SQLAlchemy 2.0 single-tenant 0 tenant_id + Alembic migrations + Postgres 16 + MinIO presigned + Qdrant 1.11 hybrid on_disk + Redis 7.2 AOF + Celery 5.4 worker + BGE-M3 FlagEmbedding + Mistral API EU `mistral-large-latest` + Tesseract OCR FR + PyMuPDF + pdfplumber + Docling worker séparé + ClamAV.
- Garage Math: PuLP + OR-Tools + Decimal 28 + référentiels JSON (bt_indices, ademe_dechets, coeffs_site, meteo_france, amiante_ss4, **V6:** indices_matériaux, seuils_eplusc, fdes_produits, ratios_financiers, taux_bce, jurisprudence).
- MCP: 3 internes + BOAMP externe.
- Infra: Docker Compose + OVH VPS 16/32Go Ubuntu 24.04 + systemd + NGINX reverse proxy + Let's Encrypt + backup AES-256-GCM S3 compatible OVH Object Storage + LVM snapshot + Prometheus + Grafana + Loki logs sans donnée métier + cosign image verify + heartbeat whitelist.
- Sécurité: JWT HS256 vps_id middleware + Argon2id + TOTP 2FA + O_NOFOLLOW + fstat + BASE_ROOT non-symlink + owner check + Excel FileLock + no LLM import mathbox + strip financier + Vault J-30 readonly cron continue + ClamAV EICAR + AES-256-GCM backup + cosign.

### G.2 Modèles de Données Backend (Résumé)
`app/models/vault_core.py` SINGLE-TENANT PUR 0 NO_TID: id, type A01-A12, filename, siret_extrait, date_validite, statut (A VALIDER/VALIDE/EXPIRE), version, file_path MinIO, ocr_text, embedding_id Qdrant, created_by user_id.
`app/models/project.py`: state machine 12 états + rejection_reason + dce_path + analyse JSON traps + provisions JSON + vault_ids + salarié_id + métré JSON + site_contraintes JSON + mémoire_path + soged_path + q/r path + book complet/expurgé paths.
`app/models/users.py`: email, password_hash Argon2id, role admin/salarié, totp_secret, is_active.
**V6:** `app/models/contentieux.py`: recours, mise_en_demeure, delais, statut.
**V6:** `app/models/post_gagne.py`: echeances, avenants, recolement, reserves.

Voir Handbook pour 23+ ADR techniques.

---



## ANNEXE H — Blocs de Dépendance — Ordre Implémentation (Logique Pas Calendaire)

**Macro Mapping:** 10 Builds (0,1,2,3,3.5,4,4.5,5,6,7,8).

- **Build 0 — Fondation Infra Single-Tenant Pur:** OVH VPS 16/32, Docker Compose, Postgres, MinIO, Qdrant, Redis AOF, FastAPI squelette, auth JWT vps_id + 2FA TOTP Argon2id, filesystem O_NOFOLLOW, backup AES-256-GCM. Gate 0: auth + filesystem + backup vert.
- **Build 1 — Vault A01-A12 + SIRET Guardian + J-30:** Upload worker PyMuPDF, OCR, SIRET extraction cohérence, Qdrant vault collection, cron J-30 readonly continue, badge. Gate 1: Vault + SIRET + J-30 vert.
- **Build 2 — ADN Extractor + Smart IA Upload:** ADN 50 contraintes, RAG dce collection, BGE-M3 on_disk, embedding_engine.py, fallback FTS btp_french. Gate 2: ADN + Upload vert.
- **Build 3 — DCE Trap Detector 4 Familles:** 28 agents RAG CCAG/CCP/DTU, classification 4 familles, JSON traps, wizard étape 3. Gate 3: 28 agents vert agent_no_euro.
- **Build 3.5 — Garage Math Historique + Excel + FileLock:** Port BTP ENGINE ChiffrageEngine, chiffrage_pulp, treasury, planning_ortools, coeff_site v1, Excel MCP FileLock single worker versioning10 validate_header. Gate 3.5: 5 solveurs histo + Excel vert no LLM import.
- **Build 4 — Wizard Salarié 10 étapes + Cockpit Admin 8 tuiles + RBAC financier + Strip:** Wizard 10 étapes UX 1 bouton + cockpit + RBAC strip_provisions_euros + test_front_no_price_leak. Gate 4: RBAC + wizard vert.
- **Build 4.5 — 10+ Solveurs Garage Étendus + Référentiels INSEE/ADEME/Météo/Matériaux/E+C-/Financiers:** bt_projection, penalites_cumul, rep_cost, site_coeff v2, incoherence_solver, capacite_financiere, pab_detector, materiaux_shield, eplusc_calculator, risques_generator. Gate 4.5: 11 solveurs vert Decimal exact.
- **Build 5 — 28 Modules Avancés Anti-Faillite + Anti-Élimination fonctionnel:** Implémentation fonctionnelle 28 modules (Trigger/IA/Garage/Vues/Action) + Finance Warfare Dashboard 5 tuiles + Q/R tactique generator + Vault Dashboard + SOGED + RAT + Site + Cross-Check + Deadline + Alloti + RSE + Coherence + Variante + Matériaux + PAB + Visite + Enveloppe + Post-Gagné + Contentieux + Certif + Capacité + Tableau Risques + MAPA + E+C-. Gate 5: 28 modules vert + RBAC provisions + Finance Warfare.
- **Build 6 — Mémoire Booster 18/20 + MCP BOAMP/PLACE + MCP Interne Filesystem/Pricing:** generator_memoire avec A08 <50km + Gantt Météo France OR-Tools + RE2020 FDES + matrice RC + MCP BOAMP 3 tools + Filesystem MCP 13 tools + Pricing Memory 4 tools + host.py. Gate 6: mémoire + MCP vert.
- **Build 7 — HANDOFF+ Double Artefact + Handoff Dashboard + Go/No-Go 24 critères + ClamAV + Backup/Restore + Cosign:** generator_handoff double artefacts physiquement distincts + Handoff Dashboard double log + check_go_nogo.sh 24 critères vert + ClamAV EICAR + backup/restore <15min + cosign verify. Gate 7: HANDOFF double artefact + Go/No-Go 24 vert + backup vert.
- **Build 8 — Fleet 31 critères + Golden Files 3×400p DCE + Monitoring Prometheus + Heartbeat whitelist 0 métier:** Fleet isolation tests, 3 golden files parse <5min, Prometheus/Grafana/Loki sans donnée métier, heartbeat whitelist test. Gate 8 Fleet: 31 critères vert + fleet tests vert.

Voir PLAN_MAITRE_V7.1 §6 pour graphe dépendances + gates détaillés.

---



## ANNEXE I — Go/No-Go 24 Critères Détail + Tests Bloquants (Complément §12)

### I.1 Liste Tests Bloquants
- test_auth_jwt_vps.py
- test_filesystem_nemesis.py (10 attaques symlink/TOCTOU/path traversal)
- test_excel_concurrency.py
- test_math_engine_no_llm_import.py (scan import)
- test_pulp_ortools_no_conflict.py
- test_api_employee_cannot_see_prices.py (API scan champs interdits)
- test_vault_j30_readonly.py (cron continue readonly)
- test_heartbeat_no_business_data.py (whitelist CPU/RAM/disk/uptime pas DCE/Vault/prix)
- test_backup_restore.py
- test_backup_restore_aes.py
- test_clamav_eicar.py
- test_golden_files.py (3×400p DCE <5min)
- test_28_agents_trap_detector.py
- test_10_solveurs.py
- test_rbac_provisions.py (0 € salarié)
- test_handoff_double_artefact.py (0 € expurgé + 2 artefacts checksum)
- test_agent_no_euro.py (agents IA 0 calcul €)
- test_handoff_irreversible.py (seul Admin GAGNE)
- test_front_no_price_leak.spec.ts (DOM 28 modules 0 €)
- test_front_no_handoff_leak.spec.ts (URL admin non devinable salarié)
- **V6:** test_deadline_guardian.py
- **V6:** test_alloti_guardian.py
- **V6:** test_enveloppe_separator.py
- **V6:** test_certif_live_checker.py
- **V6:** test_pab_detector.py
- **V6:** test_contentieux_generator.py
- **V6:** test_post_gagne_tracker.py

### I.2 Marge Nette Recalculée Honnête
Exemple marché type:
- CA HT 800k€, déboursé sec 600k€ (75%), marge brute 200k€ (25%), frais généraux 12% (96k€), marge nette avant aléas 104k€ (13%). Si pièges non détectés: BT -47k€ + pénalités 16k€ provision + BFR coût caution 960€ + REP 4.2k€ + RAT 18.5k€ + site 18k€ + omission 3.1k€ + matériaux acier 90k€ + PAB négociation 50k€ = -247k€ => marge nette -143k€ = faillite. Avec SMART_AO détection + provisions 247k€ + Q/R neutralisation 50% => marge nette sauvée 50k€+. Calcul honnête, pas garantie.

---



## ANNEXE J — Conclusion Étendue — Ce Que la Concurrence Ne Comprend Pas

**Ce que concurrence ne comprend pas:**
- BTP pas SaaS classique: chaque AO est unique, 400p CCTP différent, pièges cachés, pas process standardisable Excel.
- Souveraineté pas argument marketing mais conformité RGPD + AI Act + secret affaires CCTP + prix.
- Single-tenant pur pas surcoût mais simplification sécurité + conformité + isolation + coût rentable dès 1er client (VPS 80€/mois).
- Garage Math pas bullshit: LLM hallucine 15% chiffres, BTP ne tolère pas 1% erreur marge = faillite.
- RBAC financier pas fonctionnalité mais confiance Patron: si salarié voit marge, fuite = mort entreprise.
- Vault + SIRET pas gadget mais 90% éliminations évitables via cohérence docs.
- Mémoire Booster 18/20 pas rédaction mais preuve matérielle <50km + Gantt météo + RE2020 + matrice RC = note maximale.
- HANDOFF+ pas export PDF mais pont AO->chantier avec double artefact étanche = Conducteur démarre sans voir marge mais avec risques qualitatifs + kit admin complet.
- **V6:** 28 modules pas surcharge mais couverture complète: on ne perd pas un marché pour une connerie (Deadline, Alloti, Enveloppe, Visite, Certif), on ne signe pas sa faillite (BT, Matériaux, PAB, BFR), on gagne la note (RSE, Coherence, Mémoire), on gère après (Post-Gagné, Contentieux).

**Notre engagement :**
- Code single-tenant pur vérifiable (0 tenant_id).
- Aucune donnée ne sort VPS sans opt-in explicite disclaimer RGPD.
- Chaque euro calculé Garage Decimal exact jamais LLM.
- Tests Go/No-Go 24 critères bloquants avant 1er client payant (responsabilité).
- Documentation maintenable (ce doc) + 5 docs complémentaires sans doublon.
- Formation 2h salarié + 2h Admin cockpit.
- Support souverain EU.

---



## ANNEXE K — Détail Exhaustif Modules 7.1 à 7.12 (Cas Réels + Formulaires + Workflows)

*(Le contenu détaillé des modules 7.1 à 7.12 reste identique à la V5 source, enrichi des corrections juridiques V6 intégrées dans les sections 7.1 à 7.12 ci-dessus. Pour la complétude documentaire, les cas réels AP-HP 412p, NOVO, Lycée 12M€, EHPAD 2M€, et workflows pas à pas restent valides et applicables. Voir sections 7.1 à 7.12 pour les spécifications fusionnées.)*

---



## ANNEXE L — Détail Exhaustif Nouveaux Modules V6 7.13 à 7.28 (Workflows + Edge Cases)

### L.1 Module A Deadline — Workflows Alternatifs
- Fuseau horaire plateforme: PLACE (CEST), BOAMP (CET), AWS (UTC+2 été). Conversion auto + alerte si décalage.
- Cas hiver: is_readonly=True mais cron J-30 continue = badge EXPIRE quand même.
- Forçage Admin: bouton "Forcer dépôt" loggué avec raison obligatoire = audit trail complet.

### L.2 Module B Alloti — Edge Cases
- Marché alloti 14 lots: wizard 14 onglets séparés. Similarité mémoire inter-lots calculée via embeddings = alerte si >85%.
- Lot piège détecté: critères exigeants + prix bas = badge noir "LOT PIÈGE — Ne pas chiffrer agressivement".

### L.3 Module C RSE — Calculs Détaillés
- Heures insertion: `effectif_moyen * 6.5h/j * 20j/mois * duree_mois * taux_insertion_historique`
- Pénalité: `(heures_exigees - heures_realisables) * 2 * SMIC_horaire`
- Ex: 500h exigées, 320h réalisables, SMIC 11.65€ = pénalité 4 194€

### L.4 Module D Coherence — Seuils
- Crédible: ratio < 45%
- Surévalué: 45-55%
- Sous-évalué: 55-65%
- Irréaliste: > 65% = alerte bloquante Admin

### L.5 Module E Variante — Conditions
- Formalisée: variantes interdites sauf mention contraire (R2151-8)
- Adaptée: variantes autorisées sauf mention contraire
- Base obligatoire: détecté dans 80% des RC autorisant variantes

### L.6 Module F Matériaux — Indices
- Acier: IPB BTP (Indice Prix BTP acier)
- Bois: IPB bois
- Cuivre: cours LME cuivre converti
- Bitume: indice pétrole dérivé
- Ciment: indice ciment INSEE
- Alu: cours LME aluminium

### L.7 Module G PAB — Seuils
- Alerté orange: écart -15% à -20%
- Alerté rouge critique: écart -20% à -30%
- Élimination quasi-certaine: écart <-30%
- Justification types: achats groupés, optimisation, matériaux alternatifs, sous-traitance compétitive, savoir-faire spécifique, proximité chantier

### L.8 Module H Visite — Validation GPS
- Distance max site vs photo GPS: 500m = OK, >500m = warning "Vérifier adresse", >2km = rouge "Visite non confirmée"
- EXIF requis: timestamp, GPSLatitude, GPSLongitude. Sinon warning.

### L.9 Module I Enveloppe — Classification
- DUME remplace DC1/DC2 pour marchés <215k€ (art R2131-5)
- Certains acheteurs imposent encore DC1+DC2 malgré DUME = détection conflit
- 3 enveloppes: Candidature (DC1/DC2/DUME + attestations) / Technique (Mémoire + SOGED + PPSPS + Gantt) / Prix (AE + DPGF + BPU)

### L.10 Module J Post-Gagné — Échéances
- OS: 15j après notification
- Récolement provisoire: fin travaux + délai CCAP
- Levée réserves: 30j/60j/90j selon CCAP
- Garantie décennale: 10 ans fin récolement définitif
- Avenant max: 20% montant initial, délai 15j avant échéance

### L.11 Module K Contentieux — Délais
- Réclamation pré-attribution: 10 jours à compter notification
- Référé précontractuel: 31 jours avant signature
- Mémoire en réclamation: 30 jours décompte général
- Mise en demeure retard paiement: 8 jours avant procédure
- Intérêts moratoires LME: taux BCE + 3 points (ex: 4% + 3% = 7%)
- Frais recouvrement forfaitaire: 40€

### L.12 Module L Certif — Équivalences
- Qualibat 2112 = OPQIBI 1411 (équivalence partielle selon MOA)
- RGE = reconnaissance garant environnement
- MASE = management sécurité
- ISO 9001/14001 = génériques, pas substituts Qualibat

### L.13 Module M Capacité — Ratios
- FR minimum: 5-10% CA selon type marché
- CAF minimum: 3-5% CA
- Endettement max: 3.0
- CA minimum: 2× montant marché pour marchés >100k€

### L.14 Module N Tableau Risques — Format Comité
- 1 page A4 paysage
- 5 colonnes: Risque | Probabilité | Impact € | Mitigation | Responsable
- Ligne finale: Marge résiduelle après provisions + Recommandation Go/No-Go
- Export: PDF 1 page + PowerPoint 3 slides (contexte, tableau, recommandation) + Excel détaillé

### L.15 Module O MAPA — Formats
- MAPA <90k€: 1 dossier unique ou 2 enveloppes
- MAPA 90k€-215k€: 2 enveloppes (candidature + offre)
- DUME obligatoire <215k€ (DC1/DC2 facultatifs si DUME fourni)

### L.16 Module P E+C- — Seuils
- E1C1: <500 kg CO2e/m2 (rénovation) / <800 kg (neuf)
- E2C1: <400 kg / <650 kg
- E3C2: <300 kg / <500 kg
- C1: énergie positive
- C2: énergie très positive

---



## ANNEXE M — Référentiels DATA/REFERENTIELS — Schémas JSON

### M.1 bt_indices_insee_36m.json
`{ "BT01": [ {"date": "2023-01", "valeur": 125.3}, ... {"date": "2026-06", "valeur": 133.5} ], "BT06a": [...], "BT38": [...], "source": "INSEE", "derniere_maj": "2026-07-01", "unite": "indice base 100 2010" }`

### M.2 ratios_ademes_dechets.json
`{ "BA13 cloison 72/48": {"ratio_kg_m2": 12, "flux": {"platre": 0.7, "metal": 0.1, "inerte": 0.2}}, "source": "ADEME", "prix_defaut": {"tri_inerte": 45, "tri_platre": 95, "transport": 35, "exutoire_inerte": 25, "reprise_REP_bois": -20} }`

### M.3 coeffs_site_contraintes.json
`{ "site_occupe_hopital_EHPAD_ecole": {"coeff": 0.15}, "acces_difficile_lt_3m": {"coeff": 0.10}, "hauteur_sup_4m": {"coeff": 0.20}, "formule": "temps_corrige = temps_base * (1 + sum(coeffs actifs))" }`

### M.4 meteo_france_intemperies_10ans.json
`{ "38 Isere": {"1": {"moy_j_intemperies": 8}, "2": {"moy":6}, ... "12": {"moy":7}}, "source": "Meteo France 10 ans 2014-2024" }`

### M.5 ratios_amiante_ss4.json
`{ "curage_leger_second_oeuvre": {"ratio_eur_m2": 85}, "curage_lourd": {"ratio": 185}, "demolition": {"ratio": 250}, "aleas": 0.20, "delai_semaines_100m2": 3, "cout_mesure_air": 500 }`

### M.6 V6 indices_matériaux_insee.json
`{ "acier": [ {"date": "2023-01", "valeur": 100.0}, ... ], "bois": [...], "cuivre": [...], "bitume": [...], "ciment": [...], "aluminium": [...], "source": "INSEE / LME", "derniere_maj": "2026-07-01" }`

### M.7 V6 seuils_eplusc.json
`{ "neuf": {"E1C1": 800, "E2C1": 650, "E3C2": 500}, "renovation": {"E1C1": 500, "E2C1": 400, "E3C2": 300}, "unite": "kg CO2e/m2", "source": "Label E+C- 2024" }`

### M.8 V6 fdes_produits_btp.json
`{ "BA13_Ploco_72-48": {"co2_kg_m2": 12, "source": "FDES Placo 2023"}, "beton_voile_20cm": {"co2_kg_m2": 250, "source": "FDES CIMBETON 2024"} }`

### M.9 V6 ratios_financiers_btp.json
`{ "marche_inf_100k": {"ca_min_ratio": 2.0, "fr_min_pct_ca": 5.0, "endettement_max": 3.0}, "marche_100k_1M": {"ca_min_ratio": 2.5, "fr_min_pct_ca": 8.0, "endettement_max": 2.5} }`

### M.10 V6 taux_bce_mensuel.json
`{ "2026-01": 4.00, "2026-02": 4.00, ... "2026-07": 3.75, "source": "BCE" }`

---



## ANNEXE N — Exemples de Générateurs Output — DOCX/PDF Fonctionnels

### N.1 Générateur Q/R Tactique — Template DOCX
En-tête: Logo entreprise + SIRET + Adresse + AO num + date.
Tableau 8 lignes: N°, Page CCAP/CCTP, Extrait piège, Question opposables, Enjeu € (Admin only), Type (Juridique/Technique/Financier).
Footer: Signature Admin.

### N.2 Générateur Mémoire Booster — Structure DOCX 60p
Sommaire auto + 8 chapitres: 1 Contexte + ADN local distance agence + nom conducteur, 2 Moyens humains CACES AIPR, 3 Moyens matériels, 4 Méthodologie avec 50 contraintes CCTP réponses point par point + preuves A08 <50km photos légendées, 5 Planning Gantt PNG + MPP + chemin critique + intempéries, 6 Environnement RE2020 FDES + SOGED, 7 Qualité + PPSPS, 8 Annexes + Matrice conformité RC tableau.

### N.3 Générateur SOGED — 10 pages
Page 1 ID chantier, Page 2 Estimation volumes par flux via rep_cost, Page 3 Tri à la source, Page 4 Exutoires agréés, Page 5 Transport, Page 6 Traçabilité bordereaux, Page 7 Valorisation, Page 8 REP, Page 9 FDES, Page 10 Engagements.

### N.4 Générateur HANDOFF+ — 30 pages double artefact
Voir §7.12 + Annexe K.12.

### N.5 V6 Générateur Mémoire Réclamation — 5-10 pages
Page 1: Identité requérant, AO concerné, date notification, délai recours.
Page 2-3: Motifs d'irrégularité détaillés avec références RC/CCAG/jurisprudence.
Page 4: Preuves à l'appui (liste auto depuis dossier déposé).
Page 5: Demande de déclassification + réouverture consultation.
Annexe: Pièces du dossier déposé.

### N.6 V6 Générateur Mise en Demeure — 2-3 pages
Page 1: Identité créancier, débiteur, montant dû, délai contractuel, délai réel.
Page 2: Calcul intérêts moratoires LME (taux BCE + 3 points) + frais recouvrement 40€.
Page 3: Mise en demeure formelle — paiement sous 8 jours + accusé réception.

---



## ANNEXE O — Vision & Positionnement Offensif V6 — 4 Mondes + Inventaire

### O.1 Vision & Positionnement Offensif — Détail Fonctionnel
Promesse Unique entendue client: "Déposez votre DCE en 5 minutes, revenez en 48h avec un Go/No-Go chiffré sécurisé, un mémoire 18/20 prêt à déposer, un BFR calculé, un SOGED conforme, 8 questions MOE pour sécuriser marge, et un book chantier double artefact si GAGNÉ. Le tout sans exposer vos prix à vos salariés. Et si on vous élimine injustement, ripostez en 2 minutes."

Positionnement ressenti: "SMART_AO V6 est le copilote du patron BTP qui ne dort jamais, qui lit les 400 pages du CCTP que personne ne lit, qui détecte le piège page 312 caché, qui calcule exact €, qui garde le coffre fermé, et qui riposte quand on vous vole un marché."

Différenciation offensive 8 axes:
1. Souveraineté physique: 1 VPS = 1 client OVH FR, pas SaaS US multi-tenant.
2. Garage Math vs LLM seul: concurrent laisse LLM calculer marge = hallucination = faillite. Nous PuLP+OR-Tools+Decimal = exact.
3. RBAC étanche financier: concurrent salarié voit tout = fuite marge = mort. Nous double artefact + strip.
4. Vault + SIRET Guardian: 30% éliminations évitées.
5. Mémoire Booster preuve géolocalisée <50km + Gantt météo + RE2020 + matrice RC = 18/20 vs 12/20.
6. **V6:** 28 modules = couverture complète veille à réclamation. Ni ERP, ni cabinet, ni SaaS US ne fait ça.
7. **V6:** Contentieux intégré = avocat virtuel. Recours en 2 minutes, pas 2 semaines.
8. **V6:** Post-Gagné Tracker = on ne gagne pas pour perdre après. Avenants, récolements, réserves = sécurisés.

### O.2 Architecture des 4 Mondes — Single-Tenant by Design
Monde 1 — Admin World (Patron): Contrôle absolu, voit tout €, valide provisions, signe, contentieux, post-gagné.
Monde 2 — Salarié World (Opérateur Guidé): Wizard 12 étapes, barre progression, 1 bouton à la fois, voit nature pièges sans €, saisit Qté/Temps h sans €, photos terrain, exutoires, relecture Q/R.
Monde 3 — Infra World (VPS Dédié): 1 VPS = 1 client = 1 Postgres = 1 Qdrant = 1 MinIO = 1 Redis. Backup AES-256-GCM + LVM snapshot + cosign verify + ClamAV + heartbeat whitelist sans données métier.
Monde 4 — Cerveau Hybride: RAG Hybrid + Garage Math + MCP 3 servers internes + BOAMP externe. Cerveau lit, extrait, détecte quali ZERO €, calcule exact €.

---



## ANNEXE P — Cockpit Admin 8 Modules + APIs Fonctionnelles V6

### P.1 à P.11 (Voir Annexe C pour le détail complet des 11 modules cockpit incluant V6)

---



## ANNEXE Q — Workflow Lifecycle 12 Étapes Détaillé + State Machine + Transitions Retour

### Q.1 Diagramme États
BROUILLON (création) -> ANALYSE (upload DCE + analyse 33 modules) -> GO (Go/No-Go 39 critères) -> METRE (métré Qté/Temps) -> SITE_CONTRAINTES (contraintes site) -> MEMOIRE (mémoire booster) -> DOCS_ADMIN (DC1/DC4) -> HANDOFF (preview expurgé Handoff salarié vers Admin) -> CHIFFRAGE_ADMIN (Admin contrôle financier validation provisions) -> VALIDATION_ADMIN (vérif exhaustive) -> DEPOSE (ZIP 3 enveloppes + dépôt Profil Acheteur) -> ARCHIVE (archivé) -> GAGNE/PERDU (si GAGNE -> HANDOFF+ Book + Post-Gagné Tracker).

### Q.2 Transitions Autorisées & Retours
- BROUILLON -> ANALYSE (upload DCE)
- ANALYSE -> GO (analyse 33 modules terminée)
- GO -> METRE (Go validé) OU GO -> BROUILLON (No-Go)
- METRE -> SITE_CONTRAINTES
- SITE_CONTRAINTES -> MEMOIRE
- MEMOIRE -> DOCS_ADMIN
- DOCS_ADMIN -> HANDOFF
- HANDOFF -> CHIFFRAGE_ADMIN (seul Admin peut déclencher)
- CHIFFRAGE_ADMIN -> VALIDATION_ADMIN (si provisions validées) OU CHIFFRAGE_ADMIN -> {METRE, MEMOIRE, BROUILLON} avec rejection_reason obligatoire (ex: "Métré BA13 incohérent — Recheck plans 135m2 vs 80m2")
- VALIDATION_ADMIN -> DEPOSE (si Vault OK + provisions + mémoire + SOGED + DC4 + Q/R + Deadline OK + Certif OK + Enveloppes OK)
- DEPOSE -> ARCHIVE
- ARCHIVE -> GAGNE (déclenche Handoff+ Book + Post-Gagné Tracker) OU PERDU.

### Q.3 Gates Bloquantes Détaillées V6
- Impossible GO si Vault A01-A03 EXPIRE (J-30 rouge).
- Impossible HANDOFF si métré vide.
- Impossible CHIFFRAGE_ADMIN si Handoff non fait.
- Impossible VALIDATION_ADMIN si provision BT/penalites/BFR/RAT/REP/site/omission non validée Admin.
- Impossible DEPOSE si mémoire non généré + SOGED non généré si obligation + DC4 manquant si sous-traitance + Q/R non relue si piège critique.
- **V6:** Impossible DEPOSE si Deadline Guardian alerte rouge active (pièce manquante ou délai dépassé).
- **V6:** Impossible DEPOSE si Certification Live Checker alerte rouge (Qualibat manquant ou expiré pendant marché).
- **V6:** Impossible DEPOSE si Enveloppe Separator alerte rouge (pièce dans mauvaise enveloppe).
- Impossible GAGNE si statut != ARCHIVE.
- Seul Admin peut GAGNE + générer Book (test handoff_irreversible).

### Q.4 Audit Log & Rejection Reason
Chaque transition retour arrière loggée dans `project_history` avec user_id, from_state, to_state, rejection_reason, timestamp.

---



## ANNEXE R — Mémoire Booster + Q/R Tactique + HANDOFF+ — Workflow Intégré Complet V6

### R.1 à R.4 (Voir §7.11, §7.10, §7.12 et Annexe K pour workflows intégrés détaillés)

---



## ANNEXE S — Stack Technique & Modèles Commerciaux Synchronisés

### S.1 Stack Technique Une Page Rappel Exhaustif V6
*(Identique à Annexe G.1 avec ajout référentiels V6)*

### S.2 Modèle Commercial Formule Unique Entreprise — Synthèse Finale V6
Formule Unique Entreprise: Licence unique perpétuelle paiement unique pas abonnement. VPS facturé direct OVH client (16Go ~80€/mois, 32Go ~150€/mois). MAJ 30s docker pull + backup auto. Pas de % CA. Pas de SaaS mutualisé 100 clients même DB.

Modèle A Souverain: Client propriétaire VPS OVH FR, opère lui-même, support éditeur sans accès données métier heartbeat whitelist.

Modèle B Infogéré assumé DPA art28: VPS dédié EU par client opéré en infogérance par éditeur avec DPA art28. Souveraineté physique maintenue (serveur dédié pas mutualisé). Transparence. Formule correcte obligatoire. Slogan "je n'héberge rien" interdit mensonger.

Pricing indicatif (Voir MANIFESTE): Licence 12k€-25k€ selon modules + VPS OVH client direct. ROI 1 AO gagné = rentable (marge sauvée 50k€+ vs perte sans détection 247k€). Garantie objectif usage pas garantie chiffrée: réduction significative élimination formelle (90% via Vault), temps réduit fortement 1er AO, accéléré 2e AO via Vault.

Argumentaire vente V6: Souveraineté + Vitesse objectif + Fiabilité objectif + Prix unique + UX 1 bouton + Conformité RGPD/AI Act + Système arme marge/trésorerie + 28 boucliers + Contentieux intégré + Post-Gagné Tracker.

---



## ANNEXE T — Règles d'Or Codage & Maintenance — Rappel Bloquant

### T.1 Interdiction Copier-Coller Modules
Si module BT Guardian défini ici §7.1, interdiction redéfinir ailleurs fonctionnellement (ex: dans MANIFESTE ou MES). MANIFESTE doit écrire "Voir RAPPORT section 7.1 pour spec fonctionnelle BT Guardian". MES doit écrire "Build 5: Modules 7.1-7.28 — Voir RAPPORT §7 pour spec". ENGINEERING-HANDBOOK ne définit pas Trigger/IA/Vue salarié/Action Patron, seulement contrats API `/api/finance-warfare/bt-projection` Input Output + mem_limit + code.

### T.2 Taille Cible Respectée par Fichier
- MANIFESTE.md 10-15p 30-50KB max commercial pur pas technique.
- RAPPORT (ce doc) 100-150p 300-400KB exhaustif source unique 28 modules détaillés Trigger/IA/Garage/Vue/Action + tableau recap unique §8 + garage + dashboards + Go/No-Go + conclusion.
- ENGINEERING-HANDBOOK.md 40-60p 120-180KB technique pur 23+ ADR + C4 + invariants single-tenant + schemas + contrats API + mem_limit + code snippets + tests + infra.
- PLAN_MAITRE_V7.1.md 25-30p 60-80KB Build Chain + Pilotage + Roadmap (ex-MES + PLAN_CODAGE fusionnés).
- Arborescence_V7.1.txt liste unique propre alphabétique 368 fichiers.
Total pack 6 fichiers ~600-800KB maintenable.

### T.3 Process Modification Future Module
1. Modifier uniquement RAPPORT.md §7.X (Trigger/IA/Garage/Vue/Action) + §8 tableau récap ligne correspondante si besoin.
2. Si changement impact contrat API, mettre à jour ENGINEERING-HANDBOOK- section contrats API + mem_limit.
3. Si changement impact build order, mettre à jour PLAN_MAITRE_V7.1 via référence "Voir RAPPORT §7.X".
4. JAMAIS copier définition complète ailleurs.
5. Lancer `check_go_nogo.sh` + tests bloquants 39 critères vert avant commit.
6. Bump version dans Changelog §0.

---



## ANNEXE U — Conclusion Finale Architecte — 20 Ans Terrain en Code

20 ans chantiers et RC 412 pages nous ont appris: On ne perd pas AO sur prix, on perd sur piège non vu page 312 + provision non chiffrée + BFR non anticipé + salarié qui voit marge + mémoire générique 12/20 + book chantier sans risques qualitatifs + visite oubliée + DC1 dans offre + Qualibat sans mention + avenant oublié + recours non fait.

SMART_AO V6 = réponse: 28 modules qui protègent marge/trésorerie/note/survie juridique, RBAC étanche financier qui protège confiance Patron, Mémoire Booster 18/20 qui gagne marchés, HANDOFF+ double artefact qui sécurise exécution, Contentieux Generator qui riposte, Post-Gagné Tracker qui fidélise.

Chaque ligne code ici a été vécue sur chantier: RAT manquant => 3 semaines retard + 18.5k€ SS4, BT sans butoir => -47k€ marge fondue, pénalités sans plafond => 124k€ = 12% CA, BFR -180k€ => entreprise saine en cessation paiement M5, solidarité élargie => 180k€ exposition hors lot, DC4 62% >50% => rejet offre, site occupé hôpital +15% MO non provisionné => -18k€, 4 portes oubliées DPGF => -1.8k€ direct + réserve MOE, Q/R non posée => mémoire réclamation perdu, visite oubliée => élimination 500k€, DC1 dans offre => irrégularité, avenant oublié => 30k€ non facturés, recours non fait => 1M€ perdu définitivement.

SMART_AO V6 transforme ces en JSON + Garage Math Decimal exact + provision à valider + Q/R opposable + mémoire preuve <50km + book double artefact + deadline bloquante + alloti séparé + enveloppe triée + certif vérifiée + PAB défendu + matériaux protégé + RSE boosté + contentieux riposté + post-gagné sécurisé.

C'est système arme marge, pas outil chiffrage.
C'est étanchéité financière qui fait confiance Patron.
C'est calcul exact INSEE ADEME Météo France qui fait différence entre marché gagné et chantier qui tue entreprise.
C'est 28 boucliers pour ne plus jamais perdre un marché pour une connerie, et ne plus jamais signer sa propre faillite.

**FIN ANNEXES A-U — COMPLEMENT EXHAUSTIF V6 FUSION.**

---

*Document préparé pour usage interne — Ne pas diffuser*
*SMART_AO V6 Fusion — Source Unique Fonctionnelle 28 Modules — Édition Août 2026*


---

# ANNEXES ARCHIVÉES V12 - PRÉSERVÉES INTÉGRALEMENT (Ne pas supprimer)

> Cette section garantit le respect de la règle intangible "Ne supprime RIEN du fichier cible". Tous les compléments V12 (cas d'usage BTP réels, workflows détaillés, matrices décisionnelles, glossaire, specs ultra-détaillées) sont préservés ci-dessous. Voir RAPPORT §7.X pour version V6 à jour.





## ANNEXE FONCTIONNELLE A - DCE Trap Detector - 4 Familles Originales + Routage 12 Modules

> **Source unique fonctionnelle du Trap Detector:** Cette annexe définit les 4 familles historiques + routage vers 12 modules . Pas de redondance ailleurs. Handbook = technique.

### A.1 Famille 1 - Pièces Contractuelles & Risques Juridiques (CCAP/AE/DC1)

Exemples pièges:
- CCAP art 10-12: prix ferme sans actualisation, formule sans date base, absence butoir, révision sans indice, clause sauvegarde abusive.
- AE: solidarité GME, DC1 répartition non 100%, pièces manquantes.
- R2111-7: marque imposée sans équivalent.
- Pénalités: plafond 5% CCAG non cité, cumul particulier + général.
- Routage: Si détection formule BT -> module 4.1, pénalités -> 4.2, GME -> 4.4, DC4 -> 4.5, marque -> 4.9.

Sortie JSON: `{famille: "juridique", sous_famille: "prix", module_route: "4.1", page: 12, extrait: "...", niveau: "rouge", confiance: 0.92}`

### A.2 Famille 2 - Aspects Techniques & Site (CCTP/Plans/Diags)

- Site occupé hôpital/EHPAD/école non chiffré MO.
- Accès <3m, hauteur >4m, stockage impossible, horaires restreints, centre-ville dense, bruit <70dB.
- Amiante <1997 sans RAT, plomb, termites.
- SOGED/PEMD/REP non prévu.
- Plans manquants, diagnostic manquant.
- Routage: site -> 4.8, RAT -> 4.6, SOGED -> 4.7, cross-check -> 4.9.

### A.3 Famille 3 - Financiers & Quantitatifs (DPGF/BPU/Métré)

- Incohérence CCTP-DPGF-Plans quantités >2%, oublis portes/fenêtres, doublons.
- BFR non provisionné avance 0% RG 5% délai 30j.
- Coût REP non provisionné.
- BT inflation non provisionnée.
- Marge nette non calculée.
- Routage: BT ->4.1, trésorerie ->4.3, SOGED ->4.7, cross-check ->4.9.

### A.4 Famille 4 - Autres Pièges Fréquents

- DC4 plafond dépassé 62% >50%.
- Q/R date limite non respectée.
- DOE/DIUO retard pénalité cachée.
- Absence réunion chantier pénalité 150€/réunion.
- Absence PPSPS/SOGED pénalité.
- Routage: DC4 ->4.5, Q/R ->4.10.

### A.5 Idées Créatives / Proactives Intégrées

- Smart Suggestions: Propose automatiquement question MOE pour neutraliser piège.
- Auto-remplissage Vault: Si CCTP exige Qualibat 2112 et Vault A03 a 2112 OK => pré-remplissage.
- Chantier Matcher: Cherche chantier similaire <50km dans historique pour estimer temps/coût (quali sans € salarié).
- SIRET Guardian auto: cohérence cross-doc.

---



## ANNEXE Q - DÉTAIL FONCTIONNEL COCKPIT ADMIN 8 MODULES + APIS FONCTIONNELLES (Essence)

### Q.1 Cockpit Dashboard Principal Tuiles Gros Boutons UX

8 tuiles gros boutons 200x200px: AO en cours (Kanban), Finance Warfare (5 tuiles €), Vault (12 docs), Personnalisation (base prix), Comptes Salariés (RBAC), Contrôle Financier (provisions à valider), Analytics (taux Go), Paramètres (sécurité). Chaque tuile badge chiffre (ex: Vault 2 EXPIRE rouge). Clic tuile -> page détail.

### Q.2 Personnalisation Entreprise

Formulaire: logo entreprise (PNG), couleur primaire mémoire, base de prix: tableau PU moyens par ouvrage (BA13 45€/m2, peinture 25€/m2, béton voile 120€/m2...), taux horaire MO par qualif (maçon 45€/h, coffreur 42€/h...), coeff site défaut modifiables (hôpital 0.15 etc.), modèles mémoire docx, modèles SOGED docx, modèles DC4 pré-remplis. Versioning + preview.

### Q.3 Gestion Comptes Salariés

Liste salariés avec avatar, rôle admin/salarié, dernière connexion, AO affectés. Bouton créer salarié email + mot de passe temporaire + 2FA QR TOTP. Sandbox isolé: filesystem path /data/minio/{user_id}/ + vérif O_NOFOLLOW + fstat owner + BASE_ROOT non symlink. Révocation + audit log connexions + tentatives échouées.

### Q.4 AO en Cours Vue Globale Kanban

Kanban board 12 colonnes workflow + swimlanes salarié. Cartes AO: titre, MOA, date limite dépôt countdown J-, progression % wizard, badges pièges rouges/jaunes, montant estimé quali (Admin voit €, salarié non). Drag & drop Admin avec rejection_reason obligatoire si retour arrière. Filtres: salarié, état, Go/No-Go, date, dept, type. Search.

### Q.5 Contrôle Financier & Validation DCE Trap Detector + Garage

Page cœur Admin: liste 12 modules avec état (vert OK, orange à valider, rouge critique) + provisions 7 types à valider avec montants + graphs + commentaires salarié (photos, surfaces, temps) + bouton Valider/Provisionner/Rejeter + champ commentaire Admin + audit log. Bloque dépôt ZIP si provision non validée. Export Excel provisions.

### Q.6 Analytics & Performance

Graphiques: taux GO (60%), taux transfo Gagné/Perdu (30% gagné), marge nette moyenne par type chantier, pièges fréquents top 5 (BT sans butoir 40%, pénalités sans plafond 35%...), temps moyen analyse (2h), BFR moyen -120k€, coût REP moyen 3.8k€. Sans données métier si heartbeat test.

### Q.7 Paramètres & Sécurité

Clé API Mistral EU input mask, opt-in DeepSeek checkbox avec disclaimer RGPD texte: "En cochant, vous acceptez que des extraits CCTP non sensibles puissent être envoyés vers hors UE pour amélioration détection...". Backup config cron quotidien 02h00 AES-256-GCM S3 OVH + rétention 30j + LVM snapshot avant MAJ + cosign verify image Docker + 2FA TOTP secret + Argon2id paramètres + clé Qdrant API key + Redis password + ClamAV on/off.

### Q.8 Notifications & Alertes

Liste notifs temps réel WebSocket: Vault J-30, nouveau DCE déposé, Q/R J-2, piège critique 4.1-4.9 détecté, BFR pic, provision à valider, Handoff Book généré, backup OK/KO. Config email destinataires + fréquence.

### Q.9 Modèles de Données Backend Résumé (Technique Voir Handbook)

vault_core, project, users, handoff_logs, provisions, finance_warfare, trap_detections, mcp_audit_logs, backup_logs.

### Q.10 API Endpoints Admin (Fonctionnel)

POST /api/vault/upload, GET /api/vault/list A01-A12, POST /api/dce/analyze (orchestrateur ADN + Trap Detector 12 agents + 5 solveurs), GET /api/finance-warfare/{project_id}/bt-projection, /penalites, /bfr, /rep, /site, /incoherence, POST /api/provisions/validate, POST /api/handoff/generate, GET /api/projects/kanban, etc. Handbook pour contrats détaillés.

---



## ANNEXE V - CONCLUSION FINALE ARCHITECTE - 20 ANS TERRAIN EN CODE

20 ans chantiers et RC 412 pages nous ont appris: On ne perd pas AO sur prix, on perd sur piège non vu page 312 + provision non chiffrée + BFR non anticipé + salarié qui voit marge + mémoire générique 12/20 + book chantier sans risques qualitatifs.

SMART_AO = réponse: 12 modules qui protègent marge/trésorerie, RBAC étanche financier qui protège confiance Patron, Mémoire Booster 18/20 qui gagne marchés, HANDOFF+ double artefact qui sécurise exécution.

Chaque ligne code ici a été vécue sur chantier: RAT manquant => 3 semaines retard + 18.5k€ SS4, BT sans butoir => -47k€ marge fondue, pénalités sans plafond => 124k€ = 12% CA, BFR -180k€ => entreprise saine en cessation paiement M5, solidarité élargie => 180k€ exposition hors lot, DC4 62% >50% => rejet offre, site occupé hôpital +15% MO non provisionné => -18k€, 4 portes oubliées DPGF => -1.8k€ direct + réserve MOE, Q/R non posée => mémoire réclamation perdu.

SMART_AO transforme ces en JSON + Garage Math Decimal exact + provision à valider + Q/R opposable + mémoire preuve <50km + book double artefact.

C'est système arme marge, pas outil chiffrage.

C'est étanchéité financière qui fait confiance Patron.

C'est calcul exact INSEE ADEME Météo France qui fait différence entre marché gagné et chantier qui tue entreprise.

FIN ANNEXES P-V - COMPLEMENT 80-100 PAGES .

---



## ANNEXE W - COMPLÉMENTS EXHAUSTIFS SUPPLÉMENTAIRES POUR TAILLE CIBLE 80-100 PAGES - CAS D'USAGE BTP RÉELS DÉTAILLÉS - WORKFLOWS PAS À PAS - 50 PAGES SUPPLÉMENTAIRES

### W.1 Cas d'Usage Réel Complet 1 - Lycée 12M€ - 14 Lots - DCE 600 Pages - Temps Analyse 3h vs 40h Manuel

**Contexte:** AO Lycée neuf 12M€ 14 lots, lot 2 Gros Œuvre 800k€ concerné. DCE 600 pages: RC 30p, CCAP 50p, CCTP gros œuvre 180p, CCTP 00 40p, Plans 200p (30 plans), DPGF Excel 400 lignes, Diags amiante 20p, Planning 10p.

**Workflow SMART_AO :**

Jour 1 08h00: Patron dépose ZIP DCE 600p via drag & drop upload worker. Parsing PyMuPDF 2s/page = 20min total. Docling worker séparé 30 plans OCR.

08h30: Analyse 12 modules lancée. 12 agents RAG parallèles: CCAG 2021 search, CCP search, DTU 20.4 search. 5 solveurs Garage: bt_projection INSEE, penalites_cumul, rep_cost ADEME, site_coeff, incoherence_solver.

09h30: Analyse terminée. Dashboard pièges: Rouge 5 critiques: BT sans butoir page 18 CCAP, pénalités sans plafond 6 pénalités 2 cachées page 45 PPSPS 8j 200€/j + réunion 150€/réunion, site occupé école +15% + accès <3m +10% + hauteur >4m +20% + stockage impossible +8% = +53% MO, 4 portes oubliées DPGF vs plans + marque sans équivalent DALH, RAT manquant bâtiment 1995 <1997 suspect amiante. Orange 3: SOGED obligatoire 7 flux, DC4 plafond 50% cumul 62% dépassé si 3 sous-traitants, GME conjoint OK. Vert 4: BFR faible avance 10% + caution OK.

Salarié ouvre wizard étape 3 Analyse: voit badges rouges sans € "Risque Inflation Critique formule sans butoir - Voir Finance Warfare", "6 pénalités dont 2 cachées", "Site occupé école +2.5h/j", "4 portes non chiffrées", "RAT manquant saisir surface", "SOGED 7 flux saisir exutoire", "Cumul DC4 62% >50%". Clic badge ouvre extrait CCAP page 18 surligné.

Étape 4 Go/No-Go: 17 critères dashboard: 12 verts (auth, filesystem, Excel FileLock, MathBox no LLM, no conflict, strip financier, Vault J-30 OK car A01-A03 valides, heartbeat whitelist, rollback, backup AES, ClamAV, Golden Files), 5 verts (12 agents vert, 5 solveurs vert, RBAC provisions vert, HANDOFF double artefact vert, agent no euro vert). Salarié propose GO avec commentaire "Risques identifiés 5 rouges provisionnés côté Admin". Admin valide GO.

Étape 5 Site Visit: Salarié se rend site lycée: photos terrain 12 photos upload avec EXIF (accès camion, cour stockage, HSP salle 4.5m, école occupée bruit). Coche contraintes: site occupé école, accès <3m, hauteur >4m, stockage impossible, horaires 8h-12h, centre-ville dense. Saisie distance agence 25km.

Étape 6 Métré: DPGF 400 lignes importée: salarié saisit Qté m2 + temps h sans €: ex: voile béton 120m2 40h, cloison BA13 135m2 30h, porte 4 u 8h... Temps corrigé auto: voile 40h base *1.53 coeff site = 61.2h corrigé affiché "40h -> 61.2h +53% site" sans €. Pastilles plans: clic plan ajoute 4 portes.

Étape 7 SOGED: Saisie exutoires: bois Benne EBS 25km, plâtre Tri Vallée 30km, inerte Carrière 15km, métal Recyc Metal 20km. km transport auto. Obligation PEMD Oui >1000m2. Garage rep_cost = 4.2k€ côté Admin.

Étape 8 Mémoire Booster: Bouton Générer. ADN 50 contraintes extraites: "bruit <45dB chantier école", "accès <3m", "HSP 4.5m", "RE2020 12kg CO2/m2", "délai 18 mois dont 2 mois hiver Isère", etc. A08 recherche 3 preuves <50km: chantier école Jean Moulin 8km 2023 photo voile béton site occupé, chantier EHPAD 18km cloison acoustique, chantier lycée 25km Gantt hiver. Gantt OR-Tools avec intempéries Isère janvier 8j + février 6j. Mémoire 60p généré avec preuves photos légendées + Gantt PNG + RE2020 bilan carbone 12kg vs 15kg concurrent + matrice RC 60% technique pages 5-12.

Étape 9 Q/R: 8 questions générées tri enjeu: Q1 BT 47k€, Q2 pénalités 124k€, Q3 site 18k€, Q4 RAT 18.5k€, Q5 SOGED 4.2k€, Q6 oubli portes 1.8k€ + marque DALH, Q7 DC4 plafond, Q8 DOE retard. Salarié relit technique ajuste vocab. Admin valide juridique enjeu total 288k€ export DOCX PLACE.

Étape 10 AdminDocs: DC1 groupement conjoint OK, DC4 3 sous-traitants cumul 62% >50% alerte rouge -> Admin réduit à 45% en enlevant 1 sous-traitant. DC4 générés avec A03 Qualibat.

Étape 11 TechDocs: PPSPS + SOGED + DOE + DICT.

Étape 12 Handoff preview expurgé: preview book 30p sans € + checklist dépôt vert.

Chiffrage Admin: Finance Warfare 5 tuiles: BT -47k€ provision 8%, pénalités 124k€ provision 16k€ clause plafonnement, BFR pic -180k€ arbitrage caution 960€ vs 40k€, REP 4.2k€, site 18k€ +2 sem. Validations provisions + DPGF chiffrée PU moyens base prix 45€/m2 BA13 => DPGF total 800k€ + provisions 107k€ = 907k€ prix vente avec marge 13% ?

Validation Admin -> DEPOSE: 3 ZIP + mémoire + SOGED + DC4 + Q/R + Gantt + matrice RC upload PLACE.

Résultat: AO gagné car mémoire 18/20 preuve <50km + Gantt météo crédible + Q/R sécurisée. Book HANDOFF+ double artefact généré 30p: conducteur reçoit expurgé avec risques qualitatifs + DPGF commentée sans prix + plans pastillés + PPSPS + SOGED. Admin reçoit complet avec marge 13% + provisions + BFR + coût caution.

Sans SMART_AO, perte potentielle 107k€ + mémoire 12/20 = perdu. Avec, gagné + marge protégée.

### W.2 Cas d'Usage 2 - Rénovation EHPAD 2M€ - Amiante + Site Occupé + REP

DCE 350p: CCTP démolition + curage + BA13 + peinture + sols + CCTP 00 site occupé EHPAD + diag amiante 1995 non RAT manquant + SOGED obligation + accès <2.5m + horaires 8h-12h.

Analyse: RAT manquant rouge critique 18.5k€ SS4 + site occupé +15% + accès <3m +10% + horaires 8h-12h +12% + stockage impossible +8% = +45% MO = 35k€ + REP 6k€ + pénalités sans plafond 80k€.

Provision totale 60k€ + Q/R RAT + site. Mémoire Booster preuve EHPAD chantier similaire 18km avec photo curage SS4.

Gagné grâce preuve SS4 EHPAD <50km + planning intempéries + RE2020.

### W.3 Cas d'Usage 3 - Groupe Scolaire Neuf + Extension - GME Solidaire Élargie + DC4 Plafond

GME 3 membres mandataire solidaire élargie hors marché = exposition 2M€ vs lot 400k€ seul. DC4 plafond 50% cumul 62%. Module 4.4 + 4.5 détectent: alerte juridique critique.

Q/R solidarité + clause limitative + réduction sous-traitance 45%.

Sans détection, faillite si cotraitant défaille lot élec 600k€.

### W.4 Workflow Détaillé Mémoire Booster Pas à Pas Fonctionnel

Détail 5 sous-modules:

5.1 Ingestion ADN: RAG CCTP 180p extraction 50 contraintes avec page. Ex: "CCTP 4.2.3: Le béton doit être coulé à température >5°C + adjuvant antigel si <5°C + bruit <45dB si école + accès <3m + délai cure 7j + RE2020 12kg CO2/m2 + FDES exigée." + distance agence-chantier calculée via API adresse (12km) + nom conducteur extrait Vault A04.

5.2 Preuves A08: Vector search vault A08: query "béton coulé site occupé école <50km" -> top 3 photos: Ecole Jean Moulin 8km 2023-04-12 voile béton + légende + PV + EXIF lat/long + distance 8km + date. Insertion mémoire.

5.3 Gantt Météo: Input durées tâches salarié (démolition 10j, gros œuvre 60j, second œuvre 80j) + calendrier + intempéries dept 38 Isère janvier 8j moyenne. Solver OR-Tools CP-SAT optimise + marge intempéries + chemin critique + jalons. Output PNG Gantt + MPP.

5.4 RE2020 FDES: Vault A09 FDES BA13 12kg, béton 250kg/m3, peinture 2kg, etc. Calcul bilan carbone total chantier vs budget RE2020. SOGED 4.7 intégré.

5.5 Matrice conformité RC: Parsing RC 20% moyens humains, 15% matériels, etc. Génère tableau critère -> page mémoire + preuve.

### W.5 Workflow Q/R Tactique Pas à Pas

Agrégation pièges rouges -> tri enjeu € décroissant -> templating juridique -> 8 questions max -> relecture salarié technique -> validation admin juridique -> export DOCX -> dépôt PLACE -> trace mémoire réclamation.

Template langage: "Il semble que... Pourriez-vous confirmer... Dans l'affirmative... Dans la négative, nous provisionnerons..."

Chaque question vise neutralisation piège ou trace écrite future mémoire réclamation (ex: absence RAT => si sinistre amiante, trace Q/R = preuve MOA informée).

### W.6 Workflow HANDOFF+ Pas à Pas

Déclencheur GAGNE admin only -> bouton Générer Book -> worker async 2s: assemble DPGF annoté guerre (commentaires salarié + provisions Admin côté complet), risques résiduels, plans pastillés couleur amiante/accès/SOGED/oublis, kit admin DC4+OS+planning+PPSS+SOGED+DICT, mémoire chantier, DOE modèle, ATT, Annexes Vault.

Double artefact: /data/minio/admin/BOOK_COMPLET_ADMIN.pdf avec marges/provisions/BFR + /data/minio/salarie/BOOK_EXPURGE_SALARIE.pdf sans €. Checksum distincts SHA256. Audit log handoff_logs.

Email conducteur expurgé presigned 7j MinIO + email Admin complet coffre-fort.

Tests double artefact + irreversible + no leak.

### W.7 Sécurité Filesystem Détail Fonctionnel - `_check_access`

BASE_ROOT = /data/minio + vérifié non symlink au démarrage `os.path.islink(BASE_ROOT)` => exception bloquante si symlink.

`_check_access(path)`:
- `path = os.path.abspath(path)` + `os.path.normpath`
- Vérif path commence par BASE_ROOT + `os.path.commonpath`
- `O_NOFOLLOW` open + `os.fstat` vérif owner uid = os.getuid()
- Vérif chaque composant parent non symlink via lstat + islink
- Protection TOCTOU: open + fstat même fd pas 2 appels séparés.
Test nemesis 10 attaques: symlink escape, path traversal `../../etc/passwd`, TOCTOU race, owner mismatch, etc.

### W.8 RBAC Financier Détail Serializer

`strip_provisions_euros(obj)` récursif dict/list: si clé in [total_ht, marge, provision_euros, cout_rep, exposition_penalites, bfr_pic, cout_caution, provision_amiante, provision_omission, cout_tresorerie, provision_site, montant_marche_ht, pic_bfr, marge_nette, cout_ss4, cout_tresorerie, cout_site, cout_amiante] => remplacé par None ou masque. Si rôle salarié, API retourne None. Si Admin, retourne valeur Decimal. Middleware `require_admin` décore routes `/api/finance-warfare/*`, `/api/provisions/*`, `/api/handoff/complete`.

Frontend: composant `<PriceGuard>` qui si role salarié affiche "—" au lieu de €. Test `test_front_no_price_leak.spec.ts` scan DOM 12 modules regex € = 0.

### W.9 5 Moteurs Produit Détail Fonctionnel Exhaustif Complément

Moteur 1 Upload Worker: celery task `app/workers/upload_worker.py` - queue `upload` - Redis AOF persistence - progress WebSocket channel `project:{id}:progress`. Étapes: ClamAV scan -> PyMuPDF parse -> OCR si besoin -> chunking -> embedding BGE-M3 -> Qdrant upsert -> Vault SIRET extraction -> J-30 check.

Moteur 2 ADN Extractor: `app/services/adn_extractor.py` - RAG CCTP 180p + LLM Mistral EU `mistral-large-latest` json mode - extraction 50 contraintes avec page + type (acoustique, thermique, accès, délai, RE2020...). Output JSON strict sans hallucination + distance agence via `app/services/distance_calculator.py` OSRM.

Moteur 3 DCE Trap Detector: `app/services/dce_trap_detector_rag.py` - 12 agents: bt_agent, penalites_agent, treasury_agent, gme_agent, dc4_agent, rat_agent, soged_agent, site_agent, crosscheck_agent, qr_agent, memoire_agent, handoff_agent. Chaque agent RAG CCAG/CCP/DTU + prompt "Tu es expert BTP, extrais qualitatif ZERO €, page, extrait, niveau, confiance". Pas de calcul €.

Moteur 4 Garage Math: `app/engines/math_engine/` - 24 fichiers V7.1: chiffrage_pulp.py, treasury.py, planning_ortools.py, quantite.py, coeff_site.py, bt_projection.py, penalites_cumul.py, rep_cost.py, site_coeff.py, incoherence_solver.py, capacite_financiere.py, risques_generator.py, mapa_generator.py, eplusc_calculator.py, pab_detector.py, materiaux_shield.py, penibilite_solver.py, vigilance_solver.py, zan_solver.py, formule_algebra_checker.py, sourcing_api_solver.py. ZERO LLM import. Decimal exact. Tests 16 solveurs verts.

Moteur 5 RAG Engine: `app/services/embedding_engine.py` single-tenant pur: 0 tenant_id param - collections dce/vault/chantiers/traps sans préfixe - BGE-M3 1024 dim + sparse SPLADE + RRF + fallback FTS Postgres btp_french dict custom `btp_french` = mots BTP (DTU, CCAG, CCTP, BA13, DPGF...). `embedding_preloader.py` précharge modèle BGE-M3 au démarrage pour éviter cold start 10s.

### W.10 MCP Détail Fonctionnel Complément

Filesystem MCP 13 tools: read_file (with `_check_access`), write_file (FileLock + versioning 10), list_dir (O_NOFOLLOW), search_files (ripgrep), get_file_info (fstat), create_dir (mkdir -p with owner check), move_file, delete_file, read_excel_sheet (openpyxl + FileLock), write_excel_sheet, search_text_in_files (hybrid dense+sparse local), get_vault_doc, list_vault.

Excel MCP: single worker thread `app/mcp/internal/excel_mcp.py` queue + FileLock + versioning 10 fichiers DPGF + validate_header (check colonnes obligatoires Désignation/Qté/U + PU si Admin).

Pricing Memory MCP 4 tools détaillés:
- get_chantier_price: Input {ouvrage: "BA13 cloison 72/48", dept: "38", year: "2024"} Output {pu_moyen: 45€/m2, min:38, max:52, nb:12 chantiers, source: "Chantiers <50km"}
- detect_sous_chiffrage: Input DPGF ligne {designation, qté, pu_saisi} vs base prix Admin + historique. Si pu_saisi < pu_moyen*0.88 (-12%) => flag rouge "Sous-chiffrage probable 10k€/ligne - Vérifier oubli".
- save_price_after_win: après GAGNE, sauvegarde DPGF finale dans chantiers collection avec embedding.
- compare_pu_base_prix: compare DPGF complet vs base prix ligne par ligne écart >2% listing.

Host `app/mcp/internal/host.py` thread FastAPI: importe filesystem, excel, pricing memory, audit log middleware `mcp_audit_log.py` log tool calls dans `mcp_audit_logs` table.

BOAMP MCP externe: `app/mcp/boamp_mcp.py` 3 tools avec fetch BOAMP API + download DCE PLACE + tracking cron 6h + alerte email si DCE modifié + J-30.

### W.11 Build Chain 10 Builds Détail Fonctionnel (0 à 9 + 9.5) - Complément PLAN_MAITRE_V7.1

Rappel 10 builds: 0 Fondation Infra, 1 Vault, 2 ADN + RAG, 3 Trap Detector , 3.5 Garage Historique + Excel, 4 Wizard + Cockpit + RBAC, 4.5 5 Nouveaux Solveurs + Référentiels, 5 10 Modules Avancés + Finance Warfare, 6 Mémoire Booster + MCP, 7 HANDOFF+ + Go/No-Go 17 + ClamAV + Backup, 8 Fleet + Golden Files + Monitoring.

Chaque build gate vert obligatoire avant next. Voir PLAN_MAITRE_V7.1 §6 pour graphe détails.

### W.12 Invariants Single-Tenant Pur - 23 ADR (Synthèse - Détail Voir Handbook)

ADR 1: Single-tenant pur isolation physique pas logique.
ADR 2: 0 colonne tenant_id/client_id/vps_id en code métier.
ADR 3: 1 VPS = 1 Postgres + 1 Qdrant + 1 MinIO + 1 Redis.
ADR 4: LLM défaut API Mistral EU, hors UE opt-in disclaimer RGPD.
ADR 5: Parsing PyMuPDF+pdfplumber d'abord, Docling worker séparé.
ADR 6: RAG Hybrid Dense+Sparse+RRF+Fallback FTS btp_french.
ADR 7: Garage Math ZERO LLM import scan bloquant, PuLP+OR-Tools+Decimal exact to_decimal(str).
ADR 8: RBAC financier strip + double artefact + tests no leak.
ADR 9: Vault A01-A12 versioning 10 FileLock O_NOFOLLOW+fstat+BASE_ROOT non-symlink owner.
ADR 10: Filesystem MCP _check_access O_NOFOLLOW+fstat+owner+TOCTOU.
ADR 11: Excel FileLock single worker versioning10 validate_header.
ADR 12: Pricing Memory custom pas officiel Memory MCP (risque fuite).
ADR 13: MCP host thread FastAPI pas process séparé + audit log.
ADR 14: BOAMP 3 tools radar 6h.
ADR 15: Upload worker async Celery Redis AOF + WS progress + ClamAV EICAR.
ADR 16: ADN 50 contraintes + distance agence + preuve A08 <50km.
ADR 17: 12 agents Trap Detector ZERO € + agent_no_euro test.
ADR 18: 5 solveurs étendus Decimal exact référentiels INSEE ADEME Météo.
ADR 19: Finance Warfare 5 tuiles provision validation.
ADR 20: Mémoire Booster 18/20 preuves <50km + Gantt Météo France OR-Tools + RE2020 FDES + matrice RC.
ADR 21: Q/R tactique 8 questions max tri enjeu € templating juridique non agressif.
ADR 22: HANDOFF+ double artefact physiquement distinct checksum + irreversible + audit log.
ADR 23: Go/No-Go 17 critères single VPS /24 Fleet gate bloquant check_go_nogo.sh vert avant 1er client payant.

Voir ENGINEERING-HANDBOOK pour ADR détaillés C4 + invariants + schemas + mem_limit + code snippets.

### W.13 Tests Bloquants Exhaustifs - 20 Tests (Liste)

test_auth_jwt_vps, test_filesystem_nemesis 10 attaques, test_excel_concurrency, test_mathbox_no_llm_import, test_pulp_ortools_no_conflict, test_api_employee_cannot_see_prices, test_vault_j30_readonly, test_heartbeat_no_business_data whitelist CPU/RAM/disk/uptime pas DCE/Vault/prix, test_backup_restore, test_backup_restore_aes S3, test_clamav_eicar, test_golden_files 3x400p <5min, test_12_agents_trap_detector 12 agents ZERO € confiance >0.8, test_5_solveurs_ Decimal exact, test_rbac_provisions 0 € salarié, test_handoff_double_artefact 0 € expurgé 2 artefacts checksum, test_agent_no_euro IA 0 calcul €, test_handoff_irreversible seul Admin GAGNE, test_front_no_price_leak DOM 12 modules 0 €, test_front_no_handoff_leak URL admin non devinable.

---



## ANNEXE Y - SPÉCIFICATIONS COMPLÉMENTAIRES ULTRA-DÉTAILLÉES POUR ATTEINDRE 200KB+ - WORKFLOWS ALTERNATIFS - EDGE CASES - MATRICE DÉCISIONNELLE

### Y.1 Edge Cases & Cas Limites Fonctionnels par Module

**BT Guardian Edge Cases:**
- Formule avec 3 indices BT01+BT06a+BT38: provision = Σ coeff*écart indice. Ex: 0.4*BT01 +0.3*BT06a+0.15*BT38.
- Formule avec date base manquante: IA détecte absence + propose date base = mois remise offre par défaut CCP + Q/R.
- Marché <3 mois prix ferme: vert pas provision même si sans butoir.
- Marché >12 mois prix révisable avec butoir 5%: vert provision limitée 5% max = érosion plafonnée.
- INSEE API down: fallback dernier json local + alerte Admin maj manuelle.

**Pénalités Edge:**
- Pénalité en % montant jour: ex 1/3000*800k€=266€/j besoin montant marché => Garage récupère montant AE.
- Pénalité forfaitaire 10k€: exposition directe 10k€.
- Pénalité avec plafond propre 10k€ + plafond CCAG 5% = cumul plafond le plus bas?
- Pénalités cachées CCTP 00 vs CCAP: IA search both.

**Trésorerie Edge:**
- Avance 20% avec caution à 1ere demande + RG 5% cautionnée GDA + délai 30j = BFR positif vert.
- Avance 0% + RG 5% non cautionnable + délai 60j + facturation trimestrielle = BFR -300k€ rouge critique.
- Marché 24 mois vs 6 mois BFR courbe différente S-curve.

**GME Edge:**
- GME 2 membres 50/50 conjoint OK vert.
- GME 3 membres 60/25/15 solidarité élargie "mandataire solidaire hors marché" = rouge critique exposition 2M€.
- Cotraitant sans Qualibat: badge orange.
- Répartition 60/30/10=100% OK, 60/30/5=95% NOK rouge.

**DC4 Edge:**
- Plafond 50% cumul 62% dépassement rouge => Admin doit réduire sous-traitance ou demander dérogation MOA Q/R.
- Rang 2 interdit + rang2 détecté = rouge critique rejet DC4.
- Sous-traitant sans assurance RC = orange.

**RAT Edge:**
- Bâtiment 1998 >1997 pas obligation RAT mais si mention amiante dans diag = orange.
- Bâtiment 1960 <1997 RAT présent OK vert.
- Bâtiment <1997 RAT absent + surface 0m2 saisie = provision 0 mais alerte + Q/R.
- SS4 vs SS3: si amiante friable = SS3 retrait = coût 400€/m2 vs SS4 185€/m2.

**SOGED Edge:**
- Neuf uniquement <500m2 pas PEMD vert.
- Démolition >1000m2 PEMD obligatoire rouge si absent.
- 7 flux tri non respecté = amende ADEME 75k€.
- Exutoire non agréé = rouge.

**Site Contraintes Edge:**
- Site occupé hôpital + bruit <70dB + horaires 8h-12h + accès <1.5m cumul = +15+5+12+18=50% MO = +22.5h/j exemple.
- Centre-ville dense + stockage impossible + grue impossible = provision grue mobile 2k€/j.
- Photo terrain sans EXIF = warning mais acceptée.

**Cross-Check Edge:**
- CCTP 120m2 BA13 hydro vs DPGF 80m2 standard vs Plans 135m2 = écart type différent hydro vs standard => question technique "Confirmer type hydro requis salles humides uniquement ou partout?".
- 4 portes oubliées DPGF = oubli pur provision.
- Marque DALH sans équivalent = Q/R R2111-7 obligatoire.

**Q/R Edge:**
- 0 piège rouge => 0 Q/R badge vert "DCE clair pas de question critique".
- >8 pièges rouges => tri 8 plus gros enjeux €, reste en annexe mémoire réclamation "Autres points à 20k€...".
- Date limite Q/R passée: badge rouge bloquant "Q/R hors délai - Dépôt sous réserve pièges non levés".

**Mémoire Booster Edge:**
- Vault A08 0 preuve <50km => fallback <100km + warning "Preuve hors 50km mais similaire".
- Météo France API down => fallback json local moyen Isère.
- RC sans pondération explicite => parsing défaut 60/40 technique/prix.

**HANDOFF+ Edge:**
- Statut GAGNE mais Vault EXPIRE => bloquant régénération + alerte.
- Conducteur demande Book mais lien expiré 7j presigned => regénération lien Admin.
- double artefact checksum identical => erreur génération (doivent être distincts).

### Y.2 Matrice Décisionnelle Go/No-Go Détaillée 17 Critères Pesés

Critères 1-12 : auth, filesystem, Excel, MathBox no LLM, no conflict, strip, Vault J-30 readonly, heartbeat whitelist, rollback LVM, backup AES, ClamAV, Golden Files.

Chaque critère poids bloquant = 1 => si 1 rouge => No-Go global.

Critères 13-17 : 12 agents vert, 5 solveurs vert, RBAC provisions vert, HANDOFF double artefact vert, agent no euro vert.

Score Go/No-Go = 17/17 vert = GO, sinon NO-GO avec liste rouges.

Dashboard Go/No-Go affiche jauge 17/17 + liste verte/rouge + bouton "Run check_go_nogo.sh".

### Y.3 Workflow Alternatif - AO sans DPGF (Marché à BPU)

Certains AO à BPU (prix unitaires pas forfait). DPCF vide. Module Cross-Check: pas de DPGF vs Plans => skip. Métré devient estimation quantités BPU à partir plans. Garage quantite solver estime Qté. Provision omission BPU = Qté plan * PU BPU. Mémoire Booster adapte.

### Y.4 Workflow Alternatif - AO avec 3 DPGF Lots

AO 14 lots, lot 2 GO concerné uniquement. Upload DPGF lot 2 seul. Autres lots ignorés mais pièges transverses (CCAP global) conservés. GME Guardian si groupement.

### Y.5 Compatibilité Backwards /

Vault 10 docs -> migration 12 docs: A11 Admin + A12 Cautions ajoutés. Script migration `app/scripts/migrate_vault_v4_to_v6.py` ajoute 2 docs vides A VALIDER.

### Y.6 Performance & SLAs Fonctionnels

- Upload DCE 400p <5min, parsing PyMuPDF <2s/page, Docling worker 30p plans OCR <10min async.
- Analyse 12 modules <5min pour 400p (parallèle).
- Génération mémoire 60p <2min.
- Génération SOGED <30s.
- Génération HANDOFF+ 30p double artefact <2s.
- Finance Warfare tuiles <1s (cache provisions).
- Backup quotidien <15min 500Mbps, restore <15min objectif.
- ClamAV scan <5s par fichier.

### Y.7 Sécurité Données & Conformité RGPD/AI Act Fonctionnelle

- Données DCE/Vault/prix restent VPS OVH FR UE.
- LLM défaut API Mistral EU (host eu.mistral.ai, DPA art28).
- Opt-in hors UE: case Admin + disclaimer "Hors UE may transfer data outside EU, risk...".
- Journalisation prompts: table `llm_audit_logs` avec prompt hash, pas contenu DCE complet, RGPD conforme.
- Droit à l'effacement: suppression VPS = delete all data + backup purgé 30j.
- AI Act: classification outil aide décision pas autonome, humain valide (Admin).
- Chiffrement secrets: Fernet + AES-256-GCM Vault keys.

### Y.8 Monitoring & Heartbeat Whitelist Détail

Heartbeat toutes les 6h vers `api.smart-ao.com/heartbeat`: payload whitelist = {vps_id, cpu_pct, ram_pct, disk_pct, uptime, version, qdrant_status, postgres_status, minio_status, redis_status, backup_last, clamav_status, last_cron}. Aucune donnée métier: 0 DCE path, 0 Vault filename, 0 prix, 0 SIRET client, 0 AO title. Test `test_heartbeat_no_business_data.py` scan payload keys.

Prometheus metrics /metrics: `smart_ao_projects_total`, `smart_ao_vault_expire`, `smart_ao_provisions_total`, `smart_ao_bfr_pic`, etc. Mais sans € en valeur? Metrics infra seulement. Grafana dashboard infra.

### Y.9 Formation & Onboarding Fonctionnel

Formation salarié 2h: wizard 12 étapes, upload, analyse, métré, SOGED, mémoire, Q/R, Handoff preview. Exercice DCE 400p golden file.

Formation Admin 2h: cockpit tuiles, Finance Warfare, Vault, provisions validation, Handoff+, backup/restore, Go/No-Go, paramètres sécurité, opt-in hors UE, 2FA.

Onboarding 5 étapes Admin: 1 personnalisation entreprise base prix, 2 Vault A01-A12 upload, 3 comptes salariés, 4 test AO golden file, 5 Go/No-Go check + 1er client payant.

### Y.10 Support & SLA Fonctionnel

Support EU souverain: ticket, email, visio. Pas d'accès données métier sans DPA + consentement Admin + audit log accès support. SLA support J+1. MAJ 30s docker pull + backup auto + rollback LVM.

---



## ANNEXE Z - GLOSSAIRE BTP & ABRÉVIATIONS - POUR LISIBILITÉ 100 PAGES

AO Appel d'Offres, DCE Dossier Consultation Entreprises, RC Règlement Consultation, CCAP Cahier Clauses Administratives Particulières, CCTP Cahier Clauses Techniques Particulières, DPGF Décomposition Prix Global Forfaitaire, BPU Bordereau Prix Unitaires, DQE Détail Quantitatif Estimatif, AE Acte Engagement, DC1 Lettre candidature, DC2 Déclaration candidat, DC4 Sous-traitance, SOGED Schéma Organisation Gestion Déchets, PEMD Produits Équipements Matériaux Déchets, REP PMCB Responsabilité Élargie Producteur Produits Matériaux Construction Bâtiment, RAT Repérage Amiante Avant Travaux, SS4 Sous-section 4 amiante travaux sur matériaux amiantés, SS3 Sous-section 3 retrait amiante, PPSPS Plan Particulier Sécurité Protection Santé, DOE Dossier Ouvrages Exécutés, DIUO Dossier Intervention Ultérieure Ouvrage, ATT Attestation, PV Procès-Verbal, MOA Maître Ouvrage, MOE Maître Œuvre, CSPS Coordinateur Sécurité, GME Groupement Momentané Entreprises, BT Indice Bâtiment, BTP Bâtiment Travaux Publics, OVH Hébergeur FR, VPS Virtual Private Server, RAG Retrieval Augmented Generation, LLM Large Language Model, BGE-M3 Modèle embedding multilingue, Qdrant Base vectorielle, PuLP Solveur simplexe, OR-Tools Solveur Google optimisation, Decimal Librairie calcul exact €, MCP Model Context Protocol, SIRET Numéro entreprise, URSSAF, DGFIP, RC Assurance Responsabilité Civile, Décennale, Qualibat Qualification BTP, FDES Fiche Déclaration Environnementale Sanitaire, RE2020 Réglementation Environnementale 2020, BFR Besoin Fonds Roulement, RG Retenue Garantie, CA Chiffre Affaires, MO Main d'Œuvre, PU Prix Unitaire, PV Procès-verbal, EHPAD, AP-HP, etc.

---



## ANNEXE AA - DÉTAILS TECHNIQUES FONCTIONNELS COMPLÉMENTAIRES - 20 PAGES SUPPL POUR ATTEINDRE 80-100 PAGES

### AA.1 Détail Calculs Garage Math - Exemples Chiffrés Décimaux

**Exemple bt_projection détaillé calcul pas à pas:**

Input: montant_marche 800 000.00 €, coeff révisable 0.85, formule "0.15+0.85*BT01(m)/BT01(m0)", date base 2023-03 BT01 base 125.3, durée 18 mois, projections INSEE:
- 2024-03 BT01 128.7 érosion (128.7-125.3)/125.3*0.85*800000 = 0.02714*0.85*800000 = 18449€ (3m)
- 2024-09 BT01 130.5 érosion 4.15%*0.85*800k= 281... etc jusqu'à 18 mois.
Calcul Decimal exact to_decimal(str) pas float: Decimal("125.3") etc.

**Exemple rep_cost détaillé:**
Surface BA13 120m2 ratio 12kg/m2 =1440kg. Flux platre 70%=1008kg. Tri platre 95€/t=0.095€/kg*1008=95.76€ transport 35€/t*1008=35.28€+km 30km*0.5€/t/km=15€ exutoire platre 95€/t=95.76€ reprise REP 0 => total platre 241.8€. Métal 144kg tri 45€/t=6.48 transport 5.04 km 1.5 exutoire 10€ reprise -150€/t=-21.6 => -9.58€ (gain). Inerte 288kg tri 45=12.96 transport 10.08 km 1.5 exutoire 7.2 =>30.24€. Total BA13 =262.46€.

Même calcul pour chaque ouvrage DPGF 400 lignes => total 4.2k€.

**Exemple site_coeff détaillé:**
Temps base métré 100h (10h/j*10j). Coeffs actifs: site occupé EHPAD 0.15 + accès <3m 0.10 + hauteur >4m 0.20 + stockage impossible 0.08 + horaires 8h-12h 0.12 =0.65. Temps corrigé 100*1.65=165h =+65h =+6.5j. Taux horaire moyen 45€/h*65h=2925€ + délai 2 semaines * frais fixes chantier 5000€/sem=10k€ + location échafaudage 2k€ =15k€ impact.

### AA.2 JSON Schemas Fonctionnels (Réf Handbook pour tech)

**Provision JSON:**
{ "type": "bt_index", "module": "4.1", "niveau": "rouge", "provision_eur": "47320.00", "provision_pct": 8, "graph_data": [...], "page":12, "extrait":"...", "question_moe":"...", "validee_admin":false, "commentaire_admin":"", "timestamp":"2026-08-02T10:00:00Z" }

**Trap Detection JSON:**
{ "id":"trap_001", "famille":"financier", "module_route":"4.1", "page":12, "extrait":"Formule BT01 sans butoir", "niveau":"rouge", "confiance":0.94, "provision_type":"bt_projection", "saisie_salarie_requise": {"surface":false,"duree":true,"exutoire":false}, "vue_salarie_texte":"Risque inflation critique sans butoir - Voir Finance Warfare", "vue_admin_montant":"47320€", "qr_generee":true }

**Projet JSON:**
{ "id":"proj_123", "titre":"Lycée 12M€ Lot2 GO", "moa":"Région", "dept":"38", "statut":"ANALYSE", "dce_path":"/data/minio/projets/proj_123/dce.zip", "analyse": {"traps":[...], "provisions":{...}}, "vault_ids":["A01_123","A02_..."], "salarie_id":"user_456", "metre": {"lignes":[...]}, "site_contraintes":{"occupe":true,"acces_lt_3m":true}, "memoire_path":"/data/minio/projets/proj_123/memoire.docx", "soged_path":"...", "qr_path":"...", "book_complet":"/data/minio/admin/proj_123/BOOK_COMPLET.pdf","book_expurgé":"/data/minio/salarie/proj_123/BOOK_EXPURGE.pdf", "finance_warfare": {...}, "provisions_validees":false }

### AA.3 Workflow Notifications Email Types

Vault J-30: Sujet "Action requise: Kbis expire J-30 - SMART_AO" Corps "Votre Kbis expire le 2026-09-01 - Merci uploader nouveau - Lien Vault".
Q/R J-2: "Rappel Q/R Lycée 12M€ Lot2 - Date limite questions 2026-08-04 - 5 pièges rouges non neutralisés - Voir Q/R".
Piège critique: "Nouveau piège critique détecté: BT sans butoir -47k€ - Projet Lycée - Voir Finance Warfare".
Provision à valider: "5 provisions à valider 107k€ - Projet Lycée - Lien Cockpit".
Handoff: "Book chantier Lycée généré - Version conducteur expurgée disponible 7j - Lien".
Backup: "Backup quotidien OK 2026-08-02 02h00 taille 1.2GB S3 OVH" / "Backup KO - Action requise".

### AA.4 Matrice Permissions API Fonctionnelle (complément RBAC)

GET /api/projects/list: Salarié voit ses projets affectés, Admin voit tous.
POST /api/dce/analyze: Salarié + Admin.
GET /api/finance-warfare/*: Admin only require_admin + strip.
POST /api/provisions/validate: Admin only.
GET /api/vault/list: Salarié lecture + dépôt A VALIDER, Admin validation.
POST /api/handoff/generate: Admin only + statut GAGNE.
GET /api/handoff/download/complete: Admin only.
GET /api/handoff/download/expurge: Salarié + Admin.
GET /api/memoire/download: Salarié version expurgée, Admin version complète + expurgée.

### AA.5 Règles Gestion Verrouillages Souples Frontend

- Si Vault A01-A03 EXPIRE, bouton DEPOSE désactivé tooltip "Vault EXPIRE - Renouveler Kbis".
- Si provision BT non validée, tuile BT orange "Provision à valider" + bouton DEPOSE désactivé.
- Si métré vide, étape 6 warning "Métré vide - Saisir Qté".
- Si site contraintes non saisies, étape 5 warning.
- Si Q/R non relue, étape 9 warning.
- Autosave 30s + indicateur "Enregistré".
- Retour arrière autorisé sauf HANDOFF -> CHIFFRAGE_ADMIN irréversible côté salarié.

### AA.6 Exemple DCE Trap Detector JSON Complet 12 Modules

```json
{
 "project_id": "proj_123",
 "traps": [
 {"module":"4.1 BT","page":18,"extrait":"Prix fermes actualisables BT01 sans butoir","niveau":"rouge","confiance":0.94,"route":"4.1"},
 {"module":"4.2 Penalites","page":15,"extrait":"Penalite retard 500€/j cal sans plafond + absence reunion 150€/reunion page22","niveau":"rouge","confiance":0.92,"route":"4.2"},
 {"module":"4.3 Tresorerie","page":12,"extrait":"Avance 5% sans caution RG 5% delai 30j","niveau":"orange","confiance":0.88,"route":"4.3"},
 {"module":"4.4 GME","page":8,"extrait":"Groupement solidaire mandataire solidaire hors marche","niveau":"rouge","confiance":0.90,"route":"4.4"},
 {"module":"4.5 DC4","page":25,"extrait":"Plafond sous-traitance 50% cumul 62%","niveau":"rouge","confiance":0.91,"route":"4.5"},
 {"module":"4.6 RAT","page":0,"extrait":"Batiment <1997 RAT manquant","niveau":"rouge","confiance":0.89,"route":"4.6"},
 {"module":"4.7 SOGED","page":30,"extrait":"SOGED obligation 7 flux REP","niveau":"orange","confiance":0.87,"route":"4.7"},
 {"module":"4.8 Site","page":5,"extrait":"Site occupe ecole acces <3m hauteur >4m","niveau":"rouge","confiance":0.93,"route":"4.8"},
 {"module":"4.9 CrossCheck","page":0,"extrait":"4 portes plans non DPGF + marque DALH sans equivalent R2111-7","niveau":"rouge","confiance":0.92,"route":"4.9"},
 {"module":"4.10 QR","page":0,"extrait":"Agregation 7 pieges rouges -> 7 questions","niveau":"rouge","confiance":0.95,"route":"4.10"},
 {"module":"5 Memoire","page":0,"extrait":"50 contraintes + 3 preuves <50km + Gantt meteo + RE2020","niveau":"vert","confiance":0.96,"route":"5"},
 {"module":"6 Handoff","page":0,"extrait":"Statut GAGNE -> Book 30p double artefact","niveau":"vert","confiance":1.0,"route":"6"}
 ],
 "provisions": {
 "bt": {"type":"bt","montant":47320,"pct":8},
 "penalites": {"montant":16000},
 "bfr": {"pic":-180000,"cout_caution":960},
 "rat": {"montant":18500},
 "rep": {"montant":4200},
 "site": {"montant":18000},
 "omission": {"montant":3100}
 },
 "total_provisions": 107120,
 "enjeu_qr": 288000
}
```

### AA.7 Exemple Finance Warfare Dashboard Data JSON

```json
{
 "project_id":"proj_123",
 "bt_projection": {"base":125.3,"projections":{"conserv":132.1,"med":133.8,"pess":135.2},"erosion":{"conserv":-36700,"med":-46200,"pess":-53700},"provision_pct":8,"provision_eur":64000,"graph_36m":[...],"graph_proj":[...]},
 "penalites_cumul": {"exposition_max":124500,"pct_marche":12,"plafond_ccag":40000,"depasse":true,"sans_plafond":3,"provision":16000,"clause":"Les penalites cumulees...5% CCAG..."},
 "treasury": {"bfr_pic":-180000,"mois_pic":5,"cout_caution":960,"cout_rg_immob":40000,"graph_s_curve":[...],"cash_flow":[...]},
 "rep_cost": {"total":4200,"ventilation":{"bois":1200,"platre":1800,"inerte":800,"metal":-200,"DIB":600},"kg_total":5440,"soged_path":"/data/.../SOGED.pdf"},
 "site_coeff": {"temps_base":100,"temps_corrige":165,"coeffs":{"occupe":0.15,"acces":0.10,"hauteur":0.20,"stockage":0.08,"horaires":0.12},"impact_eur":18000,"delai_sup_sem":2,"photos":[...]},
 "incoherence": {"incoherences":[{"cctp":120,"dpgf":80,"plans":135,"ecart":50}],"oublis":["4 portes RDC"],"marques":["DALH sans equivalent"],"provision_omission":3100,"total_ecarts":18200}
}
```

---



## ANNEXE AC - DERNIERS COMPLÉMENTS POUR DÉPASSEMENT 200KB - RÉCAPITULATIF EXHAUSTIF 12 MODULES EN UNE PAGE PAR MODULE + FAQ

### AC.1 Récap Une Page Par Module Version Ultra Condensée Pour 80-100 Pages

**Module 4.1 BT Index Guardian - Une Page:**
Trigger: CCAP formule BT sans butoir. Entrées: CCAP art10-12, AE montant, planning durée. IA: extrait type prix, formule, indices, date base, butoir, risque. Garage: bt_projection INSEE 36m 3 scénarios érosion exacte Decimal. Réf: INSEE BT01. Salarié: badge rouge sans € "Risque inflation critique". Patron: -47k€ graph 3 scénarios provision 8%. Output: Finance Warfare tuile1 + Q/R. Risque si absent: -30k€ à -80k€ marge fondue. Cas AP-HP 412p exemple provision 47k€.

**Module 4.2 Pénalités Detector:**
Trigger: CCAP/CCTP/Planning pénalités. Entrées: CCAP pénalités, CCTP 00, planning jalons. IA: extrait 6 types + 2 cachées + plafond. Garage: penalites_cumul exposition max vs 5% CCAG. Salarié: liste 6 dont 2 cachées sans €. Patron: 124.5k€ 12% vs plafond 40k€ provision 16k€ clause. Output: Finance Warfare tuile2 + clause docx. Risque: 12% CA pénalités = cessation.

**Module 4.3 Trésorerie Simulator:**
Trigger: CCAP avance RG délai. Entrées: CCAP avance RG caution délai, planning, DPGF. IA: extrait avance/RG/délai/caution. Garage: treasury S-curve BFR pic -180k€ arbitrage caution 960€ vs RG 40k€. Salarié: alerte tendue M4-6 courbe sans €. Patron: pic -180k€ graph + arbitrage. Output: Finance Warfare tuile3. Risque: BFR -180k€ = cessation paiement entreprise saine.

**Module 4.4 GME Guardian:**
Trigger: GME groupement. Entrées: DC1 AE CCAP groupement A03. IA: détection conjoint/solidaire élargie répartition 100% pièces manq. Garage: contrôle 100% + exposition solidaire. Salarié: alerte juridique critique. Patron: 180k€ exposition DC1 corrigé. Output: DC1 corrigé checklist. Risque: solidarité élargie 180k€ hors lot.

**Module 4.5 DC4 Cascade:**
Trigger: CCAP plafond sous-traitance + saisie. Entrées: CCAP plafond % saisie sous-traitant A03. IA: lit plafond rang. Garage: contrôle cumul < plafond + génération DC4. Salarié: saisie masquée après. Patron: cumul 62%>50% + DC4 généré. Output: DC4 PDF. Risque: >100% sous-traitance = rejet offre.

**Module 4.6 RAT Amiante Analyzer:**
Trigger: <1997 RAT manquant. Entrées: CCTP démo diags plans date A10 SOP. IA: croise obligation RAT vs pièces. Garage: provision SS4 surface*ratio aléa. Salarié: RAT manquant saisir surface. Patron: 18.5k€ + délai SOP SS4. Output: provision PPSPS amiante Q/R. Risque: amiante sans SS4 = arrêt chantier + amende 75k€.

**Module 4.7 SOGED REP Tracker:**
Trigger: SOGED PEMD REP 7 flux. Entrées: CCTP métré photos A09 A10 exutoires. IA: détecte SOGED PEMD REP. Garage: rep_cost ADEME kg/m2*(tri+transport+exutoire-REP). Salarié: saisir exutoire 7 flux. Patron: 4.2k€ + SOGED généré. Output: SOGED PDF bilan déchets. Risque: 75k€ amende REP non conforme.

**Module 4.8 Site Contraintes Check:**
Trigger: CCTP 00 site occupé. Entrées: CCTP 00 photos notice saisie 7 contraintes. IA: détection occupé accès hauteur. Garage: site_coeff temps corrigé (1+Σcoeffs) +15% occupé +10% accès +20% hauteur. Salarié: +2.5h/j site occupé. Patron: 18k€ +2sem provision. Output: DPGF annoté pastilles plans. Risque: +53% MO non provisionné = -18k€.

**Module 4.9 Cross-Check CCTP-DPGF-Plans:**
Trigger: CCTP+DPGF+Plans. Entrées: CCTP DPGF Excel Plans PDF base prix PU. IA: triple compare quantités + marque R2111-7. Garage: incoherence_solver Qté plan*PU moyen >2% provision omission. Salarié: 4 portes non chiffrées. Patron: 3.1k€ + total écarts 18.2k€ Q/R. Output: provision Q/R DPGF annoté. Risque: oubli + marques illégales.

**Module 4.10 Q/R Tactique:**
Trigger: J-2 questions 48h. Entrées: pièges rouges 4.1-4.9. IA: génère 8 questions opposables page/§ non agressives verrouillantes tri enjeu €. Garage: templating tri € décroissant. Salarié: 7 questions relecture tech. Patron: docx enjeu 288k€ validation export PLACE. Output: DOCX Q/R trace mémoire réclamation. Risque: sans Q/R pièges non neutralisés = perte 288k€.

**Module 5 Mémoire Booster 18/20:**
Trigger: MEMOIRE + Vault A08-A10. Entrées: RC pondération Vault 50 contraintes. IA: ADN 50 contraintes + preuves <50km + météo RE2020 FDES. Garage: OR-Tools Gantt Météo France 10 ans + bilan carbone. Salarié: rédaction 80% avec preuves <50km sans prix. Patron: validation marge planning bilan RE2020. Output: mémoire 40-60p + Gantt PNG+MPP + matrice RC. Risque: mémoire générique 12/20 = perdu.

**Module 6 HANDOFF+ Book:**
Trigger: GAGNE Admin. Entrées: projet GAGNE DPGF pièges Vault. IA: assemblage DCE annoté kit admin. Garage: trésorerie finale planning réaliste double artefact. Salarié: book conducteur sans marge 30p risques quali. Patron: book complet marge provisions BFR coffre-fort audit log. Output: 2 PDFs 30p physiquement distincts + audit log. Risque: conducteur voit marge = fuite = mort entreprise.

### AC.2 FAQ Fonctionnelle 20 Questions

Q1: Single-tenant pur pourquoi pas multi-tenant? R: Isolation physique vs logique = sécurité audit conformité RGPD effacement VPS + pas de risque cross-tenant Qdrant/MinIO + coût OVH 80€/mois rentable dès 1er client. ADR 1-3.

Q2: Pourquoi Mistral EU défaut pas DeepSeek? R: Souveraineté EU + DPA art28 + RGPD + AI Act + secret affaires. DeepSeek opt-in disclaimer.

Q3: Pourquoi PuLP+OR-Tools+Decimal pas LLM calcul €? R: LLM hallucine 10-20% chiffres, BTP marge 13% -47k€ BT = faillite si hallucination. Garage exact Decimal.

Q4: RBAC étanche financier comment testé? R: 4 tests bloquants: test_api_employee_cannot_see_prices API scan, test_front_no_price_leak DOM scan 12 modules regex €=0, test_rbac_provisions 0 € salarié, test_handoff_double_artefact 0 € expurgé.

Q5: Double artefact pourquoi pas masquage JS? R: View Source fuite possible. Double artefact 2 PDFs physiquement distincts checksum différents + audit log + test double artefact regex €=0.

Q6: Vault J-30 readonly cron continue? R: Oui même is_readonly=True (suspension hiver). Test test_vault_j30_readonly vert. Sinon J-30 non alerté = EXPIRE sans prévenir.

Q7: Finance Warfare 5 tuiles € visibles salarié? R: Non Admin only require_admin. Salarié voit badges quali sans €.

Q8: Mémoire Booster 18/20 preuve <50km comment? R: Vault A08 photothèque géolocalisée EXIF + Qdrant search embedding "coulage béton site occupé" + filtre distance <50km + date <3 ans + insertion photo légendée.

Q9: Gantt Météo France source? R: data/referentiels/meteo_france_intemperies_10ans.json moyenne 10 ans jours intempéries par mois dept + OR-Tools CP-SAT + DTU cure béton 7j.

Q10: Q/R 8 questions max pourquoi? R: Profil Acheteur limite souvent 8-10 questions, tri enjeu € décroissant.

Q11: SOGED 7 flux obligatoires? R: REP PMCB 2023 loi AGEC 7 flux bois plâtre inerte métaux plastique verre DIB + amiante séparé. SOGED obligatoire si >1000m2.

Q12: RAT obligation <1997? R: Décret 2017-899 bâtiment permis <01/07/1997 obligation RAT + plomb + DTA. Sans RAT provision SS4 85-185€/m2.

Q13: Site contraintes +53% MO exemple? R: Ecole occupée +15% + accès <3m +10% + hauteur >4m +20% + stockage impossible +8% =53% => 40h base ->61.2h corrigé.

Q14: Cross-Check marque sans équivalent R2111-7 illégal? R: Oui sauf justification technique impérative. Q/R "Confirmer acceptation équivalent".

Q15: Go/No-Go 17 critères vs 12? R: 12 sécurité de base +5 (12 agents, 5 solveurs, RBAC provisions, HANDOFF double artefact, agent no euro) =17 single VPS /24 Fleet.

Q16: Taille cible RAPPORT pourquoi? R: Source unique fonctionnelle 12 modules détaillés Trigger IA Garage Vue Action pour chaque 4.1-4.10 +5+6 + tableau recap unique = exhaustif . Manifeste 10-15p commercial pur.

Q18: Pourquoi un seul tableau récap? R: Doublon tableau = maintenance 2 endroits = divergence. Un seul §8 .

Q19: Comment garantir zéro copier-coller? R: Règle inter-doc + scan manuel: si définition module ailleurs que §7, erreur bloquante. Autres docs réfèrent "Voir RAPPORT section 7.X".

Q20: Quelle est source unique technique? R: ENGINEERING-HANDBOOK- 23 ADR + C4 + contrats API + schemas + mem_limit + code + tests + infra. Fonctionnel = RAPPORT.

### AC.3 Conclusion Taille Atteinte

---


---

## SYNTHÈSE CHANGEMENTS V12 -> V6 FUSION (Résumés pour audit)

### Header
- Avant: "Source unique fonctionnelle des 12 modules"
- Après V6: "Source unique fonctionnelle des 28 modules - 24 single / 31 fleet - Édition Fusion V6 - 28 boucliers - 11 solveurs Garage"
- V7.1: "Source unique fonctionnelle des 33 modules - 39 single / 46 fleet - Édition Fusion V7.1 - 33 boucliers - 16 solveurs Garage"
- Voir RAPPORT §1 nouvelle table 39/46

### §1 Go/No-Go
- V6 : 17 -> 24 single (+7 V6), 24 -> 31 fleet (+7 V6)
- V7.1 : 24 -> 39 single (+8 V7.1), 31 -> 46 fleet (+8 V7.1 Fleet)
- Nouvelles lignes V6: Deadline Guardian, Alloti Guardian, Enveloppe Separator, Certif Live Checker, PAB Detector, Contentieux Generator, Post-Gagné Tracker
- Nouvelles lignes V7.1: Pénibilité RH, Vigilance URSSAF, ZAN Trackterres, Syntax Checker, Sourcing API, Local LLM Fallback, DLQ Reconciliation, Fleet License Updater
- Voir RAPPORT §12 pour détail tests bloquants

### §2 Différenciateurs
- V6 : 12 -> 28 boucliers
- V7.1 : 28 -> 33 boucliers
- Ajout 16 nouveaux modules V6 listés §2 + descriptions §7.13 à §7.28
- Ajout 5 nouveaux modules V7.1 + descriptions §7.29 à §7.33
- Doctrine intacte + double moteur IA ZERO € / Garage Math Decimal

### §3 RBAC étendu 14 lignes V6
- Ajout §3.1bis avec 14 lignes détaillées: Deadline J-7/J-2/J-1 blocage dépôt, Alloti similarité <85%, Enveloppe 47 pièces 3 enveloppes DUME vs DC1/DC2, Certif J-90/J-60/J-30 Qualibat/RGE/MASE, PAB -27% marge min 6% Admin only, Avenant Tracker OS récolement avenant max 20%, RSE +15%, Coherence, Variante, Matériaux Shield, Visite Auto GPS, MAPA, E+C-, Contentieux/Capacité/Tableau Risques Admin Only
- Voir RAPPORT §3.1bis

### §6 Nouveau Corrections Juridiques Critiques P0 + préservation ancien §6
- §6.1 CCAG 2021: 10% public + seuil 1000€ / 5% privé NF P03-001 / CCMI sans plafond 1/3000e (erreur V5 corrigée)
- §6.2 PAB -20 à -30% justification 48h
- §6.3 Matériaux post-covid acier bois cuivre distinct BT01
- §6.4 Avance minimale 2024 30% État / 10% EPA>60M€ collectivités RG max 5%
- §6.5 Stack Technique V12 préservé + SSoT Handbook

### §7 Cœur 33 modules complets Trigger IA ZERO € Garage Vue Salarié Action Patron Output Risque
- 7.1-7.12 préservés + compléments V6 CCAG 10% etc.
- 7.13 Deadline Guardian J-7/J-2/J-1 blocage dépôt ICS
- 7.14 Alloti Guardian similarité <85%
- 7.15 RSE Booster +15% note heures insertion
- 7.16 Prix-Mémoire Coherence score 62% IRRÉALISTE
- 7.17 Variante Guardian base+variante
- 7.18 Matériaux Shield perte=montant*variation*duree/12 acier bois cuivre distinct BT01
- 7.19 PAB Detector écart -27% marge min 6%
- 7.20 Visite Auto GPS attestation auto
- 7.21 Enveloppe Separator 47 pièces 3 enveloppes DUME vs DC1/DC2
- 7.22 Avenant Tracker OS récolement avenant max 20%
- 7.23 Contentieux Generator mémoire réclamation + mise en demeure intérêts LME 3×BCE
- 7.24 Certif Live Checker J-90/J-60/J-30 Qualibat/RGE/MASE
- 7.25 Capacité Financière FR=CapPerm-Immo CAF endettement
- 7.26 Tableau Risques marge résiduelle <3% No-Go comité direction 1 page
- 7.27 MAPA Generator dossier 10-15p
- 7.28 E+C- Detector CO2 vs seuils
- 7.29 Pénibilité RH Shield surcoût intérim +42k€
- 7.30 Vigilance URSSAF & Délit Marchandage solidarité 140k€
- 7.31 ZAN & Trackterres Shield coût évacuation +28k€
- 7.32 Syntax Checker Formules Révision Σcoeffs=1
- 7.33 Sourcing & API Profil Acheteur dépôt 1 clic
- Voir RAPPORT §7.13 à §7.33 pour spécifications complètes
- Voir RAPPORT §7.1 à §7.12 archives V12 préservées

### §8 Tableau récap 33 lignes
- Trap Detector base + 33 modules = 34 lignes (incl. base)
- Colonnes: Entrées, IA ZERO €, Solver Garage, Référentiels, Vue Salarié, Vue Admin, Output
- Archive V12 12 lignes préservée en sous-section

### §9 Garage 16 solveurs
- 5 historiques + 11 étendus V6 + 5 V7.1 = 21 solveurs nominaux (16 actifs Garage V7.1)
- Formules explicites: capacite_financiere FR=CapPerm-Immo, risques_generator <3%, mapa_generator, eplusc_calculator CO2 vs seuils, pab_detector -20% orange -30% rouge + justif 48h, materiaux_shield perte=montant*variation*duree/12, penibilite_solver surcoût intérim, vigilance_solver exposition URSSAF, zan_solver coût évacuation ISDI, formule_algebra_checker Σcoeffs=1, sourcing_api_solver scoring API
- Référentiels: indices_matériaux_insee.json, seuils_eplusc.json, fdes_produits_btp.json, ratios_financiers_btp.json, taux_bce_mensuel.json, referentiel_isdi.json, urssaf_penibilite.json, coefficients_revision_insee.json + 5 historiques
- Archive V12 5 solveurs préservée

### §10 Dashboards V6
- Finance Warfare 5 tuiles € Admin (BT projection, pénalités 10% public, trésorerie 30%/5%, REP, Site)
- Deadline Guardian Dashboard J-7/J-2/J-1/H-4
- Contentieux & Post-Gagné Dashboard Admin (OS, récolement, avenant 20%, mémoire réclamation)
- Qualifications & Capacité Dashboard Admin (J-90/J-60/J-30 + FR CAF)
- Vault, HANDOFF+, Wizard préservés
- Voir RAPPORT §10.4 à §10.6

### §12 Go/No-Go 39/46
- 39 single = 17 historiques + 7 V6 (test_deadline_guardian, test_alloti_guardian, test_enveloppe_separator, test_certif_live_checker, test_pab_detector, test_contentieux_generator, test_post_gagne_tracker) + 8 V7.1 (test_penibilite_rh, test_vigilance_urssaf, test_zan_trackterres, test_formule_revision, test_sourcing_api, test_local_llm_fallback, test_dlq_reconciliation, test_fleet_license_updater)
- 46 fleet = 39 single + 7 fleet isolation + monitoring + 8 V7.1 Fleet
- Gate bloquant check_go_nogo.sh vert

---

## V. INTÉGRATION V3.2 → V7.1 : PRÉSERVATION DE L'ADN V3.2 (Passe 1/2 + Passe 2/2 + Trésors)

> **SSoT Intégration Complète :** Cette section fusionne le rapport d'audit "V3.2 to V7.1" (Passe 1/2 + Passe 2/2) avec le "Rapport de préservation de l'ADN V3.2".

### V.0 Synthèse : Ce qui est déjà couvert par la V7.1

La V7.1 absorbe naturellement 80% de la puissance métier de la V3.2 via ses Engines :
- **Wizard 12 étapes** → Absorbé par le Workflow Engine et l'UI Engine (Wizard Salarié)
- **Chiffrage OR-Tools & Simulation** → Absorbé par le Math Engine (Garage)
- **RAG Historique Entreprise** → Absorbé par le Knowledge Engine (Qdrant remplace pgvector)
- **45+ Documents générés** → Absorbés par les 33 Agents
- **Audit DTU & Clauses** → Absorbé par le Knowledge Engine (FTS btp_french) et les Agents Juridiques

### V.1 Les 7 TRÉSORS V3.2 À INJECTER IMPÉRATIVEMENT DANS LA V7.1

#### 🏆 Trésor 1 : L'Application Desktop Native (Tauri v2) & Web Fallback

**Le constat V3.2 :** L'UI n'est pas juste un site web, c'est une **application Desktop native** (Tauri v2) installable (AppImage, .deb, .exe) avec un fallback Web (Nginx) pour l'accès VPS distant.

**L'intégration V7.1 :** Tauri devient le **Client Edge Natif** qui consomme l'API Gateway et l'UI Engine du VPS Single-Tenant.

**Actions SSoT :**
- **Arborescence_V7.1.txt :** Dossier `desktop/` (Tauri v2 + Rust backend) + `scripts/build_desktop.sh` ajoutés
- **ARCHITECTURE_V7_ENGINE.md :** Déploiement hybride "Tauri Desktop (Client lourd) + Nginx Web Fallback (VPS)" documenté dans Edge: UI Engine
- **PLAN_MAITRE_V7.1:** Sprint V32-1 inclut pont Tauri ↔ UI Engine

#### 🏆 Trésor 2 : La Philosophie "Anti-ERP" (Charte UX Stricte)

**Le constat V3.2 :** Pas de sidebar, pas de chatbot générique, max 4 champs par écran, linéarité stricte, masquage du modèle LLM ("Votre IA").

**L'intégration V7.1 :** Doctrine préservée et renforcée dans V7.1.

**Actions SSoT :**
- **RAPPORT §3.2 (NOUVEAU) :** Charte UX Anti-ERP avec règles :
  - **Linéarité stricte** (pas d'onglets dans le wizard)
  - **Max 4 champs visibles** par écran
  - **Terminologie "Votre IA"** (jamais "Mistral" ou "LLM")
  - **Zéro sidebar permanente** — l'écran principal est la liste des AO
  - **Un bouton à la fois** — le salarié ne peut pas se tromper

#### 🏆 Trésor 3 : Le Mode Panique (< 48h)

**Le constat V3.2 :** Déclencheur manuel (`Ctrl+Shift+M`) ou auto (`< 48h`). Génère le "minimum vital" pour déposer et ne pas être éliminé : DUME template + mémoire template + PPSPS + DPGF + AE.

**L'intégration V7.1 :** Transformé en **Mission à priorité URGENTE** avec bypass des optimisations.

**Actions SSoT :**
- **RAPPORT §7.34 (NOUVEAU) — Mode Panique (Emergency Bypass) :**
  - *Trigger :* Deadline < 48h ou raccourci `Ctrl+Shift+M`
  - *Garage/Math :* Bypass des optimisations lourdes, injection de templates Vault bruts
  - *Workflow :* FAST_TRACK_CAPS = {"CHECK_DEADLINE", "GENERER_DC4", "SEPARER_ENVELOPPE", "DETECTER_PAB", "GENERER_MEMOIRE_TEMPLATE", "GENERER_DPGF_TEMPLATE"}
  - *Output :* ZIP "Minimum Vital" non bloquant généré en **<3 minutes**
  - *Implémentation :* Voir ARCHITECTURE_V7_ENGINE.md §9.3 + PLAN_MAITRE_V7.1 §16.2

#### 🏆 Trésor 4 : Le Routeur LLM Multi-Providers (OpenAI-Compatible)

**Le constat V3.2 :** L'Onboarding permet de choisir son IA (Mistral, OpenAI, Anthropic, Deepseek, Kimi, Ollama).

**L'intégration V7.1 :** Routeur LLM unique avec défaut souverain + opt-in.

**Actions SSoT :**
- **ARCHITECTURE_V7_ENGINE.md §9.4 :** Bloc "LLM Router (Multi-providers)" dans Knowledge Engine
- **ENGINEERING-HANDBOOK §2 (ADR-064) :** Routeur LLM souverain avec Mistral EU par défaut, Ollama local pour Confidentiel, opt-in explicite pour hors-UE
- *Règle :* Le LLM **ne calcule JAMAIS les euros** (Garage Math uniquement)

#### 🏆 Trésor 5 : CLI & Onboarding Guidé en 5 Étapes

**Le constat V3.2 :** Commandes `smartao`, `smartao --dev`, `smartao --web`, `smartao --stop`. Onboarding (Serveur, IA, Profil).

**L'intégration V7.1 :** CLI unifiée + onboarding préservé.

**Actions SSoT :**
- **Arborescence_V7.1.txt :** `scripts/smartao` (CLI unifiée) + `scripts/smartao_cli.py` ajoutés
- **RAPPORT §2.1 (NOUVEAU) — Setup & Onboarding :**
  1. Bienvenue
  2. Connexion VPS
  3. **Routeur LLM** (Mistral EU défaut, opt-in autres, local si Confidentiel)
  4. Import Vault A01-A12
  5. Premier AO golden file
- **PLAN_MAITRE_V7.1 §15 :** Onboarding 5 étapes dans sprint V32-2

#### 🏆 Trésor 6 : Sélecteur ZIP Manuel & Export Word Natif

**Le constat V3.2 :** L'utilisateur garde le contrôle final via un "Sélecteur ZIP" (cocher/décocher les docs à inclure) et l'export Word natif (.docx) pour retouche manuelle.

**L'intégration V7.1 :** Enveloppe Separator enrichi avec contrôle manuel.

**Actions SSoT :**
- **RAPPORT §7.21 (ENRICHI) — Enveloppe Separator :**
  - Vue Salarié : **Sélecteur ZIP Interactif** (Drag & Drop des 47 pièces vers les 3 enveloppes)
  - Vue Admin : Exigence d'export **.docx natif** (via `python-docx`) pour le Mémoire Technique et le PPSPS
  - *Justification :* Le patron BTP veut toujours pouvoir retoucher manuellement ses documents avant dépôt

#### 🏆 Trésor 7 : Watermark & Gestion des Licences (Demo/Essentiel/Pro)

**Le constat V3.2 :** Gestion des filigranes sur les documents générés selon la licence achetée.

**L'intégration V7.1 :** Fleet Engine lié au Document Engine.

**Actions SSoT :**
- **RAPPORT §15 (INTÉGRATION) :** Lier le `Fleet Engine` au `Document Engine` pour l'application dynamique de **Watermarks**
- **ENGINEERING-HANDBOOK §2 (ADR-068) :** Watermarking dynamique des exports PDF/Word
- *Règles :* "DEMO - NON VALABLE POUR DEPOT" sur les exports si licence != Pro/Perpetuelle

---

## VI. INTÉGRATION V3.2 → V7.1 : MATRICE FONCTIONNELLE COMPLÈTE

> **Source unique fonctionnelle SSoT :** Cette section intégrée du rapport d'audit "V3.2 to V7.1" remplace et complète toute référence à l'intégration dans le corpus.
> **Voir aussi :** PLAN_MAITRE_V7.1 §14-18 pour le plan technique, ARCHITECTURE_V7_ENGINE.md §9 pour l'architecture, ENGINEERING-HANDBOOK §2 pour les ADR.

### V.1 Diagnostic V3.2 : 4 Frictions Mortelles (Passe 1/2 §1)

La V3.2 est un excellent MVP Desktop, mais pour le marché BTP français de 2026, elle présente 4 failles structurelles que le Kernel V7.1 doit corriger **sans casser l'UX Tauri**.

| # | Friction | Existant V3.2 | Risque BTP | Correction V7.1 |
|---|----------|---------------|------------|-----------------|
| **1** | Péril Hallucinatoire | LLM (Mistral/Ollama) utilisé pour analyse, tri, et potentiellement chiffrage déboursé sec | Un LLM hallucine les chiffres. Sur DPGF 400 lignes, une erreur de virgule ou un calcul de marge inventé = **élimination PAB ou faillite à l'exécution** | **Ségrégation Cognitive** : Knowledge Engine (IA) lit, extrait, classe (Zéro € dans findings). Math Engine (Garage) calcule avec PuLP, OR-Tools, Decimal 28 (16 solveurs, corrections P0 CCAG 10%/5%/CCMI). **Le LLM n'a plus le droit de toucher à la calculatrice.** |
| **2** | Myopie Sémantique | RAG basé sur pgvector (PostgreSQL) | pgvector est aveugle au jargon technique BTP. Ne différencie pas CCAG Travaux de CCMI, rate acronymes DTU ou clauses révision spécifiques | **Qdrant** (mode on_disk pour économiser RAM) avec embeddings BGE-M3 1024d + Recherche Hybride (Dense + Sparse RRF) + Fallback Full-Text Search Postgres avec dictionnaire custom btp_french |
| **3** | Monolithe Synchrone | API FastAPI classique avec endpoints métiers bloquants | Si parsing DCE 200 pages bloque, tout le wizard freeze | **Architecture OS avec 9 Engines**. 33 modules métiers ne sont plus des endpoints, mais des Agents (BaseAgent) orchestrés par WorkflowEngine (6 étapes canoniques) via EventBus asynchrone (asyncio.Queue + persistance PG + DLQ) |
| **4** | Absence d'Étanchéité Financière | Pas de ségrégation stricte des données financières dans les réponses API | Fuite des € = mort de l'entreprise | **RBAC V7.1** = question de survie. **Salarié = Zéro € visible**. **Patron = Finance Warfare Dashboard**. Security Engine applique strip_provisions_euros_v7 sur chaque réponse API et génère double artefact HANDOFF+ |

### V.2 Matrice d'Intégration Fonctionnelle V3.2 → V7.1 (Passe 2/2 §I)

**21 fonctions V3.2 analysées, 5 décisions possibles : RÉUTILISER / ADAPTER / CONSTRUIRE / MIGRER / ABANDONNER**

| # | Fonction v3.2 | Atterrissage V7.1 | Statut V7.1 | Verdict | Impact |
|---|---------------|------------------|-------------|---------|--------|
| 1 | App Desktop Tauri v2 (React/TS/Tailwind/Zustand) | Edge UI Engine + shell Tauri | UI Engine présent (stubs), Tauri absent | 🟡 **ADAPTER** | Conserver shell Tauri, consomme API Gateway + WS V7.1 |
| 2 | Onboarding 5 étapes | Absent | Absent | 🔵 **CONSTRUIRE** | wizard onboarding (serveur, LLM, Vault) |
| 3 | Wizard 12 étapes | Wizard 10 étapes | Partiel | 🟡 **ADAPTER** | Aligner sur 10 étapes, préserver UX v3.2 |
| 4 | Mode Panique (<48h / Ctrl+Shift+M) | Absent | Absent | 🔵 **CONSTRUIRE** | Mission priority=URGENTE fast-track |
| 5 | Chat Orchestrateur (intent) | Absent (doctrine : pas de chatbot) | Absent | ⚫ **ABANDONNER** | Désactivé par défaut (feature flag ENABLE_CHAT=false) |
| 6 | Go/No-Go scoring adaptation | Go/No-Go 39/46 gates | Présent | 🟢 **RÉUTILISER** | Mapper scoring sur gates |
| 7 | Extraction métré (CCTP + DPGF/OCR) | Document Engine + Cross-Check 7.9 | Partiel | 🟡 **ADAPTER** | |
| 8 | Chiffrage déboursé sec + OR-Tools | Math Engine chiffrage_pulp + planning | Présent | 🟢 **RÉUTILISER** | |
| 9 | Audit conformité DTU | Knowledge Engine RAG (DTU) | Partiel | 🟡 **ADAPTER** | |
| 10 | Analyse clauses + Rapport Négociation | Q/R Tactique 7.10 + Contentieux 7.23 | Présent | 🟢 **RÉUTILISER** | |
| 11 | 45+ documents générés | Générateurs DOCX/PDF | Partiel | 🟡 **ADAPTER** | |
| 12 | Sélecteur ZIP manuel | Enveloppe Separator 7.21 | Présent | 🟡 **ADAPTER** | UI sélection manuelle |
| 13 | Licences & Watermark | Fleet license_checker | Partiel | 🟡 **ADAPTER** | watermark demo + perpétuel |
| 14 | Profil entreprise qualifié | Vault A01-A12 | Présent | 🟢 **RÉUTILISER** | |
| 15 | Analytics & Dashboard | Dashboards cockpit | Présent | 🟢 **RÉUTILISER** | |
| 16 | Workflow multi-utilisateurs | RBAC rôles | Présent | 🟢 **RÉUTILISER** | |
| 17 | RAG historique entreprise | Collection Qdrant chantiers | Présent | 🟢 **RÉUTILISER** | |
| 18 | Charte graphique personnalisée | Personnalisation entreprise | Partiel | 🟡 **ADAPTER** | |
| 19 | Export Word natif | Génération DOCX | Partiel | 🟢 **RÉUTILISER** | python-docx |
| 20 | Stack pgvector/Redis/MinIO/Compose | Qdrant/Redis/MinIO/Compose | Présent | 🔵 **MIGRER** | pgvector→Qdrant |
| 21 | CLI smartao / --dev / --web / --stop | scripts/ | Partiel | 🟡 **ADAPTER** | CLI unifié |

**Bilan :** 8 RÉUTILISER · 8 ADAPTER · 3 CONSTRUIRE · 1 MIGRER · 1 ABANDONNER = **21 fonctions traitées**

**Verdict fonctionnel :** La v3.2 n'apporte presque rien de NOUVEAU sur le métier (V7.1 est strictement supérieur), mais apporte **3 actifs UX irremplaçables** : le shell Tauri, le Mode Panique, et l'onboarding. **Ce sont eux qu'il faut sauver.**

### V.3 Intégration UX : Wizard, Onboarding, Mode Panique (Passe 2/2 §II)

#### V.3.1 Wizard : 12 étapes v3.2 → 10 étapes V7.1

Le wizard v3.2 (12 étapes) et le wizard V7.1 (10 étapes) couvrent le même flux. **Solution : garder la numérotation V7.1 (10 étapes) et absorber les étapes v3.2.**

| v3.2 | → V7.1 |
|---|---|
| 1 Identify | Step01 Identify |
| 2 Upload DCE | Step02 Upload |
| 3 Analyze | Step03 Analyze (WS streaming 33 modules) |
| 4 Go/No-Go | Step04 Go/No-Go (gates 39/46) |
| 5 Visite | Step05 Visite |
| 6 Métré | Step06 Métré |
| 7 Chiffrage | **réservé Admin** (le salarié ne voit pas €) |
| 8 Docs admin | Step07 Docs |
| 9 Docs techniques | Step08 Docs tech |
| 10 Docs financiers | **réservé Admin** |
| 11 Conformité + ZIP | Step09 Conformité + ZIP |
| 12 Dépôt | Step10 Dépôt (API PLACE) |

#### V.3.2 Mode Panique → Mission URGENTE Fast-Track (CODE)

Le Mode Panique v3.2 devient une **Mission à priorité URGENTE** qui restreint les capabilities au "minimum vital" :

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

**Déclencheur :** deadline < 48h auto **OU** raccourci Ctrl+Shift+M côté Tauri → POST /api/dce/analyze avec priority="URGENTE"

#### V.3.3 Chat Orchestrateur : Décision ABANDONNER

La doctrine V7.1 est « un bouton à la fois, pas de chatbot ». **Le Chat Orchestrateur v3.2 contredit cette doctrine.**

**Décision :** ABANDONNER par défaut. Si souhaité, réintroduire comme assistant optionnel désactivé (feature flag ENABLE_CHAT=false), jamais comme entrée principale.

#### V.3.4 Onboarding 5 étapes → à construire

Mapper les 5 étapes v3.2 sur V7.1 :
1. Bienvenue
2. Connexion VPS
3. Routeur LLM (Mistral EU défaut, opt-in autres, local si Confidentiel)
4. Import Vault A01-A12
5. Premier AO golden file

C'est le seul morceau UX manquant à construire.

### V.4 Modèle Commercial & Licences : 3 700€ perpétuel vs 549€/mois (Passe 2/2 §III)

La v3.2 vend une **licence perpétuelle 3 700€** ; V7.1 vend **549€/mois** ou **2 490€ setup**. La réconciliation se fait dans le Fleet Engine license_checker :

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

**Règle commerciale :**
- Les clients v3.2 perpétuels **gardent leur licence** (watermark absent)
- MAIS **sans** les boucliers V7.1 (7.29-7.33) sauf upgrade
- Les nouveaux clients partent sur **549€/mois**
- Cela préserve la base installée sans casser le MRR

### V.5 Ponts Code V3.2 → V7.1 (Passe 2/2 §IV)

#### V.5.1 Routeur LLM OpenAI-compatible
```python
# app/engines/knowledge_engine/llm_router.py
class LLMRouter:
    def __init__(self, provider: str = "mistral", confidentiel: bool = False):
        if confidentiel:
            self.client = OllamaClient("mistral:7b")     # local, zéro sortie de données
        elif provider == "mistral":
            self.client = MistralEUClient()              # défaut souverain EU
        elif provider in ("openai", "deepseek", "kimi"):
            self.client = OpenAICompatible(provider)      # opt-in explicite + disclaimer RGPD
```

#### V.5.2 Migration pgvector → Qdrant (script one-shot)
```python
# scripts/migrate_pgvector_qdrant.py
for row in pg.execute("SELECT doc_id, chunk, embedding, meta FROM embeddings"):
    qdrant.upsert(collection="dce", points=[Point(id=row.doc_id,
        vector=row.embedding, payload=row.meta)])
```

#### V.5.3 CLI unifié smartao
```bash
# scripts/smartao
smartao          # backend + fenêtre desktop Tauri
smartao --dev    # rebuild Tauri à chaud
smartao --web    # backend seul (fallback web)
smartao --stop   # arrêt stack
```

#### V.5.4 Pont Tauri ↔ UI Engine (WebSocket)
```typescript
// desktop/src/bridge.ts
const ws = new WebSocket(`ws://${vps}/ws/mission/${missionId}`);
ws.onmessage = (e) => store.dispatch(eventFromV7(JSON.parse(e.data)));
```

### V.6 Plan d'Action Code : 3 Sprints Priorisés (Passe 2/2 §V)

| Sprint | Contenu | Fichiers | Gate |
|--------|---------|---------|------|
| **V32-1** | Ponts stack : routeur LLM, migrate pgvector→Qdrant, CLI unifié, pont Tauri WS | llm_router.py, migrate_pgvector_qdrant.py, scripts/smartao, desktop/src/bridge.ts | routeur + migration verts |
| **V32-2** | Mode Panique + onboarding | mission.py (URGENTE), workflow.py (FAST_TRACK), wizard onboarding | Mode Panique E2E <3min |
| **V32-3** | Modèle commercial : license_checker perpétuel/abonnement + watermark | fleet_engine/license_checker.py | licence perpétuelle validée sans watermark |

**Ordre imposé :** V32-1 → V32-2 → V32-3. Ne pas toucher au Kernel V7.1 pendant ces sprints (feature flag USE_WORKFLOW_ENGINE maintenu).

### V.7 Go/No-Go d'Intégration & Verdict Final (Passe 2/2 §VI)

| Critère | Exigence | Statut |
|---------|----------|--------|
| Shell Tauri branché sur API Gateway + WS V7.1 | WS streaming OK | À construire (V32-1) |
| Mode Panique = Mission URGENTE fast-track | E2E <3min, ZIP minimum vital | À construire (V32-2) |
| pgvector→Qdrant sans perte | upsert 100% chunks | À exécuter (V32-1) |
| Licences perpétuelles v3.2 honorées | watermark absent pour perpétuels | À construire (V32-3) |
| Chat Orchestrateur | désactivé par défaut | Décision : ABANDONNER |
| Gates V7.1 | 39/39 Single + 46/46 Fleet | Inchangés, bloquants |

**Verdict final de l'intégration :**
> La v3.2 est une **bonne base UX** posée sur une **mauvaise base technique** (pgvector, LLM qui calcule, pas de RBAC étanche). La V7.1 est l'inverse : **excellente base technique**, UX à parfaire. L'intégration correcte consiste donc à **transplanter le cœur V7.1 sous le shell v3.2**, en sauvant exactement trois actifs (Tauri, Mode Panique, onboarding), en migrant les données (pgvector→Qdrant), et en réconciliant les licences via le Fleet Engine. Tout le reste de la v3.2 est soit déjà supérieur dans V7.1, soit à abandonner (chatbot).

> **L'intégration est faisable en 3 sprints (V32-1/2/3) sans casser le Kernel.** Une fois V32-1/2/3 verts ET 39/39 + 46/46 verts, le produit est le monopole décrit : **le shell agréable de la v3.2, le cerveau souverain et le coffre-fort de la V7.1.**

---

### VI.4 PLAN D'INJECTION DANS LA DOCUMENTATION (CHECKLIST D'EXÉCUTION)

Pour que la V7.1 soit parfaitement rétro-compatible avec le succès commercial de la V3.2, voici les modifications apportées aux documents SSoT :

| Document SSoT | Section à Modifier / Créer | Ajout V3.2 à Intégrer | Statut |
| :--- | :--- | :--- | :--- |
| **RAPPORT (1).md** | §2.1 Setup & Onboarding | Wizard 5 étapes (Serveur, LLM Router, Vault) | ✅ Intégré |
| **RAPPORT (1).md** | §3.2 Charte UX (NOUVEAU) | Règles Anti-ERP (Max 4 champs, Linéarité, "Votre IA") | ✅ Intégré |
| **RAPPORT (1).md** | §7.21 Enveloppe Separator | Sélecteur ZIP Interactif + Export Word Natif (.docx) | ✅ Intégré |
| **RAPPORT (1).md** | §7.34 Mode Panique (NOUVEAU) | Trigger <48h, ZIP Minimum Vital, Bypass Garage | ✅ Intégré |
| **ARCHITECTURE_V7_ENGINE.md** | Edge: UI Engine | Wrapper Tauri v2 + Fallback Nginx | ✅ Intégré |
| **ARCHITECTURE_V7_ENGINE.md** | L2: Knowledge Engine | LLM Router (Multi-providers OpenAI-compatible) | ✅ Intégré |
| **ARCHITECTURE_V7_ENGINE.md** | Fleet Engine | Watermarking dynamique des exports PDF/Word | ✅ Intégré |
| **Arborescence_V7.txt** | `/desktop/` (NOUVEAU) | Code source Tauri v2 (Rust + React) | ✅ Intégré |
| **Arborescence_V7.txt** | `/scripts/smartao_cli.py` | CLI unifiée (`smartao`, `--dev`, `--web`) | ✅ Intégré |
| **MANIFESTE_V7.md** | §5 Les 4 Armes | Ajouter "Application Desktop Native + Mode Panique" | ✅ Intégré |

---

### Annexes A-U
- A DCE Trap Detector 4 familles routage 28 modules
- B Vault A01-A12
- C Cockpit 11 modules (8 + 3 V6)
- D Wizard 12 étapes 28 modules
- E RAG Hybrid
- F MCP
- G Stack
- H Blocs dépendance
- I Go/No-Go 39 critères
- J Conclusion
- K Modules 7.1-7.12 exhaustif
- L Modules 7.13-7.28 exhaustif V6
- M Modules 7.29-7.33 exhaustif V7.1 (nouveau)
- N Référentiels 15 JSON (5 + 5 V6 + 5 V7.1)
- O Générateurs DOCX/PDF V6/V7.1
- O Vision 4 mondes V6
- P Cockpit APIs V6
- Q Workflow 12 états V6
- R Mémoire+Q/R+HANDOFF+ workflow complet
- S Stack & Commercial V6
- T Règles d'or codage
- U Conclusion architecte 20 ans terrain
- Voir RAPPORT Annexes A-U

### Annexes archivées V12
- V Conclusion 20 ans terrain code (préservée)
- W Cas d'usage BTP réels 12M€ 14 lots etc. + workflows pas à pas + sécurité filesystem _check_access + RBAC serializer + 5 moteurs + MCP + build chain + 23 ADR + tests bloquants 20 tests (80-100 pages historique)
- Y Edge cases + matrice décisionnelle 17 critères + workflows alternatifs sans DPGF + SLAs + RGPD + Heartbeat + formation + support
- Z Glossaire BTP
- AA Détails techniques fonctionnels + JSON schemas + notifications + permissions API + verrouillages + DCE Trap Detector JSON complet + Finance Warfare JSON
- AC Récap une page par module + FAQ 20 questions + conclusion taille
- Voir section ARCHIVES V12

> Aucune suppression. Tout l'existant V12 est présent soit dans sa section d'origine enrichie, soit en archive marquée "préservée".

