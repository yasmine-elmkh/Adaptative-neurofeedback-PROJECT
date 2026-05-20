# NeuroCap — Application Unifiée v3.0

> Plateforme full-stack de neurofeedback EEG adaptatif.  
> Pipeline temps réel ESP32 → DSP v8.0 → LightGBM + fine-tuning automatique personnalisé.  
> Dashboard patient, gestion thérapeute, administration, assistant RAG.

---

## Contributeurs

| Partie | Auteure | Description |
|--------|---------|-------------|
| **Acquisition & Signal (DSP)** | **Oumama Sendadi** | Pipeline temps réel ESP32 : TCPReceiver, WifiManager, FilterBank, EpochExtractor, détection artefacts, features DSP v8.0, enregistrement CSV, WebSocket signal — `integration-temporaire/backend-signal/` |
| **Dashboard signal React** | **Oumama Sendadi** | Composants React signal : SignalCanvas, BandBars, WifiSetup, EpochHistory, FeaturesPanel, Sidebar, hooks useWebSocket / useRecording — `integration-temporaire/frontend-signal/` |
| **Classification ML & Deep Learning** | **Yasmine El Mkhantar** | Pipeline preprocessing/augmentation EEG, entraînement 19 architectures DL, classifieurs ML baseline (SVM, RF, XGBoost), LightGBM FeatEng 63 features LOSO |
| **Application NeuroCap full-stack** | **Yasmine El Mkhantar** | Backend FastAPI complet (auth, sessions, admin, thérapeute, assistant, EEG routes), frontend React SPA (toutes les pages), service fine-tuning automatique, intégration DSP + LightGBM dans l'app unifiée |

> **Note d'intégration** : Les modules DSP et composants signal d'Oumama Sendadi (développés dans `integration-temporaire/`) ont été intégrés dans l'application unifiée :
> - `app/Backend/app/services/eeg/` — pipeline DSP intégré
> - `app/Frontend/src/components/eeg/` + `app/Frontend/src/hooks/` — composants signal intégrés

---

## Architecture globale

