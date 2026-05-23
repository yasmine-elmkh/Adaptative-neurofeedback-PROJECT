# Architecture Neurofeedback — NeuroCap EEG

Documentation technique complète du système de neurofeedback adaptatif : protocole 15 séances (Mou et al. 2024), feedback libre par Thompson Sampling, pipeline signal EEG, et interface unifiée NeuroFeedbackHub.

---

## Vue d'ensemble du système

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         SYSTÈME NEUROFEEDBACK NEUROCAP                       │
│                                                                              │
│  ┌──────────┐    TCP 250Hz    ┌─────────────────────────────────────────┐    │
│  │  ESP32   │────────────────►│           backend-signal                │    │
│  │ ADS1115  │◄───────────────│                                         │    │
│  │ AD8232   │    UDP WiFi    │  ┌─────────┐  ┌──────────┐  ┌────────┐ │    │
│  └──────────┘                │  │   DSP   │  │ Feedback │  │Protocol│ │    │
│                              │  │pipeline │  │ Thompson │  │ 15 séa │ │    │
│                              │  └────┬────┘  └────┬─────┘  └───┬────┘ │    │
│                              │       │             │             │      │    │
│                              │       └──────── FastAPI ─────────┘      │    │
│                              └──────────────┬──────────────────────────┘    │
│                                             │ WS + REST                     │
│                              ┌──────────────▼──────────────────────────┐    │
│                              │          frontend-signal (React)        │    │
│                              │                                         │    │
│                              │  ┌───────────────────────────────────┐  │    │
│                              │  │       NeuroFeedbackHub            │  │    │
│                              │  │  ┌──────────────┐ ┌────────────┐ │  │    │
│                              │  │  │  Protocole   │ │  Feedback  │ │  │    │
│                              │  │  │  15 séances  │ │   libre    │ │  │    │
│                              │  │  └──────────────┘ └────────────┘ │  │    │
│                              │  │       [Widget EEG temps réel]    │  │    │
│                              │  └───────────────────────────────────┘  │    │
│                              └─────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Partie I — Pipeline EEG temps réel

### 1.1 Acquisition matérielle

| Composant | Rôle | Paramètre clé |
|---|---|---|
| ADS1115 | ADC 16 bits | GAIN_TWO → 62.5 µV/LSB |
| AD8232 | Amplificateur ECG/EEG | HP 0.5 Hz + LP 40 Hz intégrés |
| ESP32 | Microcontrôleur WiFi | TCP 250 Hz, UDP config |
| Fp2 | Électrode active | Frontopariétal droit (signal cognitif) |
| M2 | Référence | Mastoïde droit |
| M1 | Masse | Mastoïde gauche |

### 1.2 Traitement en temps réel (250 Hz)

```
Échantillon brut (uv ~ 1.65M µV avec DC offset ADS1115)
    │
    ├─ 1. DCRemover (IIR HP 0.05 Hz) — dans TCPReceiver
    │       → retire la composante continue de l'amplificateur
    │
    ├─ 2. FilterBank.filter_sample() — filtrage causal en ligne
    │       Notch 50 Hz  → élimine secteur électrique
    │       Notch 100 Hz → élimine harmonique 50 Hz
    │       BP [1-45 Hz] Butterworth ordre 4
    │
    ├─ 3. ContactQualityEstimator (fenêtre 500 ms glissante)
    │       → CQE score 0-100 (qualité contact électrode)
    │       → CQE < 60 → état forcé INVALID
    │
    ├─ 4. Welch temps réel (fenêtre 10 s, mise à jour 1 Hz)
    │       → puissances spectrales pour affichage barres
    │
    └─ 5. EpochExtractor.push()
            → accumule les samples
            → déclenche _process() dès que 4 s complètes (1000 samples)
            → overlap 75% → nouvelle époque toutes les ~1 s
```

### 1.3 Pipeline par époque (4 s)

