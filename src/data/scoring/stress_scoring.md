# stress_scoring.py — Documentation Détaillée

## Vue d'ensemble

`stress_scoring.py` assigne un **score de stress continu (0-10)** à chaque époque EEG du dataset SAM40 Stress. Il utilise les **ground truth des échelles psychométriques** (fichier scales.xls) comme ancre principale et ajoute une micro-variation basée sur l'EEG (±0.5 point max). Pour les tâches sans ground truth (Relax), il estime le stress à partir du ZCR.

**Fichier :** `src/data/scoring/stress_scoring.py`  
**Lignes :** ~606  
**Rôle :** Scoring du stress EEG — génère `scored_stress.csv`

---

## Constantes

| Constante | Valeur | Description |
|-----------|--------|-------------|
| `FS_STRESS` | 128 | Fréquence d'échantillonnage SAM40 (Hz) — EMOTIV |
| `EPOCH_SIZE` | 512 | Samples par époque (128 Hz × 4 s) |
| `CHANNEL` | 0 | Index du canal AF3 (frontal gauche EMOTIV) |
| `MICRO_VAR_MAX` | 0.5 | Variation maximale EEG (±0.5 points) |

### Types de tâches SAM40

| Tâche | Alias | Ground Truth |
|-------|-------|--------------|
| Arithmetic | `maths` | Oui (scales.xls) |
| Mirror_image | `sym` | Oui (scales.xls) |
| Stroop | `stroop` | Oui (scales.xls) |
| Relax | — | Non (estimé par ZCR) |

---

## Fonctions

### `load_scales()`

Charge le fichier `scales.xls` contenant les évaluations psychométriques.

**Retourne :** `dict` `{(task, subject_id, trial): stress_score}`

**Format scales.xls :**
- Colonnes : Subject, Trial, Task, Stress_Scale (0-10)
- 40 sujets × 3 tâches × plusieurs essais

**Algorithme :**
1. Lire `data/SAM40_Stress_dataset/scales.xls` avec pandas
2. Parser chaque ligne : extraire (task, subject, trial) → score
3. Retourner le dict de lookup

---

### `bandpower(signal, fmin, fmax)`

Identique à `concentration_scoring.py` — calcule la puissance dans une bande via Welch.

**Paramètre notable :** `fs=FS_STRESS=128` Hz (différent de la concentration)

---

### `extract_features(epoch)`

Extrait les biomarqueurs de stress d'une époque SAM40.

**Paramètre :** `epoch` — tableau 1D (512 points à 128 Hz)  
**Retourne :** `dict` `{'ei', 'zcr', 'tbr', 'power'}`

```python
Pt = bandpower(epoch, 4, 8)       # Theta
Pa = bandpower(epoch, 8, 13)      # Alpha
Pb = bandpower(epoch, 13, 30)     # Beta
eps = 1e-10

EI    = Pb / (Pa + Pt + eps)
ZCR   = count_zero_crossings(epoch) / len(epoch)
TBR   = Pt / (Pb + eps)
Power = np.mean(epoch**2)
```

**Note :** Le canal utilisé est AF3 (frontal gauche, index 0 dans EMOTIV) — différent de la concentration qui utilise Fp2 (frontal droit OpenBCI).

---

### `parse_filename(filename)`

Parse le nom d'un fichier .mat SAM40 pour extraire les métadonnées.

**Format SAM40 :** `Sub{N}_{task}_{trial}.mat` ou variantes.

**Exemples :**
- `Sub01_Arithmetic_01.mat` → `(1, 'maths', 1)`
- `Sub15_Stroop_02.mat` → `(15, 'stroop', 2)`
- `Sub07_Relax_01.mat` → `(7, 'relax', 1)`

**Retourne :** `(subject_id, task_type, trial_number)` ou `None` si format inconnu.

---

### `get_stress_score(task, subject, trial, scales_dict, feat)`

**Fonction centrale** — calcule le score de stress pour une époque.

**Paramètres :**
- `task` — Type de tâche ('maths', 'sym', 'stroop', 'relax')
- `subject` — ID du sujet (1-40)
- `trial` — Numéro d'essai
- `scales_dict` — Dict de ground truth chargé par `load_scales()`
- `feat` — Dict de features EEG de l'époque

**Algorithme :**

**Cas 1 — Tâche avec ground truth (maths, sym, stroop) :**
```python
gt_score = scales_dict.get((task, subject, trial), 5.0)  # Défaut 5.0 si absent

# Micro-variation basée sur l'EI
ei_normalized = normalize(feat['ei'])  # [0, 1]
micro_var = (ei_normalized - 0.5) * 2 * MICRO_VAR_MAX  # [-0.5, +0.5]

score = gt_score + micro_var
score = np.clip(score, 0.0, 10.0)
```

