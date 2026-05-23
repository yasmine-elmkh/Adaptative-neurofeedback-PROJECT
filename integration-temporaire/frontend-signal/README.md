# frontend-signal — NeuroCap EEG · Interface React

Interface React temps réel pour visualiser, analyser et piloter le neurofeedback EEG NeuroCap. Se connecte au `backend-signal` via WebSocket et REST.

---

## Architecture globale

```
backend-signal (FastAPI :8765)
    │  WebSocket  ws://localhost:8765/ws
    │  REST        http://localhost:8765/api/*
    ▼
main.jsx → AppRouter.jsx
    │
    ├── [Casque NeuroCap]   WelcomePage → WifiSetup → App.jsx (dashboard live)
    │
    ├── [Fichier EEG]       WelcomePage → FileDashboard → FeedbackSetup → FeedbackSession → FeedbackReport
    │
    └── [NeuroFeedback]     WelcomePage → NeuroFeedbackHub
                                ├── Protocole 15 séances (ProtocolDashboard → FeedbackSession → FeedbackReport)
                                └── Feedback libre (FeedbackSetup → FeedbackSession → FeedbackReport)
```

---

## Installation & démarrage

### Prérequis

- Node.js 18+ et npm
- `backend-signal` actif sur le port 8765

### Développement

```bash
cd frontend-signal
npm install
npm run dev
# → http://localhost:5173
```

Le proxy Vite redirige automatiquement :
- `/api/*` → `http://localhost:8765/api/*`
- `/ws` → `ws://localhost:8765/ws`

### Production (servie par FastAPI)

```bash
npm run build
xcopy /E /Y dist\ ..\backend-signal\static\
python ..\backend-signal\assembly.py
# → http://localhost:8765/
```

---

## Structure des fichiers

```
frontend-signal/
├── index.html
├── package.json
├── vite.config.js                  # Proxy /api et /ws → :8765
│
└── src/
    ├── main.jsx                    # Point d'entrée React 18
    ├── App.jsx                     # Dashboard live (4 tabs, WebSocket)
    ├── index.css                   # Variables CSS globales
    │
    ├── components/
    │   ├── AppRouter.jsx           # Routeur principal — machine à états
    │   ├── WelcomePage.jsx         # Écran d'accueil — 3 cartes de choix
    │   ├── WifiSetup.jsx           # Configuration WiFi ESP32 (multi-phases)
    │   ├── FileDashboard.jsx       # Upload CSV + résultats ML offline
    │   ├── NeuroFeedbackHub.jsx    # Interface unifiée Protocole + Feedback libre
    │   │
    │   ├── SignalCanvas.jsx        # Oscilloscope EEG canvas (250 samples, RAF)
    │   ├── BandBars.jsx            # Barres puissance spectrale par bande
    │   ├── BatteryIndicator.jsx    # Indicateur tension batterie ESP32
    │   ├── EpochHistory.jsx        # Historique 60 dernières époques + replay
    │   ├── FeaturesPanel.jsx       # Tableau détaillé features par époque
    │   ├── Sidebar.jsx             # Panneau état cognitif + CQE + compteurs
    │   ├── Toast.jsx               # Notifications éphémères 2 s
    │   ├── MLClassifierCard.jsx    # Carte prédiction LightGBM temps réel
    │   │
    │   ├── feedback/               # Composants session neurofeedback
    │   │   ├── FeedbackSession.jsx     # Écran session active (sidebar + stimuli)
    │   │   ├── FeedbackSetup.jsx       # Configuration avant session
    │   │   ├── FeedbackSelector.jsx    # Formulaire retour utilisateur
    │   │   ├── FeedbackJustification.jsx # Guide IA "pourquoi ce média"
    │   │   ├── FeedbackReport.jsx      # Rapport de fin de session
    │   │   ├── BrainStateIndicator.jsx # Badge état cognitif animé
    │   │   ├── EEGLiveMonitor.jsx      # Barres bandes + glossaire 15 features
    │   │   ├── MiniSignalWidget.jsx    # Oscilloscope miniature (WebSocket direct)
    │   │   ├── AudioFeedback.jsx       # Lecteur audio thérapeutique
    │   │   ├── ImageFeedback.jsx       # Afficheur image stimulus
    │   │   ├── VideoFeedback.jsx       # Lecteur vidéo relaxant
    │   │   ├── GameFeedback.jsx        # Routeur jeux (CSV, JSON, SVG, HTML)
    │   │   ├── BreathingGuide.jsx      # Cercle respiratoire animé 4-2-6-2
    │   │   ├── CalibrationTimer.jsx    # Countdown calibration
    │   │   └── FixationPoint.jsx       # Point de fixation relaxation
    │   │
    │   ├── feedback/games/         # Jeux cognitifs intégrés
    │   │   ├── SudokuGame.jsx          # Sudoku 4×4
    │   │   ├── MemoryGame.jsx          # Jeu de mémoire (appariement cartes)
    │   │   ├── CalculGame.jsx          # Calcul mental adaptatif
    │   │   ├── EnigmeGame.jsx          # Énigmes et logique
    │   │   └── PuzzleGame.jsx          # Taquin 3×3 (sliding puzzle)
    │   │
    │   └── protocol/               # Protocole 15 séances
    │       ├── ProtocolDashboard.jsx   # Tableau de bord progression 15 séances
    │       └── ProtocolSession.jsx     # Runner séance (phases + blocs + alpha bar)
    │
    ├── pages/                      # Pages complètes (orchestration flux)
    │   ├── FeedbackSetup.jsx       # Page configuration neurofeedback
    │   ├── FeedbackSession.jsx     # Page session active avec stimuli
    │   └── FeedbackReport.jsx      # Page rapport fin de session
    │
    ├── hooks/
    │   ├── useWebSocket.js         # Hook WebSocket persistant + reconnexion
    │   ├── useEEGWebSocket.js      # WebSocket spécialisé EEG (messages typés)
    │   ├── useFeedbackEngine.js    # API REST feedback (startSession, recommend…)
    │   └── useRecording.js         # Timer enregistrement (start/pause/stop)
    │
    └── lib/
        └── supabase.js             # Client Supabase (auth + DB)
```

