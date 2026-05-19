# frontend-signal — NeuroCap EEG Dashboard

Interface React temps réel pour visualiser, analyser et enregistrer le signal EEG NeuroCap. Se connecte au `backend-signal` via WebSocket et REST.

---

## Vue d'ensemble

```
backend-signal (FastAPI :8765)
    │  WebSocket ws://localhost:8765/ws
    │  REST      http://localhost:8765/api/*
    ▼
App.jsx (React 18 + Vite)
    ├─ useWebSocket.js   — connexion WebSocket persistante
    ├─ useRecording.js   — gestion enregistrement CSV
    │
    ├─ [Page 1] WifiSetup.jsx      — configuration WiFi ESP32
    └─ [Page 2] Dashboard (App.jsx)
           ├─ Tab 0 : LIVE SIGNAL   — oscilloscope + métriques temps réel
           ├─ Tab 1 : FEATURES      — vecteur complet de features par époque
           ├─ Tab 2 : HISTORIQUE    — liste des époques avec replay
           └─ Tab 3 : RAPPORT       — résumé de session
```

---

## Installation & lancement

### Prérequis

- Node.js 18+ et npm
- Le `backend-signal` doit tourner sur le port 8765

### Démarrage en développement

```bash
cd frontend-signal
npm install
npm run dev
```

L'interface est disponible sur `http://localhost:5173`.

Le proxy Vite redirige automatiquement :
- `/api/*` → `http://localhost:8765/api/*`
- `/ws` → `ws://localhost:8765/ws`

### Build de production

```bash
npm run build
# Le dossier dist/ peut être servi par le backend FastAPI (dossier static/)
```

Pour servir le build via le backend Python :

```bash
cp -r dist/ ../backend-signal/static/
python assembly.py
# Accès sur http://localhost:8765/
```

---

## Architecture des composants

### Routage — `AppRouter.jsx`

Affiche `WifiSetup` tant que le WiFi n'est pas configuré, puis passe au Dashboard `App.jsx`.

### App.jsx — Dashboard principal

Composant racine qui :
- Gère l'état global via `useState` (connexion, signal, électrodes, époques)
- Dispatche les messages WebSocket entrants vers les bons états
- Envoie des commandes au backend (baseline, recording, analyze)

**Messages WebSocket reçus et traités :**

| `type` | Action |
|---|---|
| `init` | Initialise l'état de connexion, esp32, baseline, électrodes |
| `esp32_status` | Met à jour l'état de l'ESP32 (connecté/déconnecté) |
| `electrode` | Met à jour Fp2/M2 connectés |
| `eeg` | Sample temps réel → oscilloscope, bandes, état cognitif |
| `epoch` | Époque acceptée → features, historique |
| `epoch_rejected` | Époque rejetée → compteur |
| `baseline_ready` | Notification baseline calculée |
| `wifi_config_result` | Résultat configuration WiFi |

### Composants UI

| Composant | Rôle |
|---|---|
| `SignalCanvas.jsx` | Oscilloscope canvas temps réel (signal EEG filtré) |
| `BandBars.jsx` | Barres de puissance relative par bande (delta/theta/alpha/beta/gamma) |
| `BatteryIndicator.jsx` | Indicateur tension batterie ESP32 |
| `EpochHistory.jsx` | Liste scrollable des 60 dernières époques, avec replay |
| `FeaturesPanel.jsx` | Tableau détaillé de toutes les features d'une époque |
| `Sidebar.jsx` | Panneau latéral : état cognitif, qualité signal, CQE, compteurs |
| `Toast.jsx` + `useToast` | Notifications éphémères (2 s) |
| `WifiSetup.jsx` | Page de configuration WiFi ESP32 (multi-phases) |

### Hooks

#### `useWebSocket.js`

Hook bas niveau gérant une connexion WebSocket persistante.

```js
const { send, connect, disconnect } = useWebSocket('ws://localhost:8765/ws', {
  onOpen:    () => setConnected(true),
  onClose:   () => setConnected(false),
  onMessage: (data) => handleMessage(data),  // data est déjà parsé en JSON
})
```

