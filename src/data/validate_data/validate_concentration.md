# validate_concentration.py — Documentation Détaillée

## Vue d'ensemble

`validate_concentration.py` est un script de validation de Phase 1 pour le dataset Cognitive Load Concentration. Il valide la structure des fichiers .txt OpenBCI, extrait le canal Fp2 (index 1 dans le tableau EEG), effectue des vérifications d'artefacts et génère des visualisations diagnostiques.

**Fichier :** `src/data/validate_data/validate_concentration.py`  
**Lignes :** ~423  
**Rôle :** Validation qualité dataset Cognitive Load — figures diagnostiques

---

## Contexte technique Cognitive Load

| Paramètre | Valeur |
|-----------|--------|
| Matériel | OpenBCI Cyton 8 canaux |
| Canaux EEG | 8 |
| Fréquence | 200 Hz |
| Sujets | 15 |
| Format | .txt (25 colonnes) |
| Tâches | Arithmetic (arith), Stroop (stroop) |
| Niveaux | natural, lowlevel, midlevel, highlevel |
| Canal Fp2 | Index 1 dans l'array EEG (colonne 2 du .txt) |
| Échelle ADC | OPENBCI_SCALE = 0.02235 µV/LSB |

### Format des fichiers .txt
Chaque ligne contient 25 valeurs séparées par des virgules :
```
timestamp, eeg_ch1, eeg_ch2, ..., eeg_ch8, accel_x, accel_y, accel_z, ..., autres
```
- Colonne 0 : Timestamp (µs)
- Colonnes 1-8 : 8 canaux EEG en ADC counts (entiers)
- **Fp2 = colonne index 2 du fichier = indice 1 dans le sous-tableau EEG**

---

## Constantes

```python
OPENBCI_SCALE = 0.02235  # Facteur de conversion ADC → µV
FS = 200                  # Fréquence d'échantillonnage (Hz)
BAND_DEF = {
    'δ': (0.5, 4), 'θ': (4, 8), 'α': (8, 13), 'β': (13, 30), 'γ': (30, 40)
}
LEVELS = ['natural', 'lowlevel', 'midlevel', 'highlevel']
```

---

## Fonctions

### `validate_file_structure()`

Valide la structure de tous les fichiers .txt du dataset.

**Algorithme :**
```
Pour chaque répertoire subject_XX/ :
    Pour chaque fichier .txt (arithmetic/stroop × 4 niveaux) :
        Charger avec np.loadtxt()
        Vérifier N colonnes == 25
        Vérifier N lignes > 0
        Extraire canal Fp2 (colonne index 2)
        Convertir ADC → µV via OPENBCI_SCALE
        Vérifier amplitude dans [-500, 500] µV
```

**Retourne :** `dict` `{filepath: {'valid': bool, 'n_samples': int, 'error': str}}`

---

### `load_all_labels(task)`

Charge tous les signaux Fp2 pour une tâche donnée (arithmetic ou stroop).

**Paramètre :** `task` — 'arithmetic' ou 'stroop'

**Algorithme :**
```
signals_by_level = {level: [] for level in LEVELS}

Pour chaque sujet (1-15) :
    Pour chaque niveau (natural, lowlevel, midlevel, highlevel) :
        filepath = f"Sub_{subject:02d}/{task}_{level}.txt"
        signal = read_and_convert(filepath)
        signals_by_level[level].append(signal)
```

**Retourne :** `dict` `{level: [signal_sujet1, signal_sujet2, ...]}` (200 Hz, µV)

---

### `run_artifact_checks(signals, task_label)`

Vérifie la présence d'artefacts par niveau cognitif.

**Paramètres :**
- `signals` — dict `{level: [signaux 200 Hz]}` retourné par `load_all_labels()`
- `task_label` — 'arithmetic' ou 'stroop' (pour les titres)

**Vérifications par signal :**
1. `max|signal| < 500 µV` — Pas de saturation
2. `std(signal) > 0.5 µV` — Signal actif (pas de canal coupé)
3. `|mean(signal)| < 50 µV` — Pas de drift DC excessif
4. `kurtosis(signal) < 10` — Pas d'artefacts de mouvement extrêmes

**Affiche :** Tableau récapitulatif par niveau.

---

### `visualize_all(sig_arith, sig_stroop)`

Génère toutes les visualisations de validation.

**Paramètres :**
- `sig_arith` — dict de signaux tâche arithmetic
- `sig_stroop` — dict de signaux tâche stroop

**Délègue à :** `_plot_band_power()`, `_plot_cross_subject_psd()`

---

### `_plot_band_power(signals, task_name)`

Génère des boxplots des puissances de bandes par niveau cognitif.

**Paramètre :**
- `signals` — dict `{level: [signaux]}`
- `task_name` — Nom de la tâche (pour le titre)

**Layout :** 5 subplots (un par bande δ/θ/α/β/γ)
- Axe X : niveaux (natural, low, mid, high)
- Axe Y : puissance (µV²/Hz)

**Vérification attendue :** β et EI doivent augmenter avec le niveau cognitif ; θ et TBR doivent diminuer.

---

### `cross_subject_stats(task, n_subjects)`

Calcule les statistiques PSD inter-sujets pour une tâche.

**Paramètres :**
- `task` — 'arithmetic' ou 'stroop'
- `n_subjects` — Nombre de sujets à inclure (défaut : tous)

**Statistiques calculées :**
- PSD moyenne ± std par niveau
- Test de Wilcoxon natural vs highlevel (p < 0.05 attendu pour β)
- Variabilité coefficient de variation par bande

---

### `_plot_cross_subject_psd(task_dir, task_name, n_subjects)`

PSD croisée de tous les sujets pour une tâche.

**Layout :** 4 subplots (un par niveau)
- Chaque subplot : PSD de chaque sujet en gris + moyenne en couleur
- Axe X : fréquence (0-40 Hz)
- Axe Y : PSD (µV²/Hz) échelle logarithmique

---

### `main()`

Orchestre les validations pour les deux tâches.

```python
validate_file_structure()

sig_arith  = load_all_labels('arithmetic')
sig_stroop = load_all_labels('stroop')

run_artifact_checks(sig_arith,  'arithmetic')
run_artifact_checks(sig_stroop, 'stroop')

visualize_all(sig_arith, sig_stroop)

cross_subject_stats('arithmetic', n_subjects=15)
cross_subject_stats('stroop',     n_subjects=15)
```

---

## 4 Niveaux cognitifs

| Niveau | Code | Description | Score attendu |
|--------|------|-------------|---------------|
| `natural` | 0 | État de repos, pas de tâche | 0.0 - 2.5 |
| `lowlevel` | 1 | Tâche simple | 2.5 - 5.0 |
| `midlevel` | 2 | Tâche modérée | 5.0 - 7.5 |
| `highlevel` | 3 | Tâche difficile | 7.5 - 10.0 |

---

## Différences vs validate_stress.py

| Aspect | validate_stress.py | validate_concentration.py |
|--------|-------------------|--------------------------|
| Dataset | SAM40 (EMOTIV) | Cognitive Load (OpenBCI) |
| Format | .mat (MATLAB) | .txt (CSV) |
| Canaux | 32 | 8 |
| Fp2 extraction | 3 stratégies (nom/index31/fallback) | Index direct (colonne 2) |
| Fréquence | 128 Hz | 200 Hz |
| Sujets | 40 | 15 |
| Ground truth | scales.xls | Niveau tâche (4 niveaux) |