```
raw_epoch [1000 samples]
    │
    ├─ 1. ArtifactDetector.is_bad()
    │       flat_line   : std < seuil_min → électrode déconnectée
    │       extreme_peak: max|x| > 500 µV → artefact mouvement
    │       electrode_off: lead-off ADS1115 actif
    │       emg_reject  : ratio gamma > 0.35 → contraction musculaire
    │       → REJECTED → message epoch_rejected vers le frontend
    │
    ├─ 2. PreprocessingPipeline.process() — filtrage zéro-phase
    │       median_sub → center sur la médiane (plus robuste que moyenne)
    │       Notch 50 → Notch 100 → BP [1-45 Hz] (filtfilt, zéro déphasage)
    │       Wavelet db4 (débruitage adaptatif)
    │
    ├─ 3. normalise_db()
    │       → normalisation en dB par rapport à la baseline individuelle
    │       → standard QEEG (Thatcher 2003)
    │
    ├─ 4. extract_features() → 27 features v8.0 (dashboard)
    │       Puissances relatives, ratios cognitifs, Hjorth,
    │       complexité, amplitude, PAC theta→gamma
    │
    ├─ 5. z-score de l'époque → epoch_z
    │       (même normalisation que les données d'entraînement LightGBM)
    │
    ├─ 6. _extract_feateng(epoch_z) → 63 features FeatEng
    │       7 catégories : PSD, ratios, Hjorth, DWT, texturales,
    │       non-linéaires, transitions
    │
    └─ 7. MLClassifier.predict_from_dict(ml_features)
            → StandardScaler + LightGBM → { concentration, stress, confidence }
            → uncertain = true si confidence < 0.60
```

### 1.4 Features extraites

#### 27 features v8.0 — dashboard temps réel

```
Puissances relatives (6)  : rel_delta, rel_theta, rel_alpha,
                            rel_beta, rel_beta_high, rel_gamma_low
Ratios cognitifs (4)      : engagement (β/α+θ), stress_idx (β/α),
                            theta_alpha (θ/α), alpha_beta (α/β)
Hjorth (3)                : activity, mobility, complexity
Complexité (3)            : fractal_dim (Higuchi), spectral_entropy, sef95
Amplitude (5)             : rms_uv, mean_amp, skewness, kurtosis, zcr
PAC (1)                   : pac_theta_gamma (couplage phase-amplitude θ→γ)
dB baseline (4)           : db_delta, db_theta, db_alpha, db_beta
                            ─────────────────────────────────────────
                   TOTAL : 27 features  |  utilisées pour le dashboard
```

#### 63 features FeatEng — classifieur LightGBM

```
Cat. 1 — PSD Welch (5)       : Pd, Pt, Pa, Pb, Pg
                                (bandes δ 0.5-4, θ 4-8, α 8-13, β 13-30, γ 30-40)
Cat. 2 — Ratios cognitifs (5) : TBR (θ/β), ABR (α/β), EI (β/α+θ),
                                TAR (θ/α, p<0.001 ADHD), RelEnergy_beta
Cat. 3 — Hjorth + temporel (6): Activity, Mobility, Complexity,
                                Power, MeanAmp, ZCR
Cat. 4 — DWT db4 niv.4 (20)  : 5 sous-bandes × {mean, std, energy, entropy}
                                (db4 optimal : "Multiresolution EEG" 2018)
Cat. 5 — Texturales (16)      : skewness, kurtosis, IQR, RMS, peak2peak,
                                crest_factor + dwt_band×{skew,kurt} × 5
Cat. 6 — Non-linéaires (5)    : ApEn, SampEn, PermEn, SpectralEn,
                                HFD Higuchi (kmax=10)
Cat. 7 — Transitions (6)      : pct_up, pct_down, pct_flat,
                                up_streak, down_streak, trans_freq
                                (inspiré QuadTPat, Sci. Rep. 2024)
                                ─────────────────────────────────────────
                       TOTAL : 63 features  |  < 40 ms/époque  |  LOSO validé
```

### 1.5 Classification d'état cognitif

#### Z-score heuristique (temps réel — 5 états)

