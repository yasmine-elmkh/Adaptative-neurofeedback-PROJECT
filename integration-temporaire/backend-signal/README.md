# backend-signal — NeuroCap EEG · Serveur Python temps réel

Serveur Python complet pour l'acquisition, le traitement DSP, la classification ML, le protocole neurofeedback adaptatif et la diffusion WebSocket/REST du signal EEG capté par l'ESP32 via le casque NeuroCap.

---

## Architecture globale

```
                         ┌──────────────────────────────────────────────────────┐
                         │                   backend-signal                     │
                         │                                                      │
  ESP32 (ADS1115+AD8232) │  assembly.py  ──── orchestre ─────────────────────  │
         │               │       │                                              │
  TCP :9000 ─────────────►  TCPReceiver ──► sample_queue ──► api.py            │
  UDP :4322 ◄────────────►  WifiManager ◄─────────────────────────             │
  UDP :4323               │                                                    │
                          │  api.py (FastAPI :8765)                             │
                          │   ├── processing_loop()  ←── EEG sample_queue       │
                          │   │    ├── RealTimeProcessor.push()                 │
                          │   │    │    ├── FilterBank (IIR, temps réel)        │
                          │   │    │    ├── EpochExtractor (4 s, 75% overlap)   │
                          │   │    │    │    ├── ArtifactDetector               │
                          │   │    │    │    ├── PreprocessingPipeline          │
                          │   │    │    │    ├── extract_features() ×27         │
                          │   │    │    │    ├── z-score → FeatEng ×63         │
                          │   │    │    │    └── MLClassifier.predict()         │
                          │   │    │    └── CognitiveStateClassifier (Z-score)  │
                          │   │    └── WS broadcast → Frontend React            │
                          │   ├── REST /api/*                                   │
                          │   └── WS  /ws                                       │
                          │                                                      │
                          │  feedback/    ── neurofeedback Thompson Sampling    │
                          │  protocol/    ── protocole 15 séances Mou 2024     │
                          │  recording/   ── CSV signal + époques               │
                          └──────────────────────────────────────────────────────┘
                                                │
                              WebSocket ws://localhost:8765/ws
                              REST      http://localhost:8765/api/*
                                                │
                                         Frontend React
                                         (frontend-signal)
```

---

## Installation

### Prérequis

- Python 3.10+
- Les modèles ML dans `models/baseline_FeatEng/baseline_models/`

### Dépendances

```bash
pip install fastapi uvicorn scipy numpy pywavelets websockets lightgbm joblib httpx supabase
```

| Package | Version | Usage |
|---|---|---|
| `fastapi` | ≥0.100 | Framework REST + WebSocket |
| `uvicorn` | ≥0.23 | Serveur ASGI |
| `scipy` | ≥1.11 | Filtres IIR/FIR, Welch PSD |
| `numpy` | ≥1.25 | Traitement signal |
| `pywavelets` | ≥1.4 | DWT db4 (features FeatEng) |
| `lightgbm` | ≥4.0 | Classifieur LightGBM |
| `joblib` | ≥1.3 | Chargement modèle sérialisé |
| `supabase` | ≥2.0 | Stockage médias + progression |

### Démarrage

```bash
cd backend-signal
python assembly.py
```

Affichage au démarrage :

```
═══════════════════════════════════════════
  NeuroCap EEG v8.0 — Backend Signal
  API  : http://0.0.0.0:8765/api/status
  WS   : ws://0.0.0.0:8765/ws
  Docs : http://localhost:8765/docs
═══════════════════════════════════════════
```

---

## Structure des fichiers

