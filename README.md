# NeuroCap — Adaptive EEG Neurofeedback System

> **AD8232 + ESP32 · Single-channel Fp2 · 250 Hz · CdC §2.5**

NeuroCap is a full-stack adaptive neurofeedback platform designed for cognitive training (concentration & stress regulation). It combines real-time EEG signal acquisition, a machine-learning classification pipeline, an adaptive protocol engine, and a role-based clinical web application with multilingual support (FR / EN / AR).

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Feature Highlights](#feature-highlights)
3. [Repository Structure](#repository-structure)
4. [Roles & Users](#roles--users)
5. [Quick Start](#quick-start)
6. [Environment Variables](#environment-variables)
7. [Tech Stack](#tech-stack)
8. [ML Pipeline](#ml-pipeline)
9. [Security](#security)
10. [Repository Conventions](#repository-conventions)
11. [Contributors](#contributors)

---

## Architecture Overview

```
NeuroCap/
├── app/                        # Full-stack web application
│   ├── Backend/                #   FastAPI async REST + WebSocket server
│   ├── Frontend/               #   React 18 SPA (Vite + Tailwind)
│   └── Database/               #   Supabase schema & SQL migrations
├── src/                        # ML pipeline (research → production)
│   ├── data/                   #   Preprocessing & feature extraction scripts
│   └── models/                 #   Baselines, deep learning, transfer learning
├── data/                       # Raw & processed EEG datasets
│   ├── Dataset/                #   Concentration + Stress raw recordings
│   ├── Augmentation/           #   Augmented datasets
│   ├── Merge_datasets/         #   Merged training splits
│   └── Validate_datasets/      #   Holdout validation splits
├── features/                   # Feature engineering outputs
│   ├── Features_eng/           #   Engineered feature matrices
│   └── features_extraction/    #   Extraction scripts
├── models/                     # Trained model artefacts (.pt / .pkl)
│   ├── Baseline/               #   RF, SVM, XGBoost models
│   ├── deep_learning/          #   CNN-LSTM, BiGRU, EEGNet, TCN ...
│   ├── transfer_learning/      #   EEGNet fine-tuned variants
│   └── personal/               #   Per-patient fine-tuned checkpoints
├── reports/                    # Experiment outputs, figures, metrics
├── Notebooks/                  # Exploratory analysis & prototyping
├── Tests/                      # Unit & integration tests
├── docker/                     # Docker Compose deployment
├── Feedback_METADATA/          # Feedback session metadata & media
├── Assistant_rag/              # RAG assistant vector store & config
└── requirements.txt            # ML/data-science dependencies
```

---

## Feature Highlights

### Authentication & Security
- Email verification with 8-digit code (via Brevo SMTP — 300 emails/day, free)
- Distinct login errors: unknown email vs. wrong password
- Password strength enforcement (length · uppercase · lowercase · digit · special character) with live visual checklist
- JWT access + refresh tokens, bcrypt password hashing
- Brute-force protection (rate limiting, account lockout after 5 failed attempts)
- Audit log on every login

### Patient Interface
- **Live EEG** — real-time signal stream from AD8232/ESP32 via WebSocket
- **EEG File** — upload and classify recorded CSV sessions
- **Neurofeedback Sessions** — 3-phase adaptive protocol (setup → session → rapport)
- **Adaptive Feedback Engine** — 5 feedback modalities (audio, image, video, brain-state indicator, mini-games), selection driven by Thompson Sampling stored in Supabase
- **History** — past sessions with metrics and reports
- **AI Assistant** — RAG-powered chat for cognitive health guidance
- **Electrode Guide** — integrated 10-20 system diagram, wiring schema, 4-step preparation protocol, and pre-session checklist directly in the EEG selector

### Clinical Interface (Therapist / Admin)
- Patient assignment and monitoring
- Session notes and personalized recommendations
- Admin panel: user management, role assignments, audit logs

### ML & DSP Pipeline
- Bandpass 1–45 Hz + Notch 50 Hz + baseline correction
- Welch PSD, DWT (PyWavelets), statistical and wavelet features
- 17+ deep learning architectures benchmarked (EEGNet, CNN-LSTM, BiGRU-Attention …)
- Transfer learning variants (feature extraction, layer replacement, full fine-tuning)
- Baseline classifiers: SVR, Random Forest, XGBoost, LightGBM (feat15 / feat78 × sans/avec SMOTE)
- **Best model:** EEGNet DL FULL (concentration AUC = 0.751) · EEGNet TL-LR FULL (stress AUC = 0.607) — régression continue 0–100, validation LOSO stricte
- Automated nightly fine-tuning (APScheduler) with per-patient checkpoints

### Internationalisation
- Full i18n via react-i18next: **French**, **English**, **Arabic** (RTL support)
- Light / Dark / Auto theme with design token system

---

## Repository Structure

### `app/Backend/`

```
app/Backend/
├── app/
│   ├── main.py                     # FastAPI entry point + lifespan hooks
│   ├── config.py                   # Centralised settings (loaded from .env)
│   ├── core/
│   │   ├── database.py             # Supabase AsyncClient singleton
│   │   └── security.py             # JWT creation/validation, bcrypt helpers
│   ├── middleware/
│   │   └── security.py             # CORS, rate limiting, brute-force guard
│   ├── routes/
│   │   ├── auth.py                 # /api/auth  (register, login, refresh, me)
│   │   ├── sessions.py             # /api/sessions
│   │   ├── Profile.py              # /api/profile
│   │   ├── admin.py                # /api/admin
│   │   ├── therapist.py            # /api/therapist
│   │   ├── assistant.py            # /api/assistant (RAG)
│   │   └── eeg.py                  # /api/eeg (live stream + file upload)
│   ├── schemas/
│   │   └── __init__.py             # Pydantic request/response models
│   └── services/
│       ├── eeg/
│       │   ├── eeg_pipeline.py     # Main real-time pipeline orchestrator
│       │   ├── tcp_receiver.py     # TCP receiver for ESP32 stream
│       │   ├── wifi_manager.py     # Wi-Fi connection manager
│       │   ├── dsp/
│       │   │   ├── filters.py      # Bandpass, notch, baseline filters
│       │   │   ├── epochs.py       # Epoch extraction (4 s, 75 % overlap)
│       │   │   ├── features.py     # PSD + DWT + statistical features
│       │   │   ├── artifacts.py    # Artifact detection & rejection
│       │   │   ├── ml_classifier.py    # LightGBM inference (feat63)
│       │   │   ├── dual_classifier.py  # EEGNet DL+TL (concentration + stress 0–100)
│       │   │   └── file_processor.py   # Offline .edf/.csv/.txt analysis
│       │   └── recording/
│       │       └── csv_handler.py  # Raw signal recording to CSV
│       ├── finetune/
│       │   ├── conditions.py       # Fine-tune trigger conditions
│       │   ├── runner.py           # Fine-tuning loop
│       │   └── scheduler.py        # APScheduler nightly job
│       ├── adaptative_engine.py    # EWMA adaptive threshold (P1–P4 paliers)
│       ├── email_service.py        # Brevo SMTP — verification code emails
│       ├── rag_service.py          # RAG assistant (vector retrieval + LLM)
│       └── signal_processing.py   # Offline signal processing utilities
├── models/personal/                # Per-patient fine-tuned model checkpoints
├── recordings/                     # Raw CSV signal recordings
├── .env.example                    # Environment template
├── requirements.txt
└── Dockerfile
```

### `app/Frontend/src/`

```
src/
├── components/
│   ├── Layout.jsx                  # Navigation shell, role-aware sidebar
│   ├── Brain3D.jsx                 # 3-D brain anatomy visualisation
│   ├── EEGVisualization.jsx        # Real-time waveform canvas
│   ├── EEGGauge.jsx                # Mental state confidence gauge
│   ├── TopoMap2D.jsx               # 2-D topographic map
│   ├── RecommendationEngine.jsx    # AI-driven session recommendations
│   ├── RAGChat.jsx                 # Embedded RAG assistant chat
│   ├── SignalQuality.jsx           # Signal quality indicator
│   ├── eeg/
│   │   ├── BandBars.jsx            # Frequency band power bars
│   │   └── SignalCanvas.jsx        # Raw waveform renderer
│   └── feedback/                   # ── Neurofeedback components ──
│       ├── AudioFeedback.jsx       # Audio feedback player
│       ├── ImageFeedback.jsx       # Image feedback display
│       ├── VideoFeedback.jsx       # Video feedback display
│       ├── BrainStateIndicator.jsx # Real-time brain state visual
│       ├── FeedbackSelector.jsx    # Modality selector
│       ├── FeedbackJustification.jsx# Thompson Sampling explanation
│       ├── FeedbackReport.jsx      # Post-session report card
│       ├── GameFeedback.jsx        # Game feedback wrapper
│       └── games/
│           ├── MemoryGame.jsx      # Memory card game
│           ├── PuzzleGame.jsx      # Puzzle game
│           ├── SudokuGame.jsx      # Sudoku
│           ├── CalculGame.jsx      # Mental arithmetic
│           └── EnigmeGame.jsx      # Riddle game
├── pages/
│   ├── Landing.jsx                 # Public landing page
│   ├── Login.jsx                   # Login (distinct email/password errors)
│   ├── Register.jsx                # Register + email verification + password strength
│   ├── DashboardPage.jsx           # Patient dashboard (simulation mode)
│   ├── EEGSelector.jsx             # Session launcher + integrated electrode guide
│   ├── EEGLive.jsx                 # Live EEG session
│   ├── EEGFile.jsx                 # Offline CSV analysis
│   ├── FeedbackPage.jsx            # 3-phase neurofeedback session
│   ├── SessionPage.jsx             # Session wrapper
│   ├── SessionLive.jsx             # Live session view
│   ├── History.jsx                 # Session history & reports
│   ├── Assistant.jsx               # RAG AI assistant
│   ├── Profile.jsx                 # User profile management
│   ├── TherapistDashboard.jsx      # Therapist monitoring dashboard
│   ├── TherapistPatientDetail.jsx  # Per-patient detail view
│   ├── AdminDashboard.jsx          # Admin statistics dashboard
│   └── AdminPanel.jsx              # User & role management
├── stores/                         # Zustand global state
├── hooks/                          # Custom React hooks
├── services/                       # Axios API wrappers
├── utils/                          # Shared utilities
├── lib/                            # Library helpers
├── i18n/locales/                   # FR / EN / AR translation files
└── styles/                         # Tailwind config & global CSS
```

### `src/` — ML Research Pipeline

```
src/
├── data/
│   ├── pipeline_fp2.py             # Full preprocessing pipeline (Fp2 electrode)
│   ├── pipeline_regression.py      # Regression coordinator (scoring → split → aug → feat)
│   ├── features_extraction.py      # 15 lightweight features (embarquable ESP32)
│   ├── feature_eng.py              # 78 advanced features (8 categories, ~35 ms)
│   ├── augmentation_eeg.py         # EEG augmentation (5 experiments A/B/C/D/FULL)
│   ├── scoring/                    # Score attribution 0–10 (concentration + stress)
│   └── validate_data/
│       ├── validate_concentration.py
│       └── validate_stress.py
└── models/
    ├── baselines/
    │   ├── baseline_ML_regression.py               # SVR/RF/XGB/LGBM — feat15
    │   ├── baseline_ML_regression_feature_eng.py   # feat78
    │   └── compare_baseline_global.py
    ├── metrics_professional.py     # Shared metrics module (5 levels, LOSO)
    ├── deep_learning/
    │   ├── DL_utils_regression.py  # Shared engine (CNNPreEncoder, Bahdanau, LOSO)
    │   ├── architectures/          # 19 model definitions (see below)
    │   └── compare.py              # Compare 19 architectures (figures + report)
    ├── transfer_learning/
    │   ├── EEGNet_feature_extraction.py   # TL-2: frozen backbone
    │   ├── EEGNet_full_finetuning.py      # TL-1: all layers unfrozen
    │   ├── EEGNet_layer_replacement.py    # TL-3 ★: best stress AUC 0.607
    │   └── compare_tl.py
    ├── compare/
    │   └── compare_all_models.py   # Global ML / DL / TL comparison → final decision
    └── inference_engine.py         # Unified backend interface (InferenceEngine)
```

**Deep learning architectures benchmarked (19) :**
`EEGNet · CNN1D · CNN2D · CNN3D · CNN_LSTM_Att · CNN_GRU_Att · LSTM1L · LSTM2L · LSTM_ATT · BiLSTM1L · BiLSTM2L · BiLSTM_ATT · GRU1L · GRU2L · GRU_ATT · BiGRU1L · BiGRU2L · BiGRU_ATT · TCN`

### `models/` — Trained Artefacts

| Folder | Contents |
|---|---|
| `Baseline/` | `rf_model.pkl`, `svm_model.pkl`, `xgb_model.pkl` |
| `baseline_FeatEng/` | Same classifiers trained on engineered features |
| `deep_learning/DL_models/` | `.pt` checkpoints for all 17+ architectures |
| `deep_learning/DANN_models/` | Domain Adversarial Neural Network variants |
| `transfer_learning/TL_models/` | EEGNet TL variants (3 strategies) |
| `personal/` | `patient_{id}_v{n}.joblib` — per-patient fine-tuned models |

> **Best model:** `CNN_LSTM_Att.pt` — **89.4 % accuracy**, F1: 0.89

---

## Roles & Users

| Role | Pages accessible | Description |
|---|---|---|
| **Patient** | Dashboard, Live EEG, EEG File, Feedback, History, Assistant, Profile | Performs adaptive neurofeedback sessions |
| **Therapist** | Therapist dashboard, Patient detail, Profile | Monitors assigned patients, writes session notes, sets personalised recommendations |
| **Admin** | Admin dashboard, Admin panel, all routes | Full user management, role assignments, audit log review |

---

## Quick Start

### 1 — Backend (FastAPI)
```bash
cd app/Backend
python -m venv venv && venv\Scripts\activate     # Windows
# source venv/bin/activate                        # macOS / Linux
pip install -r requirements.txt
cp .env.example .env    # fill in secrets (see table below)
uvicorn app.main:app --reload --port 8001
```

### 2 — Frontend (React)
```bash
cd app/Frontend
npm install
npm run dev      # → http://localhost:5173
```

### 3 — Docker (full stack)
```bash
docker compose -f docker/docker-compose.yml up --build
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `SUPABASE_URL` | ✅ | Supabase project URL |
| `SUPABASE_ANON_KEY` | ✅ | Supabase anon (public) key |
| `SUPABASE_SERVICE_ROLE_KEY` | ✅ | Service-role key — server-side only, never expose to frontend |
| `SECRET_KEY` | ✅ | JWT signing secret (`openssl rand -hex 32`) |
| `CLOUDINARY_CLOUD_NAME` | ✅ | Cloudinary cloud name (media storage) |
| `CLOUDINARY_API_KEY` | ✅ | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | ✅ | Cloudinary API secret |
| `SMTP_USER` | ⚙️ | Brevo SMTP login (e.g. `ac693d001@smtp-brevo.com`) |
| `SMTP_PASSWORD` | ⚙️ | Brevo SMTP master password |
| `SMTP_FROM` | ⚙️ | Sender address shown to users (must be verified in Brevo) |
| `REDIS_URL` | optional | Redis URL for cache (`redis://localhost:6379`) |
| `LLM_MODEL` | optional | Ollama model name for RAG assistant (`mistral`) |
| `OLLAMA_URL` | optional | Ollama server URL (`http://localhost:11434`) |

> ⚙️ If `SMTP_USER` is empty, the system runs in **dev mode**: the verification code is returned directly in the API response and displayed as a yellow banner on the registration page — no email setup needed for local development.

> **Never commit `.env` or service-role credentials to version control.**

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, Vite, Tailwind CSS 3, Zustand, Recharts, Three.js, i18next (FR/EN/AR) |
| **Backend** | FastAPI, Python 3.11+, Supabase AsyncClient, bcrypt, python-jose, APScheduler |
| **Database** | Supabase (PostgreSQL) |
| **Real-time** | WebSocket — EEG stream via FastAPI, TCP receiver for ESP32 |
| **Email** | Brevo SMTP (300 emails/day, free tier — transactional verification codes) |
| **ML / DSP** | PyTorch, NumPy, SciPy, MNE, PyWavelets, LightGBM, scikit-learn, XGBoost |
| **Hardware** | AD8232 ECG module + ESP32 (single-channel Fp2, 250 Hz) |
| **Deployment** | Docker Compose, Nginx (optional reverse proxy) |

---

## ML Pipeline

```
Raw EEG (AD8232 / ESP32 TCP stream or CSV upload)
    │
    ▼  Bandpass 1–45 Hz · Notch 50 Hz · Baseline correction
Cleaned signal
    │
    ▼  Epoch extraction (4 s windows, 75 % overlap)
Epochs
    │
    ▼  Welch PSD · DWT (PyWavelets) · Statistical features
Feature matrix
    │
    ├── Baseline: Random Forest / SVM / XGBoost
    └── Deep:     EEGNet / CNN-LSTM-Att / BiGRU-Att  ← best: 89.4 % acc.
    │
    ▼  Confidence threshold (0.60) · Rolling EWMA
Mental state label  {concentration · stress · rest}
    │
    ▼  Adaptive engine (P1–P4 difficulty paliers)
    │
    ▼  Thompson Sampling → optimal feedback modality selection
Real-time neurofeedback  {audio · image · video · brain-state · mini-game}
    │
    ▼  Session report + per-patient fine-tuning (nightly, APScheduler)
```

---

## Security

| Practice | Detail |
|---|---|
| **Secrets** | All credentials in `.env`, never committed to git |
| **JWT** | Short-lived access tokens (30 min) + refresh tokens (7 days) |
| **Passwords** | bcrypt hashing · strength enforced client + server-side (8 chars, upper, lower, digit, special) |
| **Email verification** | 8-digit code with 10-minute TTL required at registration |
| **Brute-force guard** | Max 5 failed logins → 15-minute IP lockout |
| **Rate limiting** | 100 requests / 60 s per IP (configurable via `.env`) |
| **Service-role key** | `SUPABASE_SERVICE_ROLE_KEY` used server-side only, never sent to frontend |
| **CORS** | Strict origin whitelist in FastAPI middleware |
| **Role guards** | Every protected route enforces role via FastAPI `Depends` — zero client-side enforcement |
| **Soft delete** | Users deactivated (`is_active = false`), not permanently erased |
| **Audit logs** | Login events logged with timestamp, user ID, and IP address |

> Generate a production secret key: `python -c "import secrets; print(secrets.token_hex(32))"`

---

## Repository Conventions

- Branch `main` — stable, deployable code
- PRs require at least one review before merge
- Secrets managed via `.env` (never committed)
- `eegenv/` and `app/Backend/venv/` excluded via `.gitignore`
- Commit style: `type(scope): description` (feat / fix / refactor / docs / chore)

---

## Contributors

### Oumama Sendadi
**Signal Processing & Feedback System**

- **DSP pipeline** (`app/Backend/app/services/eeg/dsp/`) — bandpass/notch filters, epoch extraction, artifact detection & rejection, Welch PSD and DWT feature computation
- **Signal service** (`services/signal_processing.py`) — offline signal processing utilities
- **Neurofeedback components** (`app/Frontend/src/components/feedback/`) — all 5 feedback modalities: `AudioFeedback`, `ImageFeedback`, `VideoFeedback`, `BrainStateIndicator`, `GameFeedback`; the 5 mini-games (`MemoryGame`, `PuzzleGame`, `SudokuGame`, `CalculGame`, `EnigmeGame`)
- **Feedback metadata** (`Feedback_METADATA/`) — media assets and metadata extraction from feedback sessions

### Yasmine El Mkhantar
**Full-stack Integration & ML Pipeline**

- **Full-stack web application** (`app/`) — FastAPI backend architecture, all REST routes, Supabase database integration, React frontend SPA
- **Authentication system** — JWT auth (access + refresh tokens), email verification (Brevo SMTP), password strength validation, brute-force protection, audit logging
- **Neurofeedback integration** — integrated Oumama's feedback components into the `FeedbackPage.jsx` 3-phase session flow (setup → live session → rapport), Thompson Sampling adaptive selection persisted in Supabase, patient navbar routing
- **EEG selector & electrode guide** — full preparation protocol, 10-20 system SVG diagram, AD8232 wiring schema, pre-session checklist integrated directly in `EEGSelector.jsx`
- **Dashboard & visualisations** — Brain3D anatomy, simulation mode, `RecommendationEngine`, topographic map, real-time signal canvas
- **ML pipeline** (`src/`) — data augmentation, feature engineering, LightGBM classifier, 17+ deep learning architecture training & evaluation, transfer learning strategies, per-patient nightly fine-tuning
- **Internationalisation** — full FR / EN / AR translation coverage, RTL layout, light/dark/auto theme system
