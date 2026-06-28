# compare_all_models.py — Documentation Détaillée

## Vue d'ensemble

`compare_all_models.py` est le script de comparaison finale qui agrège les résultats de TOUS les modèles (ML baseline + DL + TL) et génère une recommandation de déploiement basée sur 7 critères cliniques.

**Fichier :** `src/models/compare/compare_all_models.py`  
**Rôle :** Comparaison globale ML+DL+TL — recommandation finale  
**Sorties :** `reports/Regression/Final_Comparison/`

---

## Familles de modèles comparées

| Famille | Configurations | Source |
|---------|---------------|--------|
| ML feat15 | SVR/RF/XGB/LGBM × 5 exp | `reports/Regression/Baseline/feat15/` |
| ML feat15+SMOTE | SVR/RF/XGB/LGBM × 4 techniques × 5 exp | `reports/Regression/Baseline/feat15_smote/` |
| ML feat78 | SVR/RF/XGB/LGBM × 5 exp | `reports/Regression/Baseline/feat78/` |
| ML feat78+SMOTE | SVR/RF/XGB/LGBM × 4 techniques × 5 exp | `reports/Regression/Baseline/feat78_smote/` |
| DL | 19 architectures × 5 exp | `reports/Regression/DL/` |
| TL-1 | EEGNet FullFT × 5 exp | `reports/Regression/TL/EEGNet_FullFT/` |
| TL-2 | EEGNet FeatureExtr × 5 exp | `reports/Regression/TL/EEGNet_FeatureExtraction/` |
| TL-3 | EEGNet LayerRepl × 5 exp | `reports/Regression/TL/EEGNet_LayerReplacement/` |

---

## 7 Critères cliniques d'évaluation

| N° | Critère | Seuil pass | Seuil borderline | Poids |
|----|---------|------------|-----------------|-------|
| C1 | AUC | ≥ 0.80 | ≥ 0.70 | 25% |
| C2 | R² | ≥ 0.50 | ≥ 0.35 | 20% |
| C3 | MAE | ≤ 1.5 | ≤ 2.0 | 15% |
| C4 | Sensitivity | ≥ 0.75 | ≥ 0.60 | 15% |
| C5 | Specificity | ≥ 0.75 | ≥ 0.60 | 10% |
| C6 | ICC(2,1) | ≥ 0.60 | ≥ 0.40 | 10% |
| C7 | ECE | ≤ 0.10 | ≤ 0.20 | 5% |

---

## Fonctions

### `load_all_results()`

Charge tous les metrics.json de toutes les familles.

**Retourne :** `dict` `{family: {model_id: {target: {exp: {metric: value}}}}}`

---

### `build_global_df(all_results)`

Construit un DataFrame global avec toutes les combinaisons.

**Colonnes :** `['family', 'model_id', 'target', 'exp', 'AUC', 'R2', 'MAE', 'F1', 'MCC', 'Sensitivity', 'Specificity', 'ICC', 'ECE', 'score_composite']`

---

### `score_clinical_criteria(row)`

Évalue les 7 critères pour une ligne du DataFrame.

```python
def score_clinical_criteria(row):
    score = 0
    scores_detail = {}
    
    criteria = [
        ('AUC',         0.80, 0.70, 0.25),
        ('R2',          0.50, 0.35, 0.20),
        ('MAE',         1.50, 2.00, 0.15, inverse=True),  # inverse: lower is better
        ('Sensitivity', 0.75, 0.60, 0.15),
        ('Specificity', 0.75, 0.60, 0.10),
        ('ICC',         0.60, 0.40, 0.10),
        ('ECE',         0.10, 0.20, 0.05, inverse=True),
    ]
    
    for crit in criteria:
        name, thr_pass, thr_border, weight = crit[:4]
        inv = len(crit) > 4 and crit[4]
        val = row[name]
        
        if inv:
            status = 'pass' if val <= thr_pass else 'borderline' if val <= thr_border else 'fail'
        else:
            status = 'pass' if val >= thr_pass else 'borderline' if val >= thr_border else 'fail'
        
        pts = weight * (1.0 if status == 'pass' else 0.5 if status == 'borderline' else 0.0)
        score += pts
        scores_detail[name] = {'status': status, 'value': val, 'points': pts}
    
    return score, scores_detail
```

