# NeuroCap Backend — FastAPI v3.0

API asynchrone REST + WebSocket pour la plateforme de neurofeedback EEG NeuroCap.  
Pipeline EEG temps réel (ESP32 → DSP → EEGNet DualClassifier) + fine-tuning nocturne automatique.

---

## Contributeurs

| Module | Auteure | Périmètre |
|--------|---------|-----------|
| **DSP pipeline** (`services/eeg/dsp/`, `tcp_receiver.py`, `wifi_manager.py`) | **Oumama Sendadi** | Implémentation originale dans `integration-temporaire/backend-signal/`. Filtres IIR Golden Filter, EpochExtractor, détection artefacts EOG/EMG, extraction features DSP v8.0, TCPReceiver ESP32, WifiManager UDP. |
| **Intégration DSP + LightGBM** | **Yasmine El Mkhantar** | Ajout `ml_classifier.py` (LightGBM 63 features), `file_processor.py` (analyse offline), `eeg_pipeline.py` (orchestration), connexion au système d'auth/DB/sessions. |
| **Routes API, auth, admin, thérapeute, fine-tuning** | **Yasmine El Mkhantar** | Toutes les routes REST (`/api/eeg`, `/api/auth`, `/api/sessions`, `/api/admin`, `/api/therapist`), service fine-tuning automatique, schémas Pydantic. |

---

## Stack

| Composant | Technologie |
|---|---|
| Framework | FastAPI 0.115+ (async) |
| Base de données | Supabase (PostgreSQL via `supabase-py` AsyncClient) |
| Auth | JWT (python-jose) + bcrypt |
| Temps réel | WebSocket `/ws/eeg` (signal + epochs + électrode) |
| DSP | NumPy, SciPy, MNE, PyWavelets |
| ML primaire | EEGNet DualClassifier (concentration AUC 0.751 · stress AUC 0.607) + LightGBM fallback |
| Fine-tuning | LightGBM incremental (`init_model`) + APScheduler nocturne |
| Scheduler | APScheduler AsyncIOScheduler (02:00 UTC) |
| Config | python-dotenv + pydantic-settings |
| Media | Cloudinary |

---

## Structure du projet

```
app/Backend/
├── app/
│   ├── main.py                        # Lifespan : EEG pipeline + FT scheduler + WS /ws/eeg
│   ├── config.py                      # Settings (pydantic-settings)
│   ├── core/
│   │   ├── database.py                # Supabase AsyncClient singleton (get_db)
│   │   └── security.py                # JWT, bcrypt, get_current_user
│   ├── middleware/
│   │   └── security.py                # CORS, rate limiting
│   ├── routes/
│   │   ├── auth.py                    # /api/auth
│   │   ├── sessions.py                # /api/sessions
│   │   ├── Profile.py                 # /api/profile
│   │   ├── admin.py                   # /api/admin
│   │   ├── therapist.py               # /api/therapist
│   │   ├── assistant.py               # /api/assistant
│   │   └── eeg.py                     # /api/eeg/* (EEG + fine-tuning status)
│   ├── schemas/
│   │   └── __init__.py                # Tous les modèles Pydantic
│   └── services/
│       ├── eeg/
│       │   ├── eeg_pipeline.py        # Singleton orchestrateur (TCPReceiver + DSP + WS)
│       │   ├── tcp_receiver.py        # Réception CSV depuis ESP32 (port 9000)
│       │   ├── wifi_manager.py        # Gestion WiFi UDP (port 4320)
│       │   ├── dsp/
│       │   │   ├── filters.py         # Golden Filter IIR 1–45 Hz
│       │   │   ├── epochs.py          # EpochExtractor 4 s × 250 Hz + z-score
│       │   │   ├── features.py        # ~29 features spectrales/Hjorth/entropie (affichage dashboard live)
│       │   │   ├── artifacts.py       # Détection artefacts EOG/EMG
│       │   │   ├── dual_classifier.py # EEGNet DL+TL → concentration+stress 0–100 (production)
│       │   │   └── file_processor.py  # Analyse offline .edf/.csv/.txt
│       │   └── recording/
│       │       └── csv_handler.py
│       ├── finetune/
│       │   ├── __init__.py
│       │   ├── conditions.py          # Vérification activité + seuils déclenchement
│       │   ├── runner.py              # LightGBM incremental + sauvegarde checkpoint
│       │   └── scheduler.py          # APScheduler nocturne 02:00 UTC (lazy import)
│       ├── adaptative_engine.py
│       ├── classifieur.py
│       └── rag_service.py
├── models/
│   └── personal/                      # Checkpoints personnels : patient_{id8}_v{n}.joblib
├── requirements.txt
└── .env.example
```

