# NeuroCap — Adaptive EEG Neurofeedback System

> **AD8232 + ESP32 · Single-channel Fp2 · 250 Hz · CDC §2.5**

NeuroCap is a full-stack adaptive neurofeedback platform built for cognitive training (concentration & stress regulation). It combines real-time EEG signal processing, a machine-learning classifier, an adaptive protocol engine, and a role-based clinical web application.

---

## Architecture overview

```
NeuroCap/
├── app/                    # Full-stack web application
│   ├── Backend/            #   FastAPI async REST + WebSocket server
│   ├── Frontend/           #   React 18 SPA (Vite + Tailwind)
│   └── Database/           #   Supabase schema & SQL migrations
├── src/                    # ML pipeline (research → production)
│   ├── data/               #   Preprocessing & validation scripts
│   └── models/             #   Baselines, deep learning, transfer learning
├── data/                   # Raw & processed EEG datasets
│   ├── Dataset/            #   Concentration + Stress raw recordings
│   ├── Augmentation/       #   Augmented datasets
│   ├── Merge_datasets/     #   Merged training splits
│   └── Validate_datasets/  #   Holdout validation splits
├── features/               # Feature engineering (time/frequency/wavelet)
├── models/                 # Trained model artefacts (.pt / .pkl)
├── reports/                # Experiment outputs, figures, metrics
├── Notebooks/              # Exploratory analysis & prototyping
├── Tests/                  # Unit & integration tests
├── docker/                 # Docker Compose deployment
└── requirements.txt        # ML/data-science dependencies
```

---

## Roles & users

| Role | Access | Description |
|---|---|---|
| **Patient** | Dashboard, Session live, History, Assistant, Profile | Performs neurofeedback sessions |
| **Therapist** | Therapist dashboard, Patient detail, Profile | Monitors assigned patients, writes notes, sets recommendations |
| **Admin** | Admin dashboard, Admin panel, All routes | Full user management, assignments, audit logs |

---

## Quick start

### 1 — Backend (FastAPI)
```bash
cd app/Backend
python -m venv venv && venv\Scripts\activate   # Windows
pip install -r requirements.txt
cp .env.example .env                            # fill secrets
uvicorn app.main:app --reload --port 8001
```

### 2 — Frontend (React)
```bash
cd app/Frontend
npm install
npm run dev       # http://localhost:5173
```

### 3 — Docker (full stack)
```bash
docker compose -f docker/docker-compose.yml up --build
```

---

## Environment variables (Backend)

| Variable | Description |
|---|---|
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_KEY` | Supabase anon key |
| `SUPABASE_SERVICE_ROLE_KEY` | Service-role key (server-side only) |
| `SECRET_KEY` | JWT signing secret (change in production) |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name |
| `CLOUDINARY_API_KEY` | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret |

> **Never commit `.env` or service-role credentials to version control.**

---

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, Tailwind CSS 3, Zustand, Recharts, i18next (FR/EN/AR) |
| Backend | FastAPI, Python 3.11+, Supabase AsyncClient, bcrypt, python-jose |
| Database | Supabase (PostgreSQL) |
| Real-time | WebSocket (EEG stream via FastAPI) |
| ML / DSP | PyTorch, NumPy, SciPy, MNE, scikit-learn |
| Hardware | AD8232 ECG module + ESP32 (single-channel Fp2, 250 Hz) |
| Deployment | Docker Compose, Nginx (optional) |

---

## ML pipeline summary

```
Raw EEG (AD8232/CSV)
    ↓ Bandpass 1–45 Hz · Notch 50 Hz · Baseline correction
Cleaned signal
    ↓ Welch PSD · DWT · Statistical features
Feature matrix
    ↓ Baseline (RF/SVM/XGBoost) or Deep (EEGNet/CNN-LSTM/BiGRU)
Classification: concentration / stress / rest
    ↓ Adaptive engine (EWMA threshold, P1–P4 paliers)
Real-time feedback
```

Models are still under evaluation — benchmarks will be published after full test-set validation.

---

## Security

| Practice | Detail |
|---|---|
| **Secrets** | All credentials stored in `.env`, never committed to git |
| **JWT** | Short-lived access tokens (60 min) + refresh tokens (30 days) |
| **Passwords** | Hashed with bcrypt before storage, never stored in plain text |
| **Service-role key** | `SUPABASE_SERVICE_ROLE_KEY` used server-side only, never exposed to frontend |
| **CORS** | Strict origin whitelist configured in FastAPI middleware |
| **Role guards** | Every protected route checks role via FastAPI `Depends` — no client-side enforcement |
| **Soft delete** | Users are deactivated (`is_active=false`), not permanently erased |
| **Audit logs** | Sensitive admin actions logged with timestamp, user ID, and IP address |

> Change `SECRET_KEY` to a long random string before any production deployment (`openssl rand -hex 32`).

---

## Repository conventions

- Branch `main` — stable production code  
- PRs require at least one review before merge  
- Secrets managed via `.env` (never committed)  
- `eegenv/` and `app/Backend/venv/` are excluded from git via `.gitignore`
