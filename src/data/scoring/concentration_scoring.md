# concentration_scoring.py — Documentation Détaillée

## Vue d'ensemble

`concentration_scoring.py` assigne un **score de concentration continu (0-10)** à chaque époque EEG du dataset Cognitive Load Concentration. Il implémente un algorithme en 2 passes (calibration des percentiles + calcul des scores) basé sur 4 biomarqueurs EEG pondérés par leur corrélation de Spearman avec le niveau cognitif de la tâche.

**Fichier :** `src/data/scoring/concentration_scoring.py`  
**Lignes :** ~639  
**Rôle :** Scoring de la concentration EEG — génère `scored_concentration.csv`

---

## Constantes

| Constante | Valeur | Description |
|-----------|--------|-------------|
| `FS` | 200 | Fréquence d'échantillonnage du dataset (Hz) — OpenBCI |
| `EPOCH_SIZE` | 800 | Samples par époque (200 Hz × 4 s) |
| `CHANNEL` | 1 | Index du canal Fp2 dans les fichiers .txt |
| `W_FOCUS` | 0.314 | Poids du Focus = EI × ZCR |
| `W_EI` | 0.276 | Poids de l'Engagement Index |
| `W_ZCR` | 0.237 | Poids du Zero Crossing Rate |
| `W_TBR_INV` | 0.173 | Poids de 1/TBR (TBR inversé) |

### Plages de scores par niveau cognitif
- `natural` → [0.0, 2.5] — état naturel, pas de tâche cognitive
- `lowlevel` → [2.5, 5.0] — faible charge cognitive
- `midlevel` → [5.0, 7.5] — charge cognitive modérée
- `highlevel` → [7.5, 10.0] — forte charge cognitive

---

## Fonctions utilitaires

### `bandpower(signal, fmin, fmax)`

Calcule la puissance dans une bande fréquentielle via la méthode de Welch.

**Paramètres :**
- `signal` — Tableau 1D (800 points à 200 Hz)
- `fmin`, `fmax` — Bornes de la bande (Hz)

**Algorithme :**
```python
freqs, psd = scipy.signal.welch(signal, fs=FS, nperseg=min(256, len(signal)))
mask = (freqs >= fmin) & (freqs <= fmax)
return np.trapz(psd[mask], freqs[mask])
```

**Retourne :** `float` — puissance en µV²/Hz intégrée

---

### `extract_features(epoch)`

Extrait les 4 biomarqueurs de concentration d'une époque.

**Paramètre :** `epoch` — tableau 1D (800 points)  
**Retourne :** `dict` `{'focus', 'ei', 'zcr', 'tbr'}`

**Algorithme :**
```python
Pa = bandpower(epoch, 8, 13)      # Alpha
Pb = bandpower(epoch, 13, 30)     # Beta
Pt = bandpower(epoch, 4, 8)       # Theta
eps = 1e-10

EI    = Pb / (Pa + Pt + eps)                 # Engagement Index
ZCR   = count_zero_crossings(epoch) / len(epoch)  # Zero Crossing Rate
TBR   = Pt / (Pb + eps)                      # Theta/Beta Ratio
Focus = EI * ZCR                              # Indicateur composite
```

**Interprétation :**
- `Focus = EI × ZCR` : produit de l'engagement spectral et de la dynamique temporelle
- `TBR_INV = 1/TBR` : inversé car TBR ↑ signifie concentration ↓

---

### `normalize_feature(value, p1, p99)`

Normalise une feature dans [0, 1] par écrêtage aux percentiles 1% et 99%.

**Paramètres :**
- `value` — Valeur brute de la feature
- `p1`, `p99` — Percentiles 1% et 99% de la feature sur tout le dataset

**Algorithme :**
```python
clipped = np.clip(value, p1, p99)
return (clipped - p1) / (p99 - p1 + eps)
```

**Pourquoi percentiles plutôt que min/max ?** Robustesse aux valeurs aberrantes. Les percentiles 1% et 99% éliminent les 2% d'outliers extrêmes.

---

### `compute_conc_score(feat, p1p99, lo, hi)`

Calcule le score de concentration final pour une époque.

**Paramètres :**
- `feat` — Dict de features `{'focus', 'ei', 'zcr', 'tbr'}`
- `p1p99` — Dict de percentiles `{feature: (p1, p99)}`
- `lo`, `hi` — Bornes de la plage de score du niveau (ex: 5.0, 7.5 pour midlevel)

**Algorithme :**

**Étape 1 — Normalisation [0,1] de chaque feature :**
```python
focus_n  = normalize_feature(feat['focus'],      p1p99['focus'][0],   p1p99['focus'][1])
ei_n     = normalize_feature(feat['ei'],         p1p99['ei'][0],      p1p99['ei'][1])
zcr_n    = normalize_feature(feat['zcr'],        p1p99['zcr'][0],     p1p99['zcr'][1])
tbr_n    = normalize_feature(1/feat['tbr']+eps,  p1p99['tbr_inv'][0], p1p99['tbr_inv'][1])
```

**Étape 2 — Score composite pondéré [0,1] :**
```python
composite = (W_FOCUS * focus_n + W_EI * ei_n + 
             W_ZCR * zcr_n + W_TBR_INV * tbr_n)
# composite ∈ [0, 1]
```

**Étape 3 — Projection dans la plage du niveau :**
```python
score = lo + composite * (hi - lo)
score = np.clip(score, lo, hi)
```

**Retourne :** `float` score de concentration dans [lo, hi]

**Justification des poids :** Les poids W_FOCUS=0.314, W_EI=0.276, W_ZCR=0.237, W_TBR_INV=0.173 ont été déterminés par corrélation de Spearman entre chaque feature et le label cognitif (natural/low/mid/high). Le Focus composite obtient la corrélation la plus élevée.

