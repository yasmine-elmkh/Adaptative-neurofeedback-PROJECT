# metrics_professional.py — Documentation Détaillée

## Vue d'ensemble

`metrics_professional.py` implémente un système de métriques en 5 niveaux de sophistication pour l'évaluation clinique des modèles EEG. Il est partagé par tous les pipelines ML, DL et TL du projet NeuroCap.

**Fichier :** `src/models/metrics_professional.py`  
**Lignes :** ~1572  
**Rôle :** Évaluation professionnelle unifiée — 5 niveaux, plots diagnostiques

---

## Constantes

```python
THRESHOLD_DEFAULT = 5.0   # Seuil binarisation Low/High
N_BOOTSTRAP       = 500   # Itérations Bootstrap CI
N_PERMUTATIONS    = 500   # Tests de permutation
CONF_K_SIGMOID    = 1.5   # Courbure sigmoïde confiance
```

---

## Architecture en 5 niveaux

```
Niveau 1 — Métriques de base           compute_full_metrics()
Niveau 2 — Statistiques d'inférence    bootstrap_ci(), permutation_test()
Niveau 3 — Analyse clinique avancée    calibration_analysis(), bland_altman_analysis(), icc()
Niveau 4 — Stabilité et biais          stability_analysis(), per_subject_metrics()
Niveau 5 — Clinique décision           decision_curve_analysis(), delong_auc_ci()
```

---

## NIVEAU 1 — Métriques de base

### `compute_full_metrics(y_true, y_pred_continuous, threshold=5.0)`

Calcule 20+ métriques à partir des scores continus et binaires.

**Paramètres :**
- `y_true` — Scores réels (N,) float [0-10]
- `y_pred_continuous` — Scores prédits (N,) float [0-10]
- `threshold` — Seuil binarisation (défaut 5.0)

**Binarisation :**
```python
y_true_bin = (y_true >= threshold).astype(int)   # 0=Low, 1=High
y_pred_bin = (y_pred_continuous >= threshold).astype(int)
```

**Métriques retournées :**

| Métrique | Description |
|----------|-------------|
| `MAE` | Mean Absolute Error |
| `RMSE` | Root Mean Square Error |
| `R2` | Coefficient de détermination |
| `Pearson_r` | Corrélation de Pearson |
| `Spearman_r` | Corrélation de Spearman |
| `AUC` | Area Under ROC Curve |
| `Accuracy` | Précision de classification binarisée |
| `Sensitivity` | Rappel classe High |
| `Specificity` | Rappel classe Low |
| `F1` | F1-score |
| `MCC` | Matthews Correlation Coefficient |
| `PPV` | Positive Predictive Value |
| `NPV` | Negative Predictive Value |
| `Balanced_Accuracy` | (Sensitivity + Specificity) / 2 |
| `N` | Nombre d'échantillons |
| `N_high` | Nombre d'échantillons High |
| `N_low` | Nombre d'échantillons Low |

**Retourne :** `dict` avec toutes les métriques

---

## NIVEAU 2 — Statistiques d'inférence

### `bootstrap_ci(y_true, y_pred, metric_fn, n_boot=500, alpha=0.05)`

Calcule l'intervalle de confiance Bootstrap pour une métrique.

**Paramètres :**
- `y_true`, `y_pred` — Arrays de scores
- `metric_fn` — Fonction `f(y_true, y_pred) → float`
- `n_boot` — Nombre d'itérations
- `alpha` — Niveau de significativité

**Algorithme :**
```python
scores = []
for _ in range(n_boot):
    idx = np.random.choice(len(y_true), len(y_true), replace=True)
    scores.append(metric_fn(y_true[idx], y_pred[idx]))
ci_low  = np.percentile(scores, 100 * alpha / 2)
ci_high = np.percentile(scores, 100 * (1 - alpha / 2))
```

**Retourne :** `(mean, ci_low, ci_high)`

---

### `permutation_test(y_true, y_pred, metric_fn, n_perm=500)`

Test de permutation pour vérifier que le modèle est meilleur que le hasard.

**Algorithme :**
```python
obs = metric_fn(y_true, y_pred)
perms = [metric_fn(np.random.permutation(y_true), y_pred) for _ in range(n_perm)]
p_value = np.mean(np.array(perms) >= obs)
```

**Retourne :** `(observed_metric, p_value)`

---

### `wilcoxon_pairwise(y_true_a, y_pred_a, y_true_b, y_pred_b, metric)`

Test de Wilcoxon non-paramétrique entre deux modèles.

**Retourne :** `(statistic, p_value)` (scipy.stats.wilcoxon)

---

### `run_wilcoxon_all_pairs(results_dict, metric='MAE')`

Matrice de comparaisons Wilcoxon pour tous les modèles.

**Paramètre :** `results_dict` — `{model_name: (y_true, y_pred)}`

**Retourne :** DataFrame N×N de p-values

---

### `run_friedman_test(results_dict, metric='AUC')`

Test de Friedman pour comparer K modèles sur les mêmes données.

**Retourne :** `(statistic, p_value)` (scipy.stats.friedmanchisquare)

---

## NIVEAU 3 — Analyse clinique avancée

### `calibration_analysis(y_true, y_pred, n_bins=10)`

Analyse la calibration : est-ce que les scores prédits sont fiables ?

**Algorithme :** Reliability diagram — score prédit binné vs proportion réelle.

**Métriques :**
- **ECE** (Expected Calibration Error) = Σ (|proportion_obs - score_moy_bin| × N_bin / N_total)
- **MCE** (Maximum Calibration Error) = max(|proportion_obs - score_moy_bin|)

**Retourne :** `{'ECE': float, 'MCE': float, 'bins': [...], 'proportions': [...]}`

---

