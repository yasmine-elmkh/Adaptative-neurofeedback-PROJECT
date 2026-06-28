# Rapport Technique — Application NeuroCap
## Système Intelligent de Neurofeedback EEG Adaptatif

**Version** : 2.2.0  
**Date** : Juin 2026  
**Projet** : Easy Medical Device — Cahier des Charges 2025-2026

---

## Table des matières

1. [Vue d'ensemble](#1-vue-densemble)
2. [Architecture générale](#2-architecture-générale)
3. [Frontend — React 18](#3-frontend--react-18)
   - 3.1 Stack technique
   - 3.2 Système de navigation et routage
   - 3.3 Pages et fonctionnalités
   - 3.4 Gestion des états et contextes
4. [Backend — FastAPI](#4-backend--fastapi)
   - 4.1 Structure et démarrage
   - 4.2 Routes API REST
   - 4.3 WebSocket temps réel
   - 4.4 Pipeline EEG
   - 4.5 Système de fine-tuning
   - 4.6 Intelligence artificielle et rapports
5. [Base de données — Supabase](#5-base-de-données--supabase)
   - 5.1 Tables principales
   - 5.2 Tables Neurofeedback
   - 5.3 Tables de recommandation média
   - 5.4 Tables de fine-tuning
6. [Système de Neurofeedback Adaptatif](#6-système-de-neurofeedback-adaptatif)
7. [Protocole 15 séances](#7-protocole-15-séances)
8. [Sécurité et gestion des rôles](#8-sécurité-et-gestion-des-rôles)
9. [Flux de données complet](#9-flux-de-données-complet)

---

## 1. Vue d'ensemble

NeuroCap est une application web médicale full-stack conçue pour le neurofeedback EEG adaptatif. Elle permet à des patients de réguler leur état cognitif (concentration, stress, relaxation) via un protocole de 15 séances guidé par des mesures EEG en temps réel.

### Rôles utilisateurs

| Rôle | Accès |
|------|-------|
| **patient** | Dashboard, EEG live, analyse fichier, neurofeedback, historique, assistant IA |
| **therapist** | Tableau de bord thérapeute, suivi patients, notes cliniques, recommandations |
| **admin** | Gestion complète des utilisateurs, paramètres système, audit logs |

### Technologies clés

| Composant | Technologie |
|-----------|-------------|
| Frontend | React 18, Vite, Tailwind CSS 3 |
| Backend | FastAPI (Python), port 8001 |
| Base de données | Supabase (PostgreSQL hébergé) |
| IA | Claude API (Anthropic) pour rapports, LightGBM pour classification EEG |
| Hardware | ESP32 via WiFi/TCP (port 9000) |
| Médias | Cloudinary (CDN) |

---

## 2. Architecture générale

```
┌────────────────────────────────────────────────────────────┐
│                     FRONTEND (React 18)                    │
│  React 18 + Vite + Tailwind CSS + Zustand + Three.js       │
│  i18n: FR / EN / AR (RTL)   Theme: dark / light / auto     │
└────────────────────┬───────────────────────────────────────┘
                     │  REST + WebSocket
┌────────────────────▼───────────────────────────────────────┐
│                   BACKEND (FastAPI v2.2.0)                  │
│  JWT Auth  │  12 Routers API  │  Pipeline EEG  │  AI Layer │
│  Port 8001                                                  │
└────────────────────┬───────────────────────────────────────┘
                     │  Supabase Python SDK (AsyncClient)
┌────────────────────▼───────────────────────────────────────┐
│              BASE DE DONNÉES (Supabase / PostgreSQL)        │
│  20+ tables  │  Indexes optimisés  │  RLS désactivé        │
└────────────────────────────────────────────────────────────┘
                     ▲
         TCP :9000 / UDP 4320-4323
┌────────────────────┴───────────────────────────────────────┐
│                HARDWARE ESP32 (NeuroCap casque)             │
│  Acquisition EEG → WiFi → Backend DSP → WebSocket          │
└────────────────────────────────────────────────────────────┘
```

---

## 3. Frontend — React 18

### 3.1 Stack technique

| Librairie | Usage |
|-----------|-------|
| **React 18** | Framework UI principal |
| **Vite** | Build tool et serveur de développement |
| **Tailwind CSS 3** | Styles utilitaires + Design tokens `--nc-*` |
| **Zustand** | Gestion d'état global |
| **Recharts** | Graphiques et visualisations de données |
| **Three.js** | Cerveau 3D procédural (Brain3D.jsx) |
| **i18next** | Internationalisation FR / EN / AR (RTL) |
| **@supabase/supabase-js** | Client Supabase côté frontend (Thompson Sampling) |

**Design tokens Tailwind personnalisés :**
- `card`, `btn-primary`, `btn-ghost`, `input`, `badge-*`
- Variables CSS : `--nc-*` (couleurs, espacements, typographies)
- Thème : `dark` / `light` / `auto`, persisté via `localStorage` (`neurocap_theme`)

**Internationalisation :**
- Langue par défaut : Français
- Fichiers de traduction : `src/i18n/locales/fr.json`, `en.json`, `ar.json`
- Détection automatique de la langue navigateur

### 3.2 Système de navigation et routage

#### Routes publiques
| Route | Page | Description |
|-------|------|-------------|
| `/` | Landing | Page d'accueil avec présentation |
| `/login` | Login | Authentification JWT |
| `/register` | Register | Inscription nouveau compte |

#### Routes privées (layout principal avec sidebar)
| Route | Page | Rôle requis |
|-------|------|-------------|
| `/dashboard` | Dashboard (rôle-aware) | tous |
| `/history` | Historique des sessions | tous |
| `/history/:id` | Détail session | tous |
| `/assistant` | Assistant IA (RAG) | tous |
| `/profile` | Profil utilisateur | tous |
| `/eeg` | EEGSelector (choix mode) | tous |
| `/eeg-live` | EEGLive (ESP32 temps réel) | tous |
| `/eeg-file` | EEGFile (analyse fichier) | tous |
| `/electrode-guide` | Guide électrodes + consentement | tous |
| `/feedback` | Neurofeedback adaptatif | patient |
| `/admin` | Panneau administration | admin |
| `/therapist` | Tableau de bord thérapeute | therapist + admin |

**Navigation latérale (Layout.jsx) :**
- Icônes : LayoutDashboard, Brain (→/eeg), BookOpen, History, MessageSquare, CircleUser, Sparkles
- Items filtrés selon le rôle (patient voit "Neurofeedback", admin voit "Admin")

### 3.3 Pages et fonctionnalités

#### Page Dashboard (DashboardPage.jsx)
Tableau de bord principal adapté au rôle :
- **Patient** : métriques sessions, progression protocole, graphiques Recharts, Brain3D avec état cognitif en temps réel
- **Thérapeute** : TherapistDashboard — liste patients, notes, recommandations thérapeutiques
- **Admin** : AdminDashboard — gestion utilisateurs, statistiques globales

**Mode simulation (patient) :**
- Bouton "Démarrer simulation" génère 8 sessions synthétiques réalistes (score de 28 % à 91 %)
- `SimLivePanel` : Brain3D animé + 4 métriques (concentration, stress, TBR, alpha) mis à jour toutes les 500 ms
- Signal EEG synthétique : `concentration = 0.5 + sin(t × 0.28) × 0.32 + bruit`
- `RecommendationEngine` toujours visible (moteur de recommandations basé sur les règles du protocole)

#### Page EEGSelector (EEGSelector.jsx)
Point d'entrée EEG : deux cartes de sélection.
- **Live Hardware** → `/eeg-live` (ESP32 via WiFi)
- **Analyse Fichier** → `/eeg-file` (import EDF/CSV/TXT)

#### Page EEGLive (EEGLive.jsx)
Interface temps réel ESP32 avec **4 onglets** :

| Onglet | Contenu |
|--------|---------|
| **Signal** | Oscilloscope canvas (SignalCanvas.jsx), carte ML (état + confiance), bouton enregistrement CSV |
| **Features** | Bandes spectrales (BandBars.jsx), paramètres Hjorth, métriques spectrales, indicateurs fractals |
| **Historique** | Tableau des époques acceptées et rejetées avec confiance |
| **Rapport** | Statistiques globales : distribution états, qualité signal, export rapport |

**Configuration WiFi inline (WifiSetupCard.jsx) :**
- Scan des réseaux disponibles
- Saisie SSID/mot de passe → envoi à l'ESP32 via UDP
- Utilisation d'un réseau sauvegardé, reset WiFi

**Hook `useEEGWebSocket.js` :**
- Gère : `connected`, `eegFrame`, `epochFrame`, `rejectedFrame`, `initFrame`, `esp32Status`
- Commandes : `FINALISE_BASELINE`, `START_REC`, `STOP_REC`, `ANALYZE_NOW`

**Hook `useRecording.js` :**
- États : `rec`, `paused`, `recT` (timer)
- Actions : `start`, `pause`, `resume`, `stop` → appels `/api/eeg/recording/*`

#### Page EEGFile (EEGFile.jsx)
Analyse hors ligne de fichiers EEG :
- Zone drag-and-drop pour fichiers `.edf`, `.csv`, `.txt`
- `MLSummaryCard` : état dominant + barres de distribution (concentration / stress / incertain)
- `EpochTable` : tableau paginé 25 époques/page avec état ML et confiance par époque
- Stockage automatique des époques haute confiance (≥ 0.85) dans `training_epochs` pour le fine-tuning

#### Page Neurofeedback (FeedbackPage.jsx)
Session de neurofeedback cognitif adaptatif en **3 phases** :

| Phase | Description |
|-------|-------------|
| **Setup** | Patient sélectionne son état EEG initial (stress/focus/relax/distrait/neutre) |
| **Session** | Présentation adaptative de stimuli (audio/image/vidéo/jeu) avec évaluation |
| **Rapport** | Durée, médias joués, δ alpha/bêta, rapport IA (Claude API) |

**Types de stimuli disponibles :**
- `AudioFeedback.jsx` — musiques et sons (présets EEG : concentration, relaxation)
- `ImageFeedback.jsx` — images Cloudinary ciblées par état EEG
- `VideoFeedback.jsx` — vidéos thérapeutiques
- `GameFeedback.jsx` — routeur vers 5 mini-jeux cognitifs :
  - `SudokuGame.jsx` — résolution logique
  - `MemoryGame.jsx` — jeu de mémoire visuelle
  - `PuzzleGame.jsx` — puzzles adaptatifs
  - `EnigmeGame.jsx` — énigmes linguistiques
  - `CalculGame.jsx` — calcul mental

**Composants auxiliaires :**
- `BrainStateIndicator.jsx` — visualisation de l'état cognitif courant
- `FeedbackSelector.jsx` — évaluation like/dislike + emoji + étoiles (1-5)
- `FeedbackJustification.jsx` — guide IA cyclique (généré par Claude Haiku)
- `MiniEEGOscilloscope.jsx` — mini-aperçu du signal EEG pendant la session
- `SessionBlockTimer.jsx` — minuteur par bloc de stimulus
- `UserFeedbackBar.jsx` — barre d'évaluation subjective

#### Page Historique (History.jsx)
- Liste chronologique de toutes les sessions du patient
- Détail par session : métriques EEG, score, durée, rapport IA
- Export CSV de session

#### Assistant IA (Assistant.jsx + RAGChat.jsx)
- Interface de chat avec un assistant spécialisé neurofeedback
- Architecture RAG (Retrieval-Augmented Generation) via Claude API
- Contexte enrichi avec le profil EEG et l'historique du patient
- Réponses en langage naturel sur le protocole, les résultats, les recommandations

#### Brain3D (Brain3D.jsx)
Cerveau 3D procédural sans GLTF (Three.js pur) :
- Deux hémisphères avec géométrie SphereGeometry + déplacement sinusoïdal (simulation gyri/sulci)
- Cervelet (ellipsoïde aplati) + tronc cérébral (cylindre)
- Couleur gris-rosé (#c9a8a5) proche du cortex réel
- Éclairage dynamique : lumière chaude (concentration → cyan), lumière rouge-orangée (stress > 0.6)
- 9 électrodes marquées : Fz, Cz, Pz, F3, F4, T3, T4, P3, P4
- Props : `concentration` (0–1), `stress` (0–1)

#### RecommendationEngine (RecommendationEngine.jsx)
Moteur de recommandations basé sur les règles du protocole NeuroCap (Mou et al. 2024) :
- Détecte le palier (P1–P4) selon le nombre de sessions (1-5, 6-10, 11-13, 14-15)
- Utilise le profil EEG (type A/B/C) et la tendance TBR récente
- 7 types de recommandations : `start`, `complete`, `concentration`, `regulation`, `stress`, `rest`, `maintain`
- Règles : TBR > 4.5 → priorité stress ; score déclinant < 25 % → repos ; profil C → biais régulation

#### Panneau Administration (AdminPanel.jsx)
- Création / modification / désactivation de comptes utilisateurs
- Attribution de rôles (patient → therapist → admin)
- Affectation patient ↔ thérapeute
- Consultation des logs d'audit
- Paramètres système (durées blocs, seuils TBR, activation RAG)

### 3.4 Gestion des états et contextes

| Contexte | Rôle |
|----------|------|
| `AuthContext.jsx` | JWT token, user, rôle — persisté en mémoire + appels API |
| `ThemeContext.jsx` | Thème dark/light/auto, clé localStorage `neurocap_theme` |
| `useEEGWebSocket.js` | État WebSocket EEG temps réel |
| `useRecording.js` | État enregistrement CSV |
| `useFeedbackEngine.js` | Logique session neurofeedback (start/recommend/submit/end) avec fallback Supabase Thompson Sampling |

---

## 4. Backend — FastAPI

### 4.1 Structure et démarrage

Le backend est une API FastAPI v2.2.0 démarrant sur le **port 8001**. Au démarrage (`lifespan`), il :
1. Initialise la connexion Supabase
2. Démarre le pipeline EEG temps réel (TCPReceiver + WifiManager + DSP)
3. Démarre le scheduler de fine-tuning automatique (APScheduler)

**Structure des fichiers :**
```
app/Backend/app/
├── main.py                     # Point d'entrée + WebSocket /ws/eeg
├── config.py                   # Settings (Pydantic BaseSettings)
├── core/
│   ├── database.py             # Client Supabase AsyncClient
│   └── security.py             # JWT encode/decode, get_current_user
├── middleware/security.py      # CORS, rate limiting, headers sécurité
├── routes/                     # 12 routers FastAPI
├── services/
│   ├── eeg/                    # Pipeline EEG complet
│   ├── finetune/               # Fine-tuning automatique
│   ├── ai_report.py            # Rapports Claude API
│   └── ...
└── schemas/                    # Modèles Pydantic
```

### 4.2 Routes API REST

#### Authentification — `/api/auth/*`
| Méthode | Route | Description |
|---------|-------|-------------|
| POST | `/register` | Inscription (email, mot de passe, nom) |
| POST | `/login` | Connexion → JWT access + refresh token |
| POST | `/refresh` | Renouvellement du token |
| POST | `/logout` | Invalidation token côté serveur |

#### Sessions — `/api/sessions/*`
| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/` | Liste des sessions de l'utilisateur |
| POST | `/` | Créer une nouvelle session |
| GET | `/calendar` | Calendrier 15 séances du protocole |
| GET | `/{id}` | Détail d'une session |
| GET | `/{id}/report` | Rapport de session (texte IA) |
| GET | `/{id}/export` | Export CSV de la session |

**Constantes protocole :**
- Phase 1 (séances 1-3) : intervalle minimum 5 jours
- Phase 2 (séances 4-10) : intervalle minimum 2 jours
- Phase 3 (séances 11-15) : intervalle minimum 2 jours
- Sessions bilan obligatoires : B1 (séance 5), B2 (séance 10), B3 (séance 15)

#### EEG Temps réel — `/api/eeg/*`
| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/status` | État ESP32, baseline, qualité signal |
| GET | `/analyze` | Rapport DSP détaillé (métriques temps réel) |
| POST | `/baseline/finalise` | Calcule les Z-scores individuels |
| POST | `/recording/start` | Démarre enregistrement CSV |
| POST | `/recording/stop` | Arrête l'enregistrement |
| GET | `/recording/export` | Télécharge le fichier CSV |
| GET | `/wifi/networks` | Réseaux WiFi connus |
| POST | `/wifi/configure` | Configure le WiFi de l'ESP32 |
| POST | `/wifi/use_saved` | Utilise un réseau sauvegardé |
| POST | `/wifi/reset` | Reset configuration WiFi |
| POST | `/analyze_file` | Analyse fichier EEG (EDF/CSV/TXT) |
| POST | `/report` | Sauvegarde rapport EEG (live ou fichier) |
| GET | `/my-reports` | Rapports EEG du patient connecté |
| GET | `/finetuning/status` | État complet du fine-tuning patient |

#### Neurofeedback — `/api/feedback/*`
| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/status` | Statut protocole (séance, palier, phase) |
| POST | `/sessions` | Crée une session de feedback |
| POST | `/recommend` | Recommande le prochain média (Thompson Sampling + features EEG) |
| POST | `/submit` | Évalue un média (like/dislike, SAM score, δ EEG) |
| POST | `/skip` | Skippe un média (pénalité bayésienne) |
| POST | `/sam` | Note SAM globale (1-5) |
| POST | `/end` | Clôt la session + génère rapport Claude |
| POST | `/media-guide` | Guide IA pour le média en cours (Claude Haiku) |
| WS | `/ws/{session_id}` | WebSocket de la session neurofeedback |

#### Protocole — `/api/protocol/*`
| Méthode | Route | Description |
|---------|-------|-------------|
| POST | `/calibration` | Profil de calibration EEG (epochs C1-C4) |
| POST | `/session/start` | Démarre une séance du protocole |
| POST | `/bloc/end` | Fin d'un bloc (adapte le seuil) |
| GET | `/progress` | Progression du protocole patient |
| GET | `/dashboard` | Tableau de bord thérapeute (tous ses patients) |

#### Thérapeute — `/api/therapist/*`
- Liste patients assignés
- Profils EEG et progression protocolaire
- Notes cliniques (CRUD)
- Recommandations thérapeutiques (objectif hebdomadaire)

#### Administration — `/api/admin/*`
- Gestion CRUD des utilisateurs
- Attribution rôles et affectations patient/thérapeute
- Logs d'audit
- Statistiques globales

#### Assistant IA — `/api/assistant/*`
- Chat RAG avec contexte EEG personnalisé
- Service `rag_service.py` : retrieval + prompt enrichi + Claude API
- Réponses en français adaptées au niveau du patient

#### Médias — `/api/media/*`
- Catalogue de médias (audio/image/vidéo/jeu)
- Filtre par type, état EEG cible, catégorie
- Poids Thompson Sampling par média

#### Consentement — `/api/consent/*`
- Formulaire de consentement éclairé
- Validation et stockage en base

### 4.3 WebSocket temps réel

#### `/ws/eeg` — Signal EEG temps réel
Flux principal de l'acquisition temps réel.

**Messages envoyés par le backend :**
| Type | Fréquence | Contenu |
|------|-----------|---------|
| `init` | À la connexion | État ESP32, WiFi, baseline |
| `eeg` | ~62 Hz | Échantillon brut courant |
| `epoch` | Toutes les 4 s | Époque classifiée : état + confiance + features |
| `electrode` | Heartbeat | Qualité de contact des électrodes |
| `esp32_status` | Sur événement | Connexion/déconnexion ESP32 |

**Commandes reçues du frontend :**
| Commande | Action |
|----------|--------|
| `FINALISE_BASELINE` | Calcule les Z-scores de référence |
| `START_REC` | Démarre l'enregistrement CSV |
| `STOP_REC` | Arrête l'enregistrement, retourne le chemin |
| `ANALYZE_NOW` | Retourne le rapport complet instantané |

#### `/api/feedback/ws/{session_id}` — Session neurofeedback
- Broadcast des recommandations de médias en temps réel
- Commandes `play` (nouveau média) et `session_ended` (fin + rapport)

### 4.4 Pipeline EEG

Le pipeline EEG est le cœur du système de traitement du signal.

```
ESP32 (WiFi) → TCPReceiver (:9000) → WifiManager (UDP 4320-4323)
    ↓
DSP v8.0 (dsp/processor.py)
    ├── Filtrage Golden Filter (passe-bande 1-45 Hz)
    ├── Détection artefacts → ContactQualityEstimator (CQE)
    ├── Extraction époques (4 s, overlap 75 %)
    ├── Calcul bandes spectrales (Welch FFT)
    │    delta(1-4), theta(6-8), alpha(8-13), beta(13-30), gamma_low(30-45)
    ├── Classification Z-score individuelle (CognitiveStateClassifier)
    │    FOCUSED / STRESSED / RELAXED / NEUTRAL / INVALID
    └── DualClassifier (EEGNet + LightGBM optionnel)
         ├── EEGNet+LR/Bagging → concentration
         └── RandomForest+78 features → stress
    ↓
WebSocket Manager → broadcast vers tous les clients connectés
    ↓
Stockage training_epochs (si confiance ≥ 0.85)
```

**Règles de classification Z-score (par rapport à la baseline individuelle) :**

| État | Condition |
|------|-----------|
| **INVALID** | CQE < 60 OU emg_ratio > 0.20 |
| **FOCUSED** | Z_theta > +1.0 ET Z_beta ∈ [-0.5, +1.5] ET Z_alpha > -1.5 |
| **STRESSED** | Z_beta_high > +1.5 ET Z_alpha < -1.0 |
| **RELAXED** | Z_alpha > +1.0 ET Z_beta < -0.5 |
| **NEUTRAL** | Aucune condition précédente |

**Hystérésis** : 3 époques consécutives requises pour changer d'état (~3 s).

**Métriques extraites :**
- Puissances relatives par bande (delta, theta, alpha, beta, gamma_low)
- TBR — Theta/Beta Ratio (indicateur de fatigue/inattention)
- EI — Engagement Index (beta / (alpha + theta))
- ABR — Alpha/Beta Ratio
- Paramètres Hjorth (activité, mobilité, complexité)
- Rapport EMG (détection artefacts musculaires)

### 4.5 Système de fine-tuning

Le système de fine-tuning personnalise automatiquement le modèle de classification pour chaque patient.

**Conditions de déclenchement (`finetune/conditions.py`) :**
- **v1** : ≥ 50 nouvelles époques haute confiance depuis la dernière calibration
- **v2** : ≥ 200 époques haute confiance au total non utilisées
- **drift** : dérive détectée (précision < 60 % sur les 20 dernières sessions)
- **maintenance** : plus de 30 jours sans fine-tuning

**Processus (`finetune/runner.py`) :**
1. Récupère les époques haute confiance non utilisées depuis `training_epochs`
2. Re-entraîne le modèle LightGBM sur les données du patient spécifique
3. Valide avec cross-validation 5-fold
4. Sauvegarde le checkpoint si précision améliorée
5. Met à jour `eeg_profiles.finetuned_version` et le chemin du checkpoint
6. Marque les époques utilisées dans `training_epochs.used_in_finetuning`
7. Crée un enregistrement dans `finetuning_jobs`

**Scheduler (`finetune/scheduler.py`) :**
- Vérification toutes les heures via APScheduler
- Exécution du fine-tuning de manière non-bloquante (thread séparé)

### 4.6 Intelligence artificielle et rapports

**Génération de rapports de session (`ai_report.py`) :**
- Modèle : Claude API (Anthropic)
- Rapport structuré en 3 parties (150-200 mots)
- Données incluses : profil EEG, palier, objectif, durée, médias efficaces, δ alpha/bêta
- Généré de manière asynchrone (non bloquant pour l'utilisateur)
- Sauvegardé dans `feedback_sessions.report_text`
- Broadcasté via WebSocket à la fin de session

**Guide média IA (`generate_media_guide`) :**
- Modèle : Claude Haiku (rapide, ~200 ms)
- Personnalisé selon : type de média, état EEG, historique des 5 dernières interactions
- Fallback statique par type de média si Claude indisponible

**Assistant RAG (`rag_service.py`) :**
- Retrieval des documents pertinents sur le neurofeedback
- Prompt enrichi avec profil EEG du patient
- Réponses en français, adaptées au niveau de compréhension

---

## 5. Base de données — Supabase

La base de données est hébergée sur **Supabase** (PostgreSQL géré). Toutes les opérations passent par le SDK Supabase Python (`AsyncClient`). Le Row Level Security (RLS) est désactivé — la sécurité d'accès est gérée au niveau de l'API FastAPI.

### 5.1 Tables principales

#### `users` — Comptes utilisateurs
| Colonne | Type | Description |
|---------|------|-------------|
| id | TEXT PK | Identifiant unique |
| email | TEXT UNIQUE | Email (login) |
| username | TEXT UNIQUE | Nom d'utilisateur |
| hashed_password | TEXT | Mot de passe bcrypt |
| first_name / last_name | TEXT | Prénom / nom |
| role | TEXT | `user` / `patient` / `therapist` / `admin` |
| is_active | BOOLEAN | Compte actif |
| therapist_id | TEXT FK → users | Thérapeute assigné |
| last_login | TIMESTAMPTZ | Dernière connexion |
| deleted_at | TIMESTAMPTZ | Soft delete |

#### `eeg_profiles` — Profils EEG individuels
| Colonne | Type | Description |
|---------|------|-------------|
| user_id | TEXT FK | Patient concerné |
| profile_type | TEXT | `A` / `B` / `C` (profil cognitif) |
| iapf | FLOAT8 | Individual Alpha Peak Frequency |
| baseline_tbr/alpha/beta/theta | FLOAT8 | Valeurs de référence individuelles |
| reactivity_score | FLOAT8 | Score de réactivité neurale |
| current_threshold | FLOAT8 | Seuil adaptatif courant |
| palier | TEXT | `P1` à `P4` |
| calibrated_at | TIMESTAMPTZ | Date de calibration |
| finetuned_version | INT | Version du modèle fine-tuné |
| last_20_sessions_accuracy | FLOAT8 | Précision sur les 20 dernières sessions |

#### `sessions` — Sessions de neurofeedback
| Colonne | Type | Description |
|---------|------|-------------|
| user_id | TEXT FK | Patient |
| objective | TEXT | `concentration` / autre |
| feedback_mode | TEXT | `visual` / `audio` / etc. |
| status | TEXT | `pending` / `running` / `completed` |
| score | FLOAT8 | Score global (0-100) |
| duration_seconds | INT | Durée en secondes |
| avg_concentration / avg_stress / avg_tbr | FLOAT8 | Moyennes EEG |
| n_epochs_total / n_epochs_rejected | INT | Compteurs d'époques |
| recommendations | TEXT | Recommandations post-session |

#### `session_events` — Événements intrasession
- Enregistrement de chaque époque classifiée
- Métriques : concentration_rate, stress_rate, confidence, tbr, ei, abr, power_alpha, power_beta, power_theta
- Détection artefact (`is_artifact`), qualité signal, numéro de bloc

#### `eeg_reports` — Rapports EEG (live et fichier)
- Stockage des rapports d'analyse (session live ou fichier importé)
- Métriques agrégées : état dominant, pourcentages concentration/stress/incertain
- JSON des époques (`epochs_json`)
- Lié au patient et à son thérapeute

#### `audit_logs` — Logs d'audit
- Traçabilité complète des actions sensibles
- user_id, action, ip_address, timestamp

#### `therapist_notes` — Notes cliniques
- Notes textuelles du thérapeute sur un patient
- CRUD complet, horodatées

#### `therapist_recommendations` — Recommandations thérapeutiques
- Objectif recommandé, cible hebdomadaire, notes
- Lié thérapeute ↔ patient

#### `system_settings` — Paramètres système
| Clé | Valeur par défaut | Description |
|-----|-------------------|-------------|
| `p1_max_sessions` | 5 | Sessions max palier P1 |
| `p2_max_sessions` | 10 | Sessions max palier P2 |
| `p3_max_sessions` | 13 | Sessions max palier P3 |
| `block_duration_min` | 3 | Durée d'un bloc (minutes) |
| `n_blocks` | 6 | Blocs par session |
| `fatigue_tbr_ratio` | 2.0 | TBR > baseline × 2 → mode fatigue |
| `rag_enabled` | true | Activer l'assistant RAG |
| `anonymous_exports` | false | Anonymiser les exports |

### 5.2 Tables Neurofeedback

#### `feedback_sessions` — Sessions de neurofeedback adaptatives
| Colonne | Type | Description |
|---------|------|-------------|
| patient_id | TEXT FK | Patient |
| session_number | INT | Numéro de séance dans le protocole |
| phase | TEXT | `phase1` / `phase2` / `phase3` |
| palier | INT | 1 à 4 |
| objective | TEXT | Objectif thérapeutique |
| status | TEXT | `pending` / `running` / `completed` / `interrupted` |
| score | INT | Score 0-100 |
| delta_alpha / delta_beta | FLOAT | Variation des ondes alpha et bêta |
| session_success | BOOLEAN | δ alpha > 0.05 ET δ bêta < -0.05 |
| items_played / items_efficaces | INT | Médias joués / efficaces |
| eeg_snapshot | JSONB | Snapshot EEG au début de session |
| report_text | TEXT | Rapport généré par Claude API |

#### `feedback_session_events` — Événements neurofeedback
- Log de chaque événement : `media_recommended`, `media_skipped`, `sam_rating`
- `event_data` JSON : media_id, état EEG, confiance, TBR, rel_alpha, rel_beta

#### `media_interactions` — Interactions patient/média
| Colonne | Type | Description |
|---------|------|-------------|
| media_id | UUID FK | Média présenté |
| liked | BOOLEAN | Appréciation (like/dislike) |
| sam_score | INT 1-5 | Score SAM (Self-Assessment Manikin) |
| note_concentration | INT 1-5 | Note auto-évaluée concentration |
| note_stress | INT 1-5 | Note auto-évaluée stress |
| delta_alpha / delta_beta | FLOAT | Variation EEG pendant le média |
| efficace | BOOLEAN | delta_alpha > 0.05 ET delta_beta < -0.05 |
| was_skipped | BOOLEAN | Média sauté |

### 5.3 Tables de recommandation média

#### `medias` — Catalogue de médias
- Type : `audio`, `image`, `video`, `game`
- `eeg_target_state` : état EEG visé (`focus`, `stress`, `neutral`, `all`)
- `url_cloudinary` : URL CDN Cloudinary
- `item_weights_alpha` / `item_weights_beta` : poids Thompson Sampling bayésiens
- `category`, `tempo_bpm`, `brightness`, `saturation`, `contrast`
- `game_prefix`, `difficulty_level`, `duration_seconds`

#### `user_media_preferences` — Préférences média appris
- Préférences audio/visuelles apprises par retour utilisateur
- Vecteur de préférences JSONB, moyennes tempo/luminosité/saturation/contraste

#### `recommendations_media` — Recommandations générées
- Recommandations médias live ou offline (score 0–1)
- `is_clicked`, `expires_at`

#### `offline_recommendations` — Recommandations par époque (fichier)
- Recommandation générée pour chaque époque lors d'une analyse fichier
- `eeg_state` : `stress` / `focus` / `neutral`
- `liked`, `feedback_at` pour le retour utilisateur

#### `playlists` / `playlist_media` — Playlists
- Playlists personnelles (patient) ou thérapeutiques (thérapeute)
- Éléments ordonnés avec position

### 5.4 Tables de fine-tuning

#### `training_epochs` — Données d'entraînement
| Colonne | Type | Description |
|---------|------|-------------|
| patient_id | TEXT FK | Patient source |
| report_id | TEXT FK | Rapport EEG d'origine |
| predicted_label | TEXT | `concentration` / `stress` / `uncertain` |
| confidence | FLOAT8 | Confiance du classificateur (≥ 0.85 pour stockage) |
| features | JSONB | 63 features FeatEng extraites |
| is_high_confidence | BOOLEAN | Époque fiable |
| used_in_finetuning | BOOLEAN | Époque déjà utilisée |

**Index composites** pour optimiser les requêtes fine-tuning :
`(patient_id, is_high_confidence, used_in_finetuning)`

#### `finetuning_jobs` — Historique des runs de fine-tuning
| Colonne | Type | Description |
|---------|------|-------------|
| patient_id | TEXT FK | Patient |
| trigger_type | TEXT | `v1` / `v2` / `drift` / `maintenance` |
| status | TEXT | `pending` / `running` / `done` / `failed` |
| n_epochs_used | INT | Nombre d'époques utilisées |
| accuracy_before / accuracy_after | FLOAT8 | Gain de précision |
| model_version | INT | Numéro de version |
| checkpoint_path | TEXT | Chemin vers le modèle sauvegardé |
| error_message | TEXT | Message d'erreur si échec |

---

## 6. Système de Neurofeedback Adaptatif

### Algorithme de recommandation Thompson Sampling

La sélection des médias utilise un algorithme bayésien d'exploration-exploitation (Thompson Sampling) combiné à des features EEG temps réel.

**Processus de sélection (4 étapes) :**

```
1. Filtrage par type de média (si forcé par la logique adaptative)
2. Ciblage par état EEG (si confiance classificateur ≥ 60 %)
3. Affinage par features EEG :
   ├── TBR > 2.0 ET rel_alpha < 0.25 → médias focus
   ├── rel_alpha > 0.45 → médias calme/neutre
   └── rel_beta > 0.35 + état stress → médias relaxants
4. Thompson Sampling : score = Beta(alpha_i, beta_i) pour chaque média
   → sélection du média avec le score le plus élevé
```

**Mise à jour des poids (après évaluation) :**
- Succès (liked=true OU delta_alpha > 0.05 ET delta_beta < -0.05) → alpha_i += 1
- Échec / skip → beta_i += 1
- SAM ≥ 4 → bonus alpha ; SAM ≤ 2 → pénalité beta

**Logique adaptative basée sur l'historique :**
- Concentration faible (note ≤ 2) → force état `focus`, priorité images
- Concentration forte (note ≥ 4) → maintient l'état EEG réel, élargit le pool

### Flux complet d'une session neurofeedback

```
Patient → /feedback
    │
    ├─► Phase Setup
    │   └── Sélection état EEG initial (stress/focus/relax/distrait/neutre)
    │
    ├─► Phase Session (boucle)
    │   ├── POST /api/feedback/recommend
    │   │   ├── Lecture état EEG + features (depuis EEGLive ou snapshot)
    │   │   ├── Thompson Sampling sur catalogue médias
    │   │   └── Broadcast WebSocket → frontend joue le média
    │   │
    │   ├── Présentation média (AudioFeedback / ImageFeedback / VideoFeedback / GameFeedback)
    │   │   └── Guide IA Claude Haiku (via POST /api/feedback/media-guide)
    │   │
    │   ├── Évaluation (FeedbackSelector)
    │   │   ├── like/dislike + emoji + étoiles
    │   │   └── POST /api/feedback/submit → mise à jour poids Thompson
    │   │
    │   └── Répétition jusqu'à fin de session
    │
    └─► Phase Rapport
        ├── POST /api/feedback/end
        ├── Génération rapport Claude API (asynchrone)
        ├── Sauvegarde dans feedback_sessions.report_text
        └── Broadcast WebSocket → FeedbackReport.jsx
```

---

## 7. Protocole 15 séances

Le protocole NeuroCap est structuré en 3 phases et 4 paliers d'intensité progressive.

### Structure du protocole

| Phase | Séances | Intervalle min | Palier |
|-------|---------|----------------|--------|
| Phase 1 (initiation) | 1-3 | 5 jours | P1 |
| Phase 2 (entraînement) | 4-10 | 2 jours | P2-P3 |
| Phase 3 (consolidation) | 11-15 | 2 jours | P3-P4 |

**Sessions bilan :**
- **B1** : après séance 5 (fin phase 1 + début phase 2)
- **B2** : après séance 10 (évaluation mi-protocole)
- **B3** : après séance 15 (évaluation finale)

### Profils cognitifs (A/B/C)

| Profil | Caractéristique | Stratégie |
|--------|-----------------|-----------|
| **A** | Bon régulateur, alpha dominant | Progression standard |
| **B** | Régulateur moyen, TBR modéré | Approche équilibrée |
| **C** | Régulation difficile, stress élevé | Biais régulation, seuils abaissés |

### Score et progression

Calcul du score de session (0-100) :
```
score = (items_efficaces / items_played) × 70 + (30 si session_success)
session_success = (δ_alpha > 0.05 ET δ_beta < -0.05)
```

---

## 8. Sécurité et gestion des rôles

### Authentification JWT
- Tokens JWT signés (access + refresh)
- Middleware de vérification sur toutes les routes privées
- `get_current_user` : dépendance FastAPI injectée dans chaque route protégée

### Contrôle d'accès basé sur les rôles
- Vérification du rôle dans chaque route sensible
- `ProtectedRoute.jsx` côté frontend : redirection si rôle insuffisant
- Routes admin protégées par double vérification (JWT + rôle admin)

### Sécurité HTTP (middleware)
- CORS configuré (origines autorisées en production)
- Headers de sécurité : X-Content-Type-Options, X-Frame-Options, HSTS
- Rate limiting sur les endpoints d'authentification

### Audit
- Toutes les actions administratives enregistrées dans `audit_logs`
- IP address, user_id, action, timestamp

---

## 9. Flux de données complet

### Flux EEG temps réel (mode Live)

```
ESP32 casque
    │ TCP :9000 / UDP 4320-4323
    ▼
Backend FastAPI (EEG Pipeline)
    ├── TCPReceiver → buffer de données brutes
    ├── WifiManager → gestion connexion WiFi
    └── DSP v8.0
         ├── Filtre passe-bande 1-45 Hz
         ├── Détection artefacts (CQE)
         ├── Extraction époques (4s / overlap 75%)
         ├── Calcul Welch FFT → puissances spectrales
         ├── Classification Z-score → état cognitif
         └── DualClassifier (LightGBM + EEGNet)
              │
              ▼ WebSocket /ws/eeg (~62 Hz + epochs)
Frontend EEGLive
    ├── SignalCanvas → oscilloscope
    ├── BandBars → puissances relatives
    ├── Carte ML → état + confiance
    └── Si confiance ≥ 0.85 → stockage training_epochs (Supabase)
```

### Flux analyse fichier (mode Fichier)

```
Utilisateur → drag-drop fichier EDF/CSV/TXT
    │ POST /api/eeg/analyze_file
    ▼
Backend FastAPI
    ├── Lecture fichier (read_edf / read_csv_txt)
    └── process_signal()
         ├── Même pipeline DSP v8.0
         ├── Classification époque par époque
         └── Résumé : état dominant, % états, confiance moyenne
              │
              ▼ Réponse JSON
Frontend EEGFile
    ├── MLSummaryCard → état dominant + barres
    └── EpochTable → tableau paginé 25/page
         │
         └── Si patient authentifié → POST /api/eeg/report → sauvegarde eeg_reports
```

### Flux neurofeedback (mode Feedback)

```
Patient → /feedback → FeedbackPage (3 phases)
    │
    Setup : sélection état EEG → eeg_snapshot
    │
    Session : boucle stimulus
    ├── POST /api/feedback/recommend
    │    ├── Lecture médias depuis Supabase (table medias)
    │    ├── Thompson Sampling + features EEG
    │    └── Sélection du média optimal
    │
    ├── Présentation : Audio/Image/Video/Game + guide Claude Haiku
    │
    ├── Évaluation : FeedbackSelector
    │    └── POST /api/feedback/submit
    │         ├── Sauvegarde media_interactions
    │         └── Mise à jour poids Thompson (medias.item_weights_*)
    │
    └── Fin → POST /api/feedback/end
         ├── Calcul score (0-100)
         ├── Claude API → rapport 3 parties (asynchrone)
         └── WebSocket broadcast → FeedbackReport
```

---

## Résumé des fonctionnalités par composant

| Composant | Fonctionnalités clés |
|-----------|---------------------|
| **Frontend** | Interface multilingue (FR/EN/AR), thème adaptatif, 15+ pages, Brain3D procédural |
| **EEG Live** | Oscilloscope temps réel, classification cognitive, calibration baseline individuelle, enregistrement CSV |
| **EEG Fichier** | Import EDF/CSV/TXT, classification par époque, rapport agrégé, stockage automatique |
| **Neurofeedback** | 5 types de médias, Thompson Sampling bayésien, guide IA, rapport Claude API |
| **Protocole** | 15 séances en 3 phases, 4 paliers adaptatifs, sessions bilan, calendrier |
| **Fine-tuning** | Personnalisation automatique du modèle ML patient par patient |
| **Assistant IA** | RAG spécialisé neurofeedback, réponses contextualisées EEG |
| **Administration** | CRUD utilisateurs, rôles, audit, paramètres système |
| **Thérapeute** | Suivi multi-patients, notes cliniques, recommandations thérapeutiques |
| **Base de données** | 20+ tables Supabase, indexes optimisés, migrations versionnées |