- Reconnexion automatique toutes les 3 s si déconnexion involontaire
- Callbacks stables via `ref` pour éviter les re-renders

#### `useRecording.js`

Gère le timer de l'enregistrement (start / pause / resume / stop) avec état `rec`, `paused`, `recT`.

---

## Flux WebSocket — détail technique

### Connexion et reconnexion

```js
// Auto-connect au montage (300 ms delay)
useEffect(() => { const t = setTimeout(() => wsConnect(), 300) }, [wsConnect])

// Reconnexion auto 3 s si déconnexion involontaire
useEffect(() => {
  if (!wsConnected && !manualClose.current) {
    const t = setTimeout(() => wsConnect(), 3000)
  }
}, [wsConnected, wsConnect])
```

### Commandes envoyées

```js
send({ command: 'FINALISE_BASELINE' })  // après 10+ époques propres
send({ command: 'START_REC' })          // démarre CSV côté serveur
send({ command: 'STOP_REC' })           // arrête CSV
send({ command: 'ANALYZE_NOW' })        // rapport temps réel
```

### Payload EEG temps réel (reçu ~62 Hz)

```json
{
  "type": "eeg",
  "ts": 1748342100000,
  "uv": 1650234.5,
  "filtered": -12.345,
  "electrode_ok": true,
  "fp2_connected": true,
  "m2_connected": true,
  "batt_V": 3.85,
  "bands": {
    "delta": 0.12, "theta": 0.18, "alpha": 0.35,
    "beta": 0.25, "beta_high": 0.08, "gamma_low": 0.02
  },
  "state": "relaxed",
  "cqe_score": 82,
  "cqe_label": "good",
  "cal_progress": 67.4,
  "raw_metrics": { "rms_raw": 18.4, "peak": 45.2, "dc_uv": 1650230.1 }
}
```

---

## Configuration Vite

```js
// vite.config.js
proxy: {
  '/api': { target: 'http://localhost:8765', changeOrigin: true },
  '/ws':  { target: 'ws://localhost:8765',   ws: true, changeOrigin: true },
}
```

En production, si le frontend est servi directement par FastAPI (port 8000), ce proxy n'est plus nécessaire.

---

## WifiSetup — Machine à états

```
loading → ready ──────────────────────────────────┐
              ├── [sélectionner réseau mémorisé]    │
              └── [entrer nouveau réseau]            │
                        ↓                           │
                   confirming                       │
                        ↓                           │
                    waiting (polling /api/status)   │
                  ┌────┴────┐                       │
               success    error                     │
                  │                                 │
              onDone() ────────────────────────────►┘
                            (passe au Dashboard)
```

L'ESP32 est détecté via UDP — `WifiSetup` écoute le message WebSocket `esp32_ap_detected` pour afficher le SSID du hotspot automatiquement.

---

## Intégration IA — Guide développeur

Le frontend peut afficher des prédictions IA reçues du backend sans modification structurelle.

### Afficher un état IA dans la Sidebar

Si le backend injecte `ai_state` et `ai_confidence` dans le payload `epoch`, les afficher dans `Sidebar.jsx` :

```jsx
// components/Sidebar.jsx — ajouter dans le panneau état
{features.ai_state && (
  <div>
    <span>IA : {features.ai_state}</span>
    <span>{(features.ai_confidence * 100).toFixed(1)} %</span>
  </div>
)}
```

### Afficher un score IA dans FeaturesPanel

```jsx
// components/FeaturesPanel.jsx — ajouter une ligne au tableau
["Prédiction IA",   features.ai_state     ?? "—"],
["Confiance IA",    features.ai_confidence ?? "—"],
```

### Intégrer une inférence côté client (ONNX)

Pour exécuter un modèle directement dans le navigateur (sans latence réseau) :

```bash
npm install onnxruntime-web
```

