# backend-signal — NeuroCap EEG Signal Server

Serveur Python temps réel pour acquisition, traitement DSP et diffusion WebSocket du signal EEG capté par l'ESP32 via le casque NeuroCap.

---

## Vue d'ensemble

```
ESP32 (ADS1115 + AD8232)
    │  TCP :9000  (CSV streaming 250 Hz)
    │  UDP :4322  (annonces + config WiFi)
    ▼
assembly.py ──► WifiManager   ─── UDP ──► ESP32 config
             ├─ TCPReceiver   ─── recv ─► sample_queue
             ├─ RealTimeProcessor (DSP)
             └─ FastAPI (api.py)
                  ├─ REST  /api/*
                  └─ WS    /ws  ──► Frontend React
```

**Rôle de chaque module :**

| Fichier | Rôle |
|---|---|
| `assembly.py` | Point d'entrée — orchestre tous les composants |
| `api.py` | API REST + endpoint WebSocket + boucle DSP async |
| `tcp_receiver.py` | Serveur TCP — reçoit le flux CSV de l'ESP32 |
| `wifi_manager.py` | Gestion WiFi ESP32 par UDP |
| `dsp/processor.py` | `RealTimeProcessor` + `CognitiveStateClassifier` |
| `dsp/epochs.py` | `EpochExtractor` + `PreprocessingPipeline` |
| `dsp/features.py` | Extraction de 25+ features par époque |
| `dsp/filters.py` | `FilterBank` — Golden Filter [1-45 Hz] |
| `dsp/artifacts.py` | `ElectrodeMonitor`, `ArtifactDetector`, `ContactQualityEstimator` |
| `recording/csv_handler.py` | Enregistrement CSV signal + époques |
| `utils/constants.py` | Constantes globales (FS, ports, bandes…) |

---

## Installation

```bash
pip install fastapi uvicorn scipy numpy pywavelets websockets
```

**Python 3.10+** requis.

Dépendances complètes :

```
fastapi
uvicorn
scipy
numpy
PyWavelets
websockets
```

---

## Lancement

```bash
# Depuis la racine du dépôt ou depuis backend-signal/
python assembly.py
```

Affichage au démarrage :

```
═══════════════════════════════════════════════
  NeuroCap EEG v7.2 — WiFi Setup First
  API  : http://192.168.x.x:8000/api/status
  WS   : ws://192.168.x.x:8000/ws
  Docs : http://192.168.x.x:8000/docs
═══════════════════════════════════════════════
```

> Le serveur libère automatiquement le port 8000 s'il est déjà utilisé.

---

## Protocole réseau

### 1. Flux TCP :9000 — streaming EEG depuis l'ESP32

L'ESP32 se connecte et envoie des lignes CSV à 250 Hz.

**Format firmware minimal (4 colonnes) :**
```
timestamp_ms,raw_adc,voltage_mV,pkt_id
```

**Format firmware complet (8 colonnes) :**
```
timestamp_us,raw_adc,voltage_mV,batt_V,lo_plus,lo_minus,lead_off,pkt_id
```

`TCPReceiver` parse chaque ligne, applique un filtre DC adaptatif (IIR 0.05 Hz), et pousse le sample dans `sample_queue`.

### 2. UDP :4322/:4323 — configuration WiFi

| Port | Direction | Message |
|---|---|---|
| 4322 (listen) | ESP32 → Serveur | `ESP_EEG_AP:<ssid>` ou `ESP_EEG:<ip>` |
| 4320 (send) | Serveur → ESP32 | `WIFI_CONFIG:<ssid>:<pwd>` |
| 4323 (listen) | ESP32 → Serveur | `WIFI_OK:<ip>:<ssid>` ou `WIFI_FAILED:<ssid>:<reason>` |

Le serveur broadcast `EEG_SERVER_IP:<ip>` toutes les 2 s pour que l'ESP32 puisse trouver le PC sur le réseau.

---

## Pipeline DSP

### Signal path échantillon par échantillon (250 Hz)

```
uv brut (ESP32)
    │
    ├─► DCRemover (TCP) — IIR 0.05 Hz
    │
    ├─► FilterBank.filter_sample() — causal RT
    │     Notch 50 Hz → Notch 100 Hz → BP [1-45 Hz] Butterworth ord. 4
    │
    ├─► ContactQualityEstimator (toutes les 500 ms)
    │
    ├─► Welch temps réel (fenêtre 10 s, toutes les 1 s)
    │
    └─► EpochExtractor.push()  → si fenêtre 4 s complète → _process()
```

### Pipeline par époque (fenêtre 4 s, overlap 75 %)

```
raw_epoch (1000 samples)
    │
    ├─► ArtifactDetector.is_bad()
    │     flat_line / extreme_peak / electrode_off / emg_reject
    │     → si bad : retourne epoch_rejected
    │
    ├─► FilterBank.filter_epoch() — zéro-phase (filtfilt)
    │     median_sub → Notch 50 → Notch 100 → BP [1-45] → Wavelet db4
    │
    ├─► normalise_db()  →  dB vs baseline (QEEG standard)
    │
    └─► extract_features()  →  vecteur 25+ features
```