```python
# Baseline individuelle requise (≥ 10 époques, ~40 s)
# Z = (valeur_actuelle - baseline_mean) / baseline_std

INVALID  : CQE < 60  OU  emg_ratio > 0.20
FOCUSED  : Z_theta > +1.0  ET  Z_beta ∈ [-0.5, +1.5]  ET  Z_alpha > -1.5
STRESSED : Z_beta_high > +1.5  ET  Z_alpha < -1.0
RELAXED  : Z_alpha > +1.0  ET  Z_beta < -0.5
NEUTRAL  : reste

# Hystérésis : 3 époques consécutives pour changer d'état (~3 s)
```

#### LightGBM FeatEng (2 états + confidence)

```
Modèle : LightGBM_concentration_vs_stress.joblib
Scaler : LightGBM_scaler.joblib (StandardScaler)
Classes : Concentration / Stress
Validation : LOSO (Leave-One-Subject-Out)
Seuil incertitude : 0.60

Sortie : { concentration: float, stress: float,
           state: str, confidence: float, uncertain: bool }
```

---

## Partie II — Neurofeedback Feedback libre

### 2.1 Architecture Thompson Sampling

Le feedback libre utilise un **bandit multi-bras bayésien** (Thompson Sampling) pour sélectionner adapativement les meilleurs médias thérapeutiques pour chaque utilisateur.

```
┌────────────────────────────────────────────────────────────────────┐
│                  Moteur Feedback Libre                              │
│                                                                    │
│  État EEG ──────────────────────────────────────────────────────┐  │
│  (stressed / focused / relax / neutral)                          │  │
│                                                                  ▼  │
│  ┌──────────────────┐     ┌────────────────────────────────────┐ │  │
│  │  MediaSelector   │────►│       Thompson Sampling            │ │  │
│  │  (Supabase DB)   │     │                                    │ │  │
│  │                  │     │  Pour chaque média candidat i :    │ │  │
│  │  Filtre :        │     │    score_i ~ Beta(α_i, β_i)        │ │  │
│  │  • target_state  │     │    → tire aléatoirement            │ │  │
│  │  • type (audio,  │     │    → sélectionne argmax(score_i)   │ │  │
│  │    image, video, │     │                                    │ │  │
│  │    game)         │     │  Anti-habitude :                   │ │  │
│  │  • non vu récemm.│     │    pénalise le type vu récemment   │ │  │
│  └──────────────────┘     └────────────────┬───────────────────┘ │  │
│                                             │                     │  │
│  Média sélectionné ◄────────────────────────┘                     │  │
│  (id, type, url Cloudinary, metadata)                             │  │
│                                                                  │  │
│  ┌────────────────────────────────────────────────────────────┐  │  │
│  │  Post-stimulus : MediaAnalyzer                            │  │  │
│  │    Δα = rel_alpha_après - rel_alpha_avant                 │  │  │
│  │    Δβ = rel_beta_après  - rel_beta_avant                  │  │  │
│  │                                                            │  │  │
│  │  Mise à jour Thompson Sampling :                          │  │  │
│  │    if liked OR Δα > +0.05 → α_i += 1  (succès)          │  │  │
│  │    else                    → β_i += 1  (échec)            │  │  │
│  └────────────────────────────────────────────────────────────┘  │  │
└──────────────────────────────────────────────────────────────────┘  │
                                                                      │
```

### 2.2 Flux complet d'une session feedback libre

```
1. FeedbackSetup (configuration)
   ├── Détection état EEG (depuis features ou fichier CSV)
   ├── Choix objectif : stress_reduction | focus_enhancement | relaxation
   └── Choix type(s) média : audio | image | video | game

2. startSession(userId, objective) → sessionId

3. Boucle de session :
   │
   ├── recommend(sessionId, eegState, features, forcedType?)
   │   ├── MediaSelector → filtre DB par état + type + non-habituation
   │   ├── ThompsonSampling → score Beta → argmax → média
   │   └── → { id, type, url, fichier_jeu, alpha_boost }
   │
   ├── Affichage stimulus
   │   ├── AudioFeedback (lecteur audio + BreathingGuide si stress)
   │   ├── ImageFeedback (image nature + FixationPoint si relax)
   │   ├── VideoFeedback (vidéo relaxante)
   │   └── GameFeedback  (jeu cognitif adaptatif)
   │
   ├── FeedbackSelector (formulaire retour)
   │   ├── Like / Dislike (obligatoire)
   │   ├── Ressenti : 5 niveaux emoji
   │   └── Notes concentration + stress (1-5 étoiles)
   │
   ├── submitFeedback(sessionId, media, liked, ressenti, noteConc, noteStress)
   │   ├── MediaAnalyzer → calcule Δα, Δβ depuis features EEG
   │   ├── ThompsonSampling.update() → α_i ou β_i + 1
   │   └── SessionState.history ← item résultat
   │
   └── nextItem() / skipItem()

4. endSession(sessionId) → rapport
   ├── rapport_ia (Claude Haiku — analyse personnalisée)
   ├── deltas : { Δα_moyen, Δβ_moyen }
   ├── efficacy_pct (% items avec Δα > +0.05 ou liked)
   └── history (liste complète items + résultats)
```

