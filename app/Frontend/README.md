# NeuroCap Frontend — React 18 + Vite + Tailwind

Application SPA pour la plateforme de neurofeedback EEG NeuroCap.  
Oscilloscope temps réel, analyse fichiers EEG offline, dashboard patient, gestion thérapeute, administration.

---

## Stack

| Technologie | Version | Rôle |
|---|---|---|
| React | 18 | Framework UI |
| Vite | 5 | Build tool + serveur dev |
| Tailwind CSS | 3 | Styling utility-first |
| React Router | 6 | Routing côté client |
| Zustand | 4 | État global (auth) |
| Axios | 1 | Client HTTP |
| Recharts | 2 | Graphiques (AreaChart, BarChart, PieChart, RadialBar) |
| i18next | latest | Internationalisation (FR / EN / AR + RTL) |
| Lucide React | latest | Icônes |

---

## Structure du projet

```
app/Frontend/
├── public/
│   ├── NeuroCap_Logo.png        # Logo officiel (utilisé sur Login + Register)
│   ├── favicon.svg
│   └── video/
│       └── Brain.mp4            # Vidéo fond droite Login
├── src/
│   ├── components/
│   │   ├── Layout.jsx           # Navbar sticky + drawer mobile + bottom nav
│   │   ├── eeg/
│   │   │   ├── SignalCanvas.jsx  # Oscilloscope canvas WebGL
│   │   │   └── BandBars.jsx      # Barres puissance bandes spectrales
│   │   └── ...
│   ├── context/
│   │   └── ThemeContext.jsx     # Dark / light / auto + tokens CSS
│   ├── hooks/
│   │   └── useEEGWebSocket.js   # Hook WebSocket EEG (reconnexion auto, état)
│   ├── i18n/                    # Fichiers traductions (fr.json, en.json, ar.json)
│   ├── pages/
│   │   ├── Landing.jsx               # Page publique
│   │   ├── Login.jsx                 # Connexion (logo NeuroCap_Logo.png)
│   │   ├── Register.jsx              # Inscription (logo NeuroCap_Logo.png)
│   │   ├── DashboardPage.jsx         # Dashboard patient : EEG recordings + sessions
│   │   ├── EEGSelector.jsx           # Choix mode EEG (live / fichier / guide)
│   │   ├── EEGLive.jsx               # Oscilloscope temps réel + WiFi + baseline
│   │   ├── EEGFile.jsx               # Upload + analyse LightGBM + auto-save rapport
│   │   ├── ElectrodeGuide.jsx        # Guide 10-20 + protocole cutané + consentement RGPD
│   │   ├── Profile.jsx               # Profils A/B/C + fine-tuning IA (role-aware)
│   │   ├── TherapistDashboard.jsx    # Vue thérapeute : KPIs + patients + alertes
│   │   ├── TherapistPatientDetail.jsx# Détail patient : sessions, EEG, notes, actions
│   │   ├── AdminDashboard.jsx        # Admin : KPIs + graphiques + gestion utilisateurs
│   │   └── AdminPanel.jsx            # Admin : assignments, settings, audit logs
│   ├── stores/
│   │   └── authStore.js             # Zustand : token, user, login, logout
│   └── utils/
│       └── api.js                   # Instance Axios + tous les helpers API (eeg.*, auth.*, ...)
├── index.html
├── vite.config.js                   # Proxy /api → 8001, /ws → 8001
├── tailwind.config.js
└── package.json
```

---

## Installation

```bash
npm install
npm run dev       # http://localhost:5173
npm run build     # build production → dist/
npm run preview   # prévisualiser le build
```

---

## Proxy Vite

Toutes les requêtes `/api/*` et `/ws/*` sont proxifiées vers le backend :

```js
// vite.config.js
proxy: {
  '/api': 'http://localhost:8001',
  '/ws':  { target: 'ws://localhost:8001', ws: true },
}
```

---

## Routing et guards de rôle

