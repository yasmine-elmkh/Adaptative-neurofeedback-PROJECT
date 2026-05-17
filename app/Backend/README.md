# NeuroCap Backend — FastAPI + Supabase

Async REST API + WebSocket server for the NeuroCap adaptive neurofeedback platform.

---

## Stack

| Component | Technology |
|---|---|
| Framework | FastAPI 0.115+ (async) |
| Database | Supabase (PostgreSQL via `supabase-py` AsyncClient) |
| Auth | JWT (python-jose) + bcrypt password hashing |
| Real-time | WebSocket (`/ws/session/{id}`) |
| Signal DSP | NumPy, SciPy |
| ML inference | PyTorch (CNN-LSTM classifier) |
| RAG assistant | Ollama (local LLM) + SQLite vector store |
| Config | python-dotenv + pydantic-settings |

---

## Project structure

```
app/Backend/
├── app/
│   ├── main.py              # FastAPI app entry point + WebSocket EEG handler
│   ├── config.py            # Settings (env vars via pydantic-settings)
│   ├── database.py          # Supabase AsyncClient factory
│   ├── core/
│   │   ├── config.py        # Centralised settings
│   │   ├── database.py      # get_db dependency
│   │   └── security.py      # JWT helpers, bcrypt, FastAPI deps
│   ├── middleware/
│   │   └── security.py      # CORS, rate limiting, brute-force protection
│   ├── models/              # SQLAlchemy ORM models (legacy, kept for reference)
│   ├── routes/
│   │   ├── auth.py          # POST /register, /login, /refresh, /me, /change-password
│   │   ├── sessions.py      # CRUD sessions + EEG report + CSV export
│   │   ├── Profile.py       # GET/POST /profile/me, /calibration
│   │   ├── admin.py         # Admin: users, assignments, settings, audit logs
│   │   ├── therapist.py     # Therapist: patients, notes, recommendations, palier
│   │   └── assistant.py     # RAG chatbot endpoint
│   ├── schemas/
│   │   └── __init__.py      # All Pydantic request/response models
│   └── services/
│       ├── signal_processing.py   # Bandpass, Welch PSD, feature extraction
│       ├── classifieur.py         # CNN-LSTM inference wrapper
│       ├── adaptative_engine.py   # EWMA adaptive threshold + palier logic
│       └── rag_service.py         # Ollama RAG assistant (local LLM)
├── requirements.txt
└── .env.example
```

---

## Setup

```bash
# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux / macOS

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env — see variables below

# 4. Start server
uvicorn app.main:app --reload --port 8001
```

---

## Environment variables

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key   # server-side only, never expose

# JWT
SECRET_KEY=change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

# Cloudinary (avatar / media)
CLOUDINARY_CLOUD_NAME=your-cloud
CLOUDINARY_API_KEY=your-key
CLOUDINARY_API_SECRET=your-secret
```

---

## API reference (main routes)

### Authentication — `/api/auth`
| Method | Path | Description |
|---|---|---|
| POST | `/register` | Register new user, returns tokens |
| POST | `/login` | Login, returns access + refresh token |
| POST | `/refresh` | Renew access token via refresh token |
| GET | `/me` | Current user profile |
| POST | `/change-password` | Change own password (requires current password) |

### Sessions — `/api/sessions`
| Method | Path | Description |
|---|---|---|
| GET | `/sessions` | List user sessions |
| POST | `/sessions` | Create new session |
| GET | `/sessions/{id}/report` | Full session report |
| GET | `/sessions/{id}/export` | Export CSV |
| GET | `/sessions/export/all` | Export all sessions CSV |

### Therapist — `/api/therapist`
| Method | Path | Description |
|---|---|---|
| GET | `/patients` | List assigned patients (enriched) |
| GET | `/patients/{id}` | Patient detail + stats |
| GET | `/patients/{id}/sessions` | Patient session history |
| GET | `/patients/{id}/profile` | EEG profile (read-only) |
| GET/POST | `/patients/{id}/notes` | Private clinical notes |
| GET/POST | `/patients/{id}/recommendation` | Objective & weekly target |
| PUT | `/patients/{id}/palier` | Adjust difficulty level (P1–P4) |
| PATCH | `/patients/{id}/active` | Toggle account active status |
| GET | `/patients/{id}/export` | Export patient CSV |

### Admin — `/api/admin`
| Method | Path | Description |
|---|---|---|
| GET | `/stats` | Global KPIs |
| GET/POST | `/users` | List + create users |
| GET/PUT/DELETE | `/users/{id}` | Get, update, soft/hard delete |
| POST | `/assign-patient` | Assign patient to therapist |
| GET/PUT | `/settings/{key}` | System settings |
| GET | `/audit-logs` | Filtered audit trail |

### WebSocket — `ws://host/ws/session/{id}?token=<jwt>`

Real-time EEG stream. Client sends `{"samples": [float × 1000]}` every 4 s;  
server returns `WSFrame` JSON with concentration, stress, feedback, threshold, block info.

---

## Role access matrix

| Route group | Patient | Therapist | Admin |
|---|---|---|---|
| `/api/auth/*` | ✅ | ✅ | ✅ |
| `/api/sessions/*` | ✅ | ❌ | ❌ |
| `/api/profile/*` | ✅ | ❌ | ❌ |
| `/api/therapist/*` | ❌ | ✅ | ✅ |
| `/api/admin/*` | ❌ | ❌ | ✅ |
| `/ws/session/*` | ✅ | ❌ | ❌ |

---

## Supabase tables required

```sql
users               -- id, email, username, first_name, last_name, role, is_active,
                    --   hashed_password, therapist_id, deleted_at, created_at
sessions            -- id, user_id, objective, feedback_mode, status, score, ...
session_events      -- id, session_id, concentration_rate, stress_rate, tbr, ...
eeg_profiles        -- id, user_id, profile_type, iapf, palier, reactivity_score, ...
therapist_notes     -- id, therapist_id, patient_id, content, created_at
therapist_recommendations -- id, therapist_id, patient_id, recommended_objective, ...
audit_logs          -- id, user_id, action, details, ip_address, created_at
system_settings     -- key, value, description, updated_at
```

> SQL migrations are in `app/Database/`.
