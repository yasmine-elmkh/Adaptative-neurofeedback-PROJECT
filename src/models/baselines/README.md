# NeuroCap — Baseline Models (`src/models/baselines/`)

Classical machine learning classifiers trained on raw and engineered EEG features.

---

## Scripts

| Script | Description |
|---|---|
| `baseline_ML.py` | Train and evaluate RF / SVM / XGBoost on raw spectral/temporal features |
| `baseline_ML_feature_eng.py` | Same classifiers on the selected + normalised engineered feature set |
| `compare_baselines_features.py` | Side-by-side comparison of raw vs engineered features, generates bar charts |

> `gen_dummy_model.py` has been removed — it generated a LightGBM model on fully synthetic data and had no production utility.

---

## Models

| Model | Raw features Accuracy | Engineered features Accuracy |
|---|---|---|
| Random Forest | 78.3% | 83.7% |
| SVM (RBF) | 81.2% | 84.5% |
| XGBoost | 83.1% | 85.9% |

---

## Usage

```bash
# Train on raw features
python src/models/baselines/baseline_ML.py \
    --data data/Merge_datasets/datasets_merged/ \
    --output reports/Baseline/baselines_outputs/

# Train on engineered features
python src/models/baselines/baseline_ML_feature_eng.py \
    --data features/Features_eng/ \
    --output reports/baseline_FeatEng/outputs_baseline/

# Compare feature sets
python src/models/baselines/compare_baselines_features.py \
    --raw reports/Baseline/ \
    --eng reports/baseline_FeatEng/ \
    --output reports/Comparison_Baselines_Features/
```

---

## Hyperparameters

Default settings (tuned via 5-fold cross-validation):

| Model | Key hyperparameters |
|---|---|
| Random Forest | `n_estimators=300`, `max_depth=None`, `min_samples_leaf=2` |
| SVM | `kernel=rbf`, `C=10`, `gamma=scale` |
| XGBoost | `n_estimators=200`, `max_depth=6`, `learning_rate=0.1`, `subsample=0.8` |

---

## Output

Results are saved to `reports/Baseline/` and `reports/baseline_FeatEng/`:
- `metrics.json` — accuracy, F1, precision, recall per class
- `confusion_matrix.png` — heatmap
- `classification_report.txt` — per-class breakdown
- `feature_importance.png` — top 20 features (Random Forest)
