# pipeline_fp2.py — Documentation Détaillée

## Vue d'ensemble

`pipeline_fp2.py` est le cœur du prétraitement EEG offline du projet NeuroCap. Il implémente l'intégralité de la chaîne de traitement du signal depuis le fichier brut jusqu'à l'époque normalisée prête pour les modèles ML/DL. Il est compatible avec le hardware AD8232 + ESP32 (canal Fp2, 250 Hz).

**Fichier :** `src/data/pipeline_fp2.py`  
**Lignes :** ~1283  
**Rôle :** Prétraitement EEG offline — filtrage, segmentation, rejet d'artefacts, normalisation, extraction de features

---

## Constantes globales

| Constante | Valeur | Description |
|-----------|--------|-------------|
| `FS` | 250 | Fréquence d'échantillonnage (Hz) — identique hardware |
| `EPOCH_S` | 4.0 | Durée d'une époque (secondes) |
| `OVERLAP` | 0.75 | Taux de recouvrement (75%) — step = 250 éch. = 1 s |
| `AMP_THR` | 500.0 | Seuil de rejet d'époque (µV) — adapté bruit AD8232 |
| `HP_FREQ` | 0.5 | Fréquence de coupure passe-haut (Hz) |
| `LP_FREQ` | 40.0 | Fréquence de coupure passe-bas (Hz) |
| `NOTCH_F` | 50.0 | Fréquence filtre notch (réseau marocain) |
| `WAVELET` | 'db4' | Ondelette DWT (Daubechies 4, Gaikwad 2017) |
| `DWT_LEV` | 4 | Niveau de décomposition DWT |
| `EPOCH_SAMPLES` | 1000 | Samples par époque (= FS × EPOCH_S) |
| `STEP` | 250 | Pas de glissement entre époques |

### Bandes EEG définies (`BAND_DEF`)
- `δ (0.5-4 Hz)` — Ondes delta
- `θ (4-8 Hz)` — Ondes thêta
- `α (8-13 Hz)` — Ondes alpha
- `β (13-30 Hz)` — Ondes beta
- `γ (30-40 Hz)` — Ondes gamma

---

## Fonctions utilitaires

### `_psd(x, fs=FS, nperseg=256)`
Calcule la densité spectrale de puissance (méthode de Welch) avec fenêtre de Hann.

**Paramètres :**
- `x` — Signal 1D (numpy array)
- `fs` — Fréquence d'échantillonnage (défaut 250 Hz)
- `nperseg` — Longueur de chaque segment Welch (défaut 256)

**Retourne :** `(freqs, psd)` — fréquences et densités spectrales de puissance

**Pourquoi Welch ?** Pour une époque de 1000 points, nperseg=256 offre un bon compromis résolution/variance.

---

### `_band_power(freqs, psd, flo, fhi)`
Intègre la PSD sur une bande fréquentielle par la règle des trapèzes.

**Paramètres :**
- `freqs` — Vecteur de fréquences (Hz)
- `psd` — Densité spectrale de puissance
- `flo`, `fhi` — Bornes inférieure et supérieure de la bande (Hz)

**Retourne :** `float` — Puissance dans la bande [flo, fhi]

---

## Pipeline de prétraitement

### Étape 1 — Filtre passe-haut (`apply_hp_filter`)
**Justification :** Élimine la dérive DC et les artefacts basse fréquence (respiration < 0.5 Hz).  
**Implémentation :** Filtre Butterworth d'ordre 4, zéro-phase (`filtfilt`), coupure à 0.5 Hz.  
**Référence :** Chaudhary 2025, Acharya 2021.

### Étape 2 — Filtre passe-bas (`apply_lp_filter`)
**Justification :** Supprime les artefacts musculaires (EMG > 40 Hz) tout en conservant le gamma (30-40 Hz).  
**Implémentation :** Butterworth ordre 4, zéro-phase, coupure à 40 Hz.  
**Référence :** Acharya 2021, Gaikwad 2017.