### Features extraites par époque

| Catégorie | Features |
|---|---|
| **Puissances relatives** | `rel_delta`, `rel_theta`, `rel_alpha`, `rel_beta`, `rel_beta_high`, `rel_gamma_low` |
| **Ratios cognitifs** | `engagement`, `stress_idx`, `theta_alpha`, `alpha_beta` |
| **Hjorth** | `hjorth_activity`, `hjorth_mobility`, `hjorth_complexity` |
| **Complexité** | `fractal_dim` (HFD Higuchi), `spectral_entropy`, `sef95` |
| **Amplitude** | `rms_uv`, `mean_amp`, `skewness`, `kurtosis`, `zcr` |
| **PAC** | `pac_theta_gamma` (couplage phase-amplitude θ→γ) |
| **dB baseline** | `db_delta`, `db_theta`, `db_alpha`, `db_beta`, … |

### Bandes fréquentielles v8.0

| Bande | Plage | Justification |
|---|---|---|
| delta | 1–4 Hz | HP 1 Hz élimine drift polarisation |
| theta | **6–8 Hz** | 4-6 Hz contaminé par EOG résiduel (Klimesch 1999) |
| alpha | 8–13 Hz | Standard |
| beta | 13–30 Hz | Standard |
| beta_high | 20–30 Hz | Stress index |
| gamma_low | 30–45 Hz | Préservé par LP 45 Hz |

### Classification d'état cognitif

`CognitiveStateClassifier` produit un état parmi : **focused / stressed / relaxed / neutral / invalid**

Méthode : Z-scores individuels vs baseline du sujet (pas de valeur diagnostique clinique).

```
INVALID  : CQE < 60 OU emg_ratio > 0.20
FOCUSED  : Z_theta > +1.0 ET Z_beta ∈ [-0.5, +1.5] ET Z_alpha > -1.5
STRESSED : Z_beta_high > +1.5 ET Z_alpha < -1.0
RELAXED  : Z_alpha > +1.0 ET Z_beta < -0.5
NEUTRAL  : tout le reste
```

Hystérésis : 3 époques consécutives requises pour changer d'état (~3 s).

---

## API REST

| Méthode | Route | Description |
|---|---|---|
| GET | `/api/status` | État complet (ESP32, baseline, électrodes, REC) |
| GET | `/api/electrode` | État électrodes AD8232 |
| POST | `/api/analyze` | Rapport session DSP |
| POST | `/api/baseline/finalise` | Finalise la baseline individuelle |
| POST | `/api/recording/start` | Démarre enregistrement CSV |
| POST | `/api/recording/stop` | Arrête enregistrement CSV |
| GET | `/api/recording/export` | Télécharge le dernier CSV signal |
| POST | `/api/wifi/configure` | Envoie config WiFi à l'ESP32 |
| POST | `/api/wifi/use_saved` | Utilise un réseau mémorisé |
| POST | `/api/wifi/reset` | Efface réseaux mémorisés |
| GET | `/api/wifi/networks` | Réseaux WiFi mémorisés sur l'ESP32 |

Documentation interactive disponible sur `http://localhost:8000/docs`.

---

## WebSocket `/ws`

### Messages entrants (serveur → frontend)

```jsonc
// Init connexion
{ "type": "init", "esp32_connected": bool, "esp32_ip": "...",
  "wifi_configured": bool, "baseline_ok": bool, "electrode_ok": bool }

// Sample EEG (toutes les 4 samples → ~62 Hz)
{ "type": "eeg", "ts": int, "uv": float, "filtered": float,
  "electrode_ok": bool, "batt_V": float,
  "bands": { "delta": float, "theta": float, ... },
  "state": "focused|stressed|relaxed|neutral|invalid",
  "cqe_score": int, "cqe_label": "good|fair|poor|invalid",
  "cal_progress": float,
  "raw_metrics": { "rms_raw": float, "peak": float, "dc_uv": float } }

// Époque acceptée
{ "type": "epoch", "epoch_idx": int, "timestamp": "ISO",
  "features": { "rel_alpha": float, "engagement": float, ... },
  "eog_detected": bool, "emg_suspect": bool,
  "stats": { "total": int, "accepted": int, "rejected": int } }

// Époque rejetée
{ "type": "epoch_rejected", "reason": "flat_line|emg|electrode_off|...",
  "total": int, "rejected": int }

// Statut électrodes (heartbeat 2 Hz)
{ "type": "electrode", "electrode_ok": bool,
  "fp2_connected": bool, "m2_connected": bool }

// Statut ESP32
{ "type": "esp32_status", "connected": bool, "ip": "..." }

// Résultat WiFi
{ "type": "wifi_result", "success": bool, "ip": "...", "ssid": "..." }

// Baseline prête
{ "type": "baseline_ready", "success": bool }
```

### Commandes sortantes (frontend → serveur)

```jsonc
{ "command": "FINALISE_BASELINE" }
{ "command": "START_REC" }
{ "command": "STOP_REC" }
{ "command": "ANALYZE_NOW" }
```

