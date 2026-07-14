# NeuroCap Frontend — React 18 + Vite + Tailwind

SPA for the NeuroCap EEG neurofeedback platform: real-time oscilloscope, offline EEG file analysis, 15-session adaptive protocol, free neurofeedback sessions, media recommendations, patient dashboard, therapist workspace, administration, NeuroCoach RAG assistant.

---

## Table of Contents

1. [Contributors](#contributors)
2. [Stack](#stack)
3. [Project Structure](#project-structure)
4. [Installation](#installation)
5. [Vite Proxy](#vite-proxy)
6. [Routing](#routing)
7. [Navigation by Role](#navigation-by-role)
8. [Pages](#pages)
9. [Components](#components)
10. [Theme](#theme)
11. [Internationalisation](#internationalisation)
12. [EEG WebSocket Hook](#eeg-websocket-hook--useeegwebsocketjs)

---

## Contributors

| Area | Author | Scope |
|------|--------|-------|
| **Signal components** (`components/eeg/`) | **Oumama Sendadi** | Original implementation in `integration-temporaire/frontend-signal/`: SignalCanvas (oscilloscope), BandBars (spectral power), WiFi setup, calibration overlay, feature panel. |
| **Feedback & neurofeedback components** (`components/feedback/`, `components/neurofeedback/`) | **Oumama Sendadi** | All feedback modalities, mini-games, session block timer, media zone, breathing/fixation/calibration steps. |
| **Application shell, routing, all other pages & API integration** | **Yasmine El Mkhantar** | Dashboard, EEG pages, protocol, admin/therapist workspaces, consent, media dashboard, auth store, `api.js`, Layout, ThemeContext, i18n. |

---

## Stack

| Technology | Version | Role |
|---|---|---|
| React | 18 | UI framework |
| Vite | 5 | Build tool + dev server |
| Tailwind CSS | 3 | Utility-first styling |
| React Router | 6 | Client-side routing |
| Zustand | 4 | Global state (auth) |
| Axios | 1 | HTTP client |
| Recharts | 2 | Charts (AreaChart, BarChart, PieChart, RadialBar) |
| Three.js | latest | Brain3D anatomy visualisation |
| i18next | latest | i18n (FR / EN / AR + RTL) |
| Lucide React | latest | Icons |

---

## Project Structure

```
app/Frontend/
├── public/
│   ├── NeuroCap_Logo.png
│   ├── favicon.svg
│   └── video/Brain.mp4
├── src/
│   ├── components/            # ~35 components — see Components below
│   ├── context/ThemeContext.jsx
│   ├── hooks/useEEGWebSocket.js
│   ├── i18n/                  # fr.json, en.json, ar.json
│   ├── pages/                 # ~29 pages — see Pages below
│   ├── stores/authStore.js    # Zustand: token, user, login, logout
│   ├── styles/                # Tailwind config & CSS design tokens
│   └── utils/api.js           # Axios instance + all API helpers (eeg.*, auth.*, protocol.*, …)
├── index.html
├── vite.config.js             # Proxy /api → 8001, /ws → 8001
├── tailwind.config.js
└── package.json
```

---

## Installation

```bash
npm install
npm run dev       # http://localhost:5173
npm run build     # production build → dist/
npm run preview   # preview the build
```

---

## Vite Proxy

All `/api/*` and `/ws/*` requests are proxied to the backend:

```js
// vite.config.js
proxy: {
  '/api': 'http://localhost:8001',
  '/ws':  { target: 'ws://localhost:8001', ws: true },
}
```

---

## Routing

```
/                        → Landing (public)
/login                   → Login (public, redirects if authenticated)
/register                → Register (public)
/consent                 → ConsentPage (private, required before any session — ConsentGuard)

── Inside Layout + ConsentGuard ──────────────────────────────────────────────
/dashboard                → DashboardPage (patient) · AdminDashboard (admin) · TherapistDashboard (therapist)
/history, /history/:id    → History
/assistant                → Assistant (NeuroCoach RAG chat)
/profile                  → Profile (role-aware)

/eeg, /eeg/live, /eeg-live       → EEGPage (tab="live") — embeds EEGLive
/eeg/upload, /eeg-file           → EEGPage (tab="upload") — embeds EEGFile
/electrode-guide                  → ElectrodeGuide

/feedback                 → FeedbackPage (free-mode session setup)
/feedback/session         → FeedbackSession
/eeg-feedback              → EEGFeedbackMode

/protocol                          → ProtocolDashboard (15-session program)
/protocol/calibration              → CalibrationSession
/protocol/entry/:n                 → SessionEntry
/protocol/session/:n               → ProtocolSession
/protocol/bilan/:n                 → ProtocolBilan

/session/setup             → SessionSetup
/neurofeedback              → NeurofeedbackSession
/media-dashboard             → PatientMediaDashboard

/admin                     → AdminPanel (admin only)
/therapist                 → TherapistDashboard (therapist/admin)
/therapist/patient/:id     → TherapistPatientDetail

*                          → redirect to /
```

> `pages/EEGSelector.jsx`, `pages/SessionPage.jsx` and `pages/SessionLive.jsx` exist on disk but are not currently wired into any route — kept for reference, not dead code to be surprised by if you go looking for them.

---

## Navigation by Role

| Link | Patient | Therapist | Admin |
|---|---|---|---|
| Dashboard | ✅ | ✅ | ✅ |
| EEG (live / file) | ✅ | ❌ | ❌ |
| Electrode guide | ✅ | ❌ | ❌ |
| Protocol (15 sessions) / Neurofeedback / Feedback | ✅ | ❌ | ❌ |
| Media dashboard | ✅ | ❌ | ❌ |
| Assistant (NeuroCoach) | ✅ | ❌ | ❌ |
| My patients (therapist dashboard) | ❌ | ✅ | ❌ |
| Administration | ❌ | ❌ | ✅ |
| Profile | ✅ | ✅ | ✅ |

---

## Pages

### Patient — EEG & sessions
| Page | Description |
|---|---|
| `DashboardPage.jsx` | Patient dashboard: stat cards, AreaChart of recent activity, latest EEG reports and sessions. Empty-state CTA when there's no data yet. |
| `EEGPage.jsx` | Tab container — embeds `EEGLive` and `EEGFile` as `live` / `upload` tabs. |
| `EEGLive.jsx` | Real-time oscilloscope via `useEEGWebSocket`. ESP32 WiFi scan/config/reconnect, baseline acquisition, CSV recording, live electrode quality and spectral bands. |
| `EEGFile.jsx` | Upload `.edf` / `.csv` / `.txt`. Calls `POST /api/eeg/analyze_file` → EEGNet results (dominant state, epoch distribution, confidence). Auto-saves the report for the therapist and stores high-confidence epochs for fine-tuning. |
| `ElectrodeGuide.jsx` | 10-20 system diagram, skin-prep protocol, signal FAQ, RGPD-style consent reminder before sessions. |

### Patient — Protocol & neurofeedback
| Page | Description |
|---|---|
| `ConsentPage.jsx` | Consent acceptance step — blocks all other routes via `ConsentGuard` until accepted. |
| `ProtocolDashboard.jsx` | Entry point to the 15-session adaptive protocol — status, calendar, next session. |
| `CalibrationSession.jsx` | Session-1 calibration flow (IAPF, ERD, TBR → cognitive profile A/B/C). |
| `SessionEntry.jsx` | Pre-session checklist/entry point for protocol session *n*. |
| `ProtocolSession.jsx` | Guided protocol session *n* — adaptive blocks, live feedback. |
| `ProtocolBilan.jsx` | Post-session bilan report for session *n*. |
| `FeedbackPage.jsx` | Free-mode (non-protocol) neurofeedback session setup. |
| `FeedbackSession.jsx` | Free-mode live session runner (media + feedback modality selection). |
| `EEGFeedbackMode.jsx` | Free EEG-feedback mode, outside the 15-session protocol. |
| `SessionSetup.jsx` / `NeurofeedbackSession.jsx` | Session parameter setup and live neurofeedback runner. |
| `PatientMediaDashboard.jsx` | Personalised media recommendations, playlists, offline suggestions. |

### Shared & clinical
| Page | Description |
|---|---|
| `History.jsx` | Session history and reports. |
| `Assistant.jsx` | NeuroCoach RAG chat (cognitive-health guidance). |
| `Profile.jsx` | Role-aware: **Patient** — cognitive type A/B/C (α/β ratio + ERD), EEG metrics, palier P1–P4, fine-tuning activity status. **Therapist/Admin** — account info + password change. |
| `TherapistDashboard.jsx` | KPIs, assigned patients, protocol progress, inactivity alerts. |
| `TherapistPatientDetail.jsx` | 4 tabs: Overview (EEG profile + score chart), Sessions, EEG Reports, Actions (objective, palier, activation) + clinical notes. |
| `AdminDashboard.jsx` | Global KPIs, Recharts (roles donut, sessions bar, engagement radial), searchable/filterable user table. |
| `AdminPanel.jsx` | User & role management, patient assignment, system settings, audit logs. |
| `Landing.jsx` / `Login.jsx` / `Register.jsx` | Public pages — landing, login (distinct email/password errors), registration (email verification + password strength checklist). |

---

## Components

```
components/
├── Layout.jsx                 # Sticky navbar + mobile drawer + bottom nav, role-aware
├── ProtectedRoute.jsx          # Role-based route guard
├── Brain3D.jsx                 # 3-D brain anatomy visualisation (Three.js)
├── EEGVisualization.jsx / EEGGauge.jsx / SignalQuality.jsx / TopoMap2D.jsx
├── RAGChat.jsx                 # Embedded NeuroCoach chat widget
├── RecommendationEngine.jsx    # AI-driven session recommendations
├── GaugeChart.jsx / LineChart.jsx / SessionCalendar.jsx / UserFormModal.jsx / BiofeedbackGame.jsx / FeedbackRenderer.jsx
├── eeg/
│   ├── SignalCanvas.jsx        # Real-time oscilloscope canvas
│   ├── BandBars.jsx            # Frequency band power bars
│   ├── CalibrationOverlay.jsx  # Calibration step overlay
│   ├── FeaturesPanel.jsx       # Live DSP feature panel
│   └── WifiSetupCard.jsx       # ESP32 WiFi configuration card
├── feedback/                   # ── 5 feedback modalities + session UI ──
│   ├── AudioFeedback.jsx / ImageFeedback.jsx / VideoFeedback.jsx / BrainStateIndicator.jsx / GameFeedback.jsx
│   ├── FeedbackSelector.jsx / FeedbackJustification.jsx / FeedbackReport.jsx / MediaZone.jsx / MediaNeuroscienceGuide.jsx
│   ├── SessionBlockTimer.jsx / MiniEEGOscilloscope.jsx / BreathingGuide.jsx / FocusPoint.jsx / UserFeedbackBar.jsx
│   └── games/                  # MemoryGame, PuzzleGame, SudokuGame, CalculGame, EnigmeGame
└── neurofeedback/
    ├── CalibrationStep.jsx / BreathingStep.jsx / FixationStep.jsx
```

---

## Theme

3 modes: `auto` (system), `light`, `dark`. Managed via `ThemeContext`, toggled from the navbar. CSS design tokens (`--nc-bg`, `--nc-accent`, `--nc-surface`, …) defined in `src/styles/`.

---

## Internationalisation

Languages: **French** (default), **English**, **العربية** (RTL). Translation files in `src/i18n/{fr,en,ar}.json`. Language persisted in `localStorage`.

---

## EEG WebSocket Hook — `useEEGWebSocket.js`

Manages the `/ws/eeg` WebSocket connection with automatic reconnection. Exposes:
- `signal` — sample buffer for the oscilloscope
- `epoch` — latest classified epoch (state, confidence, features)
- `electrode` — contact quality
- `esp32` — connection state + IP
- `send(cmd)` — send commands (`FINALISE_BASELINE`, `START_REC`, …)