```js
// hooks/useAIModel.js — exemple
import * as ort from 'onnxruntime-web'

const session = await ort.InferenceSession.create('/model.onnx')

function predict(features) {
  const input = new ort.Tensor('float32',
    Float32Array.from([
      features.rel_delta, features.rel_theta, features.rel_alpha,
      features.rel_beta,  features.rel_gamma_low,
      features.engagement, features.stress_idx,
      features.hjorth_mobility, features.hjorth_complexity,
      features.fractal_dim,     features.spectral_entropy,
      features.pac_theta_gamma, features.sef95,
    ]),
    [1, 13]
  )
  const results = await session.run({ input })
  return results.output.data  // [prob_focused, prob_stressed, prob_relaxed, prob_neutral]
}
```

Appeler `predict(epoch.features)` dans `handleMessage` au moment du type `epoch`.

### Visualiser des prédictions en temps réel

Ajouter un état React dans `App.jsx` :

```jsx
const [aiPrediction, setAiPrediction] = useState(null)

// Dans handleMessage, case 'epoch' :
const pred = await predict(d.features)
setAiPrediction({ label: LABELS[pred.indexOf(Math.max(...pred))], probs: pred })
```

---

## Structure des fichiers

```
frontend-signal/
├── index.html
├── package.json
├── vite.config.js
│
└── src/
    ├── main.jsx                   # Point d'entrée React
    ├── App.jsx                    # Dashboard principal (4 tabs)
    ├── index.css                  # Variables CSS globales
    │
    ├── components/
    │   ├── AppRouter.jsx          # Router WifiSetup ↔ Dashboard
    │   ├── WifiSetup.jsx          # Configuration WiFi ESP32
    │   ├── SignalCanvas.jsx       # Oscilloscope canvas temps réel
    │   ├── BandBars.jsx           # Barres puissance spectrale
    │   ├── BatteryIndicator.jsx   # Indicateur batterie
    │   ├── EpochHistory.jsx       # Historique des époques
    │   ├── FeaturesPanel.jsx      # Détail features par époque
    │   ├── Sidebar.jsx            # Panneau état cognitif
    │   └── Toast.jsx              # Notifications
    │
    └── hooks/
        ├── useWebSocket.js        # Hook WebSocket persistant
        └── useRecording.js        # Hook timer enregistrement
```

---

## Dépendances

| Package | Version | Usage |
|---|---|---|
| `react` | ^18.3.1 | UI |
| `react-dom` | ^18.3.1 | Rendu DOM |
| `axios` | ^1.7.2 | Requêtes REST (WiFi config, export CSV) |
| `vite` | ^5.3.1 | Build + dev server + proxy |
| `@vitejs/plugin-react` | ^4.3.1 | Transform JSX |

---

## Design system

Le dashboard utilise un thème dark-mode cohérent :

| Variable | Valeur | Usage |
|---|---|---|
| Background principal | `#07090f` | Fond global |
| Background card | `#0a0e18` | Panneaux |
| Accent vert | `#00e5b0` | Signal OK, valeurs positives |
| Accent orange | `#f5a623` | Warnings |
| Accent rouge | `#ff4d6d` | Erreurs, REC actif |
| Texte principal | `#c9d8e8` | Valeurs numériques |
| Police monospace | `'Space Mono'` | Valeurs, labels techniques |

---

## Notes importantes

- **Seul le signal `filtered`** (post-filtrage IIR) est affiché dans l'oscilloscope. `uv` brut n'est pas affiché car il contient le DC offset (~1.6M µV).
- L'oscilloscope affiche ~62 Hz (1 sample sur 4 broadcasté par le backend).
- L'historique garde les 60 dernières époques en mémoire React (pas de stockage local).
- Le replay d'époque (`EpochHistory → handleReplay`) bascule sur l'onglet FEATURES avec les features de l'époque sélectionnée.

---

## Classifieur ML — Affichage temps réel — Ajout v7.3

### Nouveau composant : `MLClassifierCard.jsx`

Carte de visualisation de la prédiction LightGBM FeatEng, affichée dans **Tab 0 (LIVE SIGNAL)** juste après les métriques de bandes spectrales.

**Rendu selon l'état prédit :**