---

### `read_txt_file(filepath)`

Lit un fichier .txt OpenBCI et extrait le canal Fp2.

**Paramètre :** `filepath` — chemin vers le fichier .txt

**Format attendu :**
- 25 colonnes par ligne
- Canal Fp2 = colonne EEG d'index 1 (après soustraction du timestamp)
- Valeurs ADC en entiers → conversion µV : `valeur × OPENBCI_SCALE`

**Algorithme :**
1. Lire le fichier ligne par ligne (ignorer les commentaires `%`)
2. Parser les 25 colonnes
3. Extraire la colonne d'index 1 (EEG Fp2)
4. Convertir ADC → µV via `OPENBCI_SCALE = 0.02235`

**Retourne :** `numpy.ndarray` 1D (signal Fp2 en µV)

---

### `calibrate_percentiles(all_feats)`

**Première passe** — calibre les percentiles 1% et 99% sur tout le dataset.

**Paramètre :** `all_feats` — liste de dicts `{'focus', 'ei', 'zcr', 'tbr'}` de toutes les époques

**Algorithme :**
```python
for feature_name in ['focus', 'ei', 'zcr', 'tbr_inv']:
    values = [f[feature_name] for f in all_feats]
    p1p99[feature_name] = (np.percentile(values, 1), np.percentile(values, 99))
```

**Retourne :** `dict` `{feature_name: (p1, p99)}`

**Pourquoi calibrer sur tout le dataset ?** Pour garantir une normalisation cohérente entre sujets et niveaux cognitifs. Calibrer par sujet créerait une variance artificielle.

---

### `process_concentration_dataset()`

**Fonction principale** — orchestre l'algorithme en 2 passes.

**Algorithme :**

**Passe 1 — Collecte des features :**
```
Pour chaque fichier .txt dans data/Cognitive_Load_EEG_dataset/ :
    signal = read_txt_file(filepath)
    Pour chaque époque de 800 points (sans overlap) :
        feat = extract_features(epoch)
        Enregistrer feat + métadonnées (sujet, niveau, fichier)
```

**Passe 2 — Calibration + scoring :**
```
p1p99 = calibrate_percentiles(all_feats)

Pour chaque époque (feat, métadonnées) :
    niveau = métadonnées['level']
    (lo, hi) = SCORE_RANGES[niveau]
    score = compute_conc_score(feat, p1p99, lo, hi)
```

**4 niveaux cognitifs et leurs plages :**
```python
SCORE_RANGES = {
    'natural':    (0.0, 2.5),
    'lowlevel':   (2.5, 5.0),
    'midlevel':   (5.0, 7.5),
    'highlevel':  (7.5, 10.0),
}
```

**Retourne :** `pandas.DataFrame` avec colonnes `['subject_id', 'level', 'task', 'file', 'epoch_idx', 'conc_score', 'focus', 'ei', 'zcr', 'tbr']`

---

### `validate_scores(df)`

Valide que les scores sont bien distribués par niveau.

**Paramètre :** `df` — DataFrame retourné par `process_concentration_dataset()`

**Vérifications :**
1. Chaque niveau a des scores dans sa plage attendue
2. Pas de scores NaN/Inf
3. Corrélation positive entre niveau cognitif et score (natural < low < mid < high en moyenne)
4. Affiche des statistiques par niveau (mean, std, min, max)

---

### `generate_visualizations(df)`

Génère 4 figures PNG dans `data/Scoring/concentration/`.

**Figures :**
1. `01_score_distribution.png` — Distribution des scores par niveau (histogrammes)
2. `02_score_by_subject.png` — Score moyen par sujet (boxplot inter-sujets)
3. `03_features_correlation.png` — Corrélation entre features et niveau cognitif
4. `04_level_separation.png` — Séparation des niveaux cognitifs par score

---

### `main()`

Point d'entrée du script. Orchestre les 4 étapes :

```python
df = process_concentration_dataset()
validate_scores(df)
generate_visualizations(df)
df.to_csv('data/Scoring/scored_concentration.csv', index=False)
```

**Sortie :** `data/Scoring/scored_concentration.csv`

---

## Format du CSV de sortie

| Colonne | Type | Description |
|---------|------|-------------|
| `subject_id` | int | ID du sujet (1-15) |
| `level` | str | Niveau cognitif (natural/lowlevel/midlevel/highlevel) |
| `task` | str | Type de tâche (arithmetic/stroop/etc.) |
| `file` | str | Nom du fichier .txt source |
| `epoch_idx` | int | Index de l'époque dans le fichier |
| `conc_score` | float | Score de concentration [0-10] |
| `focus` | float | Feature Focus brute |
| `ei` | float | Feature Engagement Index |
| `zcr` | float | Feature Zero Crossing Rate |
| `tbr` | float | Feature Theta/Beta Ratio |

---

## Justification des poids et de la formule

### Corrélations de Spearman (Salam et al. 2026, Samsa & Altıntop 2026)

| Feature | Corrélation Spearman | Poids assigné |
|---------|---------------------|---------------|
| Focus = EI × ZCR | ρ = 0.47 | 0.314 |
| EI | ρ = 0.41 | 0.276 |
| ZCR | ρ = 0.35 | 0.237 |
| 1/TBR | ρ = 0.26 | 0.173 |

Les poids sont normalisés pour sommer à 1.0.

### Ancrage des plages de score

Les 4 plages [0-2.5], [2.5-5], [5-7.5], [7.5-10] correspondent aux 4 niveaux cognitifs du protocole Cognitive Load Concentration (natural < low < mid < high), ancrées à des valeurs équidistantes pour faciliter l'interprétation.