```
backend-signal/
├── assembly.py                  # Point d'entrée — orchestre tous les composants
├── api.py                       # FastAPI : REST + WebSocket + boucle DSP async
├── tcp_receiver.py              # Serveur TCP :9000 — flux CSV depuis l'ESP32
├── wifi_manager.py              # UDP :4322/:4323 — config WiFi ESP32
├── supabase_client.py           # Client Supabase (médias, sessions)
├── __init__.py
│
├── dsp/                         # Pipeline DSP complet
│   ├── processor.py             # RealTimeProcessor + CognitiveStateClassifier
│   ├── epochs.py                # EpochExtractor + PreprocessingPipeline
│   ├── features.py              # extract_features() — 27 features v8.0
│   ├── filters.py               # FilterBank — Golden Filter [1-45 Hz]
│   ├── artifacts.py             # ElectrodeMonitor, ArtifactDetector, CQE
│   ├── ml_classifier.py         # MLClassifier LightGBM — 63 features FeatEng
│   ├── file_processor.py        # Analyse offline de fichiers CSV EEG
│   └── __init__.py
│
├── feedback/                    # Moteur neurofeedback adaptatif
│   ├── feedback.py              # Routes FastAPI /api/feedback/*
│   ├── recommender.py           # Orchestrateur Thompson Sampling
│   ├── thompson_sampling.py     # Bandit multi-bras bayésien
│   ├── session_state.py         # État de session en mémoire
│   ├── media_selector.py        # Sélection médias depuis Supabase
│   ├── media_analyzer.py        # Analyse delta α/β post-stimulus
│   ├── bridge.py                # Pont EEG → état → recommandation
│   └── __init__.py
│
├── protocol/                    # Protocole 15 séances Mou et al. 2024
│   ├── neurofeedback_protocol.py # Routes FastAPI /api/protocol/*
│   ├── session_manager.py        # Gestion séances individuelles
│   ├── palier_manager.py         # Paliers P1→P4, facteurs de seuil
│   ├── threshold_adapter.py      # Adaptation inter-blocs alpha
│   ├── progression_tracker.py    # Historique multi-séances Supabase
│   ├── profile_detector.py       # Profil neuro-individuel
│   ├── bilan_generator.py        # Bilans S5/S10/S15
│   └── __init__.py
│
├── recording/
│   └── csv_handler.py           # Écriture CSV signal + époques
│
├── routes/
│   └── feedback.py              # Router FastAPI pour le module feedback
│
└── utils/
    └── constants.py             # FS=250, ports réseau, bandes, seuils
```

---

## Protocole réseau

### 1. Flux TCP :9000 — streaming EEG depuis l'ESP32

L'ESP32 se connecte et envoie des lignes CSV à 250 Hz :

```
# Format compact (4 colonnes)
timestamp_ms,raw_adc,voltage_mV,pkt_id

# Format complet (8 colonnes)
timestamp_us,raw_adc,voltage_mV,batt_V,lo_plus,lo_minus,lead_off,pkt_id
```

`TCPReceiver` applique un filtre DC adaptatif (IIR 0.05 Hz) et pousse chaque sample dans `sample_queue`.

### 2. UDP — configuration WiFi

| Port | Direction | Message |
|---|---|---|
| 4322 (écoute) | ESP32 → Serveur | `ESP_EEG_AP:<ssid>` ou `ESP_EEG:<ip>` |
| 4320 (envoi) | Serveur → ESP32 | `WIFI_CONFIG:<ssid>:<pwd>` |
| 4323 (écoute) | ESP32 → Serveur | `WIFI_OK:<ip>:<ssid>` ou `WIFI_FAILED:<ssid>:<reason>` |

Le serveur broadcast `EEG_SERVER_IP:<ip>` toutes les 2 s pour permettre à l'ESP32 de trouver le PC.

---

## Pipeline DSP

### Traitement échantillon par échantillon (250 Hz)

```
uv brut (ESP32, ~1.65M µV avec DC offset)
    │
    ├─► DCRemover (TCP) — IIR HP 0.05 Hz
    │
    ├─► FilterBank.filter_sample() — filtre causal temps réel
    │     Notch 50 Hz → Notch 100 Hz → BP [1-45 Hz] Butterworth ord. 4
    │
    ├─► ContactQualityEstimator (fenêtre 500 ms) → CQE score 0-100
    │
    ├─► Welch temps réel (fenêtre 10 s, mise à jour 1 Hz)
    │
    └─► EpochExtractor.push() → si fenêtre 4 s complète → _process()
```

### Pipeline par époque (4 s, overlap 75 %)

```
raw_epoch (1000 samples @ 250 Hz)
    │
    ├─► ArtifactDetector.is_bad()
    │     flat_line / extreme_peak / electrode_off / emg_reject
    │     → si bad → epoch_rejected (raison + compteurs)
    │
    ├─► PreprocessingPipeline.process()
    │     median_sub → Notch 50 → Notch 100 → BP [1-45 Hz] → Wavelet db4
    │
    ├─► normalise_db() → dB vs baseline individuelle (QEEG standard)
    │
    ├─► extract_features() → 27 features v8.0 (dashboard temps réel)
    │
    ├─► z-score époque → epoch_z
    │
    └─► _extract_feateng(epoch_z) → 63 features FeatEng → MLClassifier
```