### 2.3 Types de médias — 812+ items Supabase

| Type | Description | Algorithme sélection |
|---|---|---|
| Audio | Musique thérapeutique (nature, binaural, zen) | État → style sonore adapté |
| Image | Photographies nature (forêt, mer, montagne) | État → palette chromatique |
| Vidéo | Vidéos relaxantes (cascade, nuages, feu) | Durée adaptée à l'objectif |
| Jeu | Activité cognitive légère (Sudoku, Mémoire) | Difficulté adaptée au focus |

Livraison : Cloudinary CDN (réseau mondial, transcoding adaptatif).

### 2.4 Jeux cognitifs intégrés

| Jeu | Composant | Bénéfice cognitif |
|---|---|---|
| Sudoku 4×4 | `SudokuGame.jsx` | Logique, attention focalisée |
| Mémoire | `MemoryGame.jsx` | Mémoire de travail, reconnaissance |
| Calcul mental | `CalculGame.jsx` | Concentration, inhibition |
| Énigmes | `EnigmeGame.jsx` | Raisonnement, flexibilité |
| Taquin 3×3 | `PuzzleGame.jsx` | Planification, espace visuel |

### 2.5 Évaluation de l'efficacité

Un stimulus est considéré **efficace** si :
- `Δα > +0.050` (augmentation de la puissance alpha relative)
- **OU** `liked = true` (retour utilisateur positif)
- **OU** `Δβ < -0.050` (réduction du stress beta)

`efficacy_pct = nb_efficaces / nb_total × 100`

---

## Partie III — Protocole 15 séances (Mou et al. 2024)

### 3.1 Fondements scientifiques

Référence principale : **Mou et al. (2024)** — "Adaptive alpha neurofeedback training improves cognitive performance", _npj Science of Learning_.

Principes :
- Seuil alpha **individuel** (non normatif) calculé depuis la baseline du sujet
- **Adaptation inter-blocs** pour maintenir la difficulté optimale (zone de flow)
- **Progression par paliers** sur 15 séances pour l'ancrage à long terme
- **Bilans obligatoires** S5/S10/S15 pour évaluation et ajustement clinique

### 3.2 Structure d'une séance

```
┌───────────────────────────────────────────────────────────────────┐
│                    Séance Sn (~35-40 minutes)                      │
│                                                                   │
│  Phase 1 — Questionnaire pré-séance (2 min)                      │
│    Humeur / Énergie / Sommeil / Anxiété  (échelles 5 niveaux)    │
│                                                                   │
│  Phase 2 — Baseline (2 min, yeux fermés)                         │
│    → collecte rel_alpha → P_alpha_today                           │
│    → calcul seuil : S = (0.7×P_hist + 0.3×P_today) × facteur    │
│                                                                   │
│  Phase 3 — IAPF (1 min, yeux ouverts)                            │
│    → Individual Alpha Peak Frequency au repos                     │
│                                                                   │
│  Phase 4-8 — 5 Blocs neurofeedback (3 min chacun)               │
│    ┌─────────────────────────────────────────────────────────┐   │
│    │ BLOC k (3 min = 180 s)                                  │   │
│    │   Consigne : "Maintenez votre alpha au-dessus du seuil" │   │
│    │   Barre alpha en temps réel vs seuil                    │   │
│    │   Compte à rebours                                      │   │
│    │   taux_succes_k = nb_seconds_above_threshold / 180      │   │
│    └─────────────────────────────────────────────────────────┘   │
│    Pause inter-bloc : 20 s (repos, respiration)                  │
│                                                                   │
│    Adaptation inter-blocs (ThresholdAdapter) :                   │
│      taux_k > 60% → seuil × 1.05 (montée difficulté)            │
│      taux_k < 40% → seuil × 0.95 (descente difficulté)          │
│      40% ≤ taux_k ≤ 60% → seuil stable                          │
│                                                                   │
│  Phase 9 — Repos final (3 min, yeux fermés)                      │
│                                                                   │
│  Phase 10 — Questionnaire post-séance                            │
│    Ressenti / Fatigue / Facilité concentration                   │
│                                                                   │
│  → Enregistrement Supabase (taux_succes_global, blocs[], palier) │
└───────────────────────────────────────────────────────────────────┘
```

