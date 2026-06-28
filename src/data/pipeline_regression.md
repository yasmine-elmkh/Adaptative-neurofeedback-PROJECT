# pipeline_regression.py — Documentation Détaillée

## Vue d'ensemble

`pipeline_regression.py` coordonne le pipeline complet de préparation des données pour la **régression de scores EEG (0-10)**. Il réutilise les fonctions existantes (`pipeline_fp2.py`, `augmentation_eeg.py`, `features_extraction.py`, `feature_eng.py`) sans les modifier.

**Fichier :** `src/data/pipeline_regression.py`  
**Lignes :** ~370  
**Sortie :** `data/Regression/` + `Features/`

---

## Schéma général

```
Données brutes
  ├── Concentration (OpenBCI 200Hz .txt) ──→ load_concentration_with_scores()
  └── Stress (EMOTIV 128Hz .mat)         ──→ load_stress_with_scores()
          ↓
    Préprocessing (pipeline_fp2)
    [HP 0.5Hz → LP 40Hz → Notch 50Hz → DWT db4 → AmpReject → Epoch 4s → Zscore]
          ↓
    Split par sujet 70/15/15 (split_by_subject)
          ↓
    Augmentation sur train seulement (augment_train_set)
    [A: ×1, B: +bruit ×2, C: +DWT ×3, D: +warp ×2, FULL: ×4]
          ↓
    Extraction features
    ├── feat15 (features_extraction.py) → Features/{conc,stress}/feat15_*.npy
    └── feat78 (feature_eng.py)         → Features/{conc,stress}/feat78_*.npy
```

---

## Chemins de sortie

```
data/Regression/
├── preprocessed/
│   ├── X_conc.npy           — Epochs concentration (N, 1000) float32 zscore
│   ├── y_conc.npy           — Scores concentration (N,) float32 [0-10]
│   ├── subjects_conc.npy    — ID sujet (N,) int32
│   ├── levels_conc.npy      — Niveau cognitif (N,) int32 [0-3]
│   ├── X_stress.npy         — Epochs stress (N, 1000) float32 zscore
│   ├── y_stress.npy         — Scores stress (N,) float32 [0-10]
│   └── subjects_stress.npy  — ID sujet (N,) int32
│
└── augmented/
    ├── conc/
    │   ├── X_train_{A,B,C,D,FULL}.npy   — Signaux augmentés (brut, pour DL/TL)
    │   ├── y_train_{A,B,C,D,FULL}.npy   — Scores propagés (np.tile)
    │   ├── X_val.npy + y_val.npy
    │   ├── X_test.npy + y_test.npy
    │   └── subject_ids_train.npy
    └── stress/  (même structure)

Features/
├── conc/
│   ├── feat15_train_{A,B,C,D,FULL}.npy  — 15 features légères
│   ├── feat78_train_{A,B,C,D,FULL}.npy  — 78 features avancées
│   ├── feat15_val.npy + feat15_test.npy
│   ├── feat78_val.npy + feat78_test.npy
│   ├── y_train_{A,B,C,D,FULL}.npy
│   ├── y_val.npy + y_test.npy
│   └── subject_ids_train_{A,B,C,D,FULL}.npy
└── stress/  (même structure)
```

---

## Fonctions

### `step1_load_and_preprocess()`

Charge et préprocess les deux datasets.

**Actions :**
- Appelle `pipeline_fp2.load_concentration_with_scores(SCORE_CONC, RAW_CONC)`
  → X (N, 1000), y_score (N,), subjects (N,), levels (N,)
- Appelle `pipeline_fp2.load_stress_with_scores(SCORE_STR, RAW_STRESS)`
  → X (N, 1000), y_score (N,), subjects (N,)
- Sauvegarde dans `data/Regression/preprocessed/`

**Retourne :** `(X_conc, y_conc, subs_conc)`, `(X_str, y_str, subs_str)`

**Pourquoi réutiliser pipeline_fp2 :**
Les filtres HP/LP/Notch/DWT sont valides scientifiquement et identiques au hardware AD8232. Seule l'attribution des labels change (float score vs int binaire pour la classification).

---

### `step2_split(X, y, subjects, name)`

Split train/val/test par sujet (70/15/15).

**Paramètres :**
- `X` — Array (N, 1000)
- `y` — Scores float (N,)
- `subjects` — IDs sujet (N,)
- `name` — Nom du dataset pour les logs

**Méthode :** Réutilise `split_by_subject()` de `pipeline_fp2.py` avec `test_ratio=0.15`, `val_ratio=0.15`, `seed=42`.

**Vérification anti-leakage :**
```python
assert len(set(sids_tr) & set(sids_te)) == 0, "ERREUR : sujet partagé train/test !"
assert len(set(sids_tr) & set(sids_vl)) == 0, "ERREUR : sujet partagé train/val !"
```

