# merge_scoring.py — Documentation Détaillée

## Vue d'ensemble

`merge_scoring.py` fusionne les signaux EEG bruts avec leurs scores calculés et effectue le rééchantillonnage vers la fréquence cible de 250 Hz. Il constitue le pont entre les scripts de scoring et les pipelines d'entraînement ML/DL.

**Fichier :** `src/data/scoring/merge_scoring.py`  
**Lignes :** ~368  
**Rôle :** Fusion signaux-scores + rééchantillonnage vers 250 Hz → fichiers .npy

---

## Rééchantillonnage

### Concentration : 200 Hz → 250 Hz
- Époque source : 800 samples @ 200 Hz (4 secondes)
- Époque cible : 1000 samples @ 250 Hz (4 secondes)
- **Méthode :** Filtre polyphase `scipy.signal.resample_poly(epoch, up=5, down=4)`
  - up=5, down=4 → facteur 5/4 = 1.25 → 800 × 1.25 = 1000 ✓

### Stress : 128 Hz → 250 Hz
- Époque source : 512 samples @ 128 Hz (4 secondes)
- Époque cible : 1000 samples @ 250 Hz (4 secondes)
- **Méthode :** Filtre polyphase `scipy.signal.resample_poly(epoch, up=125, down=64)`
  - up=125, down=64 → facteur 125/64 ≈ 1.953 → 512 × 1.953 ≈ 1000 ✓

**Pourquoi polyphase ?** Préserve les composantes spectrales sans distorsion de phase, contrairement à l'interpolation naïve. Applique automatiquement un filtre anti-repliement (anti-aliasing).

---

## Constantes

```python
LEVEL_CODE = {
    'natural':   0,
    'lowlevel':  1,
    'midlevel':  2,
    'highlevel': 3,
}
```

---

## Fonctions

### `build_concentration_dataset(df_scores)`

Construit le dataset de concentration rééchantillonné à partir du CSV de scores.

**Paramètre :** `df_scores` — DataFrame de `scored_concentration.csv`

**Algorithme :**
```
Pour chaque ligne du DataFrame (par fichier .txt) :
    signal = read_txt_file(row['file'])     # Lire le signal brut
    epochs = segment(signal, 800, step=800) # Segmenter sans overlap
    epoch = epochs[row['epoch_idx']]        # Récupérer l'époque par index
    
    epoch_250 = resample_poly(epoch, up=5, down=4)  # 800 → 1000 points
    
    X.append(epoch_250)
    y_score.append(row['conc_score'])
    subjects.append(row['subject_id'])
    levels.append(LEVEL_CODE[row['level']])
```

**Retourne :** `dict` avec clés `{'X', 'y_score', 'subjects', 'levels'}`

---

### `build_stress_dataset(df_scores)`

Construit le dataset de stress rééchantillonné à partir du CSV de scores.

**Paramètre :** `df_scores` — DataFrame de `scored_stress.csv`

**Algorithme :**
```
Pour chaque fichier .mat unique dans df_scores :
    mat = scipy.io.loadmat(filepath)
    eeg = extract_fp2(mat)   # Canal AF3 pour stress
    epochs = segment(eeg, 512, step=512)
    
    Pour chaque époque de ce fichier :
        epoch = epochs[row['epoch_idx']]
        epoch_250 = resample_poly(epoch, up=125, down=64)  # 512 → 1000
        
        X.append(epoch_250)
        y_score.append(row['stress_score'])
        subjects.append(row['subject_id'])
```

**Retourne :** `dict` avec clés `{'X', 'y_score', 'subjects', 'task'}`

---

### `validate_and_print(name, data)`

Affiche des statistiques de validation sur le dataset construit.

**Paramètre :**
- `name` — Nom du dataset ('concentration' ou 'stress')
- `data` — Dict retourné par `build_*_dataset()`

**Sorties console :**
```
Dataset: concentration
  Shape X      : (1240, 1000)
  Shape y      : (1240,)
  Score range  : [0.12, 9.87]
  Score mean   : 5.23 ± 2.41
  N sujets     : 15
  N niveaux    : 4 (natural=310, low=310, mid=310, high=310)
```

**Vérifications :**
1. Shape X = (N, 1000) — exactement 1000 points après rééchantillonnage
2. Scores dans [0, 10]
3. Pas de NaN
4. Distribution équilibrée par niveau/sujet

---

### `save_dataset(name, data)`

Sauvegarde le dataset en fichiers .npy.

**Paramètre :**
- `name` — 'concentration' ou 'stress'
- `data` — Dict du dataset

**Fichiers créés dans `data/Merge_datasets/` :**

Pour **concentration** :
```
X_concentration.npy             # (N, 1000) float32
y_conc_score.npy               # (N,) float32 — scores 0-10
subjects_concentration.npy     # (N,) int — IDs sujets 1-15
levels_concentration.npy       # (N,) int — 0/1/2/3 = natural/.../highlevel
```

Pour **stress** :
```
X_stress.npy                   # (N, 1000) float32
y_stress_score.npy             # (N,) float32 — scores 0-10
subjects_stress.npy            # (N,) int — IDs sujets 1-40
```

---

### `main()`

Orchestre la fusion complète des deux datasets.

```python
# Charger les CSVs de scores
df_conc   = pd.read_csv('data/Scoring/scored_concentration.csv')
df_stress = pd.read_csv('data/Scoring/scored_stress.csv')

# Construire les datasets
data_conc   = build_concentration_dataset(df_conc)
data_stress = build_stress_dataset(df_stress)

# Valider et sauvegarder
validate_and_print('concentration', data_conc)
validate_and_print('stress', data_stress)
save_dataset('concentration', data_conc)
save_dataset('stress', data_stress)
```

---

## Structure des fichiers de sortie

```
data/Merge_datasets/
├── X_concentration.npy         # (N_conc, 1000) — signaux @ 250 Hz
├── y_conc_score.npy            # (N_conc,) — scores [0-10]
├── subjects_concentration.npy  # (N_conc,) — IDs sujets (1-15)
├── levels_concentration.npy    # (N_conc,) — niveaux (0-3)
├── X_stress.npy                # (N_stress, 1000) — signaux @ 250 Hz
├── y_stress_score.npy          # (N_stress,) — scores [0-10]
└── subjects_stress.npy         # (N_stress,) — IDs sujets (1-40)
```

---

## Position dans le pipeline

```
scored_concentration.csv ──┐
                            ├──→ merge_scoring.py ──→ X_*.npy, y_*.npy
scored_stress.csv ──────────┘

X_*.npy, y_*.npy ──→ pipeline_fp2.py (split) ──→ pipeline_regression.py (augmentation + features)
```
