# augmentation_eeg.py — Documentation Détaillée

## Vue d'ensemble

`augmentation_eeg.py` implémente les 4 stratégies d'augmentation de données EEG du projet NeuroCap. Il opère **après la séparation train/val/test** et **uniquement sur le set d'entraînement** pour éviter tout data leakage. Il produit 5 expériences : A (original), B (bruit gaussien), C (DWT fréquentielle), D (magnitude warping), FULL (toutes combinées).

**Fichier :** `src/data/augmentation_eeg.py`  
**Lignes :** ~1401  
**Rôle :** Augmentation des données EEG — 4 méthodes × 5 expériences

---

## Règles absolues d'augmentation

Le fichier documente 5 règles inviolables :
1. **Séparation AVANT augmentation** — jamais augmenter avant de splitter
2. **Augmentation UNIQUEMENT sur X_train** — val/test restent bruts
3. **Split par SUJET** — jamais par époque (anti data leakage inter-sujet)
4. **Magnitude Warping INDÉPENDANT** de Exp. B+C (jamais combiné)
5. **Valider que TBR/EI/TAR varient < ±15%** après augmentation

---

## Constantes

| Constante | Valeur | Description |
|-----------|--------|-------------|
| `FS` | 250 | Fréquence d'échantillonnage (Hz) |
| `EPOCH_SAMPLES` | 1000 | Samples par époque |
| `HP_FREQ` | 0.5 | Borne basse filtre bandpass post-augmentation |
| `LP_FREQ` | 40.0 | Borne haute filtre bandpass post-augmentation |
| `SNR_MIN` | 20 | SNR minimum pour le bruit gaussien (dB) |
| `SNR_MAX` | 30 | SNR maximum pour le bruit gaussien (dB) |
| `SCALE_RANGE` | (0.9, 1.1) | Plage de scaling (±10%) |
| `SHIFT_MAX` | 20 | Décalage temporel maximal (échantillons = 80 ms) |
| `MW_FREQ_MIN` | 0.05 | Fréquence minimale du warping (Hz) |
| `MW_FREQ_MAX` | 0.20 | Fréquence maximale du warping (Hz) |
| `MW_AMPLITUDE` | 0.08 | Amplitude du warping (±8% RMS) |
| `DWT_WAVELET` | 'db4' | Ondelette pour l'augmentation DWT |
| `DWT_LEVEL` | 6 | Niveau de décomposition DWT augmentation |

---

## Fonctions d'augmentation

### `augment_gaussian_noise(epoch, rng, snr_db_min=SNR_MIN, snr_db_max=SNR_MAX)`

Ajoute du bruit gaussien blanc filtré (bandpass 0.5-40 Hz) à l'époque.

**Paramètres :**
- `epoch` — Tableau 1D (1000 points)
- `rng` — Générateur aléatoire numpy (pour reproductibilité)
- `snr_db_min`, `snr_db_max` — Plage de SNR (décibels)

**Algorithme :**
1. Choisir un SNR aléatoire entre 20 et 30 dB
2. Calculer la puissance du signal : `P_signal = mean(epoch²)`
3. Calculer la puissance du bruit cible : `P_noise = P_signal / 10^(SNR/10)`
4. Générer un bruit gaussien de puissance cible
5. Filtrer le bruit (bandpass 0.5-40 Hz) pour ne pas introduire d'artefacts hors-bande
6. Ajouter le bruit filtré au signal : `epoch + noise`

**Justification :** Le filtrage du bruit garantit que les ratios TBR/EI/TAR varient < ±15% (règle N°5). Un SNR 20-30 dB simule le bruit de fond réaliste de l'AD8232.

**Référence :** Knowledge-Based Systems (2025), IEEE TNSRE (2022).

---

### `augment_scaling(epoch, rng, scale_range=SCALE_RANGE)`

Multiplie l'amplitude de l'époque par un facteur aléatoire.

**Paramètres :**
- `epoch` — Tableau 1D
- `rng` — Générateur aléatoire
- `scale_range` — Tuple `(0.9, 1.1)` → ±10%

**Algorithme :**
1. Tirer un facteur `α ∈ [0.9, 1.1]` uniformément
2. Retourner `α × epoch`

**Justification :** Le scaling ±10% est suffisamment petit pour ne pas altérer les ratios spectraux (TBR, EI, ABR sont des rapports — invariants au scaling global). Simule la variabilité de l'impédance électrode-peau entre sessions.

---

### `augment_time_shift(epoch, rng, max_shift=SHIFT_MAX)`