### Étape 3 — Filtre notch (`apply_notch_filter`)
**Justification :** Élimine l'interférence secteur marocain à 50 Hz.  
**Implémentation :** Filtre notch IIR, Q=30 (`iirnotch`), appliqué en zéro-phase.  
**Référence :** Gaikwad 2017, CdC NeuroCap.

### Étape 4 — Débruitage DWT (`apply_dwt_denoising`)
**Justification :** Supprime les artefacts haute fréquence résiduels sans ICA (impossible sur 1 canal).  
**Implémentation :** Décomposition en ondelettes discrètes `db4` niveau 4, seuillage doux (soft thresholding) sur les coefficients de détail.  
**Référence :** Gaikwad 2017.

### Étape 5 — Segmentation en époques (`segment_signal`)
**Paramètres :**
- Signal filtré (1D numpy array)
- `epoch_samples` — Taille d'une époque (1000 points)
- `step` — Pas de glissement (250 points = 75% overlap)

**Logique :** Fenêtre glissante avec `np.roll`-style indexing. Produit un tableau 2D (N_epochs × 1000).

**Pourquoi 75% overlap ?** Crée un flux quasi-continu (1 mise à jour par seconde) pour le temps réel.

### Étape 6 — Rejet d'artefacts (`reject_epochs`)
**Critère :** Amplitude crête-à-crête (PTP = max - min) > 500 µV.  
**Justification :** Adapté au bruit de fond de l'AD8232 (10-20 µV RMS). Les datasets propres utilisent 150 µV mais l'AD8232 génère plus de bruit.  
**Retourne :** Masque booléen des époques valides.

### Étape 7 — Normalisation Z-score (`normalize_epochs`)
Normalisation par époque : `(x - mean) / std` appliquée indépendamment à chaque fenêtre de 1000 points.  
**Justification :** Compense la variabilité inter-sujets et inter-sessions (Chaudhary 2025, Lawhern 2018).

---

## Fonctions principales de chargement de données

### `load_concentration_with_scores()`
Charge le dataset de Concentration Cognitive (OpenBCI, 15 sujets, 8 canaux, 200 Hz).

