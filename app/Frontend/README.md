# NeuroCap Frontend — React 18 + Vite + Tailwind

Single-page application for the NeuroCap neurofeedback platform, built with React 18, Vite 5, and Tailwind CSS 3.

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
| Recharts | 2 | Charts (BarChart, LineChart, PieChart, RadialBar) |
| i18next | latest | Internationalisation (FR / EN / AR + RTL) |
| Lucide React | latest | Icon system |

---

## Project structure

```
app/Frontend/
├── public/
│   └── video/               # Background media assets
├── src/
│   ├── assets/              # Static images, logos
│   ├── components/
│   │   ├── Layout.jsx       # Sticky navbar, mobile drawer, footer, bottom nav
│   │   ├── UserFormModal.jsx# Create / edit user modal (admin)
│   │   ├── Brain3D.jsx      # 3D brain visualisation
│   │   ├── EEGGauge.jsx     # Real-time EEG gauge
│   │   ├── EEGVisualization.jsx
│   │   ├── FeedbackRenderer.jsx
│   │   ├── GaugeChart.jsx
│   │   ├── RecommendationEngine.jsx
│   │   ├── SignalQuality.jsx
│   │   └── TopoMap2D.jsx
│   ├── context/
│   │   └── ThemeContext.jsx  # Dark / light / auto theme
│   ├── hooks/               # Custom React hooks
│   ├── i18n/                # Translation files (fr.json, en.json, ar.json)
│   ├── pages/
│   │   ├── Landing.jsx               # Public landing page
│   │   ├── Login.jsx                 # Auth pages
│   │   ├── Register.jsx
│   │   ├── DashboardPage.jsx         # Patient dashboard
│   │   ├── AdminDashboard.jsx        # Admin KPIs + charts + user table
│   │   ├── AdminPanel.jsx            # Admin: assignments, settings, audit
│   │   ├── TherapistDashboard.jsx    # Therapist overview (KPIs + table + alerts)
│   │   ├── TherapistPatientDetail.jsx# Patient detail: sessions, EEG, actions, notes
│   │   ├── SessionLive.jsx           # Live EEG session
│   │   ├── SessionPage.jsx
│   │   ├── History.jsx               # Session history
│   │   ├── Assistant.jsx             # RAG chatbot
│   │   └── Profile.jsx               # Role-aware profile (patient/therapist/admin)
│   ├── stores/
│   │   └── authStore.js     # Zustand auth store (token, user, login, logout)
│   ├── styles/              # Global CSS + Tailwind base
│   └── utils/
│       └── api.js           # Axios instance + all API helpers
├── index.html
├── vite.config.js           # Vite config + /api proxy → localhost:8001
├── tailwind.config.js
└── package.json
```

---

## Setup

```bash
npm install
npm run dev       # http://localhost:5173
npm run build     # production build → dist/
npm run preview   # preview production build
```

---

## Dev proxy

All `/api/*` and `/ws/*` requests are proxied to the backend:

```js
// vite.config.js
proxy: {
  '/api': 'http://localhost:8001',
  '/ws':  { target: 'ws://localhost:8001', ws: true },
}
```

---

## Routing & role guards

```
/                   → Landing (public)
/login              → Login (public, redirects if authenticated)
/register           → Register (public)

/dashboard          → DashboardRoute (admin → AdminDashboard, therapist → TherapistDashboard, patient → Dashboard)
/session/new        → SessionLive   (patient only)
/session/:id        → SessionLive
/history            → History       (patient only)
/assistant          → Assistant     (patient only)
/profile            → Profile       (all roles — role-aware content)
/therapist          → TherapistDashboard   (therapist + admin)
/therapist/patient/:id → TherapistPatientDetail
/admin              → AdminPanel    (admin only)
```

---

## Navigation per role

| Link | Patient | Therapist | Admin |
|---|---|---|---|
| Tableau de bord | ✅ | ✅ | ✅ |
| Session live | ✅ | ❌ | ❌ |
| Historique | ✅ | ❌ | ❌ |
| Assistant | ✅ | ❌ | ❌ |
| Mes patients | ❌ | ✅ | ❌ |
| Administration | ❌ | ❌ | ✅ |
| Mon profil | ✅ | ✅ | ✅ |

---

## Theming

Three modes: `auto` (system), `light`, `dark`. Managed via `ThemeContext`, toggled in the top navbar. Design tokens use CSS custom properties (`--nc-bg`, `--nc-accent`, `--nc-surface`, …) defined in `src/styles/`.

---

## Internationalisation

Supported languages: **Français** (default), **English**, **العربية** (RTL).
Translation keys are in `src/i18n/{fr,en,ar}.json`. Language is persisted to `localStorage`.

---

## Key pages

### `TherapistDashboard.jsx`
Full therapist overview: 5 KPI cards with SVG ring progress, bar chart (patient scores), pie chart (palier distribution), interactive patient table with search + filters, sticky alerts sidebar.

### `TherapistPatientDetail.jsx`
4-tab patient detail: **Vue d'ensemble** (EEG profile + score chart), **Sessions** (full table with TBR/blocks), **Actions** (recommend objective, prescribe sessions, adjust palier, toggle active), **Notes cliniques**.

### `Profile.jsx`
Role-aware: patients see full EEG profile + palier progress + calibration; therapists and admins see a clean info view. All roles have a collapsible password change section.

### `AdminDashboard.jsx`
Admin overview with Recharts charts (donut role distribution, bar sessions, radial engagement), 6 KPI cards, and a full user management table with role editing, active toggle, and delete.
