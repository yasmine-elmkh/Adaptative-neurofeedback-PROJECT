# feature_eng.py — Documentation Détaillée

## Vue d'ensemble

`feature_eng.py` extrait **78 features avancées** par époque EEG, organisées en 8 catégories. Il étend le vecteur de 15 features baseline en ajoutant des features DWT, texturales, non-linéaires, de transition et des noyaux binaires NeuroFeat. Conçu pour maximiser la performance des modèles ML au détriment de la latence embarquée.

**Fichier :** `src/data/feature_eng.py`  
**Lignes :** ~1073  
**Rôle :** Extraction de 78 features avancées pour ML feature engineering

---

## Constantes

| Constante | Valeur | Description |
|-----------|--------|-------------|
| `FS` | 250 | Fréquence d'échantillonnage (Hz) |
| `EPOCH_SAMPLES` | 1000 | Samples par époque |
| `WAVELET` | 'db4' | Ondelette DWT (Daubechies 4) |
| `DWT_LEVEL` | 4 | Niveau de décomposition DWT |
| `WINDOW_W` | 16 | Fenêtre ω = ⌈√250⌉ pour noyaux NeuroFeat |
| `EPS` | 1e-10 | Protection contre division par zéro |

---

## Vue d'ensemble des 8 catégories

| Catégorie | Nombre | Description |
|-----------|--------|-------------|
| 1 — PSD Welch | 5 | Puissances de bandes δ/θ/α/β/γ |
| 2 — Ratios cognitifs | 5 | TBR, ABR, EI, TAR, RelEnergy_β |
| 3 — Hjorth + temporel | 6 | Activity, Mobility, Complexity, Power, MeanAmp, ZCR |
| 4 — DWT sous-bandes | 20 | 5 sous-bandes × 4 stats (mean, std, energy, entropy) |
| 5 — Texturales | 20 | Skewness, kurtosis, IQR, RMS, peak-to-peak, etc. |
| 6 — Non-linéaires/entropies | 7 | ApEn, SampEn, PermEn, SpectralEn, HFD, RenyiEn, LogEnergyEn |
| 7 — Patterns de transition | 6 | pct_up, pct_down, pct_flat, up_streak, down_streak, trans_freq |
| 8 — NeuroFeat binaires | 9 | φ₁/φ₂/φ₃ × (mean, std, entropy) |
| **Total** | **78** | |

---

## Catégorie 1 — PSD Welch (5 features)

### `extract_psd_features(epoch)`

Identique à `features_extraction.py` — calcule les 5 puissances de bandes.

**Paramètre :** `epoch` — tableau 1D 1000 points  
**Retourne :** dict `{'Pd', 'Pt', 'Pa', 'Pb', 'Pg'}`

Voir `features_extraction.md` pour les détails.

---

## Catégorie 2 — Ratios cognitifs (5 features)

### `extract_ratio_features(psd_feats)`

Calcule les ratios cognitifs à partir des puissances de bandes.

**Paramètre :** `psd_feats` — dict retourné par `extract_psd_features()`  
**Retourne :** dict `{'TBR', 'ABR', 'EI', 'TAR', 'RelEnergy_beta'}`

```python
TBR           = Pt / (Pb + eps)            # Theta/Beta Ratio
ABR           = Pa / (Pb + eps)            # Alpha/Beta Ratio
EI            = Pb / (Pa + Pt + eps)       # Engagement Index
TAR           = Pt / (Pa + eps)            # Theta/Alpha Ratio
RelEnergy_beta = Pb / (Pd+Pt+Pa+Pb+Pg+eps) # Énergie relative beta
```

---

## Catégorie 3 — Hjorth + temporel (6 features)

### `extract_temporal_features(epoch)`

Calcule les 3 paramètres de Hjorth + 3 features temporelles, dont le ZCR.

**Paramètre :** `epoch` — tableau 1D  
**Retourne :** dict `{'Activity', 'Mobility', 'Complexity', 'Power', 'MeanAmp', 'ZCR'}`

```python
ZCR = somme des changements de signe / longueur   # Zero Crossing Rate
```