**Logique micro-variation :** Un EI élevé → plus d'engagement → légèrement plus stressé. La variation est bornée à ±0.5 pour ne pas dénaturer le ground truth.

**Cas 2 — Tâche Relax (sans ground truth) :**
```python
# Stress estimé à partir du ZCR (0.5 à 1.5)
zcr_normalized = normalize(feat['zcr'])  # [0, 1]
score = 0.5 + zcr_normalized * 1.0  # [0.5, 1.5]
score = np.clip(score, 0.0, 2.0)
```

**Logique Relax :** Pendant la relaxation, le stress vrai est bas (0.5-1.5). Le ZCR capture les légères variations d'activité même au repos.

**Retourne :** `float` — score de stress [0-10]

---

### `process_stress_dataset(scales_dict)`

**Fonction principale** — parcourt tous les fichiers .mat et calcule les scores.

**Paramètre :** `scales_dict` — dict de ground truth chargé par `load_scales()`

**Algorithme :**
```
Pour chaque fichier .mat dans data/SAM40_Stress_dataset/ :
    (subject, task, trial) = parse_filename(filename)
    
    # Charger le fichier .mat
    mat_data = scipy.io.loadmat(filepath)
    
    # Extraire canal Fp2 (3 stratégies)
    eeg = extract_fp2(mat_data)  # → canal AF3 (index 0) pour stress
    
    # Rééchantillonnage 128 Hz → 250 Hz (non appliqué ici, fait dans merge_scoring)
    
    # Segmenter en époques de 512 points (4s @ 128 Hz)
    epochs = segment(eeg, EPOCH_SIZE, step=EPOCH_SIZE//4)
    
    Pour chaque époque :
        feat = extract_features(epoch)
        score = get_stress_score(task, subject, trial, scales_dict, feat)
        Enregistrer (subject, task, trial, epoch_idx, stress_score, features...)
```

**Retourne :** `pandas.DataFrame`

---

### `validate_scores(df)`

Valide la distribution des scores de stress.

**Vérifications :**
1. Scores [0-10] sans NaN/Inf
2. Tâches stressantes (maths/sym/stroop) ont des scores > Relax (en moyenne)
3. Corrélation positive entre ground truth et scores calculés
4. Affiche la distribution par tâche (mean ± std)

**Exemple de sortie attendu :**
```
Relax    : mean=0.87 ± 0.31  [min=0.5,  max=1.5]
Arithmetic: mean=6.45 ± 1.23  [min=3.2,  max=9.1]
Mirror   : mean=5.73 ± 1.45  [min=2.1,  max=8.9]
Stroop   : mean=7.12 ± 0.98  [min=4.5,  max=9.8]
```

---

### `generate_visualizations(df)`

Génère 4 figures PNG dans `data/Scoring/stress/`.

**Figures :**
1. `01_score_by_task.png` — Distribution des scores par type de tâche
2. `02_score_by_subject.png` — Variabilité inter-sujets
3. `03_gt_vs_eeg.png` — Ground truth vs scores EEG-augmentés (scatter)
4. `04_micro_variation.png` — Distribution des micro-variations EEG (±0.5)

---

### `main()`

Point d'entrée. Orchestre les étapes :

```python
scales_dict = load_scales()
df = process_stress_dataset(scales_dict)
validate_scores(df)
generate_visualizations(df)
df.to_csv('data/Scoring/scored_stress.csv', index=False)
```

**Sortie :** `data/Scoring/scored_stress.csv`

---

## Format du CSV de sortie

| Colonne | Type | Description |
|---------|------|-------------|
| `subject_id` | int | ID du sujet (1-40) |
| `task` | str | Type de tâche (maths/sym/stroop/relax) |
| `trial` | int | Numéro d'essai |
| `epoch_idx` | int | Index de l'époque dans la session |
| `stress_score` | float | Score de stress [0-10] |
| `gt_score` | float | Ground truth (NaN pour Relax) |
| `ei` | float | Feature Engagement Index |
| `zcr` | float | Feature Zero Crossing Rate |
| `tbr` | float | Feature Theta/Beta Ratio |
| `power` | float | Puissance temporelle |

---

## Architecture de scoring SAM40 vs Cognitive Load

| Aspect | Concentration | Stress |
|--------|--------------|--------|
| Dataset | Cognitive Load (OpenBCI) | SAM40 (EMOTIV) |
| Sujets | 15 | 40 |
| Fréq. | 200 Hz | 128 Hz |
| Canal | Fp2 (index 1) | AF3 (index 0) |
| Ground truth | Niveau tâche (4 niveaux) | Échelles psychométriques (scales.xls) |
| Méthode score | Feature-based weighted sum | GT + micro-variation EEG |
| Tâches | arithmetic, stroop | maths, sym, stroop, relax |