---

## Installation

```bash
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux / macOS

pip install -r requirements.txt

# Pour activer le fine-tuning automatique (optionnel au démarrage)
pip install APScheduler lightgbm joblib

cp .env.example .env
# Remplir les variables Supabase + JWT

uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

> Le backend démarre **même sans APScheduler** : un warning est loggé et le scheduler est désactivé. Le reste (EEG, API, WS) fonctionne normalement.

---

## Variables d'environnement

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# JWT
SECRET_KEY=change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

# Cloudinary
CLOUDINARY_CLOUD_NAME=your-cloud
CLOUDINARY_API_KEY=your-key
CLOUDINARY_API_SECRET=your-secret
```

---

## Routes API

### Auth — `/api/auth`
| Méthode | Route | Description |
|---|---|---|
| POST | `/register` | Inscription + tokens JWT |
| POST | `/login` | Connexion → access + refresh token |
| POST | `/refresh` | Renouvellement token |
| GET | `/me` | Profil courant |
| POST | `/change-password` | Changement mot de passe |

### Sessions — `/api/sessions`
| Méthode | Route | Description |
|---|---|---|
| GET | `/` | Liste sessions patient |
| POST | `/` | Créer une session |
| GET | `/{id}/report` | Rapport complet session |
| GET | `/{id}/export` | Export CSV session |
| GET | `/export/all` | Export CSV toutes sessions |

### EEG — `/api/eeg`
| Méthode | Route | Description |
|---|---|---|
| GET | `/status` | État ESP32, baseline, qualité |
| GET | `/analyze` | Rapport DSP détaillé |
| POST | `/baseline/finalise` | Calcul Z-scores individuels |
| POST | `/recording/start` | Démarrer enregistrement CSV |
| POST | `/recording/stop` | Arrêter enregistrement |
| GET | `/recording/export` | Télécharger CSV signal |
| GET | `/wifi/networks` | Réseaux mémorisés ESP32 |
| POST | `/wifi/configure` | Configurer WiFi SSID + pwd |
| POST | `/wifi/use_saved` | Reconnecter réseau mémorisé |
| POST | `/wifi/reset` | Effacer configuration WiFi |
| POST | `/analyze_file` | Analyse fichier .edf/.csv/.txt (auth optionnelle → stockage epochs) |
| POST | `/report` | Sauvegarder rapport EEG (live/fichier) |
| GET | `/my-reports` | Rapports EEG du patient authentifié |
| GET | `/finetuning/status` | Statut fine-tuning IA (activité, epochs, job en cours) |
| WS | `/ws/eeg` | Stream EEG temps réel |

### Thérapeute — `/api/therapist`
| Méthode | Route | Description |
|---|---|---|
| GET | `/patients` | Liste patients assignés |
| GET | `/patients/{id}` | Détail patient |
| GET | `/patients/{id}/sessions` | Historique sessions |
| GET | `/patients/{id}/profile` | Profil EEG (lecture seule) |
| GET/POST | `/patients/{id}/notes` | Notes cliniques |
| GET/POST | `/patients/{id}/recommendation` | Objectif + cible hebdomadaire |
| PUT | `/patients/{id}/palier` | Ajustement difficulté P1–P4 |
| PATCH | `/patients/{id}/active` | Activer/désactiver compte |
| GET | `/patients/{id}/export` | Export CSV patient |
| GET | `/patients/{id}/eeg-reports` | Rapports EEG du patient |

### Admin — `/api/admin`
| Méthode | Route | Description |
|---|---|---|
| GET | `/stats` | KPIs globaux |
| GET/POST | `/users` | Lister + créer utilisateurs |
| GET/PUT/DELETE | `/users/{id}` | Détail, modification, suppression |
| POST | `/assign-patient` | Assigner patient → thérapeute |
| GET/PUT | `/settings/{key}` | Paramètres système |
| GET | `/audit-logs` | Journal d'audit filtré |

