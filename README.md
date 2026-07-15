# NeuroCap — Adaptive EEG Neurofeedback System

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-async-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![PyTorch](https://img.shields.io/badge/PyTorch-EEGNet-EE4C2C?logo=pytorch&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?logo=supabase&logoColor=white)

> **AD8232 + ESP32 · Single-channel Fp2 · 250 Hz · CdC §2.5**

NeuroCap is a full-stack adaptive neurofeedback platform for cognitive training (concentration & stress regulation). It combines real-time EEG signal acquisition, a deep-learning regression pipeline (EEGNet), an adaptive multi-session protocol engine, and a role-based clinical web application with multilingual support (FR / EN / AR).

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Feature Highlights](#feature-highlights)
3. [Repository Structure](#repository-structure)
4. [Documentation Map](#documentation-map)
5. [Roles & Users](#roles--users)
6. [Quick Start](#quick-start)
7. [Environment Variables](#environment-variables)
8. [Tech Stack](#tech-stack)
9. [ML Pipeline](#ml-pipeline)
10. [Security](#security)
11. [Repository Conventions](#repository-conventions)
12. [Contributors](#contributors)

---

## Architecture Overview

```
NeuroCap/
├── app/                        # Full-stack web application
│   ├── Backend/                #   FastAPI async REST + WebSocket server
│   ├── Frontend/               #   React 18 SPA (Vite + Tailwind)
│   └── Database/               #   Supabase schema & SQL migrations
├── src/                        # ML research pipeline (data → models → inference)
│   ├── data/                   #   Validation, scoring, preprocessing, augmentation, features
│   └── models/                 #   Baselines, deep learning, transfer learning
├── data/                       # Raw & processed EEG datasets
│   ├── Dataset/                #   Raw recordings — CLA (concentration) + SAM40 (stress)
│   ├── Regression/             #   Preprocessed + augmented arrays (current pipeline)
│   ├── Scoring/                #   Epochs scored 0–10 (CSV + merged .npy)
│   └── Validate_datasets/      #   Raw-data validation figures
├── Features/                   # Extracted feature matrices — feat15 / feat78 × conc / stress
├── models/                     # Trained model artefacts (.pt / .joblib)
│   ├── Regression/
│   │   ├── DL/                 #   19 deep learning architectures × 2 tasks × 5 experiments
│   │   ├── TL/                 #   3 EEGNet transfer-learning strategies
│   │   └── Baseline/           #   RF, SVR, XGBoost, LightGBM (feat15/feat78 × SMOTE)
│   └── personal/               #   Per-patient fine-tuned EEGNet checkpoints
├── reports/                    # Experiment outputs, figures, metrics (EDA, Regression, Tests, scoring)
├── Notebooks/                  # Exploratory analysis & prototyping
├── Tests/                      # Standalone evaluation scripts (ML / DL / TL comparison)
├── docker/                     # Docker Compose deployment
├── Feedback_METADATA/          # Feedback session metadata & media feature analysis
├── Assistant_rag/              # NeuroCoach RAG assistant (BM25 + semantic retrieval + LLM cascade)
├── integration-temporaire/     # Original standalone DSP/signal implementation (archived — merged into app/)
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
- Audit log on every login and every admin mutation
- RGPD-style consent flow (`/consent`) with a downloadable, personalised PDF before any session

### Patient Interface
- **Live EEG** — real-time signal stream from AD8232/ESP32 via WebSocket
- **EEG File** — upload and analyse recorded CSV/EDF/TXT sessions
- **Electrode Guide** — dedicated page: 10-20 system diagram, wiring schema, skin-prep protocol, pre-session checklist
- **15-Session Adaptive Protocol** — calibration → 15 guided neurofeedback sessions → per-session bilan, with adaptive difficulty (P1–P4 paliers) and early-stop / follow-up scheduling
- **Free Neurofeedback Sessions** — 3-phase session (setup → live session → report)
- **Adaptive Feedback Engine** — 5 feedback modalities (audio, image, video, brain-state indicator, mini-games), selection driven by Thompson Sampling stored in Supabase
- **Media Recommendations** — personalised playlists and offline recommendations based on session outcomes
- **History** — past sessions with metrics and reports
- **AI Assistant (NeuroCoach)** — RAG-powered chat for cognitive health guidance

### Clinical Interface (Therapist / Admin)
- Patient assignment and monitoring, protocol progress tracking
- Session notes and personalised recommendations (objective, weekly target, palier)
- Admin panel: user management, role assignments, system settings, audit logs

### ML & DSP Pipeline
- Bandpass 0.5–40 Hz + Notch 50 Hz + DWT (db4) denoising + epoch extraction (4 s, 75% overlap)
- Welch PSD, Hjorth, DWT sub-band and non-linear (entropy) features — 15-feature (embedded) and 78-feature (server) sets
- 19 deep learning architectures benchmarked (EEGNet, CNN, LSTM, GRU, BiLSTM, BiGRU, TCN, hybrids…)
- Transfer learning EEGNet (3 strategies: full fine-tuning, feature extraction, layer replacement)
- Baseline classifiers: SVR, Random Forest, XGBoost, LightGBM (feat15 / feat78 × sans/avec SMOTE)
- **Production models:** EEGNet DL FULL (concentration, AUC LOSO = 0.751) · EEGNet TL-LayerReplacement FULL (stress, AUC LOSO = 0.607, ⚠ conditional) — continuous 0–10 regression
- Nightly automated per-patient fine-tuning (APScheduler) of the EEGNet FC head

### Internationalisation
- Full i18n via react-i18next: **French**, **English**, **Arabic** (RTL support)
- Light / Dark / Auto theme with a CSS design-token system

---

## Repository Structure

> Exhaustive route lists, component inventories and per-file documentation live in the module-level READMEs — see [Documentation Map](#documentation-map). This section only shows the top-level shape of each module.

### `app/Backend/app/`

```
app/Backend/app/
├── main.py                     # FastAPI entry point + lifespan (EEG pipeline, WS, FT scheduler)
├── config.py                   # Centralised settings (loaded from .env)
├── core/                       # Supabase client singleton, JWT/bcrypt helpers
├── middleware/                 # CORS, rate limiting, brute-force guard
├── routes/                     # 13 routers — see app/Backend/README.md for the full endpoint list
│   ├── auth.py                 #   /api/auth
│   ├── sessions.py             #   /api/sessions
│   ├── Profile.py              #   /api/profile
│   ├── admin.py                #   /api/admin
│   ├── therapist.py            #   /api/therapist
│   ├── assistant.py            #   /api/assistant (RAG)
│   ├── eeg.py                  #   /api/eeg (live stream, file analysis, fine-tuning status)
│   ├── media.py                #   /api/media
│   ├── feedback.py             #   /api/feedback (+ WS /api/feedback/ws/{session_id})
│   ├── eeg_feedback.py         #   /api/eeg-feedback
│   ├── protocol.py             #   /api/protocol (15-session program)
│   ├── recommendations.py      #   media recommendations, playlists, patient dashboard, fine-tuning hooks
│   └── consent.py              #   /api/consent
├── schemas/                    # Pydantic request/response models
└── services/                   # DSP pipeline, fine-tuning, RAG, email, protocol, media, consent…
```

### `app/Frontend/src/`

```
app/Frontend/src/
├── components/                 # ~35 components — Layout, Brain3D, RAGChat, feedback/, neurofeedback/, eeg/
├── pages/                      # ~29 pages — see app/Frontend/README.md for the full list + routing table
├── stores/                     # Zustand global state (auth)
├── hooks/                      # Custom React hooks (useEEGWebSocket, …)
├── services/ · utils/ · lib/   # Axios API wrappers & shared utilities
├── i18n/locales/                # FR / EN / AR translation files
└── styles/                     # Tailwind config & design tokens
```

### `src/` — ML Research Pipeline

```
src/
├── data/
│   ├── validate_data/          # Raw-data integrity checks (step 1)
│   ├── scoring/                # Score attribution 0–10 (step 2)
│   ├── pipeline_fp2.py         # Full preprocessing pipeline (Fp2 electrode)
│   ├── pipeline_regression.py  # Regression coordinator (scoring → split → aug → features)
│   ├── features_extraction.py  # 15 lightweight features (embeddable, ESP32)
│   ├── feature_eng.py          # 78 advanced features (8 categories)
│   └── augmentation_eeg.py     # EEG augmentation (5 experiments A/B/C/D/FULL)
└── models/
    ├── baselines/               # SVR/RF/XGB/LGBM — feat15 & feat78 × SMOTE
    ├── deep_learning/           # 19 architectures + shared training engine
    ├── transfer_learning/       # 3 EEGNet TL strategies
    ├── compare/                 # Global ML/DL/TL comparison → final decision
    └── inference_engine.py      # Unified backend inference interface
```

**Deep learning architectures benchmarked (19):**
`EEGNet · CNN1D · CNN2D · CNN3D · CNN_LSTM_Att · CNN_GRU_Att · LSTM1L · LSTM2L · LSTM_ATT · BiLSTM1L · BiLSTM2L · BiLSTM_ATT · GRU1L · GRU2L · GRU_ATT · BiGRU1L · BiGRU2L · BiGRU_ATT · TCN`

### `models/` — Trained Artefacts

| Folder | Retained model(s) | AUC LOSO | Status |
|---|---|---|---|
| `Regression/DL/EEGNet/conc/` | EEGNet DL FULL | **0.751** | ✅ Production |
| `Regression/TL/EEGNet_LayerReplacement/stress/` | EEGNet TL-LR FULL | **0.607** | ⚠️ Conditional |
| `Regression/Baseline/feat78/` (+ `_smote/`) | LightGBM (conc 0.676) · RF (stress 0.668) | 0.668–0.676 | ML reference |
| `personal/` | `patient_{id8}_{task}_v{n}.pt` — EEGNet fine-tuned per patient | — | Nightly fine-tuning |

> **Production models:** `EEGNet_conc_FULL_best.pt` (concentration, AUC = 0.751) · `EEGNet_LR_stress_FULL_best.pt` (stress, AUC = 0.607) — continuous 0–10 regression, strict LOSO (Leave-One-Subject-Out) validation.

---

## Documentation Map

Every module has its own README with the level of detail that belongs there — this file only gives the big picture. No documentation lives inside `reports/`, `Rapport_PFE/`, or other report/output folders — those are generated artefacts, not source of truth.

| Area | File | Covers |
|---|---|---|
| **Backend** | [`app/Backend/README.md`](app/Backend/README.md) | Full API reference, service architecture, env vars, WebSocket protocol, fine-tuning |
| **Fine-tuning service** | [`app/Backend/app/services/finetune/README.md`](app/Backend/app/services/finetune/README.md) | Nightly EEGNet personalisation — triggers, activity rules, checkpoints |
| **Frontend** | [`app/Frontend/README.md`](app/Frontend/README.md) | Pages, components, routing table, role-based navigation, i18n, theming |
| **Database** | [`app/Database/README.md`](app/Database/README.md) | Supabase schema, tables, migrations, RLS |
| **Docker** | [`docker/README.md`](docker/README.md) | Docker Compose deployment |
| **ML pipeline (overview)** | [`src/README.md`](src/README.md) | End-to-end pipeline, execution order, final results |
| **Data processing** | [`src/data/README.md`](src/data/README.md) | Preprocessing, augmentation, feature extraction in detail |
| **Scoring** | [`src/data/scoring/README.md`](src/data/scoring/README.md) | 0–10 score attribution methodology |
| **Data validation** | [`src/data/validate_data/README.md`](src/data/validate_data/README.md) | Raw-dataset integrity checks |
| **Models** | [`src/models/README.md`](src/models/README.md) | Hyperparameters, all 19 DL architectures, TL strategies, final decision |
| **Datasets** | [`data/README.md`](data/README.md) | Raw/processed dataset layout |
| **Dataset validation figures** | [`data/Validate_datasets/README.md`](data/Validate_datasets/README.md) | Generated diagnostic figures |
| **Notebooks** | [`Notebooks/README.md`](Notebooks/README.md) | EDA notebook |
| **Tests** | [`Tests/README.md`](Tests/README.md) | Model evaluation & comparison scripts |
| **Legacy DSP/signal app** | [`integration-temporaire/backend-signal/README.md`](integration-temporaire/backend-signal/README.md), [`integration-temporaire/frontend-signal/README.md`](integration-temporaire/frontend-signal/README.md) | Original standalone implementation, now merged into `app/` |
| **Functional walkthrough (FR)** | [`ARCHITECTURE.md`](ARCHITECTURE.md) | User flows, roles, screens |
| **Full technical writeup (FR)** | [`DOCUMENTATION_APP.md`](DOCUMENTATION_APP.md) | Deep-dive reference for defense/demo prep |

---

## Roles & Users

| Role | Pages accessible | Description |
|---|---|---|
| **Patient** | Dashboard, Live EEG, EEG File, Electrode Guide, Protocol (15 sessions), Neurofeedback, Media Dashboard, History, Assistant, Profile | Performs adaptive neurofeedback sessions and free-form training |
| **Therapist** | Therapist dashboard, Patient detail, Profile | Monitors assigned patients, writes session notes, sets personalised recommendations and objectives |
| **Admin** | Admin dashboard, Admin panel, all routes | Full user management, role assignments, system settings, audit log review |

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
| `DEEPSEEK_API_KEY` | optional | DeepSeek API key — primary NeuroCoach LLM (paid, ~$0.14/M tokens) |
| `GROQ_API_KEY` / `GROQ_MODEL` | optional | Groq API key — free fallback LLM (Llama 3.3 70B, 14 400 req/day) |
| `LLM_MODEL` / `OLLAMA_URL` | optional | Local Ollama model/URL — final fallback for NeuroCoach (`mistral`, `http://localhost:11434`) |
| `REDIS_URL` | optional | Redis URL for cache (`redis://localhost:6379`) |

> ⚙️ If `SMTP_USER` is empty, the system runs in **dev mode**: the verification code is returned directly in the API response and displayed as a yellow banner on the registration page — no email setup needed for local development.
>
> ⚙️ The NeuroCoach assistant degrades gracefully: DeepSeek → Groq → local Ollama → structured fallback message. All three LLM keys are optional; leaving them empty runs everything on Ollama.

> **Never commit `.env` or service-role credentials to version control.**

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, Vite, Tailwind CSS 3, Zustand, Recharts, Three.js, i18next (FR/EN/AR) |
| **Backend** | FastAPI, Python 3.11+, Supabase (sync client + AsyncProxy), bcrypt, python-jose, APScheduler |
| **Database** | Supabase (PostgreSQL) |
| **Real-time** | WebSocket — EEG stream via FastAPI, TCP receiver for ESP32 |
| **Email** | Brevo SMTP (300 emails/day, free tier — transactional verification codes) |
| **ML / DSP** | PyTorch (EEGNet), NumPy, SciPy, MNE, PyWavelets, LightGBM, scikit-learn, XGBoost |
| **RAG Assistant** | BM25 keyword retrieval + Ollama embeddings (`nomic-embed-text`, 768d) for semantic search; LLM cascade DeepSeek → Groq (Llama 3.3 70B) → Ollama (Mistral, local) |
| **Hardware** | AD8232 ECG module + ESP32 (single-channel Fp2, 250 Hz) |
| **Deployment** | Docker Compose, Nginx (optional reverse proxy) |

---

## ML Pipeline

```
Raw EEG (AD8232 / ESP32 TCP stream  OR  CSV / EDF / TXT upload)
    │
    ▼  Golden Filter : HP 0.5 Hz · LP 40 Hz · Notch 50 Hz · DWT db4 débruitage
Cleaned signal @ 250 Hz
    │
    ▼  Epoch extraction : fenêtres 4 s (1000 samples), overlap 75 %
Epochs
    │
    ├──────────────── RECHERCHE (src/) ──────────────────────────────────────────
    │   ▼  Scoring 0–10 (CLA levels → conc_score · SAM40 scales.xls → stress_score)
    │   ▼  Augmentation 5 expériences (A/B/C/D/FULL : Noise·Scaling·Shift·DWT·MagWarp)
    │   ▼  Features : feat15 (15 features < 10 ms) · feat78 (78 features ~35 ms)
    │   ▼  Régression LOSO :
    │       ├── Baselines ML : SVR / RF / XGBoost / LightGBM (feat15 + feat78 × SMOTE)
    │       └── Deep Learning : 19 architectures (EEGNet, LSTM, GRU, BiGRU, CNN, TCN…)
    │                            + Transfer Learning EEGNet (3 stratégies TL)
    │
    └──────────────── PRODUCTION (app/Backend/) ─────────────────────────────────
        ▼  DualClassifier (EEGNet Conv2d, entrée brute 1000 samples)
            ├── Concentration : EEGNet DL FULL  → score 0–10  (AUC LOSO = 0.751)
            └── Stress        : EEGNet TL-LR FULL → score 0–10 (AUC LOSO = 0.607) ⚠ conditionnel
        │
        ▼  Normalisation sigmoid → scores 0–100 · seuil de décision 50
    État cognitif dominant  {concentration · stress · neutral}
        │
        ▼  Adaptive engine (paliers P1–P4, EWMA rolling)
        │
        ▼  Thompson Sampling → sélection modalité feedback optimale
    Neurofeedback temps réel  {audio · image · vidéo · brain-state · mini-jeu}
        │
        ▼  Rapport session + fine-tuning EEGNet personnalisé (nightly, APScheduler)
             patient_{id8}_{task}_v{n}.pt  →  modèle individuel (couche FC réentraînée)
```

---

## Security

| Practice | Detail |
|---|---|
| **Secrets** | All credentials in `.env`, never committed to git |
| **JWT** | Short-lived access tokens (30–60 min) + refresh tokens (7–30 days) |
| **Passwords** | bcrypt hashing · strength enforced client + server-side (8 chars, upper, lower, digit, special) |
| **Email verification** | 8-digit code with 10-minute TTL required at registration |
| **Brute-force guard** | Max 5 failed logins → 15-minute IP lockout |
| **Rate limiting** | 100 requests / 60 s per IP (configurable via `.env`) |
| **Service-role key** | `SUPABASE_SERVICE_ROLE_KEY` used server-side only, never sent to frontend |
| **CORS** | Strict origin whitelist in FastAPI middleware |
| **Role guards** | Every protected route enforces role via FastAPI `Depends` — zero client-side enforcement |
| **Soft delete** | Users deactivated (`is_active = false` / `deleted_at`), not permanently erased |
| **Consent** | RGPD-style consent PDF required before any session (`/api/consent`) |
| **Audit logs** | Admin mutations and login events logged with timestamp, user ID, and IP address |

> Generate a production secret key: `python -c "import secrets; print(secrets.token_hex(32))"`

---

## Repository Conventions

- Branch `main` — stable, deployable code
- PRs require at least one review before merge
- Secrets managed via `.env` (never committed)
- `eegenv/` and `app/Backend/venv/` excluded via `.gitignore`
- Commit style: `type(scope): description` (feat / fix / refactor / docs / chore)
- Documentation lives next to the code it describes, one README per module — no README files inside `reports/` or other generated-output folders

---

## Contributors

### Oumama Sendadi
**Signal Processing & Feedback System**

**Backend / DSP**
- **DSP pipeline** (`app/Backend/app/services/eeg/dsp/`) — bandpass/notch filters, epoch extraction, artifact detection & rejection, Welch PSD and DWT feature computation
- **Signal service** (`services/signal_processing.py`) — offline signal processing utilities
- **Feedback metadata** (`Feedback_METADATA/`) — media assets and metadata extraction from feedback sessions

**Frontend**
- **Neurofeedback components** (`app/Frontend/src/components/feedback/`, `neurofeedback/`) — all feedback modalities and the mini-games (`MemoryGame`, `PuzzleGame`, `SudokuGame`, `CalculGame`, `EnigmeGame`)

**Original implementation**
- `integration-temporaire/backend-signal/`, `integration-temporaire/frontend-signal/` — original standalone version, later merged into `app/`

### Yasmine El Mkhantar
**Full-stack Integration & ML Pipeline** — sole developer of the full-stack web application (`app/`), backend and frontend, detailed by layer below.

**Backend**
- **Web application backend** (`app/Backend/`) — FastAPI architecture, all REST routes, Supabase database integration
- **Authentication system** (`app/Backend/app/core/security.py`, `routes/auth.py`) — JWT auth (access + refresh tokens), email verification (Brevo SMTP), password strength validation, brute-force protection, audit logging, consent flow
- **EEGNet DualClassifier** (`app/Backend/app/services/eeg/dsp/dual_classifier.py`) — integration of trained EEGNet models (concentration AUC 0.751 · stress AUC 0.607), continuous 0–100 regression, sigmoid normalisation, nightly personal fine-tuning (APScheduler)
- **RAG assistant NeuroCoach — backend** (`Assistant_rag/`, `app/Backend/app/services/rag_service.py`) — semantic knowledge base, BM25 + Ollama embeddings, DeepSeek/Groq/Ollama LLM cascade, patient-context assembly, `/explain` endpoint
- **Protocol & recommendation engines** (`app/Backend/app/services/protocol_engine.py`, `media_recommendation.py`) — 15-session adaptive protocol engine, Thompson Sampling persisted in Supabase, media recommendation engine
- **Admin & audit system** (`app/Backend/app/routes/admin.py`) — user/role management, system settings, audit log

**Frontend**
- **React SPA** (`app/Frontend/`) — routing, pages, API integration
- **Dashboard & visualisations** (`DashboardPage.jsx`, `Brain3D.jsx`, `RecommendationEngine.jsx`, `TopoMap2D.jsx`) — Brain3D anatomy, simulation mode, recommendation engine, topographic map, real-time signal canvas
- **EEG selector & electrode guide** (`EEGSelector.jsx`, `ElectrodeGuide.jsx`) — preparation protocol, 10-20 schema, AD8232 wiring, pre-session checklist
- **Neurofeedback session UI** (`FeedbackPage.jsx`) — 3-phase session flow (setup → live → report)
- **Therapist space** (`TherapistDashboard.jsx`, `TherapistPatientDetail.jsx`) — URL-driven tabbed dashboard, patient sheet (EEG profile type A/B/C, paliers P1–P4), inactivity alerts, clinical notes, CSV export
- **Admin dashboard & panel** (`AdminDashboard.jsx`, `AdminPanel.jsx`) — global KPIs, user management, role assignment, audit log review
- **NeuroCoach chat UI** (`Assistant.jsx`, `RAGChat.jsx`) — chat interface, `/explain` integration
- **Internationalisation** (`src/i18n/`) — full FR / EN / AR, RTL layout, light/dark/auto theme

**ML Pipeline** (`src/`)
- **Data pipeline** — scoring 0–10 (CLA levels + SAM40 self-reports), subject-wise split, 5-experiment augmentation (A/B/C/D/FULL), feat15/feat78 feature extraction (8 categories)
- **Deep learning** — 19 architectures benchmarked (EEGNet, CNN, LSTM/GRU/BiLSTM/BiGRU variants, TCN, hybrids), shared training engine with strict LOSO validation
- **Transfer learning & evaluation** — 3 EEGNet transfer-learning strategies, shared 5-level metrics module (bootstrap CI, calibration, Decision Curve Analysis)

---

**Projet :** NeuroCap sous Easy Medical Device