### Features extraites — 27 features v8.0 (dashboard)

| Catégorie | Features |
|---|---|
| Puissances relatives | `rel_delta`, `rel_theta`, `rel_alpha`, `rel_beta`, `rel_beta_high`, `rel_gamma_low` |
| Ratios cognitifs | `engagement` (β/α+θ), `stress_idx` (β/α), `theta_alpha`, `alpha_beta` |
| Hjorth | `hjorth_activity`, `hjorth_mobility`, `hjorth_complexity` |
| Complexité | `fractal_dim` (Higuchi HFD), `spectral_entropy`, `sef95` |
| Amplitude | `rms_uv`, `mean_amp`, `skewness`, `kurtosis`, `zcr` |
| PAC | `pac_theta_gamma` (couplage phase-amplitude θ→γ) |
| dB baseline | `db_delta`, `db_theta`, `db_alpha`, `db_beta` |

### Features FeatEng — 63 features (classifieur ML)

```
epoch_z (z-scorée) → extract_all_features()
  │
  ├── Cat. 1 — PSD Welch (5 features)
  │     Pd, Pt, Pa, Pb, Pg  (bandes d'entraînement : δ 0.5-4, θ 4-8, γ 30-40)
  │
  ├── Cat. 2 — Ratios cognitifs (5 features)
  │     TBR, ABR, EI, TAR, RelEnergy_beta
  │
  ├── Cat. 3 — Hjorth + temporel (6 features)
  │     Activity, Mobility, Complexity, Power, MeanAmp, ZCR
  │
  ├── Cat. 4 — DWT db4 niveau 4 (20 features)
  │     5 sous-bandes × {mean, std, energy, entropy_shannon}
  │
  ├── Cat. 5 — Texturales (16 features)
  │     skewness, kurtosis, IQR, RMS, peak_to_peak, crest_factor
  │     + dwt_Xband_skew/kurt (5 sous-bandes × 2)
  │
  ├── Cat. 6 — Non-linéaires (5 features)
  │     ApEn, SampEn, PermEn, SpectralEn, HFD (Higuchi kmax=10)
  │
  └── Cat. 7 — Transitions (6 features)
        pct_up, pct_down, pct_flat, up_streak, down_streak, trans_freq
        (inspiré QuadTPat, Sci. Rep. 2024)
        ──────────────────────────────────
  TOTAL : 63 features  |  < 40 ms/époque  |  LightGBM LOSO validé
```

### Bandes fréquentielles

| Bande | DSP v8.0 (dashboard) | FeatEng (classifieur) | Justification |
|---|---|---|---|
| delta | 1–4 Hz | 0.5–4 Hz | HP 1 Hz élimine drift polarisation |
| theta | **6–8 Hz** | 4–8 Hz | 4-6 Hz contaminé EOG résiduel (Klimesch 1999) |
| alpha | 8–13 Hz | 8–13 Hz | Standard international 10-20 |
| beta | 13–30 Hz | 13–30 Hz | Standard |
| beta_high | 20–30 Hz | — | Stress index |
| gamma_low | 30–45 Hz | 30–40 Hz | LP 45/40 Hz |

### Classification d'état cognitif — Z-score heuristique

`CognitiveStateClassifier` produit : **focused / stressed / relaxed / neutral / invalid**

```
INVALID  : CQE < 60  OU  emg_ratio > 0.20
FOCUSED  : Z_theta > +1.0  ET  Z_beta ∈ [-0.5, +1.5]  ET  Z_alpha > -1.5
STRESSED : Z_beta_high > +1.5  ET  Z_alpha < -1.0
RELAXED  : Z_alpha > +1.0  ET  Z_beta < -0.5
NEUTRAL  : tout le reste
```

Hystérésis : 3 époques consécutives requises pour changer d'état (~3 s). Z-scores calculés vs baseline individuelle du sujet.

### Classification ML LightGBM

`MLClassifier` produit : **concentration / stress** avec score de confiance.

```python
# Sortie ml_prediction :
{
  "concentration": 0.8342,   # probabilité [0, 1]
  "stress":        0.1658,
  "state":         "concentration",
  "confidence":    0.8342,
  "uncertain":     false      # true si confidence < 0.60
}
```