**Score composite :** de 0 à 1 (somme pondérée des critères passés)

---

### `plot_global_ranking(df, target)`

Barres horizontales triées par score composite pour tous les modèles.

**Couleurs :**
- Vert : score > 0.75 (excellent)
- Orange : 0.50 ≤ score ≤ 0.75 (bon)
- Rouge : score < 0.50 (insuffisant)

---

### `plot_criteria_heatmap(df, target)`

Heatmap (modèles × 7 critères) colorée par statut pass/borderline/fail.

---

### `plot_family_comparison(df, target, metric)`

Boxplots d'une métrique par famille de modèles.

**Axe X :** Familles (ML_feat15, ML_feat78, DL_CNN, DL_RNN, TL_TL3, ...)

---

### `plot_pareto_frontier(df, target)`

Scatter plot AUC vs MAE avec frontière de Pareto.

**Frontière de Pareto :** Ensemble des modèles non dominés (pas de modèle meilleur sur les deux axes simultanément).

---

### `generate_deployment_recommendation(df, target)`

Génère la recommandation de déploiement finale.

```python
# Sélectionner le meilleur modèle par cible
best = df[df['target'] == target].nlargest(1, 'score_composite').iloc[0]

criteria_met = sum(1 for c in ['C1','C2','C3','C4','C5','C6','C7']
                   if best[c] == 'pass')

if criteria_met >= 6:
    recommendation = "DÉPLOIEMENT RECOMMANDÉ"
elif criteria_met >= 4:
    recommendation = "DÉPLOIEMENT CONDITIONNEL (surveillance recommandée)"
else:
    recommendation = "DÉPLOIEMENT NON RECOMMANDÉ — amélioration nécessaire"

return {
    'best_model': best['model_id'],
    'family': best['family'],
    'score': best['score_composite'],
    'criteria_met': criteria_met,
    'recommendation': recommendation
}
```

---

### `main()`

```python
all_results = load_all_results()
df = build_global_df(all_results)

for target in ['conc', 'stress']:
    plot_global_ranking(df, target)
    plot_criteria_heatmap(df, target)
    plot_family_comparison(df, target, 'AUC')
    plot_family_comparison(df, target, 'R2')
    plot_pareto_frontier(df, target)
    
    rec = generate_deployment_recommendation(df, target)
    print(f"\n=== RECOMMANDATION [{target.upper()}] ===")
    print(f"Meilleur modèle : {rec['best_model']} ({rec['family']})")
    print(f"Score composite : {rec['score']:.3f}")
    print(f"Critères validés : {rec['criteria_met']}/7")
    print(f"Recommandation : {rec['recommendation']}")
    
    save_json(rec, f"reports/Regression/Final_Comparison/{target}_recommendation.json")
```

---

## Sorties

```
reports/Regression/Final_Comparison/
├── conc_global_ranking.png
├── conc_criteria_heatmap.png
├── conc_family_comparison_AUC.png
├── conc_family_comparison_R2.png
├── conc_pareto_frontier.png
├── conc_recommendation.json
├── stress_*.png
└── stress_recommendation.json
```

---

## Utilisation

```bash
python src/models/compare/compare_all_models.py
```

**Prérequis :** Toutes les familles de modèles doivent avoir été exécutées.

**Ordre recommandé :**
```bash
# 1. ML Baselines
python src/models/baselines/baseline_ML_regression.py
python src/models/baselines/baseline_ML_regression_feature_eng.py
python src/models/baselines/baseline_ML_regression_smote.py
python src/models/baselines/baseline_ML_regression_feature_eng_smote.py

# 2. DL (19 architectures)
python src/models/deep_learning/architectures/CNN1D.py
# ... (tous les 19)

# 3. Transfer Learning
python src/models/transfer_learning/EEGNet_layer_replacement.py
python src/models/transfer_learning/EEGNet_full_finetuning.py
python src/models/transfer_learning/EEGNet_feature_extraction.py

# 4. Comparaison finale
python src/models/compare/compare_all_models.py
```
