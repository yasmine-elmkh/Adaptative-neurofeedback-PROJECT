# NeuroCap — Plateforme de Neurofeedback EEG Adaptatif

> Application full-stack temps réel pour l'entraînement cognitif par neurofeedback EEG, avec classification IA, moteur adaptatif, visualisation 3D et assistant RAG.

---

## Table des matières

1. [Architecture générale](#architecture-générale)
2. [Stack technologique](#stack-technologique)
3. [Structure du projet](#structure-du-projet)
4. [Backend (FastAPI)](#backend-fastapi)
5. [Frontend (React + Vite)](#frontend-react--vite)
6. [Pipeline temps réel](#pipeline-temps-réel)
7. [Installation & déploiement](#installation--déploiement)
8. [Configuration](#configuration)
9. [Sécurité](#sécurité)
10. [Tests](#tests)

---

## Architecture générale

```
┌─────────────────┐     ┌──────────────────────────────────────────────┐
│  Casque EEG     │     │              Backend FastAPI                 │
│  (simulateur    │────▶│                                              │
│   ou AD8232)    │     │  ┌─────────┐  ┌──────────┐  ┌───────────┐  │
└─────────────────┘     │  │ Signal  │─▶│ Features │─▶│ Classifier│  │
                        │  │ Process │  │ Extract  │  │ (EEGNet)  │  │
                        │  └─────────┘  └──────────┘  └─────┬─────┘  │
                        │                                     │        │
                        │  ┌──────────┐  ┌──────────────┐    ▼        │
                        │  │ Adaptive │◀─│  P(conc),    │────┘        │
                        │  │ Engine   │  │  P(stress)   │             │
                        │  └────┬─────┘  └──────────────┘             │
                        │       │                                      │
                        │       ▼  WebSocket (500ms)                   │
                        └───────┬──────────────────────────────────────┘
                                │
                ┌───────────────▼───────────────────┐
                │        Frontend React              │
                │                                    │
                │  ┌──────────┐ ┌────────────────┐  │
                │  │ Dashboard│ │  Session Live   │  │
                │  │ History  │ │  - Feedback     │  │
                │  │ Profile  │ │  - Brain 3D     │  │
                │  │ Assistant│ │  - TopoMap 2D   │  │
                │  └──────────┘ │  - Charts       │  │
                │               └────────────────┘  │
                └────────────────────────────────────┘
                                │
         ┌──────────────────────┼──────────────────────┐
         │                      │                       │
    PostgreSQL             Redis (cache)          ChromaDB (RAG)
```

## Stack technologique

| Couche | Technologies |
|--------|-------------|
| **Backend** | Python 3.11, FastAPI, SQLAlchemy 2.0, asyncpg, PyTorch, SciPy |
| **Frontend** | React 18, Vite, Tailwind CSS, Zustand, Recharts, Three.js (R3F) |
| **Base de données** | PostgreSQL 15, Redis 7 |
| **IA / ML** | EEGNet (PyTorch), Butterworth filters, Welch PSD, EWMA |
| **RAG** | ChromaDB, Ollama (mistral:7b) ou Claude API |
| **Infra** | Docker Compose, Nginx (reverse proxy) |

## Structure du projet

```
neurocap-platform/
├── docker-compose.yml          # Orchestration des services
├── .env.example                # Variables d'environnement
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py             # Point d'entrée FastAPI + lifespan
│       ├── core/
│       │   ├── config.py       # Pydantic Settings (env vars)
│       │   ├── database.py     # Async SQLAlchemy engine
│       │   └── security.py     # JWT + bcrypt + dependencies
│       ├── models/
│       │   └── user.py         # ORM: User, EEGProfile, Session, SessionEvent, AuditLog
│       ├── schemas/
│       │   └── __init__.py     # Pydantic: request/response validation
│       ├── api/routes/
│       │   ├── auth.py         # /auth/register, /login, /refresh, /me
│       │   ├── profile.py      # /profile/me, /profile/calibration
│       │   ├── sessions.py     # /sessions, /sessions/{id}/report, /export
│       │   ├── assistant.py    # /assistant/ask (RAG)
│       │   └── admin.py        # /admin/users, /admin/stats
│       ├── services/
│       │   ├── eeg_source.py       # EEGSource ABC + SimulatorSource + SerialSource
│       │   ├── signal_processing.py # Butterworth + Notch + Z-score + Features
│       │   ├── classifier.py       # EEGNetLite + AIClassifier (thread-safe)
│       │   ├── adaptive_engine.py  # EWMA + Mou et al. rules + paliers
│       │   └── rag_assistant.py    # ChromaDB + Ollama/Claude
│       └── websocket/
│           └── session_ws.py   # Pipeline temps réel (500ms loop)
│
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── vite.config.js
    ├── tailwind.config.js
    ├── index.html
    └── src/
        ├── main.jsx            # React entry point
        ├── App.jsx             # BrowserRouter + AuthGuard
        ├── styles/globals.css  # Tailwind + glass-card + btn-primary
        ├── utils/api.js        # API client (REST + WebSocket)
        ├── stores/index.js     # Zustand: useAuthStore + useSessionStore
        ├── components/
        │   ├── Layout.jsx          # Sidebar navigation
        │   ├── EEGGauge.jsx        # SVG circular gauge
        │   ├── SignalQuality.jsx   # Signal quality bars
        │   ├── FeedbackRenderer.jsx # Visual + Sound + Game feedback
        │   ├── RAGChat.jsx         # Reusable chat component
        │   ├── Brain3D.jsx         # Three.js 3D brain
        │   └── TopoMap2D.jsx       # Canvas 2D topographic heatmap
        └── pages/
            ├── Login.jsx
            ├── Register.jsx
            ├── Dashboard.jsx
            ├── SessionLive.jsx
            ├── History.jsx
            ├── SessionDetail.jsx
            ├── Assistant.jsx
            └── Profile.jsx
```

## Backend (FastAPI)

### Modèles de données (SQLAlchemy ORM)

**5 tables principales** avec UUIDs, timestamps, et relations cascadées :

- **User** — email, password_hash (bcrypt), role (user/admin)
- **EEGProfile** — iapf, alpha_power_ref, theta_beta_ratio_ref, reactivity_score, profile_type (A/B/C), palier (P1→P4), thresholds (JSON)
- **Session** — session_number, status (11 états FSM), feedback_mode, scores, durée
- **SessionEvent** — séries temporelles (concentration, stress, threshold, alpha, TBR, qualité)
- **AuditLog** — journalisation des accès sensibles

### API REST (6 routeurs, 12 endpoints)

| Route | Méthode | Description |
|-------|---------|-------------|
| `/api/auth/register` | POST | Inscription → JWT + refresh |
| `/api/auth/login` | POST | Connexion → JWT + refresh |
| `/api/auth/refresh` | POST | Renouvellement du token |
| `/api/auth/me` | GET | Infos utilisateur |
| `/api/profile/me` | GET | Profil EEG complet |
| `/api/profile/calibration` | POST | Calibration S1 → IAPF, type, seuils |
| `/api/sessions` | GET/POST | Liste / création de session |
| `/api/sessions/{id}/report` | GET | Rapport (timelines + recommandations) |
| `/api/sessions/{id}/export` | GET | Export CSV des événements |
| `/api/assistant/ask` | POST | Question RAG + contexte session |
| `/api/admin/users` | GET | Liste utilisateurs (admin) |
| `/api/admin/stats` | GET | Statistiques globales (admin) |

### Services métier

#### EEG Source (Pattern Factory)
```python
# Interface abstraite
class EEGSource(ABC):
    def read_window(self) -> np.ndarray: ...
    def get_signal_quality(self) -> float: ...

# Implémentations
SimulatorSource  # Alpha + beta + theta + bruit rose + artefacts
SerialSource     # Port série (AD8232 + ESP32)
```

#### Signal Processing
- Butterworth 4ème ordre (0.5–80 Hz)
- Notch 50 Hz (réseau électrique)
- Normalisation Z-score
- Features spectrales : PSD (Welch), 5 bandes (δ θ α β γ)
- Ratios : TBR, alpha/theta, engagement index
- IAPF (pic alpha individuel)
- Paramètres de Hjorth (activité, mobilité, complexité)
- Statistiques (kurtosis, skewness, RMS)

#### Classifier (EEGNetLite)
Architecture EEGNet légère (PyTorch) :
1. Conv temporelle (1×64)
2. Depthwise conv
3. Separable conv (dw + pw)
4. FC → 2 classes [P(concentration), P(stress)]

Inférence thread-safe via `asyncio.to_thread()` + `threading.Lock`.

#### Moteur adaptatif (Mou et al. 2024)
- EWMA : `α̂[t] = 0.3 × α_raw + 0.7 × α̂[t-1]`
- Seuil inter-blocs (3 min) : >60% succès → +0.5%, <40% → -0.5%
- Seuil inter-sessions : `threshold_day = 0.7 × global_ref + 0.3 × short_ref`
- 4 paliers progressifs (P1→P4) avec multiplicateurs de difficulté

#### Assistant RAG
- Vector store : ChromaDB (cosine similarity)
- 10 documents de base (protocole, FAQ, techniques)
- Enrichissement contextuel (métriques session)
- Génération : Ollama (mistral:7b) ou Claude API
- Prompt système strict : pas de diagnostic médical

### WebSocket (Pipeline temps réel)

Boucle toutes les 500ms :
```
EEG Source → Preprocess → Features → IA Classification → Adaptive Update → Feedback → WebSocket → DB
```

Frame JSON envoyée :
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "concentration": 0.72,
  "stress": 0.28,
  "features": { "alpha": 12.4, "theta_beta_ratio": 0.65, "engagement_index": 0.81, "iapf": 10.2 },
  "threshold": 0.68,
  "feedback_command": { "type": "visual", "intensity": 0.7, "is_success": true },
  "signal_quality": 0.92,
  "block_number": 3,
  "block_time_sec": 120.5,
  "ewma": 0.71,
  "success_rate": 0.65
}
```

## Frontend (React + Vite)

### Design system

Palette **"Neuro Dark"** (Tailwind custom) :
- Background : `#0a0e1a`
- Surface : `#111827`
- Card : `#1a2236` (glass effect avec backdrop-blur)
- Accent : `#00d4ff` (cyan)
- Success/Warning/Danger : vert/ambre/rouge

Classes utilitaires : `glass-card`, `btn-primary`, `btn-ghost`, `input-field`

### Pages

1. **Login/Register** — Split layout, validation, stockage JWT
2. **Dashboard** — Stats cards, DualGauge, AreaChart progression, sessions récentes, mini RAG chat
3. **Session Live** — WebSocket, 3 modes feedback, Brain3D/TopoMap2D, chart temps réel, contrôles
4. **Historique** — Table filtrable (recherche + mode), navigation vers détail
5. **Détail session** — Rapport complet, timelines, recommandations, export CSV
6. **Assistant** — Chat RAG plein écran
7. **Profil** — Type A/B/C, métriques EEG, progression paliers, recalibration

### Composants réutilisables

| Composant | Description |
|-----------|-------------|
| `EEGGauge` | Jauge SVG circulaire animée |
| `DualGauge` | Concentration + Stress côte à côte |
| `SignalQuality` | Barres de qualité signal (5 niveaux) |
| `VisualFeedback` | Orbe coloré (hue proportionnel) avec glow |
| `SoundFeedback` | Web Audio API, fréquence proportionnelle |
| `GameFeedback` | Canvas ball-game (maintenir au-dessus du seuil) |
| `Brain3D` | Three.js : hémisphères, zone préfrontale, connectome, particules |
| `TopoMap2D` | Canvas 2D : heatmap IDW, électrodes 10-20, légende couleurs |
| `RAGChat` | Chat (compact/full), historique, sources |
| `Layout` | Sidebar collapsible, navigation, user section |

### State management (Zustand)

- `useAuthStore` — user, token, fetchUser, logout
- `useSessionStore` — WebSocket, frame live, history buffer, pause/resume, feedback mode

## Installation & déploiement

### Prérequis

- Docker & Docker Compose
- Node.js 18+ (dev local frontend)
- Python 3.11+ (dev local backend)

### Lancement rapide (Docker)

```bash
# 1. Cloner et configurer
cp .env.example .env
# Éditer .env avec vos secrets

# 2. Démarrer
docker compose up -d

# 3. Accéder
# Frontend : http://localhost:5173
# Backend :  http://localhost:8000
# API docs : http://localhost:8000/docs
```

### Développement local

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (nouveau terminal)
cd frontend
npm install
npm run dev
```

## Configuration

Toutes les variables dans `.env` :

| Variable | Défaut | Description |
|----------|--------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://...` | Connexion PostgreSQL |
| `REDIS_URL` | `redis://localhost:6379` | Cache Redis |
| `JWT_SECRET_KEY` | `change-me` | Secret JWT (64 chars en prod) |
| `MODEL_PATH` | `models/eegnet_best.pt` | Chemin du modèle IA |
| `EEG_SOURCE_TYPE` | `simulator` | `simulator` ou `serial` |
| `RAG_MODE` | `local` | `local` (Ollama) ou `claude` |
| `CLAUDE_API_KEY` | — | Clé API Claude (si RAG_MODE=claude) |
| `CORS_ORIGINS` | `localhost:5173,3000` | Origines CORS autorisées |

## Sécurité

- **Authentification** : JWT (access + refresh tokens) via bcrypt
- **Autorisation** : Role-based (user/admin) avec dependencies FastAPI
- **Données** : Séparation stricte User ↔ EEGProfile (user_id non réversible)
- **Audit** : Journalisation des accès (table `audit_logs`)
- **CORS** : Whitelist configurable
- **Transport** : HTTPS/WSS en production (reverse proxy Nginx/Caddy)
- **WebSocket** : Authentification JWT via query parameter

## Tests

### Critères d'acceptation

1. **Latence** : Pipeline complet < 500ms (preprocess + inference + WebSocket)
2. **Concurrence** : 10 clients WebSocket simultanés sans perte
3. **RAG** : Réponses cohérentes sur les questions du protocole
4. **3D** : 60 FPS sur laptop standard
5. **Sécurité** : Isolation des données EEG entre utilisateurs
6. **Responsive** : Interface fonctionnelle sur mobile et desktop

---

**NeuroCap** — Développé dans le cadre d'un projet de recherche en neurofeedback EEG adaptatif.