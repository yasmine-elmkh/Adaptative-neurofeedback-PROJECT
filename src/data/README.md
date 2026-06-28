# NeuroCap — Traitement des Données (`src/data/`)

Scripts du pipeline complet de traitement des données EEG.  
**Tâche unique : régression continue → prédire un score 0–10 (concentration ou stress).**

---

## Structure du dossier

```
src/data/
├── pipeline_fp2.py           Prétraitement EEG 9 étapes (HP/LP/Notch/DWT/epoch/zscore)
│                             + chargement datasets CLA (200 Hz) et SAM40 (128 Hz) → 250 Hz
├── augmentation_eeg.py       Augmentation EEG (4 techniques → 5 expériences A/B/C/D/FULL)
│                             Gère float y (scores 0-10) via np.tile
├── features_extraction.py    Extraction 15 features légères (< 10 ms/epoch, embarquable ESP32)
├── feature_eng.py            Extraction 78 features avancées (8 catégories, ~35 ms/epoch)
├── pipeline_regression.py    Coordinateur : scoring → preprocessing → split → aug → features
├── visualize_regression.py   16 figures dans reports/Regression/ (4 sous-dossiers)
├── scoring/                  Attribution des scores 0–10 aux epochs
│   ├── concentration_scoring.py   conc_score depuis les niveaux CLA
│   ├── stress_scoring.py          stress_score depuis scales.xls SAM40
│   ├── merge_scoring.py           Fusion signaux + scores → .npy
│   ├── visualize_scoring.py       7 figures dans reports/scoring/merge/
│   └── README.md
└── validate_data/            Validation qualité des données brutes
    ├── validate_concentration.py
    ├── validate_stress.py
    └── README.md
```

---

## Pipeline de régression

```
RAW .txt (OpenBCI 200 Hz)           RAW .mat (Emotiv 128 Hz)
        ↓                                    ↓
scoring/concentration_scoring.py    scoring/stress_scoring.py
→ conc_score 0-10 par epoch         → stress_score 0-10 depuis scales.xls
        ↓                                    ↓
        └──────────── pipeline_regression.py ─────────────┘
                                │
            pipeline_fp2.load_*_with_scores()
                HP(0.5Hz) + LP(40Hz) + Notch(50Hz) + DWT db4
                rééchantillonnage → 250 Hz + segmentation 4s + zscore
                                │
            augmentation_eeg.split_by_subject()
                70/15/15 PAR SUJET (anti data leakage)
                                │
            augmentation_eeg.augment_train_set()
                5 variantes : A / B / C / D / FULL
                                │
         ┌──────────────────────┴──────────────────────┐
         │                                              │
features_extraction.py                          feature_eng.py
15 features (< 10 ms)                           78 features (~35 ms)
         │                                              │
         └──────────── data/Regression/ ───────────────┘
```

**Sorties dans `data/Regression/` :**
```
augmented/conc/    X_train_{A,B,C,D,FULL}.npy  y_train_{A,B,C,D,FULL}.npy
                   X_val.npy  X_test.npy  y_val.npy  y_test.npy
augmented/stress/  (idem)
features/conc/     feat15_train_{A,B,C,D,FULL}.npy  feat78_train_{A,B,C,D,FULL}.npy
                   feat15_val.npy  feat78_val.npy  feat15_test.npy  feat78_test.npy
features/stress/   (idem)
```

---

## Fichiers en détail

### `pipeline_fp2.py`

Pipeline de prétraitement identique au firmware ESP32 (AD8232 + Fp2, 250 Hz).

| Étape | Fonction | Paramètres | Justification |
|-------|----------|------------|--------------|
| Filtre passe-haut | `step2_highpass()` | fc=0.5 Hz, order=4, filtfilt | Élimine dérive DC (Chaudhary 2025) |
| Filtre passe-bas | `step3_lowpass()` | fc=40.0 Hz, order=4, filtfilt | Supprime EMG > 40 Hz (Acharya 2021) |
| Filtre notch | `step4_notch()` | f0=50 Hz, Q=30 | Réseau électrique marocain |
| Débruitage DWT | `step5_dwt()` | wavelet=db4, level=4, soft thresh | Remplace ICA sur 1 canal (Gaikwad 2017) |
| Segmentation | `step7_segment()` | 4s, overlap=75%, Hann, seuil 500 µV | 1 epoch/s en temps réel |
| Z-score | `step8_zscore()` | par epoch | Normalise variabilité inter-sujets |

**Fonctions de chargement datasets :**
- `resample_to_250hz(sig, fs_orig)` : CLA 200 Hz → 250 Hz, SAM40 128 Hz → 250 Hz
- `load_concentration_with_scores(scored_csv, raw_dir)` → X (N,1000), y_score (N,), subjects (N,), levels (N,)
- `load_stress_with_scores(scored_csv, raw_dir)` → même interface

### `augmentation_eeg.py`

4 techniques d'augmentation, combinées en 5 expériences.  
**Règle absolue : split par sujet AVANT d'augmenter.** (anti data leakage)

