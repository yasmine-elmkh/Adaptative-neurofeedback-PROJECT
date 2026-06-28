# validate_stress.py — Documentation Détaillée

## Vue d'ensemble

`validate_stress.py` est un script de validation de Phase 1 pour le dataset SAM40 Stress. Il analyse la qualité du signal EEG sur le canal Fp2 (index 31 dans le layout EMOTIV 32 canaux), visualise les données brutes et rééchantillonnées, et génère 10 figures de diagnostic.

**Fichier :** `src/data/validate_data/validate_stress.py`  
**Lignes :** ~539  
**Rôle :** Validation qualité dataset SAM40 Stress — 10 figures PNG

---

## Contexte technique SAM40

| Paramètre | Valeur |
|-----------|--------|
| Matériel | EMOTIV EPOC+ |
| Canaux | 32 |
| Fréquence | 128 Hz |
| Sujets | 40 |
| Format | .mat (MATLAB) |
| Tâches | Arithmetic, Mirror, Stroop, Relax |
| Canal Fp2 | Index 31 (dernier canal) dans layout EMOTIV |

### Layout EMOTIV 32 canaux
L'ordre des canaux EMOTIV est : AF3, F7, F3, FC5, T7, P7, O1, O2, P8, T8, FC6, F4, F8, AF4, ...Fp2 (index 31).

---

## Fonctions

### `explore_mat_structure(filepath)`

Explore la structure interne d'un fichier .mat pour identifier les clés EEG.

**Paramètre :** `filepath` — chemin vers un fichier .mat SAM40

**Algorithme :**
```python
mat = scipy.io.loadmat(filepath)
for key, value in mat.items():
    if not key.startswith('__'):
        print(f"{key}: shape={value.shape}, dtype={value.dtype}")
```

**Utilité :** Identifier les noms des variables dans le .mat (varient selon les versions SAM40).

---

### `validate_files()`

Valide l'intégrité de tous les fichiers .mat du dataset.

**Algorithme :**
```
Pour chaque .mat dans data/SAM40_Stress_dataset/ :
    Essayer de charger avec scipy.io.loadmat()
    Vérifier shape EEG : (32, N_samples) attendu
    Vérifier N_samples > 0
    Vérifier pas de NaN/Inf dans les données brutes
    
Retourner : résumé (nb valides, nb invalides, shapes observées)
```

**Retourne :** `dict` `{filename: {'valid': bool, 'shape': tuple, 'error': str}}`

---

### `extract_fp2(eeg, ch_names, task_name)`

Extrait le canal Fp2 avec une stratégie en 3 niveaux.

**Paramètres :**
- `eeg` — Matrice EEG (32 × N_samples)
- `ch_names` — Liste des noms de canaux (peut être None)
- `task_name` — Nom de la tâche (pour les logs)

**Stratégie d'extraction (3 niveaux) :**

**Niveau 1 — Recherche par nom :**
```python
if ch_names is not None:
    for i, ch in enumerate(ch_names):
        if 'fp2' in ch.lower() or 'fp2' in ch.lower():
            return eeg[i, :]
```

**Niveau 2 — Index fixe EMOTIV :**
```python
if eeg.shape[0] >= 32:
    return eeg[31, :]  # Fp2 = index 31 dans layout EMOTIV standard
```

**Niveau 3 — Fallback canal 0 :**
```python
return eeg[0, :]  # Canal AF3 si Fp2 non trouvable
```

**Retourne :** `numpy.ndarray` 1D — signal Fp2 (N_samples,)

---

### `extract_all_fp2(file_results)`

Extrait Fp2 pour tous les fichiers validés du dataset.

**Paramètre :** `file_results` — dict retourné par `validate_files()`

**Retourne :** `dict` `{filename: fp2_signal_128hz}`

---

### `load_and_display_scales()`

Charge et affiche les statistiques des échelles de stress (scales.xls).

**Algorithme :**
```python
df_scales = pd.read_excel('data/SAM40_Stress_dataset/scales.xls')
print(df_scales.describe())
print("Distribution par tâche:")
print(df_scales.groupby('Task')['Stress_Score'].agg(['mean', 'std', 'min', 'max']))
```

---

### `run_artifact_checks(fp2_signals)`