---

## WebSocket EEG — `ws://host/ws/eeg?token=<jwt>`

Types de messages diffusés :

| Type | Fréquence | Contenu |
|---|---|---|
| `init` | Connexion | État ESP32, baseline, qualité électrode |
| `eeg` | ~62 Hz | Échantillons signal brut |
| `epoch` | Toutes 4 s | 29 features display + prédiction EEGNet (concentration+stress 0–100) + confiance |
| `electrode` | Heartbeat | Qualité contact électrode |
| `esp32_status` | Événement | Changement connexion ESP32 |

Commandes client :

| Commande | Action |
|---|---|
| `FINALISE_BASELINE` | Calcul Z-scores individuels |
| `START_REC` / `STOP_REC` | Enregistrement CSV |
| `ANALYZE_NOW` | Rapport DSP instantané |

---

## Fine-tuning automatique

```
02:00 UTC chaque nuit :
  Pour chaque patient avec profil EEG :
    1. Vérifier activité (≤ 14j inactif, ≥3 actions/30j, ≥100 epochs/30j)
    2. Si inactif → skip (pas de fine-tuning)
    3. Vérifier seuil :
         v1          : 2 000 epochs ≥ 0.85 confiance, ≥ 25j depuis calibration
         v2          : 4 000 nouvelles epochs, ≥ 60j depuis v1
         drift       : accuracy 20 dernières sessions < 85%
         maintenance : ≥ 180j depuis dernier fine-tuning
    4. LightGBM incremental (init_model=base_clf, lr=0.01)
    5. Sauvegarde → models/personal/patient_{id8}_v{n}.joblib
    6. Mise à jour eeg_profiles + enregistrement finetuning_jobs
```

> APScheduler est un import **optionnel** : si le package n'est pas installé, le backend démarre normalement et log un warning.

---

## Sécurité

| Couche | Mesure |
|---|---|
| Secrets | Variables `.env` — jamais commitées |
| Mots de passe | bcrypt (factor 12) |
| JWT | Access 60 min · Refresh 30 jours · HS256 |
| Service-role key | Côté serveur uniquement, jamais exposée au frontend |
| CORS | Whitelist stricte dans `middleware/security.py` |
| Rôles | Dépendances FastAPI : `get_current_user` → `get_therapist_user` / `get_admin_user` |
| Rate limiting | Brute-force protection sur `/auth/login` et `/auth/register` |
| Audit | Mutations admin enregistrées dans `audit_logs` |
| Soft delete | `deleted_at = NOW()` — données préservées, accès révoqué |

---

## Tables Supabase requises

Exécuter **`app/Database/schema_v3.sql`** dans l'éditeur SQL Supabase.

| Table | Rôle |
|---|---|
| `users` | Comptes (patient / therapist / admin) |
| `eeg_profiles` | Profil cognitif A/B/C + colonnes fine-tuning |
| `sessions` | Sessions neurofeedback |
| `session_events` | Événements EEG par bloc |
| `eeg_reports` | Rapports analyses fichiers + sessions live |
| `training_epochs` | Epochs haute-confiance pour fine-tuning (JSONB 63 features) |
| `finetuning_jobs` | Historique des runs de fine-tuning |
| `therapist_notes` | Notes cliniques |
| `therapist_recommendations` | Objectifs + cibles thérapeutes |
| `audit_logs` | Journal d'audit admin |
| `system_settings` | Paramètres système configurables |

---

## Matrice d'accès par rôle

| Groupe de routes | Patient | Thérapeute | Admin |
|---|---|---|---|
| `/api/auth/*` | ✅ | ✅ | ✅ |
| `/api/sessions/*` | ✅ | ❌ | ❌ |
| `/api/profile/*` | ✅ | ❌ | ❌ |
| `/api/eeg/*` | ✅ | ❌ | ❌ |
| `/api/therapist/*` | ❌ | ✅ | ✅ |
| `/api/admin/*` | ❌ | ❌ | ✅ |
| `/ws/eeg` | ✅ (public) | ✅ | ✅ |