**Pipeline interne :**
1. Parcourt `data/Cognitive_Load_EEG_dataset/` pour chaque fichier `.txt`
2. Lit les 25 colonnes, extrait le canal Fp2 (index 1 de l'array EEG)
3. Convertit ADC → µV via `OPENBCI_SCALE ≈ 0.02235`
4. Rééchantillonne 200 Hz → 250 Hz par filtre polyphase (scipy)
5. Applique le pipeline de prétraitement complet (HP → LP → Notch → DWT)
6. Segmente en époques de 4s avec 75% overlap
7. Rejette les époques > 500 µV
8. Normalise par z-score
9. Charge les scores depuis `data/Scoring/scored_concentration.csv`
10. Aligne les scores aux époques par fichier/sujet

**Retourne :** `(X, y_scores, subject_ids)` — signaux prétraités, scores 0-10, IDs sujets

**Format fichiers .txt :** 25 colonnes, Fp2 au canal EEG index 1, format OpenBCI.

### `load_stress_with_scores()`
Charge le dataset SAM40 Stress (EMOTIV, 40 sujets, 32 canaux, 128 Hz, fichiers .mat).

**Pipeline interne :**
1. Parcourt `data/SAM40_Stress_dataset/` pour chaque `.mat`
2. Extrait le canal Fp2 — 3 stratégies en cascade :
   - Cherche 'Fp2' dans `ch_names` du fichier
   - Utilise l'index 31 (Fp2 dans layout EMOTIV 32-canaux)
   - Fallback canal 0 si tout échoue
3. Rééchantillonne 128 Hz → 250 Hz par filtre polyphase
4. Applique le pipeline de prétraitement complet
5. Segmente, rejette, normalise
6. Charge les scores depuis `data/Scoring/scored_stress.csv`

**Retourne :** `(X, y_scores, subject_ids)`

### `split_by_subject(X, y, subject_ids, val_ratio=0.15, test_ratio=0.15, seed=42)`
Divise les données en train/val/test **par sujet** (pas par époque) pour éviter le data leakage inter-sujet.

**Logique :**
1. Obtient la liste des sujets uniques
2. Mélange les sujets aléatoirement (seed fixe pour reproductibilité)
3. Assigne les derniers `test_ratio × N` sujets au test
4. Assigne les `val_ratio × N` suivants à la validation
5. Le reste va à l'entraînement

**Retourne :** `(X_train, y_train, X_val, y_val, X_test, y_test, s_train, s_val, s_test)`

**Importance :** Garantit que les signaux d'un même sujet ne se retrouvent pas dans plusieurs splits, ce qui évite le "sujet leakage" — un biais majeur dans les évaluations EEG.

---

## Fonctions de visualisation

### `plot_preprocessing_pipeline(raw, hp, lp, notch, dwt, fs=FS, out_path=None)`
Génère une figure 6-panneaux montrant le signal à chaque étape du pipeline :
- Signal brut → après HP → après LP → après Notch → après DWT → PSD finale

**Utilité :** Validation visuelle que chaque filtre a l'effet attendu.

### `plot_band_analysis(epochs, labels, fs=FS, out_path=None)`
Visualise la puissance par bande EEG (δ/θ/α/β/γ) pour chaque classe (concentration/stress).

**Utilité :** Vérifier que les bandes alpha/beta/theta sont discriminantes entre classes.

### `plot_epoch_examples(epochs, labels, n_examples=3, out_path=None)`
Affiche N exemples d'époques par classe pour validation visuelle de la qualité du signal.

### `plot_subject_variability(X, subject_ids, fs=FS, out_path=None)`
Visualise la variabilité inter-sujets via la PSD moyenne par sujet.

### `plot_augmentation_preview(X_orig, X_aug, aug_name, out_path=None)`
Compare visuellement les époques originales et augmentées pour valider les stratégies d'augmentation.

---

## Flux d'exécution (`main()`)

```
load_concentration_with_scores()  ─┐
load_stress_with_scores()          ├─→ split_by_subject() → save .npy files
                                   │
                                   └─→ Visualisations → reports/preprocessing/
```

**Sorties :**
- `data/preprocessed/concentration/` : X_train.npy, y_train.npy, X_val.npy, y_val.npy, X_test.npy, y_test.npy, subject_ids_*.npy
- `data/preprocessed/stress/` : mêmes fichiers
- `reports/preprocessing/` : figures PNG

---

## Dépendances

| Bibliothèque | Usage |
|-------------|-------|
| `numpy` | Tableaux, calculs numériques |
| `scipy.signal` | Filtres Butterworth, Welch PSD, notch |
| `pywt` | DWT débruitage (PyWavelets) |
| `matplotlib` | Visualisations |
| `scipy.io` | Chargement fichiers .mat (SAM40) |

---

## Justification scientifique de chaque étape

| Étape | Référence | Raison |
|-------|-----------|--------|
| HP 0.5 Hz | Chaudhary 2025, Acharya 2021 | Dérive DC, respiration |
| LP 40 Hz | Acharya 2021, Gaikwad 2017 | EMG > 40 Hz |
| Notch 50 Hz Q=30 | Gaikwad 2017, CdC | Réseau marocain |
| DWT db4 niveau 4 | Gaikwad 2017 | Remplacement ICA 1-canal |
| Overlap 75% | Bio-Protocol 2023 | Flux temps réel 1 Hz |
| Rejet 500 µV | NeuroCap CdC §3.1 | Bruit AD8232 |
| Z-score par époque | Chaudhary 2025, Lawhern 2018 | Variabilité inter-sujets |
| Split par sujet | Standard EEG-BCI | Anti data leakage |