### 3.3 Formule du seuil journalier

```
Seuil = (0.70 × P_alpha_historique + 0.30 × P_alpha_aujourd'hui) × facteur_palier

Où :
  P_alpha_historique = moyenne pondérée des P_alpha des séances passées
  P_alpha_aujourd'hui = rel_alpha mesuré pendant la baseline de cette séance
  facteur_palier = valeur dans la plage [factor_min, factor_max] du palier actuel
```

Le ratio 70/30 favorise la stabilité historique tout en s'adaptant à l'état du jour (fatigue, variation circadienne).

### 3.4 Structure des 4 paliers

```
P1 — Découverte    S1–S3    facteur 0.85–0.90
     Objectif : familiarisation, confort, confiance
     Seuil facile à atteindre, nombreux succès, apprentissage positif

P2 — Apprentissage S4–S7    facteur 0.95–1.10
     Objectif : régulation consciente, prise de contrôle
     Seuil autour du niveau basal, effort modéré

P3 — Consolidation S8–S12   facteur 1.10–1.25
     Objectif : automatisation, fluidité
     Seuil supérieur à la baseline, effort soutenu

P4 — Maîtrise      S13–S15  facteur 1.25–1.40
     Objectif : généralisation, haute performance
     Seuil nettement supérieur, maîtrise avancée

Changement de palier : automatique si taux_succes_global > 60% sur les N séances du palier
```

### 3.5 Bilans obligatoires (S5, S10, S15)

`bilan_generator.py` produit pour chaque bilan :
- Courbe de progression des taux de succès par séance
- Comparaison alpha pré/post (début vs fin du palier)
- Analyse de la variabilité inter-séance
- Recommandations cliniques automatisées (continuer / ajuster / pause)
- Export PDF (optionnel)

### 3.6 Stockage Supabase

```sql
-- Table progression
user_id, session_n, palier, started_at, ended_at,
taux_succes_global, blocs (JSONB), p_alpha_today,
questionnaire_pre (JSONB), questionnaire_post (JSONB)

-- Récupération progression
GET /api/protocol/user/{user_id}
→ { user_id, sessions_done, next_session, palier,
    palier_info: { factor_min, factor_max, delta },
    p_alpha_hist: float,
    history: [{ session_n, palier, ended_at,
                taux_succes_global, blocs[] }] }
```

---

## Partie IV — Interface unifiée NeuroFeedbackHub

### 4.1 Philosophie de design

Le hub fusionne les deux modes (Protocole + Feedback libre) pour refléter leur complémentarité clinique :
- Le **protocole** structure le renforcement alpha sur 15 séances
- Le **feedback libre** offre une exploration personnalisée entre les séances ou après le protocole
- La **calibration** (baseline de S1) est le prérequis commun aux deux modes

### 4.2 Architecture du hub