```
/                       → Landing (public)
/login                  → Login (public, redirige si authentifié)
/register               → Register (public)

/dashboard              → DashboardPage (patient)
                          AdminDashboard (admin)
                          TherapistDashboard (thérapeute)

/eeg                    → EEGSelector    (patient — choix live / fichier / guide)
/eeg-live               → EEGLive        (patient — oscilloscope temps réel)
/eeg-file               → EEGFile        (patient — upload + analyse offline)
/electrode-guide        → ElectrodeGuide (patient — guide + consentement RGPD)

/profile                → Profile        (tous rôles — contenu adapté au rôle)
/therapist              → TherapistDashboard
/therapist/patient/:id  → TherapistPatientDetail
/admin                  → AdminPanel
```

---

## Navigation par rôle

| Lien | Patient | Thérapeute | Admin |
|---|---|---|---|
| Tableau de bord | ✅ | ✅ | ✅ |
| EEG (live / fichier) | ✅ | ❌ | ❌ |
| Guide électrode | ✅ | ❌ | ❌ |
| Mes patients | ❌ | ✅ | ❌ |
| Administration | ❌ | ❌ | ✅ |
| Mon profil | ✅ | ✅ | ✅ |

---

## Pages clés

### `EEGLive.jsx`
Oscilloscope temps réel via `useEEGWebSocket`. Gestion WiFi ESP32 (scan, config SSID, reconnexion). Acquisition baseline + enregistrement CSV. Affichage état électrode + bandes spectrales en temps réel.

### `EEGFile.jsx`
Upload fichier `.edf` / `.csv` / `.txt`. Appel `POST /api/eeg/analyze_file` → résultats LightGBM (état dominant, distribution epochs, confiance). Auto-sauvegarde du rapport pour le thérapeute si authentifié. Stockage automatique des epochs haute-confiance dans `training_epochs` pour le fine-tuning.

### `EEGSelector.jsx`
Carte de choix entre les 3 modes : EEG temps réel, Analyser un fichier, Guide électrode. Point d'entrée `/eeg`.

### `ElectrodeGuide.jsx`
Schéma du système 10-20, protocole cutané détaillé, FAQ signal, consentement RGPD à accepter avant toute session.

### `DashboardPage.jsx`
Dashboard patient : cartes statistiques (rapports EEG, sessions, profil), AreaChart évolution temporelle, tableau des derniers rapports EEG. Empty state avec CTA vers EEGSelector si aucune donnée.

### `Profile.jsx`
Role-aware :
- **Patient** : type cognitif A/B/C (ratio α/β + ERD), métriques EEG, palier P1–P4, statut fine-tuning IA avec indicateur activité (actif / en attente / inactif longue durée).
- **Thérapeute / Admin** : vue info + changement mot de passe.

### `TherapistPatientDetail.jsx`
4 onglets : **Vue d'ensemble** (profil EEG + graphique scores), **Sessions** (tableau complet), **Rapports EEG** (analyses fichiers + sessions live), **Actions** (objectif, palier, activation), **Notes cliniques**.

### `AdminDashboard.jsx`
KPIs globaux, graphiques Recharts (donut rôles, bar sessions, radial engagement), table utilisateurs avec recherche, filtre rôle, toggle actif, suppression.

---

## Thème

3 modes : `auto` (système), `light`, `dark`. Géré via `ThemeContext`, basculable depuis la navbar. Design tokens CSS (`--nc-bg`, `--nc-accent`, `--nc-surface`, …) définis dans `src/styles/`.

---

## Internationalisation

Langues : **Français** (défaut), **English**, **العربية** (RTL).  
Fichiers de traduction dans `src/i18n/{fr,en,ar}.json`. Langue persistée dans `localStorage`.

---

## Hook WebSocket EEG — `useEEGWebSocket.js`

Gère la connexion WebSocket `/ws/eeg`, la reconnexion automatique, et expose :
- `signal` : buffer d'échantillons pour l'oscilloscope
- `epoch` : dernière epoch classifiée (state, confidence, features)
- `electrode` : qualité contact
- `esp32` : état connexion + IP
- `send(cmd)` : envoi de commandes (FINALISE_BASELINE, START_REC, …)