**ZCR** — Taux de croisement zéro. Mesure la "vitesse" d'oscillation du signal.  
**Utilité :** ZCR élevé → oscillations rapides → activité cognitive élevée.

---

## Catégorie 4 — DWT sous-bandes (20 features)

### `extract_dwt_subband_features(epoch)`

Décompose l'époque en ondelettes (db4, niveau 4) et calcule 4 statistiques par sous-bande.

**Paramètre :** `epoch` — tableau 1D 1000 points  
**Retourne :** dict `{'DWT_{band}_{stat}'}` — 5 bandes × 4 stats = 20 features

**5 sous-bandes DWT :**
- `cA4` — Approximation niveau 4 (fréquences très basses ≈ 0-15 Hz)
- `cD4` — Détails niveau 4 (≈ 7.8-15.6 Hz — alpha/beta inférieur)
- `cD3` — Détails niveau 3 (≈ 15.6-31.25 Hz — beta supérieur/gamma)
- `cD2` — Détails niveau 2 (≈ 31.25-62.5 Hz — gamma+)
- `cD1` — Détails niveau 1 (≈ 62.5-125 Hz — haute fréquence)

**4 statistiques par sous-bande :**
```python
mean    = np.mean(np.abs(coeffs))           # Amplitude absolue moyenne
std     = np.std(coeffs)                     # Écart-type
energy  = np.sum(coeffs**2)                  # Énergie (norme L2²)
entropy = _shannon_entropy(coeffs)           # Entropie de Shannon
```

**Convention de nommage :** `DWT_cA4_mean`, `DWT_cD4_energy`, `DWT_cD1_entropy`, etc.

---

## Catégorie 5 — Texturales (20 features)

### `extract_textural_features(epoch)`

Calcule des statistiques descriptives avancées du signal temporel + des statistiques DWT.

**Paramètre :** `epoch` — tableau 1D  
**Retourne :** dict de 20 features

**10 features sur signal brut :**
```python
skewness     = scipy.stats.skew(epoch)          # Asymétrie de la distribution
kurtosis     = scipy.stats.kurtosis(epoch)       # Aplatissement (queue de distribution)
IQR          = np.percentile(epoch,75) - np.percentile(epoch,25)  # Interquartile range
RMS          = np.sqrt(np.mean(epoch**2))        # Root Mean Square
peak_to_peak = np.max(epoch) - np.min(epoch)     # Amplitude crête-à-crête
crest_factor = np.max(np.abs(epoch)) / (RMS+eps) # Facteur de crête
median       = np.median(epoch)                  # Médiane
max_val      = np.max(epoch)                     # Valeur maximale
min_val      = np.min(epoch)                     # Valeur minimale
MAD          = np.mean(np.abs(epoch - median))   # Déviation absolue médiane
```

**10 features DWT (skewness + kurtosis par sous-bande) :**
```python
DWT_cA4_skew, DWT_cA4_kurt
DWT_cD4_skew, DWT_cD4_kurt
DWT_cD3_skew, DWT_cD3_kurt
DWT_cD2_skew, DWT_cD2_kurt
DWT_cD1_skew, DWT_cD1_kurt
```

**Utilité des features texturales :**
- Skewness/kurtosis détectent des distributions non gaussiennes (artefacts, patterns cognitifs)
- Crest factor mesure les pics transitoires (artefacts oculaires résiduels)
- IQR/MAD sont robustes aux outliers

---

## Catégorie 6 — Non-linéaires/Entropies (7 features)

### `extract_nonlinear_features(epoch)`

Calcule 7 mesures de complexité et d'entropie du signal EEG.

**Paramètre :** `epoch` — tableau 1D  
**Retourne :** dict `{'ApEn', 'SampEn', 'PermEn', 'SpectralEn', 'HFD', 'RenyiEn', 'LogEnergyEn'}`

---

#### Helpers d'entropie privés

### `_shannon_entropy(coeffs)`
Entropie de Shannon sur les coefficients DWT.
```python
p = coeffs² / (sum(coeffs²) + eps)
H = -sum(p × log2(p + eps))
```