Modèle : `models/baseline_FeatEng/baseline_models/LightGBM_concentration_vs_stress.joblib`
Scaler : `models/baseline_FeatEng/baseline_models/LightGBM_scaler.joblib`
Validation : LOSO (Leave-One-Subject-Out)

---

## API REST complète

### Endpoints EEG / Signal

| Méthode | Route | Description |
|---|---|---|
| GET | `/api/status` | État complet (ESP32, baseline, électrodes, REC, CQE) |
| GET | `/api/electrode` | État électrodes AD8232 (Fp2, M2, qualité contact) |
| POST | `/api/analyze` | Rapport session DSP (états, ratios, qualité) |
| POST | `/api/baseline/finalise` | Finalise la baseline individuelle (≥10 époques) |
| GET | `/api/recording/export` | Télécharge le dernier CSV signal (signal_*.csv) |
| POST | `/api/recording/start` | Démarre enregistrement CSV (signal + époques) |
| POST | `/api/recording/stop` | Arrête enregistrement CSV |

### Endpoints WiFi

| Méthode | Route | Description |
|---|---|---|
| POST | `/api/wifi/configure` | Envoie SSID + mot de passe à l'ESP32 |
| POST | `/api/wifi/use_saved` | Bascule sur un réseau mémorisé dans l'ESP32 |
| POST | `/api/wifi/reset` | Efface tous les réseaux mémorisés |
| GET | `/api/wifi/networks` | Liste des réseaux mémorisés sur l'ESP32 |

### Endpoints Neurofeedback

| Méthode | Route | Description |
|---|---|---|
| POST | `/api/feedback/session/start` | Démarre une session feedback (userId, objective) |
| POST | `/api/feedback/recommend` | Recommande un média (Thompson Sampling) |
| POST | `/api/feedback/submit` | Soumet un retour utilisateur (like, ressenti, notes) |
| POST | `/api/feedback/next` | Média suivant dans la session |
| POST | `/api/feedback/skip` | Passe le média actuel |
| POST | `/api/feedback/session/end` | Clôture la session (rapport + deltas α/β) |
| POST | `/api/feedback/justify` | Justification IA pourquoi ce média pour cet état |
| POST | `/api/feedback/analyze_file` | Analyse d'un fichier EEG CSV offline |

### Endpoints Protocole 15 séances

| Méthode | Route | Description |
|---|---|---|
| GET | `/api/protocol/user/{user_id}` | Progression complète de l'utilisateur |
| POST | `/api/protocol/session/start` | Démarre une séance (questionnaire pré) |
| POST | `/api/protocol/session/baseline` | Calcule le seuil alpha depuis la baseline |
| POST | `/api/protocol/bloc/end` | Termine un bloc (taux succès, adaptation seuil) |
| POST | `/api/protocol/session/end` | Clôture la séance (questionnaire post, rapport) |
| GET | `/api/protocol/bilan/{user_id}/{session_n}` | Bilan S5/S10/S15 |

Documentation interactive Swagger disponible sur `http://localhost:8765/docs`.

---

## WebSocket `/ws`

### Messages serveur → frontend

```jsonc
// Connexion initiale
{
  "type": "init",
  "esp32_connected": true,
  "esp32_ip": "192.168.4.2",
  "wifi_configured": true,
  "baseline_ok": false,
  "electrode_ok": true,
  "fp2_connected": true,
  "m2_connected": true
}

// Sample EEG — ~62 Hz (1 sur 4, pour réduire la charge WS)
{
  "type": "eeg",
  "ts": 1748342100000,
  "uv": 1650234.5,              // tension brute µV (avec DC offset)
  "filtered": -12.345,          // signal filtré µV (centré zéro)
  "electrode_ok": true,
  "fp2_connected": true,
  "m2_connected": true,
  "batt_V": 3.85,
  "bands": {
    "delta": 0.12, "theta": 0.18, "alpha": 0.35,
    "beta": 0.25, "beta_high": 0.08, "gamma_low": 0.02
  },
  "state": "relaxed",
  "cqe_score": 82,              // 0-100 — contact quality
  "cqe_label": "good",          // good | fair | poor | invalid
  "cal_progress": 67.4,         // % baseline complétée
  "raw_metrics": { "rms_raw": 18.4, "peak": 45.2, "dc_uv": 1650230.1 }
}

// Époque acceptée (toutes les ~1 s avec 75% overlap)
{
  "type": "epoch",
  "epoch_idx": 42,
  "timestamp": "2026-05-23T10:30:00.123Z",
  "features": {                  // 27 features v8.0 (dashboard)
    "rel_alpha": 0.312,
    "engagement": 0.87,
    "stress_idx": 0.41,
    "hjorth_activity": 142.3,
    // ...
  },
  "ml_features": {               // 63 features FeatEng (classifieur ML)
    "delta_power": 0.18, "theta_power": 0.22, "alpha_power": 0.35,
    "approx_entropy": 0.71, "hfd": 1.73,
    // ...
  },
  "ml_prediction": {
    "concentration": 0.8342,
    "stress": 0.1658,
    "state": "concentration",
    "confidence": 0.8342,
    "uncertain": false
  },
  "eog_detected": false,
  "emg_suspect": false,
  "stats": { "total": 42, "accepted": 38, "rejected": 4 }
}

// Époque rejetée
{
  "type": "epoch_rejected",
  "reason": "emg",              // flat_line | emg | electrode_off | extreme_peak
  "total": 43, "rejected": 5
}

// Statut ESP32
{ "type": "esp32_status", "connected": true, "ip": "192.168.4.2" }

// Baseline prête
{ "type": "baseline_ready", "success": true }

// Résultat configuration WiFi
{ "type": "wifi_result", "success": true, "ip": "192.168.1.42", "ssid": "MonWifi" }
```