---

## Intégration IA — Guide développeur

Ce backend est conçu pour s'interfacer avec des modèles d'IA. Voici les points d'extension clés.

### Point d'injection n°1 : post-époque dans `EpochExtractor._process()`

Chaque époque acceptée retourne un dict `features` avec 25+ valeurs numériques. C'est ici qu'un modèle de classification peut être appelé :

```python
# dsp/epochs.py — dans _process(), après extract_features()
features = extract_features(filtered, db_powers, emg_ratio=emg_ratio)

# ── INJECTION IA ──────────────────────────────────────────
# from your_ai_module import predict_state
# ai_result = predict_state(features)
# features["ai_state"] = ai_result["label"]
# features["ai_confidence"] = ai_result["confidence"]
# ─────────────────────────────────────────────────────────
```

Le dict `features` est ensuite transmis tel quel dans le message WebSocket `epoch`.

### Point d'injection n°2 : `CognitiveStateClassifier.update()` dans `processor.py`

La classification Z-score actuelle peut être remplacée ou complétée par un modèle ML :

```python
# dsp/processor.py — dans RealTimeProcessor.push()
# Remplacer ou augmenter la classification Z-score :
state = self._classifier.update(bands_rel, self._cqe_score, feat.get("emg_ratio"))
# → Appeler ici votre modèle : CNN-LSTM, SVM, XGBoost, etc.
```

### Point d'injection n°3 : boucle de diffusion dans `api.py`

La boucle `processing_loop()` broadcast toutes les données en temps réel. Vous pouvez y injecter des prédictions IA dans le payload WebSocket :

```python
# api.py — dans processing_loop(), avant ws_manager.broadcast(payload)
# payload["ai_prediction"] = my_model.predict(flt)
await ws_manager.broadcast(payload)
```

### Vecteur d'entrée recommandé pour un modèle IA

Pour un classifieur entraîné sur des époques EEG :

```python
feature_vector = [
    features["rel_delta"],   features["rel_theta"],
    features["rel_alpha"],   features["rel_beta"],
    features["rel_gamma_low"],
    features["engagement"],  features["stress_idx"],
    features["hjorth_mobility"], features["hjorth_complexity"],
    features["fractal_dim"], features["spectral_entropy"],
    features["pac_theta_gamma"], features["sef95"],
]
# Shape : (13,) par époque — ou (N, 13) pour un batch
```

### Enregistrement CSV pour entraînement

Activer via POST `/api/recording/start` → génère deux CSV dans `recordings/` :
- `signal_YYYYMMDD_HHMMSS.csv` — signal brut + filtré, 250 Hz
- `epochs_YYYYMMDD_HHMMSS.csv` — une ligne par époque avec toutes les features

Ces CSV peuvent être utilisés directement pour entraîner/évaluer vos modèles.

---

## Structure des fichiers

```
backend-signal/
├── assembly.py              # Point d'entrée principal
├── api.py                   # FastAPI REST + WebSocket + boucle DSP
├── tcp_receiver.py          # TCP server ESP32 → Python
├── wifi_manager.py          # UDP WiFi manager
├── __init__.py
│
├── dsp/
│   ├── __init__.py          # Exports publics du module DSP
│   ├── processor.py         # RealTimeProcessor + CognitiveStateClassifier
│   ├── epochs.py            # EpochExtractor + PreprocessingPipeline
│   ├── features.py          # extract_features(), higuchi_fd(), sef95
│   ├── filters.py           # FilterBank — Golden Filter
│   ├── artifacts.py         # ElectrodeMonitor, ArtifactDetector, CQE
│   └── NEUROCAP_DSP_PIPELINE.md
│
├── recording/
│   └── csv_handler.py       # Helpers CSV (appelé depuis api.py)
│
└── utils/
    └── constants.py         # FS=250, ports réseau, bandes, seuils
```

---

## Constantes importantes

```python
FS         = 250  # Hz — fréquence d'échantillonnage ADS1115
TCP_PORT   = 9000 # port streaming EEG
UDP_LISTEN = 4322 # annonces ESP32
UDP_CONFIG = 4320 # envoi config WiFi
UDP_STATUS = 4323 # résultats WiFi
EPOCH_SEC  = 2.0  # durée époque (secondes)
EPOCH_SAMP = 500  # samples par époque
```

---

## Notes importantes

- **Électrodes** : Fp2 (actif) + M2 (référence) + M1 (masse). Toujours Ag/AgCl sec.
- **WiFi** : ESP32 uniquement 2.4 GHz. Brancher le PC sur le hotspot `NeuroCap-XXXX` avant la configuration.
- **Baseline** : obligatoire pour activer la classification Z-score. Durée minimale : 10 époques propres (~40 s).
- **CQE** : score de qualité 0-100. En dessous de 60, l'état est forcé à `invalid`.
- **Thread safety** : `sample_queue` est thread-safe. Les callbacks WiFi/TCP utilisent `asyncio.run_coroutine_threadsafe` pour broadcaster vers le WebSocket.