**Pourquoi par sujet :**
Si split par epoch, le même sujet peut être en train ET test → le modèle mémorise sa signature EEG → biais de généralisation.

**Retourne :** `(X_tr, y_tr, sids_tr)`, `(X_vl, y_vl, sids_vl)`, `(X_te, y_te, sids_te)`

---

### `step3_augment(X_train, y_train, out_subdir)`

Applique l'augmentation sur le train uniquement.

**Paramètres :**
- `X_train` — (N_train, 1000)
- `y_train` — Scores float (N_train,)
- `out_subdir` — `OUT_AUG / 'conc'` ou `OUT_AUG / 'stress'`

**Méthode :** Appelle `augmentation_eeg.augment_train_set(X_train, y_train, seed=42)`.

**Propagation des scores :**
`np.tile(y_train, 2)` copie exactement les scores pour chaque epoch augmentée.

**Justification :** Ajouter du bruit gaussien à un epoch de concentration=8.5 ne change pas l'état cognitif du sujet → score conservé.

**Sortie :** `X_train_{A,B,C,D,FULL}.npy` + `y_train_{A,B,C,D,FULL}.npy`

---

### `step4_extract_features(X_aug_dir, feat_out_dir, dataset_name)`

Extrait feat15 et feat78 pour toutes les expériences.

**Paramètres :**
- `X_aug_dir` — `OUT_AUG / 'conc'` ou `OUT_AUG / 'stress'`
- `feat_out_dir` — `OUT_FEAT / 'conc'` ou `OUT_FEAT / 'stress'`
- `dataset_name` — Pour les logs

**Pour chaque expérience A/B/C/D/FULL :**
```python
# feat15 (léger, embarquable ESP32)
feat15 = [get_feature_vector(ep) for ep in X_ep]  # (N, 15)

# feat78 (avancé)
feat78 = [list(extract_all_features(ep).values()) for ep in X_ep]  # (N, 78)
```

**Nettoyage NaN :** `np.nan_to_num(feat, nan=0.0, posinf=0.0, neginf=0.0)` après extraction.

**subject_ids tiling :**
```python
sid_mapping = {'A': 1, 'B': 2, 'C': 3, 'D': 2, 'FULL': 4}
sids_tiled = np.tile(sids_orig, sid_mapping[exp])[:len(feat78)]
```
Utilisé pour LOSO dans les baselines de régression.

---

### `run_regression_pipeline()`

Orchestre les 4 étapes dans l'ordre logique.

```python
# Étape 1 : Load + Preprocess
(X_conc, y_conc, subs_conc), (X_str, y_str, subs_str) = step1_load_and_preprocess()

# Étape 2 : Split par sujet
(Xtr_c, ytr_c, sids_tr_c), (Xvl_c, ...), (Xte_c, ...) = step2_split(X_conc, ...)
(Xtr_s, ytr_s, sids_tr_s), (Xvl_s, ...), (Xte_s, ...) = step2_split(X_str,  ...)

# Sauvegarder val + test (non augmentés)

# Étape 3 : Augmentation train
step3_augment(Xtr_c, ytr_c, OUT_AUG / "conc")
step3_augment(Xtr_s, ytr_s, OUT_AUG / "stress")

# Étape 4 : Features
step4_extract_features(OUT_AUG / "conc",   OUT_FEAT / "conc",   "Concentration")
step4_extract_features(OUT_AUG / "stress",  OUT_FEAT / "stress", "Stress")
```

---

## 2 Modèles de régression distincts

| Modèle | Prédit | Données d'entrée |
|--------|--------|-----------------|
| **CONC** | `conc_score` (0-10) | Epochs Cognitive Load OpenBCI |
| **STRESS** | `stress_score` (0-10) | Epochs SAM40 EMOTIV |

Ces deux modèles sont **complètement indépendants** — datasets différents, sujets différents, splits différents.

---

## Comparaison feat15 vs feat78

| Feature set | Script baseline | Avantage |
|-------------|----------------|----------|
| feat15 | `baseline_ML_regression.py` | Léger, embarquable ESP32 |
| feat78 | `baseline_ML_regression_feature_eng.py` | Pouvoir prédictif supérieur |
| Comparaison | `compare_regression_features.py` | ΔR², ΔMAE, ΔAUC |

---

## Utilisation

```bash
# Étape 1 : Exécuter le pipeline
python src/data/pipeline_regression.py

# Étape 2 : Visualiser les résultats
python src/data/visualize_regression.py

# Étape 3 : Lancer les modèles ML
python src/models/baselines/baseline_ML_regression.py           # feat15
python src/models/baselines/baseline_ML_regression_feature_eng.py  # feat78
```
