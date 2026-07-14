# NeuroCap Backend — FastAPI v3.0

Asynchronous REST + WebSocket API for the NeuroCap EEG neurofeedback platform.
Real-time EEG pipeline (ESP32 → DSP → EEGNet DualClassifier) + 15-session adaptive protocol engine + media recommendation engine + NeuroCoach RAG assistant + automated nightly fine-tuning.

---

## Table of Contents

1. [Contributors](#contributors)
2. [Stack](#stack)
3. [Project Structure](#project-structure)
4. [Installation](#installation)
5. [Environment Variables](#environment-variables)
6. [API Routes](#api-routes)
7. [WebSocket EEG](#websocket-eeg--wshosteeg)
8. [Automated Fine-Tuning](#automated-fine-tuning)
9. [Security](#security)
10. [Required Supabase Tables](#required-supabase-tables)
11. [Role Access Matrix](#role-access-matrix)

---

## Contributors

| Module | Author | Scope |
|--------|--------|-------|
| **DSP pipeline** (`services/eeg/dsp/`, `tcp_receiver.py`, `wifi_manager.py`) | **Oumama Sendadi** | Original implementation in `integration-temporaire/backend-signal/`. IIR Golden Filter, EpochExtractor, EOG/EMG artifact detection, DSP feature extraction, ESP32 TCPReceiver, UDP WifiManager. |
| **DSP → EEGNet integration** | **Yasmine El Mkhantar** | `dual_classifier.py` (EEGNet DL+TL inference), `file_processor.py` (offline analysis), `eeg_pipeline.py` (orchestration), wiring into auth/DB/sessions. |
| **All REST routes, protocol engine, media recommendations, RAG, fine-tuning** | **Yasmine El Mkhantar** | Every router listed below, Pydantic schemas, Supabase integration. |

---

## Stack

| Component | Technology |
|---|---|
| Framework | FastAPI 0.115+ (async) |
| Database | Supabase (PostgreSQL via `supabase-py` AsyncClient) |
| Auth | JWT (python-jose) + bcrypt |
| Real-time | WebSocket `/ws/eeg` (signal + epochs + electrode) and `/api/feedback/ws/{session_id}` |
| DSP | NumPy, SciPy, MNE, PyWavelets |
| ML — production | EEGNet DualClassifier (concentration AUC 0.751 · stress AUC 0.607), continuous 0–100 regression |
| Fine-tuning | Per-patient EEGNet FC head, retrained nightly (APScheduler) |
| RAG generation | DeepSeek API → Groq (Llama 3.3 70B) → local Ollama — resilient LLM cascade |
| Scheduler | APScheduler AsyncIOScheduler (02:00 UTC), optional dependency |
| Config | python-dotenv, centralised `Settings` singleton |
| Media | Cloudinary |

---

## Project Structure

```
app/Backend/
├── app/
│   ├── main.py                        # Lifespan: EEG pipeline + FT scheduler + WS /ws/eeg
│   ├── config.py                      # Settings (python-dotenv, lru_cache singleton)
│   ├── core/
│   │   ├── database.py                # Supabase AsyncClient singleton (get_db)
│   │   └── security.py                # JWT, bcrypt, get_current_user / get_therapist_user / get_admin_user
│   ├── middleware/
│   │   └── security.py                # CORS, rate limiting, brute-force guard
│   ├── routes/                        # 13 routers — see API Routes below
│   │   ├── auth.py                    # /api/auth
│   │   ├── sessions.py                # /api/sessions
│   │   ├── Profile.py                 # /api/profile
│   │   ├── admin.py                   # /api/admin
│   │   ├── therapist.py               # /api/therapist
│   │   ├── assistant.py               # /api/assistant (RAG)
│   │   ├── eeg.py                     # /api/eeg (live stream, file upload, fine-tuning status)
│   │   ├── media.py                   # /api/media
│   │   ├── feedback.py                # /api/feedback (+ WS /api/feedback/ws/{session_id})
│   │   ├── eeg_feedback.py            # /api/eeg-feedback (free-mode interaction log)
│   │   ├── protocol.py                # /api/protocol (15-session adaptive program)
│   │   ├── recommendations.py         # media recos, playlists, patient dashboard, fine-tuning hooks
│   │   └── consent.py                 # /api/consent
│   ├── schemas/                       # Pydantic request/response models (incl. schemas/media_reco.py)
│   └── services/
│       ├── eeg/
│       │   ├── eeg_pipeline.py        # Singleton orchestrator (TCPReceiver + DSP + WS)
│       │   ├── tcp_receiver.py        # ESP32 CSV stream receiver (port 9000)
│       │   ├── wifi_manager.py        # ESP32 WiFi UDP manager (port 4320)
│       │   ├── dsp/
│       │   │   ├── filters.py         # Golden Filter IIR — HP 0.5 Hz / LP 40 Hz / Notch 50 Hz
│       │   │   ├── epochs.py          # EpochExtractor — 4 s × 250 Hz, 75% overlap, z-score
│       │   │   ├── features.py        # ~29 spectral/Hjorth/entropy features (live dashboard display)
│       │   │   ├── artifacts.py       # EOG/EMG artifact detection
│       │   │   ├── dual_classifier.py # EEGNet DL+TL → concentration + stress 0–100 (production)
│       │   │   ├── processor.py       # RealTimeProcessor orchestration
│       │   │   └── file_processor.py  # Offline .edf/.csv/.txt analysis
│       │   └── recording/csv_handler.py
│       ├── finetune/                  # see app/Backend/app/services/finetune/README.md
│       │   ├── conditions.py          # Activity rules + trigger thresholds (v1/v2/drift/maintenance)
│       │   ├── runner.py              # Nightly EEGNet FC fine-tuning per patient
│       │   └── scheduler.py           # APScheduler nightly job (lazy import, optional)
│       ├── protocol_engine.py         # 15-session protocol: phases, paliers, adaptive thresholds, early-stop
│       ├── protocol_progress_service.py # Calendar progress tracking (user_protocol_progress)
│       ├── calibration_service.py     # Session-1 calibration: IAPF, ERD, TBR, cognitive profile A/B/C
│       ├── media_recommendation.py    # EEG-state-driven adaptive media scoring engine
│       ├── session_media_bridge.py    # Bridges live session_events → media recommendation engine
│       ├── ai_report.py               # LLM session report generation (DeepSeek → Groq fallback)
│       ├── consent_service.py         # Personalised consent PDF generation
│       ├── adaptative_engine.py       # EWMA adaptive threshold (P1–P4 paliers)
│       ├── classifieur.py             # Legacy heuristic/PyTorch fallback classifier
│       ├── auth.py                    # Password hashing/verification, token helpers
│       ├── email_service.py           # Brevo SMTP — verification & consent emails
│       ├── rag_service.py             # NeuroCoach RAG orchestration (wraps Assistant_rag/)
│       └── signal_processing.py       # Offline signal processing utilities
├── models/personal/                   # Per-patient fine-tuned EEGNet checkpoints (.pt)
├── recordings/                        # Raw CSV signal recordings
├── knowledge_base.db                  # RAG knowledge base (built from Assistant_rag/kb/)
├── .env.example                       # Environment template
├── requirements.txt
└── Dockerfile
```

---

## Installation

```bash
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux / macOS

pip install -r requirements.txt

# Optional — enables nightly automated fine-tuning
pip install APScheduler

cp .env.example .env
# Fill in Supabase + JWT + Cloudinary variables (see below)

uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

> The backend starts **even without APScheduler installed**: a warning is logged and the scheduler is disabled. Everything else (EEG, API, WebSocket) works normally.

---

## Environment Variables

`.env.example` covers the required core variables. A few optional ones (LLM cascade, cache) are read directly by `config.py` with safe defaults and don't need to be set for local development.

```env
# Supabase (required)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# JWT (required)
SECRET_KEY=change-this-in-production

# Cloudinary (required)
CLOUDINARY_CLOUD_NAME=your-cloud
CLOUDINARY_API_KEY=your-key
CLOUDINARY_API_SECRET=your-secret

# Email — optional, dev mode (code shown in-app) if left empty
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=

# NeuroCoach LLM cascade — optional, falls back to local Ollama if all empty
DEEPSEEK_API_KEY=
GROQ_API_KEY=
GROQ_MODEL=llama-3.3-70b-versatile
LLM_MODEL=mistral
OLLAMA_URL=http://localhost:11434

# Cache — optional
REDIS_URL=redis://localhost:6379
```

> `SUPABASE_ANON_KEY` — note the name: earlier drafts of this project used `SUPABASE_KEY`, but `app/config.py` reads `SUPABASE_ANON_KEY`. Keep `.env` consistent with `config.py`.

---

## API Routes

13 routers are mounted in `main.py`. This table lists the main endpoint groups — the full interactive reference (all parameters, response models) is auto-generated at **`/docs`** (Swagger UI) once the server is running.

### Auth — `/api/auth`
| Method | Route | Description |
|---|---|---|
| POST | `/send-code` | Send email verification code |
| POST | `/register` | Register + JWT tokens |
| POST | `/login` | Login → access + refresh token |
| POST | `/refresh` | Refresh access token |
| GET | `/me` | Current user profile |
| POST | `/change-password` | Change password |

### Sessions — `/api/sessions`
| Method | Route | Description |
|---|---|---|
| GET | `/calendar` | Session calendar view |
| GET | `` | List patient sessions |
| POST | `` | Create a session |
| GET | `/{id}` | Session detail |
| GET | `/{id}/report` | Full session report |
| GET | `/{id}/export` | Export session as CSV |
| GET | `/export/all` | Export all sessions as CSV |

### Profile — `/api/profile`
| Method | Route | Description |
|---|---|---|
| GET | `/me` | EEG profile (type A/B/C, IAPF, TBR, palier) |
| POST | `/calibration` | Save calibration results |

### EEG — `/api/eeg`
| Method | Route | Description |
|---|---|---|
| GET | `/models/status` | Loaded model status |
| GET | `/status` | ESP32 state, baseline, signal quality |
| GET | `/analyze` | Detailed DSP report |
| POST | `/baseline/finalise` | Compute individual Z-scores |
| POST | `/recording/start` / `/recording/stop` | Start/stop CSV recording |
| GET | `/recording/export` | Download recorded signal CSV |
| GET | `/wifi/networks` | Saved ESP32 WiFi networks |
| POST | `/wifi/configure` / `/wifi/use_saved` / `/wifi/reset` | ESP32 WiFi management |
| POST | `/analyze_file` | Analyse .edf/.csv/.txt file (optional auth → stores epochs) |
| GET | `/my-reports` | Authenticated patient's EEG reports |
| GET | `/finetuning/status` | Fine-tuning status (activity, epochs, running job) |
| POST | `/report` | Save an EEG report (live or file) |
| WS | `/ws/eeg` | Real-time EEG stream |

### Media — `/api/media`
| Method | Route | Description |
|---|---|---|
| GET | `/list` | Feedback media assets (from `medias` table) |
| GET | `/illusions` | Optical-illusion image set |
| GET | `/features` | Extracted media features (from `Feedback_METADATA/` CSVs) |

### Feedback — `/api/feedback`
| Method | Route | Description |
|---|---|---|
| GET | `/status` | Feedback engine status |
| POST | `/sessions` | Create a feedback session |
| POST | `/recommend` | Next media, driven by live EEG state |
| POST | `/submit` | Submit user evaluation |
| POST | `/skip` | Skip current media (penalised in scoring) |
| POST | `/sam` | Submit SAM self-assessment (1–5) |
| POST | `/end` | Close session + generate LLM report |
| POST | `/media-guide` | Media neuroscience guide content |
| WS | `/ws/{session_id}` | Real-time feedback session stream (play/end commands) |

### EEG Feedback log — `/api/eeg-feedback`
| Method | Route | Description |
|---|---|---|
| POST | `/log` | Log a free-mode (non-protocol) feedback interaction |

### Protocol — `/api/protocol`
15-session adaptive neurofeedback program (calibration → 15 guided sessions → bilans → follow-up).

| Method | Route | Description |
|---|---|---|
| GET | `/status` | Current protocol phase/palier |
| GET | `/calendar` | Protocol session calendar |
| POST | `/sessions/{n}/start` | Start session *n* |
| GET | `/sessions/{n}/config` | Session *n* configuration (blocs, thresholds) |
| POST | `/sessions/{n}/bloc-end` | Register a block result, adapt threshold |
| PUT | `/sessions/{n}/complete` | Mark session *n* complete, evaluate palier progression |
| GET | `/bilan/{session_number}` | Session bilan report |
| GET | `/profile` | Cognitive profile (calibration output) |
| POST | `/calibration/complete` | Finalise Session-1 calibration |
| PUT | `/palier` | Manual palier override (therapist) |
| POST | `/daily-threshold` | Recompute daily adaptive threshold |
| GET | `/progress` / `/progress/therapist` | Patient / therapist progress view |
| POST | `/early-stop` | Trigger early-stop criteria evaluation |
| POST | `/followup-schedule` | Schedule follow-up session |

### Recommendations — media, playlists, patient dashboard
| Method | Route | Description |
|---|---|---|
| POST | `/api/sessions/{id}/media-recommendation` | Live EEG-driven media recommendation |
| POST | `/api/sessions/{id}/media-feedback` | Post-session media feedback |
| POST | `/api/eeg-reports/{id}/generate-media-recommendations` | Offline recommendation generation |
| POST | `/api/finetuning/{job_id}/update-media-scoring` | Recompute media scoring after fine-tuning |
| GET | `/api/patients/{id}/dashboard` | Unified patient media dashboard |
| POST/GET | `/api/patients/{id}/playlists` | Create / list personal playlists |
| GET | `/api/patients/{id}/offline-recommendations/{report_id}` | Offline recommendations |
| PATCH | `/api/patients/{id}/offline-recommendations/{rec_id}/feedback` | Like/dislike feedback |

### Consent — `/api/consent`
| Method | Route | Description |
|---|---|---|
| POST | `/accept` | Record consent, generate + email PDF |
| GET | `/pdf` | Download personalised consent PDF |

### Assistant — `/api/assistant` (NeuroCoach RAG)
| Method | Route | Description |
|---|---|---|
| POST | `/ask` | Ask the assistant a question |
| POST | `/explain` | Explain a metric/result with patient context |
| POST | `/feedback` | Rate an assistant response |

### Therapist — `/api/therapist`
| Method | Route | Description |
|---|---|---|
| GET | `/patients` | Assigned patients |
| GET | `/patients/{id}` | Patient detail |
| GET | `/patients/{id}/sessions` | Session history |
| GET | `/patients/{id}/profile` | EEG profile (read-only) |
| GET/POST | `/patients/{id}/notes` | Clinical notes |
| GET/POST | `/patients/{id}/recommendation` | Objective + weekly target |
| PUT | `/patients/{id}/palier` | Adjust difficulty P1–P4 |
| PATCH | `/patients/{id}/active` | Activate/deactivate account |
| GET | `/patients/{id}/eeg-reports` | Patient's EEG reports |
| GET | `/patients/{id}/export` | Export patient data as CSV |

### Admin — `/api/admin`
| Method | Route | Description |
|---|---|---|
| GET | `/stats` | Global KPIs |
| GET/POST | `/users` | List / create users |
| GET/PUT/DELETE | `/users/{id}` | Detail, edit, delete |
| GET | `/therapists` | List therapists |
| POST | `/assign-patient` | Assign patient → therapist |
| GET/PUT | `/settings`, `/settings/{key}` | System settings |
| GET | `/audit-logs` | Filtered audit log |
| POST | `/send-reminder`, `/send-reminder-all` | Trigger reminder emails |

---

## WebSocket EEG — `ws://host/ws/eeg?token=<jwt>`

Message types broadcast:

| Type | Frequency | Content |
|---|---|---|
| `init` | On connect | ESP32 state, baseline, electrode quality |
| `eeg` | ~62 Hz | Raw signal samples |
| `epoch` | Every 4 s | Display features + EEGNet prediction (concentration+stress 0–100) + confidence |
| `electrode` | Heartbeat | Electrode contact quality |
| `esp32_status` | Event | ESP32 connection change |

Client commands: `FINALISE_BASELINE`, `START_REC` / `STOP_REC`, `ANALYZE_NOW`.

---

## Automated Fine-Tuning

Full detail in [`app/services/finetune/README.md`](app/services/finetune/README.md). Summary:

```
02:00 UTC every night:
  For each patient with an EEG profile:
    1. Check activity (≤14d idle, ≥3 actions/30d, ≥100 reliable epochs/30d)
    2. If inactive → skip
    3. Check trigger thresholds:
         v1          : 2,000 high-confidence epochs, ≥25d since calibration
         v2          : 4,000 new epochs, ≥60d since v1
         drift       : accuracy over last 20 sessions < 85%
         maintenance : ≥180d since last fine-tune
    4. Fine-tune the EEGNet FC head only (backbone frozen) — separately for
       concentration (base: EEGNet DL FULL) and stress (base: EEGNet TL-LR FULL)
    5. Save checkpoints → models/personal/patient_{id8}_{task}_v{n}.pt
    6. Update eeg_profiles + record finetuning_jobs
```

> APScheduler is an **optional** import: if the package isn't installed, the backend starts normally and logs a warning.

---

## Security

| Layer | Measure |
|---|---|
| Secrets | `.env` variables — never committed |
| Passwords | bcrypt hashing |
| JWT | Access + refresh tokens, HS256 |
| Service-role key | Server-side only, never exposed to the frontend |
| CORS | Strict whitelist in `middleware/security.py` |
| Roles | FastAPI dependencies: `get_current_user` → `get_therapist_user` / `get_admin_user` |
| Rate limiting | Brute-force protection on `/api/auth/login` and `/api/auth/register` |
| Audit | Admin mutations recorded in `audit_logs` |
| Soft delete | `deleted_at = NOW()` — data preserved, access revoked |
| Consent | Session start blocked until `/api/consent/accept` recorded (`ConsentGuard` on the frontend) |

---

## Required Supabase Tables

Run **`app/Database/supabase_complete.sql`** in the Supabase SQL editor — it is the current, consolidated schema (23 tables). See [`app/Database/README.md`](../Database/README.md) for the full schema reference. Core tables used directly by this backend:

| Table | Role |
|---|---|
| `users` | Accounts (patient / therapist / admin), consent fields |
| `eeg_profiles` | Cognitive profile A/B/C + fine-tuning checkpoints/version |
| `sessions` / `session_events` | Neurofeedback sessions and per-block EEG events |
| `eeg_reports` | File-analysis and live-session reports |
| `training_epochs` | High-confidence epochs used for fine-tuning |
| `finetuning_jobs` | Fine-tuning run history |
| `protocol_sessions` / `protocol_blocs` / `user_protocol_progress` | 15-session protocol state |
| `medias` / `media_interactions` | Feedback media catalogue and interactions |
| `feedback_sessions` / `feedback_session_events` | Free-mode feedback sessions |
| `user_media_preferences` / `recommendations_media` / `playlists` / `playlist_media` / `offline_recommendations` | Media recommendation engine |
| `therapist_notes` / `therapist_recommendations` | Clinical notes and objectives |
| `audit_logs` / `system_settings` | Admin audit trail and configurable settings |

> `eeg_feedback_logs` (used by `/api/eeg-feedback/log`) is not part of the consolidated schema yet — the route is non-blocking and returns `{"logged": false}` if the table doesn't exist.

---

## Role Access Matrix

| Route group | Patient | Therapist | Admin |
|---|---|---|---|
| `/api/auth/*` | ✅ | ✅ | ✅ |
| `/api/sessions/*`, `/api/profile/*`, `/api/eeg/*` | ✅ | ❌ | ❌ |
| `/api/protocol/*`, `/api/feedback/*`, `/api/media/*`, `/api/consent/*` | ✅ | ❌ | ❌ |
| `/api/patients/*` (recommendations, dashboard, playlists) | ✅ (own data) | ✅ (assigned patients) | ❌ |
| `/api/therapist/*` | ❌ | ✅ | ✅ |
| `/api/admin/*` | ❌ | ❌ | ✅ |
| `/ws/eeg` | ✅ (public token) | ✅ | ✅ |