```
NeuroFeedbackHub
│
├── Header sticky (toujours visible)
│   ├── ← Accueil
│   ├── 🧠 NeuroFeedback (titre)
│   ├── [🎯 Protocole 15 séances] ← tab
│   ├── [🧘 Feedback libre 🔒/🔓] ← tab (conditionnel)
│   ├── badge CALIBRATION OK / CALIBRATION REQUISE
│   └── MiniSignalWidget (oscilloscope EEG 2s en direct)
│
├── Onglet Protocole
│   └── ProtocolDashboard
│       ├── 4 stat cards (séances, palier, score, bilan)
│       ├── 15 cercles de séances (lock/available/completed)
│       ├── Graphe SVG progression taux de succès
│       ├── Bouton Démarrer S{n}
│       └── Explication protocole (section details)
│
└── Onglet Feedback libre
    ├── [Verrouillé] LockedFeedback
    │   ├── Instructions en 4 étapes
    │   └── → Aller au Protocole
    │
    └── [Déverrouillé] FeedbackSetup
        ├── Détection état EEG (neutral par défaut)
        ├── Choix objectif
        ├── Choix type(s) média
        └── → FeedbackSession (via AppRouter)
```

### 4.3 Conditions de déverrouillage

```javascript
// Vérification à l'ouverture du hub
const response = await fetch(`/api/protocol/user/${userId}`)
const data = await response.json()

calibrationDone = data.sessions_done > 0 || data.p_alpha_hist != null
// sessions_done > 0 : au moins une séance complète (inclut calibration)
// p_alpha_hist != null : données historiques alpha disponibles
```

En mode démo (API indisponible) : données S1–S3 simulées → `sessions_done = 3`, `p_alpha_hist = 14.2` → Feedback libre déverrouillé.

### 4.4 Widget EEG temps réel (MiniSignalWidget)

Le widget est toujours visible dans le header, quel que soit l'onglet actif.

```
Connexion directe : new WebSocket('ws://localhost:8765/ws')
Buffer : Float32Array(500) — 2 secondes @ 250 Hz
Rendu : requestAnimationFrame (bypass React, < 50 ms latence)
Gradient : vert (#7BC4A0) → mauve (#B87B9E) → bleu (#7BA8C4)
Hauteur : 56px — dimensions fixes pour le header
```

Si le casque n'est pas connecté : affiche "En attente du signal…" et indique "DÉCONNECTÉ" — le reste du hub reste pleinement fonctionnel.

---

## Partie V — Flux de données complet end-to-end

### 5.1 Mode Protocole avec signal live

```
┌─────────────────────────────────────────────────────────────────┐
│  Séance Protocole avec NeuroCap connecté                        │
│                                                                 │
│  ESP32 TCP                                                      │
│    │ 250 Hz CSV                                                 │
│    ▼                                                            │
│  backend-signal (processing_loop)                               │
│    │ DSP → CQE → Époque → 27 feat → 63 feat → LightGBM         │
│    │                                                            │
│    ├── WS { type:'eeg', bands, state, cqe_score }              │
│    │        → frontend MiniSignalWidget (header)                │
│    │        → frontend ProtocolSession (barre alpha)            │
│    │                                                            │
│    └── WS { type:'epoch', features, ml_prediction }            │
│             → frontend ProtocolSession (taux_succes_k)          │
│                                                                 │
│  ProtocolSession (frontend)                                     │
│    → POST /api/protocol/bloc/end (à la fin de chaque bloc)     │
│    → ThresholdAdapter → nouveau seuil                           │
│    → POST /api/protocol/session/end (fin séance)               │
│    → progression_tracker → Supabase                             │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Mode Feedback libre avec fichier CSV

```
┌─────────────────────────────────────────────────────────────────┐
│  Session Feedback libre depuis fichier EEG                      │
│                                                                 │
│  FileDashboard                                                  │
│    → POST /api/feedback/analyze_file (CSV upload)               │
│    → backend: file_processor.py → features → état              │
│    → { eegState, features, confidence }                         │
│                                                                 │
│  FeedbackSetup                                                  │
│    → POST /api/feedback/session/start                           │
│    → { sessionId }                                              │
│                                                                 │
│  FeedbackSession (boucle)                                       │
│    → POST /api/feedback/recommend → média                       │
│    → Affichage stimulus (audio/image/video/game)                │
│    → Collecte retour (like, ressenti, notes)                    │
│    → POST /api/feedback/submit                                  │
│    → ThompsonSampling.update()                                  │
│    → Loop jusqu'à endSession()                                  │
│                                                                 │
│  FeedbackReport                                                 │
│    → rapport_ia (Claude Haiku)                                  │
│    → Δα, Δβ, efficacy%                                          │
│    → historique items                                           │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 Navigation AppRouter