### Commandes frontend → serveur

```jsonc
{ "command": "FINALISE_BASELINE" }   // finalise la baseline (10+ époques propres)
{ "command": "START_REC" }            // démarre enregistrement CSV
{ "command": "STOP_REC" }             // arrête enregistrement CSV
{ "command": "ANALYZE_NOW" }          // génère rapport session DSP
```

---

## Module Neurofeedback — `feedback/`

### Architecture Thompson Sampling

Le moteur neurofeedback adaptatif implémente un **bandit multi-bras bayésien** (Thompson Sampling) pour sélectionner les médias thérapeutiques.

```
session_start(userId, objective)
    │
    ├── SessionState créé (panier vide, historique, profil)
    │
    recommend(sessionId, eegState, features)
    │   ├── MediaSelector → filtrage Supabase par état + type
    │   ├── ThompsonSampling → tire Beta(α_i, β_i) pour chaque candidat
    │   ├── Anti-habitude → pénalise le type vu récemment
    │   └── → média retourné (id, type, url Cloudinary, metadata)
    │
    submit_feedback(sessionId, media, liked, ressenti, noteConc, noteStress)
    │   ├── MediaAnalyzer → calcule Δα et Δβ depuis les features EEG
    │   ├── ThompsonSampling.update() → β(α_i, β_i) mise à jour
    │   └── SessionState.history ← nouvel item
    │
    end_session(sessionId)
        └── rapport_ia (Claude Haiku), deltas globaux, efficacy %
```

### Structure des médias (Supabase)

```
Table: medias
  id, type (audio|image|video|game),
  url (Cloudinary CDN),
  tags (JSON), target_states (JSON array),
  alpha_boost (float), beta_reduction (float),
  fichier_jeu (pour type=game: CSV ou JSON)
```

812+ médias indexés. Cloudinary gère la livraison CDN (image, audio, vidéo).

---

## Module Protocole — `protocol/`

### Architecture 15 séances (Mou et al., npj Science of Learning 2024)

```
Séance N
  │
  ├── Phase 1 : Baseline (2 min, yeux fermés)
  │     → collecte rel_alpha → baseline_alpha
  │
  ├── Phase 2 : IAPF (1 min, yeux ouverts)
  │     → mesure Individual Alpha Peak Frequency
  │
  ├── Phase 3-7 : 5 Blocs neurofeedback (3 min chacun)
  │     │   ← Pause inter-bloc 20 s →
  │     ├── ThresholdAdapter : seuil = f(P_alpha_hist, P_alpha_today, facteur_palier)
  │     ├── Countdown + barre alpha en temps réel
  │     └── BlocResult : taux_succes, seuil_used, alpha_mean
  │
  ├── Adaptation inter-blocs (ThresholdAdapter)
  │     taux > 60% → seuil × 1.05  (montée)
  │     taux < 40% → seuil × 0.95  (descente)
  │
  └── Phase 8 : Repos final (3 min)
        → Session enregistrée dans Supabase (progression_tracker)
```

### Paliers

