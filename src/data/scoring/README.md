# NeuroCap — Module Scoring (`src/data/scoring/`)

Attribution d'un score continu 0–10 à chaque epoch EEG des deux datasets.  
**Première étape obligatoire du pipeline de régression.**

---

## Pourquoi ce module existe

Les datasets bruts ne contiennent pas de scores numériques continus :

| Dataset | Ce qui existe | Ce qui manque |
|---------|--------------|--------------|
| CLA — Concentration (OpenBCI) | 4 niveaux dans les noms de fichiers (`natural`, `lowlevel`, `midlevel`, `highlevel`) | Score continu 0–10 par epoch |
| SAM40 — Stress (Emotiv) | Notes 1–10 auto-rapportées dans `scales.xls` | Mapping précis vers les epochs individuelles |

---

## Fichiers

```
src/data/scoring/
├── concentration_scoring.py   conc_score (0-10) depuis niveaux CLA
├── stress_scoring.py          stress_score (0-10) depuis scales.xls SAM40
├── merge_scoring.py           Reconstruit signaux EEG + attache les scores → .npy
├── visualize_scoring.py       7 figures dans reports/scoring/merge/
└── README.md                  Ce fichier
```

---

## Ordre d'exécution

```bash
python src/data/scoring/concentration_scoring.py
python src/data/scoring/stress_scoring.py
python src/data/scoring/merge_scoring.py       # optionnel (utilisé par pipeline_regression.py)
python src/data/scoring/visualize_scoring.py   # optionnel — 7 figures de validation
```

---

## `concentration_scoring.py`

**Entrée :** fichiers `.txt` dans `data/Dataset/Cognitive Load Assessment Concentration/raw_data/`

**Logique :** le niveau de la tâche (natural / lowlevel / midlevel / highlevel) définit l'intervalle du score.  
À l'intérieur de chaque intervalle, le score exact est pondéré par 4 biomarqueurs EEG :

| Niveau | Intervalle conc_score | Description |
|--------|-----------------------|-------------|
| natural | [0.0 – 2.5] | Repos, aucune tâche cognitive |
| lowlevel | [2.5 – 5.0] | Calcul mental simple |
| midlevel | [5.0 – 7.5] | Calcul mental modéré |
| highlevel | [7.5 – 10.0] | Calcul mental intense |

**Biomarqueurs de pondération (validés par corrélation de Spearman sur 1 859 epochs) :**

| Feature | Formule | Corrélation Spearman | Poids |
|---------|---------|---------------------|-------|
| Focus | EI × ZCR | r = +0.1998 *** | 31% |
| EI | β/(α+θ) | r = +0.1757 *** | 28% |
| ZCR | zero-crossing rate | r = +0.1510 *** | 24% |
| TBR_inv | β/θ | r = +0.1104 *** | 17% |

**Sortie :** `data/Scoring/scored_concentration.csv`
```
Colonnes : file | epoch_idx | task | level | subject | conc_score | EI | TBR_inv | ZCR | Focus
Lignes   : ~1 859 epochs (15 sujets × ~124 epochs/sujet)
```

**Visualisations :** `reports/scoring/concentration/` (histogramme par niveau, scatter EI vs score, corrélations)

---

## `stress_scoring.py`

**Entrées :**
- Fichiers `.mat` dans `data/Dataset/Stress_dataset/raw_data/`
- `data/Dataset/Stress_dataset/scales.xls` (notes auto-rapportées 1–10)

**Logique :**
- Les scores `scales.xls` sont la **vérité terrain** (ground truth humain, immédiatement après la tâche)
- Mapping linéaire : `stress_score = (scales_score − 1) / 9 × 10` (1→0, 10→10)
- Pour les tâches `Relax` absentes de `scales.xls` : estimation par biomarqueurs EEG (θ/β bas) → 0.5–2.0

**Distribution des scores par tâche :**

| Type de tâche | Sujets | Score stress (moy. ± std) |
|--------------|--------|--------------------------|
| Relaxation   | 40     | 1.8 ± 0.7 |
| Arithmétique | 40     | 5.4 ± 1.2 |
| Stress social | 40    | 6.9 ± 1.4 |
| Stroop       | 40     | 7.6 ± 1.5 |
| **Total**    | **40** | **4.9 ± 2.3** |

**Sortie :** `data/Scoring/scored_stress.csv`
```
Colonnes : file | epoch_idx | task | subject | trial | stress_score | scales_score
Lignes   : ~2 879 epochs (40 sujets × ~72 epochs/sujet)
```

**Visualisations :** `reports/scoring/stress/`

---

## `merge_scoring.py`

Relit les signaux bruts, applique le resampling + z-score, attache les scores depuis les CSV.

**Sortie :** `data/Scoring/merged/`
```
X_concentration.npy        (N_conc, 1000)   signal EEG concentration @250 Hz, normalisé
y_conc_score.npy           (N_conc,)        scores 0–10
subjects_concentration.npy (N_conc,)        IDs sujets (0–14)
levels_concentration.npy   (N_conc,)        niveaux 0-3

X_stress.npy               (N_stress, 1000)
y_stress_score.npy         (N_stress,)
subjects_stress.npy        (N_stress,)      IDs sujets (15–54)
```

---

## `visualize_scoring.py`

**Sortie :** `reports/scoring/merge/` — 7 figures de validation du scoring

| Fichier | Contenu |
|---------|---------|
| `01_score_distributions.png` | Histogrammes concentration + stress côte à côte |
| `02_conc_by_level.png` | Boxplot concentration par niveau (natural → highlevel) |
| `03_stress_by_task.png` | Boxplot stress par type de tâche (Relax / Arithmétique / Stroop) |
| `04_conc_by_subject.png` | Score moyen ± std par sujet (15 sujets OpenBCI) |
| `05_stress_by_subject.png` | Score moyen ± std par sujet (40 sujets Emotiv) |
| `06_epochs_count.png` | Nombre d'epochs par niveau / tâche |
| `07_dataset_overview.png` | Vue d'ensemble comparative des deux datasets |

---

## Règles importantes

### Ce qu'on fait
- **2 modèles séparés** : un modèle sur CLA (conc_score), un modèle sur SAM40 (stress_score)
- Les deux datasets restent **indépendants** — pipelines d'entraînement séparés

### Ce qu'on ne fait PAS
- Ne pas utiliser les epochs CLA pour le modèle stress (matériel différent : OpenBCI vs Emotiv)
- Ne pas fusionner les deux datasets (AF3 Emotiv ≠ Fp2 NeuroCap — électrodes différentes)
- Ne pas appliquer le scoring d'un dataset à l'autre

---

## Sorties complètes

```
data/Scoring/
├── scored_concentration.csv   ~1 859 epochs avec conc_score (15 sujets CLA)
├── scored_stress.csv          ~2 879 epochs avec stress_score (40 sujets SAM40)
└── merged/
    ├── X_concentration.npy          (N_conc, 1000)
    ├── y_conc_score.npy             (N_conc,)
    ├── subjects_concentration.npy   (N_conc,)
    ├── levels_concentration.npy     (N_conc,)
    ├── X_stress.npy                 (N_stress, 1000)
    ├── y_stress_score.npy           (N_stress,)
    └── subjects_stress.npy          (N_stress,)

reports/scoring/
├── concentration/    plots produits par concentration_scoring.py
├── stress/           plots produits par stress_scoring.py
└── merge/            7 figures de validation globale
```
