# Documentation Complète — Application NeuroCap
## Plateforme Adaptive de Neurofeedback EEG

---

> **Objectif de ce document :** Expliquer en détail toute l'application NeuroCap, du signal brut de l'électrode jusqu'à l'interface utilisateur, pour préparer la soutenance et répondre aux questions du jury.

---

## Table des matières

1. [Vue d'ensemble du projet](#1-vue-densemble-du-projet)
2. [Architecture globale](#2-architecture-globale)
3. [Backend — FastAPI](#3-backend--fastapi)
   - 3.1 Point d'entrée et cycle de vie
   - 3.2 Configuration centralisée
   - 3.3 Authentification et sécurité
   - 3.4 Couche base de données (Supabase)
   - 3.5 Routes API (endpoints)
   - 3.6 Services métier
   - 3.7 Pipeline EEG temps réel
   - 3.8 Traitement du signal (DSP)
   - 3.9 Fine-tuning adaptatif
   - 3.10 Moteur d'adaptation (seuils dynamiques)
   - 3.11 Assistant RAG
4. [Frontend — React 18](#4-frontend--react-18)
   - 4.1 Structure et routage
   - 4.2 Pages principales
   - 4.3 Composants clés
   - 4.4 Gestion d'état (Zustand)
   - 4.5 Communication avec le backend
   - 4.6 Internationalisation et thèmes
5. [Intelligence Artificielle et Machine Learning](#5-intelligence-artificielle-et-machine-learning)
   - 5.1 Pipeline de données
   - 5.2 Extraction de features
   - 5.3 Modèles ML classiques (baseline)
   - 5.4 Architectures Deep Learning (17 modèles)
   - 5.5 Domain Adversarial Neural Networks (DANN)
   - 5.6 Transfer Learning (3 stratégies)
   - 5.7 Moteur d'inférence unifié
6. [Base de données — Supabase PostgreSQL](#6-base-de-données--supabase-postgresql)
7. [Sécurité](#7-sécurité)
8. [Déploiement](#8-déploiement)
9. [Flux de données de bout en bout](#9-flux-de-données-de-bout-en-bout)
10. [Questions probables du jury — Réponses préparées](#10-questions-probables-du-jury--réponses-préparées)

---

## 1. Vue d'ensemble du projet

### Qu'est-ce que NeuroCap ?

**NeuroCap** est une plateforme complète de **neurofeedback adaptatif** basée sur l'EEG (électroencéphalographie). Elle permet à des patients de s'entraîner à réguler leur activité cérébrale (concentration ou relaxation) en temps réel, guidés par des retours visuels, audio ou ludiques.

### Problème adressé

Les solutions de neurofeedback existantes sont :
- Très coûteuses (matériel médical homologué)
- Non adaptatives (seuil fixe pour tous les patients)
- Sans suivi clinique intégré
- Sans personnalisation par IA

NeuroCap résout ces problèmes avec un casque EEG low-cost (**AD8232 + ESP32**) et une IA qui s'adapte à chaque patient.

### Ce que fait l'application

| Fonctionnalité | Description |
|---|---|
| Acquisition EEG | Réception du signal de l'ESP32 via TCP/IP à 250 Hz |
| Traitement DSP | Filtrage, épochage, rejet d'artefacts en temps réel |
| Classification IA | Détection concentration / stress en temps réel (seuil confiance 60%) |
| Neurofeedback | 5 modalités de retour (image, audio, vidéo, jeux) |
| Adaptation | Seuils dynamiques ajustés automatiquement par session et entre sessions |
| Fine-tuning | Modèle IA personnalisé par patient (nuit, après session) |
| Suivi clinique | Thérapeute voit les rapports, pose des notes, ajuste le niveau |
| Administration | Admin gère les utilisateurs, voit les stats, envoie des rappels |
| Assistant IA | Chatbot RAG pour répondre aux questions sur l'EEG/neurofeedback |

### Stack technologique résumée

```
Hardware      : AD8232 + ESP32 (Fp2, 250 Hz, TCP/IP)
Backend       : FastAPI (Python 3.11) + Supabase PostgreSQL
Frontend      : React 18 + Vite + Tailwind CSS + Three.js
ML/DSP        : PyTorch + LightGBM + SciPy + MNE + PyWavelets
Communication : WebSocket (temps réel) + REST API (données)
Emails        : Brevo SMTP (300 mails/jour gratuit)
LLM local     : Ollama + Mistral (RAG assistant)
Déploiement   : Docker Compose
```

---

## 2. Architecture globale

```
┌─────────────────────────────────────────────────────────────────────┐
│                          HARDWARE                                    │
│  AD8232 (électrode Fp2) ──→ ESP32 ──→ TCP :9000 ──→ Backend        │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       BACKEND (FastAPI)                              │
│                                                                      │
│  TCPReceiver ──→ DSP Pipeline ──→ Classifier ──→ WebSocket          │
│        │              │               │               │             │
│     250 Hz         filtrage        LightGBM      Broadcast         │
│    échantillons    épochage      concentration/  vers frontend      │
│                   features         stress                           │
│                                                                      │
│  REST API ──→ Auth / Sessions / Admin / Therapist / Assistant       │
│                                                                      │
│  AdaptiveEngine ──→ seuils dynamiques (EWMA + blocs 3 min)          │
│  FineTuner ──→ modèle personnalisé par patient (APScheduler 2h UTC) │
│  RAGService ──→ Ollama Mistral + base de connaissances              │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
                    Supabase PostgreSQL (cloud)
                                   │
┌──────────────────────────────────▼──────────────────────────────────┐
│                      FRONTEND (React 18)                             │
│                                                                      │
│  Dashboard Patient ──→ Brain3D + EEGVisualization + BandBars        │
│  FeedbackPage ──→ Setup → Session Live → Rapport                    │
│  AdminDashboard ──→ 6 KPIs + gestion utilisateurs                   │
│  TherapistDashboard ──→ patients + notes + recommandations          │
│  Assistant ──→ RAGChat (questions EEG)                              │
└─────────────────────────────────────────────────────────────────────┘
```

**Trois rôles d'utilisateur :**
- **Patient** : fait ses sessions, voit ses rapports, utilise le neurofeedback
- **Thérapeute** : suit ses patients assignés, ajoute des notes cliniques, ajuste le niveau
- **Admin** : gère tous les utilisateurs, voit les statistiques globales

---

## 3. Backend — FastAPI

### 3.1 Point d'entrée et cycle de vie

**Fichier :** `app/Backend/app/main.py`

Le serveur FastAPI démarre avec un **lifespan** (cycle de vie) qui initialise tout dans l'ordre :

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # DÉMARRAGE
    await init_supabase()          # connexion à la base de données
    await init_eeg_pipeline()      # démarrage TCP + DSP + WebSocket
    scheduler.start()              # APScheduler pour fine-tuning nocturne
    yield
    # ARRÊT
    await close_supabase()
    scheduler.shutdown()
```

**WebSocket `/ws/eeg` :** canal temps réel entre le backend et le frontend.

Quand un patient ouvre la page de session, son navigateur se connecte à ce WebSocket. Le backend lui pousse des messages JSON en continu :

| Type de message | Contenu | Fréquence |
|---|---|---|
| `init` | statut ESP32, baseline calculée ou non | 1 fois |
| `eeg` | échantillon brut µV, timestamp | 62 Hz (tous les 16 ms) |
| `epoch` | concentration%, stress%, confiance, TBR, features | 1/sec (75% overlap) |
| `electrode` | qualité des électrodes Fp2/M1/M2 | 1/5 sec |
| `esp32_status` | connecté/déconnecté | à chaque changement |

**Commandes reçues du frontend via WebSocket :**

| Commande | Action |
|---|---|
| `FINALISE_BASELINE` | termine la calibration de base (calcule les Z-scores individuels) |
| `START_REC` | commence l'enregistrement CSV |
| `STOP_REC` | arrête l'enregistrement |
| `ANALYZE_NOW` | retourne un snapshot des métriques actuelles |

---

### 3.2 Configuration centralisée

**Fichier :** `app/Backend/app/config.py`

Toutes les variables d'environnement sont lues depuis le fichier `.env` et validées au démarrage. Paramètres clés :

```
EEG :
  - Fréquence d'échantillonnage : 250 Hz
  - Taille d'époque : 1000 échantillons = 4 secondes
  - Overlap : 75% → 1 époque produite chaque seconde
  - Seuil confiance : 0.60 (en dessous = "incertain")

JWT :
  - Access token : 30 minutes
  - Refresh token : 7 jours
  - Algorithme : HS256

Sécurité :
  - Max tentatives login : 5 → blocage IP 15 min
  - Rate limiting : 100 req/60s par IP

Modèles :
  - Chemin modèle global : models/best_model.pt
  - Chemin modèles personnalisés : models/personal/patient_{id}_v{n}.joblib
```

---

### 3.3 Authentification et sécurité

**Fichier :** `app/Backend/app/core/security.py`

#### Hachage des mots de passe (bcrypt)

On ne stocke JAMAIS un mot de passe en clair. bcrypt applique une fonction de hachage unidirectionnelle avec un "salt" aléatoire :

```
"MonMotDePasse123!" → $2b$12$xK3L...hash... (72 caractères)
```

La vérification compare le hash stocké avec le hash du mot de passe entré.

#### Tokens JWT (JSON Web Token)

Quand l'utilisateur se connecte, le backend crée 2 tokens :
1. **Access token** (30 min) : envoyé dans chaque requête API, contient `user_id` + `role`
2. **Refresh token** (7 jours) : sert à obtenir un nouveau access token sans re-login

```
JWT = header.payload.signature
payload = { "sub": "user_uuid", "role": "patient", "exp": timestamp }
```

#### Injection de dépendances pour les routes protégées

```python
@router.get("/patients")
async def list_patients(
    current_user = Depends(get_therapist_user)  # bloque si pas thérapeute
):
    ...
```

`get_current_user()`, `get_admin_user()`, `get_therapist_user()` vérifient le token JWT dans le header `Authorization: Bearer <token>` à chaque requête.

#### Protection brute-force

Un compteur en mémoire (ou Redis) suit les tentatives par IP :
- 5 échecs → IP bloquée 15 minutes → message d'erreur 429

#### Rate limiting

Fenêtre glissante : max 100 requêtes par 60 secondes par adresse IP. Protège contre le scraping et les attaques DDoS.

---

### 3.4 Couche base de données (Supabase)

**Fichier :** `app/Backend/app/core/database.py`

**Supabase** est une base PostgreSQL managée dans le cloud (pas besoin de gérer un serveur Postgres). On utilise leur **SDK Python asynchrone** :

```python
# Pattern Singleton : une seule connexion pour tout le serveur
_client: AsyncClient | None = None

async def get_supabase() -> AsyncClient:
    global _client
    if _client is None:
        _client = await create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    return _client
```

**Pourquoi Supabase et pas SQLAlchemy ?**
- Supabase offre une API REST directe, l'authentification intégrée, et le temps réel (Realtime)
- La `service_role_key` (clé secrète côté serveur) donne accès total à la DB
- Elle n'est JAMAIS exposée au frontend (risque de sécurité)

---

### 3.5 Routes API (endpoints)

#### `/api/auth/*` — Authentification

| Méthode + URL | Description |
|---|---|
| `POST /send-code` | Envoie un code de vérification à 8 chiffres par email (via Brevo) |
| `POST /register` | Crée un compte avec le code vérifié |
| `POST /login` | Retourne access + refresh tokens (messages d'erreur distincts : email inconnu vs mauvais mot de passe) |
| `POST /refresh` | Échange un refresh token contre un nouveau access token |
| `GET /me` | Retourne le profil de l'utilisateur connecté |

**Pourquoi des messages d'erreur distincts ?** C'est un choix UX délibéré pour faciliter le support (un admin peut distinguer "l'utilisateur n'existe pas" de "mauvais mot de passe").

#### `/api/eeg/*` — Acquisition et analyse EEG

| Méthode + URL | Description |
|---|---|
| `GET /status` | Statut de l'ESP32, baseline faite ou non, qualité signal |
| `GET /analyze` | Rapport DSP détaillé (PSD de toutes les bandes) |
| `POST /baseline/finalise` | Déclenche le calcul des Z-scores individuels après 2 min de calibration |
| `POST /recording/start` | Démarre l'enregistrement CSV |
| `POST /recording/stop` | Arrête l'enregistrement, retourne le chemin du fichier |
| `GET /recording/export` | Télécharge le CSV enregistré |
| `POST /analyze_file` | Upload + analyse d'un fichier EEG (.csv/.edf/.txt) hors ligne |
| `GET /wifi/networks` | Liste les réseaux WiFi visibles par l'ESP32 |
| `POST /wifi/configure` | Configure le WiFi de l'ESP32 (SSID + mot de passe) |
| `POST /report` | Sauvegarde un rapport EEG, notifie le thérapeute |
| `GET /my-reports` | Liste des rapports EEG du patient connecté |

#### `/api/sessions/*` — Sessions de neurofeedback

| Méthode + URL | Description |
|---|---|
| `GET /` | Liste paginée des sessions de l'utilisateur |
| `POST /` | Crée une session (objectif + mode feedback) |
| `GET /{id}` | Détails d'une session |
| `GET /{id}/report` | Rapport complet (métriques, stats, évolution) |
| `GET /{id}/export` | Export CSV de la session |

#### `/api/admin/*` — Administration (admin seulement)

| Méthode + URL | Description |
|---|---|
| `GET /stats` | 6 KPIs : total users, users actifs, thérapeutes, sessions, score moyen, nouveaux users |
| `GET /users` | Liste tous les utilisateurs avec leurs stats |
| `POST /users` | Crée un user (l'admin peut bypasser la vérification email) |
| `PUT /users/{id}` | Modifie le rôle, le statut, l'assignation thérapeute |
| `DELETE /users/{id}` | Soft delete (is_active = false, les données sont conservées) |
| `POST /assign-patient` | Assigne un patient à un thérapeute |
| `GET /audit-logs` | Journal d'audit des actions (login, création de compte, etc.) |
| `POST /send-reminders` | Envoie des emails de rappel aux users inactifs |

#### `/api/therapist/*` — Espace thérapeute

| Méthode + URL | Description |
|---|---|
| `GET /patients` | Liste les patients assignés avec leurs stats de session |
| `GET /patients/{id}` | Détail d'un patient |
| `GET /patients/{id}/sessions` | Historique des sessions d'un patient |
| `GET /patients/{id}/profile` | Profil EEG du patient (IAPF, baseline, palier) |
| `POST /patients/{id}/notes` | Ajoute une note clinique |
| `POST /patients/{id}/recommendation` | Pose une recommandation (palier cible + texte) |
| `PUT /patients/{id}/palier` | Ajuste manuellement le niveau de difficulté |
| `GET /patients/{id}/export` | Export CSV des sessions du patient |

#### `/api/assistant/*` — Assistant RAG

| Méthode + URL | Description |
|---|---|
| `POST /ask` | Pose une question, reçoit une réponse contextualisée (EEG/neurofeedback) |
| `POST /feedback` | Vote 👍/👎 sur la réponse pour améliorer le RAG |

---

### 3.6 Services métier

**Organisation des services :**

```
app/Backend/app/services/
├── eeg/
│   ├── eeg_pipeline.py          # orchestrateur principal
│   ├── tcp_receiver.py          # réception ESP32
│   ├── wifi_manager.py          # configuration WiFi ESP32
│   ├── dsp/
│   │   ├── filters.py           # filtres numériques
│   │   ├── epochs.py            # découpage en époques
│   │   ├── features.py          # extraction de features
│   │   ├── ml_classifier.py     # inférence LightGBM
│   │   └── artifacts.py         # détection d'artefacts
│   ├── finetune/
│   │   ├── runner.py            # fine-tuning par patient
│   │   ├── conditions.py        # conditions de déclenchement
│   │   └── scheduler.py         # APScheduler
│   └── adaptative_engine.py     # adaptation des seuils
├── email_service.py             # Brevo SMTP
└── rag_service.py               # assistant RAG Ollama
```

---

### 3.7 Pipeline EEG temps réel

**Fichier :** `app/Backend/app/services/eeg/eeg_pipeline.py`

Le pipeline EEG est le cœur du système. Il orchestre 5 composants qui travaillent en pipeline :

```
ESP32 (Wi-Fi)
    │
    ▼ TCP :9000
TCPReceiver
    │ 250 échantillons/sec
    ▼
DSP RealTimeProcessor
    │ filtre → époche → features → classification
    ▼
MLClassifier (LightGBM)
    │ concentration%, stress%, confiance
    ▼
AdaptiveEngine
    │ compare au seuil → succès ou échec
    ▼
WebSocketManager
    │ broadcast vers tous les clients connectés
    ▼
Frontend (React)
```

**TCPReceiver :** écoute sur le port TCP 9000. L'ESP32 envoie des données CSV en continu :
```
timestamp_ms,raw_uv,status
1716748800001,324.5,1
1716748800005,327.2,1
...
```
Le receiver parse chaque ligne et pousse l'échantillon dans la file DSP.

**ElectrodeMonitor :** surveille en parallèle la qualité des électrodes Fp2 (frontale), M1 et M2 (mastoides, référence + masse). Une mauvaise qualité déclenche une alerte dans l'interface.

---

### 3.8 Traitement du signal (DSP)

#### Pourquoi filtrer le signal EEG ?

Le signal brut de l'électrode contient :
- **Dérive DC** (mouvement du patient) → 0-1 Hz
- **Signal EEG utile** → 1-45 Hz
- **Bruit secteur électrique** → 50 Hz (Europe) et harmonique 100 Hz
- **Artefacts musculaires (EMG)** → > 45 Hz

Il faut donc garder uniquement la bande 1-45 Hz et supprimer le reste.

#### Chaîne de filtrage (Golden Filter v8.0)

**Fichier :** `app/Backend/app/services/eeg/dsp/filters.py`

```
Signal brut (250 Hz)
    │
    ▼ Soustraction médiane (suppression DC)
    │
    ▼ Filtre coupe-bande (Notch) 50 Hz, Q=30
    │
    ▼ Filtre coupe-bande (Notch) 100 Hz, Q=30
    │
    ▼ Filtre passe-bande Butterworth 1-45 Hz, ordre 4
    │
    ▼ Débruitage par ondelettes (DWT db4, niveau 4, seuillage doux)
    │
    Signal propre prêt pour l'analyse
```

**Deux modes de filtrage :**
- **Causal (lfilter)** pour l'affichage temps réel : pas de délai introduit mais légère distorsion de phase
- **Zéro-phase (filtfilt)** pour l'entraînement : double passe → aucune distorsion de phase, nécessite l'époque complète

#### Épochage

**Fichier :** `app/Backend/app/services/eeg/dsp/epochs.py`

Une **époque** = fenêtre de 4 secondes de signal (1000 échantillons à 250 Hz).

Avec 75% d'overlap : chaque seconde, une nouvelle époque est disponible (les 250 derniers échantillons sont nouveaux, les 750 précédents sont recyclés).

```
t=0s  : époque 1 = [0, 4]
t=1s  : époque 2 = [1, 5]   (75% partagé avec époque 1)
t=2s  : époque 3 = [2, 6]
...
```

**Rejet d'artefacts :** si l'amplitude crête-à-crête de l'époque dépasse 500 µV → époque rejetée (artefact de mouvement ou de clignement).

**Correction de baseline :** chaque époque est normalisée (z-score) par rapport à sa propre moyenne et écart-type. Cela rend le modèle insensible à l'amplitude absolue du signal.

#### Extraction de features (20+ features)

**Fichier :** `app/Backend/app/services/eeg/dsp/features.py`

Pour chaque époque de 4 secondes, on calcule :

**Features spectrales (Welch PSD) :**
La densité spectrale de puissance (PSD) mesure combien d'énergie le signal a dans chaque bande de fréquence.

| Feature | Bande Hz | Signification cognitive |
|---|---|---|
| Pδ (delta) | 1-4 Hz | Sommeil profond |
| Pθ (theta) | 4-8 Hz | Mémoire de travail, fatigue |
| Pα (alpha) | 8-13 Hz | Relaxation, calme attentif |
| Pβ (beta) | 13-30 Hz | Concentration active, stress |
| Pγ (gamma-low) | 30-45 Hz | Traitement cognitif complexe |

**Ratios cognitifs :**

| Ratio | Formule | Signification |
|---|---|---|
| TBR (Theta/Beta Ratio) | Pθ / Pβ | TBR élevé = déficit attentionnel (TDAH) |
| ABR (Alpha/Beta Ratio) | Pα / Pβ | ABR élevé = relaxation |
| EI (Engagement Index) | Pβ / (Pα + Pθ) | EI élevé = forte concentration |
| TAR (Theta/Alpha Ratio) | Pθ / Pα | TAR élevé = somnolence |

**Paramètres de Hjorth :**

| Paramètre | Description |
|---|---|
| Activité | Variance du signal (puissance totale) |
| Mobilité | Rapport de la dérivée première (fréquence dominante) |
| Complexité | Rapport Mobilité(dérivée) / Mobilité(signal) (irrégularité) |

**Features d'ondelettes :** énergie dans les sous-bandes de la DWT (db4, niveau 4).

**Features temporelles :** RMS, amplitude moyenne, énergie relative.

Au total : **20+ features par époche** → vecteur d'entrée du classificateur.

---

### 3.9 Fine-tuning adaptatif

**Problème :** Le modèle global est entraîné sur des données de plusieurs sujets. Les signaux EEG varient significativement entre individus (morphologie crânienne, placement des électrodes, résistance de la peau).

**Solution :** Personnaliser le modèle pour chaque patient en utilisant ses propres données collectées pendant les sessions.

#### Conditions de déclenchement

**Fichier :** `app/Backend/app/services/eeg/finetune/conditions.py`

Le fine-tuning se déclenche :
1. **Chaque nuit à 2h UTC** (APScheduler) si le patient a ≥ 50 nouvelles époques haute confiance
2. **Après une session** si assez d'époques haute confiance ont été collectées
3. **Manuellement** par le thérapeute depuis son interface

#### Processus de fine-tuning

**Fichier :** `app/Backend/app/services/eeg/finetune/runner.py`

```
1. Sélectionner les époques haute confiance (conf ≥ 0.85) du patient dans la DB
2. Charger le modèle global (LightGBM) comme point de départ
3. Fine-tuner avec un learning rate réduit (évite l'oubli catastrophique)
4. Évaluer sur un sous-ensemble de validation
5. Si la performance s'améliore → sauvegarder models/personal/patient_{id}_v{n}.joblib
6. Mettre à jour eeg_profiles.finetuned_version dans la DB
7. Enregistrer le job dans finetuning_jobs avec statut "completed"
```

**Pseudo-labels :** On utilise les prédictions du modèle global comme labels d'entraînement pour le modèle personnalisé (apprentissage auto-supervisé).

---

### 3.10 Moteur d'adaptation des seuils

**Fichier :** `app/Backend/app/services/eeg/adaptative_engine.py`

**Inspiration :** Mou et al. (2024) — Dynamic Difficulty Adjustment for neurofeedback

L'objectif est de maintenir le patient dans la **zone de flow** : ni trop facile (ennui) ni trop difficile (frustration).

#### 3 niveaux d'adaptation

**Niveau 1 — Temps réel (500 ms) :**
Lissage exponentiel EWMA (α = 0.3) des features bruts pour éviter les faux-positifs :
```
EWMA_t = α × valeur_t + (1 - α) × EWMA_{t-1}
```

**Niveau 2 — Intra-session (blocs de 3 minutes) :**
À la fin de chaque bloc de 3 minutes, on calcule le taux de succès (% d'époques au-dessus du seuil) :

```
Si succès > 60%  → seuil + 0.5 (plus difficile)
Si succès 40-60% → seuil inchangé (zone de flow optimale)
Si succès < 40%  → seuil - 0.5 (plus facile)
```

**Niveau 3 — Inter-session :**
Recalibration nocturne via le fine-tuning personnalisé. Le nouveau modèle reflète les progrès du patient sur plusieurs sessions.

#### Paliers de difficulté

| Palier | Nom | Plage de seuil |
|---|---|---|
| P1 | Initiation | 0.20 – 0.45 |
| P2 | Apprentissage | 0.40 – 0.60 |
| P3 | Maîtrise | 0.55 – 0.75 |
| P4 | Autonomie | 0.70 – 0.90 |

Le thérapeute peut ajuster le palier manuellement depuis son interface. L'IA ajuste le seuil dans les bornes du palier automatiquement.

---

### 3.11 Assistant RAG (Retrieval-Augmented Generation)

**Fichier :** `app/Backend/app/services/rag_service.py`

**Qu'est-ce que le RAG ?**
Au lieu d'utiliser un LLM (grand modèle de langage) seul — qui peut halluciner — le RAG combine :
1. Une **base de connaissances** spécialisée (documents EEG/neurofeedback)
2. Un **moteur de recherche sémantique** pour trouver les documents pertinents
3. Un **LLM local** (Mistral via Ollama) qui génère la réponse en s'appuyant sur les documents retrouvés

#### Flux d'une question

```
Question de l'utilisateur : "C'est quoi le ratio TBR ?"
    │
    ▼ Embedding de la question (vecteur numérique)
    │
    ▼ Recherche sémantique dans la base SQLite (top-k documents)
       → Retrouve le document sur les ratios cognitifs
    │
    ▼ Injection du contexte dans le prompt LLM
       Prompt = "Contexte: [documents retrouvés]\n\nQuestion: [question]\nRéponse:"
    │
    ▼ Génération par Mistral (local, données restent sur le serveur)
    │
    ▼ Réponse renvoyée à l'utilisateur
```

**Contexte EEG du patient :** quand un patient connecté pose une question, le service injecte automatiquement son profil EEG (IAPF, TBR baseline, palier actuel) dans le contexte → réponses personnalisées.

**Feedback utilisateur :** chaque réponse peut être notée 👍/👎. Ces votes sont stockés pour améliorer la qualité du RAG.

---

## 4. Frontend — React 18

### 4.1 Structure et routage

**Fichier :** `app/Frontend/src/App.jsx`

```jsx
// Routage principal avec protection par rôle
<Router>
  <Routes>
    {/* Public */}
    <Route path="/" element={<Landing />} />
    <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
    <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />

    {/* Patient */}
    <Route path="/dashboard" element={<PrivateRoute role="patient"><DashboardPage /></PrivateRoute>} />
    <Route path="/feedback" element={<PrivateRoute role="patient"><FeedbackPage /></PrivateRoute>} />
    <Route path="/history" element={<PrivateRoute><History /></PrivateRoute>} />
    <Route path="/eeg/select" element={<PrivateRoute><EEGSelector /></PrivateRoute>} />
    <Route path="/eeg/live" element={<PrivateRoute><EEGLive /></PrivateRoute>} />

    {/* Admin */}
    <Route path="/admin" element={<PrivateRoute role="admin"><AdminDashboard /></PrivateRoute>} />
    <Route path="/admin/panel" element={<PrivateRoute role="admin"><AdminPanel /></PrivateRoute>} />

    {/* Thérapeute */}
    <Route path="/therapist" element={<PrivateRoute role="therapist"><TherapistDashboard /></PrivateRoute>} />
    <Route path="/therapist/patients/:id" element={<PrivateRoute role="therapist"><TherapistPatientDetail /></PrivateRoute>} />

    {/* Commun */}
    <Route path="/assistant" element={<PrivateRoute><Assistant /></PrivateRoute>} />
    <Route path="/profile" element={<PrivateRoute><Profile /></PrivateRoute>} />
  </Routes>
</Router>
```

`DashboardRoute` redirige automatiquement vers la bonne page selon le rôle : admin → AdminDashboard, thérapeute → TherapistDashboard, patient → DashboardPage.

---

### 4.2 Pages principales

#### Page d'accueil (Landing.jsx)

Page publique présentant NeuroCap avec :
- Explication du neurofeedback
- Fonctionnalités clés
- Appel à l'action (inscription)

#### Connexion (Login.jsx)

- Champ email + mot de passe
- Messages d'erreur distincts : "Email inconnu" vs "Mot de passe incorrect"
- Bouton de changement de langue (FR/EN/AR) et de thème (clair/sombre)
- Redirection automatique selon le rôle après connexion

#### Inscription (Register.jsx)

Processus en 2 étapes :
1. **Entrée de l'email** → envoi du code de vérification
2. **Code + informations** + checklist de force du mot de passe (8+ caractères, majuscule, chiffre, caractère spécial)

#### Dashboard Patient (DashboardPage.jsx)

Vue centrale du patient avec :
- **Mode simulation** : sans ESP32, pour démo/test
- Indicateurs temps réel (concentration%, stress%)
- Brain3D : cerveau 3D avec heatmap d'activation
- BandBars : barres des 5 bandes de fréquence
- RecommendationEngine : recommandations IA pour la prochaine session
- Accès rapide à l'historique et au feedback

#### Page Neurofeedback (FeedbackPage.jsx)

La page la plus complexe. Session en **3 phases** :

**Phase 1 — Setup (Configuration)**
- Sélection de l'objectif (concentration ou relaxation)
- Sélection du mode de feedback (visuel / audio / jeu)
- Thompson Sampling suggère la modalité la plus efficace pour ce patient
- Explication au patient de ce qui va se passer

**Phase 2 — Session Live**
- Connexion WebSocket active
- Affichage du feedback sélectionné (image/audio/vidéo/jeu)
- Indicateur d'état du cerveau en temps réel
- Jauge de confiance de la classification
- Minuterie de session
- Seuil de succès visible

**Phase 3 — Rapport post-session**
- Score global
- Graphe de concentration/stress sur la durée de la session
- TBR moyen, durée totale, epochs réussies/rejetées
- Recommandation pour la prochaine session
- Bouton de sauvegarde du rapport

#### Dashboard Admin (AdminDashboard.jsx)

- **6 KPI cards** : total users, users actifs, thérapeutes, sessions totales, score moyen, nouveaux users ce mois
- Table des utilisateurs avec pagination et recherche
- Journal d'audit (dernières actions)
- Bouton d'envoi de rappels email aux inactifs

#### Dashboard Thérapeute (TherapistDashboard.jsx)

- Liste de ses patients assignés avec leurs dernières stats
- Accès au détail de chaque patient : sessions, notes cliniques, profil EEG, recommandations
- Formulaire d'ajout de note clinique
- Ajustement manuel du palier de difficulté

#### Sélecteur EEG (EEGSelector.jsx)

Page préparatoire avant de lancer une session avec le matériel réel :
- Guide intégré des électrodes avec schéma du casque
- Schéma de câblage AD8232 + ESP32
- Checklist en 4 étapes (connexion, placement, gel conducteur, signal OK)
- Bouton de test de la qualité du signal avant de démarrer

---

### 4.3 Composants clés

#### Brain3D.jsx — Cerveau 3D (Three.js)

```
Technologie : Three.js + React Three Fiber
Rendu :
- Si brain_mesh.json disponible → maillage anatomique réaliste
- Sinon → cerveau procédural (icosphère déformée) en fallback
- Matériau : MeshPhysicalMaterial avec clearcoat (effet brillant réaliste)
Heatmap :
- Chaque vertex du maillage reçoit une couleur
- Concentration → teinte bleue
- Stress → teinte rouge
- Région préfrontale (Fz) mise en évidence
Animation :
- Rotation automatique lente
- Intensité de la heatmap = valeur temps réel de la classification
```

#### EEGVisualization.jsx — Carte topographique

Affiche les 10-10 positions d'électrodes avec interpolation IDW (Inverse Distance Weighting) pour créer une carte topographique 2D de l'activité cérébrale.

#### FeedbackSelector.jsx — Sélection Thompson Sampling

**Thompson Sampling** est un algorithme de bandit manchot (exploration/exploitation) :

```
Pour chaque modalité de feedback (image, audio, vidéo, jeu, son) :
- α = nombre de "j'aime" historiques + 1
- β = nombre de "je n'aime pas" + 1
- Échantillonner une valeur de la loi Beta(α, β)
→ Choisir la modalité avec la valeur Beta la plus élevée
```

Résultat : les modalités appréciées par le patient sont sélectionnées plus souvent, mais les nouvelles modalités sont toujours explorées (pas de blocage sur une seule).

#### Jeux de neurofeedback (5 modalités)

| Jeu | Mécanisme de feedback |
|---|---|
| **MemoryGame** | Cartes retournées plus vite quand concentration élevée |
| **PuzzleGame** | Pièces plus visibles / accessibles en mode concentré |
| **SudokuGame** | Aide contextuelle activée selon l'état de concentration |
| **CalculGame** | Difficulté arithmétique ajustée en temps réel |
| **EnigmeGame** | Indices supplémentaires disponibles si concentration suffisante |

---

### 4.4 Gestion d'état (Zustand)

**Fichier :** `app/Frontend/src/stores/index.js`

Zustand est une bibliothèque de gestion d'état légère pour React (alternative à Redux).

#### AuthStore

```javascript
{
  user: { id, email, role, firstName, lastName },
  token: "eyJ...",           // access token
  
  login(email, pass) → fetche /api/auth/login, stocke token + user
  register(...) → fetche /api/auth/register
  logout() → vide le store + localStorage
  fetchUser() → fetche /api/auth/me pour récupérer le profil
}
```

#### SessionStore (WebSocket temps réel)

```javascript
{
  ws: WebSocket,
  connected: boolean,
  sessionId: string,
  
  // Données EEG temps réel
  frame: { raw_uv, timestamp },       // dernier échantillon
  concentration: 67.3,                // % concentration actuel
  stress: 22.1,                       // % stress actuel
  signalQuality: "good",              // qualité signal
  threshold: 0.55,                    // seuil de succès actuel
  
  // Adaptation
  ewma: { concentration: 65.2 },      // valeur lissée EWMA
  blockNumber: 3,                     // numéro du bloc 3-min actuel
  blockTimeSec: 127,                  // secondes dans le bloc actuel
  successRate: 58.3,                  // % succès du bloc actuel
  
  // Features spectrales pour les composants
  features: { tbr, alpha, beta, theta, gamma },
  
  connect(sessionId, token) → ouvre WebSocket + s'abonne
  disconnect() → ferme WebSocket proprement
  sendAction(cmd) → envoie commande au backend
}
```

---

### 4.5 Communication avec le backend

**Fichier :** `app/Frontend/src/utils/api.js`

Instance Axios avec :
1. **Injection automatique du token** dans le header `Authorization: Bearer <token>`
2. **Auto-refresh** : si une requête reçoit 401 (token expiré), tente automatiquement un refresh, puis relance la requête originale
3. **Intercepteur d'erreurs** : gère les erreurs réseau globalement

**Hook WebSocket :**
`hooks/useEEGWebSocket.js` :
- Connexion à `/ws/eeg` avec le token en paramètre de query
- Reconnexion automatique après 3 secondes si déconnecté
- Parser les types de messages : eeg, epoch, init, esp32_status, electrode
- Expose : `connected`, `eegFrame`, `epochFrame`, `send(cmd)`, `reconnect()`

---

### 4.6 Internationalisation et thèmes

**3 langues supportées :** Français, Anglais, Arabe (avec support RTL)

```javascript
// Utilisation dans un composant
const { t } = useTranslation()
<h1>{t('dashboard.title')}</h1>  // → "Tableau de bord" en FR
```

**Thèmes :** Clair / Sombre / Auto (suit le système)

Implémenté via des variables CSS custom :
```css
:root[data-theme="dark"] {
  --nc-surface: #1a1a2e;
  --nc-accent: #6c63ff;
  --nc-text: #e2e8f0;
}
```

---

## 5. Intelligence Artificielle et Machine Learning

### 5.1 Pipeline de données

**Fichier :** `src/data/pipeline_fp2.py`

Toute la pipeline de données se passe dans ce fichier pour l'électrode **Fp2** (frontale droite, choisie car accessible et proche des zones préfrontales liées à la concentration).

```
Données brutes ESP32 (CSV) ou datasets publics
    │
    ▼ 1. Chargement et parsing
    │
    ▼ 2. Soustraction médiane (suppression DC)
    │
    ▼ 3. Filtre Notch 50 Hz (Q=30)
    │
    ▼ 4. Filtre passe-bande Butterworth 1-45 Hz (ordre 4)
    │
    ▼ 5. Débruitage DWT (db4, niveau 4, seuillage doux)
    │
    ▼ 6. Découpage en époques (4s, 75% overlap)
    │
    ▼ 7. Rejet d'artefacts (PTP > 500 µV)
    │
    ▼ 8. Normalisation Z-score par époque
    │
    Époques normalisées (.npy) prêtes pour l'entraînement
```

#### Augmentation des données

**Fichier :** `src/data/augmentation_eeg.py`

Le dataset EEG est limité (peu de sujets). Pour enrichir l'entraînement, 4 techniques d'augmentation sont appliquées :

| Technique | Description |
|---|---|
| **Jittering** | Ajoute du bruit gaussien léger (σ = 0.05 × écart-type signal) |
| **Scaling** | Multiplie l'amplitude par un facteur aléatoire (0.8 – 1.2) |
| **Permutation** | Découpe et réarrange aléatoirement des segments |
| **Mixup** | Combine 2 époques de même classe avec un ratio aléatoire |

5 niveaux d'augmentation (A, B, C, D, FULL) ont été testés pour trouver le meilleur compromis.

---

### 5.2 Extraction de features

**Fichier :** `src/data/features_extraction.py`

Deux jeux de features ont été construits :

**Features Baseline (15 features) :**
- 5 puissances spectrales (delta, theta, alpha, beta, gamma)
- 4 ratios cognitifs (TBR, ABR, EI, TAR)
- 3 paramètres de Hjorth
- 3 features temporelles (RMS, MeanAmp, RelEnergy)

**Features Engineered (63 features) :**
- Tout ce qui précède +
- Coefficients DWT niveau 4 (statistiques)
- Features de connectivité (cohérence entre sous-bandes)
- Features statistiques d'ordre supérieur (kurtosis, skewness)

---

### 5.3 Modèles ML classiques (baseline)

**Fichier :** `src/models/baselines/baseline_ML.py`

4 algorithmes testés avec validation LOSO (Leave-One-Subject-Out) :

```
LOSO = pour chaque sujet S :
  - entraîner sur tous les sujets SAUF S
  - tester sur S
  → donne une estimation réaliste de la généralisation inter-sujets
```

| Modèle | Paramètres | Résultat (F1-macro) |
|---|---|---|
| SVM (RBF) | C=1.0, gamma='scale' | ~0.78 |
| Random Forest | 100 arbres, depth=10 | ~0.81 |
| XGBoost | 100 estimateurs, depth=6 | ~0.83 |
| **LightGBM** | **100 estimateurs, depth=8** | **~0.85** |

**LightGBM** a été sélectionné pour la production car :
- Meilleure performance
- Rapide à l'inférence (< 1 ms par époque)
- Léger (peut être fine-tuné sur CPU)

---

### 5.4 Architectures Deep Learning (19 modèles benchmarkés)

**Répertoire :** `src/models/deep_learning/architectures/`

**Pourquoi le deep learning ?**
Les features manuelles capturent bien les informations spectrales mais peuvent manquer des patterns temporels complexes. Les réseaux de neurones peuvent apprendre ces représentations directement depuis le signal brut.

**Entrée des modèles DL :** époque brute de 1000 points (4 secondes à 250 Hz)
**Sortie :** vecteur [concentration_score, stress_score]

#### Les 19 architectures

**Convolutionels (CNN) :**
- **CNN1D** : convolutions 1D glissantes sur la séquence temporelle
- **CNN2D** : signal converti en spectrogramme, convolutions 2D
- **CNN3D** : spatiotemporel (moins pertinent avec 1 électrode)

**Récurrents (LSTM/GRU) :**
- **LSTM1L / LSTM2L** : Long Short-Term Memory, 1 ou 2 couches
- **GRU1L / GRU2L** : Gated Recurrent Unit (plus léger que LSTM)
- **Versions bidirectionnelles** : lisent la séquence dans les deux sens
- **Versions avec attention** : mécanisme d'attention de Bahdanau

**Hybrides (meilleure performance) :**
- **CNN_LSTM** : CNN extrait les features locales, LSTM capture les dépendances longues
- **CNN_GRU** : même principe avec GRU

**Architecture spécialisée EEG :**
- **EEGNet** (Lawhern et al., 2018) : conçu spécifiquement pour l'EEG
  - Convolution temporelle (1×64) → capture les patterns oscillatoires
  - Convolution depthwise (F1*D, 1) → mixage spatial (inter-électrodes)
  - Convolution séparable (1×16) → réduction de paramètres
  - Très compact : < 1000 paramètres

**TCN (Temporal Convolutional Network) :**
Convolutions dilatées causales → champ récepteur exponentiel sans récurrence

#### Résultats du benchmark

**Meilleur modèle : CNN_LSTM + Attention → 89.4% accuracy, F1 = 0.89**

Choisi pour la production (en complément de LightGBM) car :
- Meilleure précision sur les cas limites
- Capture mieux les transitions entre états

---

### 5.5 Domain Adversarial Neural Networks (DANN)

**Répertoire :** `src/models/deep_learning/architectures_DANN/`

**Problème :** Les signaux EEG varient considérablement entre sujets (*domain shift*). Un modèle entraîné sur le sujet A peut être mauvais sur le sujet B.

**Solution DANN :** Entraîner un modèle qui extrait des features **invariantes au sujet** tout en étant discriminantes pour la tâche.

```
                 ┌─────────────────────┐
                 │  Extracteur de      │
   Époque EEG ──▶│  features partagé   │
                 │  (Feature Extractor)│
                 └─────────┬───────────┘
                           │
               ┌───────────┼───────────┐
               │                       │
               ▼                       ▼
    ┌──────────────────┐   ┌─────────────────────┐
    │  Classificateur  │   │  Discriminateur de  │
    │  de tâche        │   │  domaine (sujet)    │
    │  (concentration/ │   │  (qui est le sujet?)│
    │   stress)        │   │                     │
    └──────────────────┘   └─────────────────────┘
           ↑ minimise              ↑ maximise
           loss tâche              loss domaine
                    ↘            ↙
                  Gradient Reversal Layer (GRL)
```

Le **GRL** (Gradient Reversal Layer) inverse le gradient lors de la backpropagation pour le discriminateur → l'extracteur apprend à *tromper* le discriminateur de domaine tout en restant bon pour la tâche.

18 variantes DANN ont été testées (une par architecture).

---

### 5.6 Transfer Learning (3 stratégies)

**Répertoire :** `src/models/transfer_learning/`

**Contexte :** Le modèle global a été pré-entraîné sur un large dataset. Pour un nouveau patient, on dispose de peu de données.

#### Stratégie 1 — Extraction de features

```
Modèle pré-entraîné :
[Conv → LSTM → FC] → FREEZE toutes les couches sauf FC
                    ↓
         Entraîner uniquement le FC sur les données patient
```

- Rapide (peu de paramètres à entraîner)
- Préserve les features apprises du grand dataset
- Mais limité si le patient est très différent

#### Stratégie 2 — Remplacement de couche

```
Remplacer FC(128→2) par un nouveau FC(128→2) initialisé aléatoirement
Entraîner avec lr=1e-4 (faible)
```

- Plus de flexibilité que l'extraction pure
- Le nouveau FC peut apprendre les seuils de décision spécifiques au patient

#### Stratégie 3 — Fine-tuning complet

```
Dégeler toutes les couches
Entraîner avec lr=1e-5 (très faible)
+ Early stopping pour éviter l'oubli catastrophique
```

- Meilleure adaptation possible
- Risque d'oubli des connaissances générales si lr trop élevé
- Nécessite plus de données patient

**Comparaison** : `compare_tl.py` compare les 3 stratégies sur les métriques accuracy, F1, et temps d'entraînement.

---

### 5.7 Moteur d'inférence unifié

**Fichier :** `src/inference_engine.py`

Interface unique pour les 3 types de modèles :

```python
engine = InferenceEngine(model_type=ModelType.BEST_AUTO)

# Inférence
result = engine.predict(epoch_1000pts)
# → {
#     "concentration": 72.3,   # %
#     "stress": 18.5,           # %
#     "state": "concentration", # classe prédite
#     "confidence": 0.85,       # confiance [0-1]
#     "uncertain": False        # True si conf < 0.60
#   }
```

**Logique BEST_AUTO :**
1. Essaie le modèle personnalisé du patient (si disponible)
2. Sinon, utilise le CNN_LSTM global
3. Si confiance < 0.60 → marque comme "uncertain" (n'affecte pas le score)

---

## 6. Base de données — Supabase PostgreSQL

### Tables principales

#### `users` — Utilisateurs

```sql
id           UUID        PK
email        TEXT        UNIQUE, NOT NULL
password_hash TEXT       NOT NULL           -- bcrypt hash
first_name   TEXT
last_name    TEXT
username     TEXT
role         TEXT        DEFAULT 'patient'   -- patient | therapist | admin
therapist_id UUID        FK → users.id       -- pour les patients
is_active    BOOLEAN     DEFAULT true
created_at   TIMESTAMPTZ DEFAULT NOW()
```

#### `sessions` — Sessions de neurofeedback

```sql
id                UUID      PK
user_id           UUID      FK → users.id  CASCADE DELETE
status            TEXT      pending | active | completed
objective         TEXT      concentration | relaxation
feedback_mode     TEXT      visual | audio | game
score             FLOAT                   -- score global 0-100
duration_seconds  FLOAT
avg_tbr           FLOAT                   -- TBR moyen de la session
avg_concentration FLOAT
avg_stress        FLOAT
notes             TEXT
created_at        TIMESTAMPTZ
```

#### `eeg_reports` — Rapports d'analyse EEG

```sql
id                UUID    PK
patient_id        UUID    FK → users.id
therapist_id      UUID    FK → users.id    -- NULL si auto-généré
type              TEXT    live | file
filename          TEXT                     -- si type='file'
duration_s        FLOAT
n_epochs_accepted INTEGER
n_epochs_rejected INTEGER
concentration_pct FLOAT
stress_pct        FLOAT
uncertain_pct     FLOAT
mean_confidence   FLOAT
states_json       JSONB                    -- timeline des états seconde par seconde
notes             TEXT
created_at        TIMESTAMPTZ
```

#### `eeg_profiles` — Profil EEG par patient

```sql
user_id           UUID    PK FK → users.id
profile_type      TEXT                     -- A, B ou C (selon IAPF)
iapf              FLOAT                    -- Individual Alpha Peak Frequency
baseline_tbr      FLOAT                   -- TBR de repos calibré
baseline_alpha    FLOAT
baseline_beta     FLOAT
baseline_theta    FLOAT
reactivity_score  FLOAT                   -- réactivité aux stimuli
palier            TEXT    DEFAULT 'P1'    -- P1 | P2 | P3 | P4
current_threshold FLOAT                   -- seuil de succès actuel
finetuned_version INTEGER DEFAULT 0       -- version du modèle personnalisé
updated_at        TIMESTAMPTZ
```

#### `training_epochs` — Époques pour le fine-tuning

```sql
id                UUID    PK
patient_id        UUID    FK → users.id
epoch_data        BYTEA                   -- signal brut sérialisé
features          JSONB                   -- 20+ features calculées
predicted_label   INTEGER                 -- 0=stress, 1=concentration
is_high_confidence BOOLEAN               -- conf ≥ 0.85
used_in_finetuning BOOLEAN DEFAULT false  -- marquée après utilisation
created_at        TIMESTAMPTZ
```

#### `finetuning_jobs` — Journal des fine-tunings

```sql
id            UUID    PK
patient_id    UUID    FK → users.id
trigger_type  TEXT    nightly | session_complete | manual
version       INTEGER                     -- version résultante
status        TEXT    pending | running | completed | failed
error_message TEXT
started_at    TIMESTAMPTZ
completed_at  TIMESTAMPTZ
```

### Choix Supabase vs SQLAlchemy

| Critère | Supabase | SQLAlchemy |
|---|---|---|
| Déploiement | Zéro configuration serveur | Gestion PostgreSQL manuelle |
| Auth | Intégrée (utilisée en option) | À construire |
| Temps réel | Realtime natif | Besoin de pub/sub séparé |
| Coût | Gratuit jusqu'à 500 MB | Payant si hébergé |
| ORM | Non (SDK REST direct) | Oui (Orm complet) |

---

## 7. Sécurité

### Résumé des mesures de sécurité

| Mesure | Implémentation | Pourquoi |
|---|---|---|
| Hachage bcrypt | `passlib[bcrypt]` | Mots de passe non récupérables |
| JWT HS256 | `python-jose` | Tokens signés, expirables |
| Email vérification | Code 8 chiffres, TTL 10 min | Empêche les faux comptes |
| Brute-force | 5 échecs → ban 15 min par IP | Protège contre les attaques de dictionnaire |
| Rate limiting | 100 req/60s par IP | Protège contre le scraping/DoS |
| CORS strict | Whitelist de domaines | Empêche les requêtes cross-origin non autorisées |
| RBAC | `get_admin_user()`, `get_therapist_user()` | Séparation des privilèges |
| Soft delete | `is_active = false` | Les données sont conservées pour l'audit |
| Audit logs | Table `audit_logs` | Traçabilité des actions sensibles |
| Service role key | Côté serveur uniquement | La clé DB n'est jamais dans le frontend |
| Validation des données | Pydantic v2 | Reject les inputs malformés |
| Mot de passe fort | 8+ chars, upper/lower/digit/special | Réduit les mots de passe faibles |

### Flux d'authentification complet

```
1. Inscription :
   email → POST /send-code → Brevo envoie code 8 chiffres (TTL 10 min)
   POST /register (email + code + password + nom) → compte créé

2. Connexion :
   POST /login → vérifie email + bcrypt.verify(password, hash)
   → retourne { access_token (30min), refresh_token (7j) }

3. Requêtes authentifiées :
   Headers: { Authorization: "Bearer <access_token>" }
   Backend: JWT.decode() → user_id + role → autorisation

4. Renouvellement :
   POST /refresh (refresh_token) → nouveau access_token (sans re-login)

5. Déconnexion :
   POST /logout-all → invalide tous les refresh tokens du user
```

---

## 8. Déploiement

### Docker Compose

**Fichier :** `docker/docker-compose.yml`

```yaml
services:
  postgres:      # Base de données locale (optionnel si Supabase cloud)
    image: postgres:15-alpine
    
  redis:         # Cache pour rate limiting et sessions
    image: redis:7-alpine
    
  backend:       # FastAPI
    build: ./Backend
    ports: ["8000:8000"]
    
  frontend:      # React (Vite build statique)
    build: ./Frontend
    ports: ["5173:5173"]
```

### Commandes de démarrage

```bash
# Premier démarrage
docker compose up --build

# Accès :
# Frontend    : http://localhost:5173
# Backend API : http://localhost:8000
# Docs API    : http://localhost:8000/docs  (Swagger UI auto-généré)
```

### Variables d'environnement (.env)

```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...   ← JAMAIS exposée au frontend
SECRET_KEY=...                   ← Clé de signature JWT
SMTP_HOST=smtp-relay.brevo.com
SMTP_USER=...
SMTP_PASSWORD=...
LLM_MODEL=mistral
OLLAMA_URL=http://localhost:11434
```

**Mode développement sans SMTP :** si `SMTP_USER` est vide, le code de vérification s'affiche directement dans la réponse API (bannière jaune en dev).

---

## 9. Flux de données de bout en bout

### Scénario : Patient fait une session de neurofeedback

```
1. LOGIN
   Patient → Login.jsx → POST /api/auth/login
   Backend → vérifie bcrypt → retourne JWT
   Frontend → stocke JWT dans Zustand

2. CONNEXION HARDWARE
   Patient → EEGSelector.jsx → checklist électrodes
   → GET /api/eeg/status → vérifie ESP32 connecté
   ESP32 → TCP :9000 → TCPReceiver backend

3. CALIBRATION BASELINE (2 minutes)
   Patient se relaxe → signal collecté → calcul Z-scores individuels
   → WebSocket: type="init" → baseline OK
   → POST /api/eeg/baseline/finalise → profil EEG mis à jour en DB

4. DÉMARRAGE SESSION
   → POST /api/sessions/ → session créée (status="active")
   → WebSocket connecté
   → FeedbackPage.jsx phase 2 active

5. SESSION LIVE (20-30 min)
   ESP32 → TCP :9000 → TCPReceiver
     → 250 échantillons/s → DSP RealTimeProcessor
     → filtre → époche 4s (75% overlap)
     → 20+ features extraites
     → LightGBM.predict() → {concentration: 72%, stress: 18%, conf: 0.85}
     → AdaptiveEngine compare au seuil actuel
     → WebSocket push: type="epoch" → Frontend
   
   Frontend:
     → SessionStore.concentration = 72%
     → Brain3D heatmap mise à jour
     → BandBars mis à jour
     → Si époque réussie → feedback positif dans le jeu/image/audio
   
   AdaptiveEngine (tous les 3 min):
     → calcule taux de succès du bloc
     → ajuste seuil ± 0.5

6. FIN DE SESSION
   → STOP_REC via WebSocket
   → POST /api/sessions/{id} → status="completed", score calculé
   → POST /api/eeg/report → rapport sauvegardé + thérapeute notifié
   → FeedbackPage.jsx phase 3 : rapport affiché

7. FINE-TUNING NOCTURNE
   APScheduler à 2h UTC:
     → Récupère les époques haute confiance du patient (conf ≥ 0.85)
     → Fine-tune LightGBM sur ces données
     → Sauvegarde models/personal/patient_{id}_v{n+1}.joblib
     → Met à jour finetuning_jobs en DB
```

---

## 10. Questions probables du jury — Réponses préparées

### Questions sur les choix technologiques

**Q : Pourquoi FastAPI et pas Flask ou Django ?**
> FastAPI est asynchrone natif (async/await), idéal pour le WebSocket et les appels IO intensifs. Il génère automatiquement la documentation Swagger. Flask est synchrone. Django est trop lourd pour une API pure.

**Q : Pourquoi Supabase et pas une base PostgreSQL classique ?**
> Supabase offre PostgreSQL managé avec zéro configuration serveur, une API REST générée automatiquement, et un SDK Python asynchrone. Pour un projet académique/MVP, cela réduit considérablement la complexité opérationnelle.

**Q : Pourquoi React et pas Vue ou Angular ?**
> React est le framework le plus utilisé avec le plus grand écosystème. Three.js s'intègre mieux avec React Three Fiber. Zustand est plus simple qu'un Redux complet.

**Q : Pourquoi LightGBM et pas un réseau de neurones pour la production ?**
> LightGBM est 10x plus rapide à l'inférence (< 1 ms vs 5-10 ms pour un DL), ce qui est critique pour le temps réel. Il est plus facile à fine-tuner sur CPU. Sa performance (F1=0.85) est très proche du meilleur DL (F1=0.89) pour une complexité bien moindre.

**Q : Pourquoi une seule électrode (Fp2) et pas plusieurs ?**
> L'objectif était de rendre le système accessible et low-cost. L'AD8232 ne gère qu'une électrode active. Fp2 (préfrontal) est la meilleure position pour la concentration/stress avec une seule électrode. Des études montrent que le TBR frontal est le marqueur le plus fiable.

### Questions sur le signal EEG et le DSP

**Q : Pourquoi un filtre Butterworth Ordre 4 et pas ordre 8 ?**
> L'ordre 4 offre un bon compromis : atténuation suffisante (−24 dB/octave) sans introduire de distorsion de phase excessive. Un ordre plus élevé aurait des effets de bord plus prononcés sur les bords d'époque.

**Q : Pourquoi 4 secondes par époque ?**
> 4 secondes donnent assez de résolution fréquentielle pour distinguer theta (4-8 Hz) et alpha (8-13 Hz) tout en restant assez court pour le temps réel. Avec 75% d'overlap, on obtient une nouvelle classification chaque seconde.

**Q : Qu'est-ce que le TBR et pourquoi est-il important ?**
> TBR = Theta/Beta Ratio. C'est le biomarqueur EEG le plus étudié pour l'attention. Un TBR élevé (theta dominant) indique un déficit attentionnel (souvent corrélé au TDAH). Une concentration active augmente beta et réduit theta → TBR diminue. C'est notre principale feature de classification.

**Q : Comment gérez-vous les artefacts (clignement des yeux, mouvement) ?**
> 3 mécanismes : (1) Seuil d'amplitude : époque rejetée si PTP > 500 µV, (2) Détection EMG : si puissance 35-45 Hz trop élevée, (3) Electrode monitor : alerte si impédance mauvaise. Les époques rejetées ne sont pas classifiées → `uncertain_pct` dans le rapport.

### Questions sur l'IA et le Machine Learning

**Q : Comment avez-vous évalué les modèles ?**
> Validation LOSO (Leave-One-Subject-Out) : on entraîne sur N-1 sujets et on teste sur le sujet restant. C'est l'évaluation la plus rigoureuse pour les données EEG car elle mesure la généralisation inter-sujets réelle.

**Q : Qu'est-ce que le domain shift et comment DANN le résout-il ?**
> Le domain shift désigne la différence de distribution entre les signaux EEG de différents sujets (anatomie crânienne différente, placement légèrement différent des électrodes). DANN entraîne un extracteur de features adversarial qui apprend à être invariant au sujet. La Gradient Reversal Layer force l'extracteur à *ne pas* encoder l'identité du sujet tout en restant discriminant pour la tâche.

**Q : Pourquoi ne pas utiliser un seul grand modèle (type Transformer) ?**
> Les Transformers nécessitent beaucoup de données (millions d'exemples). Les datasets EEG publics ont quelques centaines de sujets. LightGBM + features manuelles + fine-tuning par patient est une approche plus adaptée à la taille des données disponibles et aux contraintes temps réel.

**Q : Comment fonctionne le Thompson Sampling pour la sélection de modalité ?**
> Pour chaque modalité (image, audio, etc.) on maintient deux compteurs α (succès) et β (échecs) basés sur les retours utilisateur. On échantillonne une valeur de Beta(α,β) pour chaque modalité et on choisit la plus haute. Cela garantit exploration (nouvelles modalités testées) + exploitation (modalités efficaces sélectionnées plus souvent). C'est la solution optimale au problème du bandit manchot.

**Q : C'est quoi l'IAPF et pourquoi est-ce important ?**
> IAPF = Individual Alpha Peak Frequency. Le pic alpha varie entre 8 et 13 Hz selon les individus (génétique, âge, état cognitif). Utiliser l'IAPF individuel (calculé pendant la baseline) améliore la précision de la segmentation des bandes alpha → meilleure classification. C'est pourquoi la phase de calibration baseline est obligatoire.

### Questions sur la sécurité

**Q : Pourquoi bcrypt et pas SHA-256 pour les mots de passe ?**
> SHA-256 est rapide (< 1 µs), ce qui le rend vulnérable aux attaques par force brute sur GPU. bcrypt est délibérément lent (> 100 ms) et intègre un salt aléatoire → chaque hash est unique même pour le même mot de passe → rend les rainbow tables inutiles.

**Q : Que se passe-t-il si le JWT est volé ?**
> L'access token expire en 30 minutes. Le refresh token est stocké en HttpOnly cookie (ne peut pas être lu par JavaScript). En cas de compromission suspectée, l'endpoint `POST /logout-all` invalide tous les refresh tokens → le pirate ne peut plus renouveler l'access token.

### Questions sur l'architecture

**Q : Pourquoi des WebSockets et pas du polling HTTP ?**
> Le polling HTTP (requête toutes les N secondes) introduit de la latence et génère beaucoup de trafic inutile. Les WebSockets maintiennent une connexion persistante → le backend pousse les données exactement quand elles sont disponibles (chaque époque = 1 sec). Indispensable pour le neurofeedback temps réel.

**Q : Comment le système gère-t-il la déconnexion de l'ESP32 ?**
> TCPReceiver détecte l'absence de données (timeout > 2s) → marque le statut ESP32 comme "déconnecté" → WebSocket push `type="esp32_status"` vers le frontend → affichage d'une alerte dans l'interface → session mise en pause automatiquement.

**Q : Pourquoi APScheduler et pas Celery pour le fine-tuning ?**
> Celery nécessite un broker séparé (Redis/RabbitMQ) et une architecture worker/coordinator plus complexe. APScheduler s'intègre directement dans le processus FastAPI, suffisant pour des tâches nocturnes simples. Si le fine-tuning devenait une charge lourde avec des centaines de patients simultanément, la migration vers Celery serait justifiée.

---