---

## Routage — `AppRouter.jsx`

Machine à états avec `useState`. États possibles :

| État | Écran affiché |
|---|---|
| `welcome` | WelcomePage — choix du mode |
| `hardware-wifi` | WifiSetup — config WiFi ESP32 |
| `hardware-live` | App.jsx — dashboard EEG temps réel |
| `file` | FileDashboard — upload CSV offline |
| `neurofeedback` | NeuroFeedbackHub — Protocole + Feedback libre |
| `feedback-setup` | FeedbackSetup — config séance (depuis fichier) |
| `feedback-session` | FeedbackSession — session active |
| `feedback-report` | FeedbackReport — rapport fin de séance |

La variable `returnMode` trace l'origine (`neurofeedback` ou `file`) pour que le rapport redirige vers le bon écran.

---

## Composants détaillés

### `App.jsx` — Dashboard live (4 tabs)

Composant racine du mode hardware. Gère l'état global via `useState` et dispatche les messages WebSocket.

**Tabs :**

| Tab | Contenu |
|---|---|
| 0 — LIVE SIGNAL | SignalCanvas + BandBars + Sidebar + MLClassifierCard |
| 1 — FEATURES | FeaturesPanel (27 features de la dernière époque) |
| 2 — HISTORIQUE | EpochHistory (60 dernières époques, replay) |
| 3 — RAPPORT | Analyse session, stats ML, export CSV |

**Messages WebSocket traités :**

| `type` | Action |
|---|---|
| `init` | Initialise connexion, esp32, baseline, électrodes |
| `eeg` | Sample temps réel → oscilloscope, bandes, état |
| `epoch` | Époque acceptée → features, ML prediction, historique |
| `epoch_rejected` | Compteur rejections |
| `baseline_ready` | Notification baseline calculée |
| `esp32_status` | Connexion/déconnexion ESP32 |
| `wifi_config_result` | Résultat configuration WiFi |

---

### `NeuroFeedbackHub.jsx` — Interface unifiée

Interface à tabs qui combine le Protocole 15 séances et le Feedback libre en un seul écran.

```
┌──────────────────────────────────────────────────────────────────────┐
│ ← Accueil  🧠 NeuroFeedback  [🎯 Protocole]  [🧘 Feedback libre 🔒]  │  ← Header sticky
│                                            ✓ CALIBRATION OK         │
│                                                   [Widget EEG live] │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Onglet Protocole : ProtocolDashboard (progression 15 séances)      │
│  Onglet Feedback libre : FeedbackSetup (si calibration ✓)           │
│                          LockedFeedback (si calibration ✗)          │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

**Déverrouillage Feedback libre :**
- Requête `GET /api/protocol/user/{userId}`
- Si `sessions_done > 0` ou `p_alpha_hist != null` → tab déverrouillé
- En mode démo : données simulées (S1–S3 complétées, alpha historique disponible)

**Widget EEG temps réel** : `MiniSignalWidget` toujours visible dans le header, connecté directement via WebSocket à `ws://localhost:8765/ws`.