### `bland_altman_analysis(y_true, y_pred)`

Analyse de Bland-Altman pour mesurer l'accord entre méthode de référence et prédiction.

**Algorithme :**
```python
diff  = y_pred - y_true       # Différence
mean  = (y_pred + y_true) / 2 # Moyenne
bias  = diff.mean()           # Biais moyen
loa   = 1.96 * diff.std()     # Limites d'accord (95%)
```

**Retourne :** `{'bias': float, 'loa_upper': float, 'loa_lower': float, 'diff': array, 'mean': array}`

---

### `icc(y_true, y_pred, model='twoway', type_='agreement')`

Calcule l'ICC (Intraclass Correlation Coefficient) version ICC(2,1).

**Algorithme :** ANOVA two-way → MS entre sujets, MS résiduelle → ICC.

**Interprétation :**
- ICC < 0.50 : accord pauvre
- 0.50 ≤ ICC < 0.75 : accord modéré
- 0.75 ≤ ICC < 0.90 : accord bon
- ICC ≥ 0.90 : accord excellent

**Retourne :** `float` — valeur ICC [0-1]

---

### `conformal_intervals(y_true_cal, y_pred_cal, y_pred_test, alpha=0.1)`

Intervalles de prédiction conformaux (sans hypothèse de distribution).

**Algorithme :**
```python
residuals = np.abs(y_true_cal - y_pred_cal)
q = np.quantile(residuals, 1 - alpha)         # Quantile 90%
lower = y_pred_test - q
upper = y_pred_test + q
```

**Retourne :** `(lower_bounds, upper_bounds)` — Intervalles garantis à (1-α)×100%

---

### `ensemble_uncertainty(predictions_list)`

Estime l'incertitude à partir d'un ensemble de prédictions.

**Paramètre :** `predictions_list` — Liste de N arrays (K modèles)

**Retourne :** `(mean_pred, std_pred)` — Moyenne et écart-type des prédictions

---

### `confidence_score(score_continuous, threshold=5.0, k=1.5)`

Calcule un score de confiance sigmoïde centré sur le seuil.

```python
margin     = abs(score_continuous - threshold)
confidence = 1 / (1 + exp(-k * margin))
```

**Retourne :** `float` [0.5-1.0] — 0.5 = proche du seuil (incertain), 1.0 = très éloigné

---

## NIVEAU 4 — Stabilité et biais

### `stability_analysis(model_fn, X, y, n_runs=10)`

Évalue la variabilité des prédictions sur plusieurs exécutions.

**Métriques :** std(AUC), std(MAE), std(R²) sur n_runs ré-entraînements.

---

### `bias_variance_decomposition(y_true, predictions_matrix)`

Décompose l'erreur en biais, variance et bruit.

**Paramètre :** `predictions_matrix` — (N_runs, N_samples) — prédictions de K runs

---

### `per_subject_metrics(y_true, y_pred, subject_ids)`

Calcule les métriques individuellement par sujet.

**Retourne :** `dict` `{subject_id: {MAE, AUC, R2, ...}}`

---

### `learning_curve_loso(X, y, subject_ids, model_fn)`

Courbe d'apprentissage LOSO : performance vs nombre de sujets d'entraînement.

---

## NIVEAU 5 — Décision clinique

### `decision_curve_analysis(y_true_bin, y_pred_prob, thresholds)`

DCA : Net Benefit = Sensitivity − (1-Specificity) × (pt/(1-pt))

Évalue l'utilité clinique à différents seuils de probabilité.

**Retourne :** DataFrame avec colonnes `threshold`, `net_benefit_model`, `net_benefit_treat_all`

---

### `delong_auc_ci(y_true, y_pred, alpha=0.05)`

Calcule l'IC de l'AUC selon la méthode de DeLong (1988) — plus précise que Bootstrap.

**Retourne :** `(auc, ci_low, ci_high)`

---

### `generate_professional_report(y_true, y_pred, subject_ids, model_name, out_dir)`

Génère un rapport complet en JSON + figures pour un modèle.

**Actions :**
1. `compute_full_metrics()` → métriques de base
2. `bootstrap_ci()` pour AUC, MAE, R²
3. `permutation_test()` pour AUC
4. `icc()`, `bland_altman_analysis()`, `calibration_analysis()`
5. `per_subject_metrics()`
6. `decision_curve_analysis()`
7. Sauvegarde `metrics.json` + figures

---

## Fonctions de visualisation

| Fonction | Figure générée |
|----------|---------------|
| `plot_reliability_diagram(...)` | Calibration : prédit vs observé par bin |
| `plot_bland_altman(...)` | Bland-Altman : différence vs moyenne |
| `plot_bootstrap_ci_bars(...)` | Barres avec IC 95% Bootstrap |
| `plot_full_confusion_matrix(...)` | Matrice de confusion normalisée |
| `plot_wilcoxon_heatmap(...)` | Heatmap des p-values inter-modèles |
| `plot_per_subject_heatmap(...)` | Heatmap métriques par sujet |
| `plot_decision_curve(...)` | Courbe DCA (Net Benefit) |

---

## Utilisation standard

```python
from src.models.metrics_professional import (
    compute_full_metrics,
    bootstrap_ci,
    generate_professional_report
)

# Métriques de base
metrics = compute_full_metrics(y_true, y_pred, threshold=5.0)

# IC Bootstrap sur AUC
from sklearn.metrics import roc_auc_score
auc_mean, auc_low, auc_high = bootstrap_ci(
    y_true, y_pred,
    metric_fn=lambda yt, yp: roc_auc_score(yt >= 5.0, yp),
    n_boot=500
)

# Rapport complet
generate_professional_report(y_true, y_pred, sids, 'EEGNet_TL3', out_dir='reports/...')
```