Décale temporellement le signal avec wrap-around circulaire.

**Paramètres :**
- `epoch` — Tableau 1D (1000 points)
- `rng` — Générateur aléatoire
- `max_shift` — Décalage maximum en échantillons (défaut 20 = 80 ms)

**Algorithme :**
1. Tirer un décalage `d ∈ [-max_shift, +max_shift]`
2. Appliquer `np.roll(epoch, d)` (rotation circulaire)

**Justification :** 80 ms correspond à la latence typique des oscillations EEG dans la fenêtre de 4s. Le `np.roll` préserve toute l'énergie du signal sans bords artificiels (pas de zero-padding).

---

### `augment_dwt_frequency(epoch, rng, wavelet=DWT_WAVELET, level=DWT_LEVEL)`

Perturbe les sous-bandes hautes fréquences via DWT tout en préservant les bandes cognitives.

**Paramètres :**
- `epoch` — Tableau 1D (1000 points)
- `rng` — Générateur aléatoire
- `wavelet` — Famille d'ondelettes ('db4')
- `level` — Niveau de décomposition (6)

**Algorithme :**
1. Décomposer l'époque en coefficients DWT (db4, 6 niveaux) : `[cA6, cD6, cD5, cD4, cD3, cD2, cD1]`
2. Conserver `cA6` (approximation — basses fréquences : δ/θ)
3. Conserver `cD6, cD5` (détails basses fréquences — α/β)
4. Perturber `cD4, cD3, cD2, cD1` (hautes fréquences — γ et au-delà) : multiplier par facteur ∈ [0.7, 1.3]
5. Reconstruire avec `pywt.waverec()`
6. Tronquer/padder pour obtenir exactement 1000 points

**Justification :** Les bandes cognitives importantes (θ, α, β — 4-30 Hz) sont aux niveaux 3-6 de la DWT à 250 Hz. En ne perturbant que les niveaux 1-4 (HF), on simule la variabilité naturelle du signal sans dégrader les marqueurs cognitifs.

**Niveau DWT à 250 Hz :**
- cD1 : 62.5-125 Hz
- cD2 : 31.25-62.5 Hz
- cD3 : 15.6-31.25 Hz (γ partiel)
- cD4 : 7.8-15.6 Hz (β partiel)
- cD5 : 3.9-7.8 Hz (θ/α)
- cD6 : 1.95-3.9 Hz (δ partiel)
- cA6 : 0-1.95 Hz

---

### `augment_magnitude_warping(epoch, rng, freq_min=MW_FREQ_MIN, freq_max=MW_FREQ_MAX, amplitude=MW_AMPLITUDE)`

Applique une déformation lente et progressive de l'amplitude via un signal sinusoïdal.

**Paramètres :**
- `epoch` — Tableau 1D (1000 points)
- `rng` — Générateur aléatoire
- `freq_min`, `freq_max` — Plage de fréquence du warping (0.05-0.20 Hz)
- `amplitude` — Amplitude de la déformation (±8% RMS)

**Algorithme :**
1. Générer un axe temporel `t = [0, 1/250, 2/250, ..., 999/250]` (4 secondes)
2. Tirer une fréquence `f ∈ [0.05, 0.20]` Hz et une phase `φ ∈ [0, 2π]`
3. Créer le signal de modulation : `w(t) = 1 + amplitude × sin(2π × f × t + φ)`
4. Retourner `epoch × w(t)`

**Justification :** Une déformation à 0.05-0.20 Hz simule la fatigue musculaire ou la variation d'attention sur 4 secondes. C'est plus réaliste qu'un scaling constant (Exp. B) car l'amplitude varie au cours de l'époque. L'amplitude ±8% RMS garantit que TBR/EI/TAR varient < ±15%.

---

## Fonctions d'orchestration

### `augment_experiment_B(X_train, y_train, rng)`

Expérience B — Augmentation basique (×2) : original + bruit+scaling+shift.

**Algorithme pour chaque époque originale :**
1. Appliquer `augment_gaussian_noise()` + `augment_scaling()` + `augment_time_shift()` séquentiellement
2. Concaténer : `[original, augmented_B]`

**Retourne :** `(X_B, y_B)` — 2× le nombre d'époques original, labels identiques

### `augment_experiment_C(X_train, y_train, rng)`

Expérience C — Augmentation B + DWT fréquentielle (×3) : original + B + DWT.

**Algorithme :**
1. Appliquer `augment_experiment_B()` pour avoir original + B
2. Appliquer `augment_dwt_frequency()` sur les originaux
3. Concaténer : `[original, augmented_B, augmented_DWT]`