---

### `SignalCanvas.jsx` — Oscilloscope temps réel

- Buffer circulaire `Float32Array` de 250 samples (1 s @ 250 Hz effective)
- Boucle `requestAnimationFrame` indépendante de React (bypass batching)
- Suppression DC par médiane ; auto-scale RMS
- Latence < 50 ms end-to-end (ESP32 → canvas)
- Overlay avertissement électrode déconnectée

### `MiniSignalWidget.jsx` — Oscilloscope miniature

- WebSocket direct (pas via props) pour latence minimale
- Buffer 500 samples (2 s @ 250 Hz)
- Gradient signal vert → mauve → bleu (palette projet)
- Hauteur 56px — intégrable dans n'importe quelle sidebar ou header
- Auto-reconnexion toutes les 3 s si déconnecté

### `EEGLiveMonitor.jsx` — Barres de bandes + glossaire

- 5 bandes : delta / theta / alpha / beta / gamma
- Cliquer une bande → explication clinique en français
- Glossaire 15 features (PSD, Hjorth, entropie, SEF95, PAC, FD)
- Références : Pope 1995, Klimesch 1999, Cohen 2014, Mou et al. 2024

### `ProtocolDashboard.jsx` — Tableau de bord 15 séances

- **15 cercles** de séances : statut (verrouillé/disponible/complété), taux de succès %, étoile pour bilans
- **4 cartes stat** : séances complétées, palier actuel, score moyen 5 der., prochain bilan
- **Graphe SVG** : courbe taux de succès par séance avec marqueurs bilans (★)
- **Tooltips** au survol : date, taux, palier, nombre de blocs
- **Mode démo** si API indisponible : données S1–S3 pré-remplies

### `ProtocolSession.jsx` — Runner de séance

Phases de la séance (machine à états avec timer) :

```
questionnaire_pre → baseline (2 min) → iapf (1 min)
→ bloc×5 [neurofeedback 3 min + pause 20 s] → repos_final (3 min)
→ questionnaire_post → rapport
```

Affiche en temps réel : barre alpha vs seuil, compte à rebours, consigne phase, taux de succès bloc courant.

### `GameFeedback.jsx` — Routeur jeux intelligent

| Source | Détection | Traitement |
|---|---|---|
| JSON Cloudinary | Extension `.json` | Décode → composant jeu typé selon `type` |
| SVG coloriage | Extension `.svg` | Coloriage interactif (click → remplissage) |
| HTML iframe | Extension `.html` | Embed direct |
| Fallback | — | Jeu intégré aléatoire (Sudoku/Mémoire/Calcul/Énigme/Puzzle) |

Préfixes CSV pour forcer le type : `CAL_*` (Calcul), `SDK_*` (Sudoku), `ENI_*` (Énigme), `MEM_*` (Mémoire), `PUZ_*` (Puzzle).

---

## Hooks

### `useWebSocket.js` — WebSocket bas niveau

```js
const { send, connect, disconnect } = useWebSocket('ws://localhost:8765/ws', {
  onOpen:    () => setConnected(true),
  onClose:   () => setConnected(false),
  onMessage: (data) => handleMessage(data),  // data déjà parsé JSON
})
```

Reconnexion automatique toutes les 3 s. Callbacks stables via `useRef` pour éviter les re-renders.

### `useFeedbackEngine.js` — Moteur feedback REST

```js
const { startSession, recommend, submitFeedback, nextItem, skipItem, endSession } = useFeedbackEngine()

const sessionId = await startSession(userId, objective)
const media     = await recommend(sessionId, eegState, features, forcedType)
await submitFeedback(sessionId, media, liked, ressenti, noteConc, noteStress)
const report    = await endSession(sessionId)
// report: { rapport_ia, deltas: { alpha, beta }, efficacy_pct, history[] }
```

### `useRecording.js` — Timer enregistrement

États : `idle | recording | paused`. Expose `rec`, `paused`, `recT` (secondes).