### `_approximate_entropy(x, m=2, r_factor=0.2)`
Approximate Entropy (ApEn) — mesure la régularité du signal.
- `m` — dimension de plongement (longueur des templates)
- `r_factor` — tolérance = r_factor × std(x)

**Algorithme :** Compte les paires de templates de longueur m et m+1 dont la distance Chebyshev < r. ApEn élevée → signal irrégulier.

### `_sample_entropy(x, m=2, r_factor=0.2)`
Sample Entropy (SampEn) — version améliorée d'ApEn, sans auto-similarité.  
Moins biaisée que l'ApEn pour des séquences courtes.

### `_permutation_entropy(x, order=3, delay=1)`
Permutation Entropy (PermEn) — entropie basée sur les patterns ordinaux.
1. Créer des vecteurs de longueur `order` avec délai `delay`
2. Calculer le rang de chaque vecteur (permutation)
3. Compter les fréquences de chaque permutation
4. Calculer l'entropie de Shannon sur ces fréquences

**Avantage :** Robuste au bruit, efficace computationnellement.

### `_spectral_entropy(epoch)`
Entropie spectrale — mesure l'uniformité de la distribution de puissance fréquentielle.
```python
psd_norm = psd / (sum(psd) + eps)
H_spectral = -sum(psd_norm × log2(psd_norm + eps))
```
Haute entropie spectrale → puissance distribuée uniformément (signal bruité ou actif).

### `_renyi_entropy(epoch, alpha=2)`
Entropie de Rényi d'ordre α=2 sur la PSD.
```python
H_renyi = log2(sum(p²)) / (1 - alpha)
```
Généralisation de l'entropie de Shannon. α=2 accentue les fréquences dominantes.

### `_log_energy_entropy(epoch)`
Entropie d'énergie logarithmique sur les coefficients DWT.
```python
H_le = sum(log2(x² + eps))
```

### `_higuchi_fractal_dimension(x, kmax=10)`
Dimension fractale de Higuchi (HFD) — mesure la complexité temporelle du signal.

**Algorithme :**
1. Pour k = 1 à kmax, calculer la longueur de courbe L(k)
2. HFD = pente de log(L(k)) vs log(1/k)

**Interprétation :**
- HFD ≈ 1 → signal très régulier (sinusoïde pure)
- HFD ≈ 2 → signal très irrégulier (bruit blanc)
- EEG cognitif ≈ 1.5-1.8 (fractal naturel)

---

## Catégorie 7 — Patterns de transition (6 features)

### `extract_transition_features(epoch)`

Analyse les patterns montants/descendants/plats dans le signal.

**Paramètre :** `epoch` — tableau 1D  
**Retourne :** dict `{'pct_up', 'pct_down', 'pct_flat', 'up_streak', 'down_streak', 'trans_freq'}`

**Algorithme :**
1. Calculer les différences `diff = np.diff(epoch)`
2. Classifier chaque transition :
   - `up` si diff > eps
   - `down` si diff < -eps
   - `flat` si |diff| ≤ eps
3. Calculer les pourcentages et les longueurs de séquences (streaks)

```python
pct_up     = count(diff > 0) / len(diff)      # % de montées
pct_down   = count(diff < 0) / len(diff)      # % de descentes
pct_flat   = count(diff == 0) / len(diff)     # % de plateaux
up_streak  = longueur_moy_sequences_montantes
down_streak = longueur_moy_sequences_descendantes
trans_freq = nb_changements_direction / len(diff)  # Fréquence de changement
```

**Utilité :** Capture les oscillations et leur régularité temporelle sans passer par la fréquence.

---

## Catégorie 8 — NeuroFeat binaires (9 features)

### `extract_neurofeat_features(epoch)`

Applique 3 noyaux binaires originaux sur des fenêtres glissantes de taille ω=16.

**Paramètre :** `epoch` — tableau 1D  
**Retourne :** dict `{'NF_phi1_mean', 'NF_phi1_std', 'NF_phi1_entropy', ...}` — 9 features (3 noyaux × 3 stats)