| État | Badge | Couleur bordure |
|---|---|---|
| Concentration | `🎯 CONCENTRATION` | `#00e5b0` (vert) |
| Stress | `⚡ STRESS` | `#ff4d6d` (rouge) |
| Incertain (`confidence < 60%`) | `⚠ INCERTAIN` | `#f5a623` (orange) |
| Pas encore de prédiction | — | Carte vide grisée |

**Contenu de la carte :**

```
┌─────────────────────────────────────────────┐
│  🧠 CLASSIFIEUR ML           LightGBM · LOSO│
│─────────────────────────────────────────────│
│  🎯 CONCENTRATION            Confiance 83 % │
│                                             │
│  Concentration ████████████████░░░░  83.4 % │
│  Stress        ███░░░░░░░░░░░░░░░░░  16.6 % │
│                                             │
│  ⚠ Confiance insuffisante (< 60%)          │  ← si uncertain
│─────────────────────────────────────────────│
│  FeatEng · 63 features · LightGBM · LOSO validé │
└─────────────────────────────────────────────┘
```

**Props :**

```jsx
<MLClassifierCard prediction={mlPrediction} />
// prediction : null | { concentration, stress, state, confidence, uncertain }
```

**Sous-composant `ProbBar`** : barre de progression animée (`width .45s ease`) affichant la probabilité pour chaque classe.

### Modifications `App.jsx`

**1. Import et state**

```jsx
import MLClassifierCard from './components/MLClassifierCard.jsx'

const [mlPrediction, setMlPrediction] = useState(null)
```

**2. Handler WebSocket — case `'epoch'`**

```jsx
case 'epoch':
  // ... traitement existant
  if (d.ml_prediction) setMlPrediction(d.ml_prediction)
  break
```

La prédiction est aussi stockée dans l'historique des époques :

```jsx
setEpochHistory(prev => [
  { ...d, features: d.features ?? {}, ml_prediction: d.ml_prediction ?? null },
  ...prev.slice(0, 59)
])
```

**3. Placement dans Tab 0**

```jsx
{/* Tab 0 — LIVE SIGNAL */}
<div>
  {/* ... composants existants (SignalCanvas, BandBars, métriques) ... */}
  <MLClassifierCard prediction={mlPrediction} />
</div>
```

**4. Stats ML dans Tab 3 (RAPPORT)**

Deux lignes sont ajoutées au tableau récapitulatif de session :

| Ligne | Valeur |
|---|---|
| Dernier état ML | `concentration` / `stress` / `—` |
| Confiance ML | `83.4 %` / `—` |

### URL WebSocket et proxy mis à jour

Le backend tourne maintenant sur le port **8765** :

```js
// App.jsx
'ws://localhost:8765/ws'

// vite.config.js — proxy
'/api' → 'http://localhost:8765'
'/ws'  → 'ws://localhost:8765'

// useRecording.js
const API = 'http://localhost:8765/api'

// WifiSetup.jsx
const API_CANDIDATES = [
  `http://${window.location.hostname}:8765/api`,
  'http://localhost:8765/api',
  'http://127.0.0.1:8765/api',
]
```

### Structure des fichiers mise à jour

```
frontend-signal/
├── package.json                 # NOUVEAU — dépendances npm (react, axios, vite)
├── vite.config.js               # Proxy mis à jour → :8765
│
└── src/
    ├── App.jsx                  # mlPrediction state + MLClassifierCard + Tab 3 stats
    ├── components/
    │   └── MLClassifierCard.jsx # NOUVEAU — carte prédiction LightGBM
    └── hooks/
        └── useRecording.js      # URL API mise à jour → :8765
```

### Flux de données complet

```
backend-signal (port 8765)
    │  WS message { type: "epoch", ml_prediction: {...} }
    ▼
App.jsx — handleMessage()
    │  case 'epoch' → setMlPrediction(d.ml_prediction)
    ▼
MLClassifierCard — re-render
    │  ProbBar animée (transition 450 ms)
    └─► Affichage état + confiance + barres de probabilité
```