**Retourne :** `(X_C, y_C)` — 3× les époques originales

### `augment_experiment_D(X_train, y_train, rng)`

Expérience D — Magnitude Warping seul (×2) : original + warped.

**Note :** Indépendant de B+C — jamais combiné avec eux pour isoler l'effet du warping.

**Algorithme :**
1. Appliquer `augment_magnitude_warping()` sur chaque époque
2. Concaténer : `[original, warped]`

**Retourne :** `(X_D, y_D)` — 2× les époques originales

### `augment_experiment_FULL(X_train, y_train, rng)`

Expérience FULL — Toutes les augmentations (×4) : original + B + DWT + D.

**Algorithme :**
1. Appliquer bruit+scaling+shift (Exp. B)
2. Appliquer DWT perturbation (Exp. C minus original)
3. Appliquer magnitude warping (Exp. D minus original)
4. Concaténer : `[original, aug_B, aug_DWT, aug_D]`

**Retourne :** `(X_FULL, y_FULL)` — 4× les époques originales

---

## Fonction principale d'augmentation

### `augment_train_set(X_train, y_train, subject_ids_train, out_dir, seed=42)`

Orchestre toutes les expériences d'augmentation et sauvegarde les résultats.

**Paramètres :**
- `X_train` — Epochs d'entraînement (N × 1000)
- `y_train` — Labels/scores (N,)
- `subject_ids_train` — IDs sujets (N,) pour LOSO
- `out_dir` — Répertoire de sortie
- `seed` — Graine pour reproductibilité (défaut 42)

**Algorithme :**
1. Initialiser `rng = np.random.default_rng(seed)`
2. Sauvegarder `X_train_A.npy`, `y_train_A.npy`, `subject_ids_train_A.npy` (exp. A = original)
3. Générer exp. B → sauvegarder `X_train_B.npy`, `y_train_B.npy`, `subject_ids_train_B.npy`
4. Générer exp. C → sauvegarder `X_train_C.npy`, `y_train_C.npy`, `subject_ids_train_C.npy`
5. Générer exp. D → sauvegarder `X_train_D.npy`, `y_train_D.npy`, `subject_ids_train_D.npy`
6. Générer exp. FULL → sauvegarder `X_train_FULL.npy`, `y_train_FULL.npy`, `subject_ids_train_FULL.npy`

**Gestion des subject_ids :** Pour les époques augmentées, les subject_ids sont dupliqués (tile strategy) pour maintenir la cohérence LOSO. Ex: si le sujet 3 a 40 époques dans A, il en a 80 dans B, 120 dans C, etc.

**Sorties :** Fichiers `.npy` dans `out_dir/` :
```
X_train_A.npy     y_train_A.npy     subject_ids_train_A.npy
X_train_B.npy     y_train_B.npy     subject_ids_train_B.npy
X_train_C.npy     y_train_C.npy     subject_ids_train_C.npy
X_train_D.npy     y_train_D.npy     subject_ids_train_D.npy
X_train_FULL.npy  y_train_FULL.npy  subject_ids_train_FULL.npy
```

---

## Fonctions de validation

### `validate_augmentation(X_orig, X_aug, fs=FS)`

Vérifie que les ratios TBR/EI/TAR varient < ±15% après augmentation (règle N°5).

**Algorithme :**
1. Calculer TBR = θ/β, EI = β/(α+θ), TAR = θ/α pour chaque époque originale et augmentée
2. Comparer les distributions
3. Retourner un rapport de validation avec les déviations max

---

## Fonctions de visualisation

### `plot_augmentation_comparison(X_orig, X_aug, aug_name, out_path=None)`
Compare visuellement une époque originale et son augmentation (signal + PSD).

### `plot_band_preservation(X_orig, X_aug_B, X_aug_C, X_aug_D, out_path=None)`
Compare les puissances par bande pour toutes les expériences.

### `plot_size_summary(sizes_dict, out_path=None)`
Bar chart montrant la taille de chaque dataset augmenté (A < B < C < D < FULL).

---

## Références scientifiques

| Méthode | Référence |
|---------|-----------|
| Bruit gaussien | Knowledge-Based Systems (2025), IEEE TNSRE (2022) |
| Scaling | Computers in Biology and Medicine (2025) |
| Time Shift | Braindecode official transformations |
| DWT frequency | IEEE TNSRE (2022) |
| Magnitude Warping | Knowledge-Based Systems (2025) |
| 5 règles | Bio-Protocol (2023), Braindecode |
