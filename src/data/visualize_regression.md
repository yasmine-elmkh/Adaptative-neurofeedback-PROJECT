# visualize_regression.py — Documentation Détaillée

## Vue d'ensemble

`visualize_regression.py` génère 13+ figures diagnostiques pour les 4 étapes du pipeline de régression EEG. Chaque étape a son propre dossier de rapports sous `reports/Regression/`.

**Fichier :** `src/data/visualize_regression.py`  
**Lignes :** ~743  
**Prérequis :** `pipeline_regression.py` doit avoir été exécuté (génère `data/Regression/`)

---

## Structure des sorties

```
reports/Regression/
├── 01_preprocessing/
│   ├── 01_signal_amplitude.png      Distribution amplitude conc vs stress
│   ├── 02_score_distributions.png   Histogrammes y_conc et y_stress
│   ├── 03_sample_epochs.png         Exemples d'epochs (4 niveaux / 4 tâches)
│   └── 04_subjects_overview.png     Epochs par sujet
│
├── 02_split/
│   ├── 01_split_sizes.png           Train/Val/Test N epochs
│   ├── 02_score_in_splits.png       Distribution des scores par split
│   └── 03_subjects_per_split.png    Histogrammes détaillés par split
│
├── 03_augmentation/
│   ├── 01_dataset_growth.png        Taille du dataset par expérience A/B/C/D/FULL
│   ├── 02_score_propagation.png     Sanity check scores après augmentation
│   └── 03_signal_examples.png       Signal original vs augmenté
│
└── 04_features/
    ├── 01_feature_count.png         Répartition feat15 vs feat78 par catégorie
    ├── 02_top_correlations_conc.png  Top 20 features Spearman (concentration)
    ├── 02_top_correlations_stress.png Top 20 features Spearman (stress)
    ├── 03_feature_distributions_conc.png  Top 12 features (concentration)
    ├── 03_feature_distributions_stress.png Top 12 features (stress)
    └── 04_feat15_vs_feat78.png      Comparaison |r| feat15 vs feat78
```

---

## Palette de couleurs

```python
C_CONC   = "#2196F3"  # Bleu (concentration)
C_STRESS = "#F44336"  # Rouge (stress)
C_TRAIN  = "#4CAF50"  # Vert (train)
C_VAL    = "#FF9800"  # Orange (validation)
C_TEST   = "#9C27B0"  # Violet (test)
```

---

## Fonctions utilitaires

### `save(fig, folder, name)`

Sauvegarde une figure matplotlib à 150 DPI.

**Paramètres :**
- `fig` — Figure matplotlib
- `folder` — Répertoire de destination (Path)
- `name` — Nom de fichier (str)

---

### `npy_exists(*paths)`

Vérifie que tous les fichiers .npy listés existent.

**Retourne :** `bool`

---

### `_get_feature_names(n_feats)`

Retourne les noms des features (import dynamique de `feature_eng.get_feature_names()`).

**Fallback :** `['feat_00', 'feat_01', ...]` si import échoue.

---

## `viz_preprocessing()`

**Génère 4 figures dans `01_preprocessing/`**

**Figure 01 — Distribution d'amplitude :**
- Histogramme des amplitudes (z-score) pour X_conc et X_stress
- Affiche μ et σ, plage [-6, 6] z-score
- Vérification : les signaux doivent être centrés en 0 après normalisation

**Figure 02 — Distribution des scores :**
- Histogramme des y_conc et y_stress (scores 0-10)
- Ligne verticale : moyenne
- Quantiles Q25/Q50/Q75

**Figure 03 — Exemples d'epochs :**
- 2×4 subplots : Concentration (4 niveaux) + Stress (4 tâches)
- Concentration : natural/lowlevel/midlevel/highlevel (coloré par niveau)
- Stress : Relax/Arithmetic/Mirror/Stroop (coloré par tâche)

**Figure 04 — Epochs par sujet :**
- Barres : nombre d'epochs par sujet
- Axe Y secondaire : score moyen par sujet (points bleu marine)
- Permet d'identifier les sujets avec peu d'epochs (rejet d'artefacts)

---

## `viz_split()`

**Génère 3 figures dans `02_split/`**

**Figure 01 — Taille des splits :**
- Barres train(70%)/val(15%)/test(15%) pour concentration et stress
- Affiche N et % pour chaque split

**Figure 02 — Scores dans chaque split :**
- Boxplots des scores pour train/val/test
- Vérification : distributions similaires = split équilibré

**Figure 03 — Histogrammes détaillés :**
- Grille 2×3 : (concentration/stress) × (train/val/test)
- N + μ par panneau

---

## `viz_augmentation()`

**Génère 3 figures dans `03_augmentation/`**

**Figure 01 — Croissance du dataset :**
- Barres : N epochs train pour A/B/C/D/FULL
- Ligne horizontale : baseline A
- Ratio de multiplication : B×2, C×3, D×2, FULL×4

**Figure 02 — Propagation des scores :**
- Boxplots des y_train pour A/B/C/D/FULL
- Vérification : distributions identiques = scores bien propagés (np.tile)

**Figure 03 — Exemples de signaux augmentés :**
- 2×5 subplots (conc/stress) × (A/B/C/D/FULL)
- Orange = différence vs signal original (Δ moyen affiché)

---

## `viz_features()`

**Génère 6 figures dans `04_features/`**

**Chargement :** feat78 et feat15 depuis `Features/{conc,stress}/feat*_train_A.npy`
- Si feat15 manquant : calcul à la volée via `get_feature_vector()`

**Figure 01 — Comparaison feat count :**
- Barres horizontales par catégorie feat78
- Lignes verticales : feat15=15, feat78=78

**Catégories feat78 :**
| Catégorie | N features |
|-----------|-----------|
| PSD Welch | 5 |
| Ratios cognitifs | 5 |
| Hjorth + temporel | 6 |
| DWT sous-bandes | 20 |
| Textural | 16 |
| Non-linéaires | 5 |
| Transitions | 6 |

**Figure 02 — Top corrélations Spearman :**
- Top 20 features les plus corrélées au score (|ρ| Spearman)
- Couleur : bleu = corrélation positive, orange = négative
- Généré pour conc et stress séparément

**Figure 03 — Distributions des features :**
- 3×4 subplots pour les 12 meilleures features
- Histogrammes par tertile de score (bas/moyen/haut)
- Affiche r Spearman en titre

**Figure 04 — feat15 vs feat78 :**
- Boxplots de |r| Spearman pour feat15 et feat78
- Montre le gain moyen en pouvoir prédictif de feat78 vs feat15

---

## `main()`

Point d'entrée — orchestre les 4 sections de visualisation.

```python
# Vérification données existantes
if not (PREP / "X_conc.npy").exists():
    print("Exécutez d'abord pipeline_regression.py")
    return

viz_preprocessing()   # 01_preprocessing/ → 4 figures
viz_split()           # 02_split/ → 3 figures
viz_augmentation()    # 03_augmentation/ → 3 figures
viz_features()        # 04_features/ → 6 figures (conc + stress)
```

**Sortie totale :** 13-16 figures PNG (selon disponibilité des données)

---

## Utilisation

```bash
python src/data/visualize_regression.py
```

**Ordre d'exécution recommandé :**
1. `python src/data/pipeline_regression.py`  — génère les données
2. `python src/data/visualize_regression.py` — génère les visualisations