| Expérience | Technique(s) | Facteur | Propriété préservée |
|------------|-------------|---------|-------------------|
| A | Aucune (baseline pur) | ×1 | — |
| B | Gaussian noise (SNR 20-30 dB) + Scaling (±10%) + Time shift (80 ms) | ×2 | TBR/EI invariants au scaling |
| C | B + DWT fréquentielle db4 (perturbe cD1-cD3, préserve cD4-cD6) | ×3 | α/β/θ conservés |
| D | Magnitude Warping (±8% RMS, spline 5 nœuds) | ×2 | Simulation fatigue cognitive |
| FULL | A + B + C + D | ×4 | Maximum de données |

**Fonctions clés :**
- `split_by_subject(X, y, subject_ids, test_ratio=0.15, val_ratio=0.15)` : split 70/15/15 par sujet
- `loso_generator(X, y, subject_ids)` : générateur LOSO (gold standard EEG, Katmah 2021)
- `augment_train_set(X_train, y_train)` → dict `{A, B, C, D, FULL}`
- `validate_augmentation(X_orig, X_aug)` : vérifie TBR/ABR/EI/TAR varient < ±15%

### `features_extraction.py` — 15 features

Features légères conçues pour l'embarqué (< 10 ms/epoch, compatible ESP32).

```
[0-4]  Puissances PSD Welch (nperseg=256)  : Pδ, Pθ, Pα, Pβ, Pγ
[5-8]  Ratios cognitifs NeuroCap            : TBR=Pθ/Pβ, ABR=Pα/Pβ, EI=Pβ/(Pα+Pθ), TAR=Pθ/Pα
[9-11] Paramètres de Hjorth                 : Activity=var(x), Mobility, Complexity
[12-14] Features embarquées (Samsa 2026)   : Power=mean(x²), MeanAmp=mean(|x|), RelEnergy=Pβ/Σbandes

Résultats (feat15_smote, LightGBM, LOSO) :
  Concentration : AUC=0.631, R²=0.148, MAE=1.89
  Stress        : AUC=0.624, R²=0.127, MAE=1.95
```

### `feature_eng.py` — 78 features (8 catégories)

Features avancées pour les modèles ML serveur/cloud.

```
Cat. 1 — PSD Welch (5)           : Pδ, Pθ, Pα, Pβ, Pγ
Cat. 2 — Ratios cognitifs (5)    : TBR, ABR, EI, TAR, RelEnergy_β
Cat. 3 — Hjorth + temporel (6)   : Activity, Mobility, Complexity, Power, MeanAmp, ZCR
Cat. 4 — DWT sous-bandes (20)    : db4 niv.4 → 5 bandes × 4 stats (mean,std,energy,entropy)
Cat. 5 — Texturales enrichies (20): stats globales + skewness/kurtosis par sous-bande DWT
Cat. 6 — Non-linéaires (7)       : ApEn, SampEn, PermEn, SpectralEn, HFD, RenyiEn(α=2), LogEnergyEn
Cat. 7 — Transition Patterns (6) : pct_up, pct_down, pct_flat, up_streak, down_streak, trans_freq
Cat. 8 — NeuroFeat kernels (9)   : 3 noyaux φ(mean/median/std) × 3 stats (mean,std,entropy)

Résultats (feat78_smote, LightGBM/RF, LOSO) :
  Concentration : AUC=0.676, R²=0.204, MAE=1.63  (+4.5 pts AUC vs feat15)
  Stress        : AUC=0.668, R²=0.184, MAE=1.72  (+4.4 pts AUC vs feat15)
```

### `pipeline_regression.py`

Coordinateur des 4 étapes du pipeline. N'importe quel étape peut être relancée seule.

```bash
python src/data/pipeline_regression.py
```

### `visualize_regression.py`

Génère 16 figures de validation dans `reports/Regression/` :
- `01_preprocessing/` : signal brut vs filtré, spectre avant/après DWT
- `02_split/` : distribution sujets train/val/test, vérification anti-leakage
- `03_augmentation/` : comparaison PSD avant/après augmentation par expérience
- `04_features/` : corrélations feat/score, distributions, feat15 vs feat78

---

## Comparaison feat15 vs feat78

| Critère | feat15 | feat78 |
|---------|--------|--------|
| Nb features | 15 | 78 |
| Temps/epoch | < 10 ms | ~35 ms |
| Embarquable | Oui (ESP32) | Oui (Raspberry Pi / serveur) |
| AUC concentration (LightGBM LOSO) | 0.631 | **0.676** (+4.5 pts) |
| AUC stress (RF LOSO) | 0.624 | **0.668** (+4.4 pts) |
| R² concentration | 0.148 | **0.204** (+5.6 pts) |
| R² stress | 0.127 | **0.184** (+5.7 pts) |
| Usage | Hardware temps réel | Serveur / mode avancé |

---

## Ordre d'exécution recommandé

```bash
# 1. Valider les données brutes
python src/data/validate_data/validate_concentration.py
python src/data/validate_data/validate_stress.py

# 2. Attribuer les scores
python src/data/scoring/concentration_scoring.py
python src/data/scoring/stress_scoring.py

# 3. Pipeline complet
python src/data/pipeline_regression.py

# 4. Visualiser (optionnel)
python src/data/visualize_regression.py
python src/data/scoring/visualize_scoring.py

# 5. Entraîner les modèles ML (depuis src/models/baselines/)
# 6. Entraîner les modèles DL (depuis src/models/deep_learning/architectures/)
# 7. Transfer Learning (depuis src/models/transfer_learning/)
```