Vérifie la présence d'artefacts dans les signaux Fp2.

**Paramètre :** `fp2_signals` — dict `{filename: signal_128hz}`

**Vérifications :**
1. **Amplitude :** Max|signal| < 500 µV (seuil NeuroCap)
2. **Signal plat :** std(signal) > 1 µV (signal non saturé)
3. **Drift DC :** |mean(signal)| < 100 µV
4. **Clips :** Pas de valeurs à ±511 µV (clip ADC 12-bit)

**Affiche :** % de signaux passant chaque vérification.

---

### `resample_all(fp2_signals)`

Rééchantillonne tous les signaux de 128 Hz vers 250 Hz.

**Paramètre :** `fp2_signals` — dict `{filename: signal_128hz}`

**Méthode :** `scipy.signal.resample_poly(signal, up=125, down=64)`

**Retourne :** `dict` `{filename: signal_250hz}`

---

### `visualize_all(file_results, fp2_signals, fp2_250)`

Génère les 10 figures de validation.

**Paramètres :**
- `file_results` — Résultats de validation fichiers
- `fp2_signals` — Signaux 128 Hz
- `fp2_250` — Signaux 250 Hz

**Délègue à :** `_plot_resample_check()`, `_plot_band_power()`, `_plot_cross_subject_psd()`

---

### `cross_subject_stats(n_subjects)`

Calcule les statistiques inter-sujets (PSD, amplitude, puissances de bandes).

**Paramètre :** `n_subjects` — Nombre de sujets à analyser

**Statistiques :**
- PSD moyenne ± std par tâche (arithmetic/mirror/stroop/relax)
- Puissance par bande (δ/θ/α/β/γ) par sujet
- Corrélation avec les scores scales.xls

---

### `_plot_resample_check(ts_128, ts_250)`

**Figure 1 :** Compare le signal avant et après rééchantillonnage.

**Layout :** 3 panneaux
- Signal 128 Hz (original)
- Signal 250 Hz (rééchantillonné)
- PSD comparative 128 Hz vs 250 Hz

**Vérification :** Les PSD doivent être identiques jusqu'à 40 Hz (bande d'intérêt).

---

### `_plot_band_power(signals, fs, suffix)`

**Figure :** Puissances de bandes EEG par tâche.

**Paramètres :**
- `signals` — dict de signaux
- `fs` — Fréquence d'échantillonnage (128 ou 250)
- `suffix` — '_128hz' ou '_250hz' pour le nom de fichier

**Calcule :** Welch PSD → intégration par bande → boxplot par tâche.

---

### `_plot_cross_subject_psd(n_subjects)`

**Figure :** PSD croisée entre sujets (variabilité inter-sujets).

**Layout :** 1 subplot avec PSD de chaque sujet superposée + moyenne en gras.

---

### `main()`

Point d'entrée — orchestre les 10 analyses.

```python
file_results = validate_files()
fp2_signals  = extract_all_fp2(file_results)

load_and_display_scales()
run_artifact_checks(fp2_signals)
fp2_250 = resample_all(fp2_signals)

visualize_all(file_results, fp2_signals, fp2_250)
cross_subject_stats(n_subjects=5)
```

**Sortie :** 10 PNG dans `outputs_stress_fp2/`

---

## Figures générées (10 PNG)

| N° | Fichier | Description |
|----|---------|-------------|
| 01 | `signal_overview.png` | Signaux Fp2 bruts pour 3 sujets × 4 tâches |
| 02 | `resample_check.png` | Comparaison 128 Hz vs 250 Hz |
| 03 | `band_power_128.png` | Puissances bandes @ 128 Hz par tâche |
| 04 | `band_power_250.png` | Puissances bandes @ 250 Hz par tâche |
| 05 | `artifact_distribution.png` | Distribution des amplitudes max |
| 06 | `psd_by_task.png` | PSD comparée par tâche (relax vs stress) |
| 07 | `cross_subject_psd.png` | PSD de chaque sujet superposée |
| 08 | `scales_distribution.png` | Distribution des scores scales.xls |
| 09 | `electrode_layout.png` | Position Fp2 sur le crâne (EMOTIV layout) |
| 10 | `validation_summary.png` | Tableau récapitulatif qualité |