**Fenêtre ω = ⌈√250⌉ = 16 samples**

**3 noyaux NeuroFeat φ₁/φ₂/φ₃ :**

```python
φ₁(w) = (mean(w) > 0) ? 1 : 0              # Signe de la moyenne locale
φ₂(w) = (energy(w) > global_median_energy) ? 1 : 0   # Énergie > médiane globale
φ₃(w) = (w[-1] > w[0]) ? 1 : 0            # Tendance montante sur la fenêtre
```

**Pour chaque noyau φᵢ, calculer sur toutes les fenêtres :**
```python
activation_i = [φᵢ(epoch[j:j+ω]) for j in range(0, 1000-ω, ω//2)]
NF_phiN_mean    = mean(activation_i)        # Fraction de fenêtres activées
NF_phiN_std     = std(activation_i)         # Variabilité d'activation
NF_phiN_entropy = shannon_entropy(activation_i)  # Entropie d'activation
```

**Intuition :**
- φ₁ : fréquence des moments où l'énergie locale est positive → activité
- φ₂ : fréquence des pics d'énergie → saillances temporelles
- φ₃ : fréquence des tendances montantes → dynamisme du signal

---

## Fonctions principales

### `extract_all_features(epoch)`

Appelle les 8 catégories séquentiellement et assemble le dict final de 78 features.

**Paramètre :** `epoch` — tableau 1D 1000 points  
**Retourne :** `dict` avec 78 clés

**Ordre de calcul :**
```python
psd_feats     = extract_psd_features(epoch)
ratio_feats   = extract_ratio_features(psd_feats)
temporal_feats = extract_temporal_features(epoch)
dwt_feats     = extract_dwt_subband_features(epoch)
textural_feats = extract_textural_features(epoch)
nonlinear_feats = extract_nonlinear_features(epoch)
transition_feats = extract_transition_features(epoch)
neurofeat_feats = extract_neurofeat_features(epoch)

# Fusion
return {**psd_feats, **ratio_feats, **temporal_feats, **dwt_feats,
        **textural_feats, **nonlinear_feats, **transition_feats, **neurofeat_feats}
```

---

### `get_feature_names()`

Retourne la liste ordonnée des 78 noms de features.

**Algorithme :** Génère une époque dummy `np.zeros(1000)`, appelle `extract_all_features()`, retourne `list(result.keys())`

**Usage :** Pour créer les colonnes d'un DataFrame pandas ou les noms d'axes.

---

### `extract_features_batch(X_epochs, y_labels, verbose=True)`

Extrait les features pour un batch complet d'époques.

**Paramètres :**
- `X_epochs` — Tableau 2D (N × 1000)
- `y_labels` — Labels/scores (N,)
- `verbose` — Afficher la progression (barre de progression)

**Algorithme :**
```python
features = []
for i, epoch in enumerate(X_epochs):
    f = extract_all_features(epoch)
    features.append([f[name] for name in feature_names])
return np.array(features, dtype=float32), feature_names
```

**Gestion des erreurs :** Les valeurs NaN/Inf sont remplacées par 0 via `np.nan_to_num()`.

**Retourne :** `(features_matrix, feature_names)` — shape (N, 78)

---

## Flux d'exécution principal

Appelé depuis `pipeline_regression.py` — voir `step4_extract_features()` dans ce module.

---

## Comparaison feat15 vs feat78

| Aspect | feat15 | feat78 |
|--------|--------|--------|
| Nombre features | 15 | 78 |
| Temps/époque | < 10 ms | 50-200 ms |
| Embarquable | Oui (ESP32) | Non |
| Catégories | PSD, Ratios, Hjorth | + DWT, Textural, Entropies, Transitions, NeuroFeat |
| Gain R² typique | — | +0.02 à +0.05 |

---

## Dépendances

| Bibliothèque | Usage |
|-------------|-------|
| `numpy` | Calculs vectoriels |
| `scipy.signal` | Welch PSD |
| `scipy.stats` | Skewness, kurtosis |
| `pywt` | DWT (PyWavelets) |