| Palier | Séances | Facteur min | Facteur max | Objectif |
|---|---|---|---|---|
| P1 — Découverte | S1–S3 | 0.85 | 0.90 | Prise en main, confort |
| P2 — Apprentissage | S4–S7 | 0.95 | 1.10 | Régulation consciente |
| P3 — Consolidation | S8–S12 | 1.10 | 1.25 | Automatisation |
| P4 — Maîtrise | S13–S15 | 1.25 | 1.40 | Généralisation |

### Formule seuil journalier

```
Seuil = (0.70 × P_alpha_historique + 0.30 × P_alpha_aujourd'hui) × facteur_palier
```

Bilans obligatoires à S5, S10 et S15 (`bilan_generator.py`) : rapport de progression globale, courbe taux de succès, recommandations.

---

## Constantes importantes — `utils/constants.py`

```python
FS          = 250       # Hz — fréquence d'échantillonnage ADS1115
TCP_PORT    = 9000      # port streaming EEG depuis l'ESP32
UDP_LISTEN  = 4322      # annonces ESP32
UDP_CONFIG  = 4320      # envoi config WiFi vers ESP32
UDP_STATUS  = 4323      # résultats WiFi depuis ESP32
SERVER_PORT = 8765      # port FastAPI (WS + REST)

EPOCH_SEC   = 4.0       # durée fenêtre époque (secondes)
EPOCH_SAMP  = 1000      # samples par époque (4 s × 250 Hz)
OVERLAP     = 0.75      # overlap entre époques (75%)
MIN_EPOCHS_BASELINE = 10

CONFIDENCE_THR = 0.60   # seuil ML "uncertain"
CQE_MIN_VALID  = 60     # score qualité minimum pour état valide
```

---

## Électrodes et hardware

| Paramètre | Valeur |
|---|---|
| Canal actif | Fp2 (frontopariétal droit) |
| Référence | M2 (mastoïde droit) |
| Masse | M1 (mastoïde gauche) |
| Électrodes | Ag/AgCl sec (Disposables ou réutilisables) |
| ADC | ADS1115, GAIN_TWO → 62.5 µV/LSB |
| Amplificateur | AD8232 (INA + filtre HP 0.5 Hz + LP 40 Hz intégrés) |
| WiFi | ESP32 2.4 GHz uniquement |
| Débit TCP | ~250 lignes CSV/s = ~6 Ko/s |

---

## Enregistrement CSV

Activer : `POST /api/recording/start`

Génère deux fichiers dans `recordings/` :

```
signal_YYYYMMDD_HHMMSS.csv     — 250 Hz — colonnes: ts, uv_brut, filtered, bands...
epochs_YYYYMMDD_HHMMSS.csv     — 1 ligne/époque — toutes les 27 features v8.0
```

Ces CSV sont exploitables directement pour l'entraînement de modèles ML ou l'analyse offline.

---

## Points d'extension IA

### 1. Post-époque dans `dsp/epochs.py`

```python
# Après extract_features()
features = extract_features(filtered, db_powers, emg_ratio=emg_ratio)

# ── INJECTION IA ──────────────────────────────
# from your_model import predict
# features["ai_state"]      = predict(features)["label"]
# features["ai_confidence"] = predict(features)["confidence"]
```

### 2. Classifieur Z-score dans `dsp/processor.py`

```python
# Remplacer ou augmenter :
state = self._classifier.update(bands_rel, self._cqe_score, feat.get("emg_ratio"))
# → Votre modèle CNN-LSTM / SVM / XGBoost ici
```

### 3. Payload WebSocket dans `api.py`

```python
# Avant broadcast :
# payload["external_prediction"] = my_external_model.predict(flt)
await ws_manager.broadcast(payload)
```

---

## Notes importantes

- **Seul le signal `filtered`** est utile côté frontend — `uv` brut contient le DC offset (~1.65M µV ADS1115).
- **Thread safety** : `sample_queue` est thread-safe via `asyncio.Queue`. Les callbacks TCP/UDP utilisent `asyncio.run_coroutine_threadsafe` pour broadcaster via WS.
- **Baseline obligatoire** : ≥10 époques propres (~40 s) avant activation de la classification Z-score.
- **WiFi** : ESP32 uniquement 2.4 GHz. Hotspot `NeuroCap-XXXX` créé automatiquement si pas de réseau configuré.
- **Port 8765** : choisi car 8000 = PostgreSQL, 8080 = Apache dans cet environnement.