```
Matériel (AD8232 + ESP32, 250 Hz, Fp2)
    │  TCP :9000  (lignes CSV)
    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  Backend FastAPI  (port 8001)                                          │
│                                                                        │
│  ┌─────────────┐   ┌─────────────────────────────────┐   ┌─────────┐ │
│  │ TCPReceiver │──▶│  DSP v8.0   (eeg/dsp/)          │──▶│  WS     │ │
│  │  port 9000  │   │  Golden Filter 1–45 Hz           │   │ /ws/eeg │ │
│  └─────────────┘   │  EpochExtractor 4 s @ 250 Hz    │   └─────────┘ │
│                    │  Z-score + 63 features FeatEng   │               │
│  ┌─────────────┐   │  LightGBM (LOSO, 63 features)   │   ┌─────────┐ │
│  │ WifiManager │   └─────────────────────────────────┘   │ /ws/    │ │
│  │ UDP :4320   │                                          │ session │ │
│  └─────────────┘   ┌─────────────────────────────────┐   └─────────┘ │
│                    │  Fine-tuning automatique          │               │
│                    │  (services/finetune/)             │               │
│                    │  APScheduler 02:00 UTC            │               │
│                    │  LightGBM incremental (init_model)│               │
│                    └─────────────────────────────────┘               │
│                                                                        │
│  REST /api/auth · /api/sessions · /api/admin · /api/profile           │
│       /api/eeg/* · /api/therapist/* · /api/assistant                  │
└────────────────────────────────────────────────────────────────────────┘
    │ WebSocket  (Vite proxy /ws → 8001)
    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  Frontend React 18 + Vite  (port 5173)                                 │
│                                                                        │
│  /dashboard     → Patient : EEG recordings + sessions neurofeedback   │
│  /eeg           → EEGSelector (choix live / fichier)                  │
│  /eeg-live      → EEGLive (oscilloscope temps réel, WiFi, baseline)   │
│  /eeg-file      → EEGFile (upload + analyse LightGBM + auto-save)     │
│  /electrode-guide → Guide scientifique + consentement RGPD            │
│  /profile       → Profil EEG (type A/B/C, palier, fine-tuning IA)     │
│  /therapist     → Dashboard thérapeute (patients, notes, rapports EEG) │
│  /admin         → Administration (users, audit, settings)              │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Structure du projet

```
app/
├── Backend/
│   ├── app/
│   │   ├── main.py                     ← FastAPI lifespan : EEG pipeline + FT scheduler
│   │   ├── config.py
│   │   ├── core/
│   │   │   ├── database.py             ← Supabase AsyncClient singleton
│   │   │   └── security.py            ← JWT, bcrypt, get_current_user
│   │   ├── middleware/security.py      ← CORS, rate limiting
│   │   ├── routes/
│   │   │   ├── auth.py                ← /api/auth
│   │   │   ├── sessions.py            ← /api/sessions
│   │   │   ├── Profile.py             ← /api/profile
│   │   │   ├── admin.py               ← /api/admin
│   │   │   ├── therapist.py           ← /api/therapist (+ /eeg-reports)
│   │   │   ├── assistant.py           ← /api/assistant
│   │   │   └── eeg.py                 ← /api/eeg/* (tout EEG + fine-tuning status)
│   │   ├── schemas/__init__.py         ← Pydantic models
│   │   └── services/
│   │       ├── eeg/
│   │       │   ├── eeg_pipeline.py    ← Singleton orchestrateur
│   │       │   ├── tcp_receiver.py
│   │       │   ├── wifi_manager.py
│   │       │   ├── dsp/
│   │       │   │   ├── filters.py     ← Golden Filter IIR
│   │       │   │   ├── epochs.py      ← EpochExtractor, z-score
│   │       │   │   ├── features.py    ← extraction spectrales
│   │       │   │   ├── artifacts.py   ← détection EOG/EMG
│   │       │   │   ├── ml_classifier.py ← LightGBM 63 features LOSO
│   │       │   │   └── file_processor.py ← Analyse offline .edf/.csv/.txt
│   │       │   └── recording/csv_handler.py
│   │       ├── finetune/               ← Fine-tuning automatique
│   │       │   ├── conditions.py      ← Règles activité + déclenchement
│   │       │   ├── runner.py          ← LightGBM incremental + sauvegarde
│   │       │   └── scheduler.py       ← APScheduler nocturne 02:00 UTC
│   │       ├── adaptative_engine.py
│   │       ├── classifieur.py
│   │       └── rag_service.py
│   └── requirements.txt
│
└── Frontend/
    └── src/
        ├── pages/
        │   ├── DashboardPage.jsx       ← Stats EEG + sessions neurofeedback
        │   ├── EEGSelector.jsx         ← Choix live / fichier
        │   ├── EEGLive.jsx             ← Stream temps réel
        │   ├── EEGFile.jsx             ← Upload + analyse + auto-save
        │   ├── ElectrodeGuide.jsx      ← Guide + consentement
        │   ├── Profile.jsx             ← Profils A/B/C + fine-tuning IA
        │   ├── TherapistDashboard.jsx
        │   ├── TherapistPatientDetail.jsx
        │   ├── AdminDashboard.jsx
        │   └── AdminPanel.jsx
        ├── components/
        │   ├── eeg/                    ← SignalCanvas, BandBars
        │   └── Layout.jsx
        ├── hooks/
        │   └── useEEGWebSocket.js
        └── utils/api.js                ← eeg.* + finetuningStatus()
```

---

## Pipeline DSP v8.0

```
ESP32 CSV ──► TCPReceiver ──► RealTimeProcessor
                                 │
                          Golden Filter (1–45 Hz IIR causal)
                          EpochExtractor (4 s × 250 Hz, overlap 75%)
                                 │
                          Rejet artefacts (amplitude relative)
                          filtfilt zéro-phase
                                 │
                          63 features FeatEng
                          ├── Spectrales (PSD bandes : delta/theta/alpha/beta/gamma)
                          ├── Ratios (TBR, ABR, engagement, stress_idx)
                          ├── Temporelles (Hjorth, Higuchi FD, variance)
                          └── Ondelettes (db4 niv. 4 : énergie par sous-bande)
                                 │
                          LightGBM LOSO → {concentration, stress, uncertain}
                          confidence seuil 0.60 (CdC §2.5.1)
                                 │
                          WSManager.broadcast()
                          ├── "eeg"     : 1/4 samples (~62 Hz)
                          ├── "epoch"   : toutes 4 s (features + état)
                          └── "electrode": heartbeat qualité contact
```

**Analyse fichier offline** (`file_processor.py`) :  
EDF / CSV / TXT → rééchantillonnage → Golden Filter → 63 features → LightGBM  
→ résumé session + tableau époques + auto-sauvegarde rapport + stockage `training_epochs`

---

## Routes API complètes

### Auth — `/api/auth`
| Méthode | Route | Description |
|---------|-------|-------------|
| POST | `/register` | Inscription + tokens JWT |
| POST | `/login` | Connexion → access + refresh token |
| POST | `/refresh` | Renouvellement token |
| GET  | `/me` | Profil courant |
| POST | `/change-password` | Changement mot de passe |

### Sessions — `/api/sessions`
| Méthode | Route | Description |
|---------|-------|-------------|
| GET  | `/` | Liste sessions patient |
| POST | `/` | Créer une session |
| GET  | `/{id}/report` | Rapport complet session |
| GET  | `/{id}/export` | Export CSV session |
| GET  | `/export/all` | Export CSV toutes sessions |

### EEG — `/api/eeg`
| Méthode | Route | Description |
|---------|-------|-------------|
| GET  | `/status` | État ESP32, baseline, qualité |
| GET  | `/analyze` | Rapport DSP détaillé |
| POST | `/baseline/finalise` | Calcul Z-scores individuels |
| POST | `/recording/start` | Démarrer enregistrement CSV |
| POST | `/recording/stop` | Arrêter enregistrement |
| GET  | `/recording/export` | Télécharger CSV signal |
| GET  | `/wifi/networks` | Réseaux mémorisés ESP32 |
| POST | `/wifi/configure` | Configurer WiFi SSID + pwd |
| POST | `/wifi/use_saved` | Reconnecter réseau mémorisé |
| POST | `/wifi/reset` | Effacer configuration WiFi |
| POST | `/analyze_file` | Analyse fichier .edf/.csv/.txt |
| POST | `/report` | Sauvegarder rapport EEG (live/fichier) |
| GET  | `/my-reports` | Rapports EEG du patient authentifié |
| GET  | `/finetuning/status` | Statut fine-tuning IA (activité, epochs, job) |
| WS   | `/ws/eeg` | Stream temps réel |

### Thérapeute — `/api/therapist`
| Méthode | Route | Description |
|---------|-------|-------------|
| GET  | `/patients` | Liste patients assignés |
| GET  | `/patients/{id}` | Détail patient |
| GET  | `/patients/{id}/sessions` | Historique sessions |
| GET  | `/patients/{id}/profile` | Profil EEG (lecture seule) |
| GET/POST | `/patients/{id}/notes` | Notes cliniques |
| GET/POST | `/patients/{id}/recommendation` | Objectif et cible hebdomadaire |
| PUT  | `/patients/{id}/palier` | Ajustement difficulté P1–P4 |
| PATCH | `/patients/{id}/active` | Activer/désactiver compte |
| GET  | `/patients/{id}/export` | Export CSV patient |
| GET  | `/patients/{id}/eeg-reports` | Rapports EEG du patient |

### Admin — `/api/admin`
| Méthode | Route | Description |
|---------|-------|-------------|
| GET  | `/stats` | KPIs globaux |
| GET/POST | `/users` | Lister + créer utilisateurs |
| GET/PUT/DELETE | `/users/{id}` | Détail, modif, suppression |
| POST | `/assign-patient` | Assigner patient → thérapeute |
| GET/PUT | `/settings/{key}` | Paramètres système |
| GET  | `/audit-logs` | Journal d'audit filtré |

---

## Fine-tuning automatique

```
Chaque nuit à 02:00 UTC :
  Pour chaque patient avec profil EEG :
    1. Vérifier activité (≤ 14j inactif, ≥ 3 actions/30j, ≥ 100 epochs fiables)
    2. Vérifier seuils :
         v1 : 2 000 epochs haute confiance (≥ 0.85), ≥ 25j depuis calibration
         v2 : 4 000 nouvelles epochs, ≥ 60j depuis v1
         drift : accuracy 20 dernières sessions < 85%, ≥ 7j depuis dernier FT
         maintenance : ≥ 180j depuis dernier FT
    3. Si conditions OK → LightGBM incremental (init_model) en asyncio.Task
    4. Sauvegarder checkpoint → models/personal/patient_{id}_v{n}.joblib
    5. Mettre à jour eeg_profiles + enregistrer finetuning_jobs
```

Stockage epochs :  
→ `POST /api/eeg/analyze_file` (patient authentifié) stocke automatiquement  
   les epochs haute confiance dans `training_epochs` (JSONB 63 features)

---

## Flux utilisateur

```
Login → /dashboard
    Patient sans données → empty state : [EEG temps réel] [Analyser un fichier]
    Patient avec données → EEG Recordings (stat cards + AreaChart + table)
                         → Sessions neurofeedback (si sessions existantes)

/eeg (EEGSelector)
    → /eeg-live          Oscilloscope RT · WiFi · baseline · enregistrement CSV
    → /eeg-file          Upload .edf/.csv/.txt → LightGBM → résultat + auto-save thérapeute
    → /electrode-guide   Schéma 10-20 · protocole cutané · consentement RGPD

/profile
    Patient → Profil type A/B/C (ratio α/β + ERD) · métriques EEG · palier · fine-tuning IA
    Thérapeute → Vue info + changement mot de passe
    Admin → Vue info + changement mot de passe
```

---

## Lancement

```bash
# Backend (port 8001)
cd app/Backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Frontend (port 5173)
cd app/Frontend
npm install
npm run dev

# Accès
# App     : http://localhost:5173
# API docs: http://localhost:8001/docs
```

---

## Matériel requis

| Composant | Détail |
|-----------|--------|
| Électrode | Ag/AgCl (Fp2, M1, M2) |
| Amplificateur | AD8232 (gain ×100, filtre 0,5–40 Hz) |
| Microcontrôleur | ESP32 (WiFi 2,4 GHz, sortie TCP CSV 250 Hz) |
| Réseau | PC et ESP32 sur le même réseau WiFi |

---

**NeuroCap v3.0** — Projet de recherche en neurofeedback EEG adaptatif avec fine-tuning IA personnalisé.