```
welcome
  │
  ├── onHardware → hardware-wifi → hardware-live (App.jsx)
  │
  ├── onFile → file (FileDashboard)
  │              └── onFeedback → feedback-setup → feedback-session → feedback-report → file
  │
  └── onNeuroFeedback → neurofeedback (NeuroFeedbackHub)
                          ├── onStartProtocolSession → feedback-session → feedback-report → neurofeedback
                          └── onStartFeedback        → feedback-session → feedback-report → neurofeedback

returnMode (state interne AppRouter) :
  → 'neurofeedback' si venu du hub
  → 'file' si venu du mode fichier
  → utilisé par FeedbackReport.onClose() et FeedbackReport.onNewSession()
```

---

## Partie VI — Guide de démarrage rapide

### 6.1 Démarrage backend + frontend

```bash
# Terminal 1 — Backend
cd backend-signal
python assembly.py
# → http://localhost:8765

# Terminal 2 — Frontend
cd frontend-signal
npm run dev
# → http://localhost:5173
```

### 6.2 Premier protocole (NeuroCap connecté)

1. Ouvrir `http://localhost:5173`
2. Cliquer **NeuroFeedback** (carte violette)
3. Cliquer **▶ Démarrer la séance S1**
4. Remplir le questionnaire pré-séance
5. Effectuer la **baseline** (2 min, yeux fermés, immobile)
6. Effectuer la mesure **IAPF** (1 min, yeux ouverts, point de fixation)
7. Réaliser les **5 blocs** de neurofeedback alpha (3 min chacun)
   - Observer la barre alpha vs le seuil en temps réel
   - S'entraîner à augmenter consciemment l'alpha (relaxation focalisée)
8. Repos final (3 min) + questionnaire post-séance
9. Revenir au dashboard → séance S1 marquée ✓
10. L'onglet **Feedback libre** est maintenant déverrouillé

### 6.3 Première session feedback libre

1. Depuis le hub, cliquer l'onglet **Feedback libre**
2. Choisir un objectif (stress / focus / relaxation)
3. Choisir les types de médias souhaités
4. Cliquer **Démarrer la session**
5. Interagir avec chaque stimulus présenté
6. Soumettre son retour après chaque média
7. La session s'adapte automatiquement aux préférences et à l'état EEG

### 6.4 Mode sans matériel (démo)

Le hub est utilisable sans ESP32 :
- Les données de protocole sont simulées (S1–S3 complétées)
- Le widget EEG affiche "En attente du signal…"
- La navigation et les interfaces sont pleinement fonctionnelles
- L'API `/api/protocol/user/demo` retourne des données de démo si le backend est absent

---

## Références scientifiques

| Référence | Application dans NeuroCap |
|---|---|
| **Mou et al. (2024)**, npj Science of Learning | Architecture protocole 15 séances, formule seuil adaptatif 70/30, paliers P1-P4 |
| **Klimesch (1999)**, Brain Res. Rev. | Bandes theta 6-8 Hz (exclusion contamination EOG 4-6 Hz) |
| **Pope et al. (1995)**, Psychophysiology | Z-scores individualisés vs normativité populationnelle |
| **Cohen (2014)**, MIT Press | PAC theta→gamma, mesures de complexité |
| **Thatcher (2003)**, Clin. EEG Neurosci. | Normalisation dB QEEG, baseline individuelle |
| **QuadTPat (Sci. Rep. 2024)** | Features de transition Cat.7 (63 features FeatEng) |
| **DWT Multiresolution (2018)** | Choix db4 niveau 4 pour Cat.4 (63 features FeatEng) |
| **Thompson Sampling (Thompson 1933)** | Bandit Bayésien pour sélection adaptative de médias |