---

## Flux WebSocket complet — mode live

```
ESP32 (WiFi TCP :9000)
    │ CSV 250 Hz
    ▼
backend-signal (processing_loop)
    │ DSP → features → ML → WS broadcast
    ▼
useWebSocket.js — onMessage(data)
    │
    ├── type:'eeg'   → setSignal, setBands, setState, setCalProgress
    ├── type:'epoch' → setFeatures, setMlPrediction, setEpochHistory
    └── type:'init'  → setConnected, setBaselineOk, setElectrodeOk
    │
    ▼
App.jsx — re-render ciblé
    ├── SignalCanvas  (RAF — bypasse React)
    ├── BandBars      (update direct)
    ├── Sidebar       (état, CQE, ratios)
    └── MLClassifierCard (prediction + barres proba)
```

Latence cible : < 50 ms signal → canvas (RAF direct).
Latence typique : ~4 ms inter-message @ 250 Hz → oscilloscope fluide.

---

## Payload EEG temps réel (reçu ~62 Hz)

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

**Important :** seul `filtered` est affiché dans l'oscilloscope. `uv` brut contient le DC offset (~1.65M µV).

---

## Configuration Vite

```js
// vite.config.js
proxy: {
  '/api': { target: 'http://localhost:8765', changeOrigin: true },
  '/ws':  { target: 'ws://localhost:8765',   ws: true, changeOrigin: true },
}
```

En production (frontend servi par FastAPI), le proxy Vite n'est pas nécessaire.

---

## Design system — deux palettes

### Palette dark (App.jsx — dashboard live)

| Token | Valeur | Usage |
|---|---|---|
| Background | `#07090f` | Fond global |
| Card | `#0a0e18` | Panneaux |
| Accent vert | `#00e5b0` | Signal OK, alpha success |
| Orange | `#f5a623` | Warnings, sous-seuil |
| Rouge | `#ff4d6d` | Erreurs, REC actif |
| Texte | `#c9d8e8` | Valeurs numériques |
| Muted | `#4a5a6e` | Labels secondaires |
| Mono | `'Space Mono'`, `'DM Mono'` | Valeurs, timestamps |

### Palette bleu-mauve (Neurofeedback — FeedbackSession, ProtocolDashboard)

| Token | Valeur | Usage |
|---|---|---|
| Background | `#C5D3E8` | Fond global |
| Card | `rgba(247,243,250,0.55)` | Panneaux frosted-glass |
| Accent mauve | `#B87B9E` | Boutons, seuil, protocole |
| Vert | `#7BC4A0` | Succès, relax, complété |
| Bleu | `#7BA8C4` | Focus, info |
| Texte | `#2B2A4A` | Principal |
| Muted | `#9A8BAE` | Secondaire |

---

## WifiSetup — Machine à états

```
loading → ready
          ├── [réseau mémorisé] → confirming → waiting (poll /api/status)
          └── [nouveau réseau]  → confirming → waiting
                                               ├── success → onDone() → App.jsx
                                               └── error   → ready
```

L'ESP32 est détecté via UDP : le backend pousse `esp32_ap_detected` via WS dès qu'il reçoit `ESP_EEG_AP:<ssid>`.

---

## MLClassifierCard — Carte LightGBM

```
┌────────────────────────────────────────────────────────┐
│  🧠 CLASSIFIEUR ML                   LightGBM · LOSO  │
│────────────────────────────────────────────────────────│
│  🎯 CONCENTRATION                     Confiance 83 %  │
│                                                        │
│  Concentration  ████████████████░░░░    83.4 %         │
│  Stress         ███░░░░░░░░░░░░░░░░░    16.6 %         │
│────────────────────────────────────────────────────────│
│  FeatEng · 63 features · LightGBM · LOSO validé       │
└────────────────────────────────────────────────────────┘
```

Props : `prediction: null | { concentration, stress, state, confidence, uncertain }`

---

## Dépendances

| Package | Version | Usage |
|---|---|---|
| `react` | ^18.3.1 | Framework UI |
| `react-dom` | ^18.3.1 | Rendu DOM |
| `axios` | ^1.7.2 | Appels REST API |
| `@supabase/supabase-js` | ^2.x | Client Supabase (optionnel) |
| `vite` | ^5.3.1 | Build + dev server + proxy |
| `@vitejs/plugin-react` | ^4.3.1 | Transform JSX |